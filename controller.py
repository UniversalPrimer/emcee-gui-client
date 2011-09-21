from PyQt4.QtCore import *
from PyQt4.QtGui import *

import gui
import os
import presentation
import plugins
import util
import ape
import pushy
import json
import cuecumber

class Controller(QObject):
    
    def __init__(self):
        QObject.__init__(self)
        self.loadDefaultSettings()
        self.screens = ScreenController()
        self.mainview = gui.MainWindow(self)
        self.beamview = gui.BeamWindow(self)
        self.prefview = gui.PreferencesWindow(self)
        self.streamStarted = False
        self.bcconnection = None
        self.presentation = None
        self.currentslide = None        

        # setup the main window
        self.mainview.setCentralWidget(gui.LoadPresentationWidget(self))

        # enable the default pointers
        self.pointers = {}
        self.drawingpointers = []

        for pointerplugin in plugins.pointer:
            pointer = pointerplugin.pointer(self)
            self.pointers[pointerplugin] = pointer
            if pointerplugin.enabledefault:
                self.enablePointer(pointerplugin)

        self.drawing = DrawingController(self.drawingpointers,self.beamview,self)   


    # application
    def start(self): 
        if self.screens.countScreens() > 1:
            self.screens.moveToScreen(1,self.beamview)
            #self.beamview.showFullScreen()
        self.beamview.show()
        self.mainview.show()

    def quitApplication(self):        
        self.beamview.close()
        self.mainview.close()
        for (pointermodule, pointer) in self.pointers.items():
            pointer.disable()

    def mainClosed(self):
        question = QMessageBox.question(self.mainview, self.tr("Application Close"), self.tr("Are you sure to quit?"), QMessageBox.No, QMessageBox.Yes)
        if question == QMessageBox.Yes:
            self.beamview.close()
            return True
        else:
            return False

    def aboutApp(self):
        QMessageBox.about(self.mainview, self.tr("emcee"),self.tr("emcee\n\nQt version: %s\nPyQt version: %s\nApplication version: %s" % (QT_VERSION_STR, PYQT_VERSION_STR, QApplication.applicationVersion())))

    def setStatus(self,message):
        self.mainview.status.showMessage(message)

    def loadDefaultSettings(self):
        settings = QSettings()
        defaults = {"pointercolor": QColor(255, 0, 0),
                    "pointersize": 20,
                    "linecolor": QColor(0,0,0),
                    "linewidth": 10,
                    }
        for (k,v) in defaults.items(): 
            settings.setValue(k,settings.value(k,v))

    # presentations
    def newPresentation(self):
        self.mainview.setCentralWidget(gui.NewPresentationWidget(self))

    def closePresentation(self):
        if self.presentation and self.presentation.saveneeded:
            print "Todo: Ask for save"
        self.mainview.showToolbar(False)
        self.mainview.setCentralWidget(gui.LoadPresentationWidget(self))

    def openPresentation(self):
        filename = QFileDialog.getOpenFileName(self.mainview, self.tr("Open Presentation"), os.getcwd(), self.tr("emcee Presentation (*.paj)"))
        if filename:
            pres = presentation.Presentation(str(filename))
            self.setPresentation(pres)
            self.presentation.emit(SIGNAL("changed()"))

    def openRemotePresentation(self):
        print "NYI: Remote Open"

    def savePresentation(self):
        if self.presentation:
            if self.presentation.filename:
                self.presentation.save()
            else:
                self.saveAsPresentation()

    def saveAsPresentation(self):
        if self.presentation:
            filename = QFileDialog.getSaveFileName(self.mainview, self.tr("Save Presentation"), os.getcwd() + "/" + self.presentation.suggestedFileName() + ".paj", self.tr("emcee Presentation (*.paj)"))
            if filename:
                self.presentation.save(str(filename))

    def setPresentation(self,presentation):
        self.presentation = presentation
        self.currentslide = presentation.defaultSlide
        self.nextslide = presentation.defaultSlide
        self.mainview.setTitle(presentation.title)
        self.mainview.setCentralWidget(gui.PresentationWidget(self))
        self.mainview.showToolbar(True)
        self.emit(SIGNAL("updateSlides()"))

    def createPresentation(self,title,name,email,forclass,organization):
        p = presentation.Presentation()
        p.title = str(title) if len(title) else str(p.title)
        p.name = str(name)
        p.email = str(email)
        p.forclass = str(forclass)
        p.organization = str(organization)
        self.setPresentation(p)

    # slide control            
    def addSlide(self, mimetype):
        plugin = plugins.mimehandlers[mimetype]
        if plugin.source == "file":
            filename = QFileDialog.getOpenFileName(None, self.tr("Select file"), os.getcwd(), "%s (*.%s)" % (plugin.name, plugin.filetype))
            if filename:
                source = presentation.Source(str(filename),mimetype)
                self.presentation.addSource(source)
        elif plugin.source == "internal":
             source = presentation.Source(None,mimetype)
             self.presentation.addSource(source)

    def nextSlide(self):
        if self.presentation:
            self.setCurrentSlide(self.presentation.nextindex)
            self.setNextSlide(self.presentation.nextindex+1)
            self.emit(SIGNAL("setNextSlide(int)"),self.presentation.nextindex)

    def previousSlide(self):
        if self.presentation:
            self.setNextSlide(self.presentation.currentindex)
            self.setCurrentSlide(self.presentation.currentindex-1)
            self.emit(SIGNAL("setNextSlide(int)"),self.presentation.nextindex)

    def setCurrentSlide(self, index):
        if index >= 0 and index < len(self.presentation.slides):
            self.presentation.currentindex = index
            self.currentslide = self.presentation.getSlide(index)
        else:
            self.currentslide = self.presentation.defaultSlide
        self.emit(SIGNAL("updateSlides()"))
        self.drawing.drawClear()
        
        if self.streamStarted:
            cuecumber.cuepointInject({"type": "slides/change", "identifier": self.currentslide.source.identifier(), "index":  self.presentation.currentindex})

        if self.bcconnection:
            self.bcconnection.send({"type": "slides/change", "identifier": self.currentslide.source.identifier(), "index":  self.presentation.currentindex})

    def setNextSlide(self, index):
        if index >= 0 and index < len(self.presentation.slides):
            self.presentation.nextindex = index
            self.nextslide = self.presentation.getSlide(index)
        else:
            self.nextslide = self.presentation.defaultSlide
        self.emit(SIGNAL("updateSlides()"))

    # chat
    def chatSend(self,chat):
        if len(self.presentation.name):
            who = self.presentation.name
        else:
            who = "Teacher"
            
        if self.bcconnection:
            self.bcconnection.send({"type": "chat/public-msg", "msg": unicode(chat), "nickname": unicode(who)})
            self.emit(SIGNAL("chatRecieved(QString)"),"<b>%s</b>: %s" % (who,chat))
        else:
            self.emit(SIGNAL("chatRecieved(QString)"),"<i>Not connected</i>" )

