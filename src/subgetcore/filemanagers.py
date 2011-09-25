import shutil, os

""" Integration with various types of desktop environments """

def Nautilus(Widget, Subget, Path):
    """ Nautilus integration """

    theFile = Path+"/.gnome2/nautilus-scripts/"+Subget.LANG[10]

    # check if Nautilus is installed
    if not os.path.isdir(Path+"/.gnome2/nautilus-scripts/"):
        print("Nautilus is not installed, disabling checkButton.")
        Widget.set_sensitive(0)
        #Widget.set_active(0)
        return False

    if not os.path.isfile(theFile):
        try:
            shutil.copyfile("/usr/share/subget/fm-integration/gnome.sh", theFile)

            if Subget.configGetKey('watch_with_subtitles', 'enabled') == "True":
                shutil.copyfile("/usr/share/subget/fm-integration/gnome-wws.sh",  Path+"/.gnome2/nautilus-scripts/"+Subget.LANG[71])

            os.system("chmod +x \""+theFile+"\"")
            Subget.Config['filemanagers']['gnome'] = True
            print("GNOME integration active.")
        except Exception as e:
            Widget.set_sensitive(0)
            print("Cannot create "+theFile+", error message: "+str(e))
    else:
        try:
            if Subget.configGetKey('watch_with_subtitles', 'enabled') == "True":
                if os.path.isfile(Path+"/.gnome2/nautilus-scripts/"+Subget.LANG[71]):
                    os.remove(Path+"/.gnome2/nautilus-scripts/"+Subget.LANG[71])

            os.remove(theFile)
            Subget.Config['filemanagers']['gnome'] = False
        except Exception as e:
            Widget.set_sensitive(0)
            print("Cannot remove "+theFile+", error message: "+str(e))

def KDEService(Widget, Subget, Path):
    """ Subget integration with Dolphin and Konqueror (KDE Service) """

    theFile = Path+"/.kde4/share/kde4/services/subget.desktop"

    # check if KDE4 is installed
    if not os.path.isdir(Path+"/.kde4/share/kde4/services/"):
        print("KDE is not installed, disabling checkButton.")
        Widget.set_sensitive(0)
        #Widget.set_active(0)
        return False

    if not os.path.isfile(theFile):
        try:
            shutil.copyfile("/usr/share/subget/fm-integration/kde4.desktop", theFile)

            if Subget.configGetKey('watch_with_subtitles', 'enabled') == "True":
                shutil.copyfile("/usr/share/subget/fm-integration/kde4-wws.desktop",  Path+"/.kde4/share/kde4/services/subget-wws.desktop")

            os.system("chmod +x \""+theFile+"\"")
            Subget.Config['filemanagers']['kde'] = True
            print("KDE4 integration active.")
        except Exception as e:
            Widget.set_active(0)
            print("Cannot create "+theFile+", error message: "+str(e))
    else:
        try:

            if Subget.configGetKey('watch_with_subtitles', 'enabled') == "True":
                if os.path.isfile(Path+"/.kde4/share/kde4/services/subget-wws.desktop"):
                    os.remove(Path+"/.kde4/share/kde4/services/subget-wws.desktop")

            os.remove(theFile)
            Subget.Config['filemanagers']['kde'] = False
        except Exception:
            Widget.set_sensitive(0)
            print("Cannot remove "+theFile+", error message: "+str(e))

thunarLock = False

def ThunarUCA(Widget, Subget, Path):
    """ Subget integration w Xfce4 (Thunar filemanager by default) """

    global thunarLock

    import xml.dom.minidom

    if thunarLock == True:
        thunarLock = False
        return True

    # check if KDE4 is installed
    if not os.path.isfile(Path+"/.config/Thunar/uca.xml"):
        print("Cannot find "+Path+"/.config/Thunar/uca.xml - disabling thunar integration.")
        Widget.set_sensitive(0)
        #Widget.set_active(0)
        return False

    try:
        fp = open(Path+"/.config/Thunar/uca.xml", "rb")
        fpContents = fp.read()
        fp.close()

        fpContents = fpContents.replace('<?xml encoding="UTF-8" version="1.0"?>', "<?xml version=\"1.0\" encoding=\"UTF-8\"?>")

        dom = xml.dom.minidom.parseString(fpContents)
        Actions = dom.getElementsByTagName("action")
    except Exception as e:
        print("[thunar] Cannot open XML file at "+Path+"/.config/Thunar/uca.xm, exception: "+str(e))
        widget.set_sensitive(0)
        return False

    Found = False

    for Item in Actions:
        command = Item.getElementsByTagName('command')[0].childNodes[0].data
        #name = Item.getElementsByTagName('name')[0].childNodes[0].data
        #icon = Item.getElementsByTagName('icon')[0].childNodes[0].data
        #patterns = Item.getElementsByTagName('patterns')[0].childNodes[0].data

        if "subget" in command:
            Found = True
            Item.parentNode.removeChild(Item)

    XML = dom.toxml()

    if Found == True:
        print("[thunar] Integration inactive")
        Subget.Config['filemanagers']['xfce'] = False

    else:
        if Widget.get_active() == True:
            thunarLock = True
            Widget.set_active(False)

        Subget.Config['filemanagers']['xfce'] = True

        if Subget.configGetKey('watch_with_subtitles', 'enabled') == "True":
            XML = XML.replace('</actions>', '<action><icon>text-plain</icon><name>'+Subget.LANG[10]+'</name><command>/usr/bin/subget %F</command><description></description><patterns>*</patterns><startup-notify/><video-files/></action><action><icon>text-plain</icon><name>'+Subget.LANG[71]+'</name><command>/usr/bin/subget -w %F</command><description></description><patterns>*</patterns><startup-notify/><video-files/></action></actions>')
        else:
            XML = XML.replace('</actions>', '<action><icon>text-plain</icon><name>'+Subget.LANG[10]+'</name><command>/usr/bin/subget %F</command><description></description><patterns>*</patterns><startup-notify/><video-files/></action></actions>')

        print("[thunar] Integration active")

    try:
        fp = open(Path+"/.config/Thunar/uca.xml", "wb")
        fp.write(XML)
        fp.close()
    except Exception as e:
        print("[thunar] Cannot write to "+Path+"/.config/Thunar/uca.xml, is it writable?")
        widget.set_sensitive(0)
        return False

    return True
