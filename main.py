from flask import Flask
import json
import os
import glob
import time
import asyncio
import random

import RPi.GPIO as GPIO
import board
import adafruit_dht

PIN_A = 27
PIN_B = 28

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
devices = glob.glob(base_dir)

sensor = adafruit_dht.DHT11(board.D0)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
GPIO.setmode(GPIO.BCM)

app = Flask(__name__)

#Temp Read Code
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        #temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c

async def read_dht():
    temperature_c = sensor.temperature
    temperature_f = temperature_c * (9 / 5) + 32
    humidity = sensor.humidity
    print("Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%".format(temperature_c, temperature_f, humidity))

    return temperature_c, temperature_f, humidity


#API
@app.route('/')
def index():
    temp = read_temp()
    object = ('{ "temp":"%s", "nonsense":"definetly"}' % temp)
    return json.loads(object)

@app.route('/humidity')
async def humidity():
    try:
        result = await asyncio.wait_for(read_dht(),timeout=7)
        object = ('{ "temp":"{0:0.1f}", "humidity":"{2:0.1f}" "nonsense":"definetly"}'.format(result.temperature_c, result.humidity))
        print(object)

        return json.loads(object)
    
    except TimeoutError as err:
        print(err.args[0])
        object = '{"status":"timeout"}'
        return json.loads(object)
    
    except RuntimeError as err:
        print(err.args[0])
        object = '{"nonsense":"no :("}'
        return json.loads(object)


@app.route('/hello')
def hello():
    object = '{"nonsense":"no :("}'
    return json.loads(object)
        

if __name__ == '__main__':
        print(devices)
        app.run(debug=True, host='0.0.0.0')