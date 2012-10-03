""" Subget core library """

import filemanagers, os, re, httplib, logging, inspect, traceback, subprocess, zipfile, sys
from collections import defaultdict
from time import strftime, localtime
from StringIO import StringIO

class Logging:
    logger = None

    # -1 = Don't log any messages even important too
    # 0 = Don't log any messages, only if important (critical errors)
    # 1 = Log everything but debugging messages
    # 2 = Debug messages

    loggingLevel = 1 
    session = ""
    parent = None

    def __init__(self, Parent):
        self.parent = Parent
        self.initializeLogger()

    def convertMessage(self, message, stackPosition):
        return strftime("%d/%m/%Y %H:%M:%S", localtime())+", "+stackPosition+": "+message

    def initializeLogger(self):
        try:
            self.logger = logging.getLogger('subget')
            handler = logging.FileHandler(os.path.expanduser("~/.subget/subget.log"))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
            return True
        except Exception as e:
            self.logger = None
            print("Cannot get access ~/.subget/subget.log, check your permissions")
        return False

    def turnOffLogger(self):
        self.logger = None
        return True

    def output(self, message, utype='', savetoLogs=True, execHook=True, skipDate=False):
        """ Output to log file and to console """

        if not skipDate:
            message = self.convertMessage(message, inspect.stack()[1][3])
        
        if utype == "debug" and self.loggingLevel > 1:
            if self.logger is not None and savetoLogs:
                self.logger.debug(message)

            print(message)

        elif utype == "" and self.loggingLevel > 0:
            if self.logger is not None and savetoLogs:
                self.logger.info(message)

            print(message)

        elif utype == "warning" and self.loggingLevel > 0:
            if self.logger is not None and savetoLogs:
                self.logger.warning(message)

            print(message)

        elif utype == "critical" and self.loggingLevel > -1:
            if self.logger is not None and savetoLogs:
                self.logger.critical(message)

            print(message)

        # save all messages to show in messages console
        self.session += message + "\n"

        # update console for example
        try:
            Hooks = self.parent.Hooking.getAllHooks("onLogChange")

            if Hooks:
                self.parent.Hooking.executeHooks(Hooks, self.session)

        except Exception as e:
            if execHook:
                self.parent.Logging.output(self.parent._("Error")+": "+self.parent._("Cannot execute hook")+"; onLogChange; "+str(e), "warning", True, False)
            else:
                print(self.parent._("Error")+": "+self.parent._("Cannot execute hook")+"; onLogChange; "+str(e))
                

# fixes episode or season number for TV series eg. 1x3 => 01x03
def addZero(number):
    if len(number) == 1:
        return "0"+str(number)
    else:
        return number

def getSearchKeywords(File, seriesTVFormat=False):
    Replacements = [ 'HDTVRIP', 'HDTV', 'CTU', 'XVID', 'crimson', 'amiable', 'lol', 'tvrip', 'fov', '720p', '360p', '1080p', 'hd', 'fullhd', 'sfm', 'bluray', 'x264', 'web-dl', 'aac20' ]

    OriginalFileName = File
    Splittext = os.path.splitext(File)
    File = Splittext[0]

    File = File.replace(".", " ").replace("[", " ").replace("]", " ").replace("-", " ").replace("_", " ")

    # replace all popular names
    for k in Replacements:
        Expr = re.compile(k, re.IGNORECASE)
        File = Expr.sub('', File)

    SearchTV1 = re.findall("([A-Za-z0-9- ]+)(.?)S([0-9]+)E([0-9]+)(.*)", File, re.IGNORECASE)

    # if its in TV series format eg. S01E02
    if SearchTV1:
        if not seriesTVFormat:
            return ""+SearchTV1[0][0]+" "+addZero(SearchTV1[0][2])+"x"+addZero(SearchTV1[0][3])
        else:
            return ""+SearchTV1[0][0]+" S"+addZero(SearchTV1[0][2])+"E"+addZero(SearchTV1[0][3])
                   # title              # season           # episode
    else:
        # try luck again, now search in TV series format #2 eg. 01x02
        SearchTV1 = re.findall("([A-Za-z0-9 ]+)(.?)([0-9]+)x([0-9]+)(.*)", File, re.IGNORECASE)

        if SearchTV1:
            Zero = SearchTV1[0][0].replace(" 0 ", "")

            if SearchTV1:
                return ""+Zero+" "+addZero(SearchTV1[0][2])+"x"+addZero(SearchTV1[0][3])
            else:
                #???: this never will be executed
                return ""+Zero+" S"+addZero(SearchTV1[0][2])+"E"+addZero(SearchTV1[0][3])

                   # title              # season           # episode
        else: # if not a TV show - just a movie release
            SearchTV1 = re.findall("([A-Za-z0-9 ]+)(.?)", File, re.IGNORECASE)

            # if its ripped movie release
            if SearchTV1:
                return SearchTV1[0][0] # print only title
            else: # if its unidentified movie type
                return False

def languageFromName(Name):
    countries = {'english': 'en', 'dutch': 'de', 'brazillian': 'br', 'brazillian-portuguese' : 'br', 'italian': 'it', 'arabic': 'sa', 'argentin': 'ar', 'hebrew': 'ps', 'vietnamese': 'vn', 'portuguese': 'pt', 'swedish': 'se', 'polish': 'pl', 'czech': 'cz'}

    return countries.get(Name, Name)


class SubtitlesList:
    """ Creates a list of subtitles, easy to use in plugins """

    results = list()

    def __init__(self):
        self.results = list() # erase the list, just for sure

    def append(self, language, site, title, url, data, domain, File):
        """ Adds new element to list of subtitles """

        self.results.append({'lang': language, 'site': site, 'title': title, 'url': url, 'data': data, 'domain': domain, 'file': File})

    def output(self):
        """ Called by Subget to get list of Subtitles """
        return [self.results]

