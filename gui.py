from PyQt4.QtCore import *
from PyQt4.QtGui import *

import plugins
import time
import util
import webbrowser

##########################################################
# The Main Window 
##########################################################

class MainWindow(QMainWindow):

    def __init__(self, controller):
        QMainWindow.__init__(self)
        self.controller = controller

        self.setWindowIcon(QIcon("icons/presentation.svg"))
        
        # setup the window
        self.createStatus()
        self.createMenus()
        self.createToolbar()

        # start centered and set minimum size  
        screen = QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        self.setMinimumSize(QSize(640,480)) 

    # menubars, status and toolbars
    def createStatus(self):
        self.status = self.statusBar()
        self.status.setSizeGripEnabled(True)
        self.status.showMessage("Ready", 5000)

    def createMenus(self):

        self.menu = self.menuBar()
        menufile = self.menu.addMenu(self.tr("&File"))
        menuedit = self.menu.addMenu(self.tr("&Edit"))        
        menupointers = self.menu.addMenu(self.tr("&Pointers"))
        menuhelp = self.menu.addMenu(self.tr("&Help"))  

        filenew = self.createAction(self.tr("&New"), self.controller.newPresentation, QKeySequence.New, None, self.tr("New presentation")) 
        fileopen = self.createAction(self.tr("&Open..."), self.controller.openPresentation, QKeySequence.Open, None, self.tr("Open presentation"))
        fileopenremote = self.createAction(self.tr("Open &Remote..."), self.controller.openRemotePresentation, "Ctrl+R", None, self.tr("Open presentation from a server")) 
        filesave = self.createAction(self.tr("&Save"), self.controller.savePresentation, QKeySequence.Save, None, self.tr("Save the presentation"))
        filesaveas = self.createAction(self.tr("Save &As..."), self.controller.saveAsPresentation, QKeySequence.SaveAs, None, self.tr("Save the presentation to a new file"))
        fileclose = self.createAction(self.tr("&Close"), self.controller.closePresentation, QKeySequence.Close, None, self.tr("Close the presentation"))
        filequit = self.createAction(self.tr("&Quit"), self.controller.quitApplication, "Ctrl+Q", None, self.tr("Close the program"))

        editpreferences = self.createAction(self.tr("&Preferences..."), lambda: self.controller.prefview.show())  
        
        pointers = []
        for pointermodule in plugins.pointer:
            act = self.createAction(pointermodule.name, None, None, None, pointermodule.description, True)
            if pointermodule.enabledefault:
                act.setChecked(True)
            self.connect(act, SIGNAL("triggered()"), lambda p=pointermodule: self.controller.enablePointer(p) if act.isChecked() else self.controller.disablePointer(p))
            pointers.append(act)

        helpwww = self.createAction(self.tr("&Website..."), lambda: webbrowser.open_new("http://github.com/UniversalPrimer"))
        helpabout = self.createAction(self.tr("&About..."), self.controller.aboutApp)

        self.addActions(menufile,(filenew,fileopen,fileopenremote,None,filesave,filesaveas,None,fileclose,filequit))
        self.addActions(menuedit,(editpreferences,))
        self.addActions(menupointers,pointers)
        self.addActions(menuhelp,(helpwww,None,helpabout))
      
    def createToolbar(self):
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
            action.setText(plugin.name)
            self.connect(action,SIGNAL("triggered()"),lambda x=mimetype: self.controller.addSlide(x))
            addsourcemenu.addAction(action)

        addsource.setMenu(addsourcemenu)

        forwardbtn = QToolButton()
        forwardbtn.setIcon(QIcon("icons/go-next.svg"))
        self.connect(forwardbtn,SIGNAL("clicked()"),self.controller.nextSlide)
        
        backbtn = QToolButton()
        backbtn.setIcon(QIcon("icons/go-previous.svg"))
        self.connect(backbtn,SIGNAL("clicked()"),self.controller.previousSlide)

        bcast = QToolButton()
        bcast.setIcon(QIcon("icons/broadcast.svg"))
        bcast.setCheckable(True)
        self.connect(bcast,SIGNAL("clicked()"),lambda: self.controller.startBroadcast() if bcast.isChecked() else self.controller.endBroadcast())

        mic = QToolButton()
        mic.setIcon(QIcon("icons/microphone.svg"))
        mic.setCheckable(True)

        cam = QToolButton()
        cam.setIcon(QIcon("icons/camera-video.svg"))
        cam.setCheckable(True)

        labeltimer = QLabel()
        labeltimer.setFont(QFont('Sans', 20, QFont.Bold))
        self.timer = QTimer()
        self.connect(self.timer,SIGNAL("timeout()"),lambda x=labeltimer: x.setText(time.strftime("%H:%M ")))
        self.timer.start(1000)

        stretch = QWidget()
        stretch.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding))
    
        self.toolbar.addWidget(addsource)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(bcast)
        self.toolbar.addWidget(mic)
        self.toolbar.addWidget(cam)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(backbtn)
        self.toolbar.addWidget(forwardbtn)
        
        self.toolbar.addWidget(stretch)
        self.toolbar.addWidget(labeltimer)
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

    def setTitle(self, name):
        self.setWindowTitle(QApplication.applicationName() + " - " + name)

    def showToolbar(self, state=True):
        self.toolbar.setVisible(state)

    def closeEvent(self, event):
        if self.controller.mainClosed():
            event.accept()
        else:
            event.ignore()

