; Inno Setup script for StatPrism.
; Compiled in CI by .github/workflows/build-windows.yml, which passes the version:
;   ISCC.exe /DAppVersion=1.2.3 packaging/installer.iss
; Build locally the same way after a `python -m nuitka launcher.py`.

#define AppName "StatPrism"
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#define AppPublisher "StatPrism Team"
#define AppURL "https://github.com/yakovkinii/stat_prism"
#define AppExeName "StatPrism.exe"
; Project-file extension associated with StatPrism.
#define ProjectExt ".sp"
#define ProjectProgId "StatPrismProjectFile"
; Nuitka standalone output folder (script name .dist, per --mode=standalone).
#define DistDir "..\build\nuitka\launcher.dist"

[Setup]
; IMPORTANT: replace this GUID once with your own and NEVER change it again -- it is how
; Windows recognises upgrades of the same app. Generate one in the Inno Setup IDE
; (Tools > Generate GUID) or any uuid tool.
AppId={{d05d34ce-7f90-451f-b1ec-d33decc6f63f}}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=StatPrism-{#AppVersion}-setup
SetupIconFile=..\resources\icon.ico
UninstallDisplayIcon={app}\{#AppExeName}
; Show the licence agreement page (standard practice).
LicenseFile=..\LICENSE
; We add/remove a .sp file association, so let Explorer refresh its icon/handler cache.
ChangesAssociations=yes
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; StatPrism is 64-bit only.
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; Per-machine install (Program Files) requires admin; drop to lowest for per-user if preferred.
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"
Name: "associate"; Description: "Associate {#ProjectExt} project files with {#AppName}"; GroupDescription: "File associations:"

[Files]
; The whole Nuitka standalone folder.
Source: "{#DistDir}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Registry]
; .sp -> StatPrism, only when the "associate" task is ticked. HKA = per-user for a non-admin
; install, per-machine for an admin one. The exe supplies the file icon (Icon.ico is embedded).
Root: HKA; Subkey: "Software\Classes\{#ProjectExt}"; ValueType: string; ValueName: ""; ValueData: "{#ProjectProgId}"; Flags: uninsdeletevalue; Tasks: associate
Root: HKA; Subkey: "Software\Classes\{#ProjectProgId}"; ValueType: string; ValueName: ""; ValueData: "StatPrism Project File"; Flags: uninsdeletekey; Tasks: associate
Root: HKA; Subkey: "Software\Classes\{#ProjectProgId}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#AppExeName},0"; Tasks: associate
Root: HKA; Subkey: "Software\Classes\{#ProjectProgId}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""; Tasks: associate

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; \
  Flags: nowait postinstall skipifsilent unchecked
