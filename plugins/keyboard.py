from PyQt4.QtCore import *
from PyQt4.QtGui import *

class pointer(QObject):

    def __init__(self, controller):
        self.controller = controller
        self.next1 = QShortcut(QKeySequence("PgDown"),self.controller.mainview)
        self.prev1 = QShortcut(QKeySequence("PgUp"),self.controller.mainview)
        self.next2 = QShortcut(QKeySequence("Right"),self.controller.mainview)
        self.prev2 = QShortcut(QKeySequence("Left"),self.controller.mainview)
        
    def enable(self):
        self.connect(self.prev1,SIGNAL("activated()"),self.controller.previousSlide)
        self.connect(self.next1,SIGNAL("activated()"),self.controller.nextSlide)
        self.connect(self.prev2,SIGNAL("activated()"),self.controller.previousSlide)
        self.connect(self.next2,SIGNAL("activated()"),self.controller.nextSlide)
        return True

    def disable(self):
        self.disconnect(self.prev1,SIGNAL("activated()"),self.controller.previousSlide)
        self.disconnect(self.next1,SIGNAL("activated()"),self.controller.nextSlide)
        self.disconnect(self.prev2,SIGNAL("activated()"),self.controller.previousSlide)
        self.disconnect(self.next2,SIGNAL("activated()"),self.controller.nextSlide)
        return True



plugintype     = 'pointer'
name           = 'Keyboard'
description    = 'Keyboard and keyboard-like remotes'
capabilities   = ['control']
enabledefault  = True
