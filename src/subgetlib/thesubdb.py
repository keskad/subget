import httplib, time, hashlib, os

apiUrl = 'http://api.opensubtitles.org/xml-rpc'
userAgent = "SubDB/1.0 (Subget/1.0; http://github.com/webnull/subget)"
subgetObject=""
HTTPTimeout = 2
Language = 'en'
SleepTime = None
SearchMethod = None

PluginInfo = { 'Requirements' : { 'OS' : 'All' }, 'Authors': 'webnull', 'API': 1, 'domain': 'thesubdb.com' }

def loadSubgetObject(x):
    global subgetObject, SearchMethod, SleepTime
    subgetObject = x

    if "plugins" in subgetObject.Config:
        if "timeout" in subgetObject.Config['plugins']:
            HTTPTimeout = subgetObject.Config['plugins']['timeout']

    SleepTime = subgetObject.configGetKey('plugin:thesubdb', 'sleep')

    if SleepTime == False:
        SleepTime = 0.2 # 200 ms between deep search
        if not "plugin:thesubdb" in subgetObject.Config:
            subgetObject.Config['plugin:thesubdb'] = dict()

        subgetObject.Config['plugin:thesubdb']['sleep'] = "0.2"

    else:
        try:
            SleepTime = float(subgetObject.configGetKey('plugin:thesubdb', 'sleep'))
        except Exception:
            SleepTime = 0.2
            if not "plugin:thesubdb" in subgetObject.Config:
                subgetObject.Config['plugin:thesubdb'] = dict()

            subgetObject.Config['plugin:thesubdb']['sleep'] = "0.2"
            

    SearchMethod = subgetObject.configGetKey("plugin:thesubdb", "search_method")
    if not SearchMethod == "simple" and not SearchMethod == "deeply":
        SearchMethod = "simple"
        subgetObject.Config['plugin:thesubdb']['search_method'] = 'simple' # simple or deeply



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
        Headers = {
            'User-Agent': userAgent,
        }
        conn = httplib.HTTPConnection('api.thesubdb.com', 80, timeout=HTTPTimeout)
        conn.request("GET", File['link'], headers=Headers)
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
    global userAgent, SearchMethod, SleepTime

    Hash = get_hash(File)

    Headers = {
        'User-Agent': userAgent,
    }
    langList = [ 'en', 'pl', 'pt', 'ru', 'hu', 'it', 'br', 'cz', 'de' ]

    if SearchMethod == 'simple':
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
            return ({'lang': Language, 'site' : 'thesubdb.com', 'title' : os.path.basename(File)+" (hash)", 'domain': 'thesubdb.com', 'data': {'file': File, 'link': "/?action=download&hash="+Hash+"&language=pl,en,pt,ru,hu,it,br,cz,de"}, 'file': File})
        else:
            print("[plugin:thesubdb] Not found for "+File+" in "+Language+" language.")
            return False

    elif SearchMethod == 'deeply':
        sublist = list()
        Language = "?"

        for lang in langList:
            time.sleep(SleepTime)
            try:
                Connection = httplib.HTTPConnection('api.thesubdb.com', 80, timeout=HTTPTimeout)
                Connection.request("GET", "/?action=download&hash="+Hash+"&language="+lang, headers=Headers)
                Response = Connection.getresponse()
                RespHeaders = Response.getheaders()
            except Exception as e:
                print("[plugin:thesubdb] Connection timed out, err: "+str(e))

            for k in RespHeaders:
                if k[0].lower() == "content-language":
                    Language = k[1].lower()

            if Response.status == 200:
                sublist.append({'lang': Language, 'site' : 'thesubdb.com', 'title' : os.path.basename(File)+" (hash)", 'domain': 'thesubdb.com', 'data': {'file': File, 'link': "/?action=download&hash="+Hash+"&language="+lang}, 'file': File})
            else:
                print("[plugin:thesubdb] Not found for "+File+" in "+lang+" language.")

        if not sublist:
            return False

        return sublist
    else:
        print("[plugin:thesubdb] Warning: Wrong method in config plugin:thesubdb->search_method (available methods: simple, deeply) Selected: "+str(SearchMethod))
        return False


def get_hash(name):
    readsize = 64 * 1024
    with open(name, 'rb') as f:
        data = f.read(readsize)
        f.seek(-readsize, os.SEEK_END)
        data += f.read(readsize)
    return hashlib.md5(data).hexdigest()
