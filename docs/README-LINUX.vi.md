# yt-dlp GUI — phiên bản cho Linux

[Français](../README-LINUX.md) · [English](README-LINUX.en.md) · [Español](README-LINUX.es.md) · [Português](README-LINUX.pt.md) · [Italiano](README-LINUX.it.md) · [Polski](README-LINUX.pl.md) · [Magyar](README-LINUX.hu.md) · [Srpski](README-LINUX.sr.md) · [Русский](README-LINUX.ru.md) · [Tiếng Việt](README-LINUX.vi.md) · [中文](README-LINUX.zh.md) · [हिन्दी](README-LINUX.hi.md) · [日本語](README-LINUX.ja.md) · [한국어](README-LINUX.ko.md) · [Filipino](README-LINUX.fil.md)

> **Bản xem trước.** Tài liệu này bổ sung cho [README chính](README.vi.md): đây vẫn là cùng một phần mềm, nhưng ở đây chỉ nói về những gì riêng của Linux (cài đặt, cookie và chùm khóa, tệp, xử lý sự cố). Điểm mới của từng phiên bản nằm trong [CHANGELOG-linux.md](../CHANGELOG-linux.md). Các bản dịch vẫn cần người bản ngữ kiểm tra; khi có nghi ngờ, bản tiếng Pháp và tiếng Anh là bản chuẩn.

## Mục lục

