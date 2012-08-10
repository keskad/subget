#-*- coding: utf-8 -*-
import subgetcore, os

####
PluginInfo = {'Requirements' : { 'OS' : 'Unix, Linux'}, 'API': 2, 'Authors': 'webnull', 'domain': '', 'type': 'extension', 'isPlugin': False}

class PluginMain(subgetcore.SubgetPlugin):
    """ Implements kdialog, xmessage, zenity to show error messages """

    subgetIcon = ""
    dialogCommand = None
    dialogType = "kdialog"
    errTypes = {}


    def _onErrorMessage(self, Data, errType='info'):
        self.sendEvent("error", str(Data), errType)
        return Data

    def sendEvent(self, errType, Data):
        if errType == "info":
            errType = "msgbox"
        else:
            errType = "sorry"

        if self.dialogCommand == None:
            self.Subget.Logging.output("dialog disabled", "debug", False)
            return False

        # error type (zenity, xmessage and kdialog has diffirent types, so we need to translate them)
        errType = self.errTypes[self.dialogType][errType]

        # send a command to operating system
        command = self.dialogCommand.replace("{errType}", errType).replace("{Data}", Data).replace("{Icon}", self.subgetIcon).replace("{Title}", "Subget")


        self.Subget.Logging.output(command, "debug", False)
        os.system(command)

    def _pluginInit(self):
        """ Initialize plugin """
        self.subgetIcon = self.Subget.getPath("/usr/share/subget/icons/Subget-logo.xpm")
        self.Subget.Hooking.connectHook("onErrorMessage", self._onErrorMessage)
        forceConfigSetting = self.Subget.configGetKey("dialog", "type")

        if forceConfigSetting == "zenity":
            self.selectZenity()
            return True

        elif forceConfigSetting == "kdialog":
            self.selectKdialog()
            return True

        elif forceConfigSetting == "xmessage":
            self.selectXmessage()
            return True

        if self.Subget.getFile({"/usr/bin/zenity", "/usr/local/bin/zenity"}):
            self.selectZenity()
            return True

        elif self.Subget.getFile({"/usr/bin/kdialog", "/usr/local/bin/kdialog"}):
            self.selectKdialog()
            return True

        elif self.Subget.getFile({"/usr/bin/xmessage", "/usr/local/bin/xmessage"}):
            self.selectXmessage()
            return True

    def selectZenity(self):
        self.dialogCommand = "zenity --info --text=\"{Data}\" --title=\"{Title}\""
        self.dialogType = "zenity"
        self.errTypes['zenity'] = {'msgbox': 'info', 'sorry': 'error'}

    def selectKdialog(self):
        self.dialogCommand = "kdialog --{errType} \"{Data}\" --icon \"{Icon}\" --title \"{Title}\""
        self.dialogType = "kdialog"
        self.errTypes['kdialog'] = {'msgbox': 'msgbox', 'sorry': 'sorry'}

    def selectXmessage(self):
        self.dialogCommand = "xmessage \"{Data}\" -center"
        self.dialogType = "xmessage"
        self.errTypes['xmessage'] = {'msgbox': 'msgbox', 'sorry': 'sorry'}

    def _pluginDestroy(self):
        """ Unload plugin """
        del self
