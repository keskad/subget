#!/usr/bin/python
import gtk, pygtk, dbus

def SubgetBUSMethod(a, MethodName, Arg=None, Arg2=None):
    global SubgetServiceObj, bus
    try:
        Method = SubgetServiceObj.get_dbus_method(MethodName, 'org.freedesktop.subget')
    except Exception: #dbus.exceptions.DBusException:
        print("Cannot connect to Subget dbus service.")
        return

    if MethodName == "addLinks":
        Method(str(Arg), False)
    elif not Arg == None and not Arg2 == None:
        Method(Arg, Arg2)
    elif not Arg == None:
        Method(Arg)
    else:
        Method()
        

window = gtk.Window(gtk.WINDOW_TOPLEVEL)
window.set_title("Subget - dbus example")
window.set_resizable(True)
window.set_size_request(600, 275)
vbox = gtk.VBox(False, 2)

try:
    bus = dbus.SessionBus()
    SubgetServiceObj = bus.get_object('org.freedesktop.subget', '/org/freedesktop/subget')
    ping = SubgetServiceObj.get_dbus_method('ping', 'org.freedesktop.subget')
    Response = True
except Exception as e:
    Response = False

openPluginsMenu = gtk.Button("Plugins menu")
openPluginsMenu.connect('clicked', SubgetBUSMethod, "openPluginsMenu")
vbox.pack_start(openPluginsMenu, False, False, 0)

openAboutDialog = gtk.Button("About dialog")
openAboutDialog.connect('clicked', SubgetBUSMethod, "openAboutDialog")
vbox.pack_start(openAboutDialog, False, False, 0)

addLinks = gtk.Button("Search for \"Borat\"")
addLinks.connect('clicked', SubgetBUSMethod, "addLinks", "Borat")
vbox.pack_start(addLinks, False, False, 0)

clearList = gtk.Button("Clean up the list")
clearList.connect('clicked', SubgetBUSMethod, "clearList")
vbox.pack_start(clearList, False, False, 0)

enableVP = gtk.Button("Enable video player")
enableVP.connect('clicked', SubgetBUSMethod, "toggleVideoPlayer", True)
vbox.pack_start(enableVP, False, False, 0)

disableVP = gtk.Button("Disable video player")
disableVP.connect('clicked', SubgetBUSMethod, "toggleVideoPlayer", False)
vbox.pack_start(disableVP, False, False, 0)

toggleVP = gtk.Button("Toggle video player")
toggleVP.connect('clicked', SubgetBUSMethod, "toggleVideoPlayer", "Auto")
vbox.pack_start(toggleVP, False, False, 0)

window.add(vbox)
window.show_all()
window.connect("destroy", gtk.main_quit)
gtk.main()
