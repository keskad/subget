import subgetcore, gtk, sys

####
PluginInfo = {'Requirements' : { 'OS' : 'All'}, 'API': 2, 'Authors': 'webnull', 'domain': '', 'type': 'extension', 'isPlugin': False, 'Description': 'Put\'s icon in system tray'}

class PluginMain(subgetcore.SubgetPlugin):
    iconInitialized = False
    lastWindowPosition = None # Remember window's last position
    contextMenu = list()

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
        self.statusicon.connect('activate', self.status_clicked)
        self.statusicon.set_tooltip("Subget")
        self.statusicon.connect("popup-menu", self.right_click_event)


    def right_click_event(self, icon, button, time):
        """ Popup menu """
        self.menu = gtk.Menu()

        show = gtk.ImageMenuItem(gtk.STOCK_YES)
        if not self.Subget.window.get_visible():
            show.set_label(self.Subget._("Show main window"))
        else:
            show.set_label(self.Subget._("Hide main window"))

        show.connect("activate", self.status_clicked)
        self.menu.append(show)

        select = gtk.ImageMenuItem(gtk.STOCK_ADD)
        select.set_label(self.Subget._("Select file"))
        select.connect("activate", self.Subget.GTKDownloadSubtitles)
        self.menu.append(select)

        preferences = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        preferences.connect("activate", self.Subget.gtkPreferences)
        self.menu.append(preferences)

        about = gtk.ImageMenuItem(gtk.STOCK_INFO)
        about.set_label(self.Subget._("About"))
        about.connect("activate", self.Subget.gtkAboutMenu)
        self.menu.append(about)

        quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quit.connect("activate", gtk.main_quit)
        self.menu.append(quit)


        self.menu.show_all()
        self.menu.popup(None, None, None, 3, time)

    def status_clicked(self,status=''):
        """ Show/Hide a window """

        visible = self.Subget.window.get_visible()

        if not visible:
            self.Subget.window.set_visible(True)

            #### Restore last window position
            remember_window_position = self.Subget.configGetKey('trayicon', 'remember_window_position')

            if remember_window_position or remember_window_position == "True":
                if self.lastWindowPosition is not None:
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
