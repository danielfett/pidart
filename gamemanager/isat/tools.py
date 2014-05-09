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

