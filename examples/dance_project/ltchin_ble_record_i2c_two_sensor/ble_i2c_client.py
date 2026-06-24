import asyncio
import logging
import csv
from datetime import datetime
from ast import literal_eval

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

LOG_FILENAME = 'log/log__' + datetime.now().strftime("%y%m%d_%H%M%S") +'.log'
CSV_FILENAME = 'log/TEST' + datetime.now().strftime("__%y%m%d_%H%M%S") + '.csv'


#############################################################################
# SETUP
#############################################################################

DEVICE_NAME = 'ESP32'
BLE_SERVICE_UUID = '19b10000-e8f2-537e-4f6c-d104768a1214'
SENSOR_CHARACTERISTIC_UUID = '19b10001-e8f2-537e-4f6c-d104768a1214' # Not the same! first one is slightly different
LED_CHARACTERISTIC_UUID = '19b10002-e8f2-537e-4f6c-d104768a1214' # Not the same! first one is slightly different

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

with open(CSV_FILENAME, 'a', newline='') as csvfile:
    spam = csv.writer(csvfile)
    spam.writerow(["Computer Timestamp", "Sensor Number", "Pressure (in. H20)", "Temperature (C)", "Trigger Pin", "ESP32 Timestamp"])

def fileWrite(rowList):
    with open(CSV_FILENAME, 'a', newline='') as csvfile:
        spam = csv.writer(csvfile)
        spam.writerow([datetime.now().timestamp()] + rowList)


#############################################################################
# BLUETOOTH FUNCTIONS
#############################################################################

def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    """Simple notification handler which prints the data received."""
    logger.info("%s: %r", characteristic.description, data)
    fileWrite(literal_eval(data.decode('utf-8'))) # Nasty bytearray nonsense

async def scanCharacteristics(client):
    for service in client.services:
        logger.info("[Service] %s", service)

        for char in service.characteristics:
            if "read" in char.properties:
                try:
                    value = await client.read_gatt_char(char.uuid)
                    extra = f", Value: {value}"
                except Exception as e:
                    extra = f", Error: {e}"
            else:
                extra = ""

            if "write-without-response" in char.properties:
                extra += f", Max write w/o rsp size: {char.max_write_without_response_size}"

            logger.info(
                "  [Characteristic] %s (%s)%s",
                char,
                ",".join(char.properties),
                extra,
            )

            if char.uuid == SENSOR_CHARACTERISTIC_UUID:
                print("Found it!")

            for descriptor in char.descriptors:
                try:
                    value = await client.read_gatt_descriptor(descriptor.handle)
                    logger.info("    [Descriptor] %s, Value: %r", descriptor, value)
                except Exception as e:
                    logger.error("    [Descriptor] %s, Error: %s", descriptor, e)

#############################################################################
# MAIN PROGRAM
#############################################################################

async def main():
    disconnected_event = asyncio.Event()

    def disconnected_callback(client):
        logger.info("Disconnected callback called!")
        disconnected_event.set()

    logger.info("starting scan...")

    device = await BleakScanner.find_device_by_name(DEVICE_NAME)
    if device is None:
        logger.error("could not find device with name " + DEVICE_NAME)
        return

    logger.info("connecting to device...")

    async with BleakClient(device, disconnected_callback=disconnected_callback) as client:
        logger.info("connected")
        await scanCharacteristics(client)

        await client.start_notify(SENSOR_CHARACTERISTIC_UUID, notification_handler)
        await disconnected_event.wait()
        logger.info("disconnecting...")

    logger.info("disconnected")


if __name__ == "__main__":
    log_level = logging.INFO
    logging.basicConfig(
        filename=LOG_FILENAME,
        filemode='a',
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(main())