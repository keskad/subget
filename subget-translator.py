#!/usr/bin/env python
import getopt, os, sys, time, hashlib

class SubgetTranlator:
    languages = {'pl': 'pl_PL.UTF-8', 'da': 'da_DK.ISO-8859-1'}
    lang = ""
    editor = ""
    lastsum = ""
    user = ""
    prefix = ""
    lastHash = ""
    runSubget = False
    
    def usage(self):
        return "Usage: subget-translator -[GNU option] --[long GNU option]\n\nOptions:\n--help, -h (this message)\n--list, -l (list avaliable languages)\n--set, -s (set language from list, eg. pl or da)\n--editor, -e (editor name to use, eg. geany or gedit, optional)\n--user, -u (run Subget as other user)\n--prefix, -p (is Subget placed in other directory? example of prefix: . for current directory\n--run, -r (run Subget automaticaly after compilation)"
    
    def setLanguage(self, lang):
        if lang in self.languages:
            self.lang = lang
        else:
            print("Invalid language selected, try --list for avaliable languages.")
            sys.exit(1)
            
    def setPrefix(self, prefix):
        if os.path.isfile(prefix+"/usr/bin/subget"):
            self.prefix = prefix
        else:
            print("Warning: cannot find "+prefix+"/usr/bin/subget, disabling prefix")
            
    def setUser(self, user):
        self.user = "su "+user+" -c"
            
    def setEditor(self, editor):
        if os.path.isfile(editor):
            self.editor = editor
        elif os.path.isfile("/usr/bin/"+editor):
            self.editor = "/usr/bin/"+editor
        elif os.path.isfile("/usr/local/bin/"+editor):
            self.editor = "/usr/local/bin/"+editor
        else:
            print("Cannot find editor executable")
            sys.exit(1)
        
    
    def listLanguages(self):
        print("Avaliable languages: \n")
        
        for i in self.languages:
            print("["+i+"] "+self.languages[i])
    
    def main(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hlre:u:p:s:", ["help", "list", "set=", "editor=", "user=", 'prefix=', 'run'])
        except getopt.GetoptError as err:
            print(self.usage())
            sys.exit(2)
            
        for o, a in opts:
            if o in ('-h', '--help'):
                print(self.usage())
                sys.exit(0)
                    
            if o in ('-l', '--list'):
                self.listLanguages()
                sys.exit(0)
                
            if o in ('--set', '-s'):
                self.setLanguage(a)

            if o in ('--editor', '-e'):
                self.setEditor(a)
            
            if o in ('--user', '-u'):
                self.setUser(a)
            
            if o in ('--prefix', '-p'):
                self.setPrefix(a)
                
            if o in ('--run', '-r'):
                self.runSubget = True
                
        if self.lang == "":
            print("No language selected, use --list to check avaliable languages and -s/--set (set language for edition, --list for list avaliable options)")
            print self.usage()
            sys.exit(1)
                
        self.mainLoop()
        
    def checkFile(self, firstTime=False):
        try:
            f = open(self.prefix+"/usr/share/subget/locale/"+self.lang+"/LC_MESSAGES/subget-src.po", "r")
            m = hashlib.md5()
            m.update(f.read())
            x = m.digest()
            f.close()
        except Exception as e:
            print("Cannot check locale file, please check permissions. "+self.prefix+"/usr/share/subget/locale/"+self.lang+"/LC_MESSAGES/subget-src.po")
            sys.exit(1)
            
        if firstTime == True:
            self.lastHash = x
            return True
        else:
            if x == self.lastHash:
                return True
            else:
                self.lastHash = x
                return False
            
    def compile(self, i):
        os.system("msgfmt "+self.prefix+"/usr/share/subget/locale/"+self.lang+"/LC_MESSAGES/subget-src.po -o "+self.prefix+"/usr/share/subget/locale/"+self.lang+"/LC_MESSAGES/subget.mo")
        print("["+str(i)+"] Commiting changes... please restart application.")

    def runTest(self):
        print("export LANG=\""+self.languages[self.lang]+"\"")
        os.putenv("LANG", self.languages[self.lang]) # set language
        
        cmd = self.user+" "+self.prefix+"/usr/bin/subget &> /dev/null &"
        print(cmd)
        os.system(cmd) # run subget

    def mainLoop(self):
        print("Language: "+self.lang)
        
        if self.editor is not "":
            print("Editor: "+self.editor)
            os.system(self.editor+" "+self.prefix+"/usr/share/subget/locale/"+self.lang+"/LC_MESSAGES/subget-src.po &")
        
        i = 0
        self.checkFile(True)
        
        while True:
            i=i+1
            
            check = self.checkFile()
            
            if check == False:
                self.compile(i)
                
                if self.runSubget == True:
                    self.runTest()
            
            
            time.sleep(3)

app = SubgetTranlator()
app.main()
