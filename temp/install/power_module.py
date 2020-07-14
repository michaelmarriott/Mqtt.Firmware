import json
import sys
from datetime import datetime

class PowerModule:

  def __init__(self, config, client, logger):
    self.config = config
    self.client = client
    self.logger = logger

    self.mqtt_username = config["mqtt_username"]
    self.timeStart = datetime.now()
    self.sendState()

  def onMessage(self, id, topic,body, callback):
    print("PowerModule: onMessage")
    return

  def onConfigChange(self,newconfig):
    self.config = newconfig

  def sendState(self):
    print("PowerModule: sendState")
    current_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    self.client.publish("tele/"+self.mqtt_username+"/STATE",  json.dumps({"Time": current_datetime ,"POWER":"ON"}))

