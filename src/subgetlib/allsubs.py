import httplib, urllib, time, os, hashlib, subprocess, re, zipfile
from xml.dom import minidom

####
PluginInfo = { 'Requirements' : { 'OS' : 'All'}, 'API': 1, 'Authors': 'webnull', 'domain': 'allsubs.org'  }
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
        conn = httplib.HTTPConnection('api.allsubs.org', 80, timeout=3)
        conn.request("GET", "/index.php?limit=20&search="+urllib.quote_plus(movieRealName))
        response = conn.getresponse()
        data = response.read()
    except Exception:
        print "[plugin:allsubs] Connection timed out"
        return False

    nodes = list()

    dom = minidom.parseString(data)

    resultsCount = int(dom.getElementsByTagName('found_results').item(0).firstChild.data)

    Results = dom.getElementsByTagName('item')

    for node in Results:
        try:
            Title = str(node.getElementsByTagName('title').item(0).firstChild.data)
            Download = str(node.getElementsByTagName('link').item(0).firstChild.data).replace("subs-download", "subs-download2")
            Languages = str(node.getElementsByTagName('languages').item(0).firstChild.data)
            Languages = Languages.split(",")
            Language = Languages[0]
            Count = (len(str(node.getElementsByTagName('files_in_archive').item(0).firstChild.data).split('|'))-1)
        except AttributeError:
            continue
   
        nodes.append({'lang': str(Language).lower(), 'site' : 'allsubs.org', 'title' : Title+" ("+str(Count)+")", 'url' : Download, 'data': {'file': File, 'url': Download, 'lang': str(Language).lower()}, 'domain': 'allsubs.org', 'file': File})

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
    try:
        conn = httplib.HTTPConnection('www.allsubs.org', 80, timeout=3)
        conn.request("GET", File['url'].replace('http://www.allsubs.org', ''))
        response = conn.getresponse()
        data = response.read()
    except Exception as e:
        print "[plugin:allsubs] Error: "+str(e)
        return False

    if os.name == "nt": # WINDOWS "THE PROBLEMATIC OS"
        TMPName = os.path.expanduser("~").replace("\\\\", "/")+"/"+os.path.basename(File['file'])+".zip.tmp"
    else: # UNIX, Linux, *BSD
        TMPName = "/tmp/"+os.path.basename(File['file']+".zip")

    Handler = open(TMPName, "wb")
    Handler.write(data)
    Handler.close()

    z = zipfile.ZipFile(TMPName)
    ListOfNames = z.namelist()

    # single file in archive
    if len(ListOfNames) == 1:
        Handler = open(SavePath, "wb")
        Handler.write(z.read(ListOfNames[0]))
        Handler.close()
        z.close()
    else:
        z.extractall(os.path.dirname(SavePath))
        z.close()

    #os.remove(TMPName)
    return SavePath
