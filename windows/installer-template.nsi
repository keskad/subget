;NSIS Modern User Interface version 1.65
 
!define MUI_PRODUCT "Subget"
!define MUI_VERSION "1.0"
 
!include "MUI.nsh"

; Style
; example: http://nsis.sourceforge.net/%22Orange%22_Modern_UI_Theme
!define MUI_ICON c:\subget\windows\icon-setup.ico
!define MUI_WELCOMEFINISHPAGE_BITMAP "c:\subget\windows\welcome-bitmap.bmp"
 

; Languages
!insertmacro MUI_RESERVEFILE_LANGDLL

;--------------------------------
;Configuration
 
  ;General
  name "Subget"
  OutFile "c:\Subget\Setup.exe"
 
  AllowRootDirInstall true
  XPStyle on
 
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
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH
 
;--------------------------------
;Languages
 
;Languages

  !insertmacro MUI_LANGUAGE "English" ;first language is the default language
  !insertmacro MUI_LANGUAGE "French"
  !insertmacro MUI_LANGUAGE "German"
  !insertmacro MUI_LANGUAGE "Spanish"
  !insertmacro MUI_LANGUAGE "SpanishInternational"
  !insertmacro MUI_LANGUAGE "SimpChinese"
  !insertmacro MUI_LANGUAGE "TradChinese"
  !insertmacro MUI_LANGUAGE "Japanese"
  !insertmacro MUI_LANGUAGE "Korean"
  !insertmacro MUI_LANGUAGE "Italian"
  !insertmacro MUI_LANGUAGE "Dutch"
  !insertmacro MUI_LANGUAGE "Danish"
  !insertmacro MUI_LANGUAGE "Swedish"
  !insertmacro MUI_LANGUAGE "Norwegian"
  !insertmacro MUI_LANGUAGE "NorwegianNynorsk"
  !insertmacro MUI_LANGUAGE "Finnish"
  !insertmacro MUI_LANGUAGE "Greek"
  !insertmacro MUI_LANGUAGE "Russian"
  !insertmacro MUI_LANGUAGE "Portuguese"
  !insertmacro MUI_LANGUAGE "PortugueseBR"
  !insertmacro MUI_LANGUAGE "Polish"
  !insertmacro MUI_LANGUAGE "Ukrainian"
  !insertmacro MUI_LANGUAGE "Czech"
  !insertmacro MUI_LANGUAGE "Slovak"
  !insertmacro MUI_LANGUAGE "Croatian"
  !insertmacro MUI_LANGUAGE "Bulgarian"
  !insertmacro MUI_LANGUAGE "Hungarian" 
;--------------------------------


Function .onInit
  ;!insertmacro MUI_UNGETLANGUAGE
  !insertmacro MUI_LANGDLL_DISPLAY

; Must set $INSTDIR here to avoid adding ${MUI_PRODUCT} to the end of the
; path when user selects a new directory using the 'Browse' button.
  StrCpy $INSTDIR "$PROGRAMFILES\${MUI_PRODUCT}"
FunctionEnd


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

  {#INSTALLER_FILES}
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
