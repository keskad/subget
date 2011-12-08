import subgetcore

####
PluginInfo = { 'Requirements' : { 'OS' : 'All'}, 'API': 2, 'Authors': 'webnull', 'domain': 'subswiki.com'  }

class PluginMain(subgetcore.SubgetPlugin):

    def getListOfSubtitles(self, movieRealName, File, resultsClass):
        print("Implment me!")
        return True

    def search_by_keywords(self, Keywords):
        return self.check_exists(Keywords)

    def check_exists(self, File, results):
        return {'errInfo': "NOT_FOUND"}

    def download_by_data(self, File, SavePath):
        print("Implement me!")
        return False
