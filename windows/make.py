import os, sys, time, shutil
os.system("xcopy \"h:\\subget\" \"c:\\subget\" /E /Y")
os.system("del \"c:\Program Files\\Subget\\*\" /Q")
os.system("del \"c:\subget\\setup.exe\" /Q")
#os.system("del \"c:\Subget\\build\\exe.win32-2.7\\*\" /Q")
if os.path.isfile("c:\\subget\\build\\"):
    shutil.rmtree("c:\\subget\\build\\")

if os.path.isfile("C:\Program Files\Subget\\"):
    shutil.rmtree("C:\Program Files\Subget\\")

os.chdir("c:\\subget\\")
os.system("c:\\subget\\cx_freeze_build_windows.py build")
os.system("c:\\subget\\windows\\nsi-paths-build.py")
time.sleep(2)
os.system('C:\\NSIS\\makensis.exe "c:\\subget\\windows\\installer.nsi"')
os.system("c:\\subget\\setup.exe")
time.sleep(10)
