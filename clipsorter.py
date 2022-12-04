import base64
import os
import requests
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
from datetime import datetime 
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DIRECTORY = "F:\Valorant"
REGION = "na"
GLZ_URL = f"https://glz-{REGION}-1.{REGION}.a.pvp.net"
PD_URL = f"https://pd.{REGION}.a.pvp.net"

mapidlist = ["Ascent", "Duality", "Foxtrot", "Canyon", "Triad", "Port", "Pitt", "Bonsai"]
maplist = ["Ascent", "Bind", "Breeze", "Fracture", "Haven", "Icebox", "Pearl", "Spilt"]
headers = {}

try:
    for m in maplist:
        path = os.path.join(DIRECTORY, m)
        os.mkdir(path)
except:
    pass

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
        print(f"No match id found. {response}")
        return 0

def get_coregame_stats():
    response = requests.get(
        GLZ_URL + f"/core-game/v1/matches/{get_coregame_match_id()}", headers=get_headers(), verify=False).json()
    return response

# try:
#     print(maplist[(mapidlist.index((str(get_coregame_stats()['MapID']).split('/'))[-1]))] + " - " + (datetime.today().strftime('%m') + '∕' + datetime.today().strftime('%d') + '∕' + datetime.today().strftime('%Y') + " " + datetime.today().strftime('%H') + "∶" + datetime.today().strftime('%M')))
# except:
#     pass

class Watcher:
    DIRECTORY_TO_WATCH = DIRECTORY

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
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
            try:
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
                shutil.move(event.src_path, (subdir + "\\" + (maplist[(mapidlist.index((str(get_coregame_stats()['MapID']).split('/'))[-1]))] + " - " + (datetime.today().strftime('%m') + '∕' + datetime.today().strftime('%d') + '∕' + datetime.today().strftime('%Y') + " " + datetime.today().strftime('%H') + "∶" + datetime.today().strftime('%M')))) + "∶" + datetime.today().strftime('%S') + '.' + (event.src_path).split('\\')[-1].split('.')[-1])
            except:
                pass

if __name__ == '__main__':
    w = Watcher()
    w.run()