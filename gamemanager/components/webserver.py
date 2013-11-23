""" Websockets connector """

from circuits import Component, Event, handler
from circuits.web.dispatchers import WebSockets
from circuits.web import Server, Controller, Logger, Static
from circuits.net.sockets import write, connect
#from circuits.web.tools import check_auth, basic_auth
 
import simplejson

from events import ReceiveInput

class SendState(Event):
    pass

class DartsServer(Component):
    channel = "wsserver"

    def __init__(self):
        Component.__init__(self)
        self.connectMessage = {'state': 'normal'}
        self.knownSockets = []

    def read(self, sock, data):
        if data == 'hello':
            msg_json = simplejson.dumps(self.connectMessage)
            self.fireEvent(write(sock, msg_json))
            self.knownSockets.append(sock)
        elif data.startswith('cmd:'):
            cmd, command = data.split(':')
            self.fireEvent(ReceiveInput('command', command))

    @handler('SendState')
    def SendState(self, msg):
        msg_json = simplejson.dumps(msg)
        for s in self.knownSockets:
            self.fireEvent(write(s, msg_json))
        self.connectMessage.update(msg)


class DartsServerController(Component):
    def serialize_short(self, state):
        return {
            'currentPlayer': state.players[state.currentPlayer],
            'currentDarts': state.currentDarts,
            'currentScore': state.scores[state.currentPlayer] - state.currentScore,
            'players': state.players
            }

    def serialize_full(self, state):
        a = self.serialize_short(state)
        a['ranking'] = state.player_list(sortby = 'started')
        return a

    @handler('GameInitialized', 'FrameFinished', 'FrameStarted')
    def _send_full_state(self, state):
        self.fire(SendState(self.serialize_full(state)))

    @handler('Hit', 'HitBust', 'HitWinner')
    def _send_short_state(self, state, code):
        self.fire(SendState(self.serialize_short(state)))

    def EnterHold(self, manual):
        self.fire(SendState({'state': 'hold'}))

    def LeaveHold(self, manual):
        self.fire(SendState({'state': 'normal'}))

    def GameOver(self, manual):
        self.fire(SendState({'state': 'gameover'}))


class Root(Controller):

    def index(self):
        return 
    '''
    def protected(self):
        realm = "Test"
        users = {"admin": "admin"}
        encrypt = str

        if check_auth(self.request, self.response, realm, users, encrypt):
            return "Hello %s" % self.request.login

        return basic_auth(self.request, self.response, realm, users, encrypt)
    '''

Webserver = Server(('0.0.0.0', 8080))
Static(docroot="../html/").register(Webserver)
DartsServer().register(Webserver)
DartsServerController().register(Webserver)
Root().register(Webserver)
#Logger().register(Webserver)
WebSockets("/websocket").register(Webserver)
