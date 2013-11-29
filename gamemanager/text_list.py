'''Texts that are prepared and can be used later. The key is an
identifier that can be used as a file name. The value-pair consists of
the text and the emotionml-emotion for this text. 
The list of emotions that can be used here is: 

  * affectionate	
  * afraid	
  * amused	
  * angry	
  * bored	
  * confident	
  * content	
  * disappointed	
  * excited	
  * happy	
  * interested	
  * loving	
  * pleased	
  * relaxed	
  * sad	
  * satisfied	
  * worried

(from http://www.w3.org/TR/emotion-voc/#everyday-categories)

'''

texts = {
    'single_1': ('The right one!', 'excited'),
    'single_1_alt_1': ('Nice one!', 'amused'),
}

'''We now want to add to this list the texts for the single-dart
hits. We use this dictionary to define the texts and emotions for
these with respect to the field that was hit (c).

'''

multiplicators = {
    'S': lambda c: (c, 'relaxed' if c < 15 else 'happy'),
    'D': lambda c: ('Double %s!' % c, 'relaxed' if c < 10 else 'happy'),
    'T': lambda c: ('Triple %s!' % c, 'happy' if c < 7 else 'excited')
}

for c in range(1, 21):
    for m in multiplicators.keys():
        code = "code_%s%s" % (m, c)
        texts[code] = multiplicators[m](c)

text_dir = '../sounds/cached-mary/'

def mary_params(text, emotion):
    eml = '''
    <emotionml version="1.0" xmlns="http://www.w3.org/2009/10/emotionml" 
    category-set="http://www.w3.org/TR/emotion-voc/xml#everyday-categories">
    <emotion><category name="%s"/>
    %s
    </emotion>
    </emotionml>
    ''' % (emotion, text)

    return {
        'INPUT_TYPE': 'EMOTIONML',
        'OUTPUT_TYPE': 'AUDIO',
        'INPUT_TEXT': eml,
        'effect_Stadium_selected': 'on',
        'effect_Stadium_parameters': 'amount:100.0',
        'VOICE_SELECTIONS': 'cmu-bdl-hsmm en_US male hmm',
        'AUDIO_OUT': 'WAVE_FILE',
        'LOCALE': 'en_US',
        'VOICE': 'cmu-bdl-hsmm',
        'AUDIO': 'WAVE_FILE',
        }


''' Generate cached voices. '''
if __name__ == '__main__':
    print "Generating cache of voices to store in %s." % text_dir
    from urllib import urlencode
    from urllib2 import Request, urlopen, HTTPError
    from os.path import join
    SERVER_URL = 'http://localhost:59125/process'

    print "Using server URL %s." % SERVER_URL
    for id, text in texts.items():
        print "Text: '''%s'''" % text[0]
        data = urlencode(mary_params(*text))
        req = Request(SERVER_URL, data)
        response = urlopen(req)
        outfile = join(text_dir, "%s.wav" % id)
        with open(outfile, 'w') as f:
            f.write(response.read())
        
    
