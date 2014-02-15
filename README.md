pidart
======

Run the dart game by changing to the gamemanager subdirectory, then
execute

    sudo ./game.py

(root rights are required for serial port access, unless explicitely
configured otherwise). Refer to 

    ./game.py --help

for further options. 

There are three sound systems available, the legacy sounds (uses the
sound files stored in sounds/old-*, the espeak sounds (uses TTS on the
fly), and the ISAT sounds (for InfSec Adaptive TTS). It uses the
legacy sounds plus pre-generated sound files from the MARY TTS system
in sounds/cached-mary. The MARY TTS system supports some emotions in
the generated voices. The sound files are (more or less) randomly
selected, as defined by rules that may depend on the current game
situation.

Adding/updating rules for the commentator
-----------------------------------------

Texts and rules are stored in gamemanager/isat/rules.py.

In the first part of this file, a list of texts is defined (see
comments there). The second part contains the rules that are applied
to select these texts.

After adding/changing stuff there, make sure to run the tests and, if
needed, to generate the sound files from the texts (for both see
below).

Testing
-------

All tests can be run by executing 

    nosetests -v

in the gamemanager directory.

Generating Sound File Cache
---------------------------

Sound files are cached. Without the cache, the ISAT sounds cannot be
used. To generate the sound files from the rules file, use

    python -m isat.generate_rules

in the gamemanager directory.

Changing Settings
-----------------

To change settings, create a file called "settings.py" in the gamemanager subdirectory. Example contents:

	users = {"pidart_username": "pidart_password"}
	port = 8181
	listen = '127.0.0.1'

Installation on a Raspberry Pi
==============================

sudo apt-get install python-dev python-espeak sox mercurial
hg clone https://bitbucket.org/webhamster/circuits-dev
cd circuits-dev
sudo python setup.py install
