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

try:
  with open("config.json", "r") as jsonFiled:
    print(jsonFiled)
    config = json.load(jsonFiled)
    unzippath = config['unzippath']
except:
  print("error loading frimware config",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

stream = os.popen('sudo systemctl stop energy_reader.service')
output = stream.read()
output
logger.info('stop energy_reader.service')
# Source path 
sourcepath = unzippath + "install/"
source =  os.listdir(sourcepath) 
  
# Destination path 
destination = "/home/pi/sensor/"
destination_firmware = "/home/pi/firmware/"

energy_config_delta = ''
energy_config = ''
logger.info(source)
try:
  for files in source:
    logger.info(files)
    if files == "firmware.py":
      shutil.copy(sourcepath+""+files,destination_firmware)
      
    if files.endswith(".py"):
      logger.info(sourcepath+""+files)
      logger.info(destination)
      shutil.copy(sourcepath+""+files,destination)
except:
  print("error copy file",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

# Source path 
config_energy_delta = unzippath + "install/config.json"
  
# Destination path 
config_energy_destination = "/home/pi/sensor/config.json"

print("merge json files")
logger.info('merge json files')
try:
  with open(config_energy_delta, "r") as jsonFileDelta:
    energy_config_delta = json.load(jsonFileDelta)
    print("load config_energy_delta")
    logger.info('load config_energy_delta')
  with open(config_energy_destination, "r") as jsonFileDestination:
    energy_config = json.load(jsonFileDestination)
    print("load config_energy_destination")
    logger.info('load config_energy_destination')

  result = merge(energy_config, energy_config_delta)
  print("merge")
  logger.info('merge')

  with open(config_energy_destination, "w+") as jsonFile:
    jsonFile.write(json.dumps(result))
    jsonFile.close()
    print("save")
    logger.info('save')
except:
  print("error loading config",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

print("start service")
logger.info('start service')
stream = os.popen('sudo systemctl start energy_reader.service')
output = stream.read()
output

stream = os.popen('sudo systemctl restart firmware.service')
output = stream.read()
output

logger.info('done')
print('done.')
exit
