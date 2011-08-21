#!/usr/bin/python
#-*- coding: utf-8 -*-
import getopt, sys, os, re, glob, gtk, gobject, pango, time
import pygtk
from threading import Thread
from distutils.sysconfig import get_python_lib

# default we will serve gui, but application will be also usable in shell, just need to use -c o --console parametr

winSubget = ""

if os.name == "nt":
    winSubget = str(os.path.dirname(sys.path[0])) 

consoleMode=False

if os.path.exists(winSubget+"/usr/share/subget/plugins/"):
    pluginsDir = winSubget+"/usr/share/subget/plugins/"
elif os.path.exists("usr/share/subget/plugins/"):
    pluginsDir="usr/share/subget/plugins/"
else:
    pluginsDir="/usr/share/subget/plugins/"


plugins=dict()
action="list"
language="pl"
languages=['pl', 'en']

## ALANG

if os.name == "nt":
    incpath=winSubget+"/usr/share/alang/python/"
elif os.path.isfile("usr/share/alang/python/alang.py"):
    incpath="usr/share/alang/python/";
else:
    incpath="/usr/share/alang/python/";

sys.path.insert( 0, incpath )

try:
           from alang import alang
except ImportError, e:
        print("Error " + str(e.args))

alang=alang()
alang.setPathPrefix(winSubget)
LANG=alang.loadLanguage('subget')

## ALANG

# THREADING SUPPORT

class SubtitleThread(Thread):
    def __init__(self,Plugin,sObject):
        Thread.__init__(self) # initialize thread
        self.Plugin = Plugin
        self.sObject = sObject
        self.status = "Idle"

    def run(self):
        self.sObject.GTKCheckForSubtitles(self.Plugin)
        self.status = "Running"

# EVAL THREADS
class threadingCommand (Thread):
    def __init__(self, objCommand, tmp="", tmp2=""):
        Thread.__init__(self)

        self.objCommand = objCommand
        self.tmp = tmp
        self.tmp2 = tmp2

    def run(self):
        exec(self.objCommand)

def usage():
    'Shows program usage and version, lists all options'

    print LANG[0]

    print ""

def exechelper(command):
    exec(command)


