from .rules import texts
from .tools import isat_filename, rot13
from subprocess import Popen, PIPE
import argparse
import sys

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

def generate_wav_file(server, id, text):
    print "Text: '''%s'''" % text[0]
    data = urlencode(mary_params(*text))
    req = Request(server, data)
    response = urlopen(req)
    outfile = isat_filename(id, text)
    convert_sample_rate(response, outfile)
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates a cache of rendered TTS audio files for later usage. Automatically caches all texts in the rules.py file. Needs a MaryTTS server for generating the audio and SOX must be installed to convert the audio files.')
    parser.add_argument('server', metavar='server_url', type=str, help='MaryTTS web server URL, e.g. http://localhost:59125/process', default='http://localhost:59125/process')
    args = parser.parse_args()
    from urllib import urlencode
    from urllib2 import Request, urlopen, HTTPError

    print "Using server URL %s." % args.server
    for id, text in texts.items():
        
        if type(text) == list:
            for t in text:
                if type(t) != tuple:
                    continue
                generate_wav_file(args.server, id, t)
        elif type(text) != tuple:
            continue
        else:
            generate_wav_file(args.server, id, text)            
        



    
