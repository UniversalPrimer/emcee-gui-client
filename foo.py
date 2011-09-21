#!/usr/bin/env python2.6
import os
import util
import pushy


def pushyRecieved(obj,var):

    print "Received: " + str(var)




def start():


    con = pushy.PushyClient('test', 4000, 'stream', callback=pushyRecieved)
    con.connect()

    

print "starting"

start()



