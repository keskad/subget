import urllib, zipfile, subgetcore, httplib, os, hashlib, subprocess

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

####
PluginInfo = { 'Requirements' : { 'OS' : 'All'}, 'API': 2, 'Authors': 'webnull', 'domain': 'napiprojekt.pl'  }

class PluginMain(subgetcore.SubgetPlugin):
    language = "PL"

    def check_exists(self, File, resultsClass):
        if File is None:
            return {'errInfo': "NOT_FOUND"}

        d = hashlib.md5(open(File, "rb").read(10485760)).hexdigest()
        Dir = "/unit_napisy/dl.php?l="+self.language.upper()+"&f="+d+"&t="+f(d)+"&v=other&kolejka=false&nick=&pass=&napios=Linux"

        # HTTP Request
        response, subtitleZipped = self.HTTPGet('napiprojekt.pl', Dir)

        # Appending to list
        if subtitleZipped and subtitleZipped != "NPc0":
            resultsClass.append(self.language.lower(), 'napiprojekt', os.path.basename(File), Dir, {'file': File, 'url': 'http://napiprojekt.pl'+Dir}, 'napiprojekt.pl', File)
            return True
        else:
            return {'errInfo': "NOT_FOUND"}



    def download_by_data(self, File, SavePath):
        # method of downloading subtitles - from already parsed URL (with calculated and fixed md5 sums)
        if File['file'][0:7] == "http://":
            subtitleZipped = urllib.urlopen(File).read()

        else: # calculating sums
            File = File['file']
            d = hashlib.md5(open(File, "rb").read(10485760)).hexdigest()
            response, subtitleZipped = self.HTTPGet('napiprojekt.pl', "/unit_napisy/dl.php?l="+self.language.upper()+"&f="+d+"&t="+f(d)+"&v=other&kolejka=false&nick=&pass=&napios=Linux")

        if subtitleZipped and subtitleZipped != "NPc0":
            self.Subget.Logging.output("napiprojekt subtitles -> unSevenZipping...", "debug", False)
            return self.unSevenZip(subtitleZipped, SavePath)
        else:
            return {'errInfo': "NOT_FOUND"}
