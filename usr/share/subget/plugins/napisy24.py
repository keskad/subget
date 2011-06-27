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
    numberOfResults = re.findall("\<a href=\"\/\"\>napisy24.pl\<\/a\> \> Znaleziono ([0-9]+) film", data)

    if numberOfResults == None:
        return {'errInfo': "NOT_FOUND"}

    if int(numberOfResults[0]) == 0:
        return {'errInfo': "NOT_FOUND"}

    #results = re.findall("\<tr\>(.?)\<a href=\"\/download\/([0-9]+)\/\"\>\<strong\>(.*)\<\/strong\>\<\/a\>(.?)\<td \>(.*)\<br \/\>\<em\>(.?)Czas trwania: \<strong\>([0-9:]+)\</strong\>\<br \/\>(.?)FPS: \<strong\>([0-9.]+)\<\/strong\>\<br \/\>(.?)Rozmiar pliku: \<strong\>([0-9]+)\<\/strong\>", data)

    resultsID = re.findall("\<a href\=\"\/download\/([0-9]+)\/\"\>\<strong\>(.*)\<\/strong\>\<\/a\>", data)
    resultsTime = re.findall("Czas trwania: \<strong\>([0-9:]+)\</strong\>", data)
    resultsFPS = re.findall("FPS: \<strong\>([0-9.]+)\<\/strong\>", data)
    resultsSize = re.findall("Rozmiar pliku: \<strong\>([0-9]+)\<\/strong\>", data)
    #<img src="/images/ico_flag_pl_2.png" width="17" height="17" alt="Polski"
    resultsLanguage = re.findall("\<img src=\"\/images\/ico_flag_([a-zA-Z]+)_([0-9+).png\" width=\"([0-9]+)\" height=\"([0-9]+)\" alt=\"([A-Za-z0-9]+)\"", data)

    for Subtitle in range(int(numberOfResults[0])):
        nodes.append({'lang': str(resultsLanguage[Subtitle][0]).lower(), 'site' : 'napisy24.pl', 'title' : str(resultsID[Subtitle][1]), 'url' : 'http://napisy24.pl/download/'+str(resultsID[Subtitle][0])+'/', 'fps': str(resultsFPS[Subtitle][0]), 'size': str(resultsSize[Subtitle][0]), 'time': str(resultsTime[Subtitle][0]), 'data': {'file': File, 'headers': response.getheaders(), 'id': str(resultsID[Subtitle][0]), 'search_string': urllib.quote_plus(movieRealName), 'lang': str(resultsLanguage[Subtitle][0]).lower()}, 'domain': 'napisy24.pl', 'file': File})

    return nodes

    

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
        #Result = list()
        #Result.append({'lang': language.lower(), 'site' : 'napisy24.pl', 'title' : os.path.basename(File)[:-3]+"txt", 'url' : subtitleUrl, 'data': {'file': File, 'lang': language}, 'domain': 'napiprojekt.pl', 'file': File})


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
  #  else:
    #    return {'errInfo': "NOT_FOUND"}
        

