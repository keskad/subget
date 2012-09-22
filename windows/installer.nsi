;NSIS Modern User Interface version 1.65
 
!define MUI_PRODUCT "Subget"
!define MUI_VERSION "1.0"
 
!include "MUI.nsh"
 
;--------------------------------
;Configuration
 
  ;General
  name "Subget"
  OutFile "c:\Subget\Setup.exe"
 
  AllowRootDirInstall true
 
;--------------------------------
;Modern UI Configuration
 
  !define MUI_WELCOMEPAGE
  !define MUI_CUSTOMPAGECOMMANDS
  !define MUI_COMPONENTSPAGE
  !define MUI_COMPONENTSPAGE_NODESC
  !define MUI_DIRECTORYPAGE
  !define MUI_CUSTOMFUNCTION_COMPONENTS_LEAVE ComponentPost
  !define MUI_CUSTOMFUNCTION_DIRECTORY_PRE DirectoryPre
  !define MUI_CUSTOMFUNCTION_DIRECTORY_SHOW DirectoryShow
  !define MUI_CUSTOMFUNCTION_DIRECTORY_LEAVE DirectoryLeave
 
  !define MUI_FINISHPAGE
    !define MUI_FINISHPAGE_RUN "$INSTDIR\subget.exe"
    !define MUI_FINISHPAGE_NOREBOOTSUPPORT
 
  !define MUI_ABORTWARNING
 
;--------------------------------
;Pages
 
  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH
 
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"
 
;--------------------------------
;Reserve Files
 
;Things that need to be extracted on first (keep these lines before any File command!)
;Only useful for BZIP2 compression
 
;--------------------------------
;Installer Types
 
  InstType "Full (Inc. Shortcuts)"
  InstType "Simple (No Shortcuts)"
 
;--------------------------------
;Installer Sections
 
Section "Program Files"
  SectionIn 1 2 RO
  SetOutPath "$INSTDIR"

