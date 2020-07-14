import json
import datetime

class RelayTimer:

  def __init__(self, config):
    print(config["timers"])
    self.config = config
    self.Timers = config["timers"]
    self.LastTimeCheck = None
    if self.Timers is None:
      self.Timers = {}
      
  def setRelayTimer(self, relay, number, data, callback):
    print("--------------------")
    print(relay)
    print(number)

    if "Timers"+str(relay) not in self.Timers:
      self.Timers["Timers"+str(relay)] = {"Timer1": {}} 
  
    timerRelay = self.Timers["Timers"+str(relay)]

    if timerRelay is None:
        self.Timers["Timer"+str(number)] = {"Timer"+str(number): {}}

    if str(data) == "0":
      timerRelay["Timer"+str(number)] = {}
    else:
      timerRelay["Timer"+str(number)] = data

    print(self.Timers)
    callback()

  def getRelayTimers(self):
    return self.Timers
  
  def getTimersString(self):
    return json.dumps(self.Timers)

  def checkRelayTimer(self, func):

    if self.Timers is None:
      return True
    print("checkRelayTimer")
    current_date_and_time = datetime.datetime.now()
    #hours = 2
   # hours_added = datetime.timedelta(hours = hours)
    date = current_date_and_time #+ hours_added

    currentTimeCheck = (int(date.strftime("%H"))*60) + (int(date.strftime("%M")) * 1)
        
    weekday = int(date.weekday())
    
    for (key, value) in self.Timers.items():
      print('key:'+ key)
      if key.startswith("Timers"):
        relay = int(key.replace("Timers", ""))
        timers = value
      
        if not(timers is None):
          for (k, item) in timers.items():
            if "Arm" in item:
              if item["Arm"] == 1:
                if item["Days"][weekday] != "-":
                  aTime = item["Time"].split(':')
                  time = (int(aTime[0]) * 60) + (int(aTime[1]) * 1)
                  if self.isTimeEvent(currentTimeCheck,time):
                    func(relay, item["Action"])

    print('TimeChecked')
    self.LastTimeCheck = currentTimeCheck

  def isTimeEvent(self, currentTimeCheck, time):
    if self.LastTimeCheck is None:
      if currentTimeCheck == time:
        return True
      else:
        return False
    if self.LastTimeCheck == currentTimeCheck:
      return False

    if self.LastTimeCheck < time and time >= currentTimeCheck: #Roll over to midnight 
      print("--------------------------------------------------")
      print("Time Event")
      print("--------------------------------------------------")
      return True
    
    return False
      
      

#//{ Action: 1, Time: "05:00", Days: "SM00TF0", Arm:1,Repeat: 1, Mode:0,Window:0,Output:0}
#     159386612 - 159386612
# {"39": "OFF", "38": "OFF", "37": "OFF", "1": "ON", "0": "OFF", "2": "ON"}
# {Timer1: {"Arm":1,"Time":"16:23","Window":0,"Days":"SM00TF0","Repeat":0,"Output":2,"Action":2},
#     Timer2: {"Arm":1,"Time":"16:23","Window":15,"Days":"SM00TF0","Repeat":0,"Output":2,"Action":2},
#     Timer3: {"Arm":1,"Time":"16:23","Window":15,"Days":"SM00TF0","Repeat":0,"Output":2,"Action":2},
#     Timer4: {"Arm":1,"Time":"16:23","Window":15,"Days":"SM00TF0","Repeat":0,"Output":2,"Action":2}
#   },{
#     Timer1: {"Arm":1,"Time":"16:23","Window":0,"Days":"SM00TF0","Repeat":0,"Output":2,"Action":2},
#     Timer2: {"Arm":1,"Time":"16:23","Window":15,"Days":"SM00TF0","Repeat":0,"Output":2,"Action":2},
#     Timer3: {"Arm":1,"Time":"16:23","Window":15,"Days":"SM00TF0","Repeat":0,"Output":2,"Action":2},
#     Timer4: {"Arm":1,"Time":"16:23","Window":15,"Days":"SM00TF0","Repeat":0,"Output":2,"Action":2}
#   }
#  }
#  Timer4 {"Arm":1,"Time":"16:23","Window":15,"Days":"SM00TF0","Repeat":0,"Output":2,"Action":2}
# 11 0.00 0.06 0.07 0.81 0.000 0.00 0.05 0.06 0.84 0.000 0.01 0.20 0.25 0.83 0.000
# 159386612 - 159386612
# {"39": "OFF", "38": "OFF", "37": "OFF", "1": "ON", "0": "OFF", "2": "ON"}
# Received message 'ON' on topic 'cmnd/Sensor2/POWER/1' with QoS 0
# power
# --------------------
# 1
# ON

