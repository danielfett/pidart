#!/usr/bin/python

players = ['T1', 'T2', 'T3']

class SkipPlayer(Exception):
    pass

class DartGame(object):
    NUMBEROFDARTS = 3

    def __init__(self, players):
        self.players = players

    @staticmethod
    def score2sum(score):
        multiplier = 1
        if score.startswith('D'):
            multiplier = 2
            score = score[1:]
        elif score.startswith('T'):
            multiplier = 3
            score = score[1:]
        return multiplier * int(score)

    def input_score(self):
        while True:
            inp = raw_input('? ').strip()
            if inp == 'skip':
                raise SkipPlayer
            try:
                return self.score2sum(inp)
            except ValueError:
                print "Illegal input value: %s" % inp

    def round(self):
        # input NUMBEROFDARTS darts from the board
        darts = []
        for dart in range(self.NUMBEROFDARTS):
            darts.append(self.input_score())
        return darts

    def get_next_player(self, skip = []):
        min_val = 99999
        min_player = None
        for player in self.players:
            if player in skip:
                continue
            num_rounds = len(self.scores[player])
            if num_rounds < min_val:
                min_player = player
                min_val = num_rounds
        return min_player

    def print_stats(self):
        for r in self.players:
            print "%s\t|" % r,
            for scores in self.scores[r]:
                print "%d\t|" % sum(scores),
            print ""

    def go(self):
        self.scores = {}
        for p in self.players:
            self.scores[p] = []

        player = self.get_next_player()
        while True:
            self.print_stats()    
            print "Now playing: %s" % player
            try:
                res = self.round()
                self.scores[player].append(res)
                player = self.get_next_player()
            except SkipPlayer:
                print "Player skipped."
                player = self.get_next_player([player])
            
        

    
if __name__ == "__main__":
    d = DartGame(players)
    d.go()
    
