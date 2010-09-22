from PyQt4.QtCore import *
from PyQt4.QtGui import *

class widget(QWidget):

    def __init__(self,container=None,index=0):
        super(widget,self).__init__()
        self.index = index
        self.aspect = 4/float(3)     
      
    def paintEvent(self,arg):
        owidth = width = self.size().width()
        oheight = height = self.size().height()
        
        if float(width)/float(height) > self.aspect:
            width = int(height*self.aspect)
        else:
            height = int(width/self.aspect)

        painter = QPainter(self)
        painter.fillRect(int((owidth-width)/2), int((oheight-height)/2), width, height, QColor("black"))
        
        
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
        image = QPixmap(width,height)
        image.fill(QColor("black"))
        QIcon.__init__(self,image)
        

class container:

    def __init__(self,reference=None):
        pass

    def numSlides(self):
        return 1
            
    def getName(self,index=0):
        return "Blank"


plugintype = 'content' 
mimetype   = 'application/x-blank-slide'
name       = 'Blank Slide'
source     = 'internal' 
