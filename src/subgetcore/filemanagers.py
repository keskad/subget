import shutil, os

def Nautilus(Widget, Subget, Path):
    """ Nautilus integration """

    theFile = Path+"/.gnome2/nautilus-scripts/"+Subget.LANG[10]
    if not os.path.isfile(theFile):
        try:
            shutil.copyfile("/usr/share/subget/fm-integration/gnome.sh", theFile)
            os.system("chmod +x \""+theFile+"\"")
            Widget.set_active(1)
            Subget.Config['filemanagers']['gnome'] = True
        except Exception as e:
            Widget.set_sensitive(0)
            print("Cannot create "+theFile+", error message: "+str(e))
    else:
        try:
            os.remove(theFile)
            Widget.set_active(0)
            Subget.Config['filemanagers']['gnome'] = False
        except Exception as e:
            Widget.set_sensitive(0)
            print("Cannot remove "+theFile+", error message: "+str(e))

def KDEService(Widget, Subget, Path):
    """ Subget integration with Dolphin and Konqueror (KDE Service) """

    theFile = Path+"/.kde4/share/kde4/services/subget.desktop"

    if not os.path.isfile(theFile):
        try:
            shutil.copyfile("/usr/share/subget/fm-integration/kde4.desktop", theFile)
            os.system("chmod +x \""+theFile+"\"")
            Widget.set_active(1)
            Subget.Config['filemanagers']['kde4'] = True
            print("Cannot create "+theFile+", error message: "+str(e))
        except Exception as e:
            Widget.set_active(0)
            print("Cannot remove "+theFile+", error message: "+str(e))
