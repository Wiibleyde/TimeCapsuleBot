import sqlite3
import datetime
import os

DATA_PATH = "data/"

class CapsuleObject:
    def __init__(self, id, userDiscordId, writingDate, discoveryDate, message):
        self.id = id
        self.userDiscordId = userDiscordId
        self.writingDate = writingDate
        self.discoveryDate = discoveryDate
        self.message = message

    def __str__(self):
        return f"Id : {self.id}\nUserDiscordId : {self.userDiscordId}\nWritingDate : {self.writingDate}\nDiscoveryDate : {self.discoveryDate}\nMessage : {self.message}"
    
    def __getattribute__(self,__name: str):
        return object.__getattribute__(self, __name)

class CapsuleManagerService:
    def __init__(self,filename):
        self.filename = DATA_PATH + filename
        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH)
        self.createTable()


    def getDate(self):
        return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    def readDate(self,date:str):
        return datetime.datetime.strptime(date,"%d/%m/%Y %Hh%M")

    def createTable(self):
        with sqlite3.connect(self.filename) as conn:
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS capsules (id INTEGER PRIMARY KEY AUTOINCREMENT, userDiscordId INTEGER, writingDate TEXT, discoveryDate TEXT, message TEXT)")
            conn.commit()
            c.close()

    def addCapsule(self,userDiscordId,discoveryDate,message):
        with sqlite3.connect(self.filename) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO capsules (userDiscordId,writingDate,discoveryDate,message) VALUES (?,?,?,?)",(userDiscordId,self.getDate(),discoveryDate,message))
            conn.commit()
            c.close()
    
    def getCapsules(self):
        with sqlite3.connect(self.filename) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM capsules")
            capsules = c.fetchall()
            c.close()
            return capsules