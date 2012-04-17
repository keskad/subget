import httplib, urllib, re, time, struct, os
import gzip
from xmlrpclib import ServerProxy, Error
from xml.dom import minidom

apiUrl = 'http://api.opensubtitles.org/xml-rpc'
userAgent = "Subget"
subgetObject=""
HTTPTimeout = 2
server = ServerProxy(apiUrl)
token = None
Language = 'eng'
LanguageTable = dict()
LanguageTable['eng'] = 'en'
LanguageTable['pol'] = 'pl'
LanguageTable['ita'] = 'it'
LanguageTable['esp'] = 'es'
LanguageTable['cze'] = 'cz'
LanguageTable['dut'] = 'de'
LanguageTable['fre'] = 'fr'
LanguageTable['rus'] = 'ru'
LanguageTable['rum'] = 'ro'
LanguageTable['fin'] = 'fi'
LanguageTable['swe'] = 'se'
LanguageTable['dan'] = 'dk'
LanguageTable['tur'] = 'tr'
LanguageTable['por'] = 'pt'
LanguageTable['bra'] = 'br'
LanguageTable['hun'] = 'hu'
LanguageTable['bra'] = 'br'
LanguageTable['hrv'] = 'hr'
LanguageTable['scc'] = 'sc'

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

    return SavePath

def search_by_keywords(Keywords):
    searchList = []
    token = getLoginToken()
    searchList.append({'query': Keywords})
    subtitlesList = server.SearchSubtitles(token, searchList)
    return parseResults(subtitlesList)

def searchSubtitles(Files):
    global Language, LanguageTable

    searchList = []
    token = getLoginToken()
    fileSizes = dict()

    for File in Files:
        searchList.append({'moviehash': str(hashFile(File)), 'moviebytesize': str(int(os.path.getsize(File)))})
        fileSizes[str(int(os.path.getsize(File)))] = File

    subtitlesList = server.SearchSubtitles(token, searchList)
    return parseResults(subtitlesList, fileSizes)


def parseResults(subtitlesList, fileSizes=False):
    nodes = list()

    if not type(subtitlesList['data']).__name__ == "list":
        print("[plugin:opensubtitles] Got corrupted data, propably server is overloaded.")
        return False

    for subtitle in subtitlesList['data']:
        if not 'SubLanguageID' in subtitle:
            continue

        if str(subtitle['SubLanguageID']) in LanguageTable:
            subtitle['SubLanguageID'] = LanguageTable[subtitle['SubLanguageID']]

        
        if fileSizes != False:
            if not subtitle['MovieByteSize'] in fileSizes:
                continue
            subtitle['File'] = fileSizes[subtitle['MovieByteSize']]
        else:
            subtitle['File'] = "None"

        
        nodes.append({'lang': subtitle['SubLanguageID'], 'site' : 'opensubtitles.org', 'title' : subtitle['SubFileName'], 'domain': 'opensubtitles.org', 'data': {'file': subtitle['File'], 'link': subtitle['SubDownloadLink']}, 'link': subtitle['SubDownloadLink'], 'file': subtitle['SubFileName']})

    return nodes

def getLoginToken():
    global userAgent

    try:
        # Connexion to opensubtitles.org server
        session = server.LogIn('', '', 'en', userAgent)
        if session['status'] != '200 OK':
            print("Cannot estabilish connection to server.")

        return session['token']

    except Exception:
        return True

# http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
def hashFile(path):
    """Produce a hash for a video file : size + 64bit chksum of the first and last 64k (even if they overlap because the file is smaller than 128k)"""
    try:
        longlongformat = 'Q' # unsigned long long little endian
        bytesize = struct.calcsize(longlongformat)
        format = "<%d%s" % (65536//bytesize, longlongformat)
        
        f = open(path, "rb")
        
        filesize = os.fstat(f.fileno()).st_size
        hash = filesize
        
        if filesize < 65536 * 2:
            return "SizeError"
        
        buffer = f.read(65536)
        longlongs = struct.unpack(format, buffer)
        hash += sum(longlongs)
        
        f.seek(-65536, os.SEEK_END)
        buffer = f.read(65536)
        longlongs = struct.unpack(format, buffer)
        hash += sum(longlongs)
        hash &= 0xFFFFFFFFFFFFFFFF
        
        f.close()
        returnedhash = "%016x" % hash
        return returnedhash
    except(IOError): 
        return "IOError"
