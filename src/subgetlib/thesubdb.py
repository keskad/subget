import httplib, urllib, re, time, hashlib, os

apiUrl = 'http://api.opensubtitles.org/xml-rpc'
userAgent = "SubDB/1.0 (Subget/1.0; http://github.com/webnull/subget)"
subgetObject=""
HTTPTimeout = 2
Language = 'en'

PluginInfo = { 'Requirements' : { 'OS' : 'All' }, 'Authors': 'webnull', 'API': 1, 'domain': 'opensubtitles.org' }

def loadSubgetObject(x):
    global subgetObject
    subgetObject = x

    if "plugins" in subgetObject.Config:
        if "timeout" in subgetObject.Config['plugins']:
            HTTPTimeout = subgetObject.Config['plugins']['timeout']

def download_list(files):
    results = searchSubtitles(files)
    test = list()
    test.append(results)
    return test

def download_quick(files):
    return

def download_by_data(File, SavePath):
    global HTTPTimeout

    try:
        conn = httplib.HTTPConnection('www.opensubtitles.org', 80, timeout=HTTPTimeout)
        conn.request("GET", File['link'].replace("http://www.opensubtitles.org", ""))
        response = conn.getresponse()
        data = response.read()
    except Exception as e:
        print("[plugin:opensubtitles] Connection timed out, details: "+str(e))
        return False

    if os.name == "nt": # WINDOWS "THE PROBLEMATIC OS"
        TMPName = os.path.expanduser("~").replace("\\\\", "/")+"/"+os.path.basename(File['file'])+".tmp"
    else: # UNIX, Linux, *BSD
        TMPName = "/tmp/"+os.path.basename(File['file'])

    try:
        Handler = open(TMPName, "wb")
        Handler.write(data)
        Handler.close()


        f = gzip.open(TMPName, 'rb')
        file_content = f.read()
        f.close()

        Handler = open(SavePath, "wb")
        Handler.write(file_content)
        Handler.close()
    except Exception as e:
        print("[plugin:opensubtitles] Exception: "+str(e))

    return True

def search_by_keywords(Keywords):
    print("[plugin:thesubdb] thesubdb.com does not support searching by keywords.")
    return False

def searchSubtitles(Files):
    global Language, LanguageTable

    #for File in Files:
        
    
    return False

def check_exists(File):
    global userAgent

    URL = "http://api.thesubdb.com/?action=download&hash={hash}&language=en"
    Hash = get_hash(File)

    Headers = dict()
    Headers['User-Agent'] = userAgent

    Connection = httplib.HTTPConnection('api.thesubdb.com', 80, timeout=10)
    Connection.request("GET", "/?action=download&hash="+Hash+"&language=en", headers=Headers)
    Response = Connection.getresponse()
    print Response.status, Response.reason

def parseResults(subtitlesList, fileSizes=False):
    nodes = list()

        #nodes.append({'lang': subtitle['SubLanguageID'], 'site' : 'opensubtitles.org', 'title' : subtitle['SubFileName'], 'domain': 'opensubtitles.org', 'data': {'file': subtitle['File'], 'link': subtitle['SubDownloadLink']}, 'link': subtitle['SubDownloadLink'], 'file': subtitle['SubFileName']})

    return nodes


def get_hash(name):
    readsize = 64 * 1024
    with open(name, 'rb') as f:
        size = os.path.getsize(name)
        data = f.read(readsize)
        f.seek(-readsize, os.SEEK_END)
        data += f.read(readsize)
    return hashlib.md5(data).hexdigest()

check_exists("/media/Movies/The.Mentalist.S03E07.720p.HDTV.x264-CTU.mkv")
