import httplib, urllib, time, os, hashlib

####
PluginInfo = { 'Requirements' : { 'OS' : 'All', 'Authors': 'webnull', 'Packages:' : ( 'p7zip' ), 'API': 1 } }
language = "PL"

apiUrl = "http://napiprojekt.pl/unit_napisy/dl.php"
retries=0 # Retry the connection if failed
maxRetries=8
errInfo=""
subgetObject=""

def loadSubgetObject(x):
    global subgetObject

    subgetObject = x

# thanks to gim,krzynio,dosiu,hash 2oo8 for this function
def f(z):
    idx = [ 0xe, 0x3,  0x6, 0x8, 0x2 ]
    mul = [   2,   2,    5,   4,   3 ]
    add = [   0, 0xd, 0x10, 0xb, 0x5 ]

    b = []
    for i in xrange(len(idx)):
        a = add[i]
        m = mul[i]
        i = idx[i]

        t = a + int(z[i], 16)
        v = int(z[t:t+2], 16)
        b.append( ("%x" % (v*m))[-1] )

    return ''.join(b)

def download_list(files, query=''):
    results = list()

    for File in files:
        results.append(check_exists(File))

    return results


# download first best subtitle
def download_quick(files, query=''):
    results = list()
    for File in files:
        results.append(get_subtitle(File))


def check_exists(File):
    global subgetObject
    print "TEST:"
    print subgetObject.subgetOSPath
    global language

    d = hashlib.md5(open(File).read(10485760)).hexdigest()

    if os.name == "posix":
       os.name = "Linux"
    
    # RECEIVE DATA
    subtitleUrl = "?l="+language.upper()+"&f="+d+"&t="+f(d)+"&v=other&kolejka=false&nick=&pass=&napios="+os.name

    try:
       conn = httplib.HTTPConnection('napiprojekt.pl', 80, timeout=2)
       conn.request("GET", "/unit_napisy/dl.php"+subtitleUrl)
       response = conn.getresponse()
       subtitleZipped = response.read(5)
    except Exception:
       print "[plugin:napiprojekt] Connection timed out"
       return False

    if len(subtitleZipped) > 0 and subtitleZipped != "NPc0":
        Result = list()
        Result.append({'lang': language.lower(), 'site' : 'napiprojekt.pl', 'title' : os.path.basename(File)[:-3]+"txt", 'url' : subtitleUrl, 'data': {'file': File, 'lang': language}, 'domain': 'napiprojekt.pl', 'file': File})
        return Result
    else:
        return {'errInfo': "NOT_FOUND"}


def get_subtitle(File):
    global language

    if File[0:4] == "http":
        subtitleZipped = urllib.urlopen(File).read()
    else:
        d = hashlib.md5(open(File).read(10485760)).hexdigest()

        if os.name == "posix":
          os.name = "Linux"

        # RECEIVE DATA
        subtitleUrl = "?l="+language.upper()+"&f="+d+"&t="+f(d)+"&v=other&kolejka=false&nick=&pass=&napios="+os.name

        try:
            conn = httplib.HTTPConnection('napiprojekt.pl', 80, timeout=2)
            conn.request("GET", "/unit_napisy/dl.php"+subtitleUrl)
            response = conn.getresponse()
            subtitleZipped = response.read()
        except Exception:
            print "[plugin:napiprojekt] Connection timed out"
            return False

    if len(subtitleZipped) > 0 and subtitleZipped != "NPc0": 
        Handler = open(File+".7z", "w")
        Handler.write(subtitleZipped)
        Handler.close()

        # use 7zip to unpack subtitles
        if os.name == "nt":
            os.system("/usr/bin/7z x -y -so -piBlm8NTigvru0Jr0 \""+File+".7z\" 2>/dev/null > \""+File+".txt\"")
        else:
            os.system(x.subgetOSPath+"/7za.exe x -y -so -piBlm8NTigvru0Jr0 \""+File+".7z\" > \""+File+".txt\"")

        os.remove(File+".7z")
        return File+".7z"
    else:
        return {'errInfo': "NOT_FOUND"}

def download_by_data(File, SavePath):
    language = File['lang']

    if File['file'][0:4] == "http":
        subtitleZipped = urllib.urlopen(File).read()
    else:
        File = File['file']

        d = hashlib.md5(open(File).read(10485760)).hexdigest()

        if os.name == "posix":
          os.name = "Linux"

        # RECEIVE DATA
        try:
            subtitleUrl = "?l="+language.upper()+"&f="+d+"&t="+f(d)+"&v=other&kolejka=false&nick=&pass=&napios="+os.name
            conn = httplib.HTTPConnection('napiprojekt.pl', 80, timeout=2)
            conn.request("GET", "/unit_napisy/dl.php"+subtitleUrl)
            response = conn.getresponse()
            subtitleZipped = response.read()
        except Exception:
            print "[plugin:napiprojekt] Connection timed out"
            return False

    if len(subtitleZipped) > 0 and subtitleZipped != "NPc0": 
        Handler = open(File+".7z", "w")
        Handler.write(subtitleZipped)
        Handler.close()

        # use 7zip to unpack subtitles
        if os.name == "nt":
            os.system("/usr/bin/7z x -y -so -piBlm8NTigvru0Jr0 \""+File+".7z\" 2>/dev/null > \""+File+".txt\"")
        else:
            os.system(x.subgetOSPath+"/7za.exe x -y -so -piBlm8NTigvru0Jr0 \""+File+".7z\" > \""+File+".txt\"")

        os.remove(File+".7z")
        return SavePath
    else:
        return {'errInfo': "NOT_FOUND"}
        

