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

; Le logiciel est ouvert pendant l'installation ou la désinstallation : fermer à la main, ou « Forcer la fermeture ».
AppRunningTitle=yt-dlp GUI is open
AppRunningText=yt-dlp GUI must be closed to continue.%n%nClose it yourself, then click "I closed it", or click "Force close": downloads in progress will be interrupted (their partial files stay in the destination folder).
AppRunningForce=Force close
AppRunningRetry=I closed it
AppRunningCancel=Cancel
french.AppRunningTitle=yt-dlp GUI est ouvert
french.AppRunningText=yt-dlp GUI doit être fermé pour continuer.%n%nFermez-le vous-même puis cliquez sur « J'ai fermé le logiciel », ou cliquez sur « Forcer la fermeture » : les téléchargements en cours seront interrompus (leurs fichiers partiels restent dans le dossier de destination).
french.AppRunningForce=Forcer la fermeture
french.AppRunningRetry=J'ai fermé le logiciel
french.AppRunningCancel=Annuler
spanish.AppRunningTitle=yt-dlp GUI está abierto
spanish.AppRunningText=Hay que cerrar yt-dlp GUI para continuar.%n%nCiérrelo usted mismo y pulse «Ya lo cerré», o pulse «Forzar cierre»: las descargas en curso se interrumpirán (sus archivos parciales permanecen en la carpeta de destino).
spanish.AppRunningForce=Forzar cierre
spanish.AppRunningRetry=Ya lo cerré
spanish.AppRunningCancel=Cancelar
brazilianportuguese.AppRunningTitle=O yt-dlp GUI está aberto
brazilianportuguese.AppRunningText=É preciso fechar o yt-dlp GUI para continuar.%n%nFeche-o você mesmo e clique em «Já fechei», ou clique em «Forçar fechamento»: os downloads em andamento serão interrompidos (os arquivos parciais permanecem na pasta de destino).
brazilianportuguese.AppRunningForce=Forçar fechamento
brazilianportuguese.AppRunningRetry=Já fechei
brazilianportuguese.AppRunningCancel=Cancelar
italian.AppRunningTitle=yt-dlp GUI è aperto
italian.AppRunningText=Per continuare è necessario chiudere yt-dlp GUI.%n%nChiudilo tu stesso e fai clic su «L'ho chiuso», oppure fai clic su «Forza chiusura»: i download in corso verranno interrotti (i file parziali restano nella cartella di destinazione).
italian.AppRunningForce=Forza chiusura
italian.AppRunningRetry=L'ho chiuso
italian.AppRunningCancel=Annulla
polish.AppRunningTitle=yt-dlp GUI jest otwarty
polish.AppRunningText=Aby kontynuować, trzeba zamknąć yt-dlp GUI.%n%nZamknij program samodzielnie i kliknij „Zamknąłem”, albo kliknij „Wymuś zamknięcie”: trwające pobieranie zostanie przerwane (pliki częściowe pozostaną w folderze docelowym).
polish.AppRunningForce=Wymuś zamknięcie
polish.AppRunningRetry=Zamknąłem
polish.AppRunningCancel=Anuluj
hungarian.AppRunningTitle=A yt-dlp GUI meg van nyitva
hungarian.AppRunningText=A folytatáshoz be kell zárni a yt-dlp GUI-t.%n%nZárja be saját maga, majd kattintson a „Bezártam” gombra, vagy kattintson a „Bezárás kényszerítése” gombra: a folyamatban lévő letöltések megszakadnak (a részleges fájlok a célmappában maradnak).
hungarian.AppRunningForce=Bezárás kényszerítése
hungarian.AppRunningRetry=Bezártam
hungarian.AppRunningCancel=Mégse
russian.AppRunningTitle=yt-dlp GUI открыт
russian.AppRunningText=Чтобы продолжить, нужно закрыть yt-dlp GUI.%n%nЗакройте программу сами и нажмите «Я закрыл», либо нажмите «Закрыть принудительно»: текущие загрузки будут прерваны (частичные файлы останутся в папке назначения).
russian.AppRunningForce=Закрыть принудительно
russian.AppRunningRetry=Я закрыл
russian.AppRunningCancel=Отмена
japanese.AppRunningTitle=yt-dlp GUI が起動しています
japanese.AppRunningText=続行するには yt-dlp GUI を終了する必要があります。%n%nご自身で終了してから「終了しました」をクリックするか、「強制終了」をクリックしてください。実行中のダウンロードは中断されます（途中のファイルは保存先フォルダーに残ります）。
japanese.AppRunningForce=強制終了
japanese.AppRunningRetry=終了しました
japanese.AppRunningCancel=キャンセル
korean.AppRunningTitle=yt-dlp GUI가 실행 중입니다
korean.AppRunningText=계속하려면 yt-dlp GUI를 종료해야 합니다.%n%n직접 종료한 뒤 "종료했습니다"를 클릭하거나 "강제 종료"를 클릭하세요. 진행 중인 다운로드는 중단됩니다(부분 파일은 저장 폴더에 남습니다).
korean.AppRunningForce=강제 종료
korean.AppRunningRetry=종료했습니다
korean.AppRunningCancel=취소
chinesesimplified.AppRunningTitle=yt-dlp GUI 正在运行
chinesesimplified.AppRunningText=必须先关闭 yt-dlp GUI 才能继续。%n%n请自行关闭后点击“我已关闭”，或点击“强制关闭”：正在进行的下载将被中断（未完成的文件会保留在保存文件夹中）。
chinesesimplified.AppRunningForce=强制关闭
chinesesimplified.AppRunningRetry=我已关闭
chinesesimplified.AppRunningCancel=取消
vietnamese.AppRunningTitle=yt-dlp GUI đang mở
vietnamese.AppRunningText=Cần đóng yt-dlp GUI để tiếp tục.%n%nHãy tự đóng rồi bấm "Tôi đã đóng", hoặc bấm "Buộc đóng": các lượt tải đang chạy sẽ bị ngắt (tệp dang dở vẫn nằm trong thư mục đích).
vietnamese.AppRunningForce=Buộc đóng
vietnamese.AppRunningRetry=Tôi đã đóng
vietnamese.AppRunningCancel=Hủy
serbianlatin.AppRunningTitle=yt-dlp GUI je otvoren
serbianlatin.AppRunningText=Da biste nastavili, morate zatvoriti yt-dlp GUI.%n%nZatvorite ga sami pa kliknite „Zatvorio sam”, ili kliknite „Nasilno zatvori”: preuzimanja u toku biće prekinuta (delimični fajlovi ostaju u odredišnom folderu).
serbianlatin.AppRunningForce=Nasilno zatvori
serbianlatin.AppRunningRetry=Zatvorio sam
serbianlatin.AppRunningCancel=Otkaži
hindi.AppRunningTitle=yt-dlp GUI खुला है
hindi.AppRunningText=जारी रखने के लिए yt-dlp GUI को बंद करना होगा।%n%nइसे खुद बंद करके "मैंने बंद कर दिया" पर क्लिक करें, या "ज़बरदस्ती बंद करें" पर क्लिक करें: चल रहे डाउनलोड बाधित हो जाएँगे (अधूरी फ़ाइलें गंतव्य फ़ोल्डर में रहेंगी)।
hindi.AppRunningForce=ज़बरदस्ती बंद करें
hindi.AppRunningRetry=मैंने बंद कर दिया
hindi.AppRunningCancel=रद्द करें

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

