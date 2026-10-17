; Installateur Inno Setup — compilé par packaging/build.py (qui fournit /DAppVersion=x.y.z).
; Le logiciel est installé sans droits administrateur par défaut (l'utilisateur peut choisir une
; installation pour tous). Les données (réglages, file d'attente, yt-dlp, ffmpeg) vont dans
; %LOCALAPPDATA%\yt-dlp-GUI et sont conservées à la désinstallation.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#define AppName "yt-dlp GUI"
#define AppExe "yt-dlp-gui.exe"

[Setup]
AppId={{8F6C1B7E-3D3A-4E5B-9A7C-5D2E4F1A6B90}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=Harlock S.
AppPublisherURL=https://ko-fi.com/harlocksuites
AppSupportURL=https://github.com/harlockSuites/YT-dlp-GUI
DefaultDirName={autopf}\yt-dlp GUI
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist
OutputBaseFilename=yt-dlp-gui-setup-{#AppVersion}
SetupIconFile=..\yt-dlp-gui.ico
UninstallDisplayIcon={app}\{#AppExe}
LicenseFile=..\LICENSE
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableWelcomePage=no
VersionInfoVersion={#AppVersion}
VersionInfoCompany=Harlock S.
VersionInfoDescription={#AppName} - installation

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "hungarian"; MessagesFile: "compiler:Languages\Hungarian.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
; Traductions copiées dans packaging\languages (voir README.md de ce dossier)
Name: "chinesesimplified"; MessagesFile: "languages\ChineseSimplified.isl"
Name: "vietnamese"; MessagesFile: "languages\Vietnamese.isl"
Name: "serbianlatin"; MessagesFile: "languages\SerbianLatin.isl"
Name: "hindi"; MessagesFile: "languages\Hindi.islu"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\yt-dlp-gui\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

[CustomMessages]
; Le filipino n'a pas de traduction Inno Setup : une phrase en filipino, affichée dans toutes les
; langues de l'installateur, indique que le logiciel lui-même est disponible en filipino.
FilipinoNote=Nag-aalok ang programang ito ng salin sa Filipino sa loob ng software.

[Code]
procedure InitializeWizard;
var
  Note: TNewStaticText;
begin
  Note := TNewStaticText.Create(WizardForm);
  Note.Parent := WizardForm.WelcomePage;
  Note.AutoSize := False;
  Note.WordWrap := True;
  Note.Left := WizardForm.WelcomeLabel2.Left;
  Note.Width := WizardForm.WelcomeLabel2.Width;
  Note.Height := ScaleY(32);
  Note.Top := WizardForm.WelcomePage.Height - Note.Height - ScaleY(4);
  Note.Font.Style := [fsItalic];
  Note.Caption := CustomMessage('FilipinoNote');
end;
