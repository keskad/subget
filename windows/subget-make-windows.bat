f:\subget\windows\nsi-paths-build.py
:: http://download.microsoft.com/download/8/e/c/8ec3a7d8-05b4-440a-a71e-ca3ee25fe057/rktools.exe will be needed for sleep command
ping 123.45.67.89 -n 1 -w 2000 > nul
echo off
cd "c:\subget"
del "c:\Program Files\Subget\*" /Q
del "c:\subget\setup.exe" /Q
del "C:\Subget\build\exe.win32-2.7\*" /Q
copy f:\subget\usr c:\subget\usr
copy f:\alang-py\usr c:\subget\usr
copy f:\subget\subget.py c:\subget\subget.py
copy f:\alang-py\usr\share\alang\python\alang.py c:\subget\alang.py
copy f:\alang-py\usr\share\alang\python\alang.py c:\subget\usr\share\alang\python\alang.py
copy f:\alang-py\usr\share\alang\python\alang.py "C:\Subget\build\exe.win32-2.7\alang.py
del c:\subget\install.sh
del c:\subget\README
del "c:\subget\commit-copy"
del "c:\subget\install-dependencies.sh"
cd c:\subget
c:\subget\cx_freeze_build_windows.py build
"C:\Program Files\NSIS\makensis.exe" "f:\subget\windows\installer.nsi"
copy "c:\subget\setup.exe" "f:\subget\setup.exe"
f:\subget\setup.exe
pause
