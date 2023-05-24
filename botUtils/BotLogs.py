import os
import sqlite3
import datetime

LOGS_PATH = "logs/"

class BotLoggerService:
    def __init__(self, filename):
        self.filename = LOGS_PATH + filename
        if not os.path.exists(LOGS_PATH):
            os.makedirs(LOGS_PATH)
        self.createTable()

    def getDate(self):
        return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    def createTable(self):
        with sqlite3.connect(self.filename) as conn:
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, userDiscordId INTEGER, date TEXT, command TEXT, args TEXT)")
            conn.commit()
            c.close()

    def addLog(self,userDiscordId,command,args=None):
        with sqlite3.connect(self.filename) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO logs (userDiscordId,date,command,args) VALUES (?,?,?,?)",(userDiscordId,self.getDate(),command,args))
            conn.commit()
            c.close()

    def getLogs(self):
        with sqlite3.connect(self.filename) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM logs")
            logs = c.fetchall()
            c.close()
            return logs
        
    def get25LastLogs(self):
        with sqlite3.connect(self.filename) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 25")
            logs = c.fetchall()
            c.close()
            return logs
        
    def get25LastLogsByUser(self,discordId):
        with sqlite3.connect(self.filename) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM logs WHERE userDiscordId = ? ORDER BY id DESC LIMIT 25",(discordId,))
            logs = c.fetchall()
            c.close()
            return logs
        
    def getLogsByUserDiscordId(self,discordId):
        with sqlite3.connect(self.filename) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM logs WHERE userDiscordId = ?",(discordId,))
            logs = c.fetchall()
            c.close()
            return logs
        
    def getLogsByCommand(self,command):
        with sqlite3.connect(self.filename) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM logs WHERE command = ?",(command,))
            logs = c.fetchall()
            c.close()
            return logs