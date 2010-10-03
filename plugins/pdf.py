from PyQt4.QtCore import *
from PyQt4.QtGui import *

import QtPoppler
import os.path
import hashlib

MAGICDPI = 72

class widget(QWidget):

    def __init__(self,container,index=0):
        super(widget,self).__init__()
        self.page = container.getSlide(index)
        self.pagesize = self.page.pageSize()
        self.aspect = self.pagesize.width()/float(self.pagesize.height())
        self.index = index
        self.cache = container.cache
              
    def paintEvent(self,arg):

        owidth = width = self.size().width()
        oheight = height = self.size().height()
        if float(width)/float(height) > self.aspect:
            width = int(height*self.aspect)
            scale = width / float(self.pagesize.width())
        else:
            height = int(width/self.aspect)
            scale = height / float(self.pagesize.height())
    
        if self.cache.has_key(self.cacheindex(width,height)):
            image = self.cache[self.cacheindex(width,height)]
        else:
            image = self.page.renderToImage(scale*MAGICDPI,scale*MAGICDPI)
            self.cache[self.cacheindex(width,height)] = image

        painter = QPainter(self)
        painter.drawImage(int((owidth-width)/2),int((oheight-height)/2),image) 

    def cacheindex(self,width,height):
        return hashlib.sha1(str(width) + "x" + str(height) + "*" + str(self.index)).hexdigest()

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
        
        f=open(pdffile)
        d=f.read()
        f.close()
        
        self.identifier = hashlib.md5(d).hexdigest()
        
        self.document = QtPoppler.Poppler.Document.load(pdffile)
        self.document.setRenderHint(QtPoppler.Poppler.Document.Antialiasing and QtPoppler.Poppler.Document.TextAntialiasing)
        self.numslides = self.document.numPages()
        size = self.document.page(0).pageSize()
        self.cache = {}
        
        self.namemap = self.parseToc(self.document.toc().firstChild())

    def numSlides(self):
        return self.numslides

    def getSlide(self,index):
        if index < self.numslides and index >= 0:
            return self.document.page(index)
        else:
            raise IndexError()
            
    def getName(self,index=0):
        if self.namemap.has_key(index+1):
            return self.namemap[index+1]
        else:
            return self.filename + " slide " + str(index+1)
        
    def getIdentifier(self):
        return self.identifier
        
    def parseToc(self, toc, hashmap={}):
        if not toc.isNull():
            name = str(toc.nodeName())
            
            dest = toc.attributes().namedItem("DestinationName")
            if not dest.isNull():
                page = self.document.linkDestination(dest.nodeValue()).pageNumber()
                hashmap[page] = name
                
            dest = toc.attributes().namedItem("Destination")
            if not dest.isNull():
                pages = dest.nodeValue().split(";")
                page = int(pages[1])
                hashmap[page] = name
                
            self.parseToc(toc.firstChild(),hashmap)
            self.parseToc(toc.nextSibling(),hashmap)
            return hashmap

        


plugintype = 'content'
mimetype   = 'application/pdf'
name       = 'PDF File'
source     = 'file'
filetype   = 'pdf'    

