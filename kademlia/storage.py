import time
import tkinter as tk
from tkinter import filedialog
import os
import base64
import hashlib

class Storage():

    def digest(self,string):
        if not isinstance(string, bytes):
            string = str(string).encode('utf8')
        return hashlib.sha1(string).digest()

    def upload(self,path=None):
        if path is None:
            file_path = filedialog.askopenfilename()
        else:
            file_path = path
        with open(file_path, "rb") as in_file:
            out_file = base64.b64encode(in_file.read())
        return out_file

    def download(self,name,data):
        path = os.getcwd()
        try:
            os.mkdir(path+"/Storage")
        except OSError:
            new_data = base64.b64decode(data)
            if '.txt' in name:
                file1 = open(path+"/Storage/"+name, "w")
                file1.write(new_data.decode("utf-8"))
            else:
                file1 = open(path+"/Storage/"+name, "wb")
                file1.write(new_data)
            file1.close()
            return path+"/Storage/"+name
        else:
            new_data = base64.b64decode(data)
            if '.txt' in name:
                file1 = open(path+"/Storage/"+name, "w")
                file1.write(new_data.decode("utf-8"))
            else:
                file1 = open(path+"/Storage/"+name, "wb")
                file1.write(new_data)
            file1.close()
            return path+"/Storage/"+name

    def find_file(self,key):
        mypath = os.getcwd()+"/Storage/"
        files = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
        for f in files:
            if self.digest(f)==key:
                return True
        return False

    def get_path(self, name):
        mypath = os.getcwd() + "/Storage/"
        files = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
        for f in files:
            if f == name:
                return mypath + name
        return None

    def get_all(self):
        path = os.getcwd()+"/Storage/"
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        dfiles = []
        for f in files:
            dfiles.append({"name":f,"path":path+f})
        return dfiles