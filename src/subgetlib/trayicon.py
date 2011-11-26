import subgetcore, gtk, sys

####
PluginInfo = {'Requirements' : { 'OS' : 'All'}, 'API': 2, 'Authors': 'webnull', 'domain': '', 'type': 'extension', 'isPlugin': False}

class PluginMain(subgetcore.SubgetPlugin):
    iconInitialized = False
    lastWindowPosition = None # Remember window's last position

    def _onGTKLoopEnd(self, Data):
        """ Start when GTK window appears """

        if len(sys.argv) == 1:
            # hide window on program startup?
            hide_at_startup = self.Subget.configGetKey('trayicon', 'hide_at_startup')

            if hide_at_startup == True or hide_at_startup == "True":
                self.Subget.window.hide()

        self.initializeIcon()

    def initializeIcon(self):
        """ Create tray icon """

        self.iconInitialized = True
        self.statusicon = gtk.StatusIcon()
        self.statusicon.set_from_file(self.Subget.subgetOSPath+"/usr/share/subget/icons/Subget-logo.png")
        self.statusicon.connect('activate', self.status_clicked )
        self.statusicon.set_tooltip("Subget")

    def status_clicked(self,status):
        """ Show/Hide a window """

        visible = self.Subget.window.get_visible()

        if visible == False:
            self.Subget.window.set_visible(True)

            #### Restore last window position
            remember_window_position = self.Subget.configGetKey('trayicon', 'remember_window_position')

            if remember_window_position == True or remember_window_position == "True":
                if self.lastWindowPosition != None:
                    self.Subget.window.set_uposition(self.lastWindowPosition[0], self.lastWindowPosition[1])
        else:
            self.lastWindowPosition = self.Subget.window.get_position()
            self.Subget.window.set_visible(False)
        
       
            

    def _pluginInit(self):
        """ Initialize plugin """

        self.Subget.Hooking.connectHook("onGTKWindowOpen", self._onGTKLoopEnd)

        if "window" in dir(self.Subget):
            self.initializeIcon()

    def _pluginDestroy(self):
        """ Unload plugin """

        self.iconInitialized = False
        del self.statusicon
        del self
