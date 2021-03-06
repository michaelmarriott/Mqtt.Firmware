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
import shutil 
from jsonmerge import merge

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

def download_url(url, save_path, chunk_size=1024):
  print("download_url")
  try:
    dr = requests.get(url)
    print("..............")
    print(dr)
    print(dr.headers['content-type'])
    print(dr.encoding)
    print('save file')
    print(save_path)
    with open(save_path, 'wb') as fd:
      print("save_path")
      for chunk in r.iter_content(chunk_size=chunk_size):
        fd.write(chunk)     
  except:
    print("error loading firmware config",sys.exc_info()[0])


def latest_version(url,current_version):
  url_version = url+"?version="+str(current_version)
  r = requests.get(url_version)
  json = r.json()
  if current_version != json["version"]:
    return json["version"]
  return None

def update_json():
  with open('config.json', 'w') as outfile:
    json.dump(config, outfile, indent=4)


try:
  with open("config.json", "r") as jsonFile:
    config = json.load(jsonFile)
except:
  print("error loading config",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

try:
  with open("../appsettings.json", "r") as jsonFile:
    appsettings = json.load(jsonFile)
    config = merge(config, appsettings)
except:
  print("error loading config",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

try:
  url = config['url']
  version = config['version']
except:
  print("error config",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

try:
  print("Firmware Setup")
  print(url)
  time.sleep(2)
  while 1:
    try:
      new_version = latest_version(url,version)
      print("new_version")
      print(new_version)
      if new_version != None and new_version != "None":
        logger.error('downloading') 
        config['version'] = new_version
        download_url(url+'/'+str(new_version),config['savepath'])
        print('downloaded')
        
        try:
          shutil.rmtree(config['unzippath']+'/install')
        except:
          print("Error occurred::: ",sys.exc_info()) 

        with zipfile.ZipFile(config['savepath'], 'r') as zip_ref:
          zip_ref.extractall(config['unzippath'])

        print(config['setup'])

        stream = os.popen('python '+ config['setup'])
        output = stream.read()
        output

        print('update_json')
        update_json()
        
      time.sleep(wait)
    except:
      print("Error occurred::: ",sys.exc_info()) 
      logger.error(sys.exc_info()[0]) 
      logger.error(sys.exc_info()[-1])
      time.sleep(2)       
        
except (IndexError):
  print("No data received within serial timeout period")
# handle app closure
except (KeyboardInterrupt):
  print("Interrupt received")
except (RuntimeError):
  print("uh-oh! time to die") 



