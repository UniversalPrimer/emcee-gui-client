import cwiid
import time
import math
#import Queue
from threading import Thread

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class pointer(QThread):

    def __init__(self, controller):
        QThread.__init__(self)
        self.controller = controller

    def __del__(self):
        self.disable()

    def enable(self):

        self.controller.setStatus("Press 1 & 2 on the Wiimote simultaneously to find it")
        self.connect(self,SIGNAL("setStatus(QString)"), self.controller.setStatus)

        self.w = None
        self.valid = False
        self.coordinatepool = []
        self.x = 0
        self.y = 0
        self.battery = 0
        self.alive = False
        self.start()
       
        return True

    def disable(self):
        self.finished = True
        return True

    def battery(self):
        return (self.battery/cwiid.BATTERY_MAX)*100

    def xy(self):
        if self.valid:
            return (self.x,self.y)
        else:
            return None

    ####

    def run(self):
            self.alive = True
            try:
                self.w = cwiid.Wiimote()
            except Exception as e:
                self.emit(SIGNAL("setStatus(QString)"),QString(str(e)))
                self.alive = False

            if self.alive:
                self.connect(self,SIGNAL("left()"),self.controller.previousSlide)
                self.connect(self,SIGNAL("right()"),self.controller.nextSlide)
                self.connect(self,SIGNAL("draw()"),lambda: self.controller.drawing.drawBegin())
                self.connect(self,SIGNAL("keyup()"),lambda: self.controller.drawing.drawEnd())
                self.connect(self,SIGNAL("clear()"),lambda: self.controller.drawing.drawClear())


                # Set Wii Parameters to get
                self.w.enable(cwiid.FLAG_MESG_IFC)
                self.w.rpt_mode = cwiid.RPT_IR | cwiid.RPT_BTN
                self.finished = False
                self.emit(SIGNAL("setStatus(QString)"),QString("Wiimote connected"))

                while not self.finished:
                    self.usleep(100)
                    try:
                        messages = self.w.get_mesg() 
                        for mesg in messages:  
                            if mesg[0] == cwiid.MESG_IR: 
                                self.handle_ir(mesg[1])                  
                            elif mesg[0] == cwiid.MESG_BTN: 
                                self.handle_key(mesg[1])

                        self.battery = self.w.state["battery"]
                    except Exception:
                        self.finished = True
                        pass
                if self.w:
                    self.w.close()
        

    def handle_ir(self,mesg):
        points = [None,None]

        # add the two largest points to points
        for s in mesg:
            if s:
                for i,p in enumerate(points):
                    if p:
                        if p['size'] < s['size']:
                            points[i] = s
                            break
                    else:
                        points[i] = s
                        break

        if points[0] and points[1]:   
            x1 = float(points[0]['pos'][0])/cwiid.IR_X_MAX
            y1 = float(points[0]['pos'][1])/cwiid.IR_Y_MAX
            x2 = float(points[1]['pos'][0])/cwiid.IR_X_MAX
            y2 = float(points[1]['pos'][1])/cwiid.IR_Y_MAX
          
            midx = 1 - ((x1+x2) / 2)
            midy = (y1+y2) / 2
            ang = math.atan2((y1-y2)*0.75,x1-x2)
            dist = math.sqrt(math.pow((y1-y2)*0.75,2)+math.pow(x1-x2,2))
            self.valid = True
        else:
            self.valid = False     

        if self.valid:
            # rotate the points
            cx = 0.5 - midx
            cy = 0.5 - midy
            if ang > math.pi / 2:
                ang -= math.pi
            elif ang < -math.pi / 2:
                ang += math.pi

            x = cx * math.cos(ang) - cy * math.sin(ang)
            y = cx * math.sin(ang) + cy * math.cos(ang)
            midx = 0.5 + x
            midy = 0.5 + y

            self.coordinatepool.append((midx,midy))

            while len(self.coordinatepool) > 10:
                self.coordinatepool.pop(0)
                        
            x = 0
            y = 0

            for i in self.coordinatepool:
                x += i[0]
                y += i[1]

            self.x = x/float(len(self.coordinatepool))
            self.y = y/float(len(self.coordinatepool))
        else:
            self.coordinatepool = []

    def handle_key(self,p):
        if p == cwiid.BTN_RIGHT:
            self.emit(SIGNAL("right()"))
        elif p == cwiid.BTN_LEFT:
            self.emit(SIGNAL("left()"))
        elif p == cwiid.BTN_A:
            self.emit(SIGNAL("draw()"))
        elif p == cwiid.BTN_B:
            self.emit(SIGNAL("clear()"))
        elif p == 0:
            self.emit(SIGNAL("keyup()"))
        else:
            print "Unhandled keypress: %x" % p

#       BTN_2=0x0001
#	    BTN_1=0x0002
#	    BTN_B=0x0004
#	    BTN_MINUS=0x0010
#	    BTN_HOME=0x0080
#	    BTN_DOWN=0x0400
#	    BTN_UP=0x0800
#	    BTN_PLUS=0x1000




plugintype     = 'pointer'
name           = 'Wiimote'
description    = 'Bluetooth Wiimote'
capabilities   = ['control','draw','attention','battery']
enabledefault  = False