OptionsOK:
  CreateDirectory "$INSTDIR"
  SetOutPath "$INSTDIR"

  
  File c:\Subget\build\exe.win32-2.7\7za.exe
  File c:\Subget\build\exe.win32-2.7\atk.pyd
  File c:\Subget\build\exe.win32-2.7\bz2.pyd
  File c:\Subget\build\exe.win32-2.7\cairo._cairo.pyd
  File c:\Subget\build\exe.win32-2.7\dde.pyd
  File c:\Subget\build\exe.win32-2.7\freetype6.dll
  File c:\Subget\build\exe.win32-2.7\gdiplus.dll
  File c:\Subget\build\exe.win32-2.7\gio._gio.pyd
  File c:\Subget\build\exe.win32-2.7\glib._glib.pyd
  File c:\Subget\build\exe.win32-2.7\gobject._gobject.pyd
  File c:\Subget\build\exe.win32-2.7\gtk._gtk.pyd
  File c:\Subget\build\exe.win32-2.7\intl.dll
  File c:\Subget\build\exe.win32-2.7\libatk-1.0-0.dll
  File c:\Subget\build\exe.win32-2.7\libcairo-2.dll
  File c:\Subget\build\exe.win32-2.7\libexpat-1.dll
  File c:\Subget\build\exe.win32-2.7\libfontconfig-1.dll
  File c:\Subget\build\exe.win32-2.7\libgdk-win32-2.0-0.dll
  File c:\Subget\build\exe.win32-2.7\libgdk_pixbuf-2.0-0.dll
  File c:\Subget\build\exe.win32-2.7\libgio-2.0-0.dll
  File c:\Subget\build\exe.win32-2.7\libglib-2.0-0.dll
  File c:\Subget\build\exe.win32-2.7\libgmodule-2.0-0.dll
  File c:\Subget\build\exe.win32-2.7\libgobject-2.0-0.dll
  File c:\Subget\build\exe.win32-2.7\libgthread-2.0-0.dll
  File c:\Subget\build\exe.win32-2.7\libgtk-win32-2.0-0.dll
  File c:\Subget\build\exe.win32-2.7\libpango-1.0-0.dll
  File c:\Subget\build\exe.win32-2.7\libpangocairo-1.0-0.dll
  File c:\Subget\build\exe.win32-2.7\libpangoft2-1.0-0.dll
  File c:\Subget\build\exe.win32-2.7\libpangowin32-1.0-0.dll
  File c:\Subget\build\exe.win32-2.7\libpng14-14.dll
  File c:\Subget\build\exe.win32-2.7\library.zip
  File c:\Subget\build\exe.win32-2.7\mfc90.dll
  File c:\Subget\build\exe.win32-2.7\pango.pyd
  File c:\Subget\build\exe.win32-2.7\pangocairo.pyd
  File c:\Subget\build\exe.win32-2.7\pyexpat.pyd
  File c:\Subget\build\exe.win32-2.7\python27.dll
  File c:\Subget\build\exe.win32-2.7\pythoncom27.dll
  File c:\Subget\build\exe.win32-2.7\pywintypes27.dll
  File c:\Subget\build\exe.win32-2.7\select.pyd
  File c:\Subget\build\exe.win32-2.7\subget.exe
  File c:\Subget\build\exe.win32-2.7\unicodedata.pyd
  File c:\Subget\build\exe.win32-2.7\win32api.pyd
  File c:\Subget\build\exe.win32-2.7\win32clipboard.pyd
  File c:\Subget\build\exe.win32-2.7\win32com.shell.shell.pyd
  File c:\Subget\build\exe.win32-2.7\win32event.pyd
  File c:\Subget\build\exe.win32-2.7\win32help.pyd
  File c:\Subget\build\exe.win32-2.7\win32process.pyd
  File c:\Subget\build\exe.win32-2.7\win32trace.pyd
  File c:\Subget\build\exe.win32-2.7\win32ui.pyd
  File c:\Subget\build\exe.win32-2.7\winxpgui.pyd
  File c:\Subget\build\exe.win32-2.7\zlib1.dll
  File c:\Subget\build\exe.win32-2.7\_hashlib.pyd
  File c:\Subget\build\exe.win32-2.7\_socket.pyd
  File c:\Subget\build\exe.win32-2.7\_ssl.pyd
  CreateDirectory c:\Subget\build\exe.win32-2.7\subgetlib
  SetOutPath $INSTDIR\subgetlib
  File c:\Subget\build\exe.win32-2.7\subgetlib\allsubs.py
  File c:\Subget\build\exe.win32-2.7\subgetlib\allsubs.pyc
  File c:\Subget\build\exe.win32-2.7\subgetlib\bus.py
  File c:\Subget\build\exe.win32-2.7\subgetlib\bus.pyc
  File c:\Subget\build\exe.win32-2.7\subgetlib\console.py
  File c:\Subget\build\exe.win32-2.7\subgetlib\console.pyc
  File c:\Subget\build\exe.win32-2.7\subgetlib\daemonize.py
  File c:\Subget\build\exe.win32-2.7\subgetlib\daemonize.pyc
  File c:\Subget\build\exe.win32-2.7\subgetlib\dialog.py
  File c:\Subget\build\exe.win32-2.7\subgetlib\dialog.pyc
  File c:\Subget\build\exe.win32-2.7\subgetlib\napiprojekt.py
  File c:\Subget\build\exe.win32-2.7\subgetlib\napiprojekt.pyc
  File c:\Subget\build\exe.win32-2.7\subgetlib\napisy24.py
  File c:\Subget\build\exe.win32-2.7\subgetlib\napisy24.pyc
  File c:\Subget\build\exe.win32-2.7\subgetlib\napisy_info.py
  File c:\Subget\build\exe.win32-2.7\subgetlib\napisy_info.pyc
  File c:\Subget\build\exe.win32-2.7\subgetlib\notify.py
  File c:\Subget\build\exe.win32-2.7\subgetlib\notify.pyc
  File c:\Subget\build\exe.win32-2.7\subgetlib\opensubtitles.py
  File c:\Subget\build\exe.win32-2.7\subgetlib\opensubtitles.pyc
  File c:\Subget\build\exe.win32-2.7\subgetlib\subscene.py
  File c:\Subget\build\exe.win32-2.7\subgetlib\subscene.pyc
  File c:\Subget\build\exe.win32-2.7\subgetlib\subswiki.py
  File c:\Subget\build\exe.win32-2.7\subgetlib\subswiki.pyc
  File c:\Subget\build\exe.win32-2.7\subgetlib\thesubdb.py
  File c:\Subget\build\exe.win32-2.7\subgetlib\thesubdb.pyc
  File c:\Subget\build\exe.win32-2.7\subgetlib\trayicon.py
  File c:\Subget\build\exe.win32-2.7\subgetlib\trayicon.pyc
  File c:\Subget\build\exe.win32-2.7\subgetlib\videoplayers.py
  File c:\Subget\build\exe.win32-2.7\subgetlib\videoplayers.pyc
  File c:\Subget\build\exe.win32-2.7\subgetlib\__init__.py
  File c:\Subget\build\exe.win32-2.7\subgetlib\__init__.pyc
  CreateDirectory c:\Subget\build\exe.win32-2.7\usr
  SetOutPath $INSTDIR\usr
  CreateDirectory c:\Subget\build\exe.win32-2.7\usr\share
  SetOutPath $INSTDIR\usr\share
  CreateDirectory c:\Subget\build\exe.win32-2.7\usr\share\applications
  SetOutPath $INSTDIR\usr\share\applications
  File c:\Subget\build\exe.win32-2.7\usr\share\applications\subget.desktop
  CreateDirectory c:\Subget\build\exe.win32-2.7\usr\share\menu
  SetOutPath $INSTDIR\usr\share\menu
  File c:\Subget\build\exe.win32-2.7\usr\share\menu\subget
  CreateDirectory c:\Subget\build\exe.win32-2.7\usr\share\subget
  SetOutPath $INSTDIR\usr\share\subget
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\config
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\gtkrc
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\version.xml
  CreateDirectory c:\Subget\build\exe.win32-2.7\usr\share\subget\api-examples
  SetOutPath $INSTDIR\usr\share\subget\api-examples
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\api-examples\dbus-example.py
  CreateDirectory c:\Subget\build\exe.win32-2.7\usr\share\subget\fm-integration
  SetOutPath $INSTDIR\usr\share\subget\fm-integration
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\fm-integration\gnome-wws.sh
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\fm-integration\gnome.sh
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\fm-integration\kde4-wws.desktop
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\fm-integration\kde4.desktop
  CreateDirectory c:\Subget\build\exe.win32-2.7\usr\share\subget\icons
  SetOutPath $INSTDIR\usr\share\subget\icons
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\error.png
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\extension.png
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\he.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\plugin-disabled.png
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\plugin.png
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\Subget-logo.png
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\Subget-logo.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\terminal.png
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\unknown.xpm
  CreateDirectory c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags
  SetOutPath $INSTDIR\usr\share\subget\icons\flags
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\bg.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\cz.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\da.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\de.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\dk.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\el.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\en.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\es.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\fi.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\fr.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\he.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\hr.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\hu.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\it.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\nl.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\pl.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\pt.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\ro.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\ru.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\sc.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\se.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\sl.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\sr.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\tr.xpm
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\icons\flags\unknown.xpm
  CreateDirectory c:\Subget\build\exe.win32-2.7\usr\share\subget\locale
  SetOutPath $INSTDIR\usr\share\subget\locale
  CreateDirectory c:\Subget\build\exe.win32-2.7\usr\share\subget\locale\da
  SetOutPath $INSTDIR\usr\share\subget\locale\da
  CreateDirectory c:\Subget\build\exe.win32-2.7\usr\share\subget\locale\da\LC_MESSAGES
  SetOutPath $INSTDIR\usr\share\subget\locale\da\LC_MESSAGES
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\locale\da\LC_MESSAGES\subget-src.mo
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\locale\da\LC_MESSAGES\subget-src.po
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\locale\da\LC_MESSAGES\subget.mo
  CreateDirectory c:\Subget\build\exe.win32-2.7\usr\share\subget\locale\pl
  SetOutPath $INSTDIR\usr\share\subget\locale\pl
  CreateDirectory c:\Subget\build\exe.win32-2.7\usr\share\subget\locale\pl\LC_MESSAGES
  SetOutPath $INSTDIR\usr\share\subget\locale\pl\LC_MESSAGES
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\locale\pl\LC_MESSAGES\subget-src.po
  File c:\Subget\build\exe.win32-2.7\usr\share\subget\locale\pl\LC_MESSAGES\subget.mo
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows
  SetOutPath $INSTDIR\windows
  File c:\Subget\build\exe.win32-2.7\windows\7za.exe
  File c:\Subget\build\exe.win32-2.7\windows\build-windows.sh
  File c:\Subget\build\exe.win32-2.7\windows\icon.ico
  File c:\Subget\build\exe.win32-2.7\windows\installer-template.nsi
  File c:\Subget\build\exe.win32-2.7\windows\installer.nsi
  File c:\Subget\build\exe.win32-2.7\windows\make.py
  File c:\Subget\build\exe.win32-2.7\windows\nsi-paths-build.py
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime
  SetOutPath $INSTDIR\windows\runtime
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime\lib
  SetOutPath $INSTDIR\windows\runtime\lib
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime\lib\gtk-2.0
  SetOutPath $INSTDIR\windows\runtime\lib\gtk-2.0
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime\lib\gtk-2.0\2.10.0
  SetOutPath $INSTDIR\windows\runtime\lib\gtk-2.0\2.10.0
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime\lib\gtk-2.0\2.10.0\engines
  SetOutPath $INSTDIR\windows\runtime\lib\gtk-2.0\2.10.0\engines
  File c:\Subget\build\exe.win32-2.7\windows\runtime\lib\gtk-2.0\2.10.0\engines\libpixmap.dll
  File c:\Subget\build\exe.win32-2.7\windows\runtime\lib\gtk-2.0\2.10.0\engines\libsvg.dll
  File c:\Subget\build\exe.win32-2.7\windows\runtime\lib\gtk-2.0\2.10.0\engines\libwimp.dll
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime\lib\gtk-2.0\include
  SetOutPath $INSTDIR\windows\runtime\lib\gtk-2.0\include
  File c:\Subget\build\exe.win32-2.7\windows\runtime\lib\gtk-2.0\include\gdkconfig.h
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime\lib\gtk-2.0\modules
  SetOutPath $INSTDIR\windows\runtime\lib\gtk-2.0\modules
  File c:\Subget\build\exe.win32-2.7\windows\runtime\lib\gtk-2.0\modules\libgail.dll
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime\share
  SetOutPath $INSTDIR\windows\runtime\share
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime\share\themes
  SetOutPath $INSTDIR\windows\runtime\share\themes
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime\share\themes\Default
  SetOutPath $INSTDIR\windows\runtime\share\themes\Default
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime\share\themes\Default\gtk-2.0-key
  SetOutPath $INSTDIR\windows\runtime\share\themes\Default\gtk-2.0-key
  File c:\Subget\build\exe.win32-2.7\windows\runtime\share\themes\Default\gtk-2.0-key\gtkrc
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime\share\themes\Emacs
  SetOutPath $INSTDIR\windows\runtime\share\themes\Emacs
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime\share\themes\Emacs\gtk-2.0-key
  SetOutPath $INSTDIR\windows\runtime\share\themes\Emacs\gtk-2.0-key
  File c:\Subget\build\exe.win32-2.7\windows\runtime\share\themes\Emacs\gtk-2.0-key\gtkrc
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime\share\themes\MS-Windows
  SetOutPath $INSTDIR\windows\runtime\share\themes\MS-Windows
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime\share\themes\MS-Windows\gtk-2.0
  SetOutPath $INSTDIR\windows\runtime\share\themes\MS-Windows\gtk-2.0
  File c:\Subget\build\exe.win32-2.7\windows\runtime\share\themes\MS-Windows\gtk-2.0\gtkrc
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime\share\themes\Raleigh
  SetOutPath $INSTDIR\windows\runtime\share\themes\Raleigh
  CreateDirectory c:\Subget\build\exe.win32-2.7\windows\runtime\share\themes\Raleigh\gtk-2.0
  SetOutPath $INSTDIR\windows\runtime\share\themes\Raleigh\gtk-2.0
  File c:\Subget\build\exe.win32-2.7\windows\runtime\share\themes\Raleigh\gtk-2.0\gtkrc
  ;CopyFiles "c:\subget\build\exe.win32-2.7\*.*" "$INSTDIR"
  WriteRegStr HKCU "SOFTWARE\Subget" 'Directory' '$INSTDIR'
  WriteRegStr HKCR "AVIFile\shell\Pobierz napisy\command" "" "$INSTDIR\subget.exe $\"%1$\""
  WriteRegStr HKCR "mpgfile\shell\Pobierz napisy\command" "" "$INSTDIR\subget.exe $\"%1$\""
  WriteRegStr HKCR "mpegfile\shell\Pobierz napisy\command" "" "$INSTDIR\subget.exe $\"%1$\""
  WriteRegStr HKCR "mp4file\shell\Pobierz napisy\command" "" "$INSTDIR\subget.exe $\"%1$\""
  WriteRegStr HKCR "3gpfile\shell\Pobierz napisy\command" "" "$INSTDIR\subget.exe $\"%1$\""
