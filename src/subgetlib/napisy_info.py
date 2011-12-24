import httplib, urllib, time, os, hashlib, re, zipfile, time
from xml.dom import minidom

####
PluginInfo = { 'Requirements' : { 'OS' : 'All' }, 'Authors': 'webnull', 'API': 1, 'domain': 'napisy.info' }

LANGLIST = {'polski': 'pl', 'angielski': 'en'}

subgetObject = ""
HTTPTimeout = 2
subgetcore = None

def loadSubgetObject(x):
    global subgetObject

    subgetObject = x

    if "plugins" in subgetObject.Config:
        if "timeout" in subgetObject.Config['plugins']:
            HTTPTimeout = subgetObject.Config['plugins']['timeout']

def download_list(files, query=''):
    results = list()

    for File in files:
        results.append(check_exists(File))

    return results


def check_exists(File):
    # http://napisy.info/plugin/SzukajTytulow.php?sid=subget&t=Sliders
    # http://napisy.info/plugin/SzukajNapisow.php?sid=subget&to=Sliders%2001x01
    # http://napisy.info/napisy_info_[tutaj ID].zip

    if File != None:
        movieName = subgetcore.getSearchKeywords(os.path.basename(File))
        movieName = getMovieName(movieName)
        
        if movieName != False:
            subtitleList = getListOfSubtitles(movieName, File)

            if subtitleList != None:
                if len(subtitleList) > 0:
                    return subtitleList
                else:
                    return {'errInfo': "NOT_FOUND"}
            else:

                return {'errInfo': "NOT_FOUND"}
        else:
            return {'errInfo': "NOT_FOUND"}

# SEARCH SUBTITLES BY MOVIE NAME
def getListOfSubtitles(movieRealName, File):
    global HTTPTimeout

    # http://napisy.info/plugin/SzukajNapisow.php?sid=subget&to=Sliders%2001x01

    try:
        conn = httplib.HTTPConnection('napisy.info', 80, timeout=HTTPTimeout)
        conn.request("GET", "/plugin/SzukajNapisow.php?sid=subget&to="+urllib.quote_plus(movieRealName))
        response = conn.getresponse()
        data = response.read()
    except Exception:
        print "[plugin:napisy_info] Connection timed out"
        return False

    dom = minidom.parseString(data)

    Items = dom.getElementsByTagName('item')
    nodes = list()

    for node in Items:
        ID = node.getElementsByTagName('id').item(0)
        LANG = node.getElementsByTagName('language').item(0)

        if ID != None:
            ID = str(ID.firstChild.data)

        if LANG != None:
            LANG = str(LANG.firstChild.data)

        nodes.append({'lang': LANGLIST[LANG.lower()], 'site' : 'napisy.info', 'title' : movieRealName, 'url' : 'http://napisy.info/napisy_info_'+ID+'.zip', 'data': {'file': File, 'url': 'http://napisy.info/napisy_info_'+ID+'.zip', 'lang': LANGLIST[LANG.lower()]}, 'domain': 'napisy.info', 'file': File})

    return nodes
    
    


# GET MOVIE NAME FROM SERVER
def getMovieName(parsedFileName):
    global HTTPTimeout

    # http://napisy.info/plugin/SzukajTytulow.php?sid=subget&t=Sliders

    try:
       conn = httplib.HTTPConnection('napisy.info', 80, timeout=HTTPTimeout)
       conn.request("GET", "/plugin/SzukajTytulow.php?sid=subget&t="+urllib.quote_plus(parsedFileName))
       response = conn.getresponse()
       data = response.read()
    except Exception:
        print "[plugin:napisy_info] Connection timed out"
        return False

    dom = minidom.parseString(data)
        
    titleOriginal =  dom.getElementsByTagName('title.original').item(0)
    if titleOriginal == None:
        return False
    else:
        titleOriginal = titleOriginal.firstChild.data.replace("\n", "")
        return titleOriginal
        


def get_subtitle(File):
    if File != None:
        movieName = subgetcore.getSearchKeywords(os.path.basename(File))
        movieName = getMovieName(movieName)
        
        if movieName != False:
            subtitleList = getListOfSubtitles(movieName, File)

            if subtitleList != None:
                if len(subtitleList) > 0:
                    return subtitleList
                else:
                    return {'errInfo': "NOT_FOUND"}
            else:

                return {'errInfo': "NOT_FOUND"}
        else:
            return {'errInfo': "NOT_FOUND"}

def search_by_keywords(Keywords):
    return check_exists(Keywords)

def download_by_data(File, SavePath):
    subtitleContent = urllib.urlopen(File['url']).read()

    if os.name == "nt": # WINDOWS "THE PROBLEMATIC OS"
        TMPName = os.path.expanduser("~").replace("\\\\", "/")+"/"+os.path.basename(File['file'])+".tmp"
    else: # UNIX, Linux, *BSD
        TMPName = "/tmp/"+os.path.basename(File['file'])

    Handler = open(TMPName, "wb")
    Handler.write(subtitleContent)
    Handler.close()

    z = zipfile.ZipFile(TMPName)
    ListOfNames = z.namelist()

    if len(ListOfNames) > 0:
        Handler = open(SavePath, "wb")
        Handler.write(z.read(ListOfNames[0]))
        Handler.close()
        z.close()
        os.remove(TMPName)

    return SavePath
        

