import httplib, urllib, time, os, hashlib, subprocess, re, zipfile, subgetcore

####
PluginInfo = { 'Requirements' : { 'OS' : 'All'}, 'API': 2, 'Authors': 'webnull', 'domain': 'napisy24.pl', 'Description': 'Polish napisy24.pl and napisy.org archive' }
language = "PL"

class PluginMain(subgetcore.SubgetPlugin):
    ### Specification:
    # http://napisy24.pl/search.php?str=QUERY - searching
    # http://napisy24.pl/download/ID/ - downloading (ZIP format)


    def getListOfSubtitles(self, movieRealName, File, resultsClass):
        response, data = self.HTTPGet('napisy24.pl', "/search.php?str="+urllib.quote_plus(movieRealName))

        if data == False:
            return False

        nodes = list()
        data = data.replace("\t", " ").replace("\n", "")
        dataAreaStart = data.find("<div id=\"mainLevel\">")
        dataAreaStop = data.find("alt=\"Uaktualnione\"")
        data = self.removeNonAscii(data)
        dataCutedOff = data[dataAreaStart:dataAreaStop]

        currentCount = re.findall("<a href=\"/\">napisy24.pl</a> > Znaleziono ([0-9]+) film", dataCutedOff)

        if int(currentCount[0]):

            Items = dataCutedOff.split("<a href=\"javascript:void(0);\" onclick=\"javascript:showInfo('")

            for Item in Items:
                ID = re.findall("<a href=\"/download/([0-9]+)/\">", Item)
            
                if ID:
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
                        if resultsLanguage[0]:
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

                    resultsClass.append(str(resultsLanguage).lower(), 'napisy24.pl', str(Name), 'http://napisy24.pl/download/'+str(ID[0])+'/', {'file': File, 'headers': response.getheaders(), 'id': str(ID[0]), 'type': 'napisy24.pl', 'search_string': urllib.quote_plus(movieRealName), 'lang': str(resultsLanguage).lower()}, 'napisy24.pl', File)


        archiveCount = re.findall("<a href=\"http://napisy.org\">Napisy.org</a> > Znaleziono ([0-9]+) film", dataCutedOff)

        if int(archiveCount[0]) == 0:
            return nodes

        # napisy.org archive support
        Archives = dataCutedOff.split("href=\"/download/archiwum/")

        #???: will this work as expected: exclude first item from Archives
        for Archive in Archives[1:]:
            End = Archive.split("png\" width=\"17\" height=\"17\" alt=\"")

            if len(End) > 5:
               continue

            Number = re.findall("([0-9]+)/\"\>", End[0])
            ID = Number[0]

            Name = re.findall("<td( | class=\"dark\")>([A-Za.-z _-]+)<\/td>", End[0])

            if not Name:
                continue

            Name = Name[0][1]
            Language = re.findall("<img src=\"\/images\/ico_flag_([A-Za-z]+)_", End[0])
            Language = Language[0]

            resultsClass.append(str(Language).lower(), 'napisy.org', str(Name), 'http://napisy24.pl/download/archiwum/'+str(ID)+'/', {'file': File, 'headers': response.getheaders(), 'id': str(ID), 'type': 'napisy.org', 'search_string': urllib.quote_plus(movieRealName), 'lang': str(Language).lower()}, 'napisy.org', File)

        return True

    def search_by_keywords(self, Keywords):
        self.Subget.Logging.output("napisy24.pl is temporary disabled because of required authentication changes", "debug", False)
        return {'errInfo': "NOT_FOUND"}

        resultsClass = subgetcore.SubtitlesList()
        self.check_exists(Keywords, resultsClass)

        return resultsClass

    def check_exists(self, File, resultsClass):
        self.Subget.Logging.output("napisy24.pl is temporary disabled because of required authentication changes", "debug", False)
        return {'errInfo': "NOT_FOUND"}

        if File is not None:
            movieName = subgetcore.getSearchKeywords(os.path.basename(File))

            if movieName:
                subtitleList = self.getListOfSubtitles(movieName, File, resultsClass)
                return True
            else:
                # This isn't a constant, this is a string-error code that subget recognize
                return {'errInfo': "NOT_FOUND"}

        else:
            return {'errInfo': "NOT_FOUND"}


    def download_by_data(self, File, SavePath):
        Cookies = None

        # Search for cookies
        for Item in File['headers']:
            if str(Item[0]).lower() == "set-cookie":
                Cookies = Item[1]
                break

        if Cookies is None:
            return {'errInfo': "NOT_FOUND"}

        PHPSESSID = re.findall('PHPSESSID=([A-Za-z-_0-9]+);', Cookies)

        Headers = {'Cookie': 'PHPSESSID='+PHPSESSID[0]+'; pobierzDotacje=1;', 'Referer': 'http://napisy24.pl/search.php?str='+File['search_string'], 'User-agent': 'Mozilla/5.0 (X11; U; Gentoo Linux; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/14.0.341.0' }

        if File['type'] == 'napisy.org':
            Dir = "/download/archiwum/"+File['id']+"/"
        else:
            Dir = "/download/"+File['id']+"/"

        response, data = self.HTTPGet('napisy24.pl', Dir, Headers)
       
        self.unZip(data, SavePath)

        return SavePath
