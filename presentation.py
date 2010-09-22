import os.path
import mimetypes

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import plugins

class Presentation(QObject):

    def __init__(self, filename=None):
        QObject.__init__(self)

        self.slides = []
        self.defaultSlide = Slide(Source(None,"application/x-blank-slide"),0)
        self.saveneeded = True
        self.currentindex = -1
        self.nextindex = -1

        # metadata
        self.title = self.tr("Untitled Presentation")
        self.name = ""
        self.email = ""
        self.forclass = ""
        self.organization = ""

        if filename:
            self.filename = filename
            self.open(filename)
            self.saveneeded = False

    def open(self,filename):
        print "NYI: Presentation->open"

    def save(self,filename=None):
        print "NYI: Presentation->save"
        self.saveneeded = False
        
    def addSource(self, source):
        for i in range(0,source.numSlides()):
            self.addSlide(source.getSlide(i))
        
    def addSlide(self, slide):
        self.slides.append(slide)
        self.emit(SIGNAL("changed()"))
        self.setSaveNeeded()

    def getSlide(self, index):
        return self.slides[index]

    def removeSlide(self, index):
        if len(self.slides) > index:
            self.slides.pop(index)
            self.emit(SIGNAL("changed()"))
            self.setSaveNeeded()

    def setSaveNeeded(self):
        self.saveneeded = True


class Source:

    def __init__(self, reference, mimetype=None):
        if mimetype == None:
            if os.path.exists(reference):
                mimetype = mimetypes.guess_type(reference)[0]
            else:
                raise RuntimeError("No mimetype was found for reference: %s" % reference)

        self.mimetype = mimetypes
        self.reference = reference
        self.handler = plugins.mimehandlers[mimetype]
        self.container = self.handler.container(self.reference)

    def numSlides(self):
        return self.container.numSlides()

    def getSlide(self,index=0):
        return Slide(self,index)
        
        
class Slide:

    def __init__(self, source, index):
        self.source = source
        self.handler = self.source.handler
        self.index = index
        self.title = self.source.container.getName(self.index)
        self.icon = self.handler.icon(self.source.container,self.index)
     
    def asWidget(self):
        return self.handler.widget(self.source.container,self.index)

    def asIcon(self):
        return self.icon

    def getTitle(self):
        return self.title



