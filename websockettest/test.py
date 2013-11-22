'''#!/usr/bin/env python

from circuits import Component, Debugger, Timer, Event
from circuits.web.websockets import WebSocketsDispatcher
from circuits.web import Server, Controller, Logger
from circuits.net.events import write
from circuits.web.tools import check_auth, basic_auth

class sendout(Event):
    pass

class DartServer(Component):

    channel = "wsserver"

    def sendout(self, msg):
        self.fireEvent(write('x', msg))

    def read(self, sock, data):
        print "Received: " + data
        self.fireEvent(write(sock, data))



class Root(Controller):

    def index(self):
        return file('index.html', 'r').read()

class Bla(Component):
    
    def started(self, blab):
        Timer(2, sendout('hallo welt.\n'), persist=True).register(self)


app = Server(("0.0.0.0", 8000))
DartServer().register(app)
Root().register(app)
Logger().register(app)
Debugger().register(app)
Bla().register(app)
WebSocketsDispatcher("/websocket", wschannel='wsserver').register(app)
app.run()
'''
#!/usr/bin/env python

from circuits import Component
from circuits.web.dispatchers import WebSockets
from circuits.web import Server, Controller, Logger
from circuits.net.sockets import write


class Echo(Component):

    channel = "wsserver"

    def read(self, sock, data):
        self.fireEvent(write(sock, "Received: " + data))


class Root(Controller):

    def index(self):
        return "Hello World!"

app = Server(("0.0.0.0", 8000))
Echo().register(app)
Root().register(app)
Logger().register(app)
WebSockets("/websocket").register(app)
app.run()
