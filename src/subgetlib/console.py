import subgetcore, gtk, sys, time, sys, traceback, os
from StringIO import StringIO

####
PluginInfo = {'Requirements' : { 'OS' : 'All'}, 'API': 2, 'Authors': 'webnull', 'domain': '', 'type': 'extension', 'isPlugin': False}

class PluginMain(subgetcore.SubgetPlugin):
    consoleState = False # Closed
    consoleWindow = None
    commands = None
    envCache = dict()
    contextMenu = list()

    def _pluginInit(self):
        """ Initialize plugin """

        self.Subget.Hooking.connectHook("onGTKWindowOpen", self._onGTKLoopEnd)
        self.Subget.Hooking.connectHook("onLogChange", self._updateConsole)
        self.Subget.Hooking.connectHook("onPreferencesOpen", self._settingsTab)

        # Add option to context menu in plugins list
        self.contextMenuAdd(self.Subget._("Show console"), self.openConsole, "")

        if "window" in dir(self.Subget):
            self._onGTKLoopEnd(False)

        self.commands = Commands(self)

    def _onGTKLoopEnd(self, Data):
        """ Start when GTK window appears """

        iconFile = self.Subget.getPath("/usr/share/subget/icons/terminal.png")

        try:
            self.consolePosition = self.Subget.interfaceAddIcon(self.Subget._("Console"), self.openConsole, "toolsMenu", "console", iconFile, '<Control>L', True, True, False)
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

    def sendCommand(self, x):
        """ Executes python code from GUI - just a python shell inside of a console 
            Captures stdout and stderr.
        """

        cmd = self.consoleWindow.gText.get_text()
        self.consoleWindow.gText.set_text("")

        if cmd == "" or cmd == " ":
            return False

        cmdLine = cmd.split(" ")

        self.Subget.Logging.output("> "+cmd, "debug", False, True, True)

        # create string buffer to capture stdout
        buffer = StringIO()
        sys.stdout = buffer

        if cmdLine[0] in dir(self.commands):
            self.commands.send(cmdLine)
            return False

        # Environment
        for envVar in self.envCache:
            try:
                exec(str(envVar)+" = self.envCache[envVar]")
                #print str(envVar)+" = self.envCache[envVar]"
            except Exception:
                pass

        subget = self.Subget
        _ = self.Subget._
        logging = self.Subget.Logging

        #for moduleName in self.commands.imported:
        #    exec(moduleName+" = self.commands.imported[moduleName]")

        try:
            exec(cmd)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)

        #self.Subget.Logging.output(bufferErr.getvalue(), "debug", False, True, True)
        self.Subget.Logging.output(buffer.getvalue(), "debug", False, True, True)

        # restore original stdout
        sys.stdout = sys.__stdout__

        env = dir()

        for envVar in env:
            if envVar == "self" or envVar == "buffer" or envVar == "logging" or envVar == "cmd" or envVar == "cmdline":
                continue

            value = eval(envVar)
            self.envCache[envVar] = value

    def gscrollMove(self, x, y):
        """ Moves scroll to bottom if console window was updated """

        vadjustment = self.consoleWindow.gscroll.get_vadjustment()
        vadjustment.value = (vadjustment.upper - vadjustment.page_size)


    def openConsole(self, x='', y=''):
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
        self.consoleWindow.gscroll.connect("size-allocate", self.gscrollMove)
        self.consoleWindow.gframe.add(self.consoleWindow.gscroll)

        # CONTAINERS
        self.consoleWindow.hbox = gtk.HBox(False, 1000)
        self.consoleWindow.hbox.pack_start(self.consoleWindow.gframe, True, True, 0)

        self.consoleWindow.vbox = gtk.VBox(False, 0)
        self.consoleWindow.vbox.set_border_width(0)
        self.consoleWindow.vbox.pack_start(self.consoleWindow.hbox, True, True, 0)

        # TEXT-AREA
        self.consoleWindow.gText = gtk.Entry()
        self.consoleWindow.gText.set_max_length(4086)
        #self.consoleWindow.gText.set_size_request(20, 20)
        self.consoleWindow.button = gtk.Button(self.Subget._("Send"))

        # Down part (textbox and button)
        self.consoleWindow.texthBox = gtk.HBox(False, 10)
        self.consoleWindow.texthBox.pack_start(self.consoleWindow.gText, True, True, 0)
        self.consoleWindow.texthBox.pack_start(self.consoleWindow.button, False, False, 0)
        self.consoleWindow.gText.connect("activate", self.sendCommand)
        self.consoleWindow.button.connect("pressed", self.sendCommand)

        # PUT ALL TOGETHER AND SHOW
        self.consoleWindow.vbox.pack_start(self.consoleWindow.texthBox, False, False, 0)
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

        self.contextMenu = list()
        self.Subget.Hooking.removeHook("onGTKWindowOpen", self._onGTKLoopEnd)
        self.Subget.Hooking.removeHook("onLogChange", self._updateConsole)
        self.Subget.Hooking.removeHook("onPreferencesOpen", self._settingsTab)
        menu, toolbar =  self.consolePosition
        self.Subget.window.Menubar.remove(menu)
        self.Subget.window.toolbar.remove(toolbar)
        self.Subget.window.Menubar.elementsArray['toolsMenu'].remove(menu)
        self.Subget.window.show_all()
        self.consoleWindow.destroy()
        del self.consoleWindow
        del self

class Commands:
    console = None
    #imported = dict()
    nav = os.path.expanduser("~")

    def __init__(self, console):
        self.console = console

    def output(self, message):
        self.console.Subget.Logging.output(message, "debug", False, True, True)

    def send(self, cmdLine):
        if cmdLine[0] == "send" or cmdLine[0] == "output" or cmdLine[0] == "__init__":
            return False

        if cmdLine[0] in dir(self):
            cmd = cmdLine[0]
            cmdLine.remove(cmd)

            exec("self."+cmd+"(cmdLine)")

    def help(self, params):
        self.output("List: subget, _, logging, subgetcore, load\nImporting libraries: load subgetlib (not accepting commas)")

    def clear(self, params):
        self.output("\n\n\n\n\n\n\n\n\n\n")

    #def load(self, params):
    #    if len(params) == 0:
    #        self.output("Usage: load [module1] [module2]\nExample: load subgetlib subgetcore")

    #    for param in params:
    #        name = param

    #        try:
    #            objParam = None
    #            exec("import "+param+" as objParam")
    #            self.imported[name] = objParam

    #        except Exception as e:
    #            self.output("Cannot import "+param+", exception: "+str(e))
    #            traceback.print_exc(file=sys.stdout)

    def cd(self, location):
        if len(location) == 0:
            self.nav = os.path.expanduser("~")
        if os.path.isdir(location[0]):
            self.nav = location[0]
        elif os.path.isdir(self.nav+"/"+location[0]):
            self.nav = self.nav+"/"+location[0]

    def pwd(self, args):
        self.output(self.nav)

    def ls(self, args):
        self.output(str(os.listdir(self.nav)))



