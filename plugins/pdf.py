from PyQt4.QtCore import *
from PyQt4.QtGui import *

import poppler
import gtk
import cStringIO
import os.path

# this plugin requires GTK for PDF conversion, it is very bad, 
# but no stable pure python libraries exist at the moment

class widget(QWidget):

    def __init__(self,container,index=0):
        super(widget,self).__init__()
        self.index = index
        self.page = container.getSlide(index)
        size = self.page.get_size()
        self.aspect = size[0]/size[1]
        
      
    def paintEvent(self,arg):
        owidth = width = self.size().width()
        oheight = height = self.size().height()
        
        if float(width)/float(height) > self.aspect:
            width = int(height*self.aspect)
        else:
            height = int(width/self.aspect)
            
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
        self.page.render_to_pixbuf(0, 0, width, height, width/self.page.get_size()[0], 0, pixbuf)

        io = cStringIO.StringIO()
        pixbuf.save_to_callback(io.write, "png")
        image = QImage()
        image.loadFromData(QByteArray(io.getvalue()))
        io.close()
        painter = QPainter(self)    
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

      def __init__(self,container,index=0,width=128,height=128):
        
        self.page = container.getSlide(index)
        size = self.page.get_size()
        self.aspect = size[0]/size[1]
        
        if float(width)/float(height) > self.aspect:
            width = int(height*self.aspect)
        else:
            height = int(width/self.aspect)
            
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
        self.page.render_to_pixbuf(0, 0, width, height, width/self.page.get_size()[0], 0, pixbuf)

        io = cStringIO.StringIO()
        pixbuf.save_to_callback(io.write, "png")
        image = QPixmap()
        image.loadFromData(QByteArray(io.getvalue()))
        io.close()
        
        QIcon.__init__(self,image)
        

class container:

    def __init__(self,pdffile):
        self.uri = "file://" + pdffile
        self.filename = os.path.basename(pdffile)
        self.document = poppler.document_new_from_file(self.uri,None) # 2nd argument is password
        self.numslides = self.document.get_n_pages()
        size = self.document.get_page(0).get_size()
        self.aspect = size[0]/size[1]

    def numSlides(self):
        return self.numslides

    def getSlide(self,index):
        if index < self.numslides and index >= 0:
            return self.document.get_page(index)
        else:
            raise IndexError()
            
    def getName(self,index=0):
        return self.filename + " slide " + str(index+1)


plugintype = 'content'
mimetype   = 'application/pdf'
name       = 'PDF File'
source     = 'file'
filetype   = 'pdf'    