# XXX        
    # ape
#    def apeRecieved(self,obj,var):
#        jvar = json.loads(var)
#        if jvar["type"] == "chat/public-msg":
#             self.emit(SIGNAL("chatRecieved(QString)"),"<b>%s</b>: %s" % (jvar["nickname"],jvar["msg"]))
        
    def pushyRecieved(self,obj,var):
        print "Received: " + str(var)

    # broadcast
    def startBroadcast(self):
       settings = QSettings()

       # TODO re-instate the comet connection
       # it connects but doesn't send correctly 
       # (it needs to nest the json as the .msg of another json string, and include the session_id)
       # (we actually don't need session_ids to be sent for a raw connection)
#       self.bcconnection = pushy.PushyClient('pushyl.uprimer.org', 4000, 'stream', callback=self.pushyRecieved)
#       self.bcconnection.connect()

       self.streamStarted = True

       cuecumber.startStream()
       
    def endBroadcast(self):
        cuecumber.stopStream()
        if self.bcconnection:
            self.bcconnection.close()
            self.bcconnection = None

    # pointers
    def enablePointer(self,pointerplugin):
        if self.pointers[pointerplugin].enable() and pointerplugin.capabilities.count("draw"):
            self.drawingpointers.append(self.pointers[pointerplugin]) 

    def disablePointer(self,pointer):
        self.pointers[pointer].disable()


class ScreenController():

    def __init__(self):
        self.desktop = QDesktopWidget()
        self.geometry = []
        primary = self.desktop.screenGeometry(self.desktop.primaryScreen()).topLeft()

        for i in range(0,self.desktop.numScreens()):
            self.geometry.append(self.desktop.screenGeometry(i).topLeft()-primary)

    def moveToScreen(self,screen,widget):
        widget.move(self.geometry[screen])

    def countScreens(self):
        return self.desktop.numScreens()

class DrawingController(QThread):
    
    def __init__(self,pointers,beamview,controller):
        QThread.__init__(self)
        self.pointers = pointers
        self.beamview = beamview
        self.controller = controller
        self.drawing = False
        self.points = []
        self.current = -1
        self.start()

    def drawBegin(self):
        self.current += 1
        self.points.append([])
        self.points[self.current] = []
        self.drawing = True

    def drawEnd(self):
        if self.drawing:
            self.drawing = False
            if self.controller.bcconnection:
                self.controller.bcconnection.send({"type": "draw/lines", "lines": self.points})

    def drawClear(self):
        self.points = []
        self.current = -1
        self.beamview.update()
        if self.controller.bcconnection:
            self.controller.bcconnection.send({"type": "draw/clear"})

    def run(self):
        while True:
            if len(self.pointers):
                pointerset = False
                for pointer in self.pointers:
                    xy = pointer.xy()
                    if xy:
                        if self.drawing:
                            self.points[self.current].append((xy[0],xy[1]))
                            
                        self.beamview.setPointer(xy[0],xy[1])
                            
                        pointerset = True
                        break

                if not pointerset:
                    self.beamview.clearPointer()
                        
                self.beamview.setPaths(self.points)


                self.msleep(33)
            else:
                self.sleep(10)    
        