const
  RunMutexName = 'yt-dlp-GUI-Running';   { identique à RUN_MUTEX_NAME dans yt-dlp-gui.pyw et à AppMutex }

function AppIsRunning: Boolean;
begin
  Result := CheckForMutexes(RunMutexName);
end;

procedure WaitForAppToStop;
var
  I: Integer;
begin
  for I := 1 to 20 do      { jusqu'à 5 secondes }
  begin
    if not AppIsRunning then
      Exit;
    Sleep(250);
  end;
end;

{ Ferme le logiciel : d'abord une demande de fermeture normale (il enregistre ses réglages), puis, s'il est
  toujours là, la fermeture forcée avec ses processus enfants (téléchargements en cours). }
function CloseApp: Boolean;
var
  Code: Integer;
begin
  Log('Fermeture du logiciel (demande normale)');
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/IM {#AppExe} /T', '', SW_HIDE, ewWaitUntilTerminated, Code);
  WaitForAppToStop;
  if AppIsRunning then
  begin
    Log('Fermeture forcée du logiciel');
    Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM {#AppExe} /T', '', SW_HIDE, ewWaitUntilTerminated, Code);
    WaitForAppToStop;
  end;
  Result := not AppIsRunning;
end;

{ Le logiciel est-il fermé ? Sinon l'utilisateur choisit : le fermer lui-même, forcer sa fermeture ou annuler.
  En mode silencieux, rien n'est demandé : le logiciel n'est fermé que avec /FORCECLOSE=1. }
function EnsureAppClosed(Silent: Boolean): Boolean;
var
  Answer: Integer;
begin
  Result := True;
  while AppIsRunning do
  begin
    Log('Le logiciel est ouvert');
    if ExpandConstant('{param:FORCECLOSE|0}') = '1' then
    begin
      Result := CloseApp;
      Exit;
    end;
    if Silent then
    begin
      Result := False;
      Exit;
    end;
    Answer := TaskDialogMsgBox(CustomMessage('AppRunningTitle'), CustomMessage('AppRunningText'),
      mbConfirmation, MB_YESNOCANCEL, [CustomMessage('AppRunningForce'),
      CustomMessage('AppRunningRetry'), CustomMessage('AppRunningCancel')], 0);   { jamais « [ » en début de ligne : balise de section }
    if Answer = IDYES then
      CloseApp
    else if Answer <> IDNO then
    begin
      Result := False;
      Exit;
    end;
  end;
end;

function InitializeSetup: Boolean;
begin
  Result := EnsureAppClosed(WizardSilent);
end;

function InitializeUninstall: Boolean;
begin
  Result := EnsureAppClosed(UninstallSilent);
end;
