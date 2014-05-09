

'''
Dart codes (e.g., S10) come with an "i" in the end iff the dart hit
the inner of the two single-fields. We are not interested in this, so
we remove this suffix.

'''

def remove_suffix(dart):
    if dart.endswith('i'):
        return dart[:-1]
    return dart
    
'''
From a dart code, return just the number (not the score!)

'''
def num(dart):
    return int(remove_suffix(dart[1:]))

'''
From a dart code without suffix, return just the multiplicator.

'''
def mod(dart):
    return dart[0]


'''
Form a dart code extract the number of points.
'''
def score2sum(score):
    if score.startswith('S'):
        multiplier = 1
    elif score.startswith('D'):
        multiplier = 2
    elif score.startswith('T'):
        multiplier = 3
    else:
        raise Exception("Unknown input: %s" % score)
    if score.endswith('i'):
        score = score[:-1]
    score = score[1:]
    return multiplier * int(score)

'''
Tell us if a score (integer) is single-dart checkoutable
'''
def singledart_checkoutable(score):
    return (score <= 20 or \
                (score <= 60 and score % 3 == 0) or \
                (score <= 40 and score % 2 == 0) or \
                score == 25 or \
                score == 50)


'''
Return possible checkout options.
'''
def checkout_options(score):
    if score < 0 or score > 60:
        return []
    o = []    
    if score < 20:
        o.append('S%d' % score)
    if score % 2 == 0 and score/2 <= 20:
        o.append('D%d' % (score/2))
    if score % 3 == 0 and score/3 <= 20:
        o.append('T%d' % (score/3))
    if score == 25:
        o.append('S25')
    elif score == 50:
        o.append('D25')
    return o

'''
Prepare some convenience variables from a given gamestate.
'''
def convenience(state):
    dart = remove_suffix(state.currentDarts[-1]) # the latest dart's
                                                 # score, e.g., T20
    dart_num = len(state.currentDarts) # number of dart in the current
                                       # frame
    darts_so_far = state.currentDarts
    score_before_frame = state.currentPlayer.score
    score_before = state.currentPlayer.score - \
        state.previousScore # the score of the player before the dart
                            # hit
    score_after = state.currentPlayer.score - \
        state.currentScore # the score afterwards
    return (dart, dart_num, darts_so_far, score_before_frame, score_before, score_after)

'''
What could this possibly be?

Note that this is intentionally overlapping at the end.

'''
RING = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5, 20, 1]

def in_ring(sequence):
    s = sorted(map(num, sequence))
    for i in range(len(RING) - len(s) + 1):
        if sorted(RING[i:i+len(s)]) == s:
            return True
    return False

'''
Say if two fields are adjacent to each other.
'''
def adjacent(a, b):
    '''
    We use the following rules:
    
    * if a and b are neighbors in the ring, and both have the same
      multiplicator, they are adjacent.

    * if a and b have the same number, but have a different
      modificator (with one being "S"), then they are adjacent.

    * only S25 is adjacent to D25
    '''
    if a == b:
        return True
    if num(a) == num(b) == 25:
        return True
    if num(a) == num(b) and (mod(a) == 'S' or mod(b) == 'S'):
        return True
    if mod(a) == mod(b) and (in_ring([a, b]) or in_ring([b, a])):
        return True
    return False