1. [Tình trạng bản xem trước](#s1)
2. [Cài đặt](#s2)
3. [Lần chạy đầu tiên và các phụ thuộc](#s3)
4. [Cookie của trình duyệt](#s4)
5. [Chùm khóa: thao tác thủ công](#s5)
6. [Các tệp nằm ở đâu](#s6)
7. [Xử lý sự cố](#s7)
8. [Báo lỗi](#s8)
9. [Dành cho nhà phát triển](#s9)

<a id="s1"></a>

## 1. Tình trạng bản xem trước

Phiên bản Linux tái hiện hành vi của phiên bản Windows 0.1.7 (đã đóng băng, dùng làm mẫu). Nó được phát hành dưới dạng **bản phát hành trước (pre-release) trên GitHub** với các nhãn `Linux-vX.Y.Z`: không bao giờ được trình bày là «bản phát hành mới nhất» của kho mã.

**Những gì đã thử** (máy ảo Debian 12, màn hình nền GNOME, Python 3.11, một tài khoản YouTube thật đã đăng nhập trong từng trình duyệt, tháng 10 năm 2026):

- **Cookie của Firefox, Waterfox, Floorp và Zen Browser**: đọc được khi trình duyệt đang mở hoặc đã đóng.
- **Cookie của Google Chrome, Chromium, Brave, Vivaldi, Opera và Microsoft Edge**: đọc được khi trình duyệt **đã đóng**, sau khi mở từng trình duyệt một lần và đăng nhập YouTube trong đó (xem [mục 5](#s5)). Tải xuống đơn lẻ và Trình kiểm tra danh sách phát đều thành công.
- **LibreWolf**: chỉ đọc được khi nó đang mở và đã đăng nhập (theo mặc định nó xóa cookie khi đóng).
- **Video riêng tư** với cookie của Firefox, và một danh sách phát ba video trong đó có một video riêng tư.
- **Gói**: AppImage và tệp nén `.tar.gz` do CI dựng trên Ubuntu 22.04; gói `.deb` đã được dựng, cài, chạy và gỡ trên Debian 12; AppImage, tệp nén và `.deb` đều đã được chạy trong máy ảo, và «Cài vào menu» / «Gỡ cài đặt» đã được thử bằng chuột với AppImage (biểu tượng được thêm rồi gỡ khỏi menu và Màn hình nền).
- **Ngôn ngữ và phông chữ**: chọn tiếng Hàn trên máy không có phông chữ Hàn; cửa sổ «Font needed» đề nghị phông chữ, nó được tải và kiểm tra, phần mềm khởi động lại và chữ đọc được.

**Những gì chưa thử**:

- các bản phân phối khác (Ubuntu, Fedora, Arch, openSUSE…) và các màn hình nền không phải GNOME, kể cả KDE Plasma (KWallet);
- trình duyệt cài dưới dạng Flatpak hoặc Snap (trừ cách bố trí của LibreWolf trong Flatpak, đã được quan sát);
- Vivaldi, Opera hoặc Edge **khi không có** Chrome và Chromium được cài (xem [mục 5](#s5));
- kiến trúc aarch64 (phần mềm có hỗ trợ, nhưng các gói chỉ được dựng cho x86_64);
- một máy tính Linux thật, ngoài máy ảo (màn hình nền và phần cứng thật);
- các bản dịch: vẫn cần người bản ngữ kiểm tra.

<a id="s2"></a>

## 2. Cài đặt

### Chọn định dạng nào

| Định dạng | Dành cho ai | Quyền quản trị | Mục trong menu |
|---|---|---|---|
| **AppImage** | mọi bản phân phối 64-bit gần đây | không | «Cài vào menu» (mục 2.3) |
| **Tệp nén `.tar.gz`** | như trên, không cần AppImage hay FUSE | không | «Cài vào menu» |
| **Gói `.deb`** | Debian, Ubuntu và các bản phái sinh | có (`sudo`) | tự động |
| **Mã nguồn** | nhà phát triển, thử nghiệm | không | không có |

Yêu cầu: Linux 64-bit (x86_64) thuộc bản phân phối từ năm 2022 trở lên (glibc 2.35 trở lên), vì các gói được dựng trên Ubuntu 22.04.

**Nếu bạn mới dùng Linux**: chỉ gói `.deb` được cài «thật sự» và hiện trong trình quản lý phần mềm. AppImage và tệp nén là các tệp hoặc thư mục bình thường, để ở đâu tùy bạn: muốn gỡ thì chỉ cần xóa chúng như bất kỳ tệp nào khác (mục 2.2 và 2.5). Cài đặt của chúng được lưu riêng, trong `~/.local/share/yt-dlp-GUI` (mục 6), và vẫn còn sau khi xóa.

Các tệp nằm ở [trang các bản phát hành](https://github.com/harlockSuites/YT-dlp-GUI/releases): tìm các nhãn `Linux-v…`, được đánh dấu «Pre-release».

### 2.1 Kiểm tra tệp đã tải

Tải thêm `SHA256SUMS-linux.txt` vào cùng thư mục, rồi:

```bash
sha256sum -c SHA256SUMS-linux.txt --ignore-missing
```

Mỗi tệp có mặt phải hiện `OK`. Điều này chứng minh tệp của bạn giống hệt bản đã phát hành, chứ không chứng minh nó vô hại: mã nguồn và quy trình dựng tự động đều công khai.

### 2.2 AppImage

```bash
chmod +x yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

AppImage cần thư viện FUSE 2:

| Bản phân phối | Gói |
|---|---|
| Debian, Ubuntu 22.04 và các bản phái sinh | `libfuse2` |
| Ubuntu 24.04 trở lên | `libfuse2t64` |
| Fedora | `fuse-libs` |

Nếu không có FUSE, vẫn cứ chạy nó: nó tự giải nén vào một thư mục tạm:

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage --appimage-extract-and-run
```

AppImage không được «cài đặt»: nó không hiện trong trình quản lý phần mềm. Muốn gỡ, hãy xóa tệp:

```bash
rm yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

Để thấy AppImage trong menu ứng dụng cùng biểu tượng, hãy dùng chức năng **«Cài vào menu…» ngay trong phần mềm** (mục 2.3): không có lệnh nào phải gõ.

### 2.3 Cài vào menu (không cần quyền quản trị)

AppImage mở bằng cách nhấp đúp không để lại biểu tượng nào trong menu ứng dụng. Trong phần mềm: menu tùy chọn › **«Cài vào menu…»**. Cửa sổ này:

- sao chép chương trình vào `~/.local/share/yt-dlp-GUI/app/`;
- ghi trình khởi chạy `~/.local/share/applications/yt-dlp-gui.desktop` và biểu tượng `~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png`;
- thêm, nếu ô được chọn, một lối tắt trên Màn hình nền (được đánh dấu «tin cậy» cho GNOME khi có công cụ `gio`);
- rồi đề nghị «Cập nhật» (sao chép lại phiên bản đang chạy) và «Gỡ cài đặt».

«Gỡ cài đặt» chỉ gỡ những gì quá trình cài đặt đã tạo và **giữ lại cài đặt của bạn** cùng các công cụ đã tải. Một trình khởi chạy không có dấu nội bộ của chúng tôi (`X-YtDlpGui-Installer=1`) sẽ không bao giờ bị xóa.

Giới hạn: cửa sổ này dùng được từ AppImage và tệp nén. Từ mã nguồn, nó hướng bạn sang AppImage; từ gói `.deb`, nó giải thích rằng phần mềm đã có trong menu.

Nếu lối tắt trên Màn hình nền hiện cảnh báo: nhấp chuột phải vào biểu tượng › «Cho phép khởi chạy». Một số màn hình nền (GNOME theo mặc định) không hiện biểu tượng trên Màn hình nền: trình khởi chạy trong menu luôn hoạt động.

Để gỡ mọi thứ thủ công:

```bash
rm -rf ~/.local/share/yt-dlp-GUI/app ~/.local/share/applications/yt-dlp-gui.desktop ~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png ~/Desktop/yt-dlp-gui.desktop
```

Nếu gói `.deb` đã được cài, đừng dùng chức năng này: phần mềm đã có trong menu và sẽ xuất hiện mục «yt-dlp GUI» thứ hai (hãy gỡ `.deb` trước bằng `sudo apt remove yt-dlp-gui` nếu bạn thích cách này).

### 2.4 Gói `.deb`

```bash
sudo apt install ./yt-dlp-gui_X.Y.Z_amd64.deb
```

Chương trình được đặt vào `/opt/yt-dlp-gui`, cùng liên kết `/usr/bin/yt-dlp-gui`, trình khởi chạy trong menu, biểu tượng và giấy phép (`/usr/share/doc/yt-dlp-gui/`). Nó phụ thuộc vào `libc6 (>= 2.35)` và `libx11-6`.

Để gỡ nó (cài đặt của bạn, trong `~/.local/share/yt-dlp-GUI`, không bao giờ bị động đến):

```bash
sudo apt remove yt-dlp-gui
```

### 2.5 Tệp nén `.tar.gz`

```bash
tar xzf yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz
```

```bash
./yt-dlp-gui/yt-dlp-gui
```

Để giữ cài đặt và công cụ **bên trong thư mục đã giải nén** (USB, thử nghiệm không để lại dấu vết), hãy tạo một tệp trống `portable.flag` cạnh tệp thực thi:

```bash
touch yt-dlp-gui/portable.flag
```

Nếu không có tệp này, dữ liệu sẽ nằm trong `~/.local/share/yt-dlp-GUI` (mục 6).

Tệp nén không được «cài đặt»: nó không hiện trong trình quản lý phần mềm. Muốn gỡ, hãy xóa thư mục đã giải nén:

```bash
rm -rf yt-dlp-gui
```

### 2.6 Từ mã nguồn

```bash
python3 yt-dlp-gui.pyw
```

Khi chạy từ mã nguồn, cài đặt và công cụ đã tải nằm trong cùng thư mục như các phiên bản đã cài (`~/.local/share/yt-dlp-GUI`): tải lại mã nguồn hoặc xóa thư mục của nó không làm mất chúng. Để giữ dữ liệu trong thư mục mã nguồn (thử nghiệm không để lại dấu vết), hãy tạo một tệp trống `portable.flag` cạnh `yt-dlp-gui.pyw`.

Cần Python 3 có Tkinter:

| Bản phân phối | Gói |
|---|---|
| Debian, Ubuntu và các bản phái sinh, openSUSE | `python3-tk` |
| Fedora | `python3-tkinter` |
| Arch | `tk` |

### 2.7 Cập nhật

Một lần kiểm tra hằng ngày (có thể tắt trong menu tùy chọn) tìm các phiên bản `Linux-vX.Y.Z`, kể cả bản phát hành trước, và **không bao giờ** đề xuất phiên bản Windows. Nó mở trang tải xuống của tệp phù hợp với cách cài của bạn (AppImage, tệp nén hoặc `.deb`); **không có gì được cài tự động**. Để cập nhật:

- **AppImage hoặc tệp nén đã cài vào menu**: tải AppImage mới, chạy nó, rồi «Cài vào menu… › Cập nhật»;
- **`.deb`**: `sudo apt install ./new-file.deb`;
- **tệp nén chưa cài**: giải nén tệp nén mới vào chỗ của tệp cũ.

### 2.8 Gỡ tất cả, kể cả dữ liệu

Sau khi gỡ chương trình (các mục 2.3 đến 2.5), để xóa luôn cài đặt, hàng đợi và các công cụ đã tải (yt-dlp, ffmpeg, deno):

```bash
rm -rf ~/.local/share/yt-dlp-GUI
```

Các video bạn đã tải không bao giờ nằm trong thư mục này.

<a id="s3"></a>

## 3. Lần chạy đầu tiên và các phụ thuộc

Ở lần chạy đầu tiên, trình hướng dẫn cài đặt đề nghị tải **yt-dlp** (`yt-dlp_linux`), **ffmpeg** (tệp nén `.tar.xz` của các bản dựng chính thức của yt-dlp) và **deno** từ các kho GitHub của chúng. Tổng kiểm SHA-256 được xác minh, không cần quyền quản trị, và các tệp nằm trong `~/.local/share/yt-dlp-GUI` (yt-dlp) và `~/.local/share/yt-dlp-GUI/bin` (ffmpeg, ffprobe, deno). Trình hướng dẫn vẫn có trong menu tùy chọn.

Chỉ ffmpeg và ffprobe là thiết yếu; deno được khuyến nghị (rãnh âm thanh phụ). **AtomicParsley, MKVToolNix và aria2** là tùy chọn: cửa sổ «Phụ thuộc» hiện lệnh của trình quản lý gói của bạn, để sao chép vào terminal. Phần mềm không bao giờ tự chạy lệnh đó. Cũng là các lệnh ấy:

| Trình quản lý gói | Lệnh |
|---|---|
| apt | `sudo apt install aria2 atomicparsley mkvtoolnix` |
| dnf | `sudo dnf install AtomicParsley aria2 mkvtoolnix` |
| pacman | `sudo pacman -S aria2 atomicparsley mkvtoolnix-cli` |
| zypper | `sudo zypper install AtomicParsley aria2 mkvtoolnix` |

<a id="s4"></a>

## 4. Cookie của trình duyệt

yt-dlp đọc cookie **ngay trên máy**, trong trình duyệt bạn chọn (rãnh âm thanh phụ, phụ đề, video riêng tư, nội dung dành cho thành viên). Theo mặc định, phần mềm đề xuất năm trình duyệt được dùng nhiều nhất trên Linux (Firefox, Google Chrome, Chromium, Brave, Vivaldi). Mục **«Trình duyệt cho cookie…»** trong menu tùy chọn mở cửa sổ «Trình duyệt cho cookie», đề xuất 11 trình duyệt: hãy chọn những cái bạn cần; dấu ✔ đánh dấu những trình duyệt có thư mục hồ sơ tồn tại trên máy của bạn.

| Trình duyệt | yt-dlp đọc dưới tên | Chùm khóa | Thư mục hồ sơ được tìm |
|---|---|---|---|
| Firefox | `firefox` | không | `~/.config/mozilla/firefox`, `~/.mozilla/firefox`, Flatpak, Snap |
| Google Chrome | `chrome` | có | `~/.config/google-chrome` |
| Chromium | `chromium` | có | `~/.config/chromium` |
| Brave | `brave` | có | `~/.config/BraveSoftware/Brave-Browser` |
| Vivaldi | `vivaldi` | có | `~/.config/vivaldi` |
| Opera | `opera` | có | `~/.config/opera` |
| Microsoft Edge | `edge` | có | `~/.config/microsoft-edge` |
| LibreWolf, Waterfox, Floorp, Zen Browser | `firefox:` + thư mục hồ sơ | không | `~/.librewolf`, `~/.config/librewolf`… (cùng cách bố trí cho các trình duyệt còn lại), gồm cả Flatpak |

Các bản phái sinh của Firefox không có tên mà yt-dlp biết: phần mềm tìm cơ sở dữ liệu `cookies.sqlite` của chúng (tối đa ba cấp dưới thư mục của chúng) và đưa cho yt-dlp thư mục của hồ sơ được dùng gần đây nhất. `XDG_CONFIG_HOME` được tôn trọng khi nó là đường dẫn tuyệt đối.

**Đèn báo** bên cạnh danh sách cho biết trạng thái: đỏ (đã tắt hoặc thất bại), cam (chưa thử hoặc đang chạy), xanh (đã đọc được cookie). Nút ↻ chạy một phép thử; chú giải giải thích lỗi. Một phép thử đọc được **0 cookie** không bao giờ hiện màu xanh.

### Các trường hợp thường gặp

| Điều bạn thấy | Nguyên nhân có thể | Cần làm gì |
|---|---|---|
| «Extracted 0 cookies» rồi «Sign in to confirm you're not a bot» | trình duyệt không giữ cookie nào trên đĩa (LibreWolf theo mặc định xóa chúng khi đóng; hồ sơ chưa từng đăng nhập; chế độ riêng tư) | để nó mở và đã đăng nhập YouTube, hoặc tắt việc xóa cookie khi đóng trong cài đặt quyền riêng tư của nó |
| «Item does not exist!» với Chrome, Chromium, Brave, Vivaldi, Opera hoặc Edge | yt-dlp không tìm thấy khóa của trình duyệt trong chùm khóa của máy tính | mở trình duyệt một lần, đăng nhập YouTube, đóng nó, chạy lại phép thử; nếu không được, xem [mục 5](#s5) |
| «Could not copy Chrome cookie database» hoặc «database is locked» | trình duyệt khóa cơ sở dữ liệu của nó khi đang chạy | đóng nó, rồi chạy lại phép thử |
| «Failed to decrypt» | cookie được mã hóa bằng một khóa mà yt-dlp không lấy được | [mục 5](#s5) |

### Thử một trình duyệt từ terminal

Đây là cách tốt nhất để thấy đúng lỗi (thay `IDENTIFIER` bằng mã định danh của một video YouTube bất kỳ):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Các dòng cần tìm: `Extracted N cookies from chromium` (N phải lớn hơn 0), `Chosen keyring: GNOMEKEYRING` (chùm khóa đã được chọn) và `cookie version breakdown: {'v10': 0, 'v11': 50, …}` (cookie `v11` cần chùm khóa, cookie `v10` thì không).

Với một bản phái sinh của Firefox, hãy chỉ ra thư mục hồ sơ. Để tìm nó:

```bash
find ~ -name cookies.sqlite -path "*librewolf*" 2>/dev/null
```

Với bản cài Flatpak, hãy tìm trong `~/.var/app`:

```bash
find ~/.var/app -name cookies.sqlite 2>/dev/null
```

Sau đó, với thư mục chứa `cookies.sqlite`:

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser "firefox:/path/to/profile" -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

<a id="s5"></a>

## 5. Chùm khóa: thao tác thủ công

### Dùng để làm gì

Các trình duyệt thuộc họ Chromium (Chrome, Chromium, Brave, Vivaldi, Opera, Edge) mã hóa cookie của chúng. Khóa mã hóa được cất trong **chùm khóa của máy tính**: GNOME Keyring (hoặc một giải pháp tương thích, thông qua «Secret Service») trên GNOME, XFCE, Cinnamon, MATE…, KWallet trên KDE. Để giải mã, yt-dlp yêu cầu chùm khóa cung cấp khóa đó. Firefox và các bản phái sinh không cần đến nó.

Hai điều hữu ích:

- **Khóa chỉ tồn tại sau khi trình duyệt được mở lần đầu.** Trong máy ảo của chúng tôi, lỗi «Item does not exist!» biến mất khi mỗi trình duyệt được mở một lần và đăng nhập YouTube. Nguyên nhân chính xác của lần thất bại đầu tiên không được xác lập chắc chắn: chùm khóa đã tồn tại, là chùm khóa mặc định và đã được mở khóa.
- **yt-dlp dùng chùm khóa nào** tùy thuộc vào môi trường màn hình nền được phát hiện (các biến `XDG_CURRENT_DESKTOP` và `DESKTOP_SESSION`), theo mã của yt-dlp (tháng 10 năm 2026):

| Màn hình nền được phát hiện | Chùm khóa yt-dlp sử dụng |
|---|---|
| GNOME, Cinnamon, MATE, XFCE, Pantheon, Unity, Deepin, UKUI | GNOME Keyring (`GNOMEKEYRING`) |
| KDE 4, 5, 6 | KWallet (`KWALLET`, `KWALLET5`, `KWALLET6`) |
| LXQt, KDE 3, màn hình nền không nhận ra (chỉ có trình quản lý cửa sổ: sway, i3…) | không dùng: văn bản thuần (`BASICTEXT`) |

Ở trường hợp cuối, yt-dlp chỉ đọc cookie `v10`: nếu trình duyệt của bạn cất khóa trong GNOME Keyring, cookie `v11` của nó sẽ không được giải mã. Khi đó bạn phải ép chùm khóa từ terminal (mục 5.6); phần mềm chưa có tùy chọn này.

Các mục được tìm trong chùm khóa có tên «*tên* Safe Storage». Theo mã của yt-dlp, đó là **«Chrome Safe Storage»** cho Chrome và Vivaldi, **«Chromium Safe Storage»** cho Chromium, Opera và Edge, **«Brave Safe Storage»** cho Brave. Trong máy ảo của chúng tôi, Chrome và Chromium cũng đã được cài và đã chạy: chúng tôi không biết liệu Vivaldi, Opera hay Edge có hoạt động một mình hay không.

### 5.1 Chùm khóa có tồn tại không?

```bash
ls -la ~/.local/share/keyrings/
```

Bạn phải thấy một tệp `login.keyring` (chùm khóa «login»). Tiếp theo, chùm khóa nào là chùm khóa **mặc định**?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets --method org.freedesktop.Secret.Service.ReadAlias default
```

Trả lời `(objectpath '/org/freedesktop/secrets/collection/login',)`: có chùm khóa mặc định. Trả lời `'/'`: **không có**, hãy sang mục 5.4.

### 5.2 Nó có bị khóa không?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Locked
```

`(<false>,)`: đã mở khóa. `(<true>,)`: đang khóa; hãy mở nó bằng Seahorse (mục 5.4), chương trình sẽ hỏi mật khẩu của nó.

### 5.3 Khóa của trình duyệt tôi có trong đó không?

Liệt kê các mục:

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Items
```

Kết quả cho các đường dẫn kết thúc bằng một số (`…/login/1`, `…/login/2`…). Để đọc tên của từng mục (hãy chỉnh danh sách số cho phù hợp):

```bash
for i in 1 2 3 4 5 6; do gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login/$i --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Item Label; done
```

Bạn sẽ thấy, ví dụ, `Chromium Safe Storage`, `Chrome Safe Storage` hoặc `Brave Safe Storage`. Các tên trống là vô hại. Nếu thiếu tên trình duyệt của bạn: mở nó một lần, đăng nhập YouTube, đóng nó, rồi chạy lại lệnh này.

### 5.4 Tạo hoặc mở khóa một chùm khóa bằng Seahorse

Cài Seahorse («Mật khẩu và khóa») và các công cụ liên quan. Lệnh chính xác cũng có trong cửa sổ «Trình duyệt cho cookie» của phần mềm:

| Trình quản lý gói | Lệnh |
|---|---|
| apt | `sudo apt install gnome-keyring seahorse libsecret-tools` |
| dnf | `sudo dnf install gnome-keyring seahorse libsecret` |
| pacman | `sudo pacman -S gnome-keyring seahorse libsecret` |
| zypper | `sudo zypper install gnome-keyring seahorse libsecret-tools` |

Sau đó mở nó:

```bash
seahorse
```

- **Chưa có chùm khóa mặc định**: tạo một chùm khóa (nút «+» hoặc menu Tệp › Mới › chùm khóa mật khẩu), đặt tên «Login», rồi nhấp chuột phải vào nó › «Đặt làm mặc định». Tên nhãn chính xác thay đổi theo phiên bản Seahorse.
- **Chùm khóa đang khóa**: nhấp đúp hoặc nhấp chuột phải › «Mở khóa», rồi nhập mật khẩu của nó (hãy tự nhập, phần mềm không bao giờ hỏi).
- **Đăng nhập tự động**: một chùm khóa được bảo vệ bằng mật khẩu không thể tự mở nếu bạn không nhập mật khẩu khi bắt đầu phiên; nó vẫn bị khóa cho đến khi bạn mở khóa (hoặc cho đến khi bạn dùng cùng một mật khẩu cho phiên và cho chùm khóa).

Sau đó **mở trình duyệt, đăng nhập YouTube, đóng nó**, rồi chạy lại phép thử (mục 4).

### 5.5 KDE Plasma (KWallet)

Trên KDE, yt-dlp truy vấn KWallet (`kwallet-query`). Trình quản lý có tên `kwalletmanager` (hoặc `kwalletmanager5`) tùy bản phân phối. Cấu hình này **chưa được thử** trong các phép thử của chúng tôi.

### 5.6 Ép chùm khóa cho yt-dlp (terminal)

Phần mềm để yt-dlp tự chọn chùm khóa theo màn hình nền. Để ép nó, hãy thêm `+CHÙM` vào tên trình duyệt (giá trị: `gnomekeyring`, `kwallet`, `kwallet5`, `kwallet6`, `basictext`):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium+gnomekeyring -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Để biết một trình duyệt Chromium thực sự dùng chùm khóa nào (lệnh lấy từ mã của yt-dlp, chưa thử ở đây):

```bash
chromium --enable-logging=stderr --v=1 2>&1 | grep key_storage_
```

### 5.7 Không dùng chùm khóa: `--password-store=basic` (nâng cao, chưa thử)

Chromium chấp nhận `--password-store=basic`: khi đó nó cất khóa ở dạng rõ (một khóa cố định, ai cũng biết) và mã hóa cookie mới theo dạng `v10`, loại yt-dlp đọc được mà không cần chùm khóa (`chromium+basictext`). **Cách này kém an toàn hơn**: bất kỳ chương trình nào đọc được tệp của bạn đều có thể giải mã các cookie này. Chỉ dùng nếu bạn hiểu sự đánh đổi này; cookie đã lưu có lẽ không được mã hóa lại: hãy đăng nhập lại.

### 5.8 Biện pháp cuối cùng

Nếu một chùm khóa bị hỏng, **hãy sao lưu nó trước**:

```bash
cp -a ~/.local/share/keyrings ~/keyrings-backup
```

Xóa `login.keyring` sẽ xóa **mọi** mật khẩu nó chứa (Wi-Fi, tài khoản trực tuyến…): đừng làm khi chưa hiểu hậu quả.

<a id="s6"></a>

## 6. Các tệp nằm ở đâu

Thư mục dữ liệu là `$XDG_DATA_HOME/yt-dlp-GUI` (theo mặc định `~/.local/share/yt-dlp-GUI`), trừ khi `portable.flag` nằm cạnh tệp thực thi của tệp nén (hoặc tập lệnh `yt-dlp-gui.pyw`).

| Tệp hoặc thư mục | Nội dung |
|---|---|
| `gui-config.json` | cài đặt (ngôn ngữ, trình duyệt, thư mục, lựa chọn trình duyệt…) |
| `download-queue.json` | hàng đợi tải xuống |
| `custom-blocks.json` | các khối tùy chọn tự tạo |
| `yt-dlp` | tệp thực thi do trình hướng dẫn tải về |
| `bin/` | ffmpeg, ffprobe, deno |
| `cmd/` | các tệp cấu hình tạm của yt-dlp |
| `app/` | bản sao chương trình do «Cài vào menu» tạo ra |
| `~/.local/share/fonts/yt-dlp-GUI/` (nằm ngoài thư mục dữ liệu) | phông chữ Noto đã tải cho tiếng Hàn, Nhật hoặc Trung; để gỡ nó: `rm -rf ~/.local/share/fonts/yt-dlp-GUI` |

<a id="s7"></a>

## 7. Xử lý sự cố

| Sự cố | Gợi ý |
|---|---|
| AppImage không khởi động | chạy nó từ terminal để đọc lỗi; cài FUSE 2 (mục 2.2) hoặc thêm `--appimage-extract-and-run` |
| Không hiện gì, hoặc lỗi thư viện | kiểm tra phiên bản glibc: `ldd --version` phải cho ra 2.35 trở lên |
| Không có biểu tượng trên Màn hình nền | GNOME theo mặc định không hiện biểu tượng; hãy dùng menu ứng dụng |
| Lối tắt trên Màn hình nền có cảnh báo | nhấp chuột phải › «Cho phép khởi chạy» |
| Kéo và thả giữa máy chủ và máy ảo không hoạt động | đó là tính năng của VirtualBox (Guest Additions), không phải của phần mềm |
| Giao diện có kích thước sai | phần mềm theo phông chữ của hệ thống (Tk); hãy thử cỡ phông chữ hệ thống khác |
| Cập nhật yt-dlp thất bại | dùng «Cập nhật & Chẩn đoán» trong menu tùy chọn; nếu không, tải `yt-dlp_linux` và chọn nó trong cửa sổ thay thế (tệp được chọn sẽ được cấp quyền thực thi) |
| Hiện ô vuông thay cho chữ (tiếng Hàn, Trung, Nhật…) | hệ thống không có phông chữ nào chứa các ký tự này; trên Debian và Ubuntu: `sudo apt install fonts-noto-cjk` (~90 MB), rồi đóng và mở lại phần mềm; trên bản phân phối khác, cài gói «Noto Sans CJK» của bản phân phối đó; phần mềm cũng có thể tự tải phông chữ (tiếng Hàn, Nhật, Trung) khi bạn chọn ngôn ngữ, không cần quyền quản trị |

<a id="s8"></a>

## 8. Báo lỗi

Nút «Báo lỗi» chuẩn bị một báo cáo kỹ thuật trong đó các thư mục, tên người dùng và địa chỉ e-mail của bạn được che đi; không có gì được gửi tự động. Với Linux, hãy thêm vào đó:

```bash
cat /etc/os-release
```

```bash
echo "$XDG_CURRENT_DESKTOP $XDG_SESSION_TYPE"
```

và cho biết bạn đã cài phần mềm **bằng cách nào** (AppImage, tệp nén, `.deb`, mã nguồn) và, với sự cố cookie, **kết quả phép thử từ terminal** (mục 4), đừng dán cookie của bạn.

<a id="s9"></a>

## 9. Dành cho nhà phát triển

Kiểm thử (trên màn hình ảo, không cần màn hình thật):

```bash
xvfb-run -a python3 -X utf8 -m unittest discover -s tests -t .
```

Dựng các gói (công cụ dựng: `pip install -r packaging/requirements-build.txt`, cộng với `appimagetool`, đường dẫn của nó được cho bởi biến `APPIMAGETOOL`):

```bash
python3 packaging/build_linux.py
```

```bash
python3 packaging/build_deb.py
```

Kết quả nằm trong `dist/`. Để tương thích tốt nhất, hãy dựng trên bản phân phối cũ nhất được hỗ trợ (glibc của máy dựng là mức tối thiểu được yêu cầu ở các máy chạy chương trình). Các kiểm tra hữu ích cho gói `.deb`:

```bash
lintian dist/yt-dlp-gui_*_amd64.deb
```

Lỗi hình thức duy nhất đã biết là `dir-or-file-in-opt` (chương trình được đặt trong `/opt`).

**Phát hành**: kiểm tra `__version__` trong `yt-dlp-gui.pyw`, ghi ngày vào mục của phiên bản trong `CHANGELOG-linux.md`, commit, rồi tạo và đẩy nhãn `Linux-vX.Y.Z`. Quy trình «Release Linux» chạy các bài kiểm thử, dựng AppImage, tệp nén và `.deb`, tính các tổng kiểm và tạo bản phát hành dưới dạng **bản phát hành trước (pre-release)**, không bao giờ là «bản phát hành mới nhất» (phần kiểm tra cập nhật của phiên bản Windows 0.1.7 không được tìm thấy nhãn Linux ở đó).

Giấy phép: MIT, như phần còn lại của kho mã (xem [LICENSE](../LICENSE)).
