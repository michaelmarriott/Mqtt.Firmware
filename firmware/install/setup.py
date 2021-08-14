#!/usr/bin/python

import logging
from logging.handlers import RotatingFileHandler
import os
import shutil 
import sys
from jsonmerge import merge
import json

logger = logging.getLogger('setup_logger')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('setup_log.log', maxBytes=2000, backupCount=10)
logger.addHandler(handler)

logger.info('running')

unzippath = ''
firmwarepath =''
sensorpath =''

try:
  with open("config.json", "r") as jsonFiled:
    print(jsonFiled)
    config = json.load(jsonFiled)
    unzippath = config['unzippath']
    firmwarepath = config['firmwarepath']
    sensorpath = config['sensorpath']
except:
  print("error loading frimware config",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

try:
  stream = os.popen('sudo systemctl stop sensor_reader.service')
  output = stream.read()
  output

  logger.info('stop sensor_reader.service')
  # Source path 
  sourcepath = unzippath + "install/"
  source =  os.listdir(sourcepath) 

  sensor_config_delta = ''
  sensor_config = ''
  logger.info(source)
except:
  print("error stop sensor_reader.service",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

try:
  for files in source:
    logger.info(files)
    if files == "firmware.py":
      shutil.copy(sourcepath+""+files, firmwarepath)
      
    if files.endswith(".py"):
      logger.info(sourcepath+""+files)
      logger.info(sensorpath)
      shutil.copy(sourcepath+""+files, sensorpath)
except:
  print("error copy file",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

try:
    # Source path 
  config_sensor_delta = unzippath + "install/config.json"
    
  # Destination path 
  config_sensor_destination = sensorpath +"config.json"

  print("merge json files")
  logger.info('merge json files')
  with open(config_sensor_delta, "r") as jsonFileDelta:
    sensor_config_delta = json.load(jsonFileDelta)
    print("load config_sensor_delta")
    logger.info('load config_sensor_delta')
  with open(config_sensor_destination, "r") as jsonFileDestination:
    sensor_config = json.load(jsonFileDestination)
    print("load config_sensor_destination")
    logger.info('load config_sensor_destination')

  result = merge(sensor_config, sensor_config_delta)
  print("merge")
  logger.info('merge')

  with open(config_sensor_destination, "w+") as jsonFile:
    jsonFile.write(json.dumps(result))
    jsonFile.close()
    print("save")
    logger.info('save')
except:
  print("error loading config",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

try:
  print("start service")
  logger.info('start service')
  stream = os.popen('sudo systemctl start sensor_reader.service')
  output = stream.read()
  output
except:
  print("error start sensor_reader.service",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

try: 
  stream = os.popen('sudo systemctl restart firmware.service')
  output = stream.read()
  output
except:
  print("error restart firmware.service",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

logger.info('done')
print('done.')
exit
