## DBUS
import os

if not os.name == "nt":
    import dbus, dbus.service, dbus.glib

    class SubgetService(dbus.service.Object):
        subget = None

        def __init__(self):
            bus_name = dbus.service.BusName('org.freedesktop.subget', bus=dbus.SessionBus())
            dbus.service.Object.__init__(self, bus_name, '/org/freedesktop/subget')

        @dbus.service.method('org.freedesktop.subget')
        def ping(self):
            """ Check if Subget is already running """

            return True

        @dbus.service.method('org.freedesktop.subget')
        def openSearchMenu(self):
            """ Opens search dialog """

            if not self.subget == None:
                return self.subget.gtkSearchMenu(None) 

        @dbus.service.method('org.freedesktop.subget')
        def openPluginsMenu(self):
            """ Opens plugin menu """

            if not self.subget == None:
                return self.subget.gtkPluginMenu(None)

        @dbus.service.method('org.freedesktop.subget')
        def openSelectVideoDialog(self):
            """ Opens Video Selection dialog """

            if not self.subget == None:
                return self.subget.gtkSelectVideo(None)

        @dbus.service.method('org.freedesktop.subget')
        def openAboutDialog(self):
            """ Opens About dialog """

            if not self.subget == None:
                return self.subget.gtkAboutMenu(None)

        @dbus.service.method('org.freedesktop.subget')
        def clearList(self):
            """ Clean up the list """
            if not self.subget == None:
                return self.subget.liststore.clear()


        @dbus.service.method('org.freedesktop.subget')
        def toggleVideoPlayer(self, Mode='Auto'):
            """ Toggle video player function """
            if not self.subget == None:
                if Mode == 'Auto': # Automatic toggle mode
                    if self.subget.Config['afterdownload']['playmovie'] == True:
                        self.subget.Config['afterdownload']['playmovie'] = False
                        self.subget.VideoPlayer.set_active(0)
                    else:
                        self.subget.Config['afterdownload']['playmovie'] = True
                        self.subget.VideoPlayer.set_active(1)

                elif Mode == True:
                    self.subget.Config['afterdownload']['playmovie'] = True
                    self.subget.VideoPlayer.set_active(1)
                elif Mode == False:
                    self.subget.Config['afterdownload']['playmovie'] = False
                    self.subget.VideoPlayer.set_active(0)

        @dbus.service.method('org.freedesktop.subget')
        def addLinks(self, Links, Wait=False):
            """ Add links seperated by new line.
                Returns nothing when not waiting, and other values when waiting for function finish working.
                On errors returns false.
                Default - Don't wait.
            """
            if self.subget == None:
                return False

            if not str(type(Links).__name__) == "String":
                return False

            Links = Links.split("\n")
            self.subget.files = Links

            if not Wait == False:
                return self.subget.TreeViewUpdate()
            else:
                self.subget.TreeViewUpdate()
