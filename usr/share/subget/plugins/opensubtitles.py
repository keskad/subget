import pycurl, httplib, urllib, StringIO, re, time, struct, os
from xml.dom import minidom

apiUrl = "http://api.opensubtitles.org/xml-rpc"
userAgent = "OS Test User Agent"
loginToken=""
retries=0 # Retry the connection if failed
maxRetries=8
errInfo=""

PluginInfo = { 'Requirements' : { 'OS' : 'Unix' }, 'Authors': 'webnull' }

def download_list(files, language='', query=''):
    return
    global loginToken

    # get login token, connection can be retried here "maxRetries" times
    if loginToken == "":
        getLoginToken() 
    
    for File in files:
        searchSubtitles(File, language, query)

def download_quick(files):
    return

def searchSubtitles(File, language, query):
    global loginToken

    print "Got file name: "+File

    XMLData = """<?xml version="1.0"?>
<methodCall>
<methodName>SearchSubtitles</methodName>
<params>
  <param>
   <value><string>"""+loginToken+"""</string></value>
  </param>
  <param>
   <value>
    <array>
     <data>
      <value>
       <struct>"""

    if language != "":
        XMLData += "<member><name>sublanguageid</name><value><string>"+language+"</string></value></member>"

    if query != "":
        XMLData += "<member><name>query</name><value><string>"+query+"</string></value></member>"
    else:
        XMLData += "<member><name>moviehash</name><value><string>"+hashFile(File)+"</string></value></member>" # SEARCH BY MOVIE HASH
        #XMLData += "<member><name>moviebytesize</name><value><string>"+str(os.path.getsize(File))+"</string></value></member>" # SEARCH BY FILE SIZE


    XMLData += """</struct>
      </value>
     </data>
    </array>
   </value>
  </param>
</params>
</methodCall>"""


    print "Sending"
    print XMLData
    print ""
    

    # PREPARE HEADERS FOR CONNECTION
    sendHeaders = {
         'Content-Length': str(len(XMLData)), 
         'User-Agent': userAgent, 
         'Content-Type': 'text/xml',
         'Accept-Charset': 'UTF-8,ISO-8859-1,US-ASCII'
                  }

    # CONNECT TO API
    conn = httplib.HTTPConnection('api.opensubtitles.org')

    # SEND DATA
    conn.request("POST", "/xml-rpc", XMLData, sendHeaders)
    response = conn.getresponse()
    data = response.read()

    print "Receiving"
    print data
    


def getLoginToken():
    global apiUrl, userAgent, loginToken, retries, maxRetries

    #print "getLoginToken()"
    XMLData = """<?xml version="1.0"?>
<methodCall>
<methodName>LogIn</methodName>
<params><param>
<value><string></string></value>
</param>
<param>
<value><string></string></value>
</param>
<param>
<value><string></string></value>
</param>
<param>
<value><string>"""+userAgent+"""</string></value>
</param></params>
</methodCall>"""

    sendHeaders = {
         'Content-Length': str(len(XMLData)), 
         'User-Agent': userAgent, 
         'Content-Type': 'text/xml',
         'Accept-Charset': 'UTF-8,ISO-8859-1,US-ASCII'
                  }

    conn = httplib.HTTPConnection('api.opensubtitles.org')
    conn.request("POST", "/xml-rpc", XMLData, sendHeaders)
    response = conn.getresponse()
    data = response.read()

    if re.findall("Error 503 Service Unavailable", data):
        if retries < (maxRetries+1):
            retries = (retries+1)
            time.sleep(1)
            return getLoginToken()
        else:
            errInfo = "Cannot connect to Opensubtitles.org while trying to grab session token (503 Service Unavailable). Reconnected "+str(maxRetries)+" times."
            return

    # initialize parser
    dom = minidom.parseString(data)

    # get all "member" tags
    Members = dom.getElementsByTagName('member')

    # search token in "member" tags
    for node in Members:
        Name = node.getElementsByTagName('name').item(0).firstChild.data
        ValueString = node.getElementsByTagName('value').item(0).getElementsByTagName('string').item(0)
        Value = ""

        if Value != None:
            Value = ValueString.firstChild.data
        else:
            continue
            #ValueDouble = node.getElementsByTagName('value').item(0).getElementsByTagName('double').item(0) # DOUBLE TYPE VALUES PARSING, NOT TESTED

            #if ValueDouble != None:
                #Value = ValueDouble.firstChild.data

        if Name == "token":
            loginToken = Value
            break
    
    # retry the connection "maxRetries" times if something will fail
    if loginToken == "":
        if retries < (maxRetries+1):
            retries = (retries+1)
            time.sleep(1)
            getLoginToken()
        else:
            errInfo = "Cannot connect to Opensubtitles.org while trying to grab session token. Reconnected "+str(maxRetries)+" times."

    return loginToken

# http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
def hashFile(name): 
      try: 
                 
                longlongformat = 'q'  # long long 
                bytesize = struct.calcsize(longlongformat) 
                    
                f = open(name, "rb") 
                    
                filesize = os.path.getsize(name) 
                hash = filesize 
                    
                if filesize < 65536 * 2: 
                       return "SizeError" 
                 
                for x in range(65536/bytesize): 
                        buffer = f.read(bytesize) 
                        (l_value,)= struct.unpack(longlongformat, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  
                         
    
                f.seek(max(0,filesize-65536),0) 
                for x in range(65536/bytesize): 
                        buffer = f.read(bytesize) 
                        (l_value,)= struct.unpack(longlongformat, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF 
                 
                f.close() 
                returnedhash =  "%016x" % hash 
                return returnedhash 
    
      except(IOError): 
                return "IOError"
