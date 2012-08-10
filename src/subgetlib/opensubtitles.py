import urllib, time, os, hashlib, subprocess, re, zipfile, subgetcore
import httplib, struct
import gzip
from xmlrpclib import ServerProxy

####
PluginInfo = { 'Requirements' : { 'OS' : 'All'}, 'API': 2, 'Authors': 'webnull', 'domain': 'opensubtitles24.org' }
language = "PL"

class PluginMain(subgetcore.SubgetPlugin):
    ### Specification:
    # http://napisy24.pl/search.php?str=QUERY - searching
    # http://napisy24.pl/download/ID/ - downloading (ZIP format)

    apiUrl = 'http://api.opensubtitles.org/xml-rpc'
    userAgent = "Subget"
    subgetObject=""
    HTTPTimeout = 2
    server = ServerProxy(apiUrl)
    token = None
    Language = 'eng'
    LanguageTable = {
        'eng': 'en',
        'pol': 'pl',
        'ita': 'it',
        'esp': 'es',
        'cze': 'cz',
        'dut': 'de',
        'fre': 'fr',
        'rus': 'ru',
        'rum': 'ro',
        'fin': 'fi',
        'swe': 'se',
        'dan': 'dk',
        'tur': 'tr',
        'por': 'pt',
        'bra': 'br',
        'hun': 'hu',
        'bra': 'br',
        'hrv': 'hr',
        'scc': 'sc',
    }

    def parseResults(self, subtitlesList, resultsClass, fileSizes=False):
        if not isinstance(subtitlesList['data'], list):
            self.error("[plugin:opensubtitles] Got corrupted data, propably server is overloaded.")
            return False

        for subtitle in subtitlesList['data']:
            if not 'SubLanguageID' in subtitle:
                continue

            print subtitle

            if str(subtitle['SubLanguageID']) in self.LanguageTable:
                subtitle['SubLanguageID'] = self.LanguageTable[subtitle['SubLanguageID'].lower()]

            
            if fileSizes:
                if not subtitle['MovieByteSize'] in fileSizes:
                    continue

                subtitle['File'] = fileSizes[subtitle['MovieByteSize']]
            else:
                subtitle['File'] = "None"

            resultsClass.append(str(subtitle['SubLanguageID']).lower(), 'opensubtitles.org', str(subtitle['SubFileName']), subtitle['SubDownloadLink'], {'file': subtitle['File'], 'link': subtitle['SubDownloadLink']}, 'opensubtitles.org', subtitle['SubFileName'])
        return resultsClass


    def download_list(self, Files):
        resultsClass = subgetcore.SubtitlesList()
        return self.searchSubtitles(Files, resultsClass)

    def searchSubtitles(self, Files, resultsClass):
        searchList = []
        token = self.getLoginToken()
        fileSizes = dict()

        for File in Files:
            searchList.append({'moviehash': str(self.hashFile(File)), 'moviebytesize': str(int(os.path.getsize(File)))})
            fileSizes[str(int(os.path.getsize(File)))] = File

        subtitlesList = self.server.SearchSubtitles(token, searchList)
        return self.parseResults(subtitlesList, resultsClass, fileSizes)

    def search_by_keywords(self, Keywords):
        resultsClass = subgetcore.SubtitlesList()

        searchList = []
        token = self.getLoginToken()
        searchList.append({'query': Keywords})
        subtitlesList = self.server.SearchSubtitles(token, searchList)
        return self.parseResults(subtitlesList, resultsClass)


    def download_by_data(self, File, SavePath):
        response, data = self.HTTPGet('www.opensubtitles.org', File['link'].replace("http://www.opensubtitles.org", ""))

        #if os.name == "nt": # WINDOWS "THE PROBLEMATIC OS"
        #    TMPName = os.path.expanduser("~").replace("\\\\", "/")+"/"+os.path.basename(File['file'])+".tmp"
        #else: # UNIX, Linux, *BSD
        #    TMPName = "/tmp/"+os.path.basename(File['file'])

        try:
            self.unSevenZip(data, SavePath.replace(".txt.txt", ".txt"))
            #os.rm(TMPName)
        except Exception as e:
            self.error("Exception: "+str(e))

        return SavePath

    # http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
    def hashFile(self, path):
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

    def getLoginToken(self):
        try:
            # Connexion to opensubtitles.org server
            session = self.server.LogIn('', '', 'en', self.userAgent)
            if session['status'] != '200 OK':
                print("Cannot estabilish connection to self.server.")

            return session['token']

        except Exception:
            return True
