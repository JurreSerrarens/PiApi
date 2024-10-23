from flask import Flask
from flask import request
import json
import os
import glob
import time
import asyncio
import threading

import RPi.GPIO as GPIO
import board
import adafruit_dht

PIN_A = 27
PIN_B = 28

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

sensor = adafruit_dht.DHT11(board.D26, use_pulseio=True)

minute = -1
hour = -1
activated = False

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
GPIO.setmode(GPIO.BCM)

GPIO.setup(21, GPIO.OUT)


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
    #temperature_f = temperature_c * (9 / 5) + 32
    humidity = sensor.humidity
    #print("Temp={0:0.1f}ºC, Humidity={2:0.1f}%".format(temperature_c, humidity))

    return temperature_c,  humidity

def clock():
    global hour
    global minute
    global activated
    while True:
        cMinute = int(time.strftime("%M"))
        cHour = int(time.strftime("%H"))
        print(cHour,":",cMinute," | ",hour,":",minute)

        if(not activated):
            if(int(hour) == cHour and int(minute) == cMinute):
                print("WEEWOOWEEWOO")
                motoron()
                activated = True
        elif not (int(hour) == cHour and int(minute) == cMinute):
            motoroff()
            print("Rest in pepperoni's weewoo")
            activated = False

        time.sleep(2) 

t1 = threading.Thread(target=clock)

#Data
@app.route('/')
def index():
    temp = read_temp()
    object = ('{ "temp":"%s", "nonsense":"definetly"}' % temp)
    return json.loads(object)

@app.route('/humidity')
async def humidity():
    try:
        result = await asyncio.wait_for(read_dht(),timeout=7)
        print(result)
        object = ('{ "temp":"{0:0.1f}", "humidity":"{2:0.1f}" "nonsense":"definetly"}'.format(result.temperature_c, result.humidity))
        print(object)

        return json.loads(object)
    
    except TimeoutError as err:
        print(err.args[0])
        object = '{"nonsense":"no :(", "status":"timeout"}'
        return json.loads(object)
    
    except RuntimeError as err:
        print(err.args[0])
        object = ('{"nonsense":"no :(", "status":"%s"}' % err.args)
        return json.loads(object)

#Actions
@app.route('/motoron')
def motoron():
    GPIO.output(21, GPIO.HIGH)
    object = '{"status":"success"}'
    return json.loads(object)

@app.route('/motoroff')
def motoroff():
    GPIO.output(21, GPIO.LOW)
    object = '{"status":"success"}'
    return json.loads(object)

@app.route('/setTime')
def settime():
    global t1
    global hour
    global minute
    global activated

    activated = False
    hour = request.args.get('hour')
    minute = request.args.get('min')

    if not t1.is_alive():
        t1 = threading.Thread(target=clock)
        t1.start()
    
    object = ('{"status":"success", "hour": "%s", "minute": "%s"}' % [hour,minute])
    return json.loads(object)

@app.route('/getTime')
def gettime():
    global hour
    global minute
    
    if(int(minute) < 0 or int(hour) < 0):
        object = '{"status":"no time set", "hour": -1, "minute": -1}'
        return json.loads(object)
    
    #Could be put in a sub property like "Time"
    object = ('{"status":"success", "hour": "%s", "minute": "%s"}' % [hour,minute])
    return json.loads(object)

if __name__ == '__main__':
    #t1 = threading.Thread(target=clock) caused two threads smh
    #t1.start()

    app.run(debug=True, host='0.0.0.0')



