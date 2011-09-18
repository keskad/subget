#-*- coding: utf-8 -*-
import httplib, urllib, re, time, hashlib, os, gzip, zipfile

import subgetcore
userAgent = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.159 Safari/535.1"
subgetObject=""
HTTPTimeout = 2

PluginInfo = { 'Requirements' : { 'OS' : 'Unix, Linux' }, 'Authors': 'webnull', 'API': 1, 'domain': 'subscene.com' }

def loadSubgetObject(x):
    global subgetObject, SearchMethod, SleepTime
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

    # GET LINK TO ZIP FILE
    try:
        Headers = dict()
        Headers['User-Agent'] = userAgent
        Headers['Host'] = 'subscene.com'
        Headers['Accept-Encoding'] = 'gzip,deflate,sdch'
        Headers['Accept-Language'] = 'pl-PL,pl;q=0.8,en-US;q=0.6,en;q=0.4'
        Headers['Cookie'] = 'subscene_lastsearchwasreleasename=selected; subscene_lastsearchwasfilmtitle=;'
        Headers['Accept-Charset'] = 'ISO-8859-2,utf-8;q=0.7,*;q=0.3'
        Headers['Origin'] = 'http://subscene.com'
        Headers['Cache-Control'] = 'max-age=0'

        conn = httplib.HTTPConnection('www.subscene.com', 80, timeout=HTTPTimeout)
        conn.request("GET", File['link'], headers=Headers)
        response = conn.getresponse()
        data = response.read()
        responseHeaders = response.getheaders()
    except Exception as e:
        print("[plugin:subscene] Connection timed out while trying to get download link, details: "+str(e))
        return False

    if not response.status == 200:
        print("[plugin:thesubdb] Server responsed with "+str(response.status)+" which is incorrect (should be 200)")
        return False

    if os.name == "nt": # WINDOWS "THE PROBLEMATIC OS"
        TMPName = os.path.expanduser("~").replace("\\\\", "/")+"/"+os.path.basename(File['file'])+".tmp"
    else: # UNIX, Linux, *BSD
        TMPName = "/tmp/"+os.path.basename(File['file'])

    # save to temporary directory
    Handler = open(TMPName, "wb")
    Handler.write(data)
    Handler.close()

    # uncompress gzipped HTML file
    f = gzip.open(TMPName, 'rb')
    data = f.read()
    f.close()

    FilmID = re.findall("\<input type\=\"hidden\" name\=\"filmId\" value\=\"([0-9]+)\"", data)
    
    if len(FilmID) == 0:
        print("[plugin:thesubdb] Cannot get filmId")
        return False

    FilmID = FilmID[0]

    ViewState = re.findall("\<input type\=\"hidden\" name\=\"__VIEWSTATE\" id\=\"__VIEWSTATE\" value\=\"([0-9A-Za-z\=\+\_\-\/\\\]+)\"", data)
    ViewState = ViewState[0]

    Type = re.findall("\<input type\=\"hidden\" name\=\"typeId\" value\=\"([A-Za-z]+)\"", data)
    Type = Type[0]

    PreviousPage = re.findall("\<input type\=\"hidden\" name=\"__PREVIOUSPAGE\" id=\"__PREVIOUSPAGE\" value=\"([0-9A-Za-z\=\+\_\-\/\\\]+)\"", data)
    PreviousPage = PreviousPage[0]

    Request = "/"+File['lang']+"/"+File['linkname']+"/subtitle-"+File['subid']+"-dlpath-"+FilmID+"/"+Type+".zipx"

    Cookies = 'subscene_lastsearchwasreleasename=selected; subscene_lastsearchwasfilmtitle=;'

    for k in responseHeaders:
        if k[0] == 'set-cookie':
           Cookies = k[1]


    # DOWNLOAD ZIP FILE
    try:
        Headers = dict()
        Headers['Host'] = 'subscene.com'
        Headers['Connection'] = 'keep-alive'
        Headers['Cache-Control'] = 'max-age=0'
        Headers['Origin'] = 'http://subscene.com'
        Headers['User-Agent'] = userAgent
        Headers['Content-Type'] = 'application/x-www-form-urlencoded'
        Headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        Headers['Referer'] = "http://subscene.com"+File['link']
        Headers['Accept-Encoding'] = 'gzip,deflate,sdch'
        Headers['Accept-Language'] = 'pl-PL,pl;q=0.8,en-US;q=0.6,en;q=0.4'
        Headers['Accept-Charset'] = 'ISO-8859-2,utf-8;q=0.7,*;q=0.3'
        Headers['Cookie'] = Cookies
        Params = urllib.urlencode({'__EVENTTARGET': 's$lc$bcr$downloadLink', '__EVENTARGUMENT': '', '__VIEWSTATE': ViewState, '__PREVIOUSPAGE': PreviousPage, 'subtitleId': File['subid'], 'filmId': FilmID, 'typeId': Type})

        conn = httplib.HTTPConnection('www.subscene.com', 80, timeout=HTTPTimeout)
        conn.request("POST", Request, Params, Headers)
        response = conn.getresponse()
    except Exception as e:
        print("[plugin:subscene] Connection timed out while trying to download ZIP file, details: "+str(e))
        return False

    if not response.status == 200:
        print("[plugin:subscene] Server responsed with "+str(response.status)+", not 200, cannot continue downloading zip file")
        return False

    try:
        Handler = open(TMPName, "wb")
        Handler.write(response.read())
        Handler.close()
    except Exception as e:
        print("[plugin:subscene] Cannot write zipped file to "+TMPName+", Exception: "+str(e))

    if os.path.getsize(TMPName) == 0:
        print("[plugin:subscene] Temporary filesize is zero, stopping.")
        return False

    if os.path.isfile(TMPName):
        if Type == "rar":
            if os.path.isfile("/usr/bin/unrar"):
                os.system("cd "+os.path.dirname(SavePath)+";/usr/bin/unrar e "+TMPName)
            else:
                print("[plugin:subscene] Cannot find /usr/bin/unrar, unpacking of RAR file failed, moving to directory containing movie")
                os.system("mv "+TMPName+" "+SavePath+".rar")
        elif Type == "zip":
            try:
                # one of reasons why you should'nt use Subget on root account
                Handler = zipfile.ZipFile(TMPName)
                Handler.extractall(os.path.dirname(SavePath))
                Handler.close()
            except Exception as e:
                print("[plugin:subscene] Failed unpacking ZIP archive, exception: "+str(e))
        else:
            print("[plugin:subscene] Unknown archive format, moving to movie directory")
            os.system("mv "+TMPName+" "+SavePath+".rar")


    return True

