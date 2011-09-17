import httplib, urllib, re, time, hashlib, os

apiUrl = 'http://api.opensubtitles.org/xml-rpc'
userAgent = "SubDB/1.0 (Subget/1.0; http://github.com/webnull/subget)"
subgetObject=""
HTTPTimeout = 2
Language = 'en'

PluginInfo = { 'Requirements' : { 'OS' : 'All' }, 'Authors': 'webnull', 'API': 1, 'domain': 'thesubdb.com' }

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

def download_quick(files):
    return

def download_by_data(File, SavePath):
    global HTTPTimeout

    try:
        conn = httplib.HTTPConnection('api.thesubdb.com', 80, timeout=HTTPTimeout)
        conn.request("GET", File['link'])
        response = conn.getresponse()
        data = response.read()
    except Exception as e:
        print("[plugin:thesubdb] Connection timed out, details: "+str(e))
        return False

    try:
        Handler = open(SavePath, "wb")
        Handler.write(data)
        Handler.close()
    except Exception as e:
        print("[plugin:thesubdb] Exception: "+str(e))

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

    try:
        Connection = httplib.HTTPConnection('api.thesubdb.com', 80, timeout=HTTPTimeout)
        Connection.request("GET", "/?action=download&hash="+Hash+"&language=en,pl,pt,ru,hu,it,br,cz,de", headers=Headers)
        Response = Connection.getresponse()
        RespHeaders = Response.getheaders()
    except Exception as e:
        print("[plugin:thesubdb] Connection timed out, err: "+str(e))
    Language = "en"

    for k in RespHeaders:
        if k[0].lower() == "content-language":
            Language = k[1].lower()

    if Response.status == 200:
        sublist = list()
        sublist.append({'lang': Language, 'site' : 'opensubtitles.org', 'title' : File+" (hash)", 'domain': 'thesubdb.com', 'data': {'file': File, 'link': "/?action=download&hash="+Hash+"&language=pl,en,pt,ru,hu,it,br,cz,de"}, 'file': File})

        return sublist
    else:
        return False


def get_hash(name):
    readsize = 64 * 1024
    with open(name, 'rb') as f:
        size = os.path.getsize(name)
        data = f.read(readsize)
        f.seek(-readsize, os.SEEK_END)
        data += f.read(readsize)
    return hashlib.md5(data).hexdigest()
