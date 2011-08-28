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
            os.system("chmod +x \""+theFile+"\"")
            Subget.Config['filemanagers']['gnome'] = True
            print("GNOME integration active.")
        except Exception as e:
            Widget.set_sensitive(0)
            print("Cannot create "+theFile+", error message: "+str(e))
    else:
        try:
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
            os.system("chmod +x \""+theFile+"\"")
            Subget.Config['filemanagers']['kde4'] = True
            print("KDE4 integration active.")
        except Exception as e:
            Widget.set_active(0)
            print("Cannot remove "+theFile+", error message: "+str(e))
    else:
        try:
            os.remove(theFile)
            Subget.Config['filemanagers']['kde4'] = False
        except Exception:
            Widget.set_sensitive(0)
            print("Cannot remove "+theFile+", error message: "+str(e))
