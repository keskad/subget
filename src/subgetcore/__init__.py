""" Subget core library """

import filemanagers, videoplayers, subgetbus, os, re

# fixes episode or season number for TV series eg. 1x3 => 01x03
def addZero(number):
    if len(number) == 1:
        return "0"+str(number)
    else:
        return number

def getSearchKeywords(File):
    Replacements = [ 'HDTVRIP', 'HDTV', 'CTU', 'XVID', 'crimson', 'amiable', 'lol', 'tvrip', 'fov', '720p', '360p', '1080p', 'hd', 'fullhd', 'sfm', 'bluray', 'x264', 'web-dl', 'aac20' ]

    OriginalFileName = File
    Splittext = os.path.splitext(File)
    File = Splittext[0]

    File = File.replace(".", " ").replace("[", " ").replace("]", " ").replace("-", " ").replace("_", " ")

    # replace all popular names
    for k in Replacements:
        Expr = re.compile(k, re.IGNORECASE)
        File = Expr.sub('', File)

    SearchTV1 = re.findall("([A-Za-z0-9- ]+)(.?)S([0-9]+)E([0-9]+)(.*)", File, re.IGNORECASE)

    # if its in TV series format eg. S01E02
    if len(SearchTV1) > 0:
            return ""+SearchTV1[0][0]+" "+addZero(SearchTV1[0][2])+"x"+addZero(SearchTV1[0][3])
                   # title              # season           # episode
    else:
        # try luck again, now search in TV series format #2 eg. 01x02
        SearchTV1 = re.findall("([A-Za-z0-9 ]+)(.?)([0-9]+)x([0-9]+)(.*)", File, re.IGNORECASE)

        if len(SearchTV1) > 0:
            Zero = SearchTV1[0][0].replace(" 0 ", "")

            return ""+Zero+" "+addZero(SearchTV1[0][2])+"x"+addZero(SearchTV1[0][3])
                   # title              # season           # episode
        else: # if not a TV show - just a movie release
            SearchTV1 = re.findall("([A-Za-z0-9 ]+)(.?)", File, re.IGNORECASE)

            # if its ripped movie release
            if len(SearchTV1) > 0:
                return SearchTV1[0][0] # print only title
            else: # if its unidentified movie type
                return False