##########################################################
# Window: Beam View, the presentation for a projector
##########################################################

class BeamWindow(QWidget):

    def __init__(self, controller):
        QWidget.__init__(self)
        self.controller = controller
        self.overlay = Overlay()
        self.slide = SlideWidget(self.overlay) 
        layout = QGridLayout()
        layout.setMargin(0)
        self.slide.layout.setMargin(0)
        self.setMinimumSize(QSize(400,300))
        layout.addWidget(self.slide,0,0)
        self.setLayout(layout)
        #self.showFullScreen()     
        self.connect(self.controller,SIGNAL("updateSlides()"),self.updateSlideView) 
        self.testcard = True
        self.setWindowTitle(self.tr("Projector Display"))

    def setPointer(self,x,y):
        size = self.overlay.size()
        x = int(size.width() * (1-x))
        y = int(size.height() * (1-y))
        self.overlay.x = x
        self.overlay.y = y
        self.overlay.update()

    def clearPointer(self):
        if not (self.overlay.x == 0 and self.overlay.y == 0):  
            self.overlay.x = 0
            self.overlay.y = 0
            self.overlay.update()

    def setPaths(self,paths):
        size = self.overlay.size()
        newpaths = []        
        for path in paths:
            if len(path):
                newpath = []
                path = util.vertexreduce(path,1/100.)
                for point in path:
                    x = int(size.width() * (1-point[0]))
                    y = int(size.height() * (1-point[1]))
                    newpath.append(QPoint(x,y))
                newpaths.append(newpath)
        self.overlay.paths = newpaths

    def updateSlideView(self):
        self.slide.setSlide(self.controller.currentslide)
        self.testcard = False

    def paintEvent(self,arg):
        painter = QPainter(self)

        if self.testcard :
            w = self.size().width()/8
            h = self.size().height()/2
            painter.fillRect(0*w, 0, w, h, QColor("white"))
            painter.fillRect(1*w, 0, w, h, QColor("yellow"))
            painter.fillRect(2*w, 0, w, h, QColor("cyan"))
            painter.fillRect(3*w, 0, w, h, QColor("lime"))
            painter.fillRect(4*w, 0, w, h, QColor("magenta"))
            painter.fillRect(5*w, 0, w, h, QColor("red"))
            painter.fillRect(6*w, 0, w, h, QColor("blue"))
            painter.fillRect(7*w, 0, w, h, QColor("black"))
            painter.fillRect(7*w, h, w, 2*h, QColor("white"))
            painter.fillRect(6*w, h, w, 2*h, QColor("yellow"))
            painter.fillRect(5*w, h, w, 2*h, QColor("cyan"))
            painter.fillRect(4*w, h, w, 2*h, QColor("lime"))
            painter.fillRect(3*w, h, w, 2*h, QColor("magenta"))
            painter.fillRect(2*w, h, w, 2*h, QColor("red"))
            painter.fillRect(1*w, h, w, 2*h, QColor("blue"))
            painter.fillRect(0*w, h, w, 2*h, QColor("black"))
            firstpen = QPen(QColor("grey"), 40, Qt.DotLine, Qt.SquareCap, Qt.BevelJoin)
            painter.setPen(firstpen)
            painter.drawRect(0,0,w*8,h*2)
        else:
            painter.fillRect(0, 0, self.size().width(), self.size().height(), QColor("black"))