SectionEnd
 
SubSection /E "Shortcuts"
  Section "Desktop"
    SectionIn 1
    SetOutPath "$INSTDIR"
    SetShellVarContext all
    CreateShortCut "$DESKTOP\Subget.lnk" "$INSTDIR\subget.exe"
  SectionEnd
 
  Section "Start Menu"
    SectionIn 1
    SetOutPath "$INSTDIR"
    SetShellVarContext all
    CreateDirectory "$SMPROGRAMS\Subget"
    CreateShortCut "$SMPROGRAMS\Subget\Subget.lnk" "$INSTDIR\subget.exe"
  SectionEnd
SubSectionEnd
 
;--------------------------------
;Installer Functions
 
Function .onInit
; Must set $INSTDIR here to avoid adding ${MUI_PRODUCT} to the end of the
; path when user selects a new directory using the 'Browse' button.
  StrCpy $INSTDIR "$PROGRAMFILES\${MUI_PRODUCT}"
FunctionEnd
 
 
Function ComponentPost
  StrCpy $9 "0"
FunctionEnd
 
Function DirectoryPre
  StrCmp $9 "0" OK
    ;Skip 2nd (Data) Directory Page if Options file Exists
    IfFileExists "$2\h2003SE.opt" "" OK
      Abort
OK:
FunctionEnd
 
 
Function DirectoryShow
  StrCmp $9 "0" DataDirectoryPage
 
DataDirectoryPage:
  StrCpy $9 "1"
  !insertmacro MUI_HEADER_TEXT "Choose Data Location" "Choose the folder in which to install ${MUI_PRODUCT} - Data Files."
  !insertmacro MUI_INNERDIALOG_TEXT 1041 "Data Destination Folder"
  !insertmacro MUI_INNERDIALOG_TEXT 1019 "$INSTDIR\Data\"
  !insertmacro MUI_INNERDIALOG_TEXT 1006 "Setup will install ${MUI_PRODUCT} - Data Files in the following folder.$\r$\n$\r$\nTo install in a different folder, click Browse and select another folder. Click Install to start the installation."
EndDirectoryShow: 				
FunctionEnd
 
Function DirectoryLeave
  StrCmp $9 "1" SaveInstallDir
  StrCmp $9 "2" SaveDatabaseDir
  Goto EndDirectoryLeave
 
SaveInstallDir:
  StrCpy $2 $INSTDIR
  Goto EndDirectoryLeave
 
SaveDatabaseDir:
  StrCpy $3 $INSTDIR
 
EndDirectoryLeave:
FunctionEnd
 
Function .onVerifyInstDir
  StrCmp $9 "2" DataPath All
 
DataPath:
;all valid if UNC
  StrCpy $R2 $INSTDIR 2
  StrCmp $R2 "\\" PathOK
 
All:
; Invalid path if root
  Push $INSTDIR
  call GetRoot
  Pop $R1
  StrCmp $R1 $INSTDIR "" PathOK
  Abort
 
PathOK:
FunctionEnd
 
;--------------------------------
;Helper Functions
 
Function GetRoot
  Exch $0
  Push $1
  Push $2
  Push $3
  Push $4
 
  StrCpy $1 $0 2
  StrCmp $1 "\\" UNC
    StrCpy $0 $1
    Goto done
 
UNC:
  StrCpy $2 3
  StrLen $3 $0
  loop:
    IntCmp $2 $3 "" "" loopend
    StrCpy $1 $0 1 $2
    IntOp $2 $2 + 1
    StrCmp $1 "\" loopend loop
  loopend:
    StrCmp $4 "1" +3
      StrCpy $4 1
      Goto loop
    IntOp $2 $2 - 1
    StrCpy $0 $0 $2
 
done:
  Pop $4
  Pop $3
  Pop $2
  Pop $1
  Exch $0
FunctionEnd
