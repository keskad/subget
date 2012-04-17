import subgetcore, gtk, sys, time, sys, traceback, os
from StringIO import StringIO

####
PluginInfo = {'Requirements' : { 'OS' : 'All'}, 'API': 2, 'Authors': 'webnull', 'domain': '', 'type': 'extension', 'isPlugin': False}

class PluginMain(subgetcore.SubgetPlugin):
    """ Easy management of video players list, with data validation.
        Can be used inside or outside of subget, in plugins """

    generatedList = dict()
    indexList = list()
    Subget = None
    default = 0

    def _pluginInit(self):
        """ Load all default video players, also parses config """

        # hook to download function
        self.Subget.Hooking.connectHook("onSubtitlesDownload", self._onSubtitlesDownload)
        self.Subget.Hooking.connectHook("onGTKWindowOpen", self._onGTKLoopEnd)
        self.Subget.Hooking.connectHook("prefsIntegrationBox", self._prefsIntegrationBox)

        if "window" in dir(self.Subget):
            self._onGTKLoopEnd(False)

        # sets default player
        default = self.Subget.configGetKey("videoplayers", "default")

        if not default == False:
            self.default = default


        # default built-in video players
        self.add(self.Subget._("System's default"), "/usr/bin/xdg-open", "%filename%")
        self.add("MPlayer", "/usr/bin/mplayer", "\"%filename%\" -sub \"%subtitles%\" > /dev/null 2> /dev/null &")
        self.add("MPlayer2", "/usr/bin/mplayer2", "\"%filename%\" -sub \"%subtitles%\" > /dev/null 2> /dev/null &")
        self.add("SMPlayer", "/usr/bin/smplayer", "\"%filename%\" -sub \"%subtitles%\" > /dev/null 2> /dev/null &")
        self.add("SMPlayer2", "/usr/bin/smplayer2", "\"%filename%\" -sub \"%subtitles%\" > /dev/null 2> /dev/null &") # + Added support for SMPlayer2
        self.add("VLC", "/usr/bin/vlc", "\"%filename%\" --sub-file \"%subtitles%\" > /dev/null 2> /dev/null &")
        self.add("Totem", "/usr/bin/totem", "\"%filename%\" > /dev/null 2> /dev/null &")
        self.add("KMPlayer", "/usr/bin/kmplayer", "\"%filename%\" > /dev/null 2> /dev/null &")
        self.add("GMplayer", "/usr/bin/gmplayer", "\"%filename%\" -sub \"%subtitles%\" > /dev/null 2> /dev/null &")
        self.add("gnome-mplayer", "/usr/bin/gnome-mplayer", "\"%filename%\" --subtitle=\"%subtitles%\" > /dev/null 2> /dev/null &")
        self.add("Rhythmbox", "/usr/bin/rhythmbox", "\"%filename%\" > /dev/null 2> /dev/null &")
        self.add("umplayer", "/usr/bin/umplayer", "\"%filename%\" -sub \"%subtitles%\" > /dev/null 2> /dev/null &")

        if os.name == "nt":
            self.add("Winamp", "c:\\Program\ Files\\Winamp\\Winamp.exe", "\"%filename%\"")
            self.add(str(self.Subget._("System's default")), "start", "%filename%")

        # video players excluded from list
        disabledPlayers = self.Subget.configGetKey("videoplayers", "disabled")

        if not disabledPlayers == False:
            x = disabledPlayers.split(",")

            for item in x:
                self.delete(item)

        # list of video players added in configuration file
        Config = self.Subget.configGetSection("videoplayers")
                

        if Config != False:
            for item in Config:
                if item == "default" or item == "disabled":
                    continue

                s1 = Config[item].split(" ")

                if len(s1) > 0:
                    self.add(item, s1[0], Config[item].replace(s1[0]+" ", ""))

    def _onGTKLoopEnd(self, Data):
        """ Start when GTK window appears """

        # Videoplayer checkbutton
        self.VPButton = gtk.CheckButton(self.Subget._("Start video player"))

        if not self.Subget.configGetKey('afterdownload', 'playmovie') == False: # TRUE, playmovie active
            self.VPButton.set_active(1)
        else:
            self.VPButton.set_active(0)
            self.VPButton.hide()

        self.Subget.window.hbox.pack_end(self.VPButton, False, False, 10)
        self.Subget.window.show_all()

    def _prefsIntegrationBox(self, Data):
        # Video player integration
        Label2 = gtk.Label(self.Subget._("Video Player settings"))
        Label2.set_alignment (0, 0)

        SelectPlayer = gtk.combo_box_new_text()

        playersList = self.listAll()

        for item in playersList:
            SelectPlayer.append_text(item["name"])

        SelectPlayer.connect("changed", self.defaultPlayerSelection)

        DefaultPlayer = self.Subget.configGetKey('afterdownload', 'defaultplayer')

        if DefaultPlayer == False:
            SelectPlayer.set_active(0)
        else:
            try:
                SelectPlayer.set_active(int(playersList.index(self.generatedList[DefaultPlayer])))
            except Exception as e:
                pass

        EnableVideoPlayer = gtk.CheckButton(self.Subget._("Start automaticaly when program runs"))
        EnableVideoPlayer.connect("toggled", self.gtkPreferencesIntegrationPlayMovie)

        if not self.Subget.configGetKey('afterdownload', 'playmovie') == False:
            EnableVideoPlayer.set_active(1)

        hbox_v = gtk.HBox(False, 2)
        hbox_v.pack_start(SelectPlayer, False, False, 0)
        Data.pack_start(Label2, False, False, 5)
        Data.pack_start(EnableVideoPlayer, False, False, 2)
        Data.pack_start(hbox_v, False, False, 2)
        return Data


    def _pluginDestroy(self):
        """ Unload plugin """

        self.Subget.Hooking.removeHook("onSubtitlesDownload", self._onSubtitlesDownload)
        self.Subget.Hooking.removeHook("onGTKWindowOpen", self._onGTKLoopEnd)
        self.Subget.Hooking.removeHook("prefsIntegrationBox", self._prefsIntegrationBox)

        self.Subget.window.hbox.remove(self.VPButton)
        self.Subget.window.show_all()

        del self.VPButton
        del self


    def add(self, name, executable, params):
        """ Add or modify existing application on list.

            Args:
              name - name of application, eg. smplayer
              executable - path to executable, eg. /usr/bin/smplayer, /usr/local/bin/vlc or just mplayer
              params - additional params to load subtitles, eg. -sub %subtitles%

            Variables to use in params:
              %subtitles% - this string will be replaced to subtitles path
              %filename% - full path to video file
        """

        if os.path.isfile(executable):
            pass # all is valid
        else:
            nExecutable = str(self.Subget.getFile(["/usr/bin/"+executable, executable.replace("/usr/bin/", "/usr/local/bin"), executable]))
            if os.path.isfile(nExecutable):
                executable = nExecutable
            elif executable == "start" and os.name == "nt":
                pass
            else:
                return False # cannot add to list - video player executable does not exists

        self.generatedList[name] = dict()
        self.generatedList[name]['name'] = name
        self.generatedList[name]['exec'] = executable
        self.generatedList[name]['params'] = params
        self.indexList.append(name)

        return True

    def delete(self, name):
        """ Removes specified application from list

            Args:
              name - appliaction name specified previously by VideoPlayers.add() function in first argument (name) eg. vlc
        """

        if name in self.generatedList:
            del self.indexList[self.indexList.index(name)]
            del self.generatedList[name]
            return True

        return False

    def getNameByIndex(self, i):
        """ Search for player name using only index number

            Args:
              i - index of application

        """

        if i in self.indexList:
            return self.indexList[i]

    def getShellCommand(self, videofile, subtitles, player, execute=False):
        """ Returns a shell command to execute 

            Args:
              videofile - full path to video file
              subtitles - absolute path to subtitles text file
              player - name of video player to use
              execute - execute command using os.system(), optional, disabled by default, set as True to enable
        """

        # if int specified
        if type(player).__name__ == "int":
            player = self.nameByIndex(player)

        if not player in self.generatedList:
            return False

        shellString = self.generatedList[player]["exec"]+" "+self.generatedList[player]["params"].replace("%subtitles%", str(subtitles)).replace("%filename%", str(videofile))

        if execute == True:
            self.Subget.Logging.output("Executing: "+shellString, "debug", False)
            os.system(shellString)
            return True

        return shellString

    def listAll(self):
        """ Returns ordered list of applications """

        newList = list()

        for i in self.indexList:
            newList.append(self.generatedList[i])

        return newList

    def _onSubtitlesDownload(self, data):
        if self.VPButton.get_active() == True:
            self.getShellCommand(data[2], data[1], str(self.Subget.configGetKey('afterdownload', 'defaultplayer')), True)

    # MOVED
    def gtkPreferencesIntegrationPlayMovie(self, Widget):
        Value = Widget.get_active()
        self.Subget.Config['afterdownload']['playmovie'] = Value

        if Value == True:
            self.VPButton.set_active(1)
        else:
            self.VPButton.set_active(0)

    def defaultPlayerSelection(self, widget):
        """ Select default external video playing program """
        self.Subget.Config['afterdownload']['defaultplayer'] = widget.get_active_text()


