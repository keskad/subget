#!/usr/bin/python2.7
#-*- coding: utf-8 -*-
import getopt, sys, os, pycurl, re, glob, gtk, gobject
import pygtk
from threading import Thread

# default we will serve gui, but application will be also usable in shell, just need to use -c o --console parametr
consoleMode=False
pluginsDir="/usr/share/subget/plugins/"
plugins=dict()
action="list"
language="pl"
languages=['pl', 'en']

## ALANG

incpath="/usr/share/alang/python/";
sys.path.insert( 0, incpath )
import_string = "from alang import alang"

try:
       	exec import_string
except ImportError, e:
        print("Error " + str(e.args))

alang=alang()
LANG=alang.loadLanguage('subget')

## ALANG

class SubtitleThread(Thread):
    def __init__(self,Adress):
        Thread.__init__(self) # initialize thread

    def run(self):
        print "test"

def usage():
	'Shows program usage and version, lists all options'

	print LANG[0]

	print ""
class SubGet:
        dialog=None
        subtitlesList=dict()

        # close the window and quit
	def delete_event(self, widget, event, data=None):
	    gtk.main_quit()
	    return False

	def __init__(self):
	    global consoleMode, action, LANG

            self.LANG = LANG

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


	def doPluginsLoad(self, args):
	    global pluginsDir, plugins

	    if not os.path.exists(pluginsDir):
		print self.LANG[3]+" "+pluginsDir+" "+self.LANG[4]
		exit(0)

	    sys.path.append(pluginsDir)

	    file_list = glob.glob(pluginsDir+"*.py")

	    for Plugin in file_list:
		Plugin = os.path.basename(Plugin)[:-3] # cut directory and .py

		# load the plugin
		try:
		    exec("import "+Plugin)
		    exec("global "+Plugin)
		    exec("plugins[\""+Plugin+"\"] = "+Plugin)
		except ImportError:
		    print self.LANG[5]+" "+Plugin




        def addSubtitlesRow(self, language, release_name, server, download_data, extension, File):
            if len(self.subtitlesList) == 0:
                ID = 0
            else:
                ID = (len(self.subtitlesList)+1)
            
            self.subtitlesList[ID] = {'language': language, 'name': release_name, 'server': server, 'data': download_data, 'extension': extension, 'file': File}

            #print "Adding "+str(ID)+" - "+release_name

            pixbuf = gtk.gdk.pixbuf_new_from_file('/usr/share/subget/icons/'+language+'.xpm') 
            self.liststore.append([pixbuf, str(release_name), str(server), ID])


        # UPDATE THE TREEVIEW LIST
        def TreeViewUpdate(self):
	    #gobject.timeout_add(100, self.TreeViewUpdate)

            for Plugin in plugins:
                gobject.timeout_add(2, self.GTKCheckForSubtitles, Plugin)


        def GTKCheckForSubtitles(self, Plugin):
            exec("Results = plugins[\""+Plugin+"\"].language = language")
	    exec("Results = plugins[\""+Plugin+"\"].download_list(self.files)")

            if Results == None:
                print "[plugin:"+Plugin+"] "+self.LANG[6]
                return

            if Results[0].has_key("title"):
                self.addSubtitlesRow(Results[0]['lang'], Results[0]['title'], Results[0]['domain'], Results[0]['data'], Plugin, Results[0]['file'])

            print "[plugin:"+Plugin+"] "+self.LANG[7]+" - "+Results[0]['title']
            



        # FLAG DISPLAYING
        def cell_pixbuf_func(self, celllayout, cell, model, iter):
            cell.set_property('pixbuf', model.get_value(iter, 0))



        # SUBTITLES DOWNLOAD DIALOGS
        def GTKDownloadSubtitles(self):
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
                        self.GTKDownloadDialog(SelectID, fileName)
                    

                    chooser.destroy()
                else:
                    print "[GTK:DownloadSubtitles] subtitle_ID="+str(SelectID)+" "+self.LANG[9]

        def GTKDownloadDialog(self, SelectID, filename):
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

             Plugin = self.subtitlesList[SelectID]['extension']

             exec("Results = plugins[\""+Plugin+"\"].language = language")
             exec("Results = plugins[\""+Plugin+"\"].download_by_data(self.subtitlesList[SelectID]['data'], filename)")

             w.destroy()

        def update_progress_bar(self):
            self.pbar.pulse()
            return gtk.TRUE


        # DESTROY THE DIALOG
        def destroyDialog(self):
            self.dialog.destroy()
            self.dialog = None


        # GTK DIALOG WITH LIST OF AVAILABLE SUBTITLES
	def graphicalMode(self,files):
	    if len(files) == 1:
                self.files = files
                gobject.timeout_add(1, self.TreeViewUpdate)

	        # Create a new window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title(self.LANG[10])
		self.window.set_size_request(600, 255)
		self.window.connect("delete_event", self.delete_event)

                self.fixed = gtk.Fixed()

                self.liststore = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str)
                self.treeview = gtk.TreeView(self.liststore)
                self.treeview.set_size_request(600, 200)

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
                self.fixed.put(self.DownloadButton, 510, 210) # put on fixed

                self.DownloadButton.connect('clicked', lambda b: self.GTKDownloadSubtitles())

                # Cancel button
                self.CancelButton = gtk.Button(stock=gtk.STOCK_CLOSE)
                self.CancelButton.set_size_request(90, 40)
                self.CancelButton.connect('clicked', lambda b: gtk.mainquit())
                self.fixed.put(self.CancelButton, 410, 210) # put on fixed

                self.fixed.put(self.treeview, 0, 0)

                self.window.add(self.fixed)
		# create a TreeStore with one string column to use as the model
		

		self.window.show_all()
                gtk.main()

	    else:
		print self.LANG[15]

	def shellMode(self, files):
	    global plugins, action


	    # just find all matching subtitles and print it to console
	    if action == "list":
		for File in files:
                    aFileList = list()
                    aFileList.append(File)

		    for Plugin in plugins:
		         exec("Results = plugins[\""+Plugin+"\"].language = language")
		         exec("Results = plugins[\""+Plugin+"\"].download_list(aFileList)")

                         if Results != None:
                             if Results[0].has_key('title'):
                                 print Results[0]['domain']+"| "+Results[0]['lang']+" | "+Results[0]['title']

	    elif action == "first-result":
		for File in files:
		    for Plugin in plugins:
		         exec("Results = plugins[\""+Plugin+"\"].language = language")
		         exec("Results = plugins[\""+Plugin+"\"].download_quick(files)")
		         
		    

if __name__ == "__main__":
    SubGet()
