import httplib, urllib, time, os, hashlib, subprocess, re, zipfile

####
PluginInfo = { 'Requirements' : { 'OS' : 'All'}, 'API': 1, 'Authors': 'webnull', 'domain': 'napisy24.pl'  }
language = "PL"

retries=0 # Retry the connection if failed
maxRetries=8
errInfo=""
subgetObject=""
HTTPTimeout = 2
subgetcore = None

### Specification:
# http://napisy24.pl/search.php?str=QUERY - searching
# http://napisy24.pl/download/ID/ - downloading (ZIP format)

#???: it is already used somewhere -> move to "utils" and reuse this function?
def removeNonAscii(s): return "".join([x for x in s if ord(x) < 128])

def loadSubgetObject(x):
    global subgetObject

    subgetObject = x

    if "plugins" in subgetObject.Config:
        if "timeout" in subgetObject.Config['plugins']:
            HTTPTimeout = subgetObject.Config['plugins']['timeout']

#???: it is already used somewhere -> move to "utils" and reuse this function?
def download_list(files, query=''):
    return [check_exists(File) for File in files]

def getListOfSubtitles(movieRealName, File):
    global HTTPTimeout

    try:
        conn = httplib.HTTPConnection('napisy24.pl', 80, timeout=HTTPTimeout)
        conn.request("GET", "/search.php?str="+urllib.quote_plus(movieRealName))
        response = conn.getresponse()
        data = response.read()
    except Exception:
        print("[plugin:napisy24] Connection timed out")
        return False

    nodes = list()
    data = data.replace("\t", " ").replace("\n", "")
    dataAreaStart = data.find("<div id=\"mainLevel\">")
    dataAreaStop = data.find("alt=\"Uaktualnione\"")
    data = removeNonAscii(data)
    dataCutedOff = data[dataAreaStart:dataAreaStop]

    currentCount = re.findall("<a href=\"/\">napisy24.pl</a> > Znaleziono ([0-9]+) film", dataCutedOff)

    if int(currentCount[0]):

        Items = dataCutedOff.split("<a href=\"javascript:void(0);\" onclick=\"javascript:showInfo('")

        for Item in Items:
            ID = re.findall("<a href=\"/download/([0-9]+)/\">", Item)
        
            if ID:
                End = Item.split("<a href=\"/napis/"+ID[0]+"/\"")
                ItemData = End[0]
                
                resultsTime = re.findall("Czas trwania: \<strong\>([0-9:]+)\</strong\>", ItemData)
                resultsFPS = re.findall("FPS: \<strong\>([0-9.]+)\<\/strong\>", ItemData)
                resultsSize = re.findall("Rozmiar pliku: \<strong\>([0-9]+)\<\/strong\>", ItemData)
                resultsLanguage = re.findall("\<img src=\"\/images\/ico_flag_([a-zA-Z]+)_([0-9+).png\" width=\"([0-9]+)\" height=\"([0-9]+)\" alt=\"([A-Za-z0-9]+)\"", ItemData)
                Name = re.findall("<a href=\"/download/([0-9]+)/\">\<strong\>(.*)\<\/strong\>\<\/a\>", ItemData)

                if len(Name) == 1:
                    if len(Name[0]) != 2:
                        continue
        
                    Name = Name[0][1]

                if len(resultsLanguage) == 1:
                    if resultsLanguage[0]:
                        resultsLanguage = resultsLanguage[0][0]
                    else:
                        resultsLanguage = "unknown"
                else:
                    resultsLanguage = "unknown"
                
                if len(resultsSize) == 1:
                    resultsSize = resultsSize[0]
                else:
                    resultsSize = 0
    
                if len(resultsFPS) == 1:
                    resultsFPS = resultsFPS[0]
                else:
                    resultsFPS = 0
    
                if len(resultsTime) == 1:
                    resultsTime = resultsTime[0]
                else:
                    resultsTime = 0

                nodes.append({'lang': str(resultsLanguage).lower(), 'site' : 'napisy24.pl', 'title' : str(Name), 'url' : 'http://napisy24.pl/download/'+str(ID[0])+'/', 'fps': resultsFPS, 'size': str(resultsSize), 'time': resultsTime, 'data': {'file': File, 'headers': response.getheaders(), 'id': str(ID[0]), 'type': 'napisy24.pl', 'search_string': urllib.quote_plus(movieRealName), 'lang': str(resultsLanguage).lower()}, 'domain': 'napisy24.pl', 'file': File})


    archiveCount = re.findall("<a href=\"http://napisy.org\">Napisy.org</a> > Znaleziono ([0-9]+) film", dataCutedOff)

    if int(archiveCount[0]) == 0:
        return nodes

    # napisy.org archive support
    Archives = dataCutedOff.split("href=\"/download/archiwum/")

    #???: will this work as expected: exclude first item from Archives
    for Archive in Archives[1:]:
        End = Archive.split("png\" width=\"17\" height=\"17\" alt=\"")

        if len(End) > 5:
           continue

        Number = re.findall("([0-9]+)/\"\>", End[0])
        ID = Number[0]

        Name = re.findall("<td( | class=\"dark\")>([A-Za.-z _-]+)<\/td>", End[0])
        Name = Name[0][1]
        Language = re.findall("<img src=\"\/images\/ico_flag_([A-Za-z]+)_", End[0])
        Language = Language[0]

        nodes.append({'lang': str(Language).lower(), 'site' : 'napisy.org', 'title' : str(Name), 'url' : 'http://napisy24.pl/download/archiwum/'+str(ID)+'/', 'data': {'file': File, 'headers': response.getheaders(), 'id': str(ID), 'type': 'napisy.org', 'search_string': urllib.quote_plus(movieRealName), 'lang': str(Language).lower()}, 'domain': 'napisy.org', 'file': File})

    return nodes

