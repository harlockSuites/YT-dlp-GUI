# yt-dlp GUI — Linux 버전

[Français](../README-LINUX.md) · [English](README-LINUX.en.md) · [Español](README-LINUX.es.md) · [Português](README-LINUX.pt.md) · [Italiano](README-LINUX.it.md) · [Polski](README-LINUX.pl.md) · [Magyar](README-LINUX.hu.md) · [Srpski](README-LINUX.sr.md) · [Русский](README-LINUX.ru.md) · [Tiếng Việt](README-LINUX.vi.md) · [中文](README-LINUX.zh.md) · [हिन्दी](README-LINUX.hi.md) · [日本語](README-LINUX.ja.md) · [한국어](README-LINUX.ko.md) · [Filipino](README-LINUX.fil.md)

> **미리 보기 버전입니다.** 이 문서는 [기본 README](README.ko.md)를 보완합니다. 소프트웨어는 같지만, 여기서는 Linux에만 해당하는 내용(설치, 쿠키와 키링, 파일, 문제 해결)만 다룹니다. 각 버전의 새로운 점은 [CHANGELOG-linux.md](../CHANGELOG-linux.md)에 있습니다. 번역은 아직 원어민의 검토가 필요하며, 의심스러운 경우에는 프랑스어와 영어 본문이 우선합니다.

## 목차

