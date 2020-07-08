#!/usr/bin/python

print('setup.')
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
    print('ok')
    unzippath = config['unzippath']
except:
  print("error loading frimware config",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

stream = os.popen('sudo systemctl stop energy_reader.service')
output = stream.read()
output

# Source path 
source = unzippath + "install/energy_reader.py"
  
# Destination path 
destination = "/home/pi/sensor/energy_reader.py"

energy_config_delta = ''
energy_config = ''
try:
  shutil.copyfile(source, destination) 
except:
  print("error copy file",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

# Source path 
config_energy_delta = unzippath + "install/config.json"
  
# Destination path 
config_energy_destination = "/home/pi/sensor/config.json"

print("merge json files")

try:
  with open(config_energy_delta, "r") as jsonFileDelta:
    energy_config_delta = json.load(jsonFileDelta)
    print("load config_energy_delta")

  with open(config_energy_destination, "r") as jsonFileDestination:
    energy_config = json.load(jsonFileDestination)
    print("load config_energy_destination")

  result = merge(energy_config, energy_config_delta)
  print("merge")

  with open(config_energy_destination, "w+") as jsonFile:
    jsonFile.write(json.dumps(result))
    jsonFile.close()
    print("save")

except:
  print("error loading config",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

print("start")

stream = os.popen('sudo systemctl start energy_reader.service')
output = stream.read()
output

logger.info('done')
print('done.')
exit
