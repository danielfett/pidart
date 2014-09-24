'''
Define rules & strings that the Text-To-Speech engine outputs.
'''

from isat.tools import fieldtexts 
from darttools import *
from operator import or_

'''Texts that are prepared and can be used later are stored in
``texts''. The key in this dictionary is an identifier that can be
used as a file name. The value-pair consists of the text and the
emotionml-emotion for this text.  The list of emotions that can be
used here is:

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

If you like, encode your texts using ROT13 to preserve the surprise
moment for anybody who reads this file. Prepend a '#' in front of the
text then. Did you know that EMACS has a macro called 'rot13-region'?
'''
texts = {
    # texts for general usage
    'ready': ('Ready.', 'pleased'),
    'next_player': ('Next player.', 'pleased'),
    'press_start': ('Remove darts!', 'pleased'),
    'good_choice': ('Excellent choice', 'pleased'),
    'train': ('Did you train for that?', 'pleased'),
    'same_three_darts': ('What a boring choice.', 'bored'),
    'less_than_10': [('#Jung qvq lbh qbb?', 'disappointed'),
                     ('#Hu-bu.', 'disappointed')],
    'less_than_3': [('Great.', 'disappointed'),
                    ('That will be fun.', 'disappointed'),
                    'wav:others/ahem_x',
                    'wav:others/gasp_x'
                    ],
    'close': ('That was close!', 'happy'),

    'low_start': ('Just take your time.', 'bored'),

    # texts for a single dart
    'single_1': [('The right one!', 'excited'),
                 ('A Nice one!', 'amused'),
                 ('The one and only one!', 'interested')],

    'triple_1': 'wav:others/gasp_x',

    # texts for two darts
    'again': ('And again!', 'happy'),

    # texts for three darts
    'washing_machine': ('Washing machine!', 'happy'),
    'double_washing_machine': ('Double washing machine!', 'happy'),
    'triple_washing_machine': ('Triple washing machine!', 'happy'),
    'highest_washing_machine': ('Highest possible washing machine!', 'happy'),
    'triple_triple_20': 'wav:others/hallelujah-trail',
    'going_for_washing_machine': ('Going for a washing machine', 'pleased'),

    # text for checkout zone
    'checkout_area': ('Welcome to checkout area!', 'happy'),
    'checkout_single': ('Single-Dart check-outable', 'happy'),

    # texts for hit_winner
    #'checked_out_winner': ("Checked out! You are today's winner!", 'excited'),
    'checked_out_winner': 'wav:wwm/spielende',
    'checked_out_winner_2': 'wav:others/hallelujah-trail',
    #'checked_out': ('Checked out!', 'happy'),
    
    # texts for hit_bust
    'bust': ('Bust!', 'amused'),
    'bust_pro': ('Bust! Like a pro!', 'amused'),
    'double_bust': ('Double bust!', 'happy'),
    'triple_bust': ('Amazing triple bust!', 'excited'),
    'highest_bust': ('Highest possible bust.', 'interested'),

    # wave files, these are referenced to by their path
    'pull_up': 'wav:aviation/pull-up',
    'pull_up_2': 'wav:aviation/terrain-ahead-pull-up',
    'zonk': 'wav:zonk',

    # high points
    'high_triple': ['wav:others/cash_register2', 'wav:others/cash_register_x'],
    'over_100': ['wav:others/applause2_x', 'wav:others/applause3', 'wav:others/cheering'],
    
    # generic',
    'boing': ['wav:others/boing_x',
              'wav:others/arrow2',
              'wav:others/arrow_x',
              'wav:others/boing2',
              'wav:others/boing3'],

    # checkout',
    'checked_out': ['wav:others/fanfare3',
                    'wav:others/fanfare_x',
                    'wav:others/fanfare2'],

    # good check-out position',
    'good_check_out': ['wav:others/drum_roll2',
                       'wav:others/drum_roll_y'],

    'check_out_still_possible': 'wav:others/gasp_ohhh',
                 
}

'''
Add default texts for code_S1 to code_T20, code_S25 and code_D25.
'''
texts.update(fieldtexts)

'''
Now we can define the rules for these texts.
'''

