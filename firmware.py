#!/usr/bin/python
import requests 
import sys
import os
import time
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import json
import zipfile


logger = logging.getLogger('firmware_logger')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('firmware_log.log', maxBytes=2000, backupCount=10)
logger.addHandler(handler)

fmt = '%Y-%m-%d %H:%M:%S'
seconds = 298
div_second = 300
current_holder = 0
config = lambda: None
url = ''
version = 0
wait = 600

def download_url(url, save_path, chunk_size=128):
  print("download_url")
  r = requests.get(url, stream=True)
  print(r)
  print(r.headers['content-type'])
  print(r.encoding)
  print('save file')
  print(save_path)
  with open(save_path, 'wb') as fd:
    print("save_path")
    for chunk in r.iter_content(chunk_size=chunk_size):
      fd.write(chunk)     


def latest_version(url,current_version):
  print(url)
  print("latest_version")
  url_verision = url+"?version="+str(current_version)
  print(url_verision)
  r = requests.get(url_verision)
  json = r.json()
  if current_version != json["version"]:
    return json["version"]

  return None

def updatejson():
  with open('config.json', 'w') as outfile:
    json.dump(config, outfile, indent=4)

try:
  with open("config.json", "r") as jsonFile:
    config = json.load(jsonFile)
    url = config['url']
    version = config['version']
except:
  print("error loading config",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

try:
  print("Firmware Setup")
  print(url)
  time.sleep(2)
  while 1:
    try:
      version = latest_version(url,version)
      print("version")
      print(version)
      if version != None:
        print("UPDATE")
        config['version'] = version
        download_url(url+'/'+str(version),config['savepath'])

        with zipfile.ZipFile(config['savepath'], 'r') as zip_ref:
          zip_ref.extractall(config['unzippath'])
          execfile(config['setup'])
        
        updatejson()
        
      time.sleep(wait)
    except:
      print("Error occurred: ",sys.exc_info()[0]) 
      logger.error(sys.exc_info()[0])
      time.sleep(2)
        
        
except (IndexError):
  print("No data received within serial timeout period")
# handle app closure
except (KeyboardInterrupt):
  print("Interrupt received")
except (RuntimeError):
  print("uh-oh! time to die") 



