import asyncio
import aioble
import bluetooth
from machine import Pin, I2C
from neopixel import NeoPixel
from time import time_ns

##################################################
# I2C SETUP
##################################################
PRESSURE_ADDR = 0x29
# Single = AA, Average 2 = AC, Average 4 = AD, Average 8 = AE, Average 16 = AF
PRESSURE_DATA_CODE = 0xAA

i2c = I2C(0, scl=Pin(0), sda=Pin(1))
addr = i2c.scan()
if PRESSURE_ADDR not in addr:
    raise ValueError('Sensor not plugged in. Expecting ' + str(PRESSURE_ADDR) + ' but found ' + str(addr))

##################################################
# GPIO SETUP
##################################################
TRIGGER_PIN = 3
triggerIn = Pin(3, Pin.IN)

##################################################
# BLE SERVICE SETUP
##################################################

# See the following for generating UUIDs: https://www.uuidgenerator.net/
# For some reason, all the same?
_BLE_SERVICE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214')
_BLE_SENSOR_CHAR_UUID = _BLE_SERVICE_UUID # Will actually be renamed to 19b100*1*
_BLE_LED_UUID = _BLE_SERVICE_UUID # Will actually be renamed to 19b100*1*
# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000

# Register GATT server, the service and characteristics
ble_service = aioble.Service(_BLE_SERVICE_UUID)
sensor_characteristic = aioble.Characteristic(ble_service, _BLE_SENSOR_CHAR_UUID, read=True, notify=True)
led_characteristic = aioble.Characteristic(ble_service, _BLE_LED_UUID, read=True, write=True, notify=True, capture=True)

# Register service(s)
aioble.register_services(ble_service)

# Helper to encode the data characteristic UTF-8
def _encode_data(data):
    return str(data).encode('utf-8')

# Helper to decode the write characteristic encoding (bytes).
def _decode_data(data):
    try:
        if data is not None:
            # Decode the UTF-8 data
            number = int.from_bytes(data, 'big')
            return number
    except Exception as e:
        print("Error decoding write data:", e)
        return None

##################################################
# TASKS
##################################################

# Get new value and update characteristic
async def sensor_task():
    while True:
        flag = 0
        i2c.writeto(PRESSURE_ADDR, bytes([PRESSURE_DATA_CODE]))
        #print('escape')
        while not flag:
            b = i2c.readfrom(PRESSURE_ADDR, 1)
            print(b[0])
            if b[0] in (0x41,0x44,0x45):
                flag = True
            else:
                flag = (b[0] == 0x40)
            
        block = i2c.readfrom(PRESSURE_ADDR, 7)
        # print(list(map(hex,block)))
        
        # https://www.mouser.com/ProductDetail/Amphenol-All-Sensors/DLHR-L10D-E1BD-C-NAV8?qs=F5EMLAvA7IAG72p6SeJcnw%3D%3D            
        #pressure_dacOutput = (block[1] << 2*8 ) + (block[2] << 8) + block[3]
        pressure_dacOutput = int.from_bytes(block[1:4],'big',False)
        #temperature_dacOutput = (block[4] << 2*8 ) + (block[5] << 8) + block[6]
        temperature_dacOutput = int.from_bytes(block[4:7],'big',False)

        pressure = 1.25*((pressure_dacOutput - (1 << 23)) / float(1 << 24))*(2*10)
        
        if pressure > 10 or pressure == -12.5:
            pressure = 10
        temperature = temperature_dacOutput * 125 / (1 << 24) - 40
        print('pressure : ' + str(pressure))

        sensor_characteristic.write(_encode_data([0, pressure, temperature, triggerIn.value(), time_ns()]), send_update=True)
        # print("Sensor " + str(address) + ": " + str(pressure) + ',' + str(temperature))
            
        await asyncio.sleep_ms(10)
        
# Serially wait for connections. Don't advertise while a central is connected.
async def peripheral_task():
    while True:
        try:
            async with await aioble.advertise(
                _ADV_INTERVAL_MS,
                name="ESP32",
                services=[_BLE_SERVICE_UUID],
                ) as connection:
                    print("Connection from", connection.device)
                    await connection.disconnected()             
        except asyncio.CancelledError:
            # Catch the CancelledError
            print("Peripheral task cancelled")
        except Exception as e:
            print("Error in peripheral_task:", e)
        finally:
            # Ensure the loop continues to the next iteration
            await asyncio.sleep_ms(10)                                                                                                                                                                                                                                                                 

##################################################
# RUN ALL
##################################################

# Run tasks
async def main():
    print("Program starting")
    t1 = asyncio.create_task(sensor_task())
    t2 = asyncio.create_task(peripheral_task())
    await asyncio.gather(t1, t2)
    
asyncio.run(main())