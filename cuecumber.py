#!/usr/bin/env python

from ctypes import *
from time import sleep
from flv_helper import *
import json

libcuecumber = None

def cuepointInject(msg):
    
    sd = scriptdata_create("onCuePoint")
    scriptdata_addpropstr(sd, "msg", json.dumps(msg))
    ft = flvtag_create(0, sd)
    prevsize = so_fixsize(ft)
    ftt = flv_tag.build(ft)
    libcuecumber.insert_cuepoint(prevsize, ftt)

def startStream():
    global libcuecumber
    libcuecumber = cdll.LoadLibrary("libcuecumber.so")

    print "starting stream"
    libcuecumber.cuecumber_init()

#    slide_change_cuepoint(3)

def stopStream():
    libcuecumber.cuecumber_stop()
    libcuecumber.cuecumber_exit()