class Hooking:
    Hooks = defaultdict(list) # list of all hooks

    def connectHook(self, name, method):
        """ Connect to hook's socket """
        # defaultdict is used so if key doesn't exist it will be automaticly
        # created
        self.Hooks[name].append(method)

    def removeHook(self, name, method):
        if not name in self.Hooks:
            return True

        self.Hooks[name].remove(method)

        if len(self.Hooks[name]) == 0:
            del self.Hooks[name]

        return True 

    def getAllHooks(self, name):
        """ Get all hooked methods to execute them """
        return self.Hooks.get(name, False)


    def executeHooks(self, hooks, data=True):
        """ Executes all functions from list. Takes self.getAllHooks as hooks """

        if hooks:
            for Hook in hooks:
                try:
                    data = Hook(data)
                except Exception as e:
                    buffer = StringIO()
                    traceback.print_exc(file=buffer)
                    print(buffer.getvalue())

        return data       


class SubgetPlugin:
    Subget = None
    HTTPTimeout = 3
    contextMenu = list()

    def error(self, strE):
        self.Subget.Logging.output("[plugin:"+str(inspect.stack()[0][1])+"] "+str(strE), "error", True)

    def removeNonAscii(self, s): 
        """ Removes non-ascii characters from a string """

        return "".join([x for x in s if ord(x) < 128])

    def __init__(self, SubgetLib=None):
        self.Subget = SubgetLib
        self.HTTPTimeout = self.Subget.configGetKey('plugins', 'timeout')

        if not self.HTTPTimeout or self.HTTPTimeout is None:
            self.HTTPTimeout = 3

    def check_exists(self, File, results):
        return False

    def unZip(self, data, SavePath):
        """ Unpacks zipped archive

            Args:
              subtitleZipped - encoded data
              SavePath - destination where to save decoded data

            Returns:
              File - you must manually check if it exists  
        """

        TMPName = self.temporaryPath(os.path.basename(SavePath))+".tmp"

        try:
            Handler = open(TMPName, "wb")
            Handler.write(data)
            Handler.close()

            print TMPName
            sys.exit(0)

            z = zipfile.ZipFile(TMPName)
            ListOfNames = z.namelist()

            if ListOfNames:
                unzipped = z.read(ListOfNames[0])

                x = open(SavePath, "wb")
                x.write(str(unzipped))
                x.close()
                z.close()
                os.remove(TMPName)

        except Exception:
            buffer = StringIO()
            traceback.print_exc(file=buffer)
            self.Subget.Logging.output(buffer.getvalue(), "warning", True)
            pass

        return SavePath


    def unSevenZip(self, subtitleZipped, File):
        """ Unpacks 7zipped archive

            Args:
              subtitleZipped - encoded data
              File - destination where to save decoded data

            Returns:
              File - you must manually check if it exists  
        """

        Handler = open(File+".7z", "wb")
        Handler.write(subtitleZipped)
        Handler.close()

        # use p7zip.exe to unpack subtitles on Windows
        if os.name == "nt":
            subprocess.call("\""+self.Subget.subgetOSPath.replace("/", "\\")+"7za.exe\" x -y -so -piBlm8NTigvru0Jr0 \""+File+".7z\" > \""+File+"\"", shell=True, bufsize=1)
        else: # and 7zip on Linux and FreeBSD
            os.system(self.Subget.getFile(["/usr/bin/7z", "/usr/local/bin/7z"])+" x -y -so -piBlm8NTigvru0Jr0 \""+File+".7z\" 2>/dev/null > \""+File+"\"")

        os.remove(File+".7z")
        return File

    def download_list(self, files, query=''):
        """ Download list of subtitles for a number of files """

        results = SubtitlesList()

        for File in files:
            self.check_exists(File, results)

        return results

    def customPluginContextMenu(self):
        """ Returns list of custom items in plugin context menu """
        return self.contextMenu

    def contextMenuAdd(self, title, hookedFunction, params):
        if not isinstance(title, str):
            return False

        if not isinstance(self.contextMenu, list):
            self.contextMenu = list()

        self.contextMenu.append([title, hookedFunction, params])


    def search_by_keywords(self, Keywords):
        """ Dummy function, you need to replace it to enable search by keyword function """

        return False

    def temporaryPath(self, fileName):
        """ Determinates temporary paths """

        if os.name == "nt": # WINDOWS "THE PROBLEMATIC OS"
            return os.path.expanduser("~").replace("\\\\", "/")+"/"+os.path.basename(fileName)+".tmp"
        else: # UNIX, Linux, *BSD
            return "/tmp/"+os.path.basename(fileName)


    def HTTPGet(self, Server, Request, Headers=None):
        """ Do a simple HTTP GET request
            Returns: False, False on error
        """

        self.Subget.Logging.output(str(Server)+str(Request), "debug", False)

        response = None

        try:
            if Headers:
                conn = httplib.HTTPConnection(Server, 80, Headers, timeout=float(self.HTTPTimeout))
            else:
                conn = httplib.HTTPConnection(Server, 80, timeout=float(self.HTTPTimeout))

            conn.request("GET", Request)
            response = conn.getresponse()
            data = response.read()

        except Exception as e:
            self.Subget.Logging.output("HTTP Connection error, "+str(e), "warning", False)
            self.Subget.errorMessage(self.Subget._("HTTP Connection error to server") + " "+Server+", "+self.Subget._("propably server is busy, please try again later. Error code: ")+str(response))
            return False, False

        return response, data