##########################################################
# Window: Preferences
##########################################################

class PreferencesWindow(QDialog):
    
    def __init__(self, controller):
        QDialog.__init__(self)
        self.setModal(True)


        settings = QSettings()
        self.serverfield = QLineEdit()
        self.serverfield.setText(settings.value("server").toString())

        self.pointercolor = ColorButton()
        self.pointercolor.setColor(QColor(settings.value("pointercolor")))

        self.linecolor = ColorButton()
        self.linecolor.setColor(QColor(settings.value("linecolor")))

        self.pointersize = QSpinBox()
        self.pointersize.setValue(settings.value("pointersize").toInt()[0])

        self.linewidth = QSpinBox()
        self.linewidth.setValue(settings.value("linewidth").toInt()[0])
        
        cancelbtn = QPushButton(self.tr("C&ancel"),self)
        savebtn = QPushButton(self.tr("C&reate"),self)
        savebtn.setDefault(True)

        formLayout = QFormLayout()
        formLayout.addRow(self.tr("&Server:"), self.serverfield)
        formLayout.addRow(self.tr("Pointer &color:"), self.pointercolor)
        formLayout.addRow(self.tr("Pointer s&ize:"), self.pointersize)
        formLayout.addRow(self.tr("Line c&olor:"), self.linecolor)
        formLayout.addRow(self.tr("Line &width:"), self.linewidth)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(cancelbtn)
        buttonLayout.addWidget(savebtn)

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("<b>" + self.tr("Preferences") +  "</b>"))
        vbox.addLayout(formLayout)
        vbox.addStretch(1)
        vbox.addLayout(buttonLayout)

        self.setLayout(vbox)
        self.connect(savebtn, SIGNAL("clicked()"), self.save)
        self.connect(cancelbtn, SIGNAL("clicked()"), self.close)

        self.resize(400,300)
        screen = QDesktopWidget().screenGeometry()
        size =  self.geometry()        
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        

    def save(self):
        settings = QSettings()
        settings.setValue("server",self.serverfield.text())
        settings.setValue("pointercolor",self.pointercolor.color)
        settings.setValue("linecolor",self.linecolor.color)
        settings.setValue("pointersize",self.pointersize.value())
        settings.setValue("linewidth",self.linewidth.value())
        self.close()


##############################################################
# Widget: Overlay widget, showing cursor and drawing
##############################################################

class Overlay(QWidget):
 
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)
        self.x = 0
        self.y = 0


        settings = QSettings()
        # Set options another place
        
        self.pointercolor = QColor(settings.value("pointercolor"))
        self.pointersize = settings.value("pointersize").toInt()[0]
        self.linecolor = QColor(settings.value("linecolor"))
        self.linewidth = settings.value("linesize").toInt()[0]

        self.paths = None
 
    def paintEvent(self, event):

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(self.linecolor, self.linewidth))
        painter.setBrush(QBrush(self.pointercolor))

        if self.x and self.y:
            painter.drawEllipse(QRectF(self.x-self.pointersize , self.y-self.pointersize , 2*self.pointersize , 2*self.pointersize ))

        if self.paths:
            for path in self.paths:
                pg = QPolygon(path)
                painter.drawPolyline(pg)
            
        painter.end()
 
        
    

##########################################################
# Widget: Loading a presentation (for application startup
#         and if the current presentation was closed)
##########################################################

