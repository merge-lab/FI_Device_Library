#include "FI_Device.h"

bool FI_Device::add_analog_sensor(int pin, float refV, int adcR, float minV, float maxV, 
    float offset, float scale)
{
    auto* sensor = new AnalogSensor(sensors.size(), pin, refV, adcR, minV, maxV, offset, scale);

    // protect against new fails
    if(sensor)
    {
        sensors.push_back(sensor);
        return true;
    }
    return false;
}

bool FI_Device::add_digital_sensor(int scale, uint8_t address, float offset)
{
    auto* sensor = new DigitalSensor(sensors.size(), scale, address, offset);
    if(sensor)
    {
        sensors.push_back(sensor);
        return true;
    }
    return false;
}

float FI_Device::get_pressure(int id)
{
    if(id < 0 || id >= sensors.size()) {return NAN;}
    return sensors[id]->get_pressure();
}

std::vector<float> FI_Device::get_all_pressures()
{
    std::vector<float> pressures;
    pressures.reserve(sensors.size());
    for(size_t i = 0; i < sensors.size(); i++)
    {
        pressures.push_back(sensors[i]->get_pressure());
    }
    return pressures;
}

SENSOR_TYPE FI_Device::get_sensor_type(int id)
{
    if(id < 0 || id >= sensors.size()){return INVALID;}

    return sensors[id]->get_sensor_type();
}

float FI_Device::get_raw_data(int id)
{
    if(id < 0 || id >= sensors.size()) {return NAN;}  

    return sensors[id]->get_raw_data();
}

int FI_Device::get_sensor_status(int id)
{
    if(id < 0 || id >= sensors.size()) {return -1;}

    return sensors[id]->get_status();
}