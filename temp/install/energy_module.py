from energy import EnergyReading
import time
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import sys

class EnergyModule:
  def __init__(self, config, client, logger):
    self.client = client
    self.config = config
    self.logger = logger

    self.mqtt_username = config["mqtt_username"]
    self.teleperiod = config["teleperiod"]
    self.teleperiod_offset = config["teleperiod_offset"]

    self.energyReading = EnergyReading([])
    self.isEnergyStart = True
    self.current_holder = 0
    self.timeStart = datetime.now()

    self.readingsLoggerName = "reading.log"
    self.readingsLogger = logging.getLogger('energy_module_readings')
    self.readingsHandler = TimedRotatingFileHandler(self.readingsLoggerName, when="midnight", interval=1,backupCount=90)
    self.readingsHandler.suffix = "%Y%m%d"
    self.readingsLogger.addHandler(self.readingsHandler)
    self.readingsLogger.setLevel(logging.DEBUG)

  def onMessage(self, id, topic, body, callback):
    if topic == "energyhistory":
      self.getLastReadings(datetime.strptime(body, '%Y-%m-%d'))
    return

  def onConfigChange(self,newconfig):
    self.config = newconfig
    self.mqtt_username = newconfig["mqtt_username"]
    self.teleperiod = newconfig["teleperiod"]
    self.teleperiod_offset = newconfig["teleperiod_offset"]

  def addReading(self, reading):
    timeNext = datetime.now()
    dt_nx = time.mktime(timeNext.timetuple())
    if len(reading) > 15: 
      #print('Energy Reading')
      if self.isEnergyStart:
        self.timeStart = datetime.now()
        print("starting....")
        self.energyReading = EnergyReading(reading)
        request = '{"Time":"'+self.timeStart.strftime("%Y-%m-%dT%H:%M:%S")+'","Energy":"'+self.energyReading.getReading()+'"}'
        self.logReading(request)
        self.isEnergyStart = False
        return

      self.energyReading.addReading(reading)

      temp_holder = int((dt_nx+self.teleperiod_offset)/self.teleperiod)
      if(temp_holder != self.current_holder):
        self.current_holder = temp_holder
        request = '{"Time":"'+self.timeStart.strftime("%Y-%m-%dT%H:%M:%S")+'","Energy":"'+self.energyReading.getReading()+'"}'
        self.logReading(request)
        print(request)
        try:
          self.client.publish("tele/"+self.mqtt_username+"/SENSORS", request)
        except:
          print("Error sending")
          self.logger.error(sys.exc_info()[0])
        
        self.isEnergyStart = True
        time.sleep(0.2)   

  def getLastReadings(self, date):
    today = datetime.today().strftime('%Y-%m-%d')
    filename = self.readingsLoggerName
    if today != date:
      filename = filename + "."+today

    with open(filename, 'r') as file:
      data = "["+ file.read().replace('\n', ',')+"]"
    
    self.client.publish("tele/"+self.mqtt_username+"/SENSORS", data)

  def logReading(self, reading):
    self.readingsLogger.info(reading)
  