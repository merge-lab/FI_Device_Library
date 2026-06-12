# FT DEVICE LIBRARY
Library for the abstraction of FT Devices on embedded microcontrollers such as ESP32
Supports:
- DLHR-L01D Analog Transducer: implemented and moderately tested
- DLHR-L10D and DLH-L30D Digital Transducers: implemented but as of yet untested

## OVERVIEW
The library consists of FT_Sensors (representing individual sensors), and FT_Devices (representing a collection of sensors).\
The intended use is for the user to create FT_Device objects to access their sensors through.

## COMPONENTS
### FT_SENSOR (FT_Sensor.h & FT_Sensor.cpp)
Each individual sensor is represented by an object of the FT_Sensor class. This class exposes the following functions:
- int get_ID() : returns the sensor's id number, assigned at creation
- float get_pressure() : theoretical / intended behavior is to return sensor pressure in inH20. Note that, although these calculations *should* work given the right constants, in practice it is likely only a basic approximation and both calibration and more refined non-linear models may be neccesary for more accurate results
- float get_raw_data() : returns whatever the appropriate unitless raw data is for the given sensor
- SENSOR_TYPE get_sensor_type() : returns what kind of sensor this has been assigned as

The FT_Sensor class itself is simply a template class off of which other, more descript classes are implemented. This structure allows us to create new types of FT_Sensors, while abstracting all FT_Sensors to the same thing for the purposes of higher level use, data structure storage, etc. Current implementations of FT_Sensor include: 

#### AnalogSensor
For sensors such as the DLHR-L01D analog transducer. The constructor parameters are as follows:
- id              : int id of the sensor
- pin             : pin on the board sensor connected to
- refV            : ADC reference voltage
- adcR            : ADC resolution
- minV            : min sensor voltage
- maxV            : max sensor voltage
- offset          : sensor offset in inH20
- scale           : sensor scaling factor (ex: 10 for L10D)

To calculate pressure, it takes an analog read, converts the adc value to a voltage, normalizes the voltage to be between min and max volts, and then runs the formula pressure = (normalized_reading * (2*scale)) - offset. Note: this pressure calculation attempts to return a value in inH20. However, in practice these values are quite small, so if greater deltas are desired, increasing the scaling factor may be useful.

#### DigitalSensor
For sensors such as the DLHR-L10D and DLH-L30D digital transducers. The constructor parameters are as follows:
- id                  : int id of this sensor
- scale               : scaling factor of this sensor
- address             : address on the i2c bus
- offset              : calibrated sensor offset

To calculate pressure, we make a request for the raw value, then convert it according to the formula pressure = (raw - offset) / (2.0 * scale / FULL_SCALE), where FULL_SCALE is 2^24.

### FT_DEVICE (FT_Device.h & FT_Device.cpp)
Represents a collection of sensors. For example, a single FORTE finger may be considered an FT_Device with 3 FT_Sensors, and a whole FORTE claw would have 2 FT_Devices.\
The following functions are exposed:
- Constructor : takes in a char* (string) name of the device for identification
- bool add_analog_sensor(...) : takes in all the parameters to create an analog sensor. returns true if sensor successfully added and false otherwise
- bool add_digital_sensor(...) : takes in all the parameters to create a digital sensor. returns true if sensor successfully added and false otherwise
- float get_pressure(int id) : returns pressure of given sensor. NAN if invalid sensor. See 'note on ids' for more info about sensor access.
- float get_raw_data(int id) : returns raw value of given sensor, based on what makes sense for the given sensor type. NAN if invalid sensor. See 'note on ids' for more info about sensor access
- SENSOR_TYPE get_sensor_type(int id) : returns the type of the given sensor or SENSOR_TYPE.invalid if invalid sensor id. See 'note on ids' for more info about sensor access. Note that some environments may require you to import "FT_Sensor.h" in order to parse sensor type, since the enum is defined there.
- std::vector<float> get_all_pressures() : returns a vector of pressures on all sensors, where sensor 0's pressure is at index 0, sensor 1's pressure is at index 1, etc. See 'note on ids' for more info about sensor access

#### NOTE ON IDs:
Sensor IDs are assigned in consecutive order, starting with 0, based on the order in which they are added. The first sensor added via a call to either add_analog_sensor() or add_digital_sensor() will be assigned id 0. The second sensor added via either of those will be assigned id 1. etc. 

## USING THIS LIBRARY
As this is not an official / published platformio library, there are some steps that must be followed to utilize the code given here.

1. Choose a directory in which to store this library.
2. Find the relative path from your project directory to your chosen directory. https://www.redhat.com/en/blog/linux-path-absolute-relative and GPT are both good resources if you don't know what this means and / or need help with this.
3. Clone the repo to your chosen directory.
4. Locate the platformio.ini file in your project. look for a line that says 'lib_deps = '. If it doesnt exist, add it to the bottom of the file. Under 'lib_deps = ', add a new line with a tab, followed by the (the relative path to your chosen directory) + 'FT_Device_Library/FT_Device_Library'. For example, my project's ini file looks like this:
```
; PlatformIO Project Configuration File
;
;   Build options: build flags, source filter
;   Upload options: custom upload port, speed and extra flags
;   Library options: dependencies, extra library storages
;   Advanced options: extra scripting
;
; Please visit documentation for the other options and examples
; https://docs.platformio.org/page/projectconf.html

[env:esp32-s3-devkitc-1]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino
monitor_speed = 9600

lib_deps =
    ../Wifi_Communications/Wifi_Communications
    ../../FT_Device_Library/FT_Device_Library
```
5. place a #include "FT_Device.h" at the top of your desired file and test to make sure everything compiles. See common issues below if this fails.
6. Depending on your workspace, accessing things directly inside of FT_Sensor.h may not work unless you explictly call #include "FT_Sensor.h" at the top of the given file. Most of the time, however, including FT_Device should be sufficient, and most of the items in FT_Sensor are meant to be abstracted from general users anyways.

### Common Issues:
- The platformio.ini file specifies the board for which a given project is meant to compile. 99% of the time, the definition for an ESP32 board will work for any ESP32, but occasionally depending on the board and configuration in question, it may break. Locate the platformio.ini file in the library. There will be a line similar to '[env:esp32-s3-devkitc-1]' at the top. Locate the same line in your project's ini file. If they don't match, replace the line in your copy of the library with the one from your project's ini file.