def search_by_keywords(Keywords):
    return check_exists(Keywords)

def check_exists(File):
    global subgetObject
    global language

    if File is not None:
        movieName = subgetcore.getSearchKeywords(os.path.basename(File))

        if movieName:
            subtitleList = getListOfSubtitles(movieName, File)
            return subtitleList
        else:
            #???: is this an constant?
            return {'errInfo': "NOT_FOUND"}

    else:
        return {'errInfo': "NOT_FOUND"}


def download_by_data(File, SavePath):
    global HTTPTimeout

    Cookies = None

    # Search for cookies
    for Item in File['headers']:
        if str(Item[0]).lower() == "set-cookie":
            Cookies = Item[1]
            break

    if Cookies is None:
        return {'errInfo': "NOT_FOUND"}

    PHPSESSID = re.findall('PHPSESSID=([A-Za-z-_0-9]+);', Cookies)

    Headers = {'Cookie': 'PHPSESSID='+PHPSESSID[0]+'; pobierzDotacje=1;', 'Referer': 'http://napisy24.pl/search.php?str='+File['search_string'], 'User-agent': 'Mozilla/5.0 (X11; U; Gentoo Linux; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/14.0.341.0' }

    try:
        conn = httplib.HTTPConnection('napisy24.pl', 80, Headers, timeout=HTTPTimeout)

        if File['type'] == 'napisy.org':
            conn.request("GET", "/download/archiwum/"+File['id']+"/")
        else:
            conn.request("GET", "/download/"+File['id']+"/")

        response = conn.getresponse()
        data = response.read()
    except Exception as e:
        print("[plugin:napisy24] Connection timed out, err: "+str(e))
        return False

    if os.name == "nt": # WINDOWS "THE PROBLEMATIC OS"
        TMPName = os.path.expanduser("~").replace("\\\\", "/")+"/"+os.path.basename(File['file'])+".tmp"
    else: # UNIX, Linux, *BSD
        TMPName = "/tmp/"+os.path.basename(File['file'])

    Handler = open(TMPName, "wb")
    Handler.write(data)
    Handler.close()

    z = zipfile.ZipFile(TMPName)
    ListOfNames = z.namelist()

    if ListOfNames:
        Handler = open(SavePath, "wb")
        Handler.write(z.read(ListOfNames[0]))
        Handler.close()
        z.close()
        os.remove(TMPName)

        return SavePath