class LoadPresentationWidget(QWidget):

    def __init__(self, controller):
        QWidget.__init__(self)
        self.controller = controller

        loadlocalbtn = QPushButton()
        loadlocalbtn.setStatusTip("Open file")
        loadlocalbtn.setIcon(QIcon("icons/document-open.svg"))
        loadlocalbtn.setIconSize(QSize(64,64))
        loadlocalbtn.setFlat(True)

        loadserverbtn = QPushButton()
        loadserverbtn.setStatusTip("Open from server")
        loadserverbtn.setIcon(QIcon("icons/document-remote-open.svg"))
        loadserverbtn.setIconSize(QSize(64,64))
        loadserverbtn.setFlat(True)

        loadnewbtn = QPushButton()        
        loadnewbtn.setStatusTip("New file")
        loadnewbtn.setIcon(QIcon("icons/document-new.svg"))
        loadnewbtn.setIconSize(QSize(64,64))
        loadnewbtn.setFlat(True)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(loadlocalbtn)
        hbox.addWidget(loadserverbtn)
        hbox.addWidget(loadnewbtn)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addStretch(1)
        self.setLayout(vbox)

        self.connect(loadlocalbtn, SIGNAL("clicked()"), self.controller.openPresentation)
        self.connect(loadserverbtn, SIGNAL("clicked()"), self.controller.openRemotePresentation)
        self.connect(loadnewbtn, SIGNAL("clicked()"), self.controller.newPresentation)


##########################################################
# Widget: Metadata for a new presentation
##########################################################

class NewPresentationWidget(QWidget):

    def __init__(self, controller):
        QWidget.__init__(self)
        self.controller = controller
       
        self.titlefield = QLineEdit()
        self.namefield = QLineEdit()
        self.emailfield = QLineEdit()
        self.classfield = QComboBox()
        self.classfield.setEditable(True)
        self.orgfield = QComboBox()
        self.orgfield.setEditable(True)

        cancelbtn = QPushButton(self.tr("C&ancel"),self)
        createbtn = QPushButton(self.tr("C&reate"),self)
        createbtn.setDefault(True)

        formLayout = QFormLayout()
        formLayout.addRow(self.tr("&Title:"), self.titlefield)
        formLayout.addRow(self.tr("Your &Name:"), self.namefield)
        formLayout.addRow(self.tr("Your &Email:"), self.emailfield)
        formLayout.addRow(self.tr("&Class:"), self.classfield)
        formLayout.addRow(self.tr("&Organisation:"), self.orgfield)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(cancelbtn)
        buttonLayout.addWidget(createbtn)

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("<b>" + self.tr("New Presentation") +  "</b>"))
        vbox.addLayout(formLayout)
        vbox.addStretch(1)
        vbox.addLayout(buttonLayout)

        self.setLayout(vbox)
        self.connect(createbtn, SIGNAL("clicked()"), self.create)
        self.connect(cancelbtn, SIGNAL("clicked()"), self.controller.closePresentation)

    def create(self):
        self.controller.createPresentation(self.titlefield.text(),self.namefield.text(),self.emailfield.text(),self.classfield.currentText(),self.orgfield.currentText())

##########################################################
# Widget: The presenter display
##########################################################

class PresentationWidget(QWidget):

    def __init__(self, controller):
        QWidget.__init__(self)
        self.controller = controller
               
        # Main Layout
        splitter = QSplitter(Qt.Vertical)
        lowerlayout = QHBoxLayout()
        upperlayout = QHBoxLayout()
        upperpart = QWidget()
        upperpart.setLayout(upperlayout)
        lowerpart = QWidget()
        lowerpart.setLayout(lowerlayout)
        splitter.addWidget(upperpart)
        splitter.addWidget(lowerpart)
        splitter.setSizes([1,1])

        # Chat Box
        chatwidget = QWidget()
        chatlayout = QVBoxLayout()
        chatfield = QLineEdit()
        chatview = QTextEdit()
        chatlayout.addWidget(chatview)
        chatlayout.addWidget(chatfield)
        chatwidget.setLayout(chatlayout)

        # Slide Overview
        slideoverview = QWidget()
        slideoverviewlist = DragDropListWidget(self.controller)
        slideoverviewlist.setIconSize(QSize(64,64))
        slideoverviewlist.setSelectionMode(QAbstractItemView.SingleSelection)
        slideoverviewlayout = QGridLayout()
        slideoverviewlayout.addWidget(slideoverviewlist,0,0)
        slideoverview.setLayout(slideoverviewlayout)

        # Left and Right Slide
        self.leftslide = SlideWidget()
        self.rightslide = SlideWidget()
                
        upperlayout.addWidget(self.leftslide)
        upperlayout.addWidget(self.rightslide)
        lowerlayout.addWidget(chatwidget)
        lowerlayout.addWidget(slideoverview)
        
        layout = QGridLayout()
        layout.addWidget(splitter,0,0)
        layout.setMargin(0)
        self.setLayout(layout)

        self.connect(self.controller.presentation,SIGNAL("changed()"),slideoverviewlist.update)
        self.connect(self.controller,SIGNAL("updateSlides()"),self.updateSlideView)
        self.connect(chatfield,SIGNAL("returnPressed()"),lambda: self.chatSend(chatfield))
        self.connect(self.controller,SIGNAL("chatRecieved(QString)"),chatview.append)
        
    def updateSlideView(self):
        self.leftslide.setSlide(self.controller.currentslide)
        self.rightslide.setSlide(self.controller.nextslide)

    def chatSend(self,field):
        self.controller.chatSend(field.text())
        field.setText("")



