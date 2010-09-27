import os.path
import mimetypes
import unicodedata
import re
import json
import hashlib

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

        if filename:
            self.filename = filename
            self.saveneeded = False

            openfile = open(self.filename,"r")
            openfilejson = json.load(openfile)
            openfile.close()

            self.title = openfilejson["metadata"]["title"]
            self.name = openfilejson["metadata"]["author"]
            self.email = openfilejson["metadata"]["email"]
            self.forclass = openfilejson["metadata"]["class"]
            self.organization = openfilejson["metadata"]["organization"]

            tmpsrc = {}
            for (ident,source) in openfilejson["sources"].items():
                tmpsrc[ident] = Source(source["reference"], source["mimetype"]) 

            for slide in openfilejson["slides"]:
                self.slides.append(Slide(tmpsrc[slide["source"]],slide["index"]))

        else:
            self.filename = None
            # metadata
            self.title = self.tr("Untitled Presentation")
            self.name = ""
            self.email = ""
            self.forclass = ""
            self.organization = ""

    def save(self,filename=None):
        if filename:
            self.filename = filename

        if self.filename:
            savefile = open(self.filename,"w")
            savefile.write(self.asJSON())
            savefile.close()           
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

    def suggestedFileName(self):
        if len(self.title)  > 0:
            self.title = unicodedata.normalize('NFKD', unicode(self.title)).encode('ascii', 'ignore')
            self.title = unicode(re.sub('[^\w\s-]', '', self.title).strip().lower())
            self.title = re.sub('[-\s]+', '-', self.title)
            return str(self.title)
        else:
            return self.tr("untitled")

    def asJSON(self):
        metadata = {"title": self.title, 
                    "author": self.name, 
                    "email": self.email, 
                    "class": self.forclass, 
                    "organization": self.organization}
        slides = []
        sources = {}

        for slide in self.slides:
            sources[slide.source.identifier()] = {"reference": slide.source.reference, "mimetype": slide.source.mimetype}
            slides.append({"index": slide.index, "source": slide.source.identifier()})

        return json.dumps({"metadata": metadata, "slides": slides, "sources": sources})
        
class Source:

    def __init__(self, reference, mimetype=None):
        if mimetype == None:
            if os.path.exists(reference):
                mimetype = mimetypes.guess_type(reference)[0]
            else:
                raise RuntimeError("No mimetype was found for reference: %s" % reference)

        self.mimetype = mimetype
        self.reference = reference
        self.handler = plugins.mimehandlers[mimetype]
        self.container = self.handler.container(self.reference)

    def numSlides(self):
        return self.container.numSlides()

    def getSlide(self,index=0):
        return Slide(self,index)
        
    def identifier(self):
        return hashlib.sha1(self.reference + "***" + self.mimetype).hexdigest().upper()


     
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



