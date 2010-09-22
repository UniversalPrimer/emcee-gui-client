from PyQt4.QtCore import *
from PyQt4.QtGui import *

import QtPoppler
import os.path

MAGICDPI = 72

class widget(QWidget):

    def __init__(self,container,index=0):
        super(widget,self).__init__()
        self.page = container.getSlide(index)
        self.pagesize = self.page.pageSize()

        self.aspect = self.pagesize.width()/float(self.pagesize.height())
              
    def paintEvent(self,arg):
        owidth = width = self.size().width()
        oheight = height = self.size().height()

        if float(width)/float(height) > self.aspect:
            width = int(height*self.aspect)
            scale = width / float(self.pagesize.width())
        else:
            height = int(width/self.aspect)
            scale = height / float(self.pagesize.height())
    
        painter = QPainter(self)
        image = self.page.renderToImage(scale*MAGICDPI,scale*MAGICDPI)
        painter.drawImage(int((owidth-width)/2),int((oheight-height)/2),image) 
        
    def sizeHint(self):
        width = self.size().width()
        height = self.size().height()
        
        a = 0
        if height > 0:
            float(width)/float(height)
            
        if  a > self.aspect:
            width = int(height*self.aspect)
        else:
            height = int(width/self.aspect)
            
        return QSize(width,height)
        
class icon(QIcon):

      def __init__(self,container,index=0,width=128,height=96):
        page = container.getSlide(index)
        image = QPixmap.fromImage(page.renderToImage()) 
        QIcon.__init__(self,image)
        

class container:

    def __init__(self,pdffile):

        self.filename = os.path.basename(pdffile)
        self.document = QtPoppler.Poppler.Document.load(pdffile)
        self.document.setRenderHint(QtPoppler.Poppler.Document.Antialiasing and QtPoppler.Poppler.Document.TextAntialiasing)
        self.numslides = self.document.numPages()
        size = self.document.page(0).pageSize()

    def numSlides(self):
        return self.numslides

    def getSlide(self,index):
        if index < self.numslides and index >= 0:
            return self.document.page(index)
        else:
            raise IndexError()
            
    def getName(self,index=0):
        return self.filename + " slide " + str(index+1)


plugintype = 'content'
mimetype   = 'application/pdf'
name       = 'PDF File'
source     = 'file'
filetype   = 'pdf'    

