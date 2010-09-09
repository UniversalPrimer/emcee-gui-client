from PyQt4.QtCore import *
from PyQt4.QtGui import *

import presentation

# Main Widgets

class LoadPresentationWidget(QWidget):

    def __init__(self,parent):
        QWidget.__init__(self,parent)
        self.parent = parent

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

        self.connect(loadlocalbtn, SIGNAL("clicked()"), self.parent.open)
        self.connect(loadserverbtn, SIGNAL("clicked()"), self.parent.openremote)
        self.connect(loadnewbtn, SIGNAL("clicked()"), self.parent.new)


class NewPresentationWidget(QWidget):

    def __init__(self,parent):
        QWidget.__init__(self,parent)
        self.parent = parent
       
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
        self.connect(cancelbtn, SIGNAL("clicked()"), self.parent.pclose)

    def create(self):
        p = presentation.Presentation()
        p.title = self.titlefield.text()
        p.name = self.namefield.text()
        p.email = self.emailfield.text()
        p.forclass = self.classfield.currentText()
        p.organization = self.orgfield.currentText()
        self.parent.openpresentation(p)

class PresentationWidget(QWidget):

    def __init__(self,parent):
        QWidget.__init__(self,parent)
        self.parent = parent
        
        self.currentSlide = SlideWidget(self, self.parent.presentation.defaultSlide)
        self.nextSlide = SlideWidget(self, self.parent.presentation.defaultSlide)
        self.chatBox = ChatWidget(self)
        self.slideOverview =  SlideOverviewWidget(self)
        
        splitter = QSplitter(Qt.Vertical)
        lowerlayout = QHBoxLayout()
        upperlayout = QHBoxLayout()
        
        upper = QWidget()
        upper.setLayout(upperlayout)
        
        lower = QWidget()
        lower.setLayout(lowerlayout)
        
        splitter.addWidget(upper)
        splitter.addWidget(lower)
        splitter.setSizes([1,1])
                
        upperlayout.addWidget(self.currentSlide)
        upperlayout.addWidget(self.nextSlide)
        lowerlayout.addWidget(self.chatBox)
        lowerlayout.addWidget(self.slideOverview)
        
        layout = QGridLayout()
        layout.addWidget(splitter,0,0)
        self.setLayout(layout)

    def setCurrentSlide(self,slide):
        self.currentSlide.setSlide(slide)        

    def setNextSlide(self,slide):
        self.nextSlide.setSlide(slide)


# Sub Widgets for PresentationWidget
class ChatWidget(QWidget):
    
     def __init__(self,parent):
        QWidget.__init__(self,parent)
        self.parent = parent
        
        layout = QVBoxLayout()
        chatfield = QLineEdit()
        chatview = QTextEdit()
        layout.addWidget(chatview)
        layout.addWidget(chatfield)
        
        self.setLayout(layout)

        
class SlideWidget(QWidget):

    def __init__(self,parent,slide):
        QWidget.__init__(self,parent)
        self.parent = parent
        self.slide = slide.asWidget()
        
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.slide)
        self.setLayout(self.layout)
    
    def setSlide(self,slide):
        self.slide.hide()
        self.layout.removeWidget(self.slide)
        self.slide = slide.asWidget()
        self.layout.addWidget(self.slide)

        
    
class SlideOverviewWidget(QWidget):

    def __init__(self,parent):
        QWidget.__init__(self,parent)
        self.parent = parent

        self.list = DragDropListWidget()
        self.list.setIconSize(QSize(64,64))
        self.list.setSelectionMode(QAbstractItemView.SingleSelection)
        layout = QGridLayout()
        layout.addWidget(self.list,0,0)
        self.setLayout(layout)

        self.connect(self.parent.parent.presentation,SIGNAL("changed()"),self.update)
        self.connect(self.parent.parent.presentation,SIGNAL("updateslides()"),self.updateslides)
        self.connect(self.list,SIGNAL("itemSelectionChanged()"),self.changed)
        self.connect(self.list,SIGNAL("listChanged()"),self.reordered)
        self.connect(self.list,SIGNAL("removeItem(int)"),self.parent.parent.presentation.removeSlide)


    def update(self):
        index = self.list.currentRow()
        self.list.clear()
        for item in self.parent.parent.presentation.slides:
            i = QListWidgetItem(item.asIcon(),item.getTitle())
            i.setData(Qt.UserRole,item)
            self.list.addItem(i)
        if self.list.count() > 0 and index == -1:
            index = 0
        self.list.setCurrentRow(index)

    def reordered(self):
        slides = []
        for i in range(0,self.list.count()):
            slide = self.list.item(i).data(Qt.UserRole).toPyObject()
            slides.append(slide)
        self.parent.parent.presentation.slides = slides
        self.parent.parent.presentation.nextindex = self.list.currentRow()
        self.parent.parent.presentation.setSaveNeeded()

    def changed(self):
        n = len(self.parent.parent.presentation.slides)
        if  n > 0:
                self.parent.parent.presentation.nextindex = self.list.currentRow()
                item = self.list.currentItem()
                if item:
                    slide = item.data(Qt.UserRole).toPyObject()
                    self.parent.setNextSlide(slide)            
        else:
            self.parent.setNextSlide(self.parent.parent.presentation.defaultSlide)

    def updateslides(self):
        if self.parent.parent.presentation.slides:
            if self.parent.parent.presentation.currentindex > -1:
                self.parent.setCurrentSlide(self.parent.parent.presentation.slides[self.parent.parent.presentation.currentindex])
            else:
                self.parent.setCurrentSlide(self.parent.parent.presentation.defaultSlide)
            if self.parent.parent.presentation.nextindex > -1:
                self.parent.setNextSlide(self.parent.parent.presentation.slides[self.parent.parent.presentation.nextindex])
            else:
                self.parent.setNextSlide(self.parent.parent.presentation.defaultSlide)
            self.list.setCurrentRow(self.parent.parent.presentation.nextindex)

# Subclasses for quirks

class DragDropListWidget(QListWidget):
    def __init__(self):
        QListWidget.__init__(self)
        self.setDragDropMode(self.InternalMove)
        self.installEventFilter(self)

    def eventFilter(self, sender, event):
        if (event.type() == QEvent.ChildRemoved):
            self.emit(SIGNAL("listChanged()"))
        return False 

    def contextMenuEvent(self,s):
        item = self.itemAt(s.pos())
        if item:
            i = item.data(Qt.UserRole).toPyObject()
            menu = QMenu(i.getTitle(),self)
            action = QAction(self)
            action.setText("Remove slide")
            action.setIcon(QIcon("icons/list-remove.svg"))
            self.connect(action,SIGNAL("triggered()"),lambda x=item: self.itemRemoved(x)) 
            menu.addAction(action)
            menu.exec_(s.globalPos())
            
    def itemRemoved(self,item):
        self.emit(SIGNAL("removeItem(int)"),self.row(item))

