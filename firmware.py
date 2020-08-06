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
auth_url= ''
token= ''
username=''
pwd=''
client_id=''
version = 0
wait = 600

def download(url,username,version, save_path, token, chunk_size=1024):
  print("download...")
  try:
    url_version = url+"/firmware/"+username+"/"+str(version)
    url_token = 'Bearer '+token+''
    print(url_version)
    dr = requests.get(url_version, headers={'Authorization': url_token})
    print(download)
    if dr.status_code >= 400:
      return False
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
    print("error loading firmware config:download_url:",sys.exc_info()[0])
    return False
  return True

def get_latest_version(url,username, current_version,token):
  url_version = url+"/firmware/"+username+"?version="+str(current_version)
  print(url_version)
  
  url_token = 'Bearer '+token+''
  print(url_token)
  r = requests.get(url_version, headers={'Authorization': url_token })

  print(r.text)
  json = r.json()
  if current_version != json["version"]:
    return json["version"]
  return None

def get_token(auth_url, username, password,client_id):
  try:
    body = {'username':username,'password':password, 'client_id': client_id}
    r = requests.post(auth_url+"/device/token", json=body) 
    text = r.text
    return text
  except:
    print("Error occurred::: ",sys.exc_info()) 
    print("error get_token:",sys.exc_info()[0])

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
  print("Error occurred: ",sys.exc_info()) 
  print("error loading config",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

try:
  url = config['url']
  auth_url = config['auth_url']
  version = config['version']
  client_id = config['client_id']
  username = config['username']
  pwd = config['pwd']
except:
  print("Error occurred: ",sys.exc_info()) 
  print("error config",sys.exc_info()[0])
  logger.error(sys.exc_info()[0])

try:
  print("Firmware Setup")
  print(url)
  print(auth_url)
  print(username)
  time.sleep(2)
  while 1:
    try:
      token = get_token(auth_url, username, pwd, client_id)
      new_version = get_latest_version(url, username, version, token)
      print("new_version")
      print(new_version)
      if new_version != None and new_version != "None":
        logger.error('downloading') 
        config['version'] = new_version
        success = download(url,username,str(new_version),config['savepath'],token)
        if success == True:
          print('downloaded')        
          try:
            shutil.rmtree(config['unzippath']+'/install')
          except:
            print("Error occurred shutil.rmtree ::: ",sys.exc_info()) 

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
      print("Error occurred in loop::: ",sys.exc_info()) 
      logger.error(sys.exc_info()[0]) 
      logger.error(sys.exc_info()[-1])
      time.sleep(wait)       
        
except (IndexError):
  print("No data received within serial timeout period")
# handle app closure
except (KeyboardInterrupt):
  print("Interrupt received")
except (RuntimeError):
  print("uh-oh! time to die") 



