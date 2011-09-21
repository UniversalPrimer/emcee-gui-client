import asyncore, asynchat
import socket
import json
import string
import random
import threading
import time
import select
import urllib

class PushyConnection(asynchat.async_chat):

    def __init__(self, pushyclient):
        asynchat.async_chat.__init__(self)

        self.set_terminator("\n\n")        
        self.pushyclient = pushyclient
        self.callback_func = pushyclient.callback
        self.data = ""
        self.gotheaders = False
        self.age = time.time()
#        self.timeout = 15

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.pushyclient.host, self.pushyclient.port))

#    TODO re-instate this?
#        if len(self.pushyclient.msgqueue) > 0:
#            data = self.pushyclient.msgqueue.pop(0)


        print "connected"
        print "queue length: " + str(len(self.pushyclient.msgqueue))

        self.send_raw("RAW")

        self.send_msg({
                'session_id': self.gen_session_id(),
                'channel_id': self.pushyclient.channel
                })
        
#        if len(self.pushyclient.msgqueue) > 0:
#            self.close()

#    def send_msg(self, msg):
#        data = json.dumps(msg)
#        len_str = str(len(data)) 
#        len_str = ('0'*(8-len(len_str))) + len_str
#        data = len_str + data
#        self.push(data)

    def send_msg(self, msg):
        data = json.dumps(msg) + "\n"
        print "SENDING: " + data
        self.push(data)

    def send_raw(self, data):
        self.push(data)


    def gen_session_id(self):
        return ''.join(random.sample(list(string.letters + string.digits),8))

    def handle_expt(self):
        self.close()

    def collect_incoming_data(self, data):
        self.data = self.data + data

    def found_terminator(self):

        data = self.data
        if data.endswith("\r"):
            data = data[:-1]
        self.data = ""

        if not self.gotheaders:
            (headers, data) = data.split("\r\n\r\n",1)
            self.gotheaders = True

        reply = json.loads(data.strip())
        self.handle_reply(reply)
            

    def handle_reply(self,reply):
        self.age = time.time()
        for item in reply:
            key = item["raw"]
            value = item["data"]
            if key == u"LOGIN":
                self.pushyclient.sessid = value["sessid"]
                self.pushyclient.state = 1
                self.close()
            elif key == u"CHANNEL":
                self.pushyclient.pipeid = value["pipe"]["pubid"]
                self.pushyclient.state = 2
            elif key == u"CLOSE":
                self.close()
            elif key == u"ERR":
                self.pushyclient.terminate = True
                print value
            elif key == u"DATA":
                self.callback(value["msg"])
            elif key == u"IDENT":
                pass
            elif key == u"LEFT":
                pass
            elif key == u"JOIN":
                pass
            else:
                print "Unhandled: " + key
                print value

    def readable(self):
#        if time.time() - self.age > self.timeout:
#           self.close()
        return 1

    def callback(self,msg):
        if self.callback_func:  
            self.callback_func(self.pushyclient,self.descape(msg))
            
    def escape(self,msg):
        return urllib.quote(msg)
        
    def descape(self,msg):
        return urllib.unquote(msg)
        
class PushyClient:

    def __init__(self, host, port, channel, frequency=0, callback=None):
        self.frequency = frequency
        self.channel = channel
        self.host = host
        self.port = port
        self.challenge = 1
        self.state = 0
        self.sessid = None
        self.pipeid = None
        self.callback = callback
        self.terminate = False
        self.connection = None
        self.thread = threading.Thread(target=self.run)
        self.msgqueue = []

    def run(self):
        while not self.terminate:
            try:
                self.connection = PushyConnection(self)
                asyncore.loop(1)
            except select.error:
                pass

            
    def connect(self):
        self.thread.start()

    def close(self):
        self.terminate = True
        self.thread.join(0)
        self.connection.close()


    def send(self, msg):
        self.connection.send_msg(msg)
