from circuits import Event

class ReceiveInput(Event):
    """ Some input arrived (fieldcode or other input) """

class StartGame(Event):
    """ Start a new game. """

class GameInitialized(Event):
    """ A new game was started. """

class DartStuck(Event):
    """ A dart is stuck. May be fired many times in a row. """

class SkipPlayer(Event):
    """ The button for skipping a player was pressed. """

class CodeNotImplemented(Event):
    """ This part of the code is not implemented. """

class Hit(Event):
    """ A dart hit the board. """

class HitBust(Event):
    """ A dart hit the board, but busted. """

class HitWinner(Event):
    """ A dart hit the board, and the player won. """

class EnterHold(Event):
    """ Wait for the player to hit start. """

class LeaveHold(Event):
    """ Player has pressed start to continue. """

class FrameStarted(Event):
    """ A new frame was started. """

class FrameFinished(Event):
    """ A player has thrown three darts (or the round was skipped, etc.) """

class GameOver(Event):
    """ The game is over. """
