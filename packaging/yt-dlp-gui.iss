; Installateur Inno Setup — compilé par packaging/build.py (qui fournit /DAppVersion=x.y.z).
; Le logiciel est installé sans droits administrateur par défaut (l'utilisateur peut choisir une
; installation pour tous). Les données (réglages, file d'attente, yt-dlp, ffmpeg) vont dans
; %LOCALAPPDATA%\yt-dlp-GUI et sont conservées à la désinstallation.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#ifndef DataDirName
  ; dossier des données dans %LOCALAPPDATA% (voir DATA_DIR dans yt-dlp-gui.pyw)
  #define DataDirName "yt-dlp-GUI"
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
UninstallDisplayName={#AppName}
; Mutex créé par le logiciel (RUN_MUTEX_NAME) : l'installateur et le désinstalleur demandent de le fermer.
AppMutex=yt-dlp-GUI-Running
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
; Question posée à la désinstallation (le Filipino n'est pas une langue de l'installateur).
DeleteDataPrompt=Also delete the yt-dlp GUI data (settings, queue, yt-dlp and ffmpeg downloaded by the software)?%n%nYour downloaded videos will not be deleted.%n%nFolder: %1
french.DeleteDataPrompt=Supprimer aussi les données de yt-dlp GUI (réglages, file d'attente, yt-dlp et ffmpeg téléchargés par le logiciel) ?%n%nVos vidéos téléchargées ne seront pas supprimées.%n%nDossier : %1
spanish.DeleteDataPrompt=¿Eliminar también los datos de yt-dlp GUI (ajustes, cola, yt-dlp y ffmpeg descargados por el programa)?%n%nSus vídeos descargados no se eliminarán.%n%nCarpeta: %1
brazilianportuguese.DeleteDataPrompt=Excluir também os dados do yt-dlp GUI (configurações, fila, yt-dlp e ffmpeg baixados pelo programa)?%n%nSeus vídeos baixados não serão excluídos.%n%nPasta: %1
italian.DeleteDataPrompt=Eliminare anche i dati di yt-dlp GUI (impostazioni, coda, yt-dlp e ffmpeg scaricati dal programma)?%n%nI video scaricati non verranno eliminati.%n%nCartella: %1
polish.DeleteDataPrompt=Czy usunąć także dane programu yt-dlp GUI (ustawienia, kolejkę, yt-dlp i ffmpeg pobrane przez program)?%n%nPobrane filmy nie zostaną usunięte.%n%nFolder: %1
hungarian.DeleteDataPrompt=Törli a yt-dlp GUI adatait is (beállítások, várólista, a program által letöltött yt-dlp és ffmpeg)?%n%nA letöltött videók nem törlődnek.%n%nMappa: %1
russian.DeleteDataPrompt=Удалить также данные yt-dlp GUI (настройки, очередь, yt-dlp и ffmpeg, загруженные программой)?%n%nЗагруженные видео удалены не будут.%n%nПапка: %1
japanese.DeleteDataPrompt=yt-dlp GUI のデータ（設定、キュー、本ソフトがダウンロードした yt-dlp と ffmpeg）も削除しますか？%n%nダウンロードした動画は削除されません。%n%nフォルダー: %1
korean.DeleteDataPrompt=yt-dlp GUI 데이터(설정, 대기열, 프로그램이 내려받은 yt-dlp와 ffmpeg)도 삭제하시겠습니까?%n%n다운로드한 동영상은 삭제되지 않습니다.%n%n폴더: %1
chinesesimplified.DeleteDataPrompt=是否同时删除 yt-dlp GUI 的数据（设置、队列、程序下载的 yt-dlp 和 ffmpeg）？%n%n已下载的视频不会被删除。%n%n文件夹：%1
vietnamese.DeleteDataPrompt=Xóa luôn dữ liệu của yt-dlp GUI (cài đặt, hàng đợi, yt-dlp và ffmpeg do phần mềm tải về)?%n%nCác video đã tải xuống sẽ không bị xóa.%n%nThư mục: %1
serbianlatin.DeleteDataPrompt=Da li želite da obrišete i podatke programa yt-dlp GUI (podešavanja, red čekanja, yt-dlp i ffmpeg koje je program preuzeo)?%n%nPreuzeti video snimci neće biti obrisani.%n%nFolder: %1
hindi.DeleteDataPrompt=क्या yt-dlp GUI का डेटा भी हटाएँ (सेटिंग्स, कतार, सॉफ़्टवेयर द्वारा डाउनलोड किए गए yt-dlp और ffmpeg)?%n%nडाउनलोड किए गए वीडियो नहीं हटाए जाएँगे।%n%nफ़ोल्डर: %1

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

const
  DataFolderName = '{#DataDirName}';

function DataFolder: String;
begin
  Result := ExpandConstant('{localappdata}') + '\' + DataFolderName;
end;

{ Les réglages, la file d'attente, yt-dlp et ffmpeg téléchargés par le logiciel vivent dans
  %LOCALAPPDATA%\yt-dlp-GUI : ils sont supprimés seulement sur confirmation (jamais les vidéos
  téléchargées). En désinstallation silencieuse, ils sont conservés sauf avec /DELETEDATA=1. }
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Remove: Boolean;
begin
  if (CurUninstallStep = usPostUninstall) and DirExists(DataFolder) then
  begin
    if UninstallSilent then
      Remove := ExpandConstant('{param:DELETEDATA|0}') = '1'
    else
      Remove := MsgBox(FmtMessage(CustomMessage('DeleteDataPrompt'), [DataFolder]),
                       mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES;
    if Remove then
      DelTree(DataFolder, True, True, True);
  end;
end;
