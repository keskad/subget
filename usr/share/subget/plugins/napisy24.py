import httplib, urllib, time, os, hashlib, subprocess, re, zipfile

####
PluginInfo = { 'Requirements' : { 'OS' : 'All'}, 'API': 1, 'Authors': 'webnull'  }
language = "PL"

retries=0 # Retry the connection if failed
maxRetries=8
errInfo=""
subgetObject=""

### Specification:
# http://napisy24.pl/search.php?str=QUERY - searching
# http://napisy24.pl/download/ID/ - downloading (ZIP format)

def removeNonAscii(s): return "".join(filter(lambda x: ord(x)<128, s))

def loadSubgetObject(x):
    global subgetObject

    subgetObject = x

# fixes episode or season number for TV series eg. 1x3 => 01x03
def addZero(number):
    if len(number) == 1:
        return "0"+str(number)
    else:
        return number

def getSearchKeywords(File):
    OriginalFileName = File
    File = File.replace(".", " ").replace("[", " ").replace("]", " ").replace("-", " ").replace("_", " ")
    SearchTV1 = re.findall("([A-Za-z0-9- ]+)(.?)S([0-9]+)E([0-9]+)(.*)", File)

    # if its in TV series format eg. S01E02
    if len(SearchTV1) > 0:
            return ""+SearchTV1[0][0]+" "+addZero(SearchTV1[0][2])+"x"+addZero(SearchTV1[0][3])
                   # title              # season           # episode
    else:
        # try luck again, now search in TV series format #2 eg. 01x02
        SearchTV1 = re.findall("([A-Za-z0-9 ]+)(.?)([0-9]+)x([0-9]+)(.*)", File)

        if len(SearchTV1) > 0:
            return ""+SearchTV1[0][0]+" "+addZero(SearchTV1[0][2])+"x"+addZero(SearchTV1[0][3])
                   # title              # season           # episode
        else: # if not a TV show - just a movie release
            SearchTV1 = re.findall("([A-Za-z0-9 ]+)(.?)([dvdrip|xvid|lol|tvrip|cam]+)(.*)", File, re.IGNORECASE)

            # if its ripped movie release
            if len(SearchTV1) > 0:
                return SearchTV1[0][0] # print only title
            else: # if its unidentified movie type
                SearchTV1 = re.findall("([A-Za-z0-9 ]+)(.?)\.([a-zA-Z]{3}+)", File, re.IGNORECASE)
                return SearchTV1

def download_list(files, query=''):
    results = list()

    for File in files:
        results.append(check_exists(File))

    return results

def getListOfSubtitles(movieRealName, File):
    try:
        conn = httplib.HTTPConnection('napisy24.pl', 80, timeout=2)
        conn.request("GET", "/search.php?str="+urllib.quote_plus(movieRealName))
        response = conn.getresponse()
        data = response.read()
    except Exception:
        print "[plugin:napisy24] Connection timed out"
        return False

    nodes = list()
    data = data.replace("\t", " ").replace("\n", "")
    dataAreaStart = data.find("<div id=\"mainLevel\">")
    dataAreaStop = data.find("alt=\"Uaktualnione\"")
    data = removeNonAscii(data)
    dataCutedOff = data[dataAreaStart:dataAreaStop]

    currentCount = re.findall("<a href=\"/\">napisy24.pl</a> > Znaleziono ([0-9]+) film", dataCutedOff)

    print currentCount
    print urllib.quote_plus(movieRealName)
    if int(currentCount[0]) > 0:

        Items = dataCutedOff.split("<a href=\"javascript:void(0);\" onclick=\"javascript:showInfo('")

        for Item in Items:
            ID = re.findall("<a href=\"/download/([0-9]+)/\">", Item)
        
            if len(ID) > 0:
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
                    if len(resultsLanguage[0]) > 0:
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
    print "Napisy.org !"

    for Archive in Archives:
        End = Archive.split("png\" width=\"17\" height=\"17\" alt=\"")
        
        if len(End) > 5:
           continue
        
        Number = re.findall("([0-9]+)/\"\>", End[0])
        ID = Number[0]
    
        Name = re.findall("<td( | class=\"dark\")>(.*)<\/td>", End[0])
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

    if File != None:
        movieName = getSearchKeywords(os.path.basename(File))
         
        if movieName != False:
            subtitleList = getListOfSubtitles(movieName, File)
            return subtitleList
        else:
            return {'errInfo': "NOT_FOUND"}

    else:
        return {'errInfo': "NOT_FOUND"}


def download_by_data(File, SavePath):
    Cookies = None

    # Search for cookies
    for Item in File['headers']:
        if str(Item[0]).lower() == "set-cookie":
            Cookies = Item[1]
            break

    if Cookies == None:
        return {'errInfo': "NOT_FOUND"}

    PHPSESSID = re.findall('PHPSESSID=([A-Za-z-_0-9]+);', Cookies)

    Headers = {'Cookie': 'PHPSESSID='+PHPSESSID[0]+'; pobierzDotacje=1;', 'Referer': 'http://napisy24.pl/search.php?str='+File['search_string'], 'User-agent': 'Mozilla/5.0 (X11; U; Gentoo Linux; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/13.0.481.0' }

    try:
        conn = httplib.HTTPConnection('napisy24.pl', 80, Headers, timeout=2)

        if File['type'] == 'napisy.org':
            conn.request("GET", "/download/archiwum/"+File['id']+"/")
        else:
            conn.request("GET", "/download/"+File['id']+"/")

        response = conn.getresponse()
        data = response.read()
    except Exception:
        print "[plugin:napisy24] Connection timed out"
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

    if len(ListOfNames) > 0:
        Handler = open(SavePath, "wb")
        Handler.write(z.read(ListOfNames[0]))
        Handler.close()
        z.close()
        os.remove(TMPName)

        return SavePath
