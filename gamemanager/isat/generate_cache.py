from .rules import texts
from .tools import tts_filename, rot13
from subprocess import Popen, PIPE

'''
Assemble parameters for mary speech engine.
'''
def mary_params(text, emotion):
    if text.startswith('#'):
        text = rot13(text[1:])
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
        #'effect_Stadium_selected': 'on',
        #'effect_Stadium_parameters': 'amount:100.0',
        'AUDIO_OUT': 'WAVE_FILE',
        'LOCALE': 'en_US',
#        'VOICE': 'cmu-bdl-hsmm',
        'VOICE': 'cmu-rms-hsmm',
        'AUDIO': 'WAVE_FILE',
        }

def convert_sample_rate(infile, outfilename):
    sox = Popen(['sox', '-r', '16000', '-', '-r', '44100', outfilename], stdin=PIPE)
    sox.stdin.write(infile.read())
    sox.communicate()


'''
Generate cached voices.
'''
if __name__ == '__main__':
    print "Generating cache of voices."
    from urllib import urlencode
    from urllib2 import Request, urlopen, HTTPError
    SERVER_URL = 'http://localhost:59125/process'

    print "Using server URL %s." % SERVER_URL
    for id, text in texts.items():
        print "Text: '''%s'''" % text[0]
        data = urlencode(mary_params(*text))
        req = Request(SERVER_URL, data)
        response = urlopen(req)
        outfile = tts_filename(id)
        convert_sample_rate(response, outfile)
        
    
