#-*- coding: utf-8 -*-
import subgetcore
import sys
import os
import time
import socket
import json
import asyncore
from threading import Thread

####
PluginInfo = {'Requirements' : { 'OS' : 'Unix, Linux, Windows'}, 'API': 2, 'Authors': 'webnull', 'domain': '', 'type': 'extension', 'isPlugin': False, 'Description': 'DBUS interface'}

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


# based on example from: http://docs.python.org/library/asyncore.html
class SocketInterface(asyncore.dispatcher_with_send):
    """ Very simple socket interface """

    app = None

    def ping(self, data=''):
        """ Check if Subget is already running """

        return True

    def openSearchMenu(self, data=''):
        """ Opens search dialog """

        return self.app.gtkSearchMenu(None) 

    def openPluginsMenu(self, data=''):
        """ Opens plugin menu """

        return self.app.gtkPluginMenu(None)

    def openSelectVideoDialog(self, data=''):
        """ Opens Video Selection dialog """

        return self.app.gtkSelectVideo(None)

    def openAboutDialog(self, data=''):
        """ Opens About dialog """

        return self.app.gtkAboutMenu(None)

    def clearList(self, data=''):
        """ Clean up the list """
        return self.app.cleanUpResults()

    def addLinks(self, Links):
        """ Add links seperated by new line.
            Returns nothing when not waiting, and other values when waiting for function finish working.
            On errors returns false.
            Default - Don't wait.
        """
        Links = Links.split("\n")
        self.app.files = Links

        return self.app.TreeViewUpdate()

    def __init__(self, socket, app, addr):
        asyncore.dispatcher_with_send.__init__(self)
        self.set_socket(socket)
        self.app = app
        self.addr = addr

    def handle_read(self):
        data = self.recv(8192)

        if data:
            if data == "ping":
                self.send("pong")
                return False

            try:
                text = json.loads(data)

                if text['function'] == "handle_read" or text['function'] == "__init__":
                    self.send("Function not avaliable")
                    return False

                if hasattr(self, text['function']):
                    exec("r = str(self."+text['function']+"(text['data']))")
                else:
                    r = "Function not found"

                self.app.Logging.output("Socket::GET="+str(text['function'])+"&addr="+str(self.addr), "debug", False)

                # send response                
                self.send(r)

            except Exception as e:
                self.app.Logging.output(self.app._("SubgetSocketInterface: Cannot parse json data, is the client bugged?")+" "+str(e), "warning", True)
                self.send("Server Error: "+str(e))

class SocketServer(asyncore.dispatcher):
    app = None

    def __init__(self, host, port, app):
        self.app = app
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM) # IPv6 support will be implemented later
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(3)

    def handle_accept(self):
        pair = self.accept()

        if pair is None:
            pass
        else:
            sock, addr = pair
            handler = SocketInterface(sock, self.app, addr)

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

        if Data[0] == True:
            self.Subget.Logging.output(self.Subget._("Disabling bus in shell mode"))
            return False

        busType = self.Subget.configGetKey("plugin:bus", "bustype")

        if str(busType) == "False" or busType == "detect":
            self.Subget.configSetKey("plugin:bus", "bustype", "detect")
            self.Subget.Logging.output(self.Subget._("Setting bus type to \"detect\" (Linux: dbus, Windows: socket)"), "debug", False)
            self.Subget.saveConfiguration()
            
            # use IP connection (com is bugged) on Windows
            if os.name == "nt":
                busType = "socket"
            else: # on Linux and *BSD we have dbus
                busType = "dbus"

        if busType == "dbus":
            check = self.checkDBUS()
        else:
            host = self.Subget.configGetKey("plugin:bus", "host")
            port = self.Subget.configGetKey("plugin:bus", "port")

            if str(host) == "False":
                self.Subget.configSetKey("plugin:bus", "host", "localhost")
                host = "localhost"
                self.Subget.Logging.output(self.Subget._("Setting default socket host:")+ " localhost", "debug", False)

            if str(port) == "False":
                self.Subget.configSetKey("plugin:bus", "port", "9918")
                self.Subget.Logging.output(self.Subget._("Setting default socket port:")+ " 9118", "debug", False)

            try:
                port = int(port)
            except Exception:
                self.Subget.configSetKey("plugin:bus", "port", "9918")
                self.Subget.Logging.output(self.Subget._("Non-numeric port detected, falling back to")+ " 9118", "warning", True)
                port = 9918


            self.Subget.saveConfiguration()

            check = self.checkSocket()

        if check == True:

            if len(Data[1]) > 0:
                links = str.join('\n', Data[1])

                if busType == "dbus":
                    addLinks = self.bus.get_dbus_method('addLinks', 'org.freedesktop.subget')
                    addLinks(links, False)
                else: # Socket connection
                    self.socketSend("addLinks", links)

                self.Subget.Logging.output(self.Subget._("Added new files to existing list."), "", False)
            else:
                self.Subget.Logging.output(self.Subget._("Only one instance (graphical window) of Subget can be running at once by one user."), "", False) # only one instance of Subget can be running at once

            sys.exit(0)

        # server
        if Data[2] != "watch": # if not running watch with subtitles function
            self.Subget.Logging.output("Spawning server...", "error", True)

            if busType == "socket":
                self.Subget.Logging.output(self.Subget._("Socket server is running on")+ " "+str(host)+":"+str(port), "debug", False)
                self.bus = SocketServer(host, port, self.Subget)
                self.thread = Thread(target=asyncore.loop)
                self.thread.setDaemon(True)
                self.thread.start()
            else:
                self.Subget.Logging.output(self.Subget._("Dbus interface is up..."), "debug", False)
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


    def checkSocket(self):
        if self.socketSend("ping", "") == False:
            return False
        else:
            return True

    def socketSend(self, function, data=''):
        HOST = str(self.Subget.configGetKey("plugin:bus", "host"))
        PORT = int(self.Subget.configGetKey("plugin:bus", "port"))

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))

            if function == "ping":
                text = "ping"
            else:
                text = json.dumps({'function': function, 'data': data})

            s.sendall(text)
            data = s.recv(1024)
            s.close()
            return data
        except socket.error as e:
            return False