def hit(state):
    dart, dart_num, darts_so_far, score_before_frame, \
        score_before, score_after = convenience(state)
    '''
    We now assemble the rules-list. Each rule is a dictionary with the
    following elements:
      * use: True if this rule can be use. Write any expression here.
      * text: The *key* of the text in the ``texts'' dictionary (above).
      * weight: A weight that is used for the random selection of the texts.

    Besides the variables above, you can apply mod() and num() to
    dart-values to get the multiplicator or the numeric value,
    respectively.
    '''
    coo = None
    if singledart_checkoutable(score_before):
        coo = checkout_options(score_before)

    rules = [
        {
            'use': (score_before - score_after) < 5,
            'text': 'good_choice',
            'weight': 20,
            },
        {
            'use': len(darts_so_far) == 3 and (darts_so_far[0] == darts_so_far[1] == darts_so_far[2]),
            'text': 'train',
            'weight': 20,
            },
        {
            'use': len(darts_so_far) == 3 and (darts_so_far[0] == darts_so_far[1] == darts_so_far[2]),
            'text': 'same_three_darts',
            'weight': 20,
            },
        {
            'use': score_after < 10 and len(darts_so_far) == 3,
            'text': 'less_than_10',
            'weight': 100,
            },

        {
            'use': score_after < 3 and len(darts_so_far) == 3,
            'text': 'less_than_3',
            'weight': 200,
            },
        {
            'use': score_after > 200 and len(darts_so_far) == 1 and (score_before - score_after) < 10,
            'text': 'low_start',
            'weight': 20,
            },
        {
            'use': (dart == 'T1' or dart == 'T2' or dart == 'T3') and score_before > 50,
            'text': 'triple_1',
            'weight': 50
            },
        # check if the player missed by one field
        {
            'use': coo != None and \
                reduce(or_, map(lambda x: adjacent(dart,x), coo)),
            'text': 'close',
            'weight': 100
            },
        {
            'use': coo != None and \
                reduce(or_, map(lambda x: adjacent(dart,x), coo)) and\
                singledart_checkoutable(score_after),
            'text': 'check_out_still_possible',
            'weight': 150
            },
        # add the default field code text with a weight of 50
        {
            'use': True,
            'text': 'code_%s' % dart,
            'weight': 50
            },
        {
            'use': True,
            'text': 'boing',
            'weight': 2
                },

        # add two simple rules for the single one field.
        {
            'use': dart == 'S1',
            'text': 'single_1',
            'weight': 90
            },


        # say 'and again' when the same dart is hit again
        {
            'use': (dart_num > 1) and darts_so_far[-2] == dart,
            'text': 'again',
            'weight': 100
            },

        # good check out position
        {
            'use': score_after > 11 and score_after < 21,
            'text': 'good_check_out',
            'weight': 20
            },
        
        # add the all-famous washing machine(s).
        {
            'use': len(darts_so_far) == 3 and in_ring(darts_so_far) and [mod(darts_so_far[x]) for x in range(3)] == ['S' * 3],
            'text': 'washing_machine',
            'weight': 150
            },
        {
            'use': len(darts_so_far) == 3 and in_ring(darts_so_far) and [mod(darts_so_far[x]) for x in range(3)] == ['D' * 3],
            'text': 'double_washing_machine',
            'weight': 150
            },
        {
            'use': len(darts_so_far) == 3 and in_ring(darts_so_far) and [mod(darts_so_far[x]) for x in range(3)] == ['T' * 3],
            'text': 'triple_washing_machine',
            'weight': 150
            },
        {
            'use': 'S19' in darts_so_far and 'S7' in darts_so_far and 'S16' in darts_so_far,
            'text': 'highest_washing_machine',
            'weight': 300
            },
        {
            'use': len(darts_so_far) == 2 and in_ring(darts_so_far),
            'text': 'going_for_washing_machine',
            'weight': 150
            },

        # Just a lot of points...
        {
            'use': score_after <= 180 and score_before > 180,
            'text': 'checkout_area',
            'weight': 150
            },

        {
            'use': singledart_checkoutable(score_after) and score_after > 20,
            'text': 'checkout_single',
            'weight': 100
            },

        {
            'use': dart in ['T20', 'T19', 'T18', 'T17'],
            'text': 'high_triple',
            'weight': 70
                },
                

        {
            'use': darts_so_far == ['T20' * 3],
            'text': 'triple_triple_20',
            'weight': 100000
            },

        # over 100
        {
            'use': (len(darts_so_far) == 3) and (score_before_frame - score_after) >= 100,
            'text': 'score_%s' % (score_before_frame - score_after),
            'weight': 150
            },
        {
            'use': (score_before_frame - score_after) >= 100,
            'text': 'over_100',
            'weight': 150
            },

        # pull up!
        {
            'use': (len(darts_so_far) < 3) and score2sum(darts_so_far[-1]) > score_after,
            'text': 'pull_up',
            'weight': 80,
            },
        # pull up!
        {
            'use': (len(darts_so_far) < 3) and score_after < 10 and score2sum(darts_so_far[-1]) > score_after,
            'text': 'pull_up_2',
            'weight': 80,
            },
        ]

    return rules

def hit_winner(state):
    dart, dart_num, darts_so_far, score_before_frame, \
        score_before, score_after = convenience(state)
    num_before = len(state.winners()) # players that checked out before
    rules = [
#        {
#            'use': num_before == 0,
#            'text': 'checked_out_winner',
#            'weight': 50
#            },
        
        {
            'use': num_before == 0,
            'text': 'checked_out_winner_2',
            'weight': 50
            },
        {
            'use': num_before > 0,
            'text': 'checked_out',
            'weight': 50
            }
        ]
    return rules

def hit_bust(state):
    dart, dart_num, darts_so_far, score_before_frame, \
        score_before, score_after = convenience(state)
    # note that score_after is now a negative number
    rules = [
        {
            'use': score_after <= -30,
            'text': 'bust_pro',
            'weight': 40
            },

        {
            'use': mod(dart) == 'D',
            'text': 'double_bust',
            'weight': 30
            },

        {
            'use': mod(dart) == 'T',
            'text': 'triple_bust',
            'weight': 30
            },
        
        {
            'use': dart == 'T20',
            'text': 'highest_bust',
            'weight': 70
            },
        {
            'use': True,
            'text': 'zonk',
            'weight': 30
            },

        ]
    return rules
