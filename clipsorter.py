import base64
import os
import requests
import time
import shutil
import urllib3
import sys
import tkinter as tk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime 
from tkinter import filedialog
from win32com.client import Dispatch
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# pyinstaller --onefile --icon=Icon.ico --noconsole clipsorter.py --hidden-import "watchdog" --hidden-import "datetime" --hidden-import "tkinter" --hidden-import "win32com"

DIRECTORY = ""
REGION = "na"
GLZ_URL = f"https://glz-{REGION}-1.{REGION}.a.pvp.net"
PD_URL = f"https://pd.{REGION}.a.pvp.net"

mapidlist = ["Ascent", "Duality", "Foxtrot", "Canyon", "Triad", "Port", "Pitt", "Bonsai"]
maplist = ["Ascent", "Bind", "Breeze", "Fracture", "Haven", "Icebox", "Pearl", "Spilt"]
headers = {}

def get_lockfile():
    try:
        with open(os.path.join(os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Config\lockfile')) as lockfile:
            data = lockfile.read().split(':')
            keys = ['name', 'PID', 'port', 'password', 'protocol']
            return dict(zip(keys, data))
    except:
        pass

lockfile = get_lockfile()

def get_headers():
    global headers
    if headers == {}:
        local_headers = {}
        local_headers['Authorization'] = 'Basic ' + base64.b64encode(
            ('riot:' + lockfile['password']).encode()).decode()
        response = requests.get(f"https://127.0.0.1:{lockfile['port']}/entitlements/v1/token", headers=local_headers,
                                verify=False)
        entitlements = response.json()
        headers = {
            'Authorization': f"Bearer {entitlements['accessToken']}",
            'X-Riot-Entitlements-JWT': entitlements['token']
        }
    return headers

def get_puuid():
    local_headers = {}
    local_headers['Authorization'] = 'Basic ' + base64.b64encode(
        ('riot:' + lockfile['password']).encode()).decode()
    response = requests.get(f"https://127.0.0.1:{lockfile['port']}/entitlements/v1/token", headers=local_headers,
                            verify=False)
    entitlements = response.json()
    puuid = entitlements['subject']
    return puuid

def get_coregame_match_id():
    try:
        response = requests.get(
            GLZ_URL + f"/core-game/v1/players/{get_puuid()}", headers=get_headers(), verify=False).json()
        match_id = response['MatchID']
        return match_id
    except KeyError:
        return 0

def get_coregame_stats():
    response = requests.get(
        GLZ_URL + f"/core-game/v1/matches/{get_coregame_match_id()}", headers=get_headers(), verify=False).json()
    return response

if (os.path.exists('path')):
    f = open("path", "r")
    DIRECTORY = (f.read())
    f.close()
else:
    root = tk.Tk()
    root.iconbitmap(str(os.environ['SystemRoot']) + '\explorer.exe')
    root.withdraw()

    file_path = filedialog.askdirectory()

    write = open("path", "w+")
    write.write(file_path)
    write.close()
    DIRECTORY = file_path

if (DIRECTORY == ''):
    os.remove("path")
    quit()

for m in maplist:
    try:
        path = os.path.join(DIRECTORY, m)
        os.mkdir(path)
    except:
        pass

try:
    os.mkdir(os.path.join(DIRECTORY, "Menu"))
except:
    pass

startup_path = str(os.getenv('APPDATA') + r"\Microsoft\Windows\Start Menu\Programs\Startup")
dir = (sys.executable).split('\\')
tmpsubdir = ""
for i, x in enumerate(dir[:-1]):
    if (i != 0):
        tmpsubdir += "\\" + x
    else:
        tmpsubdir = x
target = sys.executable
wDir = tmpsubdir
icon = sys.executable
shell = Dispatch('WScript.Shell')
shortcut = shell.CreateShortCut(os.path.join(startup_path, "Valorant Clip Sorter.lnk"))
shortcut.Targetpath = target
shortcut.WorkingDirectory = wDir
shortcut.IconLocation = icon
shortcut.save()

class Watcher:
    DIRECTORY_TO_WATCH = DIRECTORY
    def __init__(self):
        self.observer = Observer()
    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        try:
            self.observer.start()
        except:
            try:
                os.remove("path")
            except:
                pass
            quit()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            pass

        self.observer.join()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            for m in maplist:
                try:
                    path = os.path.join(DIRECTORY, m)
                    os.mkdir(path)
                except:
                    pass

                try:
                    os.mkdir(os.path.join(DIRECTORY, "Menu"))
                except:
                    pass
            try:
                if ('errorCode' in str(get_coregame_stats())):
                    dir = (event.src_path).split('\\')
                    subdir = ""
                    for i, x in enumerate(dir[:-1]):
                        if (i != 0):
                            subdir += "\\" + x
                        else:
                            subdir = x
                    subdir += "\\Menu" 
                    historicalSize = -1
                    while (historicalSize != os.path.getsize(event.src_path)):
                        historicalSize = os.path.getsize(event.src_path)
                        time.sleep(1)
                    shutil.move(event.src_path, (subdir + "\\" + ("Menu - " + (datetime.today().strftime('%m') + '???' + datetime.today().strftime('%d') + '???' + datetime.today().strftime('%Y') + " " + datetime.today().strftime('%H') + "???" + datetime.today().strftime('%M')))) + "???" + datetime.today().strftime('%S') + '.' + (event.src_path).split('\\')[-1].split('.')[-1])
                else:
                    dir = (event.src_path).split('\\')
                    subdir = ""
                    for i, x in enumerate(dir[:-1]):
                        if (i != 0):
                            subdir += "\\" + x
                        else:
                            subdir = x
                    subdir += "\\" + maplist[(mapidlist.index((str(get_coregame_stats()['MapID']).split('/'))[-1]))]
                    historicalSize = -1
                    while (historicalSize != os.path.getsize(event.src_path)):
                        historicalSize = os.path.getsize(event.src_path)
                        time.sleep(1)
                    shutil.move(event.src_path, (subdir + "\\" + (maplist[(mapidlist.index((str(get_coregame_stats()['MapID']).split('/'))[-1]))] + " - " + (datetime.today().strftime('%m') + '???' + datetime.today().strftime('%d') + '???' + datetime.today().strftime('%Y') + " " + datetime.today().strftime('%H') + "???" + datetime.today().strftime('%M')))) + "???" + datetime.today().strftime('%S') + '.' + (event.src_path).split('\\')[-1].split('.')[-1])
            except:
                pass

if __name__ == '__main__':
    w = Watcher()
    w.run()