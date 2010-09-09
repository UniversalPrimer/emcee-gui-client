from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys
import os

import widgets
import presentation
import plugins

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self,parent)
        self.setWindowIcon(QIcon("icons/presentation.svg"))
        
        # setup the window
        self.__createStatus()
        self.__createMenus()
        self.__createToolbar()
        
        self.setCentralWidget(widgets.LoadPresentationWidget(self))

        # start centered and set minimum size
        self.center()
        self.setMinimumSize(QSize(640,480))
        self.presentation = None
        

    # application logic

    def new(self):
        self.setCentralWidget(widgets.NewPresentationWidget(self))

    def pclose(self):
        if self.presentation:
            print "Todo: Ask for save"
        self.toolbar.setVisible(False)
        self.setCentralWidget(widgets.LoadPresentationWidget(self))

    def open(self):
        print "NYI: File->Open"

    def openremote(self):
        print "NYI: File->Open Remote"


    def openpresentation(self,p):
        self.presentation = p
        self.setTitle(p.title)
        self.setCentralWidget(widgets.PresentationWidget(self))
        self.toolbar.setVisible(True)

    def save(self):
        print "NYI: File->Save"

    def saveas(self):
        print "NYI: File->Save As"
                
    def addcontent(self,plugin):
        p = plugins.mimehandlers[plugin]
        if p.plugin_info["source"] == "file":
            filename = QFileDialog.getOpenFileName(self, self.tr("Select file"), os.getcwd(), "%s (*.%s)" % (p.plugin_info["name"], p.plugin_info["filetype"]))
            if filename:
                source = presentation.Source(str(filename),plugin)
                self.presentation.addSource(source)
        elif p.plugin_info["source"] == "internal":
             source = presentation.Source(None,plugin)
             self.presentation.addSource(source)

    def nextslide(self):
        self.presentation.nextSlide()

    def prevslide(self):
        self.presentation.previousSlide()

    # menubars, status and toolbars

    def __createStatus(self):
        self.status = self.statusBar()
        self.status.setSizeGripEnabled(True)
        self.status.showMessage("Ready", 5000)

    def __createMenus(self):
        # menubar
        self.menu = self.menuBar()
        menufile = self.menu.addMenu(self.tr("&File"))
        menuedit = self.menu.addMenu(self.tr("&Edit"))
        menuview = self.menu.addMenu(self.tr("&View"))
        menutools = self.menu.addMenu(self.tr("&Tools"))

        filenew = self.createAction(self.tr("&New"), self.new, QKeySequence.New, None, self.tr("New presentation")) 
        fileopen = self.createAction(self.tr("&Open..."), self.open, QKeySequence.Open, None, self.tr("Open presentation"))
        fileopenremote = self.createAction(self.tr("Open &Remote..."), self.openremote, "Ctrl+R", None, self.tr("Open presentation from a server")) 
        filesave = self.createAction(self.tr("&Save"), self.save, QKeySequence.Save, None, self.tr("Save the presentation"))
        filesaveas = self.createAction(self.tr("Save &As..."), self.saveas, QKeySequence.SaveAs, None, self.tr("Save the presentation to a new file"))
        fileclose = self.createAction(self.tr("&Close"), self.pclose, QKeySequence.Close, None, self.tr("Close the presentation"))
        filequit = self.createAction(self.tr("&Quit"), self.close, "Ctrl+Q", None, self.tr("Close the program"))

        self.addActions(menufile,(filenew,fileopen,fileopenremote,None,filesave,filesaveas,None,fileclose,filequit))
      
    def __createToolbar(self):
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(32,32))
        self.toolbar.setVisible(False)
        self.toolbar.setMovable(False)

        addsource = QToolButton()
        addsource.setIcon(QIcon("icons/list-add.svg"))
        addsource.setPopupMode(QToolButton.InstantPopup)
        
        addsourcemenu = QMenu(self)
        
        for mimetype in plugins.mimehandlers.iterkeys():
            plugin = plugins.mimehandlers[mimetype]
            action = QAction(self)
            action.setText(plugin.plugin_info["name"])
            self.connect(action,SIGNAL("triggered()"),lambda who=mimetype: self.addcontent(who))
            addsourcemenu.addAction(action)

        addsource.setMenu(addsourcemenu)

        forwardbtn = QToolButton()
        forwardbtn.setIcon(QIcon("icons/go-next.svg"))
        self.connect(forwardbtn,SIGNAL("clicked()"),self.nextslide)
        
        backbtn = QToolButton()
        backbtn.setIcon(QIcon("icons/go-previous.svg"))
        self.connect(backbtn,SIGNAL("clicked()"),self.prevslide)

        bcast = QToolButton()
        bcast.setIcon(QIcon("icons/broadcast.svg"))

        mic = QToolButton()
        mic.setIcon(QIcon("icons/microphone.svg"))

        cam = QToolButton()
        cam.setIcon(QIcon("icons/camera-video.svg"))
        
        self.toolbar.addWidget(addsource)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(bcast)
        self.toolbar.addWidget(mic)
        self.toolbar.addWidget(cam)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(backbtn)
        self.toolbar.addWidget(forwardbtn)

        self.addToolBar(self.toolbar)
        
    # helpers
    def createAction(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
        action = QAction(self)
        action.setText(text) #pyside bug
        if icon is not None:
            action.setIcon(QIcon(icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action


    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
    def setTitle(self,name):
        self.setWindowTitle(self.tr("emcee") + " - " + name)




            




