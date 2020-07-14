
defaultId = 11

class EnergyReading:
    def __init__(self, reading):
        if len(reading)>15:
            self.Id = int(reading[0])
            self.RealPower1 = float(reading[1])
            self.AppaPower1 = float(reading[2]) 
            self.Irms1 = float(reading[3]) 
            self.Vrms1 = float(reading[4]) 
            self.PowerFact1 = float(reading[5])
            self.RealPower2 = float(reading[6])
            self.AppaPower2 = float(reading[7]) 
            self.Irms2 = float(reading[8]) 
            self.Vrms2 = float(reading[9]) 
            self.PowerFact2 = float(reading[10])
            self.RealPower3 = float(reading[11])
            self.AppaPower3 = float(reading[12]) 
            self.Irms3 = float(reading[13])
            self.Vrms3 = float(reading[14]) 
            self.PowerFact3 = float(reading[15])
            self.Items = 1
        else:
            self.Id = defaultId
            self.RealPower1 = 0
            self.AppaPower1 = 0
            self.Irms1 = 0
            self.Vrms1 = 0
            self.PowerFact1 = 0
            self.RealPower2 = 0
            self.AppaPower2 = 0 
            self.Irms2 = 0 
            self.Vrms2 = 0 
            self.PowerFact2 = 0
            self.RealPower3 = 0
            self.AppaPower3 = 0
            self.Irms3 = 0
            self.Vrms3 = 0
            self.PowerFact3 = 0
            self.Items = 1

    def addReading(self, reading):
        if len(reading)>15:
            self.Items += 1
            self.RealPower1 += self.calcExtra(self.RealPower1, reading[1], self.Items)
            self.AppaPower1 += self.calcExtra(self.AppaPower1, reading[2], self.Items)
            self.Irms1 += self.calcExtra(self.Irms1, reading[3] ,self.Items)
            self.Vrms1 += self.calcExtra(self.Vrms1, reading[4] ,self.Items)
            self.PowerFact1 += self.calcExtra(self.PowerFact1, reading[5] ,self.Items)
            self.RealPower2 += self.calcExtra(self.RealPower2,reading[6],self.Items)
            self.AppaPower2 += self.calcExtra(self.AppaPower2, reading[7] ,self.Items)
            self.Irms2 += self.calcExtra(self.Irms2, reading[8] ,self.Items)
            self.Vrms2 += self.calcExtra(self.Vrms2, reading[9] ,self.Items)
            self.PowerFact2 += self.calcExtra(self.PowerFact2, reading[10] ,self.Items)
            self.RealPower3 += self.calcExtra(self.RealPower3,reading[11],self.Items)
            self.AppaPower3 += self.calcExtra(self.AppaPower3, reading[12] ,self.Items)
            self.Irms3 += self.calcExtra(self.Irms3, reading[13] ,self.Items)
            self.Vrms3 += self.calcExtra(self.Vrms3, reading[14] ,self.Items)
            self.PowerFact3 += self.calcExtra(self.PowerFact3, reading[15] ,self.Items)
        elif len(reading)>0:
             print("Reading Incorrect "+reading[0]+":"+str(len(reading)))
        else:
             print("Reading empty")
    
    def calcExtra(self, org, new, items):
        #print('org:{0} new:{1} items:{2}'.format(org, new, items))
        return float((float(new) - float(org))/float(items))

    def getReading(self):
        printReading = "{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13} {14} {15}"
        return printReading.format(self.Id,self.RealPower1,self.AppaPower1,self.Irms1,self.Vrms1,self.PowerFact1,self.RealPower2,self.AppaPower2,self.Irms2,self.Vrms2,self.PowerFact2,self.RealPower3,self.AppaPower3,self.Irms3,self.Vrms3,self.PowerFact3)

