import yaml
import os

class ConfigService:
    def __init__(self,filename):
        self.filename = filename
        if not os.path.exists(self.filename):
            self.createConfigFile()
        self.config = self.loadConfigFile()

    def createConfigFile(self):
        with open(self.filename,'w') as f:
            yaml.dump({
                "Bot_token":"Your bot token",
                "Capsule_channel":"capsule reveal channel id"
            },f)

    def loadConfigFile(self):
        with open(self.filename,'r') as f:
            return yaml.load(f,Loader=yaml.FullLoader)
        
    def getBotToken(self):
        return self.config["Bot_token"]
    
    def getCapsuleChannel(self):
        return self.config["Capsule_channel"]
    
    def setBotToken(self,token):
        self.config["Bot_token"] = token
        self.saveConfigFile()
        return True
    
    def setCapsuleChannel(self,channelId):
        self.config["Capsule_channel"] = channelId
        self.saveConfigFile()
        return True

    def saveConfigFile(self):
        with open(self.filename,"w") as f:
            f.write(yaml.dump(self.config))
        return True
