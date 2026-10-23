# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

Giao diện đồ họa cho [yt-dlp](https://github.com/yt-dlp/yt-dlp), được thiết kế để ai cũng dùng được mà vẫn khai thác trọn vẹn khả năng của nó.

> **Dự án đang được phát triển.** Một số tính năng có thể thay đổi, chưa hoàn chỉnh hoặc còn lỗi. Có cho Windows; đồng thời cung cấp **bản xem trước cho Linux**, được kiểm thử ít hơn.

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## Tính năng

### Trình tải đơn lẻ và hàng đợi

- **Tùy chọn**: chất lượng tối đa (đến 4K), chỉ âm thanh (MP3), phụ đề (định dạng vtt, srt, ass), nhúng phụ đề và ảnh thu nhỏ, ngôn ngữ âm thanh chính, các rãnh âm thanh phụ (tệp MKV nhiều rãnh) và thư viện «khối script» (xử lý sau, xuất, mạng, hành vi) mà bạn có thể bổ sung bằng khối của riêng mình.
- **Nhiều track âm thanh**: trong tệp MKV, mỗi track âm thanh mang nhãn ngôn ngữ của nó («vie», «eng»…); trình phát hiển thị nhãn này trong menu âm thanh.
- **Lệnh được tạo**: lệnh yt-dlp tương ứng với lựa chọn của bạn được hiển thị trực tiếp.
- **Hàng đợi**: thêm URL hiện tại, rồi chạy toàn bộ hàng đợi, từ một mục trở đi, một video hoặc một khoảng; tạm dừng và tiếp tục, bỏ qua mục đang chạy, dừng và dọn các tệp dở dang. Hàng đợi được giữ lại giữa các phiên.
- **Tên tệp đã tồn tại**: một video đơn lẻ có tên đã có trong thư mục đích sẽ được thêm hậu tố (`_2`, `_3`…) để không ghi đè gì cả. Danh sách phát tải từ trình tải này không được đánh số lại: các video đã có trong thư mục sẽ bị bỏ qua («has already been downloaded»).

### Trình kiểm tra danh sách phát

- **Phân tích** danh sách phát: mỗi video được liệt kê cùng các rãnh âm thanh và phụ đề khả dụng; các mục bị ẩn, riêng tư hoặc đã xóa được bỏ qua mà không chặn phần còn lại.
- **Quy tắc chung** (chất lượng, chỉ âm thanh, định dạng và nhúng phụ đề, ảnh thu nhỏ, đánh số, ngôn ngữ, khối script, thư mục đầu ra) với **ngoại lệ theo từng video** cho ngôn ngữ chính, rãnh phụ và phụ đề.
- **Mã màu**: đỏ khi thiếu ngôn ngữ chính, cam khi thiếu rãnh phụ hoặc phụ đề.
- **Tải phần đã chọn** với nhật ký, tạm dừng, tiếp tục và bỏ qua; nếu các rãnh yêu cầu không tồn tại, video được thử lại mà không có chúng, sau đó **bản tổng kết** cho biết điều gì đã thành công, được điều chỉnh hay thất bại.

### Thư mục thông minh và sổ đăng ký

- **Thư mục thông minh**: yt-dlp bỏ qua các video đã tải nhờ một sổ đăng ký lưu trong thư mục đầu ra. Tệp `.yt-dlp-registre.json` chứa mã định danh, URL, tiêu đề, thời lượng, tên tệp và ngày của mỗi video; `.yt-dlp-archive.txt`, do yt-dlp đọc, được tạo ra từ đó.
- **Kiểm tra hồi tố**: nếu các video trong phần đã chọn đã có trong thư mục nhưng chưa có trong sổ đăng ký, một cửa sổ đề nghị ghi chúng vào và bỏ qua (so sánh tiêu đề). Bạn có thể bỏ chọn các trường hợp khớp sai.
- **Cập nhật sổ đăng ký**: đếm số video trong thư mục, trong sổ đăng ký và còn thiếu, rồi tìm thông tin còn thiếu trên YouTube (tiêu đề và thời lượng qua ffprobe). Không có gì được ghi nếu bạn chưa xác nhận, và hai nút mở tệp cục bộ hoặc liên kết YouTube tìm được để bạn kiểm tra.

![yt-dlp GUI](img/registry.en.png)

### Cookie của trình duyệt

- Chọn trình duyệt (Chrome, Firefox, Edge, Brave, Opera) mà yt-dlp đọc cookie cục bộ: cần cho các rãnh âm thanh phụ và một số phụ đề. **Nên dùng Firefox.**
- **Kết quả thử nghiệm của chúng tôi** (Windows 11, tháng 10 năm 2026, đã đăng nhập tài khoản YouTube trên từng trình duyệt): **Firefox** hoạt động, dù trình duyệt đang mở hay đã đóng. **Opera** chỉ hoạt động **khi trình duyệt đã đóng**: nó khóa cơ sở dữ liệu cookie khi đang mở và yt-dlp sẽ hiện «Could not copy Chrome cookie database». **Chrome, Edge và Brave** thất bại ngay cả khi đã đóng: chúng mã hóa cookie theo cách yt-dlp không phải lúc nào cũng đọc được. Những giới hạn này đến từ trình duyệt và yt-dlp chứ không phải từ phần mềm, và có thể thay đổi khi chúng cập nhật.
- Nếu trình duyệt được đặt để **xóa cookie khi đóng** (hoặc bạn duyệt ở chế độ riêng tư), sẽ không còn cookie nào trên ổ đĩa để đọc: yt-dlp không thể lấy gì, dù dùng Chrome, Edge, Brave hay Firefox. Với Chrome, Edge và Brave, đây là cái bẫy: phải đóng trình duyệt, và việc đó xóa cookie. Hãy tắt tùy chọn này hoặc giữ lại cookie của youtube.com và google.com.
- Một **đèn báo** cho biết trạng thái: đỏ nếu tắt hoặc lỗi, cam nếu chưa kiểm tra hoặc đang chạy, xanh nếu cookie đã được tải. Nút ↻ chạy kiểm tra và chú giải giải thích trạng thái hoặc lỗi.
- **Trên Linux (bản xem trước)**: có Firefox, Chromium, Chrome, Brave, Edge, Opera và Vivaldi. Các trình duyệt họ Chromium bảo vệ cookie bằng chùm khóa của máy tính (GNOME Keyring, KWallet): phải được mở khóa, tức là phải có phiên đồ họa đang mở. Chỉ mới thử đọc một hồ sơ Firefox; **nên dùng Firefox**.

### Trình hướng dẫn cài đặt, phụ thuộc và cập nhật yt-dlp

- **Trình hướng dẫn cài đặt**: ở lần chạy đầu tiên, nó đề nghị tải yt-dlp và ffmpeg từ kho GitHub chính thức. Tổng kiểm SHA-256 được xác minh và không cần quyền quản trị.
- **Phụ thuộc**: cửa sổ riêng kiểm tra ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 và deno, và có thể cài chúng bằng Chocolatey. Chỉ ffmpeg và ffprobe là bắt buộc; deno được khuyến nghị (track âm thanh phụ); AtomicParsley, MKVToolNix và aria2 là tùy chọn: phần mềm vẫn chạy khi thiếu chúng. Trên Linux, trình hướng dẫn tải ffmpeg, ffprobe và deno (đã kiểm tra tổng SHA-256, không cần quyền quản trị); với AtomicParsley, MKVToolNix và aria2, cửa sổ hiển thị lệnh của trình quản lý gói (apt, dnf, pacman hoặc zypper) để sao chép vào terminal.
- **Cập nhật và chẩn đoán**: cập nhật yt-dlp (`yt-dlp -U`) hoặc thay tệp thực thi của nó, hiển thị phiên bản và kiểm tra các tùy chọn mà giao diện sử dụng.
- **Cập nhật phần mềm**: kiểm tra hằng ngày (có thể tắt) báo có phiên bản mới bằng một dải thông báo kín đáo; cửa sổ riêng cho biết có gì mới và mở bản tải phù hợp với cách bạn cài đặt (trình cài đặt hoặc bản di động). Không có gì được cài tự động. Một công tắc trong menu tùy chọn («Kiểm tra cập nhật khi khởi động») bật hoặc tắt việc kiểm tra tự động, còn «Kiểm tra bản cập nhật phần mềm…» chạy kiểm tra theo yêu cầu. Trên Linux, đó là AppImage hoặc tệp nén `.tar.gz` phù hợp với kiến trúc của bạn.

### Giao diện và ngôn ngữ

- Các điều khiển tự xuống dòng theo chiều rộng cửa sổ; nội dung cuộn dọc, và bảng của trình kiểm tra còn cuộn ngang.
- Giao diện **15 ngôn ngữ**: Pháp, Anh, Tây Ban Nha, Bồ Đào Nha, Ý, Ba Lan, Hungary, Serbia, Nga, Việt, Trung, Hindi, Nhật, Hàn và Filipino. Thay đổi ngôn ngữ có hiệu lực sau khi khởi động lại, kèm tùy chọn khởi động lại ngay.

### Báo lỗi

- Nút «Báo lỗi» chuẩn bị một báo cáo kỹ thuật: phiên bản phần mềm, Python, hệ điều hành và yt-dlp, các cài đặt vô hại và những dòng nhật ký cuối. Thư mục, tên người dùng và địa chỉ e-mail của bạn được che đi. Gửi báo cáo trên GitHub cần có tài khoản GitHub miễn phí.
- Không có gì được gửi tự động: bạn xem lại và chỉnh sửa báo cáo, rồi mở trang phiếu GitHub đã điền sẵn (hoặc sao chép báo cáo).

## Cài đặt

- **Trình cài đặt (khuyến nghị)**: tải `yt-dlp-gui-setup-X.Y.Z.exe` từ [trang các bản phát hành](https://github.com/harlockSuites/YT-dlp-GUI/releases) rồi chạy. Windows 10 hoặc 11 (64 bit), không cần quyền quản trị; không cần Python.
- **Bản di động**: tải `yt-dlp-gui-portable-X.Y.Z.zip`, giải nén ở bất cứ đâu rồi chạy `yt-dlp-gui.exe`; cài đặt nằm trong thư mục đó.
- **Linux, AppImage (bản xem trước)**: tải `yt-dlp-gui-X.Y.Z-x86_64.AppImage` từ [trang các bản phát hành](https://github.com/harlockSuites/YT-dlp-GUI/releases), cấp quyền thực thi (`chmod +x`) rồi chạy. Cần `libfuse2` (gói `libfuse2` hoặc `fuse-libs`); nếu không có, hãy chạy với `--appimage-extract-and-run`.
- **Linux, tệp nén (bản xem trước)**: tải `yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz`, giải nén (`tar xzf`) rồi chạy `./yt-dlp-gui/yt-dlp-gui`. Cài đặt và các công cụ đã tải nằm trong `~/.local/share/yt-dlp-GUI`; để gỡ cài đặt, hãy xóa thư mục đó cùng tệp hoặc thư mục của phần mềm.
- **Linux, yêu cầu và kiểm tra**: Linux 64 bit (x86_64) của bản phân phối từ năm 2022 trở lên (glibc 2.35 trở lên). Để kiểm tra một tệp, hãy tải thêm `SHA256SUMS-linux.txt` và chạy trong cùng thư mục: `sha256sum -c SHA256SUMS-linux.txt --ignore-missing`. Các tệp cho Linux được phát hành riêng, trong những bản phát hành có thẻ bắt đầu bằng “Linux-v” (được GitHub đánh dấu “Pre-release”); bản phát hành hiển thị mặc định trên trang là bản dành cho Windows.
- **Từ mã nguồn**: xem các mục «Yêu cầu» và «Bắt đầu nhanh» bên dưới.
- **Gỡ cài đặt**: Cài đặt Windows › Ứng dụng › Ứng dụng đã cài đặt › yt-dlp GUI, hoặc lối tắt «Gỡ cài đặt» trong menu Start. Phần mềm đề nghị xóa luôn dữ liệu của nó (cài đặt, hàng đợi, yt-dlp và ffmpeg đã tải); video của bạn không bao giờ bị xóa. Vì việc cài đặt gắn với từng tài khoản Windows, phần mềm chỉ xuất hiện trong danh sách của tài khoản đã cài đặt. Với bản portable, chỉ cần xóa thư mục của nó. Các công cụ cài riêng bằng Chocolatey (ffmpeg, Deno…) không bị gỡ.
- **Phân tích diệt virus (VirusTotal)**: phiên bản 0.1.7 được phân tích ngày 21 tháng 10 năm 2026. [Trình cài đặt](https://www.virustotal.com/gui/file/7177f2dc75c3b5309b2d6b96a2104d578dbaf67a0c8ed28af286aa37159df91c) bị 4 trên 69 công cụ gắn cờ (Arctic Wolf, Microsoft, SecureAge, Skyhigh) bằng các phát hiện heuristic chung; [trình khởi chạy của bản portable](https://www.virustotal.com/gui/file/6889bde864b341a948dc23c01e29eba3c63315145705eb0d5bb24a4964b0735a) bị 5 trên 70 công cụ gắn cờ (Arctic Wolf, CrowdStrike Falcon, Microsoft, SecureAge, Zillya) và [tệp ZIP portable](https://www.virustotal.com/gui/file/7fd0a4bb101ca4b4c513ff42e0782cc2371304c643bf03cb3ccd8e9abdb43706) bị 1 trên 66 (Zillya, trên chính tệp lưu trữ). Nhiều khả năng là báo động giả do chương trình được nén và chưa ký số. Kết quả này chỉ áp dụng cho phiên bản này. Nếu còn nghi ngờ, hãy kiểm tra tổng SHA-256.
- **Code signing policy**: các tệp chưa được ký số. Yêu cầu ký số miễn phí gửi SignPath Foundation đã bị từ chối ngày 19 tháng 10 năm 2026 (dự án chưa đủ hiện diện công khai) và có thể gửi lại; [chính sách ký mã](https://github.com/harlockSuites/YT-dlp-GUI/blob/main/docs/CODE_SIGNING_POLICY.md) mô tả quy trình dự kiến nếu có được chứng chỉ.
- **Cảnh báo Windows SmartScreen**: trình cài đặt chưa được ký số nên Windows có thể hiện «Windows đã bảo vệ PC của bạn». Bấm «Thông tin thêm», rồi «Vẫn chạy». Để kiểm tra tính xác thực của tệp, hãy so sánh tổng SHA-256 của nó với tổng trong `SHA256SUMS.txt` được công bố cùng mỗi bản phát hành:

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

## Cảnh báo của Windows và trình duyệt

Phần mềm này miễn phí, do một người phát hành, và các tệp của nó **chưa được ký số**. Một tệp mới mà hầu như chưa ai tải xuống thì chưa có «uy tín»: vì vậy trình duyệt và Windows hiển thị cảnh báo **ngay cả với phần mềm an toàn**. Cảnh báo không chứng minh tệp nguy hiểm, và việc không có cảnh báo cũng không chứng minh tệp an toàn: đây là cách tự kiểm tra.

- **Trình duyệt** (Firefox, Chrome, Edge, Brave): lượt tải có thể bị gắn nhãn «ít phổ biến» hoặc «chứa vi-rút hoặc phần mềm độc hại». Đây là bước kiểm tra uy tín tự động của tệp. Hãy kiểm tra tổng kiểm tra trước (bên dưới); nếu khớp, bạn có thể chọn tùy chọn cho phép hoặc giữ lại lượt tải.
- **Windows SmartScreen**: «Windows đã bảo vệ PC của bạn» → bấm «Thông tin thêm» rồi «Vẫn chạy», **sau khi** đã kiểm tra tổng kiểm tra.
- **Microsoft Defender (Bảo mật Windows)**: có thể cách ly hoặc xóa tệp, báo «Trojan:Win32/Wacatac.C!ml». Hậu tố `!ml` chỉ một phát hiện tự động bằng học máy, thường gặp với tệp mới và chưa ký số; các phát hiện này đã được báo cho Microsoft là báo động giả. Sau khi kiểm tra tổng SHA-256 (bên dưới), bạn có thể khôi phục tệp: Bảo mật Windows › Bảo vệ khỏi virus và mối đe dọa › Lịch sử bảo vệ › mở mục đó › Hành động › «Cho phép trên thiết bị» (hoặc «Khôi phục»). Đừng tắt tính năng bảo vệ của Windows và đừng thêm ngoại lệ rộng hơn chính tệp này.
- **Diệt virus**: một vài công cụ hiển thị phát hiện chung (xem phần phân tích diệt virus ở trên). Để xem phân tích tệp của bạn, hãy dán tổng SHA-256 của nó vào ô tìm kiếm của [VirusTotal](https://www.virustotal.com/): nếu tệp đã được biết, bạn nhận được báo cáo mà không cần tải lên.
- **Kiểm tra lượt tải của bạn**: hãy tải thêm `SHA256SUMS.txt` từ cùng trang phiên bản, mở PowerShell trong thư mục chứa các tệp và chạy lệnh bên dưới: lệnh so sánh từng tệp với tổng đã công bố và in `OK` hoặc `DIFFERENT`. Nếu một tệp là `DIFFERENT`, đừng chạy nó.

```powershell
Get-Content .\SHA256SUMS.txt | ForEach-Object { $h, $n = $_ -split '\s+\*?', 2; if ((Get-FileHash $n -Algorithm SHA256).Hash -eq $h.ToUpper()) { "$n : OK" } else { "$n : DIFFERENT" } }
```

- Việc kiểm tra này chứng minh tệp của bạn **giống hệt** tệp đã đăng trên GitHub; bản thân nó không chứng minh tệp vô hại. Mã nguồn và quy trình dựng tệp tự động ([GitHub Actions](https://github.com/harlockSuites/YT-dlp-GUI/actions)) là công khai, và chưa có chữ ký số: đơn gửi SignPath Foundation đã bị từ chối ngày 19 tháng 10 năm 2026 (xem «Code signing policy»).

## Yêu cầu

- Windows 10 hoặc 11, hoặc Linux 64 bit (bản xem trước)
- [Python 3](https://www.python.org/) có Tkinter (đã gồm trong bản cài chuẩn) (trên Linux: gói `python3-tk`)
- `yt-dlp.exe` và nên có [ffmpeg](https://ffmpeg.org/): trình hướng dẫn cài đặt tải chúng ở lần chạy đầu tiên (trên Linux: `yt-dlp`, không có `.exe`)

## Bắt đầu nhanh

1. Tải hoặc sao chép kho mã này và vào thư mục của nó.
2. Chạy `yt-dlp-gui.bat` (hoặc `pythonw yt-dlp-gui.pyw`). Trên Linux: `python3 yt-dlp-gui.pyw`.
3. Ở lần chạy đầu tiên, hãy để trình hướng dẫn cài yt-dlp và ffmpeg; nó vẫn có trong menu tùy chọn.
4. Dán một URL, chọn tùy chọn, rồi tải xuống, thêm vào hàng đợi hoặc mở trình kiểm tra cho một danh sách phát.

## Quyền riêng tư và sử dụng có trách nhiệm

- Phần mềm này không gửi dữ liệu nào cho tác giả và không có telemetry. Các kết nối mạng đi qua yt-dlp (các trang video), trình hướng dẫn cài đặt (GitHub) và công cụ sổ đăng ký (tìm kiếm YouTube). Việc tự động kiểm tra cập nhật cũng kết nối tới GitHub khi khởi động (tối đa mỗi ngày một lần); bạn có thể tắt trong «Kiểm tra cập nhật khi khởi động».
- Cookie của bạn ở lại trên máy tính của bạn: yt-dlp đọc chúng cục bộ từ trình duyệt đã chọn.
- Hãy dùng công cụ này tuân thủ bản quyền, điều khoản sử dụng của các trang web và luật pháp nước bạn, và chỉ tải những gì bạn có quyền tải.

## Phát triển

Các bài kiểm thử (bản dịch, sổ đăng ký, dựng lệnh, giao diện, trình hướng dẫn cài đặt, tài liệu) được chạy bằng:

```bash
python -X utf8 -m unittest discover -s tests -t .
```

Chúng cũng tự động chạy trên GitHub mỗi lần đẩy mã. Số phiên bản được định nghĩa bởi `__version__` trong `yt-dlp-gui.pyw` và phải khớp với tiêu đề của [CHANGELOG.md](../CHANGELOG.md). Các tệp dịch giao diện nằm trong `lang/` và của tài liệu này trong `docs/`; rất hoan nghênh người bản ngữ rà soát.

## Ủng hộ dự án

Việc dùng giao diện này đã, đang và sẽ luôn miễn phí và tự do cho bất kỳ ai. Nếu công cụ đặc biệt hữu ích với bạn, bạn có thể ủng hộ dự án trên [Ko-fi](https://ko-fi.com/harlocksuites).

## Lời cảm ơn

Cảm ơn cộng đồng thường xuyên cập nhật [yt-dlp](https://github.com/yt-dlp/yt-dlp), nếu không có nó thì tất cả những điều này sẽ không thể có.

## Giấy phép

Mã nguồn được phát hành theo giấy phép [MIT](../LICENSE). Biểu tượng, logo và biểu ngữ «Harlock S.» (tệp `yt-dlp-gui.ico` và thư mục `assets/`) là các tác phẩm gốc do AI tạo ra theo yêu cầu của tác giả. Chúng tạo nên nhận diện hình ảnh của dự án và không thuộc phạm vi giấy phép MIT: vui lòng không dùng lại cho dự án khác hoặc theo cách gây nhầm lẫn.
