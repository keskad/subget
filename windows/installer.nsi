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

  
  File c:\subget\build\exe.win32-2.7\alang.py
  File c:\subget\build\exe.win32-2.7\atk.pyd
  File c:\subget\build\exe.win32-2.7\bz2.pyd
  File c:\subget\build\exe.win32-2.7\cairo._cairo.pyd
  File c:\subget\build\exe.win32-2.7\freetype6.dll
  File c:\subget\build\exe.win32-2.7\gdiplus.dll
  File c:\subget\build\exe.win32-2.7\gio._gio.pyd
  File c:\subget\build\exe.win32-2.7\glib._glib.pyd
  File c:\subget\build\exe.win32-2.7\gobject._gobject.pyd
  File c:\subget\build\exe.win32-2.7\gtk._gtk.pyd
  File c:\subget\build\exe.win32-2.7\intl.dll
  File c:\subget\build\exe.win32-2.7\libatk-1.0-0.dll
  File c:\subget\build\exe.win32-2.7\libcairo-2.dll
  File c:\subget\build\exe.win32-2.7\libexpat-1.dll
  File c:\subget\build\exe.win32-2.7\libfontconfig-1.dll
  File c:\subget\build\exe.win32-2.7\libgdk-win32-2.0-0.dll
  File c:\subget\build\exe.win32-2.7\libgdk_pixbuf-2.0-0.dll
  File c:\subget\build\exe.win32-2.7\libgio-2.0-0.dll
  File c:\subget\build\exe.win32-2.7\libglib-2.0-0.dll
  File c:\subget\build\exe.win32-2.7\libgmodule-2.0-0.dll
  File c:\subget\build\exe.win32-2.7\libgobject-2.0-0.dll
  File c:\subget\build\exe.win32-2.7\libgthread-2.0-0.dll
  File c:\subget\build\exe.win32-2.7\libgtk-win32-2.0-0.dll
  File c:\subget\build\exe.win32-2.7\libpango-1.0-0.dll
  File c:\subget\build\exe.win32-2.7\libpangocairo-1.0-0.dll
  File c:\subget\build\exe.win32-2.7\libpangoft2-1.0-0.dll
  File c:\subget\build\exe.win32-2.7\libpangowin32-1.0-0.dll
  File c:\subget\build\exe.win32-2.7\libpng14-14.dll
  File c:\subget\build\exe.win32-2.7\library.zip
  File c:\subget\build\exe.win32-2.7\pango.pyd
  File c:\subget\build\exe.win32-2.7\pangocairo.pyd
  File c:\subget\build\exe.win32-2.7\pyexpat.pyd
  File c:\subget\build\exe.win32-2.7\python27.dll
  File c:\subget\build\exe.win32-2.7\select.pyd
  File c:\subget\build\exe.win32-2.7\subget.exe
  File c:\subget\build\exe.win32-2.7\unicodedata.pyd
  CreateDirectory c:\subget\build\exe.win32-2.7\usr
  SetOutPath $INSTDIR\usr
  CreateDirectory c:\subget\build\exe.win32-2.7\usr\share
  SetOutPath $INSTDIR\usr\share
  CreateDirectory c:\subget\build\exe.win32-2.7\usr\share\alang
  SetOutPath $INSTDIR\usr\share\alang
  CreateDirectory c:\subget\build\exe.win32-2.7\usr\share\alang\python
  SetOutPath $INSTDIR\usr\share\alang\python
  File c:\subget\build\exe.win32-2.7\usr\share\alang\python\alang.py
  File c:\subget\build\exe.win32-2.7\usr\share\alang\python\__init__.py
  CreateDirectory c:\subget\build\exe.win32-2.7\usr\share\alang\translations
  SetOutPath $INSTDIR\usr\share\alang\translations
  CreateDirectory c:\subget\build\exe.win32-2.7\usr\share\alang\translations\english
  SetOutPath $INSTDIR\usr\share\alang\translations\english
  File c:\subget\build\exe.win32-2.7\usr\share\alang\translations\english\subget.py
  File c:\subget\build\exe.win32-2.7\usr\share\alang\translations\english\__init__.py
  CreateDirectory c:\subget\build\exe.win32-2.7\usr\share\alang\translations\polski
  SetOutPath $INSTDIR\usr\share\alang\translations\polski
  File c:\subget\build\exe.win32-2.7\usr\share\alang\translations\polski\subget.py
  File c:\subget\build\exe.win32-2.7\usr\share\alang\translations\polski\subget.pyc
  File c:\subget\build\exe.win32-2.7\usr\share\alang\translations\polski\__init__.py
  File c:\subget\build\exe.win32-2.7\usr\share\alang\translations\__init__.py
  File c:\subget\build\exe.win32-2.7\usr\share\alang\__init__.py
  CreateDirectory c:\subget\build\exe.win32-2.7\usr\share\subget
  SetOutPath $INSTDIR\usr\share\subget
  CreateDirectory c:\subget\build\exe.win32-2.7\usr\share\subget\icons
  SetOutPath $INSTDIR\usr\share\subget\icons
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\bg.gif
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\bg.xpm
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\cz.xpm
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\da.gif
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\da.xpm
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\el.gif
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\el.xpm
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\en.xpm
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\error.png
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\es.xpm
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\fi.gif
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\fi.xpm
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\fr.gif
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\fr.xpm
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\he.gif
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\he.xpm
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\hu.gif
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\hu.xpm
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\nl.gif
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\nl.xpm
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\pl.xpm
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\plugin.png
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\pt.gif
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\pt.xpm
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\ro.gif
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\ro.xpm
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\sr.gif
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\sr.xpm
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\Subget-logo.png
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\tr.gif
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\tr.xpm
  File c:\subget\build\exe.win32-2.7\usr\share\subget\icons\unknown.xpm
  CreateDirectory c:\subget\build\exe.win32-2.7\usr\share\subget\plugins
  SetOutPath $INSTDIR\usr\share\subget\plugins
  File c:\subget\build\exe.win32-2.7\usr\share\subget\plugins\allsubs.py
  File c:\subget\build\exe.win32-2.7\usr\share\subget\plugins\allsubs.pyc
  File c:\subget\build\exe.win32-2.7\usr\share\subget\plugins\napiprojekt.py
  File c:\subget\build\exe.win32-2.7\usr\share\subget\plugins\napiprojekt.pyc
  File c:\subget\build\exe.win32-2.7\usr\share\subget\plugins\napisy24.py
  File c:\subget\build\exe.win32-2.7\usr\share\subget\plugins\napisy24.pyc
  File c:\subget\build\exe.win32-2.7\usr\share\subget\plugins\napisy_info.py
  File c:\subget\build\exe.win32-2.7\usr\share\subget\plugins\napisy_info.pyc
  File c:\subget\build\exe.win32-2.7\usr\share\subget\plugins\opensubtitles.py
  File c:\subget\build\exe.win32-2.7\usr\share\subget\plugins\opensubtitles.pyc
  File c:\subget\build\exe.win32-2.7\usr\share\subget\plugins\zlib1.dll
  File c:\subget\build\exe.win32-2.7\usr\share\subget\plugins\_hashlib.pyd
  File c:\subget\build\exe.win32-2.7\usr\share\subget\plugins\_socket.pyd
  File c:\subget\build\exe.win32-2.7\usr\share\subget\plugins\_ssl.pyd
  File c:\subget\build\exe.win32-2.7\usr\share\subget\plugins\__init__.py
  File c:\subget\build\exe.win32-2.7\usr\share\subget\__init__.py
  File c:\subget\build\exe.win32-2.7\usr\share\__init__.py
  File c:\subget\build\exe.win32-2.7\usr\__init__.py
  File c:\subget\build\exe.win32-2.7\zlib1.dll
  File c:\subget\build\exe.win32-2.7\_hashlib.pyd
  File c:\subget\build\exe.win32-2.7\_socket.pyd
  File c:\subget\build\exe.win32-2.7\_ssl.pyd
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
