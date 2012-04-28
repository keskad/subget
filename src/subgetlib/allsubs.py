import urllib, os, zipfile, subgetcore
from xml.dom import minidom

### Specification:
# http://napisy24.pl/search.php?str=QUERY - searching
# http://napisy24.pl/download/ID/ - downloading (ZIP format)

####
PluginInfo = { 'Requirements' : { 'OS' : 'All'}, 'API': 2, 'Authors': 'webnull', 'domain': 'allsubs.org'  }

class PluginMain(subgetcore.SubgetPlugin):

    def getListOfSubtitles(self, movieRealName, File, resultsClass):
        response, data = self.HTTPGet("api.allsubs.org", "/index.php?limit=20&search="+urllib.quote_plus(movieRealName))

        if not response == False or not data:
            return False

        dom = minidom.parseString(data)

        #!!!: this var is unused
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
       
            resultsClass.append(str(Language).lower(), 'allsubs.org', Title+" ("+str(Count)+")", Download, {'file': File, 'url': Download, 'lang': str(Language).lower()}, 'allsubs.org', File)

        return True

    def search_by_keywords(self, Keywords):
        results = subgetcore.SubtitlesList()
        self.check_exists(Keywords, results)
        return results.output()

    def check_exists(self, File, results):
        global subgetObject
        global language

        if File is not None:
            movieName = subgetcore.getSearchKeywords(os.path.basename(File))
             
            if movieName:
                #!!!: this var is unused
                subtitleList = self.getListOfSubtitles(movieName, File, results)
                return True
            else:
                return {'errInfo': "NOT_FOUND"}

        else:
            return {'errInfo': "NOT_FOUND"}


    def download_by_data(self, File, SavePath):
        response, data = self.HTTPGet('www.allsubs.org', File['url'].replace('http://www.allsubs.org', ''))

        if not response or not data:
            return False

        TMPName = self.temporaryPath(File['file'])

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
        else:
            z.extractall(os.path.dirname(SavePath))

        z.close()

        #os.remove(TMPName)
        return SavePath
