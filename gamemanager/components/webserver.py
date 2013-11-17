""" Websockets connector """

from circuits import Component
from circuits.core import handler
from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import WebSocketServerFactory, \
                               WebSocketServerProtocol, \
                               listenWS
 
from threading import Thread
from Queue import Queue
import simplejson

class DartsProtocol(WebSocketServerProtocol):
    def __init__(self):
        self.queue = Queue()

    def onOpen(self):
        self.factory.register(self)     

class DartsServerFactory(WebSocketServerFactory):
   def __init__(self, url, debug = False, debugCodePaths = False):
       WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debugCodePaths)
       self.clients = []
       self.connectMessage = {}
      
   def broadcast(self, msg):
       msg_json = simplejson.dumps(msg)
       for client in self.clients:
           client.sendMessage(msg_json)
       self.connectMessage.update(msg)
       

   def register(self, client):
       if not client in self.clients:
           print "registered client " + client.peerstr
           self.clients.append(client)
           if len(self.connectMessage):
               client.sendMessage(simplejson.dumps(self.connectMessage))

   def unregister(self, client):
       if client in self.clients:
           print "unregistered client " + client.peerstr
           self.clients.remove(client)

class Webserver(Component):
    def __init__(self):
        super(Webserver, self).__init__()
        self.factory = DartsServerFactory("ws://localhost:9000")

        self.factory.protocol = DartsProtocol
        self.factory.setProtocolOptions(allowHixie76 = True)
        listenWS(self.factory)
        
        webdir = File("../html/")
        web = Site(webdir)
        reactor.listenTCP(8080, web)
        self.thread = Thread(target=reactor.run, args=(), kwargs={'installSignalHandlers':0})
        self.thread.daemon = True
        self.thread.start()

    def serialize_short(self, state):
        return {
            'currentPlayer': state.players[state.currentPlayer],
            'currentDarts': state.currentDarts,
            'currentScore': state.scores[state.currentPlayer]
            }

    def serialize_full(self, state):
        a = self.serialize_short(state)
        a['ranking'] = state.player_list(sortby = 'order')
        return a

    @handler('game_initialized', 'round_finished', 'round_started')
    def _send_full_state(self, state):
        self.factory.broadcast(self.serialize_full(state))

    @handler('hit', 'hit_bust', 'hit_winner')
    def _send_short_state(self, state, code):
        self.factory.broadcast(self.serialize_short(state))

    def enter_hold(self, manual):
        self.factory.broadcast({'state': 'hold'})

    def leave_hold(self, manual):
        self.factory.broadcast({'state': 'normal'})

    def game_over(self, manual):
        self.factory.broadcast({'state': 'gameover'})
