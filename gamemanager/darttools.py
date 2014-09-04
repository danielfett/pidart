

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

checkoutable_scores = [ [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 30, 32, 33, 34, 36, 38, 39, 40, 42, 45, 48, 50, 51, 54, 57, 60],
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 104, 105, 107, 108, 110, 111, 114, 117, 120],
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 164, 165, 167, 168, 170, 171, 174, 177, 180] ]
'''
Tell us if a score (integer) is checkoutable with remainingdarts left
'''
def checkoutable(score,remainingdarts):
    return score in checkoutable_scores[remainingdarts-1]


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
