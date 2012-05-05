#-*- coding: utf-8 -*-
import subgetcore, sys, os, time
from threading import Thread

####
PluginInfo = {'Requirements' : { 'OS' : 'Unix, Linux, Windows'}, 'API': 2, 'Authors': 'webnull', 'domain': '', 'type': 'extension', 'isPlugin': False}

if os.name == "posix":
    try:
        import dbus, dbus.service, dbus.glib
    except ImportError:
        #!!!: when dbus will not be installed all code under this line will crash
        # Response: it should crash, Subget will automatically disable the plugin, but there is no error handling yet i should implmement any
        # this plugin wont be installed by Linux package manager if dbus were not installed
        pass

    class SubgetService(dbus.service.Object):
        subget = None

        def __init__(self):
            bus_name = dbus.service.BusName('org.freedesktop.subget', bus=dbus.SessionBus())
            super(SubgetService, self).__init__(bus_name, '/org/freedesktop/subget')

        @dbus.service.method('org.freedesktop.subget')
        def ping(self):
            """ Check if Subget is already running """

            return True

        @dbus.service.method('org.freedesktop.subget')
        def openSearchMenu(self):
            """ Opens search dialog """

            if self.subget is not None:
                return self.subget.gtkSearchMenu(None) 

        @dbus.service.method('org.freedesktop.subget')
        def openPluginsMenu(self):
            """ Opens plugin menu """

            if self.subget is not None:
                return self.subget.gtkPluginMenu(None)

        @dbus.service.method('org.freedesktop.subget')
        def openSelectVideoDialog(self):
            """ Opens Video Selection dialog """

            if self.subget is not None:
                return self.subget.gtkSelectVideo(None)

        @dbus.service.method('org.freedesktop.subget')
        def openAboutDialog(self):
            """ Opens About dialog """

            if self.subget is not None:
                return self.subget.gtkAboutMenu(None)

        @dbus.service.method('org.freedesktop.subget')
        def clearList(self):
            """ Clean up the list """
            if self.subget is not None:
                return self.subget.cleanUpResults()

        @dbus.service.method('org.freedesktop.subget')
        def addLinks(self, Links, Wait=False):
            """ Add links seperated by new line.
                Returns nothing when not waiting, and other values when waiting for function finish working.
                On errors returns false.
                Default - Don't wait.
            """
            if self.subget is None:
                return False

            if not str(type(Links).__name__) == "String":
                return False

            Links = Links.split("\n")
            self.subget.files = Links

            if Wait:
                return self.subget.TreeViewUpdate()
            else:
                self.subget.TreeViewUpdate()

else:
    import win32com.server.register, pythoncom, win32com.client

    class SubgetService:
        _public_methods_ = [ 'ping', 'openSearchMenu', 'openPluginsMenu', 'openSelectVideoDialog', 'openAboutDialog', 'clearList', 'addLinks', 'setSubgetObject' ]
        _reg_progid_ = "Subget"
        _reg_clsid_ = pythoncom.CreateGuid()
        subget = None

        def setSubgetObject(self, Subget):
            print Subget.gtkSearchMenu
            self.subget = Subget
    
        def ping(self):
            """ Check if Subget is already running """

            return True

        def openSearchMenu(self):
            """ Opens search dialog """

            if self.subget is not None:
                return self.subget.gtkSearchMenu(None) 

        def openPluginsMenu(self):
            """ Opens plugin menu """

            if self.subget is not None:
                return self.subget.gtkPluginMenu(None)

        def openSelectVideoDialog(self):
            """ Opens Video Selection dialog """

            if self.subget is not None:
                return self.subget.gtkSelectVideo(None)

        def openAboutDialog(self):
            """ Opens About dialog """

            if self.subget is not None:
                return self.subget.gtkAboutMenu(None)

        def clearList(self):
            """ Clean up the list """
            if self.subget is not None:
                return self.subget.cleanUpResults()

        def addLinks(self, Links, Wait=False):
            """ Add links seperated by new line.
                Returns nothing when not waiting, and other values when waiting for function finish working.
                On errors returns false.
                Default - Don't wait.
            """
            if self.subget is None:
                return False

            if not str(type(Links).__name__) == "String":
                return False

            Links = Links.split("\n")
            self.subget.files = Links

            if Wait:
                return self.subget.TreeViewUpdate()
            else:
                self.subget.TreeViewUpdate()

class PluginMain(subgetcore.SubgetPlugin):
    """ Instance manager, uses DBUS on Linux/BSD and other Unix systems, and COM on Windows """

    thread = None
    bus = None

    def _onInstanceCheck(self, Data):
        """# == Data {
        # 0 => consoleMode
        # 1 => args
        # 2 => action
        # """

        if os.name == "nt":
            self.Subget.Logging.output("Bus plugin disabled on Windows", "", False)
            return Data

        if os.name == "posix":
            check = self.checkDBUS()
        else:
            # trivial method to check if the COM server is online... crappy Windows API...
            self.thread = Thread(target=self.checkCOM)
            self.thread.setDaemon(False)
            self.thread.start()

            time.sleep(0.5)

            if self.bus is None:
                self.thread._Thread__stop()
                check = False
            else:
                check = True

        if check == True:
            if len(Data[1]) > 0:
                if os.name == "posix":
                    addLinks = self.bus.get_dbus_method('addLinks', 'org.freedesktop.subget')
                else: # Windows NT
                    addLinks = self.bus.addLinks


                addLinks(str.join('\n', Data[1]), False)
                self.Subget.Logging.output(self.Subget._("Added new files to existing list."), "", False)
            else:
                self.Subget.Logging.output(self.Subget._("Only one instance (graphical window) of Subget can be running at once by one user."), "", False) # only one instance of Subget can be running at once

            sys.exit(0)

        # server
        if Data[2] != "watch": # if not running watch with subtitles function
            self.Subget.Logging.output("Spawning server...", "error", True)

            if os.name == "nt":
                pythoncom.CoInitialize()
                win32com.server.register.UseCommandLine(SubgetService)
                self.bus = win32com.client.Dispatch("Subget")
                self.bus.setSubgetObject(self.Subget)
            else:
                self.bus = SubgetService()
                self.bus.subget = self.Subget

        return Data

    def _pluginInit(self):
        """ Initialize plugin """
        self.Subget.Hooking.connectHook("onInstanceCheck", self._onInstanceCheck)

    def _pluginDestroy(self):
        """ Unload plugin """
        self.Subget.Hooking.removeHook("onInstanceCheck", self._onInstanceCheck)
        del self

    def checkDBUS(self):
        try:
            bus = dbus.SessionBus()
            self.bus = bus.get_object('org.freedesktop.subget', '/org/freedesktop/subget')
            ping = self.bus.get_dbus_method('ping', 'org.freedesktop.subget')
        except Exception as e:
            return False

        return True


    def checkCOM(self):
        pythoncom.CoInitialize()
        self.bus = win32com.client.Dispatch("Subget")
