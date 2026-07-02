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
SetupIconFile=..\resources\StatPrism_icon_small.ico
UninstallDisplayIcon={app}\{#AppExeName}
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

[Files]
; The whole Nuitka standalone folder.
Source: "{#DistDir}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
; Visual C++ runtime, downloaded by CI into packaging\. Installed only if missing (see [Code]).
Source: "vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: VCRedistNeeded

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/install /quiet /norestart"; \
  StatusMsg: "Installing the Visual C++ runtime..."; Check: VCRedistNeeded
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; \
  Flags: nowait postinstall skipifsilent

[Code]
function VCRedistNeeded: Boolean;
var
  installed: Cardinal;
begin
  { True (needs installing) unless the x64 VC++ 2015-2022 runtime is already registered. }
  Result := not (
    RegQueryDWordValue(HKLM, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Installed', installed)
    and (installed = 1));
end;
