#!/usr/bin/python
import paho.mqtt.client as mqtt
import serial
import sys
import os
import time
from datetime import datetime
from energy import EnergyReading
import logging
from logging.handlers import RotatingFileHandler
import json
import requests


logger = logging.getLogger('energy_logger')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('energy_log.log', maxBytes=2000, backupCount=10)
logger.addHandler(handler)

readingfile = "reading.txt"
serialdev = '/dev/ttyAMA0'
mqtt_url = ''
mqtt_username = ''
mqtt_pwd = ''
fmt = '%Y-%m-%d %H:%M:%S'
seconds = 298
teleperiod = 300
teleperiod_offset = 0
current_holder = 0
config = lambda: None

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if msg.topic.endswith("TelePeriod"):
        print("teleperiod")
        teleperiod = msg.payload
        config['teleperiod'] = teleperiod
        updatejson()
    if msg.topic.endswith("TelePeriodOffset"):
        print("teleperiod_offset")
        teleperiod_offset = msg.payload
        config['teleperiod_offset'] = teleperiod_offset
        updatejson()

def updatejson():
    with open('config.json', 'w') as outfile:
        json.dump(config, outfile)

def logreading(reading):
    f = open(readingfile, "r")
    f.close()

def cleanup():
    print("Ending and cleaning up")
    client.disconnect()
    ser.close()

def getlastreadings(linecount):
    print("Ending and cleaning up")


try:
    with open("config.json", "r") as jsonFile:
        config = json.load(jsonFile)
        mqtt_url = config['mqtt_url']
        mqtt_username = config['mqtt_username']
        mqtt_pwd = config['mqtt_pwd']
        teleperiod = config['teleperiod']
        teleperiod_offset = config['teleperiod_offset']

except:
    print("error loading config")

try:
    print("Connecting... ", serialdev)
    #connect to serial port
    ser = serial.Serial(serialdev, 38400, timeout=1)
    print("connected...")
except:
    print("Failed to connect serial")
    #unable to continue with no serial input
    raise SystemExit

try:
    print("Mqtt Setup")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    #client.username_pw_set("bogecsys","Q6l2kwQoiZ96")
    client.username_pw_set(mqtt_username,mqtt_pwd)
    print("mqtt connecting...")
    client.connect(mqtt_url, 1883, 60)
    print("mqtt connected")
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    #client.loop_forever()
    client.loop_start()
    i = 0
    timeStart = datetime.now()

    dt_st = time.mktime(timeStart.timetuple())

    current_holder = int((dt_st + teleperiod_offset)/teleperiod)
    
    er = EnergyReading([])
    time.sleep(2)
    while 1:
        try:
            line = ser.readline()
            line = line[:-2]
            print(line)
            reading = line.split(' ')
            if len(reading)>15: 
                
                if i == 0:
                    timeStart = datetime.now()
                    print("starting....")
                    er = EnergyReading(reading)
                    dt_st = time.mktime(timeStart.timetuple())
                    i += 1
                    continue

                print("CRT1:{0}W {1}W {2}mA {3}v {4}".format(reading[1],reading[2],reading[3],reading[4],reading[5]))
                print("CRT2:{0}W {1}W {2}mA {3}v {4}".format(reading[6],reading[7],reading[8],reading[9],reading[10]))
                print("CRT3:{0}W {1}W {2}mA {3}v {4}".format(reading[11],reading[12],reading[13],reading[14],reading[15]))

                timeNext = datetime.now()
                dt_nx = time.mktime(timeNext.timetuple())
                
                er.addReading(reading)
                i += 1
            
                #print("NEW:" + er.getReading())
                #print("Time - {0} - {1}".format(int(dt_nx-dt_st),i))
                print("{0} - {1}".format(int(dt_nx/teleperiod), current_holder))
                #if(int(dt_nx-dt_st) >= seconds):
                temp_holder = int((dt_nx+teleperiod_offset)/teleperiod)
                if(temp_holder != current_holder):
                    current_holder = temp_holder
                    request = '{"Time":"'+timeStart.strftime("%Y-%m-%dT%H:%M:%S")+'","Energy":"'+er.getReading()+'"}'
                    logreading(request)
                    print(request)
                    try:
                        client.publish("tele/"+mqtt_username+"/SENSORS", request)
                    except:
                        print("Error sending")
                        logger.error(sys.exc_info()[0])
                    
                    i = 0
                    time.sleep(0.2)

                print("-----------------------------------")
        except:
             print("Error occurred: ",sys.exc_info()[0]) 
             logger.error(sys.exc_info()[0])
             time.sleep(2)
        
        
except (IndexError):
    print("No data received within serial timeout period")
    cleanup()
# handle app closure
except (KeyboardInterrupt):
    print("Interrupt received")
    cleanup()
except (RuntimeError):
    print("uh-oh! time to die")
    cleanup()    
