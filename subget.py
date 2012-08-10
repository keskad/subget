#!/usr/bin/env python
#-*- coding: utf-8 -*-
import getopt, sys, os, glob, time, gettext, locale, xml.dom.minidom
import traceback
from threading import Thread
import subgetcore # libraries
from pango import FontDescription

winSubget = ""

if os.name == "nt":
    winSubget = str(os.path.dirname(sys.path[0]+"/")).replace("subget.exe", "") 
    #winSTDOUT = open(winSubget+"/stdout.log", "w")
    #winSTDERR = open(winSubget+"/stderr.log", "w")
    #sys.stdout = winSTDOUT
    #sys.stderr = winSTDERR

    # windows native appearance
    os.environ['PATH'] += ";gtk/lib;gtk/bin"
    os.environ['GTK_PATH'] = winSubget+"/windows/runtime/lib/gtk-2.0"
    os.environ['GTK2_RC_FILES'] = winSubget+"/windows/runtime/share/themes/MS-Windows/gtk-2.0/gtkrc"

import gtk, gobject

if os.name != "nt":
    gtk.gdk.threads_init()
    from distutils.sysconfig import get_python_lib

if sys.version_info[0] >= 3:
    import configparser
else:
    import ConfigParser as configparser

consoleMode=False
action="list"
language="pl"
languages=['pl', 'en']


    ####################################
    ##### GNU Gettext translations #####
    ####################################

if os.name == "nt":
    incpath=winSubget+"/usr/share/subget/locale/"
elif os.path.isdir("usr/share/subget/locale/"):
    incpath="usr/share/subget/locale/";
else:
    incpath="/usr/share/subget/locale/";

langs = ['pl_PL', 'en_US']
lc, encoding = locale.getdefaultlocale()

if (lc):
    langs = [lc]

#print("Translations: "+incpath)
gettext.bindtextdomain('subget', incpath)

t = gettext.translation('subget', incpath, langs, fallback=True)
_ = t.gettext


    ###########################################
    ##### End of GNU Gettext translations #####
    ###########################################


def usage():
    'Shows program usage and version, lists all options'

    print(_("subget for GNU/Linux. Simple Subtitle Downloader for shell and GUI.\nUsage: subget [long GNU option] [option] first-file, second-file, ...\n\n\n --help                : this message\n --console, -c         : show results in console, not in graphical user interface\n --language, -l        : specify preffered language\n --quick, -q           : grab first result and download"))
    print("")

