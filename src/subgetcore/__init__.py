""" Subget core library """

import filemanagers, videoplayers, subgetbus, os, re, httplib, logging, inspect
from time import strftime, localtime

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
            pass
        return False

    def turnOffLogger(self):
        self.logger = None
        return True

    def output(self, message, utype='', savetoLogs=True, execHook=True):
        """ Output to log file and to console """

        message = self.convertMessage(message, inspect.stack()[1][3])
        
        if utype == "debug" and self.loggingLevel > 1:
            if self.logger != None and savetoLogs == True:
                self.logger.debug(message)

            print(message)

        elif utype == "" and self.loggingLevel > 0:
            if self.logger != None and savetoLogs == True:
                self.logger.info(message)

            print(message)

        elif utype == "warning" and self.loggingLevel > 0:
            if self.logger != None and savetoLogs == True:
                self.logger.warning(message)

            print(message)

        elif utype == "critical" and self.loggingLevel > -1:
            if self.logger != None and savetoLogs == True:
                self.logger.critical(message)

            print(message)

        # save all messages to show in messages console
        self.session += message + "\n"

        # update console for example
        try:
            Hooks = self.parent.Hooking.getAllHooks("onLogChange")

            if Hooks != False:
                self.parent.Hooking.executeHooks(Hooks, self.session)

        except Exception as e:
            if execHook == True:
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
    if len(SearchTV1) > 0:
        if seriesTVFormat == False: 
            return ""+SearchTV1[0][0]+" "+addZero(SearchTV1[0][2])+"x"+addZero(SearchTV1[0][3])
        else:
            return ""+SearchTV1[0][0]+" S"+addZero(SearchTV1[0][2])+"E"+addZero(SearchTV1[0][3])
                   # title              # season           # episode
    else:
        # try luck again, now search in TV series format #2 eg. 01x02
        SearchTV1 = re.findall("([A-Za-z0-9 ]+)(.?)([0-9]+)x([0-9]+)(.*)", File, re.IGNORECASE)

        if len(SearchTV1) > 0:
            Zero = SearchTV1[0][0].replace(" 0 ", "")

            if len(SearchTV1) > 0:
                return ""+Zero+" "+addZero(SearchTV1[0][2])+"x"+addZero(SearchTV1[0][3])
            else:
                return ""+Zero+" S"+addZero(SearchTV1[0][2])+"E"+addZero(SearchTV1[0][3])

                   # title              # season           # episode
        else: # if not a TV show - just a movie release
            SearchTV1 = re.findall("([A-Za-z0-9 ]+)(.?)", File, re.IGNORECASE)

            # if its ripped movie release
            if len(SearchTV1) > 0:
                return SearchTV1[0][0] # print only title
            else: # if its unidentified movie type
                return False

def languageFromName(Name):
    countries = {'english': 'en', 'dutch': 'de', 'brazillian': 'br', 'brazillian-portuguese' : 'br', 'italian': 'it', 'arabic': 'sa', 'argentin': 'ar', 'hebrew': 'ps', 'vietnamese': 'vn', 'portuguese': 'pt', 'swedish': 'se', 'polish': 'pl', 'czech': 'cz'}

    if Name in countries:
        return countries[Name]
    else:
        return Name


class SubtitlesList:
    """ Creates a list of subtitles, easy to use in plugins """

    results = list()

    def append(self, language, site, title, url, data, domain, File):
        """ Adds new element to list of subtitles """

        self.results.append({'lang': language, 'site': site, 'title': title, 'url': url, 'data': data, 'domain': domain, 'file': File})

    def output(self):
        """ Called by Subget to get list of Subtitles """

        results = list()
        
        for File in self.results:
            results.append(File)

        return [results]

class Hooking:
    Hooks = dict() # list of all hooks

    def connectHook(self, name, method):
        """ Connect to hook's socket """
        if not name in self.Hooks:
            self.Hooks[name] = list()

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

        if name in self.Hooks:
            return self.Hooks[name]

        return False

    def executeHooks(self, hooks, data=True):
        """ Executes all functions from list. Takes self.getAllHooks as hooks """

        if not hooks == False:
            for Hook in hooks:
                Hook(data)

            return True

        return False        


class SubgetPlugin:
    Subget = None
    HTTPTimeout = 3

    def removeNonAscii(s): 
        """ Removes non-ascii characters from a string """

        return "".join(filter(lambda x: ord(x)<128, s))

    def __init__(self, SubgetLib=None):
        self.Subget = SubgetLib
        self.HTTPTimeout = self.Subget.configGetKey('plugins', 'timeout')

        if self.HTTPTimeout == False or self.HTTPTimeout == None:
            self.HTTPTimeout = 3

    def check_exists(self, File, results):
        return False

    def download_list(self, files, query=''):
        """ Download list of subtitles for a number of files """

        results = SubtitlesList()

        for File in files:
            self.check_exists(File, results)

        return results


    def search_by_keywords(self, Keywords):
        """ Dummy function, you need to replace it to enable search by keyword function """

        return False

    def temporaryPath(self, fileName):
        """ Determinates temporary paths """

        if os.name == "nt": # WINDOWS "THE PROBLEMATIC OS"
            return os.path.expanduser("~").replace("\\\\", "/")+"/"+os.path.basename(fileName)+".zip.tmp"
        else: # UNIX, Linux, *BSD
            return "/tmp/"+os.path.basename(fileName+".zip")


    def HTTPGet(self, Server, Request):
        """ Do a simple HTTP GET request
            Returns: False, False on error
        """

        try:
            conn = httplib.HTTPConnection(Server, 80, timeout=float(self.HTTPTimeout))
            conn.request("GET", Request)
            response = conn.getresponse()
            data = response.read()
        except Exception as e:
            print("[SubgetPlugin] Connection timed out, "+str(e))
            return False, False

        return response, data
