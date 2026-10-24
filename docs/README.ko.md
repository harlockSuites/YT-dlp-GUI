# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

[yt-dlp](https://github.com/yt-dlp/yt-dlp)를 위한 그래픽 인터페이스로, 누구나 쉽게 사용하면서 그 기능을 최대한 활용할 수 있도록 만들었습니다.

> **개발 중인 프로젝트입니다.** 일부 기능은 변경되거나 불완전하거나 버그가 있을 수 있습니다. Windows용으로 제공되며, 검증이 덜 된 **Linux용 미리보기 버전**도 함께 제공합니다.

🐧 **Linux** : [README-LINUX](README-LINUX.ko.md)

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## 기능

### 단일 다운로더와 대기열

- **옵션**: 최고 화질(최대 4K), 오디오만(MP3), 자막(vtt, srt, ass 형식), 자막과 썸네일 삽입, 기본 오디오 언어, 보조 오디오 트랙(멀티트랙 MKV 파일), 그리고 직접 만든 블록으로 확장할 수 있는 '스크립트 블록' 라이브러리(후처리, 내보내기, 네트워크, 동작).
- **여러 오디오 트랙**: MKV 파일에서 각 오디오 트랙에는 언어 태그('kor', 'eng' 등)가 붙으며, 플레이어의 오디오 메뉴에 표시됩니다.
- **생성된 명령**: 선택에 해당하는 yt-dlp 명령이 실시간으로 표시됩니다.
- **대기열**: 현재 URL을 추가한 뒤 전체 대기열, 특정 항목부터, 영상 하나 또는 범위를 실행합니다. 일시 정지와 재개, 현재 항목 건너뛰기, 미완성 파일을 정리하며 중지할 수 있습니다. 대기열은 세션 간에 유지됩니다.
- **이미 있는 파일 이름**: 저장 폴더에 같은 이름이 있는 단일 동영상에는 아무것도 덮어쓰지 않도록 접미사(`_2`, `_3`…)가 붙습니다. 이 다운로더로 받는 재생목록은 번호가 다시 매겨지지 않으며, 폴더에 이미 있는 동영상은 건너뜁니다('has already been downloaded').

### 재생목록 검사기

- 재생목록 **분석**: 각 영상이 사용 가능한 오디오 트랙과 자막과 함께 나열됩니다. 숨김, 비공개 또는 삭제된 항목은 나머지를 막지 않고 무시됩니다.
- **전역 규칙**(화질, 오디오만, 자막 형식과 삽입, 썸네일, 번호 매기기, 언어, 스크립트 블록, 출력 폴더)과 기본 언어, 보조 트랙, 자막에 대한 **영상별 예외**.
- **색상 코드**: 기본 언어가 없으면 빨간색, 보조 트랙이나 자막이 없으면 주황색.
- **선택 항목 다운로드**: 로그, 일시 정지, 재개, 건너뛰기를 지원합니다. 요청한 트랙이 없으면 해당 트랙 없이 다시 시도하고, 이후 **요약**에서 성공, 조정, 실패한 항목을 보여 줍니다.

### 스마트 디렉터리와 기록

- **스마트 디렉터리**: 출력 폴더에 저장된 기록 덕분에 yt-dlp가 이미 받은 영상을 건너뜁니다. `.yt-dlp-registre.json` 파일에는 각 영상의 식별자, URL, 제목, 길이, 파일 이름, 날짜가 들어 있으며, yt-dlp가 읽는 `.yt-dlp-archive.txt`는 여기서 만들어집니다.
- **소급 확인**: 선택한 영상이 이미 폴더에 있는데 기록에 없으면, 창이 (제목 비교로) 기록하고 건너뛰도록 제안합니다. 잘못된 일치는 체크를 해제할 수 있습니다.
- **기록 업데이트**: 폴더의 영상, 기록의 영상, 누락된 영상을 세고, 누락된 정보를 YouTube에서 찾습니다(제목, 그리고 ffprobe를 통한 길이). 확인 없이는 아무것도 기록되지 않으며, 두 개의 버튼으로 로컬 파일이나 찾은 YouTube 링크를 열어 확인할 수 있습니다.

![yt-dlp GUI](img/registry.en.png)

### 브라우저 쿠키

- yt-dlp가 로컬에서 쿠키를 읽을 브라우저(Chrome, Firefox, Edge, Brave, Opera)를 선택하세요. 보조 오디오 트랙과 일부 자막에 필요합니다. **Firefox를 권장합니다.**
- **우리의 테스트 결과**(Windows 11, 2026년 10월, 각 브라우저에서 YouTube 계정에 로그인한 상태): **Firefox**는 브라우저가 열려 있든 닫혀 있든 작동합니다. **Opera**는 **브라우저를 닫았을 때만** 작동합니다. 실행 중에는 쿠키 데이터베이스를 잠가 yt-dlp에 'Could not copy Chrome cookie database'가 표시됩니다. **Chrome, Edge, Brave**는 닫아도 실패합니다. yt-dlp가 항상 읽을 수는 없는 방식으로 쿠키를 암호화하기 때문입니다. 이러한 제한은 브라우저와 yt-dlp에서 비롯되며 이 소프트웨어의 문제가 아니고, 업데이트에 따라 달라질 수 있습니다.
- 브라우저가 **종료 시 쿠키를 삭제**하도록 설정되어 있거나(또는 비공개 모드로 탐색하는 경우) 디스크에 읽을 쿠키가 남지 않습니다. Chrome, Edge, Brave, Firefox 어느 것을 쓰든 yt-dlp는 아무것도 가져올 수 없습니다. Chrome, Edge, Brave에서는 이것이 함정입니다. 브라우저를 종료해야 하는데, 종료하면 쿠키가 지워지기 때문입니다. 이 옵션을 끄거나 youtube.com과 google.com의 쿠키를 유지하세요.
- **표시등**이 상태를 보여 줍니다: 비활성 또는 실패는 빨간색, 미테스트 또는 진행 중은 주황색, 쿠키가 로드되면 초록색. ↻ 버튼은 테스트를 실행하고, 툴팁이 상태나 오류를 설명합니다.
- **Linux(미리보기 버전)**: 기본으로 이 시스템에서 가장 많이 쓰는 Firefox, Google Chrome, Chromium, Brave, Vivaldi를 선택할 수 있습니다. 옵션 메뉴의 '쿠키용 브라우저' 창에서 최대 11개 브라우저(Opera, Microsoft Edge, LibreWolf, Waterfox, Floorp, Zen Browser 포함)를 선택할 수 있습니다. Chromium 계열 브라우저는 쿠키를 데스크톱 키링(GNOME Keyring, KWallet)으로 보호하므로 키링이 잠금 해제되어 있어야 하고, 그래픽 세션이 열려 있어야 합니다. YouTube에 로그인한 상태로 확인한 것은 Firefox 쿠키 읽기뿐이며(비공개 동영상 포함), **Firefox를 권장합니다**.

### 설치 도우미, 종속성, yt-dlp 업데이트

- **설치 도우미**: 처음 실행할 때 공식 GitHub 저장소에서 yt-dlp와 ffmpeg를 내려받도록 제안합니다. SHA-256 체크섬을 검증하며 관리자 권한이 필요하지 않습니다.
- **종속성**: 전용 창에서 ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2, deno를 확인하고 Chocolatey로 설치할 수 있습니다. ffmpeg와 ffprobe만 필수입니다. deno는 권장(보조 오디오 트랙용), AtomicParsley, MKVToolNix, aria2는 선택 사항이며 없어도 동작합니다. Linux에서는 설치 도우미가 ffmpeg, ffprobe, deno를 내려받습니다(SHA-256 검증, 관리자 권한 불필요). AtomicParsley, MKVToolNix, aria2는 창에 패키지 관리자(apt, dnf, pacman, zypper)의 명령이 표시되며, 터미널에 복사해 실행하면 됩니다.
- **업데이트와 진단**: yt-dlp를 업데이트(`yt-dlp -U`)하거나 실행 파일을 교체하고, 버전을 표시하며, GUI가 사용하는 옵션을 확인합니다.
- **소프트웨어 업데이트**: 하루에 한 번 확인하며(끌 수 있음) 새 버전이 있으면 눈에 띄지 않는 배너로 알립니다. 전용 창에서 새로운 기능을 보여 주고 설치 방식(설치 프로그램 또는 휴대용 버전)에 맞는 다운로드를 엽니다. 자동으로 설치되는 것은 없습니다. 옵션 메뉴의 스위치('시작할 때 업데이트 확인')로 자동 확인을 켜거나 끌 수 있고, '소프트웨어 업데이트 확인…'로 원할 때 직접 확인할 수 있습니다. Linux에서는 사용 중인 아키텍처에 맞는 AppImage 또는 `.tar.gz` 압축 파일입니다.

### 인터페이스와 언어

- 컨트롤은 창 너비에 따라 줄이 바뀌고, 내용은 세로로 스크롤되며, 검사기 표는 가로로도 스크롤됩니다.
- **15개 언어**의 인터페이스: 프랑스어, 영어, 스페인어, 포르투갈어, 이탈리아어, 폴란드어, 헝가리어, 세르비아어, 러시아어, 베트남어, 중국어, 힌디어, 일본어, 한국어, 필리핀어. 언어 변경은 다시 시작할 때 적용되며, 바로 다시 시작할 수도 있습니다.

### 버그 신고

- '버그 신고' 버튼은 기술 보고서를 준비합니다: 소프트웨어, Python, 운영체제, yt-dlp의 버전, 무해한 설정, 로그의 마지막 줄. 폴더, 사용자 이름, 이메일 주소는 가려집니다. GitHub에 보고서를 보내려면 무료 GitHub 계정이 필요합니다.
- 자동으로 전송되는 것은 없습니다: 보고서를 검토하고 편집한 뒤 미리 채워진 GitHub 이슈 페이지를 열거나 보고서를 복사합니다.

## 설치

- **설치 프로그램(권장)**: [릴리스 페이지](https://github.com/harlockSuites/YT-dlp-GUI/releases)에서 `yt-dlp-gui-setup-X.Y.Z.exe`를 내려받아 실행하세요. Windows 10 또는 11(64비트)에서 관리자 권한 없이 설치되며 Python은 필요하지 않습니다.
- **휴대용 버전**: `yt-dlp-gui-portable-X.Y.Z.zip`을 내려받아 원하는 곳에 압축을 풀고 `yt-dlp-gui.exe`를 실행하세요. 설정은 그 폴더에 저장됩니다.
- **Linux, AppImage(미리보기 버전)**: [릴리스 페이지](https://github.com/harlockSuites/YT-dlp-GUI/releases)에서 `yt-dlp-gui-X.Y.Z-x86_64.AppImage`를 내려받아 실행 권한을 주고(`chmod +x`) 실행하세요. `libfuse2`(패키지 `libfuse2` 또는 `fuse-libs`)가 필요하며, 없으면 `--appimage-extract-and-run` 옵션으로 실행하세요.
- **Linux, 압축 파일(미리보기 버전)**: `yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz`를 내려받아 압축을 풀고(`tar xzf`) `./yt-dlp-gui/yt-dlp-gui`를 실행하세요. 설정과 내려받은 도구는 `~/.local/share/yt-dlp-GUI`에 있으며, 삭제하려면 이 폴더와 프로그램 파일 또는 폴더를 지우세요.
- **Linux, 응용 프로그램 메뉴에 추가(미리 보기)**: AppImage나 압축 파일에서 실행하면 옵션 메뉴 ›'메뉴에 설치'가 프로그램을 `~/.local/share/yt-dlp-GUI/app`에 복사하고, 실행기와 아이콘을 데스크톱 메뉴에 추가하며, 원하면 바탕 화면 바로 가기도 만듭니다. 관리자 권한은 필요 없습니다. 같은 창에서 업데이트나 제거도 할 수 있으며 설정은 보존됩니다.
- **Linux, .deb 패키지(미리 보기)**: Debian, Ubuntu 및 파생 배포판에서는 `yt-dlp-gui_X.Y.Z_amd64.deb`를 내려받아 `sudo apt install ./yt-dlp-gui_X.Y.Z_amd64.deb`로 설치합니다. 프로그램이 아이콘과 함께 응용 프로그램 메뉴에 나타나며, `sudo apt remove yt-dlp-gui`로 제거할 수 있고 설정(`~/.local/share/yt-dlp-GUI`)은 보존됩니다.
- **Linux, 요구 사항과 검증**: 2022년 이후 배포판의 64비트 Linux(x86_64)(glibc 2.35 이상). 파일을 검증하려면 `SHA256SUMS-linux.txt`도 함께 내려받아 같은 폴더에서 `sha256sum -c SHA256SUMS-linux.txt --ignore-missing`을 실행하세요. Linux 파일은 따로 게시되며, 태그가 'Linux-v'로 시작하는 릴리스(GitHub에서 'Pre-release'로 표시)에 있습니다. 페이지에 기본으로 표시되는 릴리스는 Windows용입니다.
- **소스에서 실행**: 아래의 '요구 사항'과 '빠른 시작'을 참고하세요.
- **제거**: Windows 설정 › 앱 › 설치된 앱 › yt-dlp GUI, 또는 시작 메뉴의 '제거' 바로 가기. 소프트웨어가 자체 데이터(설정, 대기열, 내려받은 yt-dlp와 ffmpeg)도 삭제할지 묻습니다. 동영상은 절대 삭제되지 않습니다. 설치는 Windows 계정별로 이루어지므로, 소프트웨어는 설치한 계정의 목록에만 나타납니다. 포터블 버전은 폴더만 삭제하면 됩니다. Chocolatey로 따로 설치한 도구(ffmpeg, Deno 등)는 제거되지 않습니다.
- **백신 분석(VirusTotal)**: 0.1.7 버전은 2026년 10월 21일에 분석되었습니다. [설치 프로그램](https://www.virustotal.com/gui/file/7177f2dc75c3b5309b2d6b96a2104d578dbaf67a0c8ed28af286aa37159df91c)은 69개 엔진 중 4개(Arctic Wolf, Microsoft, SecureAge, Skyhigh)에서 일반적인 휴리스틱 탐지로 표시되었고, [포터블 버전의 실행 파일](https://www.virustotal.com/gui/file/6889bde864b341a948dc23c01e29eba3c63315145705eb0d5bb24a4964b0735a)은 70개 중 5개(Arctic Wolf, CrowdStrike Falcon, Microsoft, SecureAge, Zillya), [포터블 ZIP 아카이브](https://www.virustotal.com/gui/file/7fd0a4bb101ca4b4c513ff42e0782cc2371304c643bf03cb3ccd8e9abdb43706)는 66개 중 1개(Zillya, 아카이브 자체에 대한 탐지)에서 표시되었습니다. 압축되고 서명되지 않은 프로그램 때문에 생긴 오탐일 가능성이 높습니다. 이 결과는 이 버전에만 해당합니다. 걱정되면 SHA-256 합계를 확인하세요.
- **Code signing policy**: 파일에는 디지털 서명이 없습니다. SignPath Foundation에 대한 무료 서명 신청은 2026년 10월 19일에 거절되었습니다(프로젝트의 대외 인지도가 아직 부족함). 다시 신청할 수 있습니다. 인증서를 얻을 경우의 예정 절차는 [코드 서명 정책](https://github.com/harlockSuites/YT-dlp-GUI/blob/main/docs/CODE_SIGNING_POLICY.md)에 설명되어 있습니다.
- **Windows SmartScreen 경고**: 설치 프로그램에는 디지털 서명이 없어 Windows에 'Windows의 PC 보호' 화면이 나타날 수 있습니다. '추가 정보'를 누른 다음 '실행'을 선택하세요. 파일의 진위를 확인하려면 각 릴리스와 함께 게시되는 `SHA256SUMS.txt`의 SHA-256 값과 비교하세요:

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

## Windows 및 브라우저 경고

이 소프트웨어는 무료이며 한 사람이 배포하고, 파일은 **아직 디지털 서명이 되어 있지 않습니다**. 거의 아무도 내려받지 않은 새 파일에는 '평판'이 없으므로, 브라우저와 Windows는 **안전한 소프트웨어에도** 경고를 표시합니다. 경고가 있다고 위험하다는 증거는 아니며, 경고가 없다고 안전하다는 증거도 아닙니다. 직접 확인하는 방법은 다음과 같습니다.

- **브라우저**(Firefox, Chrome, Edge, Brave): 다운로드가 '흔하지 않음' 또는 '바이러스나 악성 소프트웨어 포함'으로 표시될 수 있습니다. 파일 평판의 자동 검사입니다. 먼저 아래의 체크섬을 확인하고, 일치하면 다운로드를 허용하거나 유지하는 옵션을 선택할 수 있습니다.
- **Windows SmartScreen**: 'Windows에서 PC를 보호했습니다' → 체크섬을 확인한 **후에** '추가 정보'를 클릭한 다음 '실행'을 클릭합니다.
- **Microsoft Defender(Windows 보안)**: 파일을 격리하거나 삭제하며 'Trojan:Win32/Wacatac.C!ml'이라고 표시할 수 있습니다. 접미사 `!ml`은 기계 학습에 의한 자동 탐지를 뜻하며, 새롭고 서명되지 않은 파일에서 흔합니다. 이러한 탐지는 오탐으로 Microsoft에 신고했습니다. SHA-256 합계를 확인한 후(아래) 파일을 복원할 수 있습니다: Windows 보안 › 바이러스 및 위협 방지 › 보호 기록 › 항목 열기 › 작업 › '장치에서 허용'(또는 '복원'). Windows 보호를 끄거나 이 파일 하나보다 넓은 예외를 추가하지 마세요.
- **백신**: 일부 엔진이 일반적인 탐지를 표시합니다(위의 백신 분석 참조). 내 파일의 분석을 보려면 SHA-256 합계를 [VirusTotal](https://www.virustotal.com/) 검색창에 붙여 넣으세요. 이미 알려진 파일이면 업로드하지 않고도 보고서를 볼 수 있습니다.
- **다운로드 확인**: 같은 릴리스 페이지에서 `SHA256SUMS.txt`도 내려받고, 파일이 있는 폴더에서 PowerShell을 열어 아래 명령을 실행하세요. 각 파일을 게시된 값과 비교해 `OK` 또는 `DIFFERENT`를 표시합니다. `DIFFERENT`인 파일은 실행하지 마세요.

```powershell
Get-Content .\SHA256SUMS.txt | ForEach-Object { $h, $n = $_ -split '\s+\*?', 2; if ((Get-FileHash $n -Algorithm SHA256).Hash -eq $h.ToUpper()) { "$n : OK" } else { "$n : DIFFERENT" } }
```

- 이 확인은 파일이 GitHub에 게시된 파일과 **동일**함을 증명하며, 그것만으로 무해함을 증명하지는 않습니다. 소스 코드와 파일의 자동 빌드([GitHub Actions](https://github.com/harlockSuites/YT-dlp-GUI/actions))는 공개되어 있으며, 디지털 서명은 아직 없습니다. SignPath Foundation 신청은 2026년 10월 19일에 거절되었습니다('Code signing policy' 참조).

## 요구 사항

- Windows 10 또는 11, 또는 64비트 Linux(미리보기 버전)
- Tkinter가 포함된 [Python 3](https://www.python.org/) (표준 설치에 포함) (Linux에서는 `python3-tk` 패키지)
- `yt-dlp.exe`와 가급적 [ffmpeg](https://ffmpeg.org/): 설치 도우미가 처음 실행할 때 내려받습니다 (Linux에서는 `.exe` 없는 `yt-dlp`)

## 빠른 시작

1. 이 저장소를 내려받거나 복제하고 해당 폴더로 이동합니다.
2. `yt-dlp-gui.bat`(또는 `pythonw yt-dlp-gui.pyw`)를 실행합니다. Linux에서는 `python3 yt-dlp-gui.pyw`를 실행합니다.
3. 처음 실행할 때 도우미가 yt-dlp와 ffmpeg를 설치하도록 하세요. 도우미는 옵션 메뉴에서 계속 열 수 있습니다.
4. URL을 붙여 넣고 옵션을 선택한 다음, 다운로드하거나 대기열에 추가하거나 재생목록용 검사기를 엽니다.

## 개인정보와 책임 있는 사용

- 이 소프트웨어는 작성자에게 어떤 데이터도 보내지 않으며 원격 측정을 포함하지 않습니다. 네트워크 연결은 yt-dlp(영상 사이트), 설치 도우미(GitHub), 기록 도구(YouTube 검색)를 통해 이루어집니다. 자동 업데이트 확인도 시작할 때 GitHub에 접속합니다(하루 최대 한 번). '시작할 때 업데이트 확인'에서 끌 수 있습니다.
- 쿠키는 사용자의 컴퓨터에 남습니다. yt-dlp가 선택한 브라우저에서 로컬로 읽습니다.
- 저작권, 사이트 이용약관, 거주 국가의 법률을 준수하여 이 도구를 사용하고, 내려받을 권리가 있는 것만 내려받으세요.

## 개발

테스트(번역, 기록, 명령 구성, 인터페이스, 설치 도우미, 문서)는 다음 명령으로 실행합니다:

```bash
python -X utf8 -m unittest discover -s tests -t .
```

푸시할 때마다 GitHub에서도 자동으로 실행됩니다. 버전 번호는 `yt-dlp-gui.pyw`의 `__version__`으로 정의되며 [CHANGELOG.md](../CHANGELOG.md)의 머리글과 일치해야 합니다. 인터페이스 번역 파일은 `lang/`에, 이 문서의 번역은 `docs/`에 있습니다. 원어민의 검토를 환영합니다.

## 프로젝트 후원

이 GUI는 지금까지도, 앞으로도 무료이며 누구에게나 열려 있습니다. 이 도구가 특히 유용했다면 [Ko-fi](https://ko-fi.com/harlocksuites)에서 프로젝트를 후원하실 수 있습니다.

## 감사의 말

[yt-dlp](https://github.com/yt-dlp/yt-dlp)를 꾸준히 업데이트하는 커뮤니티에 감사드립니다. 그것이 없었다면 이 모든 것은 불가능했을 것입니다.

## 라이선스

코드는 [MIT](../LICENSE) 라이선스로 공개됩니다. 아이콘, 로고, 'Harlock S.' 배너(`yt-dlp-gui.ico` 파일과 `assets/` 폴더)는 작성자의 요청으로 AI가 생성한 독창적인 작품입니다. 이 자료는 프로젝트의 시각적 정체성이며 MIT 라이선스의 적용 대상이 아닙니다. 다른 프로젝트에 재사용하거나 혼동을 일으킬 수 있는 방식으로 사용하지 마세요.
