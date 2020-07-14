#!/usr/bin/python
import paho.mqtt.client as mqtt
import serial
import sys
import os
import time
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler
import json
import requests

from energy_module import EnergyModule
from relay_module import RelayModule
from power_module import PowerModule

logger = logging.getLogger('sensor_logger')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('sensor_logger.log', maxBytes=2000, backupCount=10)
logger.addHandler(handler)

serialdev = '/dev/ttyAMA0'
mqtt_url = ''
mqtt_username = ''
mqtt_pwd = ''

fmt = '%Y-%m-%d %H:%M:%S'
seconds = 298
teleperiod = 300
teleperiod_offset = 0
config = lambda: None
relay_on = False
energy_on = False

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    try:
        print("Received message '" + str(msg.payload) + "' on topic '" + msg.topic + "' with QoS " + str(msg.qos))
        fulltopic = msg.topic.replace("cmnd/"+mqtt_username+"/", "").lower()

        t = fulltopic.split("/",1)
        topic = ""
        id = ""
        if len(t) > 0:
            topic = t[0]
        if len(t) > 1:
            id = t[1]
        

        body=str(msg.payload.decode("utf-8","ignore"))
        print("Received message '" + str(body) + "' on topic '" + topic + "' with QoS " + str(id))
        if topic == "teleperiod":
            print("teleperiod")
            teleperiod = body
            config['teleperiod'] = teleperiod
            update_json()
        if topic == "teleperiodoffset":
            print("teleperiod_offset")
            teleperiod_offset = body
            config['teleperiod_offset'] = teleperiod_offset
            update_json()
        
        print("---------------------")
        powerModule.onMessage(id, topic, body,update_json)
        print("---------------------")
        if relay_on:
            print("relay_on")      
            relayModule.onMessage(id, topic, body,update_json)
        if energy_on:
            energyModule.onMessage(id, topic, body,update_json)

        print("config done")                  
    except:
        logger.error(sys.exc_info())   
        print(sys.exc_info())
        #client.publish("stat/"+mqtt_username+"/POWER/"+id, msg.payload)

def update_json():
    print("UPDATE JSON")
    with open('config.json', 'w') as outfile:
        json.dump(config, outfile, indent=4, sort_keys=True)
        powerModule.onConfigChange(config)
        if relay_on:
            relayModule.onConfigChange(config)
        if energy_on:
            energyModule.onConfigChange(config)
          
def cleanup():
    print("Ending and cleaning up")
    client.disconnect()
    ser.close()

def logSerial(reading):
    serialLogger.info(reading)

try:
    with open("config.json", "r") as jsonFile:
        print("config loading..")
        config = json.load(jsonFile)
        print("json loaded..")
        mqtt_url = config['mqtt_url']
        mqtt_username = config['mqtt_username']
        mqtt_pwd = config['mqtt_pwd']
        teleperiod = config['teleperiod']
        teleperiod_offset = config['teleperiod_offset']
        relay_on = config['relay_on']
        energy_on = config['energy_on']
        print("config loaded")
except:
    print(sys.exc_info()[0])
    logger.error(sys.exc_info())
    print("ERROR: loading config")

try:
    print("Connecting... ", serialdev)
    #connect to serial port
    ser = serial.Serial(serialdev, 38400, timeout=1)
    print("connected...")
except:
    print("ERROR: Failed to connect serial")
    #unable to continue with no serial input
    raise SystemExit

try:
    serialLoggerName = "serial.log"
    serialLogger = logging.getLogger('serial')
    print("2")
    serialHandler = TimedRotatingFileHandler(serialLoggerName, when="midnight", interval=1,backupCount=90)
    print("4")
    serialHandler.suffix = "%Y%m%d"
    serialLogger.addHandler(serialHandler)
    print("6")
    serialLogger.setLevel(logging.DEBUG)
except:
    print(sys.exc_info()[0])
    print("-------------------------------------------")
    print("ERROR: Logger failed")
    print("-------------------------------------------")

try:
    print("Mqtt Setup")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(mqtt_username,mqtt_pwd)
    client.connect(mqtt_url, 1883, 60)
    print("Mqtt connected")
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.subscribe("cmnd/"+mqtt_username+"/#")
    #client.loop_forever()
    client.loop_start()

    try:
        powerModule = PowerModule(config, client, logger)
    except:
        print("ERROR: config power",sys.exc_info())

    try:
        if relay_on:
            relayModule = RelayModule(config, client, logger)
    except:
        print("ERROR: config relay",sys.exc_info())

    try:
        if energy_on:
            energyModule = EnergyModule(config, client, logger)
    except:
        print("ERROR: config energy",sys.exc_info())

    time_start = datetime.now()
    dt_start = time.mktime(time_start.timetuple())
    previous_tele_period = int((dt_start + teleperiod_offset)/teleperiod)

    time.sleep(2)
    if relay_on:
        relayModule.sendState()

    print("INFO: Start running")
    while 1:
        try:
            line = ser.readline()
            line = line[:-2]
            logSerial(line)
            print(line)
            reading = line.split(' ')
            if energy_on:
                energyModule.addReading(reading)
 
            if relay_on:
                relayModule.checkRelayTimer()

            time_current = datetime.now()
            dt_current = time.mktime(time_current.timetuple())
            current_tele_period = int((dt_current+teleperiod_offset)/teleperiod)

            if current_tele_period != previous_tele_period:
                print("Publish POWER")
                previous_tele_period = current_tele_period
                powerModule.sendState()
                if relay_on:
                    relayModule.sendState()

        except:
            print("Error occurred: ",sys.exc_info()) 
            logger.error(sys.exc_info()[0])
            time.sleep(10)
              
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
