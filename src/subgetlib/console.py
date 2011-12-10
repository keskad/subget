import subgetcore, gtk, sys

####
PluginInfo = {'Requirements' : { 'OS' : 'All'}, 'API': 2, 'Authors': 'webnull', 'domain': '', 'type': 'extension', 'isPlugin': False}

class PluginMain(subgetcore.SubgetPlugin):
    consoleState = False # Closed
    consoleWindow = None

    def _pluginInit(self):
        """ Initialize plugin """

        self.Subget.Hooking.connectHook("onGTKWindowOpen", self._onGTKLoopEnd)
        self.Subget.Hooking.connectHook("onLogChange", self._updateConsole)
        self.Subget.Hooking.connectHook("onPreferencesOpen", self._settingsTab)

        if "window" in dir(self.Subget):
            self._onGTKLoopEnd(False)



    def _onGTKLoopEnd(self, Data):
        """ Start when GTK window appears """

        self.consolePosition = gtk.ImageMenuItem(self.Subget._("Console"))
        self.consolePosition.connect("activate", self.openConsole)

        try:
            image = gtk.Image()
            image.set_from_file(self.Subget.getPath("/usr/share/subget/icons/terminal.png"))
            self.consolePosition.set_image(image)
        except Exception as e:
            print(e)
            True

        if self.Subget.configGetKey("console", "open_at_startup") == "True":
            self.openConsole(False)

        self.Subget.window.Menubar.elementsArray['toolsMenu'].append(self.consolePosition)
        self.Subget.window.show_all()

    def _settingsTab(self, Data):
        Startup = gtk.CheckButton(self.Subget._("Show console on Subget startup"))
        Startup.connect("pressed", self.Subget.configSetButton, 'console', 'open_at_startup', Startup, True)

        if not self.Subget.configGetKey("console", "open_at_startup") == False:
            Startup.set_active(1)

        Vbox = gtk.VBox(False, 0)
        Hbox = gtk.HBox(False, 0)
        Hbox.pack_start(Startup, False, False, 10)
        Vbox.pack_start(Hbox, False, False, 8)

        self.Subget.createTab(self.Subget.winPreferences.notebook, self.Subget._("Console"), Vbox)
        self.Subget.winPreferences.show_all()
            

    def _updateConsole(self, text):
        """ Dynamic update console event """

        if self.consoleState == True:
            self.consoleWindow.textarea.set_text(text)



    def openConsole(self, x):
        """ Open the console window """

        if self.consoleState == True:
            return False

        self.consoleState = True

        self.consoleWindow = gtk.Window()
        self.consoleWindow.set_resizable(True)
        self.consoleWindow.set_title(self.Subget._("Console")+" - Subget")
        self.consoleWindow.set_size_request(450, 240)

        try:
            self.consoleWindow.set_icon_from_file(self.Subget.getPath("/usr/share/subget/icons/terminal.png"))
        except Exception:
            pass

        # FRAME
        self.consoleWindow.gframe = gtk.Frame("")
        self.consoleWindow.gframe.set_border_width(0) 
        #self.consoleWindow.gframe.set_size_request(100, 240)
        self.consoleWindow.gframe.set_shadow_type(gtk.SHADOW_ETCHED_OUT)

        # TEXTAREA INSIDE OF FRAME
        self.consoleWindow.textarea = gtk.Label(self.Subget.Logging.session)
        self.consoleWindow.textarea.set_alignment (0, 0)

        # SCROLL
        self.consoleWindow.gscroll = gtk.ScrolledWindow()
        self.consoleWindow.gscroll.set_border_width(0)
        self.consoleWindow.gscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.consoleWindow.gscroll.add_with_viewport(self.consoleWindow.textarea)
        self.consoleWindow.gframe.add(self.consoleWindow.gscroll)

        # CONTAINERS
        self.consoleWindow.hbox = gtk.HBox(False, 1000)
        self.consoleWindow.hbox.pack_start(self.consoleWindow.gframe, True, True, 0)

        self.consoleWindow.vbox = gtk.VBox(False, 0)
        self.consoleWindow.vbox.set_border_width(0)
        self.consoleWindow.vbox.pack_start(self.consoleWindow.hbox, True, True, 0)

        # PUT ALL TOGETHER AND SHOW
        self.consoleWindow.add(self.consoleWindow.vbox)
        self.consoleWindow.show_all()
        self.consoleWindow.connect("delete_event", self.windowDeleteEvent)





    def windowDeleteEvent(self, widget, event, data=None):
        self.consoleState = False
        del self.consoleWindow
        self.consoleWindow = None
        return False



    def _pluginDestroy(self):
        """ Unload plugin """
        self.Subget.Hooking.removeHook("onGTKWindowOpen", self._onGTKLoopEnd)
        self.Subget.Hooking.removeHook("onLogChange", self._updateConsole)
        self.Subget.Hooking.removeHook("onPreferencesOpen", self._settingsTab)

        self.Subget.window.Menubar.elementsArray['toolsMenu'].remove(self.consolePosition)
        self.consoleWindow.destroy()
        del self.consoleWindow
        del self

