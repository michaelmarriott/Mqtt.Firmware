import RPi.GPIO as GPIO
import json
from relay_timer import RelayTimer
import sys
from datetime import datetime

GPIO.setmode(GPIO.BOARD)

class RelayModule:
  def __init__(self, config, client,logger):
    self.config = config
    self.client = client
    self.logger = logger

    self.mqtt_username = config["mqtt_username"]
    config_relay = config["relay"]
    self.Pins = config_relay["pins"]
    self.Powers = {}  
    self.time_previous = datetime.now()
    self.relay_time_check = config_relay["time_check"]

    try:
      self.relayTimer = RelayTimer(config_relay)
    except:
      print("Error config timer: ",sys.exc_info()) 

    i = 1
    for pin in self.Pins:
      self.Powers[str(i)] = "ON"
      GPIO.setup(pin, GPIO.OUT)
      GPIO.output(pin, GPIO.LOW)
      i=i+1    

  def onMessage(self, id, topic,body, callback):
 #'{"Action":"0","Time":"15:00","Days":"SMTWTFS","Arm":1,"Repeat":1,"Mode":0,"Window":0,"Output":0}'
 # on topic 'cmnd/Sensor3/TIMERS2/2' with QoS 0
    print("Relay: onMessage")
    print(id, topic,body)
    if topic == "power":
      self.setPin(id,body)
      #client.publish("stat/"+mqtt_username+"/POWER/"+id, msg.payload)
    if topic == "timer":
      jbody = json.loads(body)
      self.setRelayTimer(1,id,jbody,callback)
    if "timers" in topic:
      print("timers")
      jbody = json.loads(body)
      relay = int(topic.replace("timers",""))
      print("relay")
      self.setRelayTimer(relay,id,jbody,callback)
    

  def onConfigChange(self,newconfig):
    self.config = newconfig
    self.mqtt_username = newconfig["mqtt_username"]

  def setPin(self, pin, state):
    apin = int(pin)-1
    if state == "ON":
      self.Powers[str(pin)] = state
      GPIO.output(self.Pins[apin], GPIO.LOW)
    if state == "OFF":
      self.Powers[str(pin)] = state
      GPIO.output(self.Pins[apin], GPIO.HIGH)
      self.client.publish("stat/"+self.mqtt_username+"/POWER/"+id, state)
     
  def getPowers(self):
    return self.Powers

  def getPowersString(self):
    return json.dumps(self.Powers)    

  def checkRelayTimer(self):   
    time_current = datetime.now()
    duration = (time_current-self.time_previous).total_seconds()
    print(str(duration)+"-"+str(self.relay_time_check))
    if int(duration) >= self.relay_time_check:
      print(str(duration),str(self.relay_time_check))
      self.time_previous = time_current
      self.relayTimer.checkRelayTimer(self.setPin)

  def setRelayTimer(self, relay, number, data, callback):
    print("self.relayTimer.setRelayTimer")
    print(relay, number, data)
    self.relayTimer.setRelayTimer(relay, number, data, callback)    

  def sendState(self):
    for (i, state) in self.getPowers().items():
      print("client.publish:POWER:"+i)
      current_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
      self.client.publish("tele/"+self.mqtt_username+"/STATE/"+str(i),  json.dumps({"Time":current_datetime,"POWER":state}))
