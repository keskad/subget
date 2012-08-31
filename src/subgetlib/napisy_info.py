import httplib, urllib, time, os, hashlib, subprocess, re, zipfile, subgetcore
from xml.dom import minidom

####
PluginInfo = { 'Requirements' : { 'OS' : 'All'}, 'API': 2, 'Authors': 'webnull', 'domain': 'napisy.info', 'Description': 'Polish and English napisy.info database' }

class PluginMain(subgetcore.SubgetPlugin):
    ### Specification:
    # http://napisy24.pl/search.php?str=QUERY - searching
    # http://napisy24.pl/download/ID/ - downloading (ZIP format)

    
    LANGLIST = {'polski': 'pl', 'angielski': 'en'}


    def getListOfSubtitles(self, movieRealName, File, resultsClass):
        response, data = self.HTTPGet("napisy.info", "/plugin/SzukajNapisow.php?sid=subget&to="+urllib.quote_plus(movieRealName))
        dom = minidom.parseString(data)

        Items = dom.getElementsByTagName('item')

        for node in Items:
            ID = node.getElementsByTagName('id').item(0)
            LANG = node.getElementsByTagName('language').item(0)

            if ID is not None:
                ID = str(ID.firstChild.data)

            if LANG is not None:
                LANG = str(LANG.firstChild.data)

            resultsClass.append(self.LANGLIST[LANG.lower()], 'napisy.info', str(movieRealName), 'http://napisy.info/napisy_info_'+ID+'.zip', {'file': File, 'url': '/napisy_info_'+ID+'.zip', 'lang': self.LANGLIST[LANG.lower()]}, 'napisy.info', File)

        return True
    
    
    def getMovieName(self, parsedFileName):
      # http://napisy.info/plugin/SzukajTytulow.php?sid=subget&t=Sliders
      response, data = self.HTTPGet("napisy.info", "/plugin/SzukajTytulow.php?sid=subget&t="+urllib.quote_plus(parsedFileName))
      dom = minidom.parseString(data)
      
      titleOriginal =  dom.getElementsByTagName('title.original').item(0)
      if titleOriginal is None:
        return False
      else:
        titleOriginal = titleOriginal.firstChild.data.replace("\n", "")
        return titleOriginal

    def search_by_keywords(self, Keywords):
        resultsClass = subgetcore.SubtitlesList()
        self.check_exists(Keywords, resultsClass)

        return resultsClass
        
    def download_list(self, Files):
        resultsClass = subgetcore.SubtitlesList()
        return self.check_exists_multiple(Files, resultsClass)


    def check_exists_multiple(self, Files, resultsClass):
        if type(Files).__name__ == "list":
            result = False

            for File in Files:
                i = self.check_exists(File, resultsClass)

                if i == True: # if at least one interation was sucessfull
                    result = True

            return resultsClass
        else:
            return check_exists(Files, resultsClass)

    def check_exists(self, File, resultsClass):
        if File is not None:
            movieName = subgetcore.getSearchKeywords(os.path.basename(File))
            movieName = self.getMovieName(movieName)

            if movieName:
                result = self.getListOfSubtitles(movieName, File, resultsClass)

                if result is not None and result:
                    return resultsClass
                else:
                    return {'errInfo': "NOT_FOUND"}
        else:
            return {'errInfo': "NOT_FOUND"}


    def download_by_data(self, File, SavePath):
        try:
            response, subtitleContent = self.HTTPGet("napisy.info", File['url'])
        except Exception as e:
            self.Subget.errorMessage(self.Subget._("Cannot download file")+ " "+File['url']+", "+str(e)+", "+str(response))
            return False

        self.unZip(subtitleContent, SavePath)
        return SavePath
