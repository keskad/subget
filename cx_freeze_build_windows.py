from cx_Freeze import setup, Executable
import zipfile
import os, sys
from socket import _socket
import subgetcore, subgetlib
import win32com.server.register, pythoncom, win32com.client

os.system("setup.py build")
os.system("setup.py install")
os.system("setup.py install_data")

def zip_dir(dirpath, zippath):
    fzip = zipfile.ZipFile(zippath, 'a', zipfile.ZIP_DEFLATED)
    basedir = os.path.dirname(dirpath) + '/' 
    for root, dirs, files in os.walk(dirpath):
        if os.path.basename(root)[0] == '.':
            continue #skip hidden directories        
        dirname = root.replace(basedir, '')
        for f in files:
            if f[-1] == '~' or (f[0] == '.' and f != '.htaccess'):
                #skip backup files and all hidden files except .htaccess
                continue
            fzip.write(root + '/' + f, dirname + '/' + f)
    fzip.close()

#incpath = os.path.expanduser("~")+"/alang"
#sys.path.insert( 0, incpath )

exe = Executable(
    script="subget.py",
    base="Win32GUI",
    icon = 'c:\\Subget\\windows\\icon.ico'
    )

includefiles = ['usr', '7za.exe', 'windows']
includes = ['usr', 'src']
excludes = []
packages = ['_socket', 'socket', 'httplib', 'subprocess', 'os', 'time', 'urllib', 'hashlib', 're', 'zipfile', 'xml', 'StringIO', 'struct', 'sys', 'gettext', 'getopt', 'subgetcore', 'pythoncom', 'win32com', 'win32com.server.register', 'json', 'asyncore', 'xmlrpclib']
 
setup(
    name = "Subget",
    version = "1.3",
    description = "A simple Subtitle downloading application for Linux, FreeBSD and Windows",
    appendScriptToExe = False,
    appendScriptToLibrary = False,
    options = {'build_exe': {'excludes':excludes,'packages':packages,'include_files':includefiles}}, 
    executables = [exe]
    )

os.mkdir("build\\exe.win32-2.7\\subgetlib")
os.system("copy src\\subgetlib build\\exe.win32-2.7\\subgetlib")
#zip_dir("windows/runtime", "build/exe.win32-2.7/library.zip")
