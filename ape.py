import asyncore, asynchat
import socket
import json
import string
import random
import threading
import time
import select
import urllib

class APEConnection(asynchat.async_chat):

    def __init__(self, apeclient):
        asynchat.async_chat.__init__(self)
        
        self.apeclient = apeclient
        self.callback_func = apeclient.callback
        self.set_terminator("\n\n")
        self.data = ""
        self.gotheaders = False
        self.age = time.time()
        self.timeout = 15
        
        if self.apeclient.state == 0:
            cmd = 'connect'
            params = {'name': self.apeclient.name}

        elif self.apeclient.state == 1:
            cmd = 'join'
            params =  {'channels': self.apeclient.channel}

        elif self.apeclient.state == 2:
            if len(self.apeclient.msgqueue) > 0:
                msg = self.apeclient.msgqueue.pop(0)
                cmd = 'send'
                params =  {"msg": self.escape(msg), "pipe": self.apeclient.pipeid}
            else:
                cmd = 'check'
                params =  {}

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.apeclient.host, self.apeclient.port))

        data = [{'cmd': cmd.upper(),'chl': self.apeclient.challenge, 'params': params}]

        if self.apeclient.sessid:
            data[0]['sessid'] = self.apeclient.sessid

        data_json = json.dumps(data, False, True, True, True, json.JSONEncoder, None, (',',':'))

        s  = "POST /%d/? HTTP/1.1\r\n" % self.apeclient.protocol
        s += "Host: %s:%d\r\n" % (self.apeclient.host,self.apeclient.port)
        s += "Accept-Encoding: identity\r\n"
        s += "Content-type: application/x-www-form-urlencoded; charset=utf-8\r\n"
        s += "Keep-alive: 60\r\n"
        s += "Connection: Keep-alive\r\n"
        s += "Content-Length: %d\r\n" % len(data_json)
        s += "\r\n"
        s += data_json

        self.push(s)
        self.apeclient.challenge += 1
        
        if len(self.apeclient.msgqueue) > 0:
            self.close()

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
                self.apeclient.sessid = value["sessid"]
                self.apeclient.state = 1
                self.close()
            elif key == u"CHANNEL":
                self.apeclient.pipeid = value["pipe"]["pubid"]
                self.apeclient.state = 2
            elif key == u"CLOSE":
                self.close()
            elif key == u"ERR":
                self.apeclient.terminate = True
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
        if time.time() - self.age > self.timeout:
            self.close()
        return 1

    def callback(self,msg):
        if self.callback_func:  
            self.callback_func(self.apeclient,self.descape(msg))
            
    def escape(self,msg):
        return urllib.quote(msg)
        
    def descape(self,msg):
        return urllib.unquote(msg)
        
class APEClient:

    def __init__(self, host, port, channel, frequency=0, callback=None):
        self.frequency = frequency
        self.channel = channel
        self.host = str(frequency) + "."  + host
        self.port = port
        self.name = ''.join(random.sample(list(string.letters + string.digits),16))
        self.challenge = 1
        self.state = 0
        self.protocol = 1 # XHR
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
                self.connection = APEConnection(self)
                asyncore.loop(1)
            except select.error:
                pass

            
    def connect(self):
        self.thread.start()

    def close(self):
        self.terminate = True
        self.thread.join(0)
        self.connection.close()

    def send(self,msg):
        self.msgqueue.append(msg)
        if self.connection:
            self.connection.close()


