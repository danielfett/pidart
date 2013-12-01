'''
Define rules & strings that the Text-To-Speech engine outputs.
'''

from isat.tools import convenience, fieldtexts, remove_suffix, mod, num

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
    'next_player': ('Next player.', 'relaxed'),
    'press_start': ('Remove darts and press start!', 'relaxed'),

    # texts for a single dart
    'single_1': ('The right one!', 'excited'),
    'single_1_alt_1': ('Nice one!', 'amused'),

    # texts for two darts
    'again': ('And again!', 'happy'),

    # texts for three darts
    'washing_machine': ('Washing machine!', 'happy'),
    'double_washing_machine': ('Double washing machine!', 'happy'),
    'triple_washing_machine': ('Triple washing machine!', 'happy'),
    'triple_20': ('#Bar, uhaqerq, naq, rvtugl! Vaperqvoyr! Nznmvat! Snagnfgvp!', 'excited'),
    '100': ('One Hundred!', 'excited'),
    'over_100': ('Over 100!', 'excited'),

    # texts for hit_winner
    'checked_out_winner': ("Checked out! You are today's winner!", 'excited'),
    'checked_out': ('Checked out!', 'happy'),
    
    # texts for hit_bust
    'bust': ('Bust!', 'amused'),
    'bust_pro': ('Bust! Like a pro!', 'amused'),
    'double_bust': ('Double bust!', 'happy'),
    'triple_bust': ('Amazing triple bust!', 'excited'),
    'highest_bust': ('Highest possible bust.', 'interested'),
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
       
    rules = [
        # add the default field code text with a weight of 50
        {
            'use': True,
            'text': 'code_%s' % dart,
            'weight': 50
            },

        # add two simple rules for the single one field.
        {
            'use': dart == 'S1',
            'text': 'single_1',
            'weight': 30
            },

        {
            'use': dart == 'S1',
            'text': 'single_1_alt_1',
            'weight': 30
            },

        # say 'and again' when the same dart is hit again
        {
            'use': (dart_num > 1) and darts_so_far[-2] == dart,
            'text': 'again',
            'weight': 100
            },
        
        # add the all-famous washing machine(s).
        {
            'use': sorted(darts_so_far) == ['S1', 'S20', 'S5'],
            'text': 'washing_machine',
            'weight': 150
            },

        {
            'use': sorted(darts_so_far) == ['D1', 'D20', 'D5'],
            'text': 'washing_machine',
            'weight': 150
            },

        {
            'use': sorted(darts_so_far) == ['T1', 'T20', 'T5'],
            'text': 'washing_machine',
            'weight': 150
            },

        # Just a lot of points...
        {
            'use': (score_before_frame - score_after) == 100 ,
            'text': '100',
            'weight': 150
            },

        {
            'use': (score_before_frame - score_after) > 100 ,
            'text': 'over_100',
            'weight': 150
            },
        ]

    return rules

def hit_winner(state):
    dart, dart_num, darts_so_far, score_before_frame, \
        score_before, score_after = convenience(state)
    num_before = len(state.winners()) # players that checked out before
    rules = [
        {
            'use': num_before == 0,
            'text': 'checked_out_winner',
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
            'use': score_after > -30,
            'text': 'bust',
            'weight': 20
            },
        
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

        ]
    return rules