class SubGet:
    dialog=None
    subtitlesList=dict()

    def doPluginsLoad(self, args):
        global pluginsDir, plugins
        debugErrors = ""

        pluginsDir = get_python_lib()+"/subgetlib/"
        file_list = glob.glob(pluginsDir+"*.py")

        for Plugin in file_list:
            Plugin = os.path.basename(Plugin)[:-3] # cut directory and .py

            # skip the index
            if Plugin == "__init__":
                continue

            # load the plugin
            try:
                exec("import subgetlib."+Plugin)
                exec("plugins[\""+Plugin+"\"] = subgetlib."+Plugin)
                plugins[Plugin].loadSubgetObject(self)
            except Exception as errno:
                plugins[Plugin] = str(errno)
                print self.LANG[5]+" "+Plugin+" ("+str(errno)+")"

        # close the window and quit
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def main(self):
        global consoleMode, action, LANG

        self.LANG = LANG

        if os.name == "nt":
            self.subgetOSPath = winSubget+"/"
        elif os.path.exists("usr/share/subget"):
            print "[debug] Developer mode"
            self.subgetOSPath = "."
        else:
            self.subgetOSPath = ""

        try:
            opts, args = getopt.getopt(sys.argv[1:], "hcql:", ["help", "console", "quick", "language="])
        except getopt.GetoptError, err:
            print self.LANG[2]+": "+str(err)+", "+self.LANG[1]+"\n\n"
            usage()
            sys.exit(2)

        for o, a in opts:
            if o in ('-h', '--help'):
                 usage()
                 exit(2)
            if o in ('-c', '--console'):
                consoleMode=True
            if o in ('-q', '--quick'):
                action="first-result"

        self.doPluginsLoad(args)

        if consoleMode == True:
            self.shellMode(args)
        else:
            self.graphicalMode(args)

    def addSubtitlesRow(self, language, release_name, server, download_data, extension, File):
            if len(self.subtitlesList) == 0:
                ID = 0
            else:
                ID = (len(self.subtitlesList)+1)
            
            self.subtitlesList[ID] = {'language': language, 'name': release_name, 'server': server, 'data': download_data, 'extension': extension, 'file': File}

            #print "Adding "+str(ID)+" - "+release_name
            pixbuf_path = self.subgetOSPath+'/usr/share/subget/icons/'+language+'.xpm'

            if not os.path.isfile(pixbuf_path):
                pixbuf_path = self.subgetOSPath+'/usr/share/subget/icons/unknown.xpm'
                print "[addSubtitlesRow] "+language+".xpm icon does not exists, using unknown.xpm"

            pixbuf = gtk.gdk.pixbuf_new_from_file(pixbuf_path)

            self.liststore.append([pixbuf, str(release_name), str(server), ID])


        # UPDATE THE TREEVIEW LIST
    def TreeViewUpdate(self):
        #gobject.timeout_add(100, self.TreeViewUpdate)
            subThreads = list()

            for Plugin in plugins:
                current = SubtitleThread(Plugin, self)
                subThreads.append(current)
                current.start()

            for sThread in subThreads:
                sThread.join()
                


    def GTKCheckForSubtitles(self, Plugin):
            State = plugins[Plugin]

            if type(State).__name__ != "module":
                return

            Results = plugins[Plugin].language = language
            Results = plugins[Plugin].download_list(self.files)

            if Results == None:
                print "[plugin:"+Plugin+"] "+self.LANG[6]
            else:
                for Result in Results:
                    for Movie in Result:
                        try:
                            if Movie.has_key("title"):
                                self.addSubtitlesRow(Movie['lang'], Movie['title'], Movie['domain'], Movie['data'], Plugin, Movie['file'])
                                print "[plugin:"+Plugin+"] "+self.LANG[7]+" - "+Movie['title']
                        except AttributeError:
                             print "[plugin:"+Plugin+"] "+self.LANG[6]
                
            



        # FLAG DISPLAYING
    def cell_pixbuf_func(self, celllayout, cell, model, iter):
            """ Flag rendering """
            cell.set_property('pixbuf', model.get_value(iter, 0))

    def gtkDebugDialog(self,message):
            self.dialog = gtk.MessageDialog(parent = None,flags = gtk.DIALOG_DESTROY_WITH_PARENT,type = gtk.MESSAGE_INFO,buttons = gtk.BUTTONS_OK,message_format = message)
            self.dialog.set_title("Debug informations")
            self.dialog.connect('response', lambda dialog, response: self.destroyDialog())
            self.dialog.show()


        # SUBTITLES DOWNLOAD DIALOGS
    def GTKDownloadSubtitles(self):
            """ Dialog with file name chooser to save subtitles to """
            #print "TEST: CLICKED, LETS GO DOWNLOAD!"

            entry1,entry2 = self.treeview.get_selection().get_selected()    

            if entry2 == None:
                if self.dialog != None:
                    return
                else:
                    self.dialog = gtk.MessageDialog(parent = None,flags = gtk.DIALOG_DESTROY_WITH_PARENT,type = gtk.MESSAGE_INFO,buttons = gtk.BUTTONS_OK,message_format = self.LANG[18])
                    self.dialog.set_title(self.LANG[17])
                    self.dialog.connect('response', lambda dialog, response: self.destroyDialog())
                    self.dialog.show()
            else:
                SelectID = int(entry1.get_value(entry2, 3))
                
                if len(self.subtitlesList) == int(SelectID) or len(self.subtitlesList) > int(SelectID):
                    chooser = gtk.FileChooserDialog(title=self.LANG[8],action=gtk.FILE_CHOOSER_ACTION_SAVE,buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
                    chooser.set_current_folder(os.path.dirname(self.subtitlesList[SelectID]['file']))
                    chooser.set_current_name(os.path.basename(self.subtitlesList[SelectID]['file'])+".txt")
                    response = chooser.run()

                    if response == gtk.RESPONSE_OK:
                        fileName = chooser.get_filename()
                        chooser.destroy()
                        self.GTKDownloadDialog(SelectID, fileName)
                    else:
                        chooser.destroy()
                else:
                    print "[GTK:DownloadSubtitles] subtitle_ID="+str(SelectID)+" "+self.LANG[9]

    def GTKDownloadDialog(self, SelectID, filename):
             """Download progress dialog, downloading and saving subtitles to file"""

             Plugin = self.subtitlesList[SelectID]['extension']
             State = plugins[Plugin]

             if type(State).__name__ == "module":

                 w = gtk.Window(gtk.WINDOW_TOPLEVEL)
                 w.set_resizable(False)
                 w.set_title(self.LANG[10])
                 w.set_border_width(0)
                 w.set_size_request(300, 70)

                 fixed = gtk.Fixed()

                 # progress bar
                 self.pbar = gtk.ProgressBar()
                 self.pbar.set_size_request(180, 15)
                 self.pbar.set_pulse_step(0.01)
                 self.pbar.pulse()
                 w.timeout_handler_id = gtk.timeout_add(20, self.update_progress_bar)
                 self.pbar.show()

                 # label
                 label = gtk.Label(self.LANG[11])
                 fixed.put(label, 50,5)
                 fixed.put(self.pbar, 50,30)

                 w.add(fixed)
                 w.show_all()

                 Results = plugins[Plugin].language = language
                 Results = plugins[Plugin].download_by_data(self.subtitlesList[SelectID]['data'], filename)

                 w.destroy()

    def update_progress_bar(self):
            """ Progressbar updater, called asynchronously """
            self.pbar.pulse()
            return gtk.TRUE


        # DESTROY THE DIALOG
    def destroyDialog(self):
            """ Destroys all dialogs and popups """
            self.dialog.destroy()
            self.dialog = None

    def gtkSelectVideo(self, arg):
            """ Selecting multiple videos to search for subtitles """
            chooser = gtk.FileChooserDialog(title=self.LANG[21],action=gtk.FILE_CHOOSER_ACTION_OPEN,buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            chooser.set_select_multiple(True)
            response = chooser.run()

            if response == gtk.RESPONSE_OK:
                fileNames = chooser.get_filenames()
                chooser.destroy()

                for fileName in fileNames:
                    if not os.path.isfile(fileName) or not os.access(fileName, os.R_OK):
                        continue

                    self.files = list()
                    self.files.append(fileName)
                    #self.files = {fileName} # works on Python 2.7 only
                    #print self.files
                    self.TreeViewUpdate()
            else:
                chooser.destroy()

    def gtkPluginMenu(self, arg):
            """ GTK Widget with list of plugins """
            window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            window.set_title(self.LANG[37])
            window.set_resizable(False)
            window.set_size_request(500, 290)
            window.set_icon_from_file(self.subgetOSPath+"/usr/share/subget/icons/plugin.png")
            fixed = gtk.Fixed()

            liststore = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str)
            treeview = gtk.TreeView(liststore)


            # column list
            tvcolumn = gtk.TreeViewColumn(self.LANG[38])
            tvcolumn1 = gtk.TreeViewColumn(self.LANG[33])
            tvcolumn2 = gtk.TreeViewColumn(self.LANG[34])
            tvcolumn3 = gtk.TreeViewColumn(self.LANG[35])

            treeview.append_column(tvcolumn)
            treeview.append_column(tvcolumn1)
            treeview.append_column(tvcolumn2)
            treeview.append_column(tvcolumn3)

            cellpb = gtk.CellRendererPixbuf()
            cell = gtk.CellRendererText()
            cell1 = gtk.CellRendererText()
            cell2 = gtk.CellRendererText()
            cell3 = gtk.CellRendererText()

            # add the cells to the columns - 2 in the first
            tvcolumn.pack_start(cellpb, False)
            tvcolumn.set_cell_data_func(cellpb, self.cell_pixbuf_func)
            tvcolumn.pack_start(cell, True)
            tvcolumn1.pack_start(cell1, True)
            tvcolumn2.pack_start(cell2, True)
            tvcolumn3.pack_start(cell3, True)
            tvcolumn.set_attributes(cell, text=1)
            tvcolumn1.set_attributes(cell1, text=2)
            tvcolumn2.set_attributes(cell2, text=3)
            tvcolumn3.set_attributes(cell3, text=4)

            for Plugin in plugins:
                try:
                    API = plugins[Plugin].PluginInfo['API']
                except Exception:
                    API = "?"

                try:
                    Author = plugins[Plugin].PluginInfo['Authors']
                except Exception:
                    Author = self.LANG[36]

                try:
                    OS = plugins[Plugin].PluginInfo['Requirements']['OS']

                    if OS == "All":
                        OS = "Unix, Linux, Windows"
                except Exception:
                    OS = self.LANG[36]

                try:
                    Packages = plugins[Plugin].PluginInfo['Requirements']['Packages']

                    if len(Packages) > 0:
                        i=0
                        for Package in Packages:
                            if i == 0:
                                Packages_c = Packages_c + Package
                            else:
                                Packages_c = Packages_c + Package + ", "
                            i=i+1

                except Exception:
                    Packages = self.LANG[36]

                if type(plugins[Plugin]).__name__ == "module":
                    pixbuf = gtk.gdk.pixbuf_new_from_file(self.subgetOSPath+'/usr/share/subget/icons/plugin.png') 
                    liststore.append([pixbuf, Plugin, OS, str(Author), str(API)])
                else:
                    pixbuf = gtk.gdk.pixbuf_new_from_file(self.subgetOSPath+'/usr/share/subget/icons/error.png') 
                    liststore.append([pixbuf, Plugin, OS, str(Author), str(API)])

            # make treeview searchable
            treeview.set_search_column(1)

            # Allow sorting on the column
            tvcolumn.set_sort_column_id(1)
            tvcolumn1.set_sort_column_id(1)
            tvcolumn2.set_sort_column_id(2)
            tvcolumn3.set_sort_column_id(3)

            scrolled_window = gtk.ScrolledWindow()
            scrolled_window.set_border_width(0)
            scrolled_window.set_size_request(500, 230)
            scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
            scrolled_window.add_with_viewport(treeview)

            # Cancel button
            CancelButton = gtk.Button(stock=gtk.STOCK_CLOSE)
            CancelButton.set_size_request(90, 40)
            CancelButton.connect('clicked', lambda b: window.destroy())
            fixed.put(CancelButton, 400, 240) # put on fixed

            fixed.put(scrolled_window, 0, 0)
            window.add(fixed)
            window.show_all()

    def gtkAboutMenu(self, arg):
            """ Shows about dialog """

            about = gtk.Window(gtk.WINDOW_TOPLEVEL)
            about.set_title(self.LANG[23])
            about.set_resizable(False)
            about.set_size_request(600,550)
            about.set_icon_from_file(self.subgetOSPath+"/usr/share/subget/icons/Subget-logo.png")

            # container
            fixed = gtk.Fixed()
            
            # logo
            logo = gtk.Image()
            logo.set_from_file(self.subgetOSPath+"/usr/share/subget/icons/Subget-logo.png")
            fixed.put(logo, 12, 20)

            # title
            title = gtk.Label(self.LANG[23])
            title.modify_font(pango.FontDescription("sans 18"))
            fixed.put(title, 150, 20)

            # description title
            description = gtk.Label(self.LANG[24])
            description.modify_font(pango.FontDescription("sans 8"))
            fixed.put(description, 150, 60)

            # TABS
            notebook = gtk.Notebook()
            notebook.set_tab_pos(gtk.POS_TOP)
            notebook.show_tabs = True
            notebook.set_size_request(580, 370)
            notebook.set_border_width(0) 
            self.gtkAddTab(notebook, self.LANG[25], self.LANG[26]+":\n WebNuLL <http://webnull.kablownia.org>\n\n"+self.LANG[27]+":\n Tiritto <http://dawid-niedzwiedzki.pl>\n WebNuLL <http://webnull.kablownia.org>\n\n"+self.LANG[28]+":\n iluzion <http://dobreprogramy.pl/iluzion>\n famfamfam <http://famfamfam.com>")

            self.gtkAddTab(notebook, self.LANG[29], self.LANG[30])

            self.gtkAddTab(notebook, self.LANG[31], "English:\n WebNuLL <http://webnull.kablownia.org>\n\nPolish:\n WebNuLL <http://webnull.kablownia.org>")

            fixed.put(notebook, 12, 160)

           

            # add container show all
            about.add(fixed)
            about.show_all()

    def gtkAddTab(self, notebook, label, text):
            authorsFrame = gtk.Frame("")
            authorsFrame.set_border_width(0) 
            authorsFrame.set_size_request(100, 75)
            authorsFrame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)

            authorsFrameContent = gtk.Label(text)
            authorsFrameContent.set_alignment (0, 0)

            # Scrollbars
            scrolled_window = gtk.ScrolledWindow()
            scrolled_window.set_border_width(0)
            scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
            scrolled_window.add_with_viewport(authorsFrameContent)

            authorsFrame.add(scrolled_window)

            authorsLabel = gtk.Label(label)
            notebook.prepend_page(authorsFrame, authorsLabel)

    def gtkSearchMenu(self, arg):
            self.sm = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.sm.set_title(self.LANG[39])
            self.sm.set_size_request(350, 180)
            self.sm.set_resizable(False)
            self.sm.set_icon_from_file(self.subgetOSPath+"/usr/share/subget/icons/Subget-logo.png")

            self.sm.fixed = gtk.Fixed()

            # informations
            self.sm.label = gtk.Label(self.LANG[40])

            # text query
            self.sm.entry = gtk.Entry()
            self.sm.entry.set_max_length(50)
            self.sm.entry.set_size_request(190, 26)
            self.sm.entry.show()

            # combo box with plugin selection
            self.sm.cb = gtk.combo_box_new_text()
            self.sm.cb.append_text(self.LANG[41])
            self.sm.plugins = dict()

            for Plugin in plugins:
                if type(plugins[Plugin]).__name__ != "module":
                    continue

                # does plugin inform about its domain?
                if plugins[Plugin].PluginInfo.has_key('domain'):
                    pluginDomain = plugins[Plugin].PluginInfo['domain']
                    self.sm.plugins[pluginDomain] = Plugin
                    self.sm.cb.append_text(pluginDomain)
                else:
                    self.sm.plugins[Plugin] = Plugin
                    self.sm.cb.append_text(Plugin)

            # Set "All plugins" as default active
            self.sm.cb.set_active(0)


            # search button
            self.sm.searchButton = gtk.Button(self.LANG[39])
            self.sm.searchButton.set_size_request(80, 35)

            image = gtk.Image() # image for button
            image.set_from_stock(gtk.STOCK_FIND, 4)
            self.sm.searchButton.set_image(image)
            self.sm.searchButton.connect('clicked', self.gtkDoSearch)

            # cancel button
            self.sm.cancelButton = gtk.Button(self.LANG[42])
            self.sm.cancelButton.set_size_request(80, 35)
            self.sm.cancelButton.connect('clicked', lambda b: self.sm.destroy())

            image = gtk.Image() # image for button
            image.set_from_stock(gtk.STOCK_CLOSE, 4)
            self.sm.cancelButton.set_image(image)

            # list clearing check box
            self.sm.clearCB = gtk.CheckButton(self.LANG[43])

            self.sm.fixed.put(self.sm.label, 10, 8)
            self.sm.fixed.put(self.sm.entry, 10, 60)
            self.sm.fixed.put(self.sm.cb, 210, 59)
            self.sm.fixed.put(self.sm.clearCB, 20, 90)
            self.sm.fixed.put(self.sm.searchButton, 250, 128)
            self.sm.fixed.put(self.sm.cancelButton, 165, 128)

            self.sm.add(self.sm.fixed)
            self.sm.show_all()

    def gtkDoSearch(self, arg):
            query = self.sm.entry.get_text()
            self.sm.destroy()
            time.sleep(0.1)

            if query == "" or query == None:
                return

            if self.sm.clearCB.get_active():
                self.liststore.clear()

            plugin = self.sm.cb.get_active_text()

            # search in all plugins
            if plugin == self.LANG[41]:
                for Plugin in plugins:
                    try:
                        plugins[Plugin].language = language
                        Results = plugins[Plugin].search_by_keywords(query) # query the plugin for results

                        if Results == None:
                            return

                        for Subtitles in Results:
                            if str(type(Subtitles).__name__) == "str":
                                continue

                            self.addSubtitlesRow(Subtitles['lang'], Subtitles['title'], Subtitles['domain'], Subtitles['data'], Plugin, Subtitles['file'])

                    except AttributeError:
                       True # Plugin does not support searching by keywords
            else:
                try:
                    plugins[self.sm.plugins[plugin]].language = language
                    Results = plugins[self.sm.plugins[plugin]].search_by_keywords(query) # query the plugin for results

                    if Results == None:
                        return

                    for Result in Results:
                        if str(type(Result).__name__) == "str":
                            continue

                        self.addSubtitlesRow(Result['lang'], Result['title'], Result['domain'], Result['data'], plugin, Result['file'])

                except AttributeError as errno:
                    print "[plugin:"+self.sm.plugins[plugin]+"] "+self.LANG[45]
                    True # Plugin does not support searching by keywords
            

    def gtkMainScreen(self,files):
        """ Main GTK screen of the application """
        #if len(files) == 1:
        #gobject.timeout_add(1, self.TreeViewUpdate)
        
        
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(self.LANG[10])
        self.window.set_resizable(False)
        self.window.set_size_request(600, 275)
        self.window.connect("delete_event", self.delete_event)
        self.window.set_icon_from_file(self.subgetOSPath+"/usr/share/subget/icons/Subget-logo.png")

        # DRAG & DROP SUPPORT
        TARGET_STRING = 82
        TARGET_IMAGE = 83

        self.window.drag_dest_set(0, [], 0)
        self.window.connect("drag_motion", self.motion_cb)
        self.window.connect("drag_drop", self.drop_cb)
        self.window.connect("drag_data_received", self.drag_data_received)

        ############# Menu #############
        mb = gtk.MenuBar()
        icon_theme = gtk.icon_theme_get_default()

        # Shortcuts
        agr = gtk.AccelGroup()
        self.window.add_accel_group(agr)

        # "File" menu
        fileMenu = gtk.Menu()
        fileMenuItem = gtk.MenuItem(self.LANG[22])
        fileMenuItem.set_submenu(fileMenu)
        mb.append(fileMenuItem)

        # "Tools" menu
        toolsMenu = gtk.Menu()
        toolsMenuItem = gtk.MenuItem(self.LANG[32])
        toolsMenuItem.set_submenu(toolsMenu)
        mb.append(toolsMenuItem)

        # "Plugins list"
        pluginMenu = gtk.ImageMenuItem(self.LANG[37], agr)
        key, mod = gtk.accelerator_parse("<Control>P")
        pluginMenu.add_accelerator("activate", agr, key,mod, gtk.ACCEL_VISIBLE)
        pluginMenu.connect("activate", self.gtkPluginMenu)

        try:
            image = gtk.Image()
            image.set_from_file(self.subgetOSPath+"/usr/share/subget/icons/plugin.png")
            pluginMenu.set_image(image)
        except gobject.GError, exc:
            True

        toolsMenu.append(pluginMenu)

        # "About"
        infoMenu = gtk.ImageMenuItem(self.LANG[23], agr) # gtk.STOCK_CDROM
        key, mod = gtk.accelerator_parse("<Control>I")
        infoMenu.add_accelerator("activate", agr, key,mod, gtk.ACCEL_VISIBLE)
        infoMenu.connect("activate", self.gtkAboutMenu)

        try:
            pixbuf = icon_theme.load_icon("dialog-information", 16, 0)
            image = gtk.Image()
            image.set_from_pixbuf(pixbuf)
            infoMenu.set_image(image)
        except gobject.GError, exc:
            True

        toolsMenu.append(infoMenu)

        # "Clear"
        clearMenu = gtk.ImageMenuItem(self.LANG[44])
        clearMenu.connect("activate", lambda b: self.liststore.clear())

        try:
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_CLEAR, 2)
            clearMenu.set_image(image)
        except gobject.GError, exc:
            True


        toolsMenu.append(clearMenu)

        # Adding files to query
        openMenu = gtk.ImageMenuItem(gtk.STOCK_ADD, agr)
        key, mod = gtk.accelerator_parse("<Control>O")
        openMenu.add_accelerator("activate", agr, key,mod, gtk.ACCEL_VISIBLE)
        openMenu.connect("activate", self.gtkSelectVideo)
        fileMenu.append(openMenu)

        # Search
        find = gtk.ImageMenuItem(gtk.STOCK_FIND, agr)
        key, mod = gtk.accelerator_parse("<Control>F")
        find.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
        find.connect("activate", self.gtkSearchMenu)
        fileMenu.append(find)

        # Exit position in menu
        exit = gtk.ImageMenuItem(gtk.STOCK_QUIT, agr)
        key, mod = gtk.accelerator_parse("<Control>Q")
        exit.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
        exit.connect("activate", gtk.main_quit)
        fileMenu.append(exit)

        ############# End of Menu #############
        self.fixed = gtk.Fixed()

        self.liststore = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str)
        self.treeview = gtk.TreeView(self.liststore)


        # column list
        self.tvcolumn = gtk.TreeViewColumn(self.LANG[12])
        self.tvcolumn1 = gtk.TreeViewColumn(self.LANG[13])
        self.tvcolumn2 = gtk.TreeViewColumn(self.LANG[14])

        self.treeview.append_column(self.tvcolumn)
        self.treeview.append_column(self.tvcolumn1)
        self.treeview.append_column(self.tvcolumn2)


        self.cellpb = gtk.CellRendererPixbuf()
        #self.cellpb.set_property('pixbuf', pixbuf)

        self.cell = gtk.CellRendererText()
        self.cell1 = gtk.CellRendererText()
        self.cell2 = gtk.CellRendererText()

        # add the cells to the columns - 2 in the first
        self.tvcolumn.pack_start(self.cellpb, False)

        self.tvcolumn.set_cell_data_func(self.cellpb, self.cell_pixbuf_func)
        #self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn1.pack_start(self.cell1, True)
        self.tvcolumn2.pack_start(self.cell2, True)
        self.tvcolumn1.set_attributes(self.cell1, text=1)
        self.tvcolumn2.set_attributes(self.cell2, text=2)

        # make treeview searchable
        self.treeview.set_search_column(1)

        # Allow sorting on the column
        self.tvcolumn1.set_sort_column_id(1)
        self.tvcolumn2.set_sort_column_id(2)


        # Create buttons
        self.DownloadButton = gtk.Button(stock=gtk.STOCK_GO_DOWN)
        self.DownloadButton.set_label(self.LANG[16])
        image = gtk.Image()
        image.set_from_stock("gtk-go-down", gtk.ICON_SIZE_BUTTON)
        self.DownloadButton.set_image(image)
        self.DownloadButton.set_size_request(80, 40)
        self.fixed.put(self.DownloadButton, 510, 205) # put on fixed

        self.DownloadButton.connect('clicked', lambda b: self.GTKDownloadSubtitles())

        # Cancel button
        self.CancelButton = gtk.Button(stock=gtk.STOCK_CLOSE)
        self.CancelButton.set_size_request(90, 40)
        self.CancelButton.connect('clicked', lambda b: gtk.mainquit())
        self.fixed.put(self.CancelButton, 410, 205) # put on fixed

        # scrollbars
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(0)
        scrolled_window.set_size_request(600, 200)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        scrolled_window.add_with_viewport(self.treeview)

        self.fixed.put(scrolled_window, 0, 0)
        self.fixed.set_border_width(0)
        
        vbox = gtk.VBox(False, 0)
        vbox.set_border_width(0)
        vbox.pack_start(mb, False, False, 0)
        vbox.pack_start(self.fixed, False, False, 0)

        self.window.add(vbox)
        # create a TreeStore with one string column to use as the model
        

        self.window.show_all()

        #else:
            #    print self.LANG[15]

    ##### DRAG & DROP SUPPORT #####
    def motion_cb(self, wid, context, x, y, time):
        context.drag_status(gtk.gdk.ACTION_COPY, time)
        return True
    
    def drop_cb(self, wid, context, x, y, time):
        if context.targets:
            wid.drag_get_data(context, context.targets[0], time)
            return True
        return False

    
    def drag_data_received(self, img, context, x, y, data, info, time):
        """ Receive dropped data, parse and call plugins """

        if data.format == 8:
            Files = data.data.replace('\r', '').split("\n")
            self.files = list()

            for File in Files:
                File = File.replace("file://", "")

                if os.path.isfile(File):
                    self.files.append(File)

            context.finish(True, False, time)
            self.TreeViewUpdate()
                
        

    ##### END OF DRAG & DROP SUPPORT #####

    def graphicalMode(self, files):
            """ Detects operating system and load GTK GUI """
            self.files = files
            self.gtkMainScreen(files)
            gobject.timeout_add(50, self.TreeViewUpdate)
            gtk.main()

    def shellMode(self, files):
        """ Works in shell mode, searching, downloading etc..."""
        global plugins, action

        # just find all matching subtitles and print it to console
        if action == "list":
            for Plugin in plugins:
                State = plugins[Plugin]

                if type(State).__name__ != "module":
                    continue

                Results = plugins[Plugin].language = language
                Results = plugins[Plugin].download_list(files)

                if Results == None:
                    continue

                for Result in Results:
                    for Movie in Result:
                        try:
                            if Movie.has_key("title"):
                                print Movie['domain']+"|"+Movie['lang']+"|"+Movie['title']
                        except AttributeError:
                            continue


        elif action == "first-result":
                Found = False
                preferredData = False

        for File in files:
            for Plugin in plugins:
                exec("State = plugins[\""+Plugin+"\"]")

                if type(State).__name__ != "module":
                    continue

                fileToList = list()
                fileToList.append(File)

                Results = plugins[Plugin].language = language
                Results = plugins[Plugin].download_list(fileToList)

                if Results != None:
                    if type(Results[0]).__name__ == "dict":
                        continue
                    else:
                        if Results[0][0]["lang"] == language:
                            FileTXT = File+".txt"
                            exec("DLResults = plugins[\""+Plugin+"\"].download_by_data(Results[0][0]['data'], FileTXT)")
                            print LANG[19]+" "+str(DLResults)
                            Found = True
                            break
                        elif preferredData != None:
                            continue
                        else:
                            preferredData = Results[0][0]
                 
        if Found == False and preferredData == True:
            FileTXT = File+".("+str(preferredData['lang'])+").txt"
            exec("DLResults = plugins[\""+Plugin+"\"].download_by_data(prefferedData['data'], FileTXT)")
            print LANG[19]+" "+str(DLResults)+", "+LANG[20]

if __name__ == "__main__":
    SubgetMain = SubGet()
    SubgetMain.main()
