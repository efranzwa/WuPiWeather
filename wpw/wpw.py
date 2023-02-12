#!/usr/bin/env python

import smbus2
import os
import sys
import urllib.request, urllib.parse, urllib.error
from math import log
from time import sleep
import bme280


# define global variables for configuration
# if /boot/wpw-station.conf exists will set these variables
PORT        = 1     # most raspberry pi use 1
ADDRESS     = 0x76  # default device I2C address 
INTERVAL    = 300   # delay between each reading (secs)
STATION_ID  = "my-station-id"
STATION_KEY = "my-station-key"
WU_URL      = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"
ALTITUDE    = 100   # altitude in feet for barometric pressure correction


def sendDataWU(url,statid,statkey,temp,pres,humid,dewpt):
# send sensor data to weather underground

    values = {
    "action": "updateraw",
    "ID": statid,
    "PASSWORD": statkey,
    "dateutc": "now",
    "tempf": str(temp),
    "baromin": str(pres),
    "humidity": str(humid),
    "dewptf": str(dewpt),
    }

    # build url request string
    urlmod = url + "?"
    postdata = urllib.parse.urlencode(values)
    postdata = postdata.encode('ascii')
    req = urllib.request.Request(urlmod, postdata)

    try:
        response = urllib.request.urlopen(req)
        html_string = response.read()
        #print("Server response: ", html_string)
        response.close()

    except urllib.error.HTTPError as e:
        print("HTTP error: ", e)
        sleep(60)

    except urllib.error.URLError as e:
        print("URL error: ", e)
        sleep(60)

    except Exception as e:
        print("Exception: ", e)
        sleep(60)


def dewpoint_c(temp,relh):
    # calculate dewpoint from T(C) and RH
    eqn1 = (17.62 * temp) / (243.12 + temp)
    eqn2 = log(relh/100)
    return (243.12*(eqn1 + eqn2))/(17.62-(eqn1 + eqn2))


def c_to_f(input_temp):
    # convert Celsius to Farenheit
    return (input_temp * 1.8) + 32


def mb_to_in(input_pressure):
    # convert millibar or hPa to Inches Hg
    return (input_pressure * 0.0295300)


def altitude_cor(input_pressure, alt):
    # altitude correction factor for pressure measurement
    alt_cor = (760 - alt * 0.026) / 760
    return (input_pressure/alt_cor)


def main():

    global PORT
    global ADDRESS
    global INTERVAL
    global STATION_ID
    global STATION_KEY
    global WU_URL
    global ALTITUDE
    config=[0,1,2,3,4,5,6,7]

    # check for configuration file in /boot/wpw-station.conf
    if os.path.isfile('/boot/wpw-station.conf')==True:
        print("Found station file wpw-station.conf")
        f = open('/boot/wpw-station.conf','r')
        config = f.read().splitlines()
        f.close()
    
    # assign station configuration from file
    if config[0]=='wpw':
        print("Using station file wpw-station.conf")
        PORT          = int(config[1])
        ADDRESS       = int(config[2],16)
        INTERVAL      = int(config[3])
        STATION_ID    = config[4]
        STATION_KEY   = config[5]
        WU_URL        = config[6]
        ALTITUDE      = int(config[7])
    
    else:
        print("No station data in wpw-station.conf, exiting")
        sys.exit(1)

    try:

        while True:
            
            # retrieve sensor data
            bus = smbus2.SMBus(PORT)
            data = bme280.sample(bus, ADDRESS)
            temp_raw = data.temperature
            pres_raw = data.pressure
            humid_raw = data.humidity
            
            # apply conversions and format results
            dewpoint_raw = dewpoint_c(temp_raw, humid_raw)
            dewpoint_f = round(c_to_f(dewpoint_raw), 3)
            temp_f = round(c_to_f(temp_raw), 3)
            pres_in = mb_to_in(pres_raw)
            pres_in_cor = round(altitude_cor(pres_in, ALTITUDE), 3)
            humid = round(humid_raw, 3)
            
            # uncomment for debugging
            #print("Temp = ",temp_f)
            #print("Pres = ",pres_in_cor)
            #print("Humi = ",humid)
            #print("Dewp = ",dewpoint_f,"\n")
            
            # send data to weather underground
            sendDataWU(WU_URL,STATION_ID,STATION_KEY,temp_f,pres_in_cor,humid,dewpoint_f)
            sys.stdout.flush()
            
            # wait for next reading
            sleep(INTERVAL)

    except KeyboardInterrupt:
        print("\nExiting Application\n")
        sys.exit(0)

    except Exception as e:
        print("Exception: ", e)
        sleep(INTERVAL)
        #sys.exit(1)


if __name__=="__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\nExiting Application\n")
        sys.exit(0)

    except Exception as e:
        print("Exception: ", e)
        sleep(INTERVAL)
        #sys.exit(1)
