#-*- coding: utf-8 -*-
import subgetcore, sys, os, subprocess

try:
    import dbus
except ImportError:
    pass

####
PluginInfo = {'Requirements' : { 'OS' : 'Unix, Linux'}, 'API': 2, 'Authors': 'webnull', 'domain': '', 'type': 'extension', 'isPlugin': False}

class PluginMain(subgetcore.SubgetPlugin):
    notifyType = None
    notifyData = None
    subgetIcon = ""
    iconContents = ""

    def _onSubtitlesDownload(self, Data):
        """# == Data {
        # 0 => Play video? True : False
        # 1 => Text file location
        # 2 => Video file (if any)
        # """

        if Data[3] == False:
            self.sendEvent("subget:", "<b>"+self.Subget._("Subtitles cannot be downloaded, see console for details")+".</b>")
            return Data

        if os.path.isfile(str(Data[2])):
            self.sendEvent("subget:", "<b>"+self.Subget._("Downloaded subtitles for file")+":<br/> "+os.path.basename(str(Data[2]))+"</b><br/>"+self.Subget._("Have a nice time watching the movie!"))
        else:
            self.sendEvent("subget:", "<b>"+self.Subget._("Subtitles downloaded")+".</b>")

        return Data

    def sendEvent(self, title, text):
        """ Sends notification """

        if self.notifyType == None:
            self.selectNotify()

        if self.notifyType == "":
            self.Subget.Logging.output(self.Subget._("Cannot identify system notification"), "warning", True)
            return True

        self.Subget.Logging.output(self.notifyType+" -> "+title+": "+text, "debug", False)

        if self.notifyType == "knotify": # knotify (throught dbus interface on kde)
            self._knotifySend(text, title)

        elif self.notifyType == "libnotify": # libnotify (pynotify)
            self._libnotifySend(text, title)

        elif self.notifyType == "command": # /usr/bin/notify-send (libnotify-bin)
            os.system(self.notifyData.replace("%title%", title).replace("%text%", text))



    def _knotifySend(self, message, title=''):
        """ Use knotify dbus interface to create and send notification """

        try:
            if self.iconContents == "":
                w = open(self.subgetIcon, "r")
                self.iconContents = w.read()
                w.close()

            self.notifyData.event("warning", "kde", [], title, message, bytearray(self.iconContents), [], 16000, 0, dbus_interface="org.kde.KNotify")
        except Exception as e:
            self.Subget.Logging.output(self.Subget._("Error")+": "+str(e), "error", True)
            pass

    def _libnotifySend(self, message, title=''):
        try:
            notification = self.libnotify.Notification(title, message, self.subgetIcon)
            notification.show()
        except Exception as e:
            self.Subget.Logging.output("libnotify failed, "+str(e), "warning", True)

    def selectNotify(self):
        """ Detects installed notify systems and select first one """

        if os.name != "nt":
            p = subprocess.Popen(['/bin/ps', 'aux'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            output, errors = p.communicate()

            notifySend = self.Subget.getFile(["/usr/bin/notify-send", "/usr/local/bin/notify-send"])

            if "gnome-settings-daemon" in output:
                if notifySend != False:
                    self.notifyType = "command"
                    self.notifyData = notifySend+" -u normal -i /usr/share/subget/icons/Subget-logo.png \"%title%\" \"%text%\""
                else:
                    # libnotify
                    try:
                        import pynotify
                        self.notifyType = "libnotify"
                        self.libnotify = pynotify
                    except Exception as e:
                        pass

                return True

            # knotify
            try:
                knotify = dbus.SessionBus().get_object("org.kde.knotify", "/Notify")
                self.notifyType = "knotify"
                self.notifyData = knotify
                return True

            except dbus.exceptions.DBusException as e:
                self.Subget.Logging.output("knotify "+self.Subget._("not found"), "debug", False)

            # notify-send command
            if notifySend != False:
                self.notifyType = "command"
                self.notifyData = notifySend+" -u normal -i /usr/share/subget/icons/Subget-logo.png \"%title%\" \"%text%\""
                return True

        self.notifyType = ""

    def _pluginInit(self):
        """ Initialize plugin """

        self.subgetIcon = self.Subget.getPath("/usr/share/subget/icons/Subget-logo.xpm")
        self.Subget.Hooking.connectHook("onSubtitlesDownload", self._onSubtitlesDownload)

    def _pluginDestroy(self):
        """ Unload plugin """
        del self
