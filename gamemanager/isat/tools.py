from os.path import join
import codecs

def rot13(s):
    return codecs.encode(s, 'rot_13')

'''
Directory for generated sound files.
'''
text_dir = '../sounds/' # base path
tts_dir = 'cached-mary' # added for tts sounds
wav_dir = '.'           # added for wave files

'''
Get the name of the audio file for given text id.

'''
def isat_filename(text_id, text_desc):
    if type(text_desc) == tuple:
        return join(text_dir, tts_dir, "%s.wav" % text_id)
    elif type(text_desc) == str:
        if text_desc.startswith('wav:'):
            return join(text_dir, wav_dir, "%s.wav" % text_desc[4:])
    raise Exception("Unknown text format: %s %r" % (text_id, text_desc))
                       


'''We prepare a list of texts for the single-dart hits (e.g., as
code_S20). We use this dictionary to define the texts and emotions for
these with respect to the field that was hit (c).

'''

fieldtexts = {
    'code_S25': ("Bull's eye!", 'happy'),
    'code_D25': ("Inner Bull's eye!", 'excited')
}

multiplicators = {
    'S': lambda c: ('%s' % c, 'relaxed' if c < 15 else 'happy'),
    'D': lambda c: ('Double %s!' % c, 'relaxed' if c < 10 else 'happy'),
    'T': lambda c: ('Triple %s!' % c, 'happy' if c < 7 else 'excited')
}

for c in range(1, 21):
    for m in multiplicators.keys():
        code = "code_%s%s" % (m, c)
        fieldtexts[code] = multiplicators[m](c)

'''Prepare announcements for 100 to 180'''
for c in range(100, 181):
    fieldtexts['score_%s' % c] = ('%s' % c, 'excited')

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
From a dart code without suffix, return just the number (not the score!)

'''
def num(dart):
    return int(dart[1:])

'''
From a dart code without suffix, return just the multiplicator.

'''
def mod(dart):
    return dart[0]

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
    for i in range(len(RING) - len(sequence) + 1):
        if RING[i:i+len(sequence)] == sequence:
            return True
    return False

'''
Say if two fields are adjacent to each other. Works only with removed
suffixes.
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
    if mod(a) == mod(b) and (in_ring([num(a), num(b)]) or in_ring([num(b), num(a)])):
        return True
    return False
