#!/usr/bin/env python

# test script to verify sensor functionality 

import smbus2
import bme280

# change default port and address if needed

port = 1
address = 0x76
bus = smbus2.SMBus(port)

# read sensor 

data = bme280.sample(bus, address)

# display sensor readings

print("I2C port    = ",port)
print("BME280 Addr = ",hex(address))
print("Timestamp   = ",data.timestamp,"GMT")
print("Temperature = ","{:.2f}".format(data.temperature),"C")
print("Pressure    = ","{:.2f}".format(data.pressure),"hPa")
print("Humidity    = ","{:.2f}".format(data.humidity),"%RH")