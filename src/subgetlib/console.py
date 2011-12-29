import subgetcore, gtk, sys, time

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

        iconFile = self.Subget.getPath("/usr/share/subget/icons/terminal.png")

        try:
            self.Subget.interfaceAddIcon(self.Subget._("Console"), self.openConsole, "toolsMenu", "console", iconFile, '<Control>L', True, True, False)
        except Exception:
            self.consolePosition = gtk.ImageMenuItem(self.Subget._("Console"))
            self.consolePosition.connect("activate", self.openConsole)

            try:
                image = gtk.Image()
                image.set_from_file(iconFile)
                self.consolePosition.set_image(image)
            except Exception as e:
                print(e)
                True

            if self.Subget.configGetKey("console", "open_at_startup") == "True":
                self.openConsole(False)

            self.Subget.window.Menubar.elementsArray['toolsMenu'].append(self.consolePosition)
            self.Subget.window.show_all()


    def errorLevel_Scale(self, x):
        newLevel = (int(x.value)-2)
        self.Subget.configSetKey("logging", "level", str(newLevel))
        self.Subget.Logging.loggingLevel = newLevel

    def _settingsTab(self, Data):
        Startup = gtk.CheckButton(self.Subget._("Show console on Subget startup"))
        Startup.connect("pressed", self.Subget.configSetButton, 'console', 'open_at_startup', Startup, True)

        if not self.Subget.configGetKey("console", "open_at_startup") == False:
            Startup.set_active(1)

        confSize = gtk.CheckButton(self.Subget._("Remeber window size"))
        confSize.connect("pressed", self.Subget.configSetButton, 'console', 'remember_size', confSize, True)

        if not self.Subget.configGetKey("console", "remember_size") == False:
            confSize.set_active(1)

        confPosition = gtk.CheckButton(self.Subget._("Remember window position"))
        confPosition.connect("pressed", self.Subget.configSetButton, 'console', 'remember_position', confPosition, True)

        if not self.Subget.configGetKey("console", "remember_position") == False:
            confPosition.set_active(1)


        Label2 = gtk.Label(self.Subget._("Errorlevel outside of internal console:"))
        adj = gtk.Adjustment(1.0, 1.0, 5.0, 1.0, 1.0, 1.0)

        adj.connect("value_changed", self.errorLevel_Scale)
        scale = gtk.HScale(adj)
        scale.set_digits(0)
        scale.set_size_request(230, 40)
        scaleValue = int(self.Subget.configGetKey('logging', 'level'))+2


        if not scaleValue == False and scaleValue > 0 and scaleValue <= 30:
            adj.set_value(scaleValue)

        Vbox = gtk.VBox(False, 0)
        Hbox = gtk.HBox(False, 0)
        Vbox.pack_start(Startup, False, False, 2)
        Vbox.pack_start(confSize, False, False, 2)
        Vbox.pack_start(confPosition, False, False, 2)
        Vbox.pack_start(Label2, False, False, 2)
        Vbox.pack_start(scale, False, False, 2)
        Hbox.pack_start(Vbox, False, False, 8)

        self.Subget.createTab(self.Subget.winPreferences.notebook, self.Subget._("Console"), Hbox)
        self.Subget.winPreferences.show_all()
            

    def _updateConsole(self, text):
        """ Dynamic update console event """

        if self.consoleState == True:
            self.consoleWindow.textarea.set_text(text)


    def openConsole(self, x):
        """ Open the console window """

        if self.consoleState == True:
            return False

        self.consoleWindow = gtk.Window()
        self.consoleWindow.set_resizable(True)
        self.consoleWindow.set_title(self.Subget._("Console")+" - Subget")
        self.consoleWindow.set_size_request(450, 240)

        # TEXTAREA INSIDE OF FRAME
        self.consoleWindow.textarea = gtk.Label(self.Subget.Logging.session)
        self.consoleWindow.textarea.set_selectable(True)
        self.consoleWindow.textarea.set_alignment(0, 0)

        self.consoleState = True

        if not self.Subget.configGetKey("console", "remember_size") == False:
            try:
                x = str(self.Subget.configGetKey("console", "sizex"))
                y = str(self.Subget.configGetKey("console", "sizey"))

                if x != "False" and y != "False":
                    x = int(x)
                    y = int(y)
                    self.Subget.Logging.output("Restoring console size: "+str(x)+"x"+str(y), "debug", False)
                    self.consoleWindow.set_size_request(x, y)
                    self.consoleWindow.set_resizable(True)

            except Exception as e:
                print(e)

        try:
            self.consoleWindow.set_icon_from_file(self.Subget.getPath("/usr/share/subget/icons/terminal.png"))
        except Exception:
            pass

        # FRAME
        self.consoleWindow.gframe = gtk.Frame("")
        self.consoleWindow.gframe.set_border_width(0) 
        #self.consoleWindow.gframe.set_size_request(100, 240)
        self.consoleWindow.gframe.set_shadow_type(gtk.SHADOW_ETCHED_OUT)

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
        self.consoleWindow.set_size_request(450, 240)

        if not self.Subget.configGetKey("console", "remember_position") == False:
            try:
                x = str(self.Subget.configGetKey("console", "posx"))
                y = str(self.Subget.configGetKey("console", "posy"))

                if x != "False" and y != "False":
                    x = int(x)
                    y = int(y)
                    self.Subget.Logging.output("Restoring console at "+str(x)+"x"+str(y), "debug", False)
                    self.consoleWindow.set_uposition(x, y)

            except Exception as e:
                print(e)

        self.consoleWindow.connect("delete_event", self.windowDeleteEvent)




    def windowDeleteEvent(self, widget, event, data=None):
        self.consoleState = False

        if not self.Subget.configGetKey("console", "remember_position") == False:
            pos = self.consoleWindow.get_position()
            self.Subget.configSetKey("console", "posx", pos[0])
            self.Subget.configSetKey("console", "posy", pos[1])
            self.Subget.Logging.output("Saving console position at "+str(pos[0])+"x"+str(pos[1]), "debug", False)

        if not self.Subget.configGetKey("console", "remember_size") == False:
            size = self.consoleWindow.get_size()
            self.Subget.configSetKey("console", "sizex", size[0])
            self.Subget.configSetKey("console", "sizey", size[1])
            self.Subget.Logging.output("Saving console size: "+str(size[0])+"x"+str(size[1]), "debug", False)

        if not self.Subget.configGetKey("console", "remember_size") == False or not self.Subget.configGetKey("console", "remember_size") == False:
            self.Subget.saveConfiguration()

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