def search_by_keywords(Keywords):
    return check_exists(Keywords)

def convertToQuery(FileName):
    FileName = FileName.replace("  ", " ") # Fix double spaces
    FileName = FileName.replace(" ", "+") # Replace single spaces with "+"
    return FileName

def check_exists(File):
    global userAgent, SearchMethod, SleepTime

    Headers = dict()
    Headers['User-Agent'] = userAgent
    langList = [ 'en', 'pl', 'pt', 'ru', 'hu', 'it', 'br', 'cz', 'de' ]

    try:
        Connection = httplib.HTTPConnection('subscene.com', 80, timeout=HTTPTimeout)
        Connection.request("GET", "/s.aspx?q="+convertToQuery(subgetcore.getSearchKeywords(File, True)), headers=Headers)
        Response = Connection.getresponse()
        RespHeaders = Response.getheaders()
    except Exception as e:
        print("[plugin:subscene] Connection timed out, err: "+str(e))

    plainResponse = Response.read()

    if "No results found." in plainResponse:
        print("[plugin:subscene] No any matches in database found")
        return False


    if Response.status == 200:
        #<a href="/english/Ganz-The-Perfect-Answer-Gantz-Part-2/subtitle-481694.aspx"
        plainResponse = plainResponse.replace("\r", " ")
        plainResponse = plainResponse.replace("\n", " ")
        plainResponse = plainResponse.replace("\t", " ")
        subsFound = re.findall("\<a class\=\"a1\" href\=\"\/([a-z-A-Z\-]+)/([A-Za-z\_\-0-9]+)/subtitle-([0-9]+)\.aspx\" title=\"([A-Za-z_\-\ 0-9\&\^\%\$\#\@\!\*\(\)\+\=]+)\"\>", plainResponse)

        # No subtitles found!
        if len(subsFound) == 0:
            return False

        sublist = list()

        for sub in subsFound:
            try:
                Language = subgetcore.languageFromName(sub[0])
                LinkName = sub[1]
                ID = str(sub[2])

                title = re.findall("\<span id\=\"r"+ID+"\"\>([A-Za-z0-9\_\-\&\^\%\$\#\@\!\&\(\)\+\=\:\;\'\\\"\ ĘęÓóĄąŚśŁłŻżŹźĆćŃń\.\,]+)\<\/span\>", plainResponse)

                if len(title) > 0:
                    title = title[0]
                else:
                    title = LinkName

                # append to list
                sublist.append({'lang': Language, 'site' : 'subscene.com', 'title' : title, 'domain': 'subscene.com', 'data': {'file': File, 'link': "/"+sub[0]+"/"+sub[1]+"/subtitle-"+sub[2]+".aspx", 'lang': sub[0], 'linkname': sub[1], 'subid': ID}, 'file': File})

            except Exception as e:
                print("[plugin:subscene] Exception catched, "+str(e))

        return sublist
    else:
        print("[plugin:subscene] Not found for "+File+", server returned code \""+str(Response.status)+"\"")
        return False