##########################################################
# Widget: A QListWidget that you can drag and 
#         drop items in
##########################################################

class DragDropListWidget(QListWidget):
    def __init__(self, controller):
        QListWidget.__init__(self)
        self.controller = controller
        self.presentation = controller.presentation
        self.setDragDropMode(self.InternalMove)
        self.installEventFilter(self)
        self.connect(self,SIGNAL("itemSelectionChanged()"),self.updateSelection)
        self.connect(self.controller,SIGNAL("setNextSlide(int)"),self.setrow)

    def eventFilter(self, sender, event):
        if (event.type() == QEvent.ChildRemoved):
            self.reorderModel()
        return False 

    def contextMenuEvent(self, s):
        item = self.itemAt(s.pos())
        if item:
            i = item.data(Qt.UserRole).toPyObject()
            menu = QMenu(i.getTitle(),self)
            action = QAction(self)
            action.setText("Remove slide")
            action.setIcon(QIcon("icons/list-remove.svg"))
            self.connect(action,SIGNAL("triggered()"),lambda: self.presentation.removeSlide(self.row(item))) 
            menu.addAction(action)
            menu.exec_(s.globalPos())

    def update(self):
        index = self.currentRow()
        self.clear()
        for item in self.presentation.slides:
            i = QListWidgetItem(item.asIcon(),item.getTitle())
            i.setData(Qt.UserRole,item)
            self.addItem(i)
        if self.count() > 0 and index == -1:
            index = 0
        self.setCurrentRow(index)

    def updateSelection(self):
        self.controller.setNextSlide(self.currentRow())

    def reorderModel(self):
        slides = []
        for i in range(0,self.count()):
            slide = self.item(i).data(Qt.UserRole).toPyObject()
            slides.append(slide)
        self.presentation.slides = slides
        self.presentation.setSaveNeeded()

    def setrow(self,i):
        self.setCurrentRow(i)

##########################################################
# Widget: Slide View Widget
##########################################################
       
class SlideWidget(QWidget):

    def __init__(self,overlay=None):
        QWidget.__init__(self)
        self.overlay = overlay
        self.slide = QWidget()
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.slide)
        self.setLayout(self.layout)        
        if self.overlay:
            wl = QHBoxLayout()
            wl.addWidget(self.overlay)
            self.slide.setLayout(wl)
    
    def setSlide(self, slide):
        self.slide.hide()
        self.layout.removeWidget(self.slide)
        self.slide = slide.asWidget()
        self.layout.addWidget(self.slide)
        if self.overlay:
            wl = QHBoxLayout()
            wl.addWidget(self.overlay)
            self.slide.setLayout(wl)

##########################################################
# Widget: Color Chooser Button
##########################################################

class ColorButton(QPushButton):
    
    def __init__(self):
        QPushButton.__init__(self)
        self.setColor(QColor("black"))
        self.connect(self,SIGNAL("clicked()"),self.choose)

    def setColor(self, color):
        self.color = color
        self.update()

    def paintEvent(self, event):
        super(ColorButton,self).paintEvent(event)
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(self.color))
        painter.drawRect(7,7,self.size().width()-14,self.size().height()-14)
        painter.end()

    def choose(self):
        color = QColorDialog.getColor(self.color, self, self.tr("Pick a color"))
        print color
        self.setColor(color)


