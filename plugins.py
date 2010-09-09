import os
import sys

content = []
pointer = []
mimehandlers = {}

sys.path.insert(0,"plugins/")

for f in os.listdir("plugins/"):
    if f.endswith(".py"):
        module = __import__(f[:-3])
        
        if module.plugin_info["type"] == "content":
            content.append(module)
            mimehandlers[module.plugin_info["mimetype"]] = module
        if module.plugin_info["type"] == "pointer":
            pointer.append(module)


