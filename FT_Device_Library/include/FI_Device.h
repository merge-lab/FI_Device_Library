#ifndef FI_DEVICE_H
#define FI_DEVICE_H

#include <Arduino.h>
#include <vector>
#include "FI_Sensor.h"

/* Can extend this to whatever sensor device you have if needed */
class FI_Device
{
public:
    /*
    Constructor
    Input: name - the name of this device
    */
    FI_Device(const char* name) : name(name){}
    
    /* Destructor */
    ~FI_Device(){for(FI_Sensor* s : sensors) { delete s; } sensors.clear();}

    /* Disable copying */
    FI_Device(const FI_Device&) = delete;
    FI_Device& operator=(const FI_Device&) = delete;

    /* Disable moves */
    FI_Device(FI_Device&&) = delete;
    FI_Device& operator=(FI_Device&&) = delete;

    /*
    Adds a new analog sensor such as L01D
    Assigns next consecutive id value
    Input: see analog_sensor constructor
    Return: True if sensor add successful, false otherwise
    */
    bool add_analog_sensor(int pin, float refV, int adcR, float minV, float maxV, 
        float offset, float scale);

    /*
    Adds a new digital sensor such as L10D or L30D
    Assigns next consectuive id value
    Input: see digital_sensor constructor
    Return: True if sensor add successful, false otherwise
    */
    bool add_digital_sensor(int scale, uint8_t address, float offset);

    /*
    theoretical / intended behavior is to return sensor pressure in inH20.
    Note that, although these calculations should work given the right 
    constants, in practice it is likely only a basic approximation and both 
    calibration and more refined non-linear models may be neccesary for more 
    accurate results

    Input: int id of sensor accessed in order of sensor addition / creation
    Output: float pressure at given sensor
        or NAN if id invalid
    */
    float get_pressure(int id);

    /*
    theoretical / intended behavior is to return sensor pressure in inH20.
    Note that, although these calculations should work given the right 
    constants, in practice it is likely only a basic approximation and both 
    calibration and more refined non-linear models may be neccesary for more 
    accurate results

    Input: none
    Output: Vector<float> of sensor pressures
        In order of sensor creation (ie: sensor 0's pressure is at vector[0])
    */
    std::vector<float> get_all_pressures();

    /*
    Get type of this sensor
    Input: int id of sensor accessed in order of sensor addition / creation
    Output: SENSOR_TYPE value of this sensor. Import FI_SENSOR.h to parse
        or SENSOR_TYPE.INVALID if not a valid id
    */
    SENSOR_TYPE get_sensor_type(int id);

    /*
    Returns the raw value of this sensor
    Input: None
    Output: Raw value for given sensor, units depending on sensortype
        or NAN if not a valid id
    */
    float get_raw_data(int id);

    /*
    Returns sensor status. Interpret using get_sensor_type()
    Input: int id of sensor accessed in order of sensor addition / creation
    Output: int representation of sensor status enum.
        or -1 if invalid id
    */
    int get_sensor_status(int id);


private:
    const char* name;                           // name of this device 
    std::vector<FI_Sensor*> sensors;            // sensors on this device
};

#endif