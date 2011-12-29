from cx_Freeze import setup, Executable

import os, sys
from socket import _socket

os.system("setup.py install")
import subgetcore, subgetlib

#incpath = os.path.expanduser("~")+"/alang"
#sys.path.insert( 0, incpath )

exe = Executable(
    script="subget.py",
    base="Win32GUI",
    icon = 'c:\\Subget\\windows\\icon.ico'
    )

includefiles = ['usr']
includes = ['usr', 'src']
excludes = []
packages = ['_socket', 'socket', 'httplib', 'subprocess', 'os', 'time', 'urllib', 'hashlib', 're', 'zipfile', 'xml', 'StringIO', 'struct', 'sys', 'gettext', 'getopt', 'subgetcore', 'subgetlib']
 
setup(
    name = "Subget",
    version = "1.1",
    description = "A simple Subtitle downloading application for Linux, FreeBSD and Windows",
    appendScriptToExe = False,
    appendScriptToLibrary = False,
    options = {'build_exe': {'excludes':excludes,'packages':packages,'include_files':includefiles}}, 
    executables = [exe]
    )