1. [미리 보기 버전의 상태](#s1)
2. [설치](#s2)
3. [첫 실행과 의존성](#s3)
4. [브라우저 쿠키](#s4)
5. [키링: 수동 작업](#s5)
6. [파일 위치](#s6)
7. [문제 해결](#s7)
8. [버그 신고](#s8)
9. [개발자를 위한 안내](#s9)

<a id="s1"></a>

## 1. 미리 보기 버전의 상태

Linux 버전은 Windows 버전 0.1.8(동결되어 있으며 기준으로 쓰입니다)의 동작을 그대로 따릅니다. `Linux-vX.Y.Z` 태그의 **GitHub 시험판(pre-release)**으로 공개되며, 저장소의 '최신 릴리스'로 표시되는 일은 결코 없습니다.

**시도해 본 것** (Debian 12 가상 머신, GNOME 데스크톱, Python 3.11, 각 브라우저에 실제 YouTube 계정으로 로그인한 상태, 2026년 10월):

- **Firefox, Waterfox, Floorp, Zen Browser의 쿠키**: 브라우저가 열려 있어도 닫혀 있어도 읽혔습니다.
- **Google Chrome, Chromium, Brave, Vivaldi, Opera, Microsoft Edge의 쿠키**: 각 브라우저를 한 번 실행해 YouTube에 로그인한 뒤, 브라우저를 **닫은 상태**에서 읽혔습니다([5절](#s5) 참조). 단일 다운로드와 재생목록 검사기 모두 성공했습니다.
- **LibreWolf**: 열려 있고 로그인된 동안에만 읽을 수 있습니다(기본적으로 종료할 때 쿠키를 삭제합니다).
- Firefox 쿠키로 받은 **비공개 동영상**, 그리고 세 개 중 하나가 비공개인 재생목록.
- **패키지**: AppImage와 `.tar.gz` 아카이브는 CI가 Ubuntu 22.04에서 빌드합니다. `.deb`는 Debian 12에서 빌드, 설치, 실행, 제거까지 확인했습니다. AppImage, 아카이브, `.deb` 모두 가상 머신에서 실행했고, '메뉴에 설치'와 '제거'는 AppImage로 마우스 조작을 시험했습니다(아이콘이 메뉴와 바탕 화면에 추가된 뒤 제거됨).
- **언어와 글꼴**: 한국어 글꼴이 없는 머신에서 한국어를 선택했습니다. 'Font needed' 창이 글꼴을 제안하고, 내려받아 검증한 뒤 소프트웨어가 다시 시작되어 글자가 읽힙니다.

**아직 시도하지 않은 것**:

- 다른 배포판(Ubuntu, Fedora, Arch, openSUSE 등)과 KDE Plasma(KWallet)를 포함한 GNOME 외의 데스크톱.
- Flatpak이나 Snap으로 설치한 브라우저(관찰한 Flatpak 버전 LibreWolf의 폴더 구조는 제외).
- Chrome과 Chromium이 설치되어 있지 **않은** 상태의 Vivaldi, Opera, Edge([5절](#s5) 참조).
- aarch64 아키텍처(소프트웨어는 지원하지만, 패키지는 x86_64용으로만 빌드됩니다).
- 가상 머신이 아닌 실제 Linux 컴퓨터(실제 데스크톱과 하드웨어).
- 번역: 아직 원어민의 검토가 필요합니다.

<a id="s2"></a>

## 2. 설치

### 어떤 형식을 고를까

| 형식 | 대상 | 관리자 권한 | 메뉴 항목 |
|---|---|---|---|
| **AppImage** | 최근의 64비트 배포판이라면 어디서나 | 불필요 | '메뉴에 설치'(2.3절) |
| **`.tar.gz` 아카이브** | 위와 같음, AppImage나 FUSE 없이 | 불필요 | '메뉴에 설치' |
| **`.deb` 패키지** | Debian, Ubuntu 및 파생 배포판 | 필요(`sudo`) | 자동 |
| **소스 코드** | 개발자, 시험 | 불필요 | 없음 |

요구 사항: 2022년 이후 배포판의 64비트 Linux(x86_64)(glibc 2.35 이상). 패키지가 Ubuntu 22.04에서 빌드되기 때문입니다.

**Linux가 처음이라면**: '진짜로' 설치되어 소프트웨어 관리자에 나타나는 것은 `.deb` 패키지뿐입니다. AppImage와 아카이브는 평범한 파일 또는 폴더이며 원하는 곳에 둘 수 있습니다. 지우려면 다른 파일처럼 삭제하면 됩니다(2.2절과 2.5절). 설정은 따로 `~/.local/share/yt-dlp-GUI`(6절)에 저장되며, 삭제해도 남습니다.

파일은 [릴리스 페이지](https://github.com/harlockSuites/YT-dlp-GUI/releases)에 있습니다. 'Pre-release'로 표시된 `Linux-v…` 태그를 찾으세요.

### 2.1 다운로드 확인

`SHA256SUMS-linux.txt`도 같은 폴더에 받은 다음:

```bash
sha256sum -c SHA256SUMS-linux.txt --ignore-missing
```

있는 파일마다 `OK`가 표시되어야 합니다. 이는 내 파일이 공개된 파일과 동일하다는 뜻이지, 무해하다는 보증은 아닙니다. 소스 코드와 자동 빌드는 공개되어 있습니다.

### 2.2 AppImage

```bash
chmod +x yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

AppImage에는 FUSE 2 라이브러리가 필요합니다.

| 배포판 | 패키지 |
|---|---|
| Debian, Ubuntu 22.04 및 파생 배포판 | `libfuse2` |
| Ubuntu 24.04 이상 | `libfuse2t64` |
| Fedora | `fuse-libs` |

FUSE가 없어도 실행해 보세요. 스스로 임시 폴더에 풀어서 실행됩니다.

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage --appimage-extract-and-run
```

AppImage는 '설치'되지 않습니다. 소프트웨어 관리자에는 나타나지 않습니다. 제거하려면 파일을 삭제하세요.

```bash
rm yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

AppImage를 아이콘과 함께 응용 프로그램 메뉴에서 찾으려면 **소프트웨어 안의 '메뉴에 설치…' 기능**을 사용하세요(2.3절). 입력할 명령은 없습니다.

### 2.3 메뉴에 설치(관리자 권한 없이)

더블 클릭으로 실행한 AppImage는 응용 프로그램 메뉴에 아이콘을 남기지 않습니다. 소프트웨어에서 옵션 메뉴 › **'메뉴에 설치…'**를 선택하세요. 이 창은 다음을 합니다.

- 프로그램을 `~/.local/share/yt-dlp-GUI/app/`에 복사합니다.
- 실행기 `~/.local/share/applications/yt-dlp-gui.desktop`와 아이콘 `~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png`를 씁니다.
- 체크 상자를 선택했다면 바탕 화면에 바로 가기를 추가합니다(`gio` 도구가 있으면 GNOME용으로 '신뢰함' 표시를 합니다).
- 이후 '업데이트'(실행 중인 버전을 다시 복사합니다)와 '제거'를 제공합니다.

'제거'는 설치가 만든 것만 지우며, **설정**과 내려받은 도구는 그대로 둡니다. 우리의 내부 표시(`X-YtDlpGui-Installer=1`)가 없는 실행기는 결코 삭제되지 않습니다.

제한: 이 창은 AppImage와 아카이브에서 사용할 수 있습니다. 소스 코드에서는 AppImage를 안내하고, `.deb` 패키지에서는 소프트웨어가 이미 메뉴에 있다고 설명합니다.

프로그램이 메뉴에 없는 동안에는 AppImage와 아카이브가 시작할 때 이 설치를 스스로 제안하며, '메뉴에 설치할까요?' 창이 나타납니다. '예, 설치…'는 위의 창을 열고, '나중에'는 다음 실행 때 다시 묻고, '다시 묻지 않음'은 제안을 멈춥니다(기능은 옵션 메뉴에 그대로 남습니다).

바탕 화면 바로 가기에 경고가 표시되면 아이콘을 마우스 오른쪽 버튼으로 눌러 '실행 허용'을 선택하세요. 일부 데스크톱(GNOME은 기본적으로)은 바탕 화면에 아이콘을 표시하지 않습니다. 메뉴의 실행기는 어떤 경우에도 작동합니다.

모든 것을 직접 제거하려면:

```bash
rm -rf ~/.local/share/yt-dlp-GUI/app ~/.local/share/applications/yt-dlp-gui.desktop ~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png ~/Desktop/yt-dlp-gui.desktop
```

`.deb` 패키지가 이미 설치되어 있다면 이 기능을 쓰지 마세요. 소프트웨어가 이미 메뉴에 있어서 두 번째 'yt-dlp GUI' 항목이 생기게 됩니다(이 방법을 쓰려면 먼저 `sudo apt remove yt-dlp-gui`로 `.deb`를 제거하세요).

### 2.4 `.deb` 패키지

```bash
sudo apt install ./yt-dlp-gui_X.Y.Z_amd64.deb
```

프로그램은 `/opt/yt-dlp-gui`에 들어가며, `/usr/bin/yt-dlp-gui` 링크, 메뉴 실행기, 아이콘, 라이선스(`/usr/share/doc/yt-dlp-gui/`)가 함께 설치됩니다. `libc6 (>= 2.35)`와 `libx11-6`에 의존합니다.

제거하려면(`~/.local/share/yt-dlp-GUI`에 있는 설정은 결코 건드리지 않습니다):

```bash
sudo apt remove yt-dlp-gui
```

### 2.5 `.tar.gz` 아카이브

```bash
tar xzf yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz
```

```bash
./yt-dlp-gui/yt-dlp-gui
```

설정과 도구를 **압축을 푼 폴더 안**에 두려면(USB 메모리, 흔적을 남기지 않는 시험), 실행 파일 옆에 빈 `portable.flag` 파일을 만드세요.

```bash
touch yt-dlp-gui/portable.flag
```

이 파일이 없으면 데이터는 `~/.local/share/yt-dlp-GUI`(6절)에 저장됩니다.

아카이브는 '설치'되지 않습니다. 소프트웨어 관리자에는 나타나지 않습니다. 제거하려면 압축을 푼 폴더를 삭제하세요.

```bash
rm -rf yt-dlp-gui
```

### 2.6 소스 코드에서

```bash
python3 yt-dlp-gui.pyw
```

소스 코드에서 실행해도 설정과 내려받은 도구는 설치된 버전과 같은 폴더(`~/.local/share/yt-dlp-GUI`)에 저장됩니다. 소스 코드를 다시 받거나 그 폴더를 삭제해도 지워지지 않습니다. 데이터를 소스 코드 폴더 안에 두려면(흔적을 남기지 않는 시험) `yt-dlp-gui.pyw` 옆에 빈 `portable.flag` 파일을 만드세요.

Tkinter가 포함된 Python 3이 필요합니다.

| 배포판 | 패키지 |
|---|---|
| Debian, Ubuntu 및 파생 배포판, openSUSE | `python3-tk` |
| Fedora | `python3-tkinter` |
| Arch | `tk` |

### 2.7 업데이트

매일 하는 확인(옵션 메뉴에서 끌 수 있습니다)은 시험판을 포함해 `Linux-vX.Y.Z` 버전을 찾으며, Windows 버전은 **절대** 제안하지 않습니다. 내 설치 방식(AppImage, 아카이브, `.deb`)에 맞는 파일의 다운로드 페이지를 엽니다. **자동으로 설치되는 것은 없습니다**. 업데이트하려면:

- **메뉴에 설치한 AppImage 또는 아카이브**: 새 AppImage를 받아 실행한 다음 '메뉴에 설치… › 업데이트'를 선택합니다.
- **`.deb`**: `sudo apt install ./new-file.deb`
- **설치하지 않은 아카이브**: 새 아카이브를 이전 것 자리에 풉니다.

### 2.8 데이터까지 모두 제거하기

프로그램을 제거한 뒤(2.3~2.5절), 설정, 대기열, 내려받은 도구(yt-dlp, ffmpeg, deno)까지 지우려면:

```bash
rm -rf ~/.local/share/yt-dlp-GUI
```

내려받은 동영상은 이 폴더에 들어가지 않습니다.

<a id="s3"></a>

## 3. 첫 실행과 의존성

처음 실행하면 설치 도우미가 **yt-dlp**(`yt-dlp_linux`), **ffmpeg**(yt-dlp 공식 빌드의 `.tar.xz` 아카이브), **deno**를 GitHub 저장소에서 내려받자고 제안합니다. SHA-256 합계가 검증되고, 관리자 권한은 요구하지 않으며, 파일은 `~/.local/share/yt-dlp-GUI`(yt-dlp)와 `~/.local/share/yt-dlp-GUI/bin`(ffmpeg, ffprobe, deno)에 저장됩니다. 도우미는 옵션 메뉴에서 계속 사용할 수 있습니다.

꼭 필요한 것은 ffmpeg와 ffprobe뿐이며, deno는 권장됩니다(보조 오디오 트랙용). **AtomicParsley, MKVToolNix, aria2**는 선택 사항입니다. '의존성' 창에는 사용 중인 패키지 관리자의 명령이 표시되며, 터미널에 복사해서 쓰면 됩니다. 소프트웨어가 직접 실행하는 일은 없습니다. 같은 명령은 다음과 같습니다.

| 패키지 관리자 | 명령 |
|---|---|
| apt | `sudo apt install aria2 atomicparsley mkvtoolnix` |
| dnf | `sudo dnf install AtomicParsley aria2 mkvtoolnix` |
| pacman | `sudo pacman -S aria2 atomicparsley mkvtoolnix-cli` |
| zypper | `sudo zypper install AtomicParsley aria2 mkvtoolnix` |

<a id="s4"></a>

## 4. 브라우저 쿠키

yt-dlp는 선택한 브라우저의 쿠키를 **로컬에서** 읽습니다(보조 오디오 트랙, 자막, 비공개 동영상, 멤버 전용 콘텐츠용). 기본적으로 Linux에서 가장 많이 쓰이는 브라우저 다섯 개(Firefox, Google Chrome, Chromium, Brave, Vivaldi)가 제공됩니다. 옵션 메뉴의 **'쿠키용 브라우저…'**를 선택하면 '쿠키용 브라우저' 창이 열리고 11개 브라우저가 제공됩니다. 필요한 것을 선택하세요. ✔는 프로필 폴더가 내 컴퓨터에 존재하는 브라우저를 나타냅니다.

| 브라우저 | yt-dlp에서 읽는 이름 | 키링 | 탐색하는 프로필 폴더 |
|---|---|---|---|
| Firefox | `firefox` | 불필요 | `~/.config/mozilla/firefox`, `~/.mozilla/firefox`, Flatpak, Snap |
| Google Chrome | `chrome` | 필요 | `~/.config/google-chrome` |
| Chromium | `chromium` | 필요 | `~/.config/chromium` |
| Brave | `brave` | 필요 | `~/.config/BraveSoftware/Brave-Browser` |
| Vivaldi | `vivaldi` | 필요 | `~/.config/vivaldi` |
| Opera | `opera` | 필요 | `~/.config/opera` |
| Microsoft Edge | `edge` | 필요 | `~/.config/microsoft-edge` |
| LibreWolf, Waterfox, Floorp, Zen Browser | `firefox:` + 프로필 폴더 | 불필요 | `~/.librewolf`, `~/.config/librewolf` 등(나머지도 같은 방식), Flatpak 포함 |

Firefox 파생 브라우저는 yt-dlp가 아는 이름이 없습니다. 소프트웨어는 그 브라우저의 `cookies.sqlite` 데이터베이스를 찾아(각 폴더 아래로 최대 세 단계) 가장 최근에 사용한 프로필 폴더를 yt-dlp에 전달합니다. `XDG_CONFIG_HOME`은 절대 경로일 때 존중됩니다.

목록 옆의 **표시등**은 상태를 보여 줍니다. 빨강(꺼짐 또는 실패), 주황(시험 전 또는 진행 중), 초록(쿠키를 읽음). ↻ 버튼은 시험을 실행하며, 풍선 도움말이 오류를 설명합니다. 쿠키를 **0개** 읽은 시험은 결코 초록이 되지 않습니다.

### 자주 있는 경우

| 보이는 내용 | 있을 수 있는 원인 | 할 일 |
|---|---|---|
| 'Extracted 0 cookies' 다음에 'Sign in to confirm you're not a bot' | 브라우저가 디스크에 쿠키를 남기지 않음(LibreWolf는 기본적으로 종료 시 삭제, 한 번도 로그인하지 않은 프로필, 비공개 모드) | 열어 둔 채 YouTube에 로그인한 상태로 두거나, 개인정보 설정에서 종료 시 쿠키 삭제를 끕니다 |
| Chrome, Chromium, Brave, Vivaldi, Opera, Edge에서 'Item does not exist!' | yt-dlp가 데스크톱 키링에서 브라우저의 키를 찾지 못함 | 브라우저를 한 번 실행해 YouTube에 로그인하고 닫은 뒤 시험을 다시 실행합니다. 그래도 안 되면 [5절](#s5) |
| 'Could not copy Chrome cookie database' 또는 'database is locked' | 브라우저가 실행 중에 데이터베이스를 잠금 | 브라우저를 닫은 뒤 시험을 다시 실행합니다 |
| 'Failed to decrypt' | yt-dlp가 얻지 못한 키로 쿠키가 암호화됨 | [5절](#s5) |

### 터미널에서 브라우저 시험하기

정확한 오류를 보는 가장 좋은 방법입니다(`IDENTIFIER`는 아무 YouTube 동영상의 식별자로 바꾸세요).

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

찾아볼 줄: `Extracted N cookies from chromium`(N은 0보다 커야 합니다), `Chosen keyring: GNOMEKEYRING`(선택된 키링), `cookie version breakdown: {'v10': 0, 'v11': 50, …}`(`v11` 쿠키에는 키링이 필요하고 `v10`에는 필요 없습니다).

Firefox 파생 브라우저는 프로필 폴더를 지정하세요. 찾는 방법:

```bash
find ~ -name cookies.sqlite -path "*librewolf*" 2>/dev/null
```

Flatpak 설치에서는 `~/.var/app`에서 찾으세요.

```bash
find ~/.var/app -name cookies.sqlite 2>/dev/null
```

그런 다음 `cookies.sqlite`가 들어 있는 폴더로:

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser "firefox:/path/to/profile" -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

<a id="s5"></a>

## 5. 키링: 수동 작업

### 무엇에 쓰는가

Chromium 계열 브라우저(Chrome, Chromium, Brave, Vivaldi, Opera, Edge)는 쿠키를 암호화합니다. 암호화 키는 **데스크톱 키링**에 보관됩니다. GNOME, XFCE, Cinnamon, MATE 등에서는 GNOME Keyring(또는 'Secret Service'를 통한 호환 대체품), KDE에서는 KWallet입니다. 복호화할 때 yt-dlp는 키링에 그 키를 요청합니다. Firefox와 그 파생 브라우저에는 필요 없습니다.

알아 두면 좋은 사실 두 가지:

- **키는 브라우저를 처음 실행한 뒤에야 존재합니다.** 우리 가상 머신에서는 각 브라우저를 한 번 실행해 YouTube에 로그인하자 'Item does not exist!' 오류가 사라졌습니다. 첫 실패의 정확한 원인은 확실히 밝혀지지 않았습니다. 키링은 존재했고, 기본 키링이었으며, 잠금이 풀려 있었습니다.
- **yt-dlp가 어떤 키링을 쓰는지**는 감지된 데스크톱 환경(변수 `XDG_CURRENT_DESKTOP`과 `DESKTOP_SESSION`)에 따라 달라지며, yt-dlp의 코드(2026년 10월) 기준으로 다음과 같습니다.

| 감지된 데스크톱 | yt-dlp가 쓰는 키링 |
|---|---|
| GNOME, Cinnamon, MATE, XFCE, Pantheon, Unity, Deepin, UKUI | GNOME Keyring(`GNOMEKEYRING`) |
| KDE 4, 5, 6 | KWallet(`KWALLET`, `KWALLET5`, `KWALLET6`) |
| LXQt, KDE 3, 인식되지 않는 데스크톱(창 관리자만 있는 환경: sway, i3 등) | 없음: 평문(`BASICTEXT`) |

마지막 경우에는 yt-dlp가 `v10` 쿠키만 읽습니다. 브라우저가 키를 GNOME Keyring에 보관한다면 그 `v11` 쿠키는 복호화되지 않습니다. 이때는 터미널에서 키링을 지정해야 하며(5.6절), 소프트웨어는 아직 이 설정을 제공하지 않습니다.

키링에서 찾는 항목의 이름은 '*이름* Safe Storage'입니다. yt-dlp의 코드에 따르면 Chrome과 Vivaldi는 **'Chrome Safe Storage'**, Chromium, Opera, Edge는 **'Chromium Safe Storage'**, Brave는 **'Brave Safe Storage'**입니다. 우리 가상 머신에는 Chrome과 Chromium도 설치되어 실행된 상태였습니다. Vivaldi, Opera, Edge가 단독으로 작동하는지는 알지 못합니다.

### 5.1 키링이 존재하는가

```bash
ls -la ~/.local/share/keyrings/
```

`login.keyring` 파일('login' 키링)이 보여야 합니다. 다음으로, **기본** 키링은 무엇일까요?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets --method org.freedesktop.Secret.Service.ReadAlias default
```

응답이 `(objectpath '/org/freedesktop/secrets/collection/login',)`이면 기본 키링이 있습니다. 응답이 `'/'`이면 **없습니다**. 5.4절로 가세요.

### 5.2 잠겨 있는가

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Locked
```

`(<false>,)`: 잠금 해제됨. `(<true>,)`: 잠김. Seahorse(5.4절)로 열면 비밀번호를 묻습니다.

### 5.3 내 브라우저의 키가 들어 있는가

항목을 나열합니다.

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Items
```

응답에는 숫자로 끝나는 경로(`…/login/1`, `…/login/2` 등)가 나옵니다. 각각의 이름을 읽으려면(숫자 목록은 알맞게 바꾸세요):

```bash
for i in 1 2 3 4 5 6; do gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login/$i --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Item Label; done
```

예를 들어 `Chromium Safe Storage`, `Chrome Safe Storage`, `Brave Safe Storage`가 보여야 합니다. 이름이 빈 항목은 무해합니다. 내 브라우저의 이름이 없다면 한 번 실행해 YouTube에 로그인하고 닫은 뒤 이 명령을 다시 실행하세요.

### 5.4 Seahorse로 키링 만들기 또는 잠금 해제하기

Seahorse('암호 및 키')와 관련 도구를 설치하세요. 정확한 명령은 소프트웨어의 '쿠키용 브라우저' 창에도 있습니다.

| 패키지 관리자 | 명령 |
|---|---|
| apt | `sudo apt install gnome-keyring seahorse libsecret-tools` |
| dnf | `sudo dnf install gnome-keyring seahorse libsecret` |
| pacman | `sudo pacman -S gnome-keyring seahorse libsecret` |
| zypper | `sudo zypper install gnome-keyring seahorse libsecret-tools` |

그런 다음 실행합니다.

```bash
seahorse
```

- **기본 키링이 없을 때**: 하나 만들고('+' 버튼 또는 파일 › 새로 만들기 › 암호 키링 메뉴), 이름을 'Login'으로 한 뒤, 마우스 오른쪽 버튼 › '기본값으로 설정'을 선택합니다. 정확한 표기는 Seahorse 버전에 따라 다릅니다.
- **잠긴 키링**: 더블 클릭하거나 마우스 오른쪽 버튼 › '잠금 해제'를 선택하고 비밀번호를 입력합니다(직접 입력하세요. 소프트웨어는 비밀번호를 묻지 않습니다).
- **자동 로그인**: 비밀번호로 보호된 키링은 세션을 시작할 때 비밀번호를 입력하지 않으면 스스로 열리지 않습니다. 직접 잠금을 풀 때까지(또는 세션과 키링에 같은 비밀번호를 쓸 때까지) 잠긴 채로 남습니다.

그다음 **브라우저를 실행하고, YouTube에 로그인하고, 닫은 뒤** 시험을 다시 실행하세요(4절).

### 5.5 KDE Plasma(KWallet)

KDE에서는 yt-dlp가 KWallet(`kwallet-query`)에 질의합니다. 관리 도구의 이름은 배포판에 따라 `kwalletmanager`(또는 `kwalletmanager5`)입니다. 이 구성은 우리 시험에서 **시도하지 않았습니다**.

### 5.6 yt-dlp에 키링 지정하기(터미널)

소프트웨어는 키링 선택을 데스크톱 환경에 따라 yt-dlp에 맡깁니다. 강제로 지정하려면 브라우저 이름에 `+키링`을 붙이세요(값: `gnomekeyring`, `kwallet`, `kwallet5`, `kwallet6`, `basictext`).

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium+gnomekeyring -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Chromium이 실제로 어떤 키링을 쓰는지 알아보려면(yt-dlp의 코드에서 가져온 명령이며 여기서는 시도하지 않았습니다):

```bash
chromium --enable-logging=stderr --v=1 2>&1 | grep key_storage_
```

### 5.7 키링 없이: `--password-store=basic`(고급, 시도하지 않음)

Chromium은 `--password-store=basic`을 받아들입니다. 그러면 키를 평문(고정된, 널리 알려진 키)으로 보관하고 새 쿠키를 `v10`으로 암호화하며, yt-dlp는 이를 키링 없이 읽습니다(`chromium+basictext`). **덜 안전합니다**. 파일을 읽을 수 있는 프로그램이라면 이 쿠키를 복호화할 수 있습니다. 이 절충을 이해하는 경우에만 사용하세요. 이미 저장된 쿠키는 아마 다시 인코딩되지 않으므로 다시 로그인하세요.

### 5.8 최후의 수단

키링이 손상되었다면 **먼저 백업**하세요.

```bash
cp -a ~/.local/share/keyrings ~/keyrings-backup
```

`login.keyring`을 삭제하면 그 안에 보관된 **모든** 비밀번호(Wi-Fi, 온라인 계정 등)가 지워집니다. 결과를 이해하지 못한 채로는 하지 마세요.

<a id="s6"></a>

## 6. 파일 위치

데이터 폴더는 `$XDG_DATA_HOME/yt-dlp-GUI`(기본값 `~/.local/share/yt-dlp-GUI`)입니다. 다만 아카이브의 실행 파일(또는 `yt-dlp-gui.pyw` 스크립트) 옆에 `portable.flag`가 있으면 그 폴더가 됩니다.

| 파일 또는 폴더 | 내용 |
|---|---|
| `gui-config.json` | 설정(언어, 브라우저, 폴더, 브라우저 선택 등) |
| `download-queue.json` | 다운로드 대기열 |
| `custom-blocks.json` | 사용자 지정 옵션 블록 |
| `yt-dlp` | 도우미가 내려받은 실행 파일 |
| `bin/` | ffmpeg, ffprobe, deno |
| `cmd/` | yt-dlp의 임시 구성 파일 |
| `app/` | '메뉴에 설치'가 만든 프로그램 사본 |
| `~/.local/share/fonts/yt-dlp-GUI/`(데이터 폴더 밖) | 한국어, 일본어, 중국어용으로 내려받은 Noto 글꼴. 제거하려면: `rm -rf ~/.local/share/fonts/yt-dlp-GUI` |

<a id="s7"></a>

## 7. 문제 해결

| 문제 | 단서 |
|---|---|
| AppImage가 시작되지 않음 | 터미널에서 실행해 오류를 읽습니다. FUSE 2를 설치(2.2절)하거나 `--appimage-extract-and-run`을 추가합니다 |
| 아무것도 표시되지 않거나 라이브러리 오류 | glibc 버전을 확인합니다. `ldd --version`이 2.35 이상이어야 합니다 |
| 바탕 화면에 아이콘이 없음 | GNOME은 기본적으로 표시하지 않습니다. 응용 프로그램 메뉴를 사용하세요 |
| 바탕 화면 바로 가기에 경고가 표시됨 | 마우스 오른쪽 버튼 › '실행 허용' |
| 호스트와 가상 머신 사이의 끌어서 놓기가 작동하지 않음 | VirtualBox(Guest Additions)의 기능이며 소프트웨어의 기능이 아닙니다 |
| 화면 크기가 맞지 않음 | 소프트웨어는 시스템 글꼴(Tk)을 따릅니다. 시스템 글꼴 크기를 바꿔 보세요 |
| yt-dlp 업데이트 실패 | 옵션 메뉴의 '업데이트 & 진단'을 사용하세요. 그래도 안 되면 `yt-dlp_linux`를 내려받아 교체 창에서 선택합니다(선택한 파일은 실행 가능하게 됩니다) |
| 텍스트 대신 네모가 표시됨(한국어, 중국어, 일본어 등) | 시스템에 이 문자를 담은 글꼴이 없습니다. Debian과 Ubuntu에서는 `sudo apt install fonts-noto-cjk`(약 90 MB)를 실행한 뒤 소프트웨어를 닫았다가 다시 여세요. 다른 배포판에서는 그 배포판의 'Noto Sans CJK' 패키지를 설치하세요. 언어를 선택할 때 소프트웨어가 글꼴을 직접 내려받을 수도 있습니다(한국어, 일본어, 중국어에 한함). 관리자 권한은 필요하지 않습니다 |

<a id="s8"></a>

## 8. 버그 신고

'버그 신고' 버튼은 폴더, 사용자 이름, 이메일 주소를 가린 기술 보고서를 준비합니다. 자동으로 전송되는 것은 없습니다. Linux에서는 다음을 추가하세요.

```bash
cat /etc/os-release
```

```bash
echo "$XDG_CURRENT_DESKTOP $XDG_SESSION_TYPE"
```

그리고 소프트웨어를 **어떻게** 설치했는지(AppImage, 아카이브, `.deb`, 소스 코드) 적고, 쿠키 문제라면 **터미널 시험 결과**(4절)도 함께 적어 주세요. 쿠키 자체는 붙여 넣지 마세요.

<a id="s9"></a>

## 9. 개발자를 위한 안내

시험(가상 디스플레이에서 실행하므로 실제 화면이 필요 없습니다):

```bash
xvfb-run -a python3 -X utf8 -m unittest discover -s tests -t .
```

패키지 빌드(빌드 도구: `pip install -r packaging/requirements-build.txt`, 그리고 `appimagetool`이며, 그 경로는 `APPIMAGETOOL` 변수로 지정합니다):

```bash
python3 packaging/build_linux.py
```

```bash
python3 packaging/build_deb.py
```

결과는 `dist/`에 있습니다. 호환성을 최대로 하려면 지원하는 가장 오래된 배포판에서 빌드하세요(빌드 머신의 glibc가 프로그램을 실행하는 머신에 요구되는 최소 버전이 됩니다). `.deb`의 유용한 점검:

```bash
lintian dist/yt-dlp-gui_*_amd64.deb
```

알려진 형식상 오류는 `dir-or-file-in-opt`(프로그램이 `/opt`에 포함됨) 하나뿐입니다.

**배포**: `yt-dlp-gui.pyw`의 `__version__`을 확인하고, `CHANGELOG-linux.md`에서 해당 버전 절에 날짜를 적고, 커밋한 다음 `Linux-vX.Y.Z` 태그를 만들어 푸시합니다. 'Release Linux' 워크플로가 시험을 실행하고, AppImage, 아카이브, `.deb`를 빌드하고, 합계를 계산하여 릴리스를 **시험판(pre-release)**으로 만듭니다. '최신 릴리스'가 되는 일은 없습니다(Windows 버전 0.1.8의 업데이트 확인이 거기서 Linux 태그를 찾아서는 안 되기 때문입니다).

라이선스: MIT, 저장소의 나머지와 같습니다([LICENSE](../LICENSE) 참조).