class SubGet:
    dialog=None
    subtitlesList=list()
    Config = dict()
    Windows = dict() # active or non-active windows
    Windows['preferences'] = False
    plugins=dict()
    pluginsList=list() # ordered list
    queueCount = 0
    locks = dict()
    locks['reorder'] = False
    disabledPlugins = list()
    versioning = None
    Hooking = None
    finishedJobs = list()
    gtkSettings = None

    def __init__(self):
        # initialize hooking and logging
        self.Hooking = subgetcore.Hooking()
        self.Logging = subgetcore.Logging(self)

    def getFile(self, kwargs, x=''):
        """ Usage: /usr/bin/subget /usr/local/bin/subget - it will find first working path and return it """

        for key in kwargs:
            if os.path.isfile(key):
                return key

        return False

    def getPath(self, path):
        userPath = os.path.expanduser("~")+path

        if os.path.exists(userPath):
            return userPath
        else:
            return self.subgetOSPath+path

    def doPluginsLoad(self, args):
        global plugins
        debugErrors = ""

        # Windows NT
        if os.name == "nt":
            pluginsDir = self.subgetOSPath+"/subgetlib/"
            sys.path.insert( 0, pluginsDir )
        else: # Linux, FreeBSD and other Unix systems
            pluginsDir = get_python_lib()+"/subgetlib/"

        # fix for python bug which returns invalid path
        if not os.path.isdir(pluginsDir):
            pluginsDir = pluginsDir.replace("/usr/lib/", "/usr/local/lib/")

        # list of disabled plugins
        pluginsDisabled = self.configGetKey('plugins', 'disabled')

        if pluginsDisabled:
            self.disabledPlugins = pluginsDisabled.split(",")


        file_list = glob.glob(pluginsDir+"*.py")

        for Plugin in file_list:
            Plugin = os.path.basename(Plugin)[:-3] # cut directory and .py

            # skip the index
            if Plugin == "__init__":
                continue

            try:
                self.disabledPlugins.index(Plugin)
                self.plugins[Plugin] = 'Disabled'
                self.Logging.output("Disabling "+Plugin, "debug", False)

                continue
            except ValueError:
                self.togglePlugin(False, Plugin, 'activate')


        # plugin execution order
        if "plugins" in self.Config:
            if "order" in self.Config['plugins']:
                order = self.Config['plugins']['order'].split(",")

                for Item in order:
                    if Item in self.plugins:
                        # Python 2.6 compatibility
                        self.pluginsList.append(Item)
            else:
                self.reorderPlugins()
        else:
            self.reorderPlugins()

        # add missing plugins
        [self.pluginsList.append(k) for k in self.plugins if k not in self.pluginsList]

    def reorderPlugins(self):
        """ If plugins order is empty, try to create alphabetical order """
        self.pluginsList = sorted(self.plugins)

    # close the window and quit
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def sendCriticAlert(self, Message):
        """ Send critical error message before exiting when in X11 session """

        if os.path.isfile("/usr/bin/kdialog"):
            os.system("/usr/bin/kdialog --error \""+Message+"\"")
        elif os.path.isfile("/usr/bin/zenity"):
            os.system("/usr/bin/zenity --info --text=\""+Message+"\"")
        elif os.path.isfile("/usr/bin/xmessage"):
            os.system("/usr/bin/xmessage -nearmouse \""+Message+"\"")
        else:
            print(Message)


    def loadConfig(self):
        """ Parsing configuration from ~/.subget/config """

        if not os.path.isdir(os.path.expanduser("~/.subget/")):
            try:
                os.mkdir(os.path.expanduser("~/.subget/"))
            except Exception:
                print("Cannot create ~/.subget directory, please check your permissions")

        configPath = os.path.expanduser("~/.subget/config")
        if not os.path.isfile(configPath):
            configPath = self.subgetOSPath+"/usr/share/subget/config"

        if os.path.isfile(configPath):
            Parser = configparser.ConfigParser()
            try:
                Parser.read(configPath)
            except Exception as e:
                self.Logging.output("Error parsing configuration file from "+configPath+", error: "+str(e), "critical", True)
                self.sendCriticAlert("Subget: Error parsing configuration file from "+configPath+", error: "+str(e))
                sys.exit(os.EX_CONFIG)

            # all configuration sections
            Sections = Parser.sections()

            for Section in Sections:
                Options = Parser.options(Section)
                self.Config[Section] = dict()

                # and configuration variables inside of sections
                for Option in Options:
                    self.Config[Section][Option] = Parser.get(Section, Option)

    def main(self):
        """ Main function, getopt etc. """

        global consoleMode, action, _

        self.LANG = _
        self._ = _

        if os.name == "nt":
            self.subgetOSPath = winSubget+"/"
        elif os.path.exists("usr/share/subget"):
            self.Logging.output("Developer mode", "", False)
            self.subgetOSPath = "."
        else:
            self.subgetOSPath = ""

        try:
            opts, args = getopt.getopt(sys.argv[1:], "hcqw", ["help", "console", "quick", "language=", "watch-with-subtitles"])
        except getopt.GetoptError as err:
            print(_('Error')+": "+str(err)+", "+_("Try --help for usage")+"\n\n")
            usage()
            sys.exit(2)
        # replace with argparse/optparse
        for o, a in opts:
            if o in ('-h', '--help'):
                 usage()
                 exit(2)
            if o in ('-c', '--console'):
                consoleMode=True
            if o in ('-q', '--quick'):
                action="first-result"
            if o in ('-w', '--watch-with-subtitles'):
                action="watch"

        self.loadConfig()

        try:
            level = int(self.configGetKey("logging", "level"))
            self.Logging.loggingLevel = level
        except Exception:
            self.Logging.loggingLevel = 1

        self.Logging.output("Logging level: "+str(self.Logging.loggingLevel), "debug", False)

        self.Logging.output("Loading plugins...", "debug", False)
        self.doPluginsLoad(args)

        cwd = os.getcwd()
        if cwd[:-1] != "/":
            cwd += "/"

        newarg = list()

        for arg in args:
            if os.path.isfile(cwd+arg):
                newarg.append(cwd+arg)
            else:
                newarg.append(arg)

        self.Hooking.executeHooks(self.Hooking.getAllHooks("onInstanceCheck"), [consoleMode, args, action])

        if consoleMode:
            self.shellMode(args)
        else:
            # Fast download option
            if action == "watch":
                self.watchWithSubtitles(args)
            else:
                self.graphicalMode(args)



    ########################################################
    ##### FAST DOWNLOAD, "WATCH WITH SUBTITLES" OPTION #####
    ########################################################


    def textmodeDL(self, Plugin, File):
        State = self.plugins[Plugin]

        if type(State).__name__ != "module":
            self.queueCount = (self.queueCount - 1)
            return False


        if self.plugins[Plugin].PluginInfo['API'] == 1:
            Results = self.plugins[Plugin].download_list(File)
        elif self.plugins[Plugin].PluginInfo['API'] == 2:
            Results = self.plugins[Plugin].instance.download_list(File).output()

        for Result in Results:
            if not Result:
                self.queueCount = (self.queueCount - 1)
                return False

            for Sub in Result:
                try:
                    if Sub == "errInfo":
                        continue

                    self.subtitlesList.append({'language': Sub['lang'], 'name': Sub['title'], 'data': Sub['data'], 'extension': Plugin, 'file': Sub['file']})
                except Exception as e:
                    self.Logging.output("[textModeDL] "+self._("Error trying to get list of subtitles from")+" "+Plugin+", "+str(e))

        self.queueCount = (self.queueCount - 1)



    def textmodeWait(self):
        """ Wait util jobs not done, after that sort all results and download subtitles """

        self.workingState(True)
        Sleept = 0.0

        while True:
            time.sleep(0.2)
            Sleept += 0.2

            if self.queueCount <= 0:
                break

            if Sleept in [30.0, 60.0, 90.0, 120.0]:
                self.Logging.output("[textModeWait] "+str(Sleept)+"s sleep", "debug", False)

            # if waited too many time
            if Sleept > 180:
                self.Logging.output("[textmodeWait] "+_("One of plugins cannot finish its job, cancelling."), "warning")
                self.workingState(False)
                return False

        self.reorderTreeview(False) # Reorder list without using GTK


        self.finishedJobs = dict()
        prefferedLanguage = self.configGetKey('watch_with_subtitles', 'preferred_language')

        # set default language to english
        if not prefferedLanguage:
            prefferedLanguage = 'en'

        # search for matching subtitles
        for Job in self.subtitlesList:
            if not Job['data']['file'] in self.finishedJobs:
                if Job['language'].lower() == prefferedLanguage.lower():
                    self.finishedJobs[Job['data']['file']] = Job
                    current = Thread(target=self.textmodeDLSub, args=(Job,))
                    current.setDaemon(False)
                    current.start()

        # accept other langages than preffered
        if not self.configGetKey('watch_with_subtitles', 'only_preferred_language') == "True":
            for Job in self.subtitlesList:
                if not Job['data']['file'] in self.finishedJobs:
                    self.finishedJobs[Job['data']['file']] = Job
                    current = Thread(target=self.textmodeDLSub, args=(Job,))
                    current.setDaemon(False)
                    current.start()

        self.workingState(False)


    def textmodeDLSub(self, Job):
        self.Logging.output("[textmodeWait] " + _("Downloading to") + " "+Job['data']['file']+".txt")
        Result = self.plugins[Job['extension']].download_by_data(Job['data'], Job['data']['file']+".txt")
        return Result


    def watchWithSubtitles(self, args):
        """ Download first matching subtitles and launch video player.
            Always returns True
        """

        if not args:
            self.Logging.output(_("No files specified in watch with subtitles."), "", False)
            self.sendCriticAlert(_("No files specified in watch with subtitles."))
            sys.exit(1)

        # subtitlesList
        self.queueCount = 0

        # Upgraded to API v2
        for plugin in self.plugins:
            if self.isPlugin(plugin):
                self.queueCount += 1

        for Plugin in self.pluginsList:
            if not self.isPlugin(Plugin):
                continue

            current = Thread(target=self.textmodeDL, args=(Plugin,args))
            current.setDaemon(False)
            current.start()

        # Loop waiting for download to be done
        current = Thread(target=self.textmodeWait)
        current.setDaemon(False)
        current.start()

        # wait for threads to end jobs
        current.join()

        if len(args) == 1:
            # get the first job using "for" and "break" after first result
            if not self.configGetKey('watch_with_subtitles', 'download_only'):
                Found = False

                for File in self.finishedJobs:
                    Found = True
                    break

                if not Found:
                    self.Logging.output(_("No subtitles found for file") + " "+args[0], "warning")
                    self.sendCriticAlert(_("No subtitles found for file") + " "+args[0])

                    try:
                        self.Hooking.executeHooks(self.Hooking.getAllHooks("onSubtitlesDownload"), [False, False, False, False])
                    except Exception as e:
                        self.Logging.output(_("Error")+": "+_("Cannot execute hook")+"; onSubtitlesDownload; "+str(e), "warning", True)
                else:
                    try:
                        self.Hooking.executeHooks(self.Hooking.getAllHooks("onSubtitlesDownload"), [self.configGetKey('watch_with_subtitles', 'download_only'), File+".txt", File, True])
                    except Exception as e:
                        self.Logging.output(_("Error")+": "+_("Cannot execute hook")+"; onSubtitlesDownload; "+str(e), "warning", True)
        else:
            try:
                self.Hooking.executeHooks(self.Hooking.getAllHooks("onSubtitlesDownload"), [False, False, False, True])
            except Exception as e:
                self.Logging.output(_("Error")+": "+_("Cannot execute hook")+"; onSubtitlesDownload; "+str(e), "warning", True)

        return True


    #################################################
    ##### END OF "WATCH WITH SUBTITLES" OPTION  #####
    #################################################





    def addSubtitlesRow(self, language, release_name, server, download_data, extension, File,Append=True):
            """ Adds parsed subtitles to list """
            
            self.subtitlesList.append({'language': language, 'name': release_name, 'server': server, 'data': download_data, 'extension': extension, 'file': File})

            pixbuf_path = self.getPath('/usr/share/subget/icons/flags/'+language+'.xpm')

            if not os.path.isfile(pixbuf_path):
                pixbuf_path = self.getPath('/usr/share/subget/icons/flags/unknown.xpm')
                self.Logging.output("[addSubtitlesRow] "+language+".xpm "+_("icon does not exists, using unknown.xpm"), "warning", False)

            try:
                pixbuf = gtk.gdk.pixbuf_new_from_file(pixbuf_path)
            except Exception:
                self.Logging.output(pixbuf_path+" "+_("icon file not found"), "warning", True)
                return False

            self.liststore.append([pixbuf, str(release_name), str(server), (len(self.subtitlesList)-1)])

    def reorderTreeview(self, useGTK=True):
        """ Sorting subtitles list by plugin priority """

        if self.locks['reorder']:
            return False

        self.locks['reorder'] = True
        self.workingState(True)

        if "plugins" in self.Config:
            if not self.dictGetKey(self.Config['plugins'], 'list_ordering'):
                self.Logging.output(_("Sorting disabled."), "debug", True)
                return True

        while not self.queueCount == 0:
            time.sleep(0.2) # give some time to finish the jobs
            #print("SLEEPING 200ms sec, becasue count is "+str(self.queueCount))

            if self.queueCount == 0:
                break

        #print("QUEUE COUNT: "+str(self.queueCount))

        if self.queueCount == 0:
            self.workingState(False)
            newList = list()

            for Item in self.subtitlesList:
                Item['priority'] = self.pluginsList.index(str(Item['extension']))
                newList.append(Item)

            sortedList = sorted(newList, key=lambda k: k['priority'])
            self.subtitlesList = list()

            if useGTK:
                self.liststore.clear()

                for Item in sortedList:
                    self.addSubtitlesRow(Item['language'], Item['name'], Item['server'], Item['data'], Item['extension'], Item['file'])
            else:
                for Item in sortedList:
                    self.subtitlesList.append({'language': Item['language'], 'name': Item['name'], 'server': Item['extension'], 'data': Item['data'], 'extension': Item['extension'], 'file': Item['file']})

        self.locks['reorder'] = False

    def GTKCheckForSubtitles(self, Plugin):
            State = self.plugins[Plugin]

            if type(State).__name__ != "module":
                self.queueCount = (self.queueCount - 1)
                return

            if self.plugins[Plugin].PluginInfo['API'] == 1:
                Results = self.plugins[Plugin].download_list(self.files)
            elif self.plugins[Plugin].PluginInfo['API'] == 2:
                Results = self.plugins[Plugin].instance.download_list(self.files).output()

            if Results is None:
                self.Logging.output("[plugin:"+Plugin+"] "+_("ERROR: Cannot import"), "warning", True)
            else:
                for Result in Results:
                    if not Result:
                        self.queueCount = (self.queueCount - 1)
                        return False

                    for Movie in Result:
                        try:
                            if not type(Movie).__name__ == "dict":
                                self.Logging.output("[plugin:"+Plugin+"] Error: got "+str(type(Movie).__name__)+", not a dictionary. Data="+str(Movie), "debug", True)
                                continue

                            if not "title" in Movie:
                                self.Logging.output("[plugin:"+Plugin+"] Error: no title found in results", "debug", True)
                                continue

                            self.addSubtitlesRow(Movie['lang'], Movie['title'], Movie['domain'], Movie['data'], Plugin, Movie['file'])
                            self.Logging.output("[plugin:"+Plugin+"] "+_("found subtitles")+" - "+Movie['title'], "debug", True)
                        except AttributeError as e:
                             self.Logging.output("[plugin:"+Plugin+"] "+_("no any subtitles found")+", "+str(e), "debug", True)

            # mark job as done
            self.queueCount = (self.queueCount - 1)


    def dictGetKey(self, Array, Key):
        """ Return key from dictionary, if not exists returns false """

        if Key in Array:
            if Array[Key] == "False":
                return False

            return Array[Key]
        else:
            return False


    # displaying the flag
    def cell_pixbuf_func(self, celllayout, cell, model, iter):
            """ Flag rendering """
            cell.set_property('pixbuf', model.get_value(iter, 0))

    def gtkDebugDialog(self,message):
            self.dialog = gtk.MessageDialog(parent = None,flags = gtk.DIALOG_DESTROY_WITH_PARENT,type = gtk.MESSAGE_INFO,buttons = gtk.BUTTONS_OK,message_format = message)
            self.dialog.set_title("Debug informations")
            self.dialog.connect('response', lambda dialog, response: self.destroyDialog())
            self.dialog.show()


    # DOWNLOAD DIALOG
    def GTKDownloadSubtitles(self, a='', b=''):
            """ Dialog with file name chooser to save subtitles to """

            entry1,entry2 = self.treeview.get_selection().get_selected()    

            if entry2 is None:
                if self.dialog is not None:
                    return
                else:
                    self.dialog = gtk.MessageDialog(parent = None,flags = gtk.DIALOG_DESTROY_WITH_PARENT,type = gtk.MESSAGE_INFO,buttons = gtk.BUTTONS_OK,message_format = _("No subtitles selected."))
                    self.dialog.set_title(_("Information"))
                    self.dialog.connect('response', lambda dialog, response: self.destroyDialog())
                    self.dialog.show()
            else:
                SelectID = int(entry1.get_value(entry2, 3))
                
                if len(self.subtitlesList) == int(SelectID) or len(self.subtitlesList) > int(SelectID):
                    chooser = gtk.FileChooserDialog(title=self._("Where to save the subtitles?"),action=gtk.FILE_CHOOSER_ACTION_SAVE,buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
                    chooser.set_current_folder(os.path.dirname(self.subtitlesList[SelectID]['file']))

                    txtFileName = self.subtitlesList[SelectID]['file']

                    if not ".txt" in txtFileName:
                        txtFileName = txtFileName+".txt"

                    chooser.set_current_name(os.path.basename(txtFileName))
                    response = chooser.run()

                    if response == gtk.RESPONSE_OK:
                        fileName = chooser.get_filename()
                        chooser.destroy()
                        self.GTKDownloadDialog(SelectID, fileName)
                    else:
                        chooser.destroy()
                else:
                    self.Logging.output("[GTK:DownloadSubtitles] subtitle_ID="+str(SelectID)+" "+_("not found in a list, its wired"), "warning", True)

    def GTKDownloadDialog(self, SelectID, filename):
             """Download progress dialog, downloading and saving subtitles to file"""

             print self.subtitlesList[SelectID]
             Plugin = self.subtitlesList[SelectID]['extension']

             State = self.plugins[Plugin]

             if type(State).__name__ == "module":

                 w = gtk.Window(gtk.WINDOW_TOPLEVEL)
                 w.set_resizable(False)
                 w.set_title(_("Download subtitles"))
                 w.set_border_width(0)
                 w.set_size_request(300, 70)

                 fixed = gtk.Fixed()

                 # progress bar
                 self.pbar = gtk.ProgressBar()
                 self.pbar.set_size_request(180, 15)
                 self.pbar.set_pulse_step(0.01)
                 self.pbar.pulse()
                 w.timeout_handler_id = gtk.timeout_add(20, self.update_progress_bar)
                 self.pbar.show()

                 # label
                 label = gtk.Label(_("Please wait, downloading subtitles..."))
                 fixed.put(label, 50,5)
                 fixed.put(self.pbar, 50,30)

                 w.add(fixed)
                 w.show_all()

                 Results = self.plugins[Plugin].language = language

                 if self.plugins[Plugin].PluginInfo['API'] == 1:
                    Results = self.plugins[Plugin].download_by_data(self.subtitlesList[SelectID]['data'], filename)
                 elif self.plugins[Plugin].PluginInfo['API'] == 2:
                    Results = self.plugins[Plugin].instance.download_by_data(self.subtitlesList[SelectID]['data'], filename)

                 if Results != language and Results:
                    try:
                        self.Hooking.executeHooks(self.Hooking.getAllHooks("onSubtitlesDownload"), [False, Results, self.dictGetKey(self.subtitlesList[SelectID]['data'], 'file'), True])
                    except Exception as e:
                        self.Logging.output(_("Error")+": "+_("Cannot execute hook")+"; onSubtitlesDownload; "+str(e), "warning", True)
                        traceback.print_exc(file=sys.stdout)

                 else:
                    try:
                        self.Hooking.executeHooks(self.Hooking.getAllHooks("onSubtitlesDownload"), [False, False, False, False])
                    except Exception as e:
                        self.Logging.output(_("Error")+": "+_("Cannot execute hook")+"; onSubtitlesDownload; "+str(e), "warning", True)

                 w.destroy()

    def update_progress_bar(self):
            """ Progressbar updater, called asynchronously """
            self.pbar.pulse()
            return True


        # DESTROY THE DIALOG
    def destroyDialog(self):
            """ Destroys all dialogs and popups """
            self.dialog.destroy()
            self.dialog = None

    def gtkSelectVideo(self, arg):
            """ Selecting multiple videos to search for subtitles """
            chooser = gtk.FileChooserDialog(title=_("Please select video files"),action=gtk.FILE_CHOOSER_ACTION_OPEN,buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            chooser.set_select_multiple(True)
            response = chooser.run()

            if response == gtk.RESPONSE_OK:
                fileNames = chooser.get_filenames()
                chooser.destroy()

                for fileName in fileNames:
                    if not os.path.isfile(fileName) or not os.access(fileName, os.R_OK):
                        continue

                    self.files = [fileName, ]
                    #self.files = {fileName} # works on Python 2.7 only
                    #print self.files
                    self.TreeViewUpdate()
            else:
                chooser.destroy()

            return True

    def togglePlugin(self, x, Plugin, Action, liststore=None):
        if Action == 'activate':
            self.Logging.output("Activating "+Plugin, "debug", False)

            # load the plugin
            try:
                exec("import subgetlib."+Plugin)
                exec("self.plugins[Plugin] = subgetlib."+Plugin)

                # old API v1
                if self.plugins[Plugin].PluginInfo['API'] == 1:
                    self.plugins[Plugin].loadSubgetObject(self)
                    self.plugins[Plugin].subgetcore = subgetcore

                # compability with new API v2
                elif self.plugins[Plugin].PluginInfo['API'] == 2:
                    exec("self.plugins[Plugin] = subgetlib."+Plugin+"")
                    exec("self.plugins[Plugin].instance = subgetlib."+Plugin+".PluginMain(self)")

                    if "_pluginInit" in dir(self.plugins[Plugin].instance):
                        self.plugins[Plugin].instance._pluginInit()



                if not "type" in self.plugins[Plugin].PluginInfo:
                    self.plugins[Plugin].PluginInfo['type'] = 'normal'

                # refresh the list
                if liststore is not None:
                    liststore.clear() 
                    self.pluginsListing(liststore)

                return True

            except Exception as errno:
                self.plugins[Plugin] = str(errno)
                self.Logging.output(_("ERROR: Cannot import")+" "+Plugin+" ("+str(errno)+")", "warning", True)
                
                return False

        elif Action == 'deactivate':
            self.Logging.output("Deactivating "+Plugin, "debug", False)
            if self.plugins[Plugin] == 'disabled':
                return True

            try:
                self.plugins[Plugin].instance._pluginDestroy()
                del self.plugins[Plugin].instance
            except Exception:
                pass

            self.plugins[Plugin] = 'Disabled'

            # refresh the list
            if liststore is not None:
                liststore.clear() 
                self.pluginsListing(liststore)

            return True

    def pluginInfo(self, x, Plugin):
        print("Feature not implemented.")

    def osName(self):
        if os.name == "nt":
            return "Windows"
        elif sys.platform[0:5] == "linux":
            return "Linux"
        elif sys.platform[0:7] == "freebsd":
            return "FreeBSD"
        else:
            return "Unknown operating system"

    def pluginTreeviewEvent(self, treeview, event, liststore):
        if event.button == 3 or event.type == gtk.gdk._2BUTTON_PRESS:
            x = int(event.x)
            y = int(event.y)
            time = event.time

            pthinfo = treeview.get_path_at_pos(x, y)

            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.grab_focus()
                treeview.set_cursor( path, col, 0)

                # items
                Info = None
                Plugin = liststore[pthinfo[0][0]][1]


        if event.button == 3:
                if event.type == gtk.gdk.BUTTON_PRESS:
                    menu = gtk.Menu() 

                    if self.plugins[Plugin] == 'Disabled':
                        Deactivate = gtk.MenuItem(_("Activate plugin"))
                        Deactivate.connect("activate", self.togglePlugin, Plugin, 'activate', liststore)
                    else:
                        Deactivate = gtk.MenuItem(_("Deactivate plugin"))
                        Deactivate.connect("activate", self.togglePlugin, Plugin, 'deactivate', liststore)

                        if self.plugins[Plugin].PluginInfo['API'] > 1:
                            customMenu = self.plugins[Plugin].instance.customPluginContextMenu()

                            for option in customMenu:
                                try:
                                    customItem = gtk.MenuItem(str(option[0]))
                                    customItem.connect("activate", option[1], option[2])
                                    menu.append(customItem)
                                except Exception as e:
                                    self.Logging.output(_("Cannot add custom menu")+". "+_("plugin")+": "+Plugin+", "+_("exception")+": "+str(e))

                    menu.append(Deactivate)
                    menu.show_all()
                    menu.popup( None, None, None, event.button, time)
        elif event.type == gtk.gdk._2BUTTON_PRESS:
                if self.plugins[Plugin] == 'Disabled':
                    self.togglePlugin(False, Plugin, "activate", liststore)
                else:
                    self.togglePlugin(False, Plugin, "deactivate", liststore)

    def pluginsListing(self, liststore):
            for Plugin in self.pluginsList:
                try:
                    API = self.plugins[Plugin].PluginInfo['API']
                except Exception:
                    API = "?"

                try:
                    Author = self.plugins[Plugin].PluginInfo['Authors']
                except Exception:
                    Author = _("Unknown")

                try:
                    OS = self.plugins[Plugin].PluginInfo['Requirements']['OS']

                    if OS == "All":
                        OS = "Unix, Linux, Windows"

                except Exception:
                    OS = _("Unknown")

                try:
                    Packages = self.plugins[Plugin].PluginInfo['Requirements']['Packages']

                    if Packages:
                        #!!!: refactored, but this var is not used
                        Packages_c = ', '.join(Packages)

                except Exception:
                    Packages = _("Unknown")

                if self.plugins[Plugin] == "Disabled":
                    pixbuf = gtk.gdk.pixbuf_new_from_file(self.subgetOSPath+'/usr/share/subget/icons/plugin-disabled.png')
                    liststore.append([pixbuf, Plugin, OS, str(Author), str(API)])
                    continue

                if not "PluginInfo" in dir(self.plugins[Plugin]):
                    pixbuf = gtk.gdk.pixbuf_new_from_file(self.subgetOSPath+'/usr/share/subget/icons/error.png') 
                    liststore.append([pixbuf, Plugin, OS, str(Author), str(API)])
                    continue

                if self.plugins[Plugin].PluginInfo['type'] == 'extension':
                    pixbuf = gtk.gdk.pixbuf_new_from_file(self.subgetOSPath+'/usr/share/subget/icons/extension.png') 
                    liststore.append([pixbuf, Plugin, OS, str(Author), str(API)])
                    continue

                if type(self.plugins[Plugin]).__name__ == "module":
                    pixbuf = gtk.gdk.pixbuf_new_from_file(self.subgetOSPath+'/usr/share/subget/icons/plugin.png') 
                    liststore.append([pixbuf, Plugin, OS, str(Author), str(API)])
                else:
                    pixbuf = gtk.gdk.pixbuf_new_from_file(self.subgetOSPath+'/usr/share/subget/icons/error.png') 
                    liststore.append([pixbuf, Plugin, OS, str(Author), str(API)])


    def gtkPluginMenu(self, arg):
            """ GTK Widget with list of plugins """

            if not self.dictGetKey(self.Windows, 'gtkPluginMenu'):
                self.Windows['gtkPluginMenu'] = True
            else:
                return False

            window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            window.set_title(_("Plugins"))
            window.set_resizable(True)
            window.set_size_request(700, 290)
            window.set_icon_from_file(self.subgetOSPath+"/usr/share/subget/icons/plugin.png")
            window.connect("delete_event", self.closeWindow, window, 'gtkPluginMenu')

            liststore = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str)
            treeview = gtk.TreeView(liststore)


            # column list
            tvcolumn = gtk.TreeViewColumn(_("Plugin"))
            tvcolumn1 = gtk.TreeViewColumn(_("Operating system"))
            tvcolumn2 = gtk.TreeViewColumn(_("Authors"))
            tvcolumn3 = gtk.TreeViewColumn(_("API interface version"))

            treeview.append_column(tvcolumn)
            treeview.append_column(tvcolumn1)
            treeview.append_column(tvcolumn2)
            treeview.append_column(tvcolumn3)
            treeview.set_reorderable(1)

            cellpb = gtk.CellRendererPixbuf()
            cell = gtk.CellRendererText()
            cell1 = gtk.CellRendererText()
            cell2 = gtk.CellRendererText()
            cell3 = gtk.CellRendererText()

            # add the cells to the columns - 2 in the first
            tvcolumn.pack_start(cellpb, False)
            tvcolumn.set_cell_data_func(cellpb, self.cell_pixbuf_func)
            tvcolumn.pack_start(cell, True)
            tvcolumn1.pack_start(cell1, True)
            tvcolumn2.pack_start(cell2, True)
            tvcolumn3.pack_start(cell3, True)
            tvcolumn.set_attributes(cell, text=1)
            tvcolumn1.set_attributes(cell1, text=2)
            tvcolumn2.set_attributes(cell2, text=3)
            tvcolumn3.set_attributes(cell3, text=4)

            self.pluginsListing(liststore)

            # make treeview searchable
            treeview.set_search_column(1)

            # context menu
            treeview.connect("button-press-event", self.pluginTreeviewEvent, liststore)

            # Allow sorting on the column
            if self.configGetKey('interface', 'custom_plugins_sorting'):
                tvcolumn.set_sort_column_id(1)
                tvcolumn1.set_sort_column_id(1)
                tvcolumn2.set_sort_column_id(2)
                tvcolumn3.set_sort_column_id(3)

            scrolled_window = gtk.ScrolledWindow()
            scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
            scrolled_window.set_border_width(0)
            scrolled_window.set_size_request(700, 230)
            scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
            scrolled_window.add(treeview)

            # Cancel button
            CancelButton = gtk.Button(stock=gtk.STOCK_CLOSE)
            CancelButton.set_size_request(90, 40)
            CancelButton.connect('clicked', self.closePluginsMenu, liststore, window)

            vbox = gtk.VBox(False, 0)
            vbox.set_border_width(0)
            vbox.pack_start(scrolled_window, True, True, 0)

            hbox = gtk.HBox(False, 5)
            hbox.pack_end(CancelButton, False, False, 8)
            vbox.pack_start(hbox, False, False, 8)

            window.add(vbox)
            window.show_all()


    def closePluginsMenu(self, x, liststore, window):
            Order = ""
            self.pluginsList = list() # clear the list

            # create new plugins list
            for Item in liststore:
                self.pluginsList.append(str(Item[1])) # add sorted elements

                # Skip extensions
                if "PluginInfo" in dir(self.plugins[str(Item[1])]): 
                    if self.plugins[str(Item[1])].PluginInfo['type'] == 'extension':
                        continue

                Order += str(Item[1])+","

            if not "plugins" in self.Config:
                self.Config['plugins'] = dict()

            # add to configuration
            self.Config['plugins']['order'] = Order[0:-1]
            
            # save disabled items
            Disabled = ""

            for Item in self.plugins:
                if self.plugins[Item] == 'Disabled':
                    Disabled += str(Item)+","

            self.Config['plugins']['disabled'] = Disabled[0:-1]

            # save configuration and close the window
            self.saveConfiguration()
            self.closeWindow(False, False, window, 'gtkPluginMenu')
            self.reorderTreeview()

    def gtkAboutMenu(self, arg=''):
            """ Shows about dialog """

            if not self.dictGetKey(self.Windows, 'gtkAboutMenu'):
                self.Windows['gtkAboutMenu'] = True
            else:
                return False

            about = gtk.Window(gtk.WINDOW_TOPLEVEL)
            about.set_title(_("About Subget"))
            about.set_resizable(False)
            about.set_size_request(600,550)
            about.set_icon_from_file(self.subgetOSPath+"/usr/share/subget/icons/Subget-logo.png")
            about.connect("delete_event", self.closeWindow, about, 'gtkAboutMenu')

            # container
            fixed = gtk.Fixed()
            
            # logo
            logo = gtk.Image()
            logo.set_from_file(self.subgetOSPath+"/usr/share/subget/icons/Subget-logo.png")
            fixed.put(logo, 12, 20)

            # title
            title = gtk.Label(_("About Subget"))
            title.modify_font(FontDescription("sans 18"))
            fixed.put(title, 150, 20)

            # description title
            description = gtk.Label(_("Small, multiplatform and portable Subtitles downloader \nwritten in Python and GTK.\nWorks on most Unix systems, based on Linux kernel and on Windows NT.\nThis program is a free software licensed on GNU General Public License v3."))
            description.modify_font(FontDescription("sans 8"))
            fixed.put(description, 150, 60)

            # TABS
            notebook = gtk.Notebook()
            notebook.set_tab_pos(gtk.POS_TOP)
            notebook.show_tabs = True
            notebook.set_size_request(580, 370)
            notebook.set_border_width(0) 
            self.gtkAddTab(notebook, _("Team"), _("Programming")+":\n WebNuLL <http://webnull.kablownia.org>\n\n"+_("Testing")+":\n Tiritto <http://dawid-niedzwiedzki.pl>\n WebNuLL <http://webnull.kablownia.org>\n\n"+_("Special thanks")+":\n iluzion <http://dobreprogramy.pl/iluzion>\n famfamfam <http://famfamfam.com>")

            self.gtkAddTab(notebook, _("License"), _("This program was published on Free and Open Software license.\n\nConditions:\n - You have right to share this program in original or modified form\n - You are free to run this program in any purpose\n - You are free to view and modify the source code in any purpose\n - You have right to translate this program to any language you want\n - You must leave a note about original author when modifying or sharing this software\n - The program must remain on the same license when editing or sharing\n\n\nProgram license: GNU General Public License 3 (GNU GPLv3)"))

            self.gtkAddTab(notebook, _("Translating"), "English:\n WebNuLL <http://webnull.kablownia.org>\n\nPolski:\n WebNuLL <http://webnull.kablownia.org>")


            if not os.path.isfile(self.subgetOSPath+"/usr/share/subget/version.xml"):
                self.gtkAddTab(notebook, _("Version"), _("Version information can't be read because file /usr/share/subget/version.xml is missing."))
            else:
                if self.versioning is  None:
                    try:
                        dom = xml.dom.minidom.parse(self.subgetOSPath+"/usr/share/subget/version.xml")

                        self.versioning = {'version': dom.getElementsByTagName('version')[0].childNodes[0].data, 'platforms': '', 'mirrors': '', 'developers': '', 'contact': ''}

                        # Platforms list
                        Platforms = dom.getElementsByTagName('platform')

                        for Item in Platforms:
                            self.versioning['platforms'] += "- "+Item.childNodes[0].data+"\n"
                        del(Platforms)

                        # Mirrors list
                        Mirrors = dom.getElementsByTagName('mirror')

                        for Item in Mirrors:
                            self.versioning['mirrors'] += Item.childNodes[0].data+"\n"
                        del(Mirrors)

                        # Developers list
                        Developers = dom.getElementsByTagName('developer')

                        for Item in Developers:
                            self.versioning['developers'] += '- '+Item.childNodes[0].data+"\n"
                        del(Developers)

                        # Contact list
                        Contact = dom.getElementsByTagName('contact_im')

                        for Item in Contact:
                            self.versioning['contact'] += "* "+Item.getAttribute('type')+": "+Item.childNodes[0].data+"\n"
                        del(Contact)
                    except Exception as e:
                        self.versioning = False
                        self.Logging.output("Catched an exception while tried to parse /usr/share/subget/version.xml, details: "+str(e), "error", True)
                    

                if not self.versioning:
                    self.gtkAddTab(notebook, _("Version"), _("Version information can't be read because there was a problem parsing file /usr/share/subget/version.xml"))
                else:
                    self.gtkAddTab(notebook, _("Version"), _("Version")+": "+self.versioning['version']+", "+self.osName()+"\n\n"+_("Supported platforms")+":\n"+self.versioning['platforms']+"\n"+_("Project developers")+":\n "+self.versioning['developers']+"\n"+_("Contact")+":\n"+self.versioning['contact'])

            fixed.put(notebook, 12, 160)

           

            # add container show all
            about.add(fixed)
            about.show_all()

    def gtkAddTab(self, notebook, label, text):
        authorsFrame = gtk.Frame("")
        authorsFrame.set_border_width(0) 
        authorsFrame.set_size_request(100, 75)
        authorsFrame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)

        authorsFrameContent = gtk.Label(text)
        authorsFrameContent.set_alignment (0, 0)
        authorsFrameContent.set_selectable(True)

        # Scrollbars
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(0)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.add_with_viewport(authorsFrameContent)

        authorsFrame.add(scrolled_window)

        authorsLabel = gtk.Label(label)
        notebook.prepend_page(authorsFrame, authorsLabel)

    def closeWindow(self, Event, X, Window, ID):
        Window.destroy()
        self.Windows[ID] = False

    def isPlugin(self, Plugin):
        if type(self.plugins[Plugin]).__name__ != "module":
            return False

        if not "PluginInfo" in dir(self.plugins[Plugin]):
            return False

        if self.plugins[Plugin].PluginInfo['type'] == 'extension':
            if "isPlugin" in self.plugins[Plugin].PluginInfo:
                return self.plugins[Plugin].PluginInfo['isPlugin'] or self.plugins[Plugin].PluginInfo['isPlugin'] == "True"
            else:
                return False

        return True

    def gtkSearchMenu(self, arg):
            if not self.dictGetKey(self.Windows, 'gtkSearchMenu'):
                self.Windows['gtkSearchMenu'] = True
            else:
                return False

            self.sm = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.sm.set_title(_("Search"))
            self.sm.set_size_request(450, 180)
            self.sm.set_resizable(False)
            self.sm.set_icon_from_file(self.subgetOSPath+"/usr/share/subget/icons/Subget-logo.png")
            self.sm.connect("delete_event", self.closeWindow, self.sm, 'gtkSearchMenu')

            self.sm.fixed = gtk.Fixed()

            # informations
            self.sm.label = gtk.Label(_("Select website to search subtitles on.\nNote: not all websites supports searching subtitles by keywords."))

            # text query
            self.sm.entry = gtk.Entry()
            self.sm.entry.set_max_length(50)
            self.sm.entry.set_size_request(290, 26)
            self.sm.entry.show()

            # combo box with plugin selection
            self.sm.cb = gtk.combo_box_new_text()
            self.sm.cb.append_text(_("All"))
            self.sm.plugins = dict()

            for Plugin in self.pluginsList:
                if not self.isPlugin(Plugin):
                    continue

                # does plugin inform about its domain?
                if self.plugins[Plugin].PluginInfo.has_key('domain'):
                    pluginDomain = self.plugins[Plugin].PluginInfo['domain']
                    self.sm.plugins[pluginDomain] = Plugin
                    self.sm.cb.append_text(pluginDomain)
                else:
                    self.sm.plugins[Plugin] = Plugin
                    self.sm.cb.append_text(Plugin)

            # Set "All plugins" as default active
            self.sm.cb.set_active(0)


            # search button
            self.sm.searchButton = gtk.Button(_("Search"))
            self.sm.searchButton.set_size_request(80, 35)

            image = gtk.Image() # image for button
            image.set_from_stock(gtk.STOCK_FIND, 4)
            self.sm.searchButton.set_image(image)
            self.sm.searchButton.connect('clicked', self.gtkDoSearch)

            # cancel button
            self.sm.cancelButton = gtk.Button(_("Cancel"))
            self.sm.cancelButton.set_size_request(80, 35)
            self.sm.cancelButton.connect('clicked', self.closeWindow, False, self.sm, 'gtkSearchMenu')

            image = gtk.Image() # image for button
            image.set_from_stock(gtk.STOCK_CLOSE, 4)
            self.sm.cancelButton.set_image(image)

            # list clearing check box
            self.sm.clearCB = gtk.CheckButton(_("Clear list before search"))

            self.sm.fixed.put(self.sm.label, 10, 8)
            self.sm.fixed.put(self.sm.entry, 10, 60)
            self.sm.fixed.put(self.sm.cb, 310, 59)
            self.sm.fixed.put(self.sm.clearCB, 20, 90)
            self.sm.fixed.put(self.sm.searchButton, 350, 128)
            self.sm.fixed.put(self.sm.cancelButton, 265, 128)

            self.sm.add(self.sm.fixed)
            self.sm.show_all()
            return True

    def cleanUpResults(self, arg=''):
        self.liststore.clear()
        self.subtitlesList = list()

    def gtkDoSearch(self, arg):
            query = self.sm.entry.get_text()
            #self.sm.destroy()
            time.sleep(0.1)

            if query == "" or query is None:
                return

            if self.sm.clearCB.get_active():
                self.cleanUpResults()

            plugin = self.sm.cb.get_active_text()

            # search in all plugins
            if plugin == _("All"):
                for Plugin in self.pluginsList:
                    try:
                        if not self.isPlugin(Plugin):
                            continue

                        self.plugins[Plugin].language = language

                        if self.plugins[Plugin].PluginInfo['API'] == 1:
                            Results = self.plugins[Plugin].search_by_keywords(query) # query the plugin for results
                        elif self.plugins[Plugin].PluginInfo['API'] == 2:
                            Results = self.plugins[Plugin].instance.search_by_keywords(query).output() # query the plugin for results
                            Results = Results[0]

                        if not Results:
                            return

                        for Subtitles in Results:
                            if isinstance(Subtitles, str):
                                continue

                            self.addSubtitlesRow(Subtitles['lang'], Subtitles['title'], Subtitles['domain'], Subtitles['data'], Plugin, Subtitles['file'])

                    except AttributeError:
                       return True # Plugin does not support searching by keywords
            else:
                try:
                    Plugin = self.sm.plugins[plugin]
                    self.plugins[Plugin].language = language

                    if self.plugins[Plugin].PluginInfo['API'] == 1:
                        Results = self.plugins[Plugin].search_by_keywords(query) # query the plugin for results
                    elif self.plugins[Plugin].PluginInfo['API'] == 2:
                        Results = self.plugins[Plugin].instance.search_by_keywords(query) # query the plugin for results

                        if Results is not False:
                            Results = Results[0]

                    if Results is None or Results is False:
                        return

                    for Result in Results:
                        if isinstance(Result, str):
                            continue

                        self.addSubtitlesRow(Result['lang'], Result['title'], Result['domain'], Result['data'], plugin, Result['file'])

                except AttributeError as errno:
                    self.Logging.output("[plugin:"+self.sm.plugins[plugin]+"] "+_("Searching by keywords is not supported by this plugin"), "info", True)

    def gtkPreferencesQuit(self):
        self.winPreferences.destroy()
        self.Windows['preferences'] = False
        self.saveConfiguration()
        

    def saveConfiguration(self):
        Output = ""

        # saving settings to file
        for Section in self.Config:
            Output += "["+str(Section)+"]\n"

            for Option in self.Config[Section]:
                Output += str(Option)+" = "+str(self.Config[Section][Option])+"\n"

            Output += "\n"

        try:
            self.Logging.output(_("Saving to")+" ~/.subget/config", "debug", True)
            Handler = open(os.path.expanduser("~/.subget/config"), "wb")
            Handler.write(Output)
            Handler.close()
        except Exception as e:
            self.Logging.output(_("Error, cannot save to")+" ~/.subget/config, "+str(e), "critical", True)

    def gtkPreferences(self, aid=''):
        #self.sendCriticAlert("Sorry, this feature is not implemented yet.")
        #return
        if self.Windows['preferences']:
            return False

        self.Windows['preferences'] = True

        self.winPreferences = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.winPreferences.set_title(_("Settings"))
        self.winPreferences.set_resizable(False)
        self.winPreferences.set_size_request(600, 400)
        self.winPreferences.set_icon_from_file(self.subgetOSPath+"/usr/share/subget/icons/Subget-logo.png")
        self.winPreferences.connect('delete_event', lambda b: self.gtkPreferencesQuit())

        # Container
        self.winPreferences.fixed = gtk.Fixed()

        # Notebook
        self.winPreferences.notebook = gtk.Notebook()
        self.winPreferences.notebook.set_scrollable(True)
        self.winPreferences.notebook.set_size_request(580, 330)
        self.winPreferences.notebook.set_properties(group_id=0, tab_vborder=0, tab_hborder=1, tab_pos=gtk.POS_LEFT)
        self.winPreferences.notebook.popup_enable()
        self.winPreferences.notebook.show()

        # Create tabs and append to notebook
        self.gtkPreferencesIntegration()
        self.gtkPreferencesPlugins()
        self.gtkPreferencesWWS()
        self.gtkPreferencesInterface()

        # Close button
        self.winPreferences.CloseButton = gtk.Button(stock=gtk.STOCK_CLOSE)
        self.winPreferences.CloseButton.set_size_request(90, 40)
        self.winPreferences.CloseButton.connect('clicked', lambda b: self.gtkPreferencesQuit())

        # Glue it all together
        self.winPreferences.fixed.put(self.winPreferences.notebook, 10,10)
        self.winPreferences.fixed.put(self.winPreferences.CloseButton, 490, 350)
        self.winPreferences.add(self.winPreferences.fixed)
        self.winPreferences.show_all()

        try:
            self.Hooking.executeHooks(self.Hooking.getAllHooks("onPreferencesOpen"))
        except Exception as e:
            self.Logging.output(_("Error")+": "+_("Cannot execute hook")+"; onPreferencesOpen; "+str(e), "warning", True)

        return True

    def configSetButton(self, Type, Section, Option, Value, revert=False):

        if revert:
            Value = self.revertBool(Value.get_active())
        else:
            Value = Value.get_active()

        try:
            self.Config[Section][Option] = Value
            self.Logging.output(_("Setting config values: ")+ Section+"->"+Option+" = \""+str(Value)+"\"", "debug", False)
            #print("SET to "+str(Value))
        except Exception as e:
            self.Logging.output(_("Error setting configuration variable:")+" "+Section+"->"+Option+" = \""+str(Value)+"\". "+_("Error")+": "+str(e), "warning", True)

    def revertBool(self, boolean):
        return boolean == "False" or boolean

    def configGetSection(self, Section):
        """ Returns section as dictionary 

            Args:
              Section - name of section of ini file ([section] header)

            Returns:
              Dictionary - on success
              False - on false

        """
        return self.Config.get(Section, False)


    def configGetKey(self, Section, Key):
        """ Returns value of Section->Value configuration variable

            Args:
              Section - name of section of ini file ([section] header)
              Key - variable name

            Returns:
              False - when section or key does not exists
              False - when value of variable is "false" or "False" or just False
              string value - value of variable
        """
        try:
            cfg = self.Config[Section][Key]
            if str(cfg).lower() == "false":
                return False
            else:
                return cfg
        except KeyError:
            return False


    def gtkPreferencesIntegration(self):
        # "General" preferences
        Path = os.path.expanduser("~/")

        Label1 = gtk.Label(_("File managers popup menu integration"))
        Label1.set_alignment (0, 0)
        Label1.show()

        # Filemanagers

        # ==== Dolphin, Konqueror
        Dolphin = gtk.CheckButton("Dolphin, Konqueror (KDE)")

        if os.name == "nt":
            dom = False
            Found = False
            Dolphin.set_sensitive(False)
        else:
            Found = subgetcore.filemanagers.checkKDEService(Dolphin, self, Path)
            Dolphin.set_sensitive(True)

        Dolphin.connect("pressed", subgetcore.filemanagers.KDEService, self, Path)

        if Found:
            Dolphin.set_active(1)

        # ==== Nautilus
        Nautilus = gtk.CheckButton("Nautilus (GNOME)")
        if os.name == "nt":
            dom = False
            Found = False
            Nautilus.set_sensitive(False)
        else:
            Found = subgetcore.filemanagers.checkNautilus(Nautilus, self, Path)
            Nautilus.set_sensitive(True)


        Nautilus.connect("pressed", subgetcore.filemanagers.Nautilus, self, Path)

        if Found:
            Nautilus.set_active(1)

        # ==== Thunar
        Thunar = gtk.CheckButton("Thunar (XFCE)")

        if os.name == "nt":
            dom = False
            Found = False
            Thunar.set_sensitive(False)
        else:
            dom, Found = subgetcore.filemanagers.checkThunar(Thunar, self, Path)
        Thunar.connect("pressed", subgetcore.filemanagers.ThunarUCA, self, Path, dom, Found)

        if Found:
            Thunar.set_active(1)

        # ==== PCManFM
        #Thunar.set_sensitive(False)
        PCManFM = gtk.CheckButton("PCManFM (LXDE)")
        PCManFM.connect("pressed", self.configSetButton, "filemanagers", "lxde", PCManFM)
        PCManFM.set_sensitive(False)

        GeneralPreferences = gtk.VBox(False, 0)
        GeneralPreferences.pack_start(Label1, False, False, 4)
        GeneralPreferences.pack_start(Dolphin, False, False, 2)
        GeneralPreferences.pack_start(Nautilus, False, False, 2)
        GeneralPreferences.pack_start(Thunar, False, False, 2)
        GeneralPreferences.pack_start(PCManFM, False, False, 2)

        GeneralPreferences = self.Hooking.executeHooks(self.Hooking.getAllHooks("prefsIntegrationBox"), GeneralPreferences)

        # create margin
        hbox = gtk.HBox(False, 0)
        hbox.pack_start(GeneralPreferences, False, False, 8)

        self.createTab(self.winPreferences.notebook, _("System integration"), hbox)

    def configSetKey(self, Section, Option, Value):
        if not Section in self.Config:
            self.Config[Section] = dict()

        self.Config[Section][Option] = str(Value)

    def WWSDefaultLanguage(self, x, liststore, checkbox):
        """ Sets preferred language for Watch with subtitles feature """
        self.configSetKey('watch_with_subtitles', 'preferred_language', str(liststore[checkbox.get_active()][1]))
        
    def gtkPreferencesInterface(self):
        """ Makes settings tab for subget's interface """

        Toolbar = gtk.CheckButton(self._("Show toolbar")+" ("+self._("requires restart")+")")
        Toolbar.connect("pressed", self.configSetButton, 'interface', 'toolbar', Toolbar, True)

        if self.configGetKey("interface", "toolbar"):
            Toolbar.set_active(1)

        Vbox = gtk.VBox(False, 0)
        Hbox = gtk.HBox(False, 0)
        Vbox.pack_start(Toolbar, False, False, 2)
        Hbox.pack_start(Vbox, False, False, 8)

        self.createTab(self.winPreferences.notebook, self._("Interface"), Hbox)
        self.winPreferences.show_all()

    def gtkPreferencesWWS(self):
        """ Watch with subtitles preferences """

        # "General" preferences
        #!!!: unused
        Path = os.path.expanduser("~/")

        WWS = gtk.Fixed()
        Label1 = gtk.Label(_("\"Watch with subtitles\" settings"))
        Label1.set_alignment (0, 0)
        Label1.show()

        # Filemanagers

        # ==== Download only option
        downloadOnly = gtk.CheckButton(_("Never launch movie, just download subtitles"))
        downloadOnly.connect("pressed", self.configSetButton, 'watch_with_subtitles', 'download_only', downloadOnly, True)
        downloadOnly.set_sensitive(True)
        downloadOnly.set_active(bool(self.configGetKey('watch_with_subtitles', 'download_only')))

        # ==== Only preferred language
        only_preferred_language = gtk.CheckButton(_("Download subtitles only in preferred language"))
        only_preferred_language.connect("pressed", self.configSetButton, 'watch_with_subtitles', 'only_preferred_language', only_preferred_language, True)
        only_preferred_language.set_sensitive(True)
        only_preferred_language.set_active(bool(self.configGetKey('watch_with_subtitles', 'only_preferred_language')))

        # ==== Selection of preferred language
        Label2 = gtk.Label(_("Preferred language:"))

        liststore = gtk.ListStore(gtk.gdk.Pixbuf, str)
        languages = os.listdir(self.getPath("/usr/share/subget/icons/flags"))

        preferred_language = gtk.ComboBox(liststore)
        preferred_language.set_wrap_width(4)

        preferred_language_conf = self.configGetKey('watch_with_subtitles', 'preferred_language')

        i=0
        fi=0

        for Lang in languages:
            basename, extension = os.path.splitext(Lang)

            if extension == ".xpm":
                i+=1

                pixbuf = gtk.gdk.pixbuf_new_from_file(self.getPath("/usr/share/subget/icons/flags/"+basename+".xpm"))
                liststore.append([pixbuf, str(basename)])
                if basename == preferred_language_conf:
                    fi=i

        preferred_language.set_active((fi-1))

        preferred_language.connect("changed", self.WWSDefaultLanguage, liststore, preferred_language)



        cellpb = gtk.CellRendererPixbuf()
        preferred_language.pack_start(cellpb, True)
        preferred_language.add_attribute(cellpb, 'pixbuf', 0)
        cell = gtk.CellRendererText()
        preferred_language.pack_start(cell, True)
        preferred_language.add_attribute(cell, 'text', 1)

        WWS.put(Label1, 10, 8)
        WWS.put(downloadOnly, 10, 25)
        WWS.put(only_preferred_language, 10, 45)
        WWS.put(Label2, 10, 80)
        WWS.put(preferred_language, 150, 75)
        #WWS.put(SelectPlayer, 10, 163)
        
        self.createTab(self.winPreferences.notebook, _("Watch with subtitles"), WWS)

    # Set connection timeouts for all plugins supporting this function
    def gtkPreferencesPlugins_Scale(self, x):
        if not "plugins" in self.Config:
            self.Config['plugins'] = dict()

        self.Config['plugins']['timeout'] = int(x.value)

    def gtkPreferencesPlugins_Sort(self, x):
        self.x.get_active()

    def gtkPreferencesPlugins(self):
        g = gtk.Fixed()
        Label = gtk.Label(_("List ordering"))
        Label.set_alignment (0, 0)

        # Sorting
        AllowSorting = gtk.CheckButton(_("Sort search results by plugins list"))
        if self.configGetKey('plugins', 'list_ordering') == "True":
            AllowSorting.set_active(1)
        else:
            AllowSorting.set_active(0)

        AllowSorting.connect("toggled", self.configSetButton, 'plugins', 'list_ordering', AllowSorting)

        # Global settings
        Label2 = gtk.Label(_("Extensions global settings"))
        adj = gtk.Adjustment(1.0, 1.0, 30.0, 1.0, 1.0, 1.0)
        adj.connect("value_changed", self.gtkPreferencesPlugins_Scale)
        scale = gtk.HScale(adj)
        scale.set_digits(0)
        scale.set_size_request(230, 40)
        scaleValue = int(self.configGetKey('plugins', 'timeout'))

        if scaleValue and scaleValue <= 30:
            adj.set_value(scaleValue)


        Label3 = gtk.Label(_("Timeout waiting for connection")+":")
        
        # put all elements
        g.put(Label, 10, 8)
        g.put(AllowSorting, 10, 26)
        g.put(Label2, 10, 70)
        g.put(Label3, 20, 95)
        g.put(scale, 80, 115)

        self.createTab(self.winPreferences.notebook, _("Plugins"), g)



    def createTab(self, widget, title, inside):
        """ This appends a new page to the notebook. """
        
        page = gtk.Label(title)
        page.show()
        
        widget.append_page(inside, page)
        widget.set_tab_reorderable(page, True)
        widget.set_tab_detachable(page, True)

    def mainTreeViewSelection(self, Object, Event):
        """ Handling all events in main gtk.Treeview """

        if str(Event.type.value_name) == "GDK_2BUTTON_PRESS":
            self.GTKDownloadSubtitles()

    def createImage(self, icon):
        image = gtk.Image()

        try:
            if type(icon).__name__ == "Pixbuf":
                image.set_from_pixbuf(icon)
            elif icon[0:3] == "gtk":
                image.set_from_stock(icon, 2)
            else:
                image.set_from_file(icon)
        except Exception:
            pass

        return image

    def interfaceAddIcon(self, title, onActivate, menuItem, itemName='', icon='', shortkey='', isMenu=False, isToolbar=False, iconOnlyToolbar=False):
        """ Adds icon to toolbar and/or menu of main window """

        toolbar = None
        menu = None

        if isMenu:
            if menuItem in self.window.Menubar.elementsArray:
                menu = gtk.ImageMenuItem(title, self.window.agr)

                if shortkey:
                    key, mod = gtk.accelerator_parse(shortkey)
                    menu.add_accelerator("activate", self.window.agr, key, mod, gtk.ACCEL_VISIBLE)

                menu.connect("activate", onActivate)

                if icon and not iconOnlyToolbar:
                    try:
                        image = self.createImage(icon)
                        menu.set_image(image)
                    except gobject.GError as exc:
                        pass

                self.window.Menubar.elementsArray[menuItem].append(menu)
                self.window.Menubar.show_all()

        if isToolbar and self.window.toolbar is not None:
            self.window.toolbar.elements[itemName] = gtk.ToolButton(title)

            if icon:
                try:
                    image = self.createImage(icon)
                    self.window.toolbar.elements[itemName].set_icon_widget(image)
                except gobject.GError as exc:
                    pass

                self.window.toolbar.elements[itemName].connect("clicked", onActivate)
                self.window.toolbar.insert(self.window.toolbar.elements[itemName], -1)

                toolbar = self.window.toolbar.elements[itemName]
                self.window.toolbar.show_all()

        return menu, toolbar
            
            

    def gtkMainScreen(self,files):
        """ Main GTK screen of the application """
        #if len(files) == 1:
        #gobject.timeout_add(1, self.TreeViewUpdate)
        
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.screen = self.window.get_screen()
        self.window.set_title(_("Download subtitles"))
        self.window.set_resizable(True)

        # make the application bigger if it will fit on screen
        if self.screen.get_width() >= 800:
            self.window.set_size_request(750, 340)

        self.window.connect("delete_event", self.delete_event)
        self.window.set_icon_from_file(self.subgetOSPath+"/usr/share/subget/icons/Subget-logo.png")

        # DRAG & DROP SUPPORT
        TARGET_STRING = 82
        TARGET_IMAGE = 83

        if os.path.isfile("/usr/bin/nautilus"):
            self.window.drag_dest_set(gtk.DEST_DEFAULT_DROP,[("text/plain", 0, TARGET_STRING),("image/*", 0, TARGET_IMAGE)],gtk.gdk.ACTION_COPY)
        else:
            self.window.drag_dest_set(0, [], 0)

        self.window.connect("drag_motion", self.motion_cb)
        self.window.connect("drag_drop", self.drop_cb)
        self.window.connect("drag_data_received", self.drag_data_received)

        ############# Menu #############
        self.window.Menubar = gtk.MenuBar()
        icon_theme = gtk.icon_theme_get_default()

        # Here will be all menus and submenus accessible from plugins api
        self.window.Menubar.elementsArray = dict()

        # Shortcuts
        self.window.agr = gtk.AccelGroup()
        self.window.add_accel_group(self.window.agr)

        # "File" menu
        self.window.Menubar.elementsArray['fileMenu'] = gtk.Menu()
        self.window.Menubar.elementsArray['fileMenuItem'] = gtk.MenuItem(_("File"))
        self.window.Menubar.elementsArray['fileMenuItem'].set_submenu(self.window.Menubar.elementsArray['fileMenu'])
        self.window.Menubar.append(self.window.Menubar.elementsArray['fileMenuItem'])

        # "Tools" menu
        self.window.Menubar.elementsArray['toolsMenu'] = gtk.Menu()
        self.window.Menubar.elementsArray['toolsMenuItem'] = gtk.MenuItem(_("Tools"))
        self.window.Menubar.elementsArray['toolsMenuItem'].set_submenu(self.window.Menubar.elementsArray['toolsMenu'])
        self.window.Menubar.append(self.window.Menubar.elementsArray['toolsMenuItem'])

        # "Plugins list"
        pluginMenu = gtk.ImageMenuItem(_("Plugins"), self.window.agr)
        key, mod = gtk.accelerator_parse("<Control>P")
        pluginMenu.add_accelerator("activate", self.window.agr, key,mod, gtk.ACCEL_VISIBLE)
        pluginMenu.connect("activate", self.gtkPluginMenu)

        try:
            image = gtk.Image()
            image.set_from_file(self.subgetOSPath+"/usr/share/subget/icons/plugin.png")
            pluginMenu.set_image(image)
        except gobject.GError as exc:
            True

        self.window.Menubar.elementsArray['toolsMenu'].append(pluginMenu)

        # Toolbars
        if self.configGetKey("interface", "toolbar") != "False":
            self.window.toolbar = gtk.Toolbar()
            #self.window.toolbar.set_style(gtk.TOOLBAR_ICONS)
            self.window.toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)
            self.window.toolbar.elements = dict()
            self.interfaceAddIcon(gtk.STOCK_ADD, self.gtkSelectVideo, "fileMenu", "add", gtk.STOCK_ADD, '<Control>O', True, True, True)
            self.interfaceAddIcon(gtk.STOCK_FIND, self.gtkSearchMenu, "fileMenu", "search", gtk.STOCK_FIND, '<Control>F', True, True, True)
            self.window.toolbar.set_tooltips(True)

        # "Clear"
        try:
            pixbuf = icon_theme.load_icon("dialog-information", 16, 0)
        except Exception:
            pixbuf = ''

        self.interfaceAddIcon(_("About Subget"), self.gtkAboutMenu, "toolsMenu", "about", pixbuf, '', True, True, False)
        self.interfaceAddIcon(_("Clear list"), self.cleanUpResults, "toolsMenu", "clear", gtk.STOCK_CLEAR, '<Control>L', True, True, False)

        # Preferences
        self.interfaceAddIcon(gtk.STOCK_PREFERENCES, self.gtkPreferences, "toolsMenu", "preferences", gtk.STOCK_PREFERENCES, '<Control>P', True, True, True)

        # Exit position in menu
        self.interfaceAddIcon(gtk.STOCK_QUIT, gtk.main_quit, "fileMenu", "quit", gtk.STOCK_FIND, '<Control>Q', True, False, True)

        ############# End of Menu #############
        #self.fixed = gtk.Fixed()

        self.liststore = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str)
        self.treeview = gtk.TreeView(self.liststore)
        selection = self.treeview.get_selection()
        self.treeview.connect('button-press-event', self.mainTreeViewSelection)


        # column list
        self.tvcolumn = gtk.TreeViewColumn(_("Language"))
        self.tvcolumn1 = gtk.TreeViewColumn(_("Name of release"))
        self.tvcolumn2 = gtk.TreeViewColumn(_("Server"))

        # Resizable attributes
        self.tvcolumn1.set_resizable(True)
        self.tvcolumn2.set_resizable(True)

        self.treeview.append_column(self.tvcolumn)
        self.treeview.append_column(self.tvcolumn1)
        self.treeview.append_column(self.tvcolumn2)


        self.cellpb = gtk.CellRendererPixbuf()
        #self.cellpb.set_property('pixbuf', pixbuf)

        self.cell = gtk.CellRendererText()
        self.cell1 = gtk.CellRendererText()
        self.cell2 = gtk.CellRendererText()

        # add the cells to the columns - 2 in the first
        self.tvcolumn.pack_start(self.cellpb, False)

        self.tvcolumn.set_cell_data_func(self.cellpb, self.cell_pixbuf_func)
        #self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn1.pack_start(self.cell1, True)
        self.tvcolumn2.pack_start(self.cell2, True)
        self.tvcolumn1.set_attributes(self.cell1, text=1)
        self.tvcolumn2.set_attributes(self.cell2, text=2)

        # make treeview searchable
        self.treeview.set_search_column(1)

        # Allow sorting on the column
        self.tvcolumn1.set_sort_column_id(1)
        self.tvcolumn2.set_sort_column_id(2)


        # Create buttons
        self.DownloadButton = gtk.Button(stock=gtk.STOCK_GO_DOWN)
        self.DownloadButton.set_label(_("Download"))
        image = gtk.Image()
        image.set_from_stock("gtk-go-down", gtk.ICON_SIZE_BUTTON)
        self.DownloadButton.set_image(image)
        self.DownloadButton.set_size_request(100, 40)
        #self.fixed.put(self.DownloadButton, 490, 205) # put on fixed

        self.DownloadButton.connect('clicked', lambda b: self.GTKDownloadSubtitles())

        # Cancel button
        self.CancelButton = gtk.Button(stock=gtk.STOCK_CLOSE)
        self.CancelButton.set_size_request(90, 40)
        self.CancelButton.connect('clicked', lambda b: gtk.main_quit())

        # Spinner "Progress indicator"
        try:
            self.window.spinner = gtk.Spinner()
        except Exception:
            self.window.spinner = None

        spinnerHbox = gtk.HBox(False, 0)
        spinnerHbox.pack_start(self.window.Menubar, True, True, 0)

        if self.window.spinner is not None:
            spinnerHbox.pack_end(self.window.spinner, False, False, 5)


        # scrollbars
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scrolled_window.set_border_width(0)
        scrolled_window.set_size_request(600, 200)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(self.treeview)

        #self.fixed.put(scrolled_window, 0, 0)
        #self.fixed.set_border_width(0)
        self.window.vbox = gtk.VBox(False, 0)
        self.window.vbox.set_border_width(0)
        self.window.vbox.pack_start(spinnerHbox, False, False, 0)

        if self.configGetKey("interface", "toolbar"):
            self.window.vbox.pack_start(self.window.toolbar, False, False, 0)

        self.window.vbox.pack_start(scrolled_window, True, True, 0)

        self.window.hbox = gtk.HBox(False, 5)
        self.window.hbox.pack_end(self.DownloadButton, False, False, 5)
        self.window.hbox.pack_end(self.CancelButton, False, False, 0)
        self.window.vbox.pack_start(self.window.hbox, False, False, 8)

        # spinner status
        self.workingState(False)

        self.window.add(self.window.vbox)

        try:
            self.Hooking.executeHooks(self.Hooking.getAllHooks("onGTKWindowOpen"))
        except Exception as e:
            self.Logging.output(_("Error")+": "+_("Cannot execute hook")+"; GTKWindowOpen; "+str(e), "warning", True)

        self.window.show_all()

    def workingState(self, state):
        try:
            if self.window.spinner is not None:
                if state:
                    self.window.spinner.show()
                    self.window.spinner.start()
                    return True
                else:
                    self.window.spinner.stop()
                    self.window.spinner.hide()
                    return False
        except Exception:
            pass

    ##### DRAG & DROP SUPPORT #####
    def motion_cb(self, wid, context, x, y, time):
        context.drag_status(gtk.gdk.ACTION_COPY, time)
        return True
    
    def drop_cb(self, wid, context, x, y, time):
        if context.targets:
            wid.drag_get_data(context, context.targets[0], time)
            return True
        return False

    
    def drag_data_received(self, img, context, x, y, data, info, time):
        """ Receive dropped data, parse and call plugins """

        if data.format == 8:
            Files = data.data.replace('\r', '').split("\n")
            self.files = list()

            for File in Files:
                File = File.replace("file://", "")

                if os.path.isfile(File):
                    self.files.append(File)

            context.finish(True, False, time)
            self.TreeViewUpdate()
                
        
    ##### END OF DRAG & DROP SUPPORT #####

    # UPDATE THE TREEVIEW LIST
    def TreeViewUpdate(self):
        """ Refresh TreeView, run all plugins to parse files """

        if not self.files:
            return

        # increase queue
        self.queueCount = (self.queueCount + len(self.pluginsList))

        for Plugin in self.pluginsList:
            if not self.isPlugin(Plugin):
                continue

            current = Thread(target=self.GTKCheckForSubtitles, args=(Plugin,))
            current.setDaemon(True)
            current.start()

        current = Thread(target=self.reorderTreeview)
        current.setDaemon(True)
        current.start()



    def graphicalMode(self, files):
        """ Detects operating system and load GTK GUI """
        self.files = files

        self.Logging.output("Preparing GTK interface...", "debug", False)

        #gtk.rc_parse("usr/share/subget/gtkrc")
        self.gtkMainScreen(files)
        gobject.timeout_add(50, self.TreeViewUpdate)
        gtk.mainloop()

    def shellMode(self, files):
        """ Works in shell mode, searching, downloading etc..."""
        global plugins, action

        # just find all matching subtitles and print it to console
        if action == "list":
            for Plugin in self.pluginsList:
                State = self.plugins[Plugin]

                if not self.isPlugin(Plugin):
                    continue

                Results = self.plugins[Plugin].language = language

                if self.plugins[Plugin].PluginInfo['API'] == 1:
                    Results = self.plugins[Plugin].download_list(files)
                elif self.plugins[Plugin].PluginInfo['API'] == 2:
                    Results = self.plugins[Plugin].instance.download_list(files).output()

                if Results is None:
                    continue

                for Result in Results:
                    for Movie in Result:
                        try:
                            if Movie.has_key("title"):
                                print(Movie['domain']+"|"+Movie['lang']+"|"+Movie['title'])
                        except AttributeError:
                            continue


        elif action == "first-result":
                Found = False
                preferredData = False

        for File in files:
            for Plugin in self.plugins:
                State = self.plugins[Plugin]

                if not self.isPlugin(Plugin):
                    continue

                fileToList = list()
                fileToList.append(File)

                Results = self.plugins[Plugin].language = language

                if self.plugins[Plugin].PluginInfo['API'] == 1:
                    Results = self.plugins[Plugin].download_list(fileToList)
                elif self.plugins[Plugin].PluginInfo['API'] == 2:
                    Results = self.plugins[Plugin].instance.download_list(fileToList).output()

                if Results is not None:
                    if isinstance(Results[0], dict):
                        continue
                    else:
                        if Results[0][0]["lang"] == language:
                            FileTXT = File+".txt"

                            if self.plugins[Plugin].PluginInfo['API'] == 1:
                                DLResults = self.plugins[Plugin].download_by_data(Results[0][0]['data'], FileTXT)
                            elif self.plugins[Plugin].PluginInfo['API'] == 2:
                                DLResults = self.plugins[Plugin].instance.download_by_data(Results[0][0]['data'], FileTXT)

                            print(_("Subtitles saved to")+" "+str(DLResults))
                            Found = True
                            break
                        elif preferredData is not None:
                            continue
                        else:
                            preferredData = Results[0][0]

        if not Found and preferredData:
            FileTXT = File+".("+str(preferredData['lang'])+").txt"

            if self.plugins[Plugin].PluginInfo['API'] == 1:
                DLResults = self.plugins[Plugin].download_by_data(preferredData['data'], FileTXT)
            elif self.plugins[Plugin].PluginInfo['API'] == 2:
                DLResults = self.plugins[Plugin].instance.download_by_data(preferredData['data'], FileTXT)

            print(_("Subtitles saved to")+" "+str(DLResults)+", "+_("but not in your preferred language"))

    def errorMessage(self, message):
         """ Create's error popups, created for notify plugin """

         self.Hooking.executeHooks(self.Hooking.getAllHooks("onErrorMessage"), message)

if __name__ == "__main__":
    SubgetMain = SubGet()
    SubgetMain.main()
