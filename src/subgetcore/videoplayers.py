""" Integration with Video Players """

import os

def Spawn(Subget, VideoFile, Subtitles):
    DefaultPlayer = int(Subget.Config['afterdownload']['defaultplayer'])
    Command = ""

    if DefaultPlayer == 0:
        Command = "/usr/bin/xdg-open \""+VideoFile+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 1: # MPlayer
        Command = "/usr/bin/mplayer \""+VideoFile+"\" -sub \""+Subtitles+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 2: # SMPlayer
        Command = "/usr/bin/smplayer \""+VideoFile+"\" -sub \""+Subtitles+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 3: # VLC
        Command = "/usr/bin/vlc \""+VideoFile+"\" --sub-file \""+Subtitles+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 4: # Totem
        Command = "/usr/bin/totem \""+VideoFile+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 5: # MPlayer2 (fork of Mplayer)
        Command = "/usr/bin/mplayer2 \""+VideoFile+"\" -sub \""+Subtitles+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 6: # KMPlayer (Konqueror plugin)
        Command = "/usr/bin/kmplayer \""+VideoFile+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 7: # GMPlayer (mplayer-gui)
        Command = "/usr/bin/gmplayer \""+VideoFile+"\" -sub \""+Subtitles+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 8: # GNOME Mplayer
        Command = "/usr/bin/gnome-mplayer \""+VideoFile+"\" --subtitle=\""+Subtitles+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 9: # Rhythmbox
        Command = "/usr/bin/rhythmbox \""+VideoFile+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 10: # Rhythmbox
        Command = "/usr/bin/umplayer \""+VideoFile+"\" -sub \""+Subtitles+"\" > /dev/null 2> /dev/null &"

    if not Command == "":
        print("Executing: "+Command)
        os.system(Command)
