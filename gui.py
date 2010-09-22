from PyQt4.QtCore import *
from PyQt4.QtGui import *

import plugins

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
        self.center()
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
        menuview = self.menu.addMenu(self.tr("&View"))
        menutools = self.menu.addMenu(self.tr("&Tools"))

        filenew = self.createAction(self.tr("&New"), self.controller.newPresentation, QKeySequence.New, None, self.tr("New presentation")) 
        fileopen = self.createAction(self.tr("&Open..."), self.controller.openPresentation, QKeySequence.Open, None, self.tr("Open presentation"))
        fileopenremote = self.createAction(self.tr("Open &Remote..."), self.controller.openRemotePresentation, "Ctrl+R", None, self.tr("Open presentation from a server")) 
        filesave = self.createAction(self.tr("&Save"), self.controller.savePresentation, QKeySequence.Save, None, self.tr("Save the presentation"))
        filesaveas = self.createAction(self.tr("Save &As..."), self.controller.saveAsPresentation, QKeySequence.SaveAs, None, self.tr("Save the presentation to a new file"))
        fileclose = self.createAction(self.tr("&Close"), self.controller.closePresentation, QKeySequence.Close, None, self.tr("Close the presentation"))
        filequit = self.createAction(self.tr("&Quit"), self.controller.quitApplication, "Ctrl+Q", None, self.tr("Close the program"))

        self.addActions(menufile,(filenew,fileopen,fileopenremote,None,filesave,filesaveas,None,fileclose,filequit))
      
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
            self.connect(action,SIGNAL("triggered()"),lambda who=mimetype: self.controller.addSlide(who))
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
        
    def setTitle(self, name):
        self.setWindowTitle(self.tr("emcee") + " - " + name)

    def showToolbar(self, state=True):
        self.toolbar.setVisible(state)


##########################################################
# Window: Beam View, the presentation for a projector
##########################################################

class BeamWindow(QWidget):

    def __init__(self, controller):
        QWidget.__init__(self)
        self.controller = controller
        self.slide = SlideWidget()        
        layout = QGridLayout()
        layout.setMargin(0)
        self.slide.layout.setMargin(0)
        self.setMinimumSize(QSize(400,300))
        layout.addWidget(self.slide,0,0)
        self.setLayout(layout)
        self.showFullScreen()     
        self.connect(self.controller,SIGNAL("updateSlides()"),self.updateSlideView) 
        self.testcard = True


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
        self.setLayout(layout)

        self.connect(self.controller.presentation,SIGNAL("changed()"),slideoverviewlist.update)
        self.connect(self.controller,SIGNAL("updateSlides()"),self.updateSlideView)

    def updateSlideView(self):
        self.leftslide.setSlide(self.controller.currentslide)
        self.rightslide.setSlide(self.controller.nextslide)



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
            self.connect(action,SIGNAL("triggered()"),lambda x=item: self.presentation.removeSlide(self.row(x))) 
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

    def __init__(self):
        QWidget.__init__(self)
        self.slide = QWidget()
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.slide)
        self.setLayout(self.layout)
    
    def setSlide(self, slide):
        self.slide.hide()
        self.layout.removeWidget(self.slide)
        self.slide = slide.asWidget()
        self.layout.addWidget(self.slide)


