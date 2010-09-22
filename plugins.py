import os
import sys

content = []
pointer = []
mimehandlers = {}

sys.path.insert(0,"plugins/")

for f in os.listdir("plugins/"):
    if f.endswith(".py"):
        module = __import__(f[:-3])
        
        if module.plugintype == "content":
            content.append(module)
            mimehandlers[module.mimetype] = module
        if module.plugintype == "pointer":
            pointer.append(module)


