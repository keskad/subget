import shutil, os
import xml.dom.minidom

""" Integration with various types of desktop environments """

def Nautilus(Widget, Subget, Path):
    """ Nautilus integration """

    theFile = Path+"/.gnome2/nautilus-scripts/"+Subget._("Download subtitles")

    if Widget.get_active() == False:
        try:
            shutil.copyfile("/usr/share/subget/fm-integration/gnome.sh", theFile)

            if Subget.configGetKey('watch_with_subtitles', 'enabled') == "True":
                shutil.copyfile("/usr/share/subget/fm-integration/gnome-wws.sh",  Path+"/.gnome2/nautilus-scripts/"+Subget._("Watch with subtitles"))

            os.system("chmod +x \""+theFile+"\"")
            Subget.Logging.output(Subget._("Integration active"), "debug", False)
        except Exception as e:
            Widget.set_sensitive(0)
            Subget.Logging.output("Cannot create "+theFile+", error message: "+str(e), "warning", True)
    else:
        try:
            if Subget.configGetKey('watch_with_subtitles', 'enabled') == "True":
                if os.path.isfile(Path+"/.gnome2/nautilus-scripts/"+Subget._("Watch with subtitles")):
                    os.remove(Path+"/.gnome2/nautilus-scripts/"+Subget._("Watch with subtitles"))
                    Subget.Logging.output(Subget._("Integration inactive"), "debug", False)

            os.remove(theFile)
        except Exception as e:
            Widget.set_sensitive(0)
            Subget.Logging.output("Cannot remove "+theFile+", error message: "+str(e), "debug", False)

def checkNautilus(self, Subget, Path):
    # check if Nautilus is installed
    if not os.path.isdir(Path+"/.gnome2/nautilus-scripts/"):
        Subget.Logging.output("Nautilus is not installed, disabling checkButton.", "debug", False)
        Widget.set_sensitive(0)
        #Widget.set_active(0)
        return False, False

    theFile = Path+"/.gnome2/nautilus-scripts/"+Subget._("Download subtitles")

    if not os.path.isfile(theFile):
        return False
    else:
        return True

def checkKDEService(Widget, Subget, Path):
    theFile = Path+"/.kde4/share/kde4/services/subget.desktop"

    # check if KDE4 is installed
    if not os.path.isdir(Path+"/.kde4/"):
        Subget.Logging.output("KDE is not installed, disabling checkButton.", "debug", False)
        Widget.set_sensitive(0)
        #Widget.set_active(0)
        return False

    if not os.path.isdir(Path+"/.kde4/share/kde4/services/"):
        os.system("mkdir -p "+Path+"/.kde4/share/kde4/services/")

    if not os.path.isfile(theFile):
        return False
    else:
        return True

def KDEService(Widget, Subget, Path):
    """ Subget integration with Dolphin and Konqueror (KDE Service) """

    theFile = Path+"/.kde4/share/kde4/services/subget.desktop"


    if Widget.get_active() == False:
        try:
            shutil.copyfile("/usr/share/subget/fm-integration/kde4.desktop", theFile)

            if Subget.configGetKey('watch_with_subtitles', 'enabled') == "True":
                shutil.copyfile("/usr/share/subget/fm-integration/kde4-wws.desktop",  Path+"/.kde4/share/kde4/services/subget-wws.desktop")

            os.system("chmod +x \""+theFile+"\"")
            Subget.Logging.output(Subget._("Integration active"), "debug", False)
        except Exception as e:
            Widget.set_active(0)
            Subget.Logging.output("Cannot create "+theFile+", error message: "+str(e), "warning", True)
    else:
        try:

            if Subget.configGetKey('watch_with_subtitles', 'enabled') == "True":
                if os.path.isfile(Path+"/.kde4/share/kde4/services/subget-wws.desktop"):
                    os.remove(Path+"/.kde4/share/kde4/services/subget-wws.desktop")
                    Subget.Logging.output(Subget._("Integration inactive"), "debug", False)

            os.remove(theFile)
        except Exception:
            Widget.set_sensitive(0)
            Subget.Logging.output("Cannot remove "+theFile+", error message: "+str(e), "warning", True)



