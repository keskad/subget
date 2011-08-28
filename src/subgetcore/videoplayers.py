""" Integration with Video Players """

import os

def Spawn(Subget, VideoFile, Subtitles):
    DefaultPlayer = Subget.Config['afterdownload']['defaultplayer']
    Command = ""

    if DefaultPlayer == 0:
        Command = "/usr/bin/xdg-open "+VideoFile+" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 1: # MPlayer
        Command = "/usr/bin/mplayer "+VideoFile+" -sub "+Subtitles+" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 2: # SMPlayer
        Command = "/usr/bin/smplayer "+VideoFile+" -sub "+Subtitles+" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 3: # VLC
        Command = "/usr/bin/vlc "+VideoFile+" --sub-file "+Subtitles+" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 4: # Totem
        Command = "/usr/bin/totem "+VideoFile+" > /dev/null 2> /dev/null &"

    if not Command == "":
        print("Executing: "+Command)
        os.system(Command)
