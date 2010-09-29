from PyQt4.QtCore import *
from PyQt4.QtGui import *

import gui
import os
import presentation
import plugins
import util

class Controller(QObject):
    
    def __init__(self):
        QObject.__init__(self)

        self.screens = ScreenController()
        self.mainview = gui.MainWindow(self)
        self.beamview = gui.BeamWindow(self)
        self.presentation = None
        self.currentslide = None
        self.nextslide = None

        # setup the main window
        self.mainview.setCentralWidget(gui.LoadPresentationWidget(self))

        # enable the default pointers
        self.pointers = {}
        self.drawingpointers = []

        for pointerplugin in plugins.pointer:
            pointer = pointerplugin.pointer(self)
            if pointerplugin.enabledefault:
                if pointer.enable() and pointerplugin.capabilities.count("draw"):
                    self.drawingpointers.append(pointer) 
            self.pointers[pointerplugin] = pointer

        self.drawing = DrawingController(self.drawingpointers,self.beamview)   


    # application
    def start(self): 
        if self.screens.countScreens() > 1:
            self.screens.moveToScreen(1,self.beamview)
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
        QMessageBox.about(self.mainview, self.tr("emcee"),self.tr("Qt version: %s\nPyQt version: %s\nApplication version: %s" % (QT_VERSION_STR, PYQT_VERSION_STR, QApplication.applicationVersion())))


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
        p.title = str(title)
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

    def setNextSlide(self, index):
        if index >= 0 and index < len(self.presentation.slides):
            self.presentation.nextindex = index
            self.nextslide = self.presentation.getSlide(index)
        else:
            self.nextslide = self.presentation.defaultSlide
        self.emit(SIGNAL("updateSlides()"))

    # chat
    def chatSend(self,chat):
        self.emit(SIGNAL("chatRecieved(QString)"),chat)

    # broadcast
    def startBroadcast(self):
        print "NYI: Start broadcast"

    def endBroadcast(self):
        print "NYI: End broadcast"



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
    
    def __init__(self,pointers,beamview):
        QThread.__init__(self)
        self.pointers = pointers
        self.beamview = beamview
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

    def drawClear(self):
        self.points = []
        self.current = -1
        self.beamview.update()

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
        