def checkThunar(Widget, Subget, Path):
    """ Check status of Thunar integration with Subget """

    if not os.path.isfile("/usr/bin/thunar"):
        Subget.Logging.output("Cannot find "+Path+"/.config/Thunar/uca.xml - disabling thunar integration.", "warning", True)
        Widget.set_sensitive(0)
        #Widget.set_active(0)
        return False, False

    try:
        if not os.path.isdir(Path+"/.config/Thunar"):
            os.mkdir(Path+"/.config/Thunar")
            Subget.Logging.output("mkdir "+Path+"/.config/Thunar", "debug", False)

        if not os.path.isfile(Path+"/.config/Thunar/uca.xml"):
            w = open(Path+"/.config/Thunar/uca.xml", "w")
            w.write("<?xml version=\"1.0\" ?>\n<actions></actions>")
            w.close()
            Subget.Logging.output("Creating "+Path+"/.config/Thunar/uca.xml", "debug", False)

    except Exception as e:
        Subget.Logging.output("Cannot create file or directory for thunar integration: \""+str(e)+"\", check permissions.", "warning", True)

    try:
        fp = open(Path+"/.config/Thunar/uca.xml", "rb")
        fpContents = fp.read()
        fp.close()

        fpContents = fpContents.replace('<?xml encoding="UTF-8" version="1.0"?>', "<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        fpContents = fpContents.replace("<actions/>", "<actions></actions>")

        dom = xml.dom.minidom.parseString(fpContents)

        Found = False
        Actions = dom.getElementsByTagName("action")

        for Item in Actions:
            command = Item.getElementsByTagName('command')[0].childNodes[0].data

            if "subget" in command:
                Found = True

        return dom, Found
    except Exception as e:
        Subget.Logging.output("[thunar] Cannot open XML file at "+Path+"/.config/Thunar/uca.xml, exception: "+str(e), "warning", True)
        Widget.set_sensitive(0)
        return False, False


def ThunarUCA(Widget, Subget, Path, dom, Found):
    """ Subget integration w Xfce4 (Thunar filemanager by default) """

    Actions = dom.getElementsByTagName("action")

    for Item in Actions:
        command = Item.getElementsByTagName('command')[0].childNodes[0].data
        #name = Item.getElementsByTagName('name')[0].childNodes[0].data
        #icon = Item.getElementsByTagName('icon')[0].childNodes[0].data
        #patterns = Item.getElementsByTagName('patterns')[0].childNodes[0].data

        if "subget" in command:
            Found = True
            Item.parentNode.removeChild(Item)

    XML = dom.toxml().replace("<actions/>", "<actions></actions>")

    if Widget.get_active() == True:
        Subget.Logging.output(Subget._("Integration inactive"), "debug", False)
    else:
        if Subget.configGetKey('watch_with_subtitles', 'enabled') == "True":
            XML = XML.replace('</actions>', '<action><icon>text-plain</icon><name>'+Subget._("Download subtitles")+'</name><command>/usr/bin/subget %F</command><description></description><patterns>*</patterns><startup-notify/><video-files/></action><action><icon>text-plain</icon><name>'+Subget._("Watch with subtitles")+'</name><command>/usr/bin/subget -w %F</command><description></description><patterns>*</patterns><startup-notify/><video-files/></action></actions>')
        else:
            XML = XML.replace('</actions>', '<action><icon>text-plain</icon><name>'+Subget._("Download subtitles")+'</name><command>/usr/bin/subget %F</command><description></description><patterns>*</patterns><startup-notify/><video-files/></action></actions>')

        Subget.Logging.output(Subget._("Integration active"), "debug", False)

    try:
        fp = open(Path+"/.config/Thunar/uca.xml", "wb")
        fp.write(XML)
        fp.close()
    except Exception as e:
        Subget.Logging.output("[thunar] Cannot write to "+Path+"/.config/Thunar/uca.xml, is it writable?", "warning", True)
        widget.set_sensitive(0)
        return False

    return True
