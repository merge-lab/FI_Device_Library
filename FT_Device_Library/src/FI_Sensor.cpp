#include "FI_Sensor.h"

float AnalogSensor::get_normalized_reading() const
{
    int raw = analogRead(pin);
    float voltage = raw * (reference_voltage / adc_resolution);
    float normalized = (voltage - min_volt) / (max_volt - min_volt);
    return normalized;
}

float AnalogSensor::get_pressure() const
{
    return (get_normalized_reading() * (2*scale)) - offset;
}

float AnalogSensor::get_raw_data() const
{
    return get_normalized_reading();
}

uint32_t DigitalSensor::retrieve_raw() const
{
    constexpr uint32_t TIMEOUT_MS = 25;

    Wire.beginTransmission(address);
    Wire.write(READ_CMD);

    if (Wire.endTransmission() != 0)
    {
        last_status = I2C_ERROR;
        return 0;
    }

    uint32_t start = millis();

    while ((millis() - start) < TIMEOUT_MS)
    {
        Wire.requestFrom(address, (uint8_t)7);

        if (Wire.available() < 7)
        {
            delay(1);
            continue;
        }

        uint8_t status = Wire.read();

        bool powered     = status & 0x40;
        bool busy        = status & 0x20;
        bool memoryError = status & 0x04;
        bool aluError    = status & 0x01;

        if (!powered)
        {
            delay(1);
            continue;
        }

        if (busy)
        {
            last_status = BUSY;

            // consume remaining bytes
            for (int i = 0; i < 6 && Wire.available(); i++)
                Wire.read();

            delay(1);
            continue;
        }

        if (memoryError)
        {
            last_status = MEMORY_ERROR;
            return 0;
        }

        if (aluError)
        {
            last_status = ALU_ERROR;
            return 0;
        }

        uint32_t raw =
            ((uint32_t)Wire.read() << 16) |
            ((uint32_t)Wire.read() << 8)  |
             (uint32_t)Wire.read();

        // discard temperature bytes
        Wire.read();
        Wire.read();
        Wire.read();

        last_status = OK;
        return raw;
    }

    last_status = TIMEOUT;
    return 0;
}

float DigitalSensor::get_pressure() const
{
    uint32_t raw = retrieve_raw();

    if (last_status != OK)
        return NAN;

    return (raw - offset) * (2.0f * scale / FULL_SCALE);
}

float DigitalSensor::get_raw_data() const
{
    uint32_t raw = retrieve_raw();

    if (last_status != OK)
        return NAN;

    return static_cast<float>(raw);
}