import subgetcore, gtk, sys

####
PluginInfo = {'Requirements' : { 'OS' : 'All'}, 'API': 2, 'Authors': 'webnull', 'domain': '', 'type': 'extension', 'isPlugin': False}

class PluginMain(subgetcore.SubgetPlugin):
    iconInitialized = False

    def _onGTKLoopEnd(self, Data):
        """ Start when GTK window appears """

        if len(sys.argv) == 1:
            # hide window on program startup?
            if self.Subget.configGetKey('startup', 'hide_at_startup') == True:
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
        else:
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
