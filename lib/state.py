import machine
import os
import time
import ujson
import urequests
import network
import socket
import binascii
import audiovisual
#import pycom
from machine import SD
from network import WLAN
from network import Sigfox
from network import Bluetooth
from audiovisual import AV
#from L76GNSS import L76GNSS
#from pytrack import Pytrack

PARSE_BASE_URL = 'http://tracksi-parse-server.herokuapp.com'
PARSE_APPLICATION_ID = 'tracksiAppId'
PARSE_MASTER_KEY = 'tracksiMasterKey'
PARSE_REST_API_KEY = 'anykeyworks'
BLE_DEVICE_NAME = 'mytracksi'
BLE_SERVICE_LOCK = 0001
BLE_SERVICE_UNLOCK = 0002
BLE_SECRET_KEY = 'SECRET'

class State:
    def __init__(self):
        self.debug('doing state init')
        #load (or create) a local file
        sd = SD()
        os.mount(sd, '/sd')

        #sigfox setup
        sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
        self.sig = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
        self.sig.setblocking(False)
        self.sig.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)

        #py = Pytrack()
        #self.gps = L76GNSS(py)

        self.debug('trying to get state from net...')
        try:
            data = {}
            data["order"] = '-createdAt'
            data["limit"] = '1'
            headers = {'X-Parse-Application-Id': PARSE_APPLICATION_ID, 'X-Parse-REST-API-Key': PARSE_REST_API_KEY, 'Content-Type': 'application/json'}
            self.debug('sending request.')
            resp = urequests.get(PARSE_BASE_URL+'/classes/ConfigObject', headers=headers, data=ujson.dumps(data))
            config = resp.json()
            resp.close()
            self.debug('got state from net:')
            self.debug(ujson.dumps(config))
            self.write_config(config["results"][0])

        except:
            self.debug('could not get state from net.')
            try:
                f = open('/sd/config.json', 'r')
                config = f.read()
                f.close()
                if config == '':
                    self.debug('found invalid local json file, writing...')
                    config = {}
                    config["state"] = 0
                    self.write_config(config)
                else:
                    self.debug('found valid local json file:')
                    self.debug(config)
                    self.config = ujson.loads(config)
            except:
                self.debug('ERROR - could not get/create a valid config file!')
                pass

    def write_config(self, config):
        f = open('/sd/config.json', 'w+')
        f.write(ujson.dumps(config))
        f.close()
        self.config = config
        self.debug('wrote new config:')
        self.debug(ujson.dumps(config))

    def debug(self, string):
        print(string)
        #pass

    def update_config(self, state=0):
        #m_lat, m_lng = self.gps.coordinates()

        config = {}
        config["state"] = state
        #config["lat"] = m_lat
        #config["long"] = m_lng
        self.write_config(config)

    def parse_job(self, job):
        try:
            headers = {'X-Parse-Application-Id': PARSE_APPLICATION_ID, 'X-Parse-Master-Key': PARSE_MASTER_KEY}
            r = urequests.post(PARSE_BASE_URL+'/jobs/'+job, headers=headers)
            r.close()
        except:
            pass

    def unlock(self):
        self.update_config(state=0)
        self.parse_job('unlock')

    def lock(self):
        self.update_config(state=1)
        self.parse_job('lock')

    def trigger(self):
        self.update_config(state=2)
        self.parse_job('trigger')

    def notify(self):
        self.sig.send("TRACKSi")
        self.update_config(state=3)

    def upone(self):
        up = self.config["state"]+1
        self.update_config(state=up)
        try:
            data = {}
            data["state"] = up
            headers = {'X-Parse-Application-Id': PARSE_APPLICATION_ID, 'X-Parse-Master-Key': PARSE_MASTER_KEY, 'Content-Type': 'application/json'}
            rf = urequests.post(PARSE_BASE_URL+'/jobs/upone', headers=headers, data=ujson.dumps(data))
            self.debug(rf.json())
            rf.close()
            self.debug('updated job upone:' + up)
            return 'good'
        except:
            print('error with upone job')

    def getState(self):
        return self.config

    def bt_check(self):
        av = AV()
        av.blue()

        bluetooth = Bluetooth()
        bluetooth.set_advertisement(name=BLE_DEVICE_NAME, manufacturer_data=BLE_DEVICE_NAME, service_uuid=0001)

        bluetooth.advertise(True)
        srv1 = bluetooth.service(uuid=0001, isprimary=True)
        chr1 = srv1.characteristic(uuid=0002, value=5)

        if self.config["state"] == 0:
            lock_state = 0
        else:
            lock_state = 1

        def char1_cb_handler(chr):
            if chr.value() == bytes(BLE_SECRET_KEY, "utf-8"):
                if self.config["state"] == 0:
                    self.lock()
                    av.locked()
                    return 'good'
                else:
                    self.unlock()
                    av.unlocked()
                    return 'good'

        srv2 = bluetooth.service(uuid=0003, isprimary=True)
        chr2 = srv2.characteristic(uuid=0004, value=lock_state)

        char1_cb = chr2.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=char1_cb_handler)

        time.sleep(20)
        av.off()
        bluetooth.advertise(False)
