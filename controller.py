from PyQt4.QtCore import *
from PyQt4.QtGui import *

import gui
import os
import presentation
import plugins

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

    # application
    def start(self): 
        if self.screens.countScreens() > 1:
            self.screens.moveToScreen(1,self.beamview)
            self.beamview.show()
        self.mainview.show()

    def quitApplication(self):
        print "QUIT"
        self.beamview.close()
        self.mainview.close()

    # presentations
    def newPresentation(self):
        self.mainview.setCentralWidget(gui.NewPresentationWidget(self))

    def closePresentation(self):
        if self.presentation.saveneeded:
            print "Todo: Ask for save"
        self.mainview.showToolbar(False)
        self.mainview.setCentralWidget(gui.LoadPresentationWidget(self))

    def openPresentation(self):
        print "NYI: Open"

    def openRemotePresentation(self):
        print "NYI: Remote Open"

    def savePresentation(self):
        print "NYI: Save"

    def saveAsPresentation(self):
        print "NYI: Save As"

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
        p.title = title
        p.name = name
        p.email = email
        p.forclass = forclass
        p.organization = organization
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
        self.setCurrentSlide(self.presentation.nextindex)
        self.setNextSlide(self.presentation.nextindex+1)
        self.emit(SIGNAL("setNextSlide(int)"),self.presentation.nextindex)

    def previousSlide(self):
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

    def setNextSlide(self, index):
        if index >= 0 and index < len(self.presentation.slides):
            self.presentation.nextindex = index
            self.nextslide = self.presentation.getSlide(index)
        else:
            self.nextslide = self.presentation.defaultSlide
        self.emit(SIGNAL("updateSlides()"))



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
        
        


