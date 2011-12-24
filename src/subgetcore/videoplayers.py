""" Integration with Video Players """

import os

def Spawn(Subget, VideoFile, Subtitles):
    DefaultPlayer = int(Subget.configGetKey('afterdownload', 'defaultplayer'))
    Command = ""

    if DefaultPlayer == 1: # MPlayer
        Command = str(Subget.getFile("/usr/bin/mplayer", "/usr/local/bin/mplayer"))+" \""+VideoFile+"\" -sub \""+Subtitles+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 2: # SMPlayer
        Command = str(Subget.getFile("/usr/bin/smplayer", "/usr/local/bin/smplayer"))+" \""+VideoFile+"\" -sub \""+Subtitles+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 3: # VLC
        Command = str(Subget.getFile("/usr/bin/vlc", "/usr/local/bin/vlc"))+" \""+VideoFile+"\" --sub-file \""+Subtitles+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 4: # Totem
        Command = str(Subget.getFile("/usr/bin/totem", "/usr/local/bin/totem"))+" \""+VideoFile+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 5: # MPlayer2 (fork of Mplayer)
        Command = str(Subget.getFile("/usr/bin/mplayer2", "/usr/local/bin/mplayer2"))+" \""+VideoFile+"\" -sub \""+Subtitles+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 6: # KMPlayer (Konqueror plugin)
        Command = str(Subget.getFile("/usr/bin/kmplayer", "/usr/local/bin/kmplayer"))+" \""+VideoFile+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 7: # GMPlayer (mplayer-gui)
        Command = str(Subget.getFile("/usr/bin/gmplayer", "/usr/local/bin/gmplayer"))+" \""+VideoFile+"\" -sub \""+Subtitles+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 8: # GNOME Mplayer
        Command = str(Subget.getFile("/usr/bin/gnome-mplayer", "/usr/local/bin/gnome-mplayer"))+" \""+VideoFile+"\" --subtitle=\""+Subtitles+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 9: # Rhythmbox
        Command = str(Subget.getFile("/usr/bin/rhythmbox", "/usr/local/bin/rhythmbox"))+" \""+VideoFile+"\" > /dev/null 2> /dev/null &"
    elif DefaultPlayer == 10: # UMPlayer
        Command = str(Subget.getFile("/usr/bin/umplayer", "/usr/local/bin/umplayer"))+" \""+VideoFile+"\" -sub \""+Subtitles+"\" > /dev/null 2> /dev/null &"
    else:
        Command = str(Subget.getFile("/usr/bin/xdg-open", "/usr/local/bin/xdg-open"))+" \""+VideoFile+"\" > /dev/null 2> /dev/null &"

    if not Command == "":
        Subget.Logging.output("Executing: "+Command, "debug", False)
        os.system(Command)
