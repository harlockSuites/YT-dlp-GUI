# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

Giao diện đồ họa cho [yt-dlp](https://github.com/yt-dlp/yt-dlp), được thiết kế để ai cũng dùng được mà vẫn khai thác trọn vẹn khả năng của nó.

> **Dự án đang được phát triển.** Một số tính năng có thể thay đổi, chưa hoàn chỉnh hoặc còn lỗi.

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## Tính năng

### Trình tải đơn lẻ và hàng đợi

- **Tùy chọn**: chất lượng tối đa (đến 4K), chỉ âm thanh (MP3), phụ đề (định dạng vtt, srt, ass), nhúng phụ đề và ảnh thu nhỏ, ngôn ngữ âm thanh chính, các rãnh âm thanh phụ (tệp MKV nhiều rãnh) và thư viện «khối script» (xử lý sau, xuất, mạng, hành vi) mà bạn có thể bổ sung bằng khối của riêng mình.
- **Lệnh được tạo**: lệnh yt-dlp tương ứng với lựa chọn của bạn được hiển thị trực tiếp.
- **Hàng đợi**: thêm URL hiện tại, rồi chạy toàn bộ hàng đợi, từ một mục trở đi, một video hoặc một khoảng; tạm dừng và tiếp tục, bỏ qua mục đang chạy, dừng và dọn các tệp dở dang. Hàng đợi được giữ lại giữa các phiên.

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

- Chọn trình duyệt (Chrome, Firefox, Edge, Brave, Opera) mà yt-dlp đọc cookie cục bộ: cần cho các rãnh âm thanh phụ và một số phụ đề. Với Chrome, Edge hoặc Brave, hãy đóng hoàn toàn trình duyệt trước khi tải: nó khóa cơ sở dữ liệu cookie khi đang mở và yt-dlp sẽ hiện «Could not copy Chrome cookie database». Firefox không có giới hạn này.
- Một **đèn báo** cho biết trạng thái: đỏ nếu tắt hoặc lỗi, cam nếu chưa kiểm tra hoặc đang chạy, xanh nếu cookie đã được tải. Nút ↻ chạy kiểm tra và chú giải giải thích trạng thái hoặc lỗi.

### Trình hướng dẫn cài đặt, phụ thuộc và cập nhật yt-dlp

- **Trình hướng dẫn cài đặt**: ở lần chạy đầu tiên, nó đề nghị tải yt-dlp và ffmpeg từ kho GitHub chính thức. Tổng kiểm SHA-256 được xác minh và không cần quyền quản trị.
- **Phụ thuộc**: cửa sổ riêng kiểm tra ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 và deno, và có thể cài chúng bằng Chocolatey.
- **Cập nhật và chẩn đoán**: cập nhật yt-dlp (`yt-dlp -U`) hoặc thay tệp thực thi của nó, hiển thị phiên bản và kiểm tra các tùy chọn mà giao diện sử dụng.
- **Cập nhật phần mềm**: kiểm tra hằng ngày (có thể tắt) báo có phiên bản mới bằng một dải thông báo kín đáo; cửa sổ riêng cho biết có gì mới và mở bản tải phù hợp với cách bạn cài đặt (trình cài đặt hoặc bản di động). Không có gì được cài tự động. Một công tắc trong menu tùy chọn («Kiểm tra cập nhật khi khởi động») bật hoặc tắt việc kiểm tra tự động, còn «Kiểm tra bản cập nhật phần mềm…» chạy kiểm tra theo yêu cầu.

### Giao diện và ngôn ngữ

- Các điều khiển tự xuống dòng theo chiều rộng cửa sổ; nội dung cuộn dọc, và bảng của trình kiểm tra còn cuộn ngang.
- Giao diện **15 ngôn ngữ**: Pháp, Anh, Tây Ban Nha, Bồ Đào Nha, Ý, Ba Lan, Hungary, Serbia, Nga, Việt, Trung, Hindi, Nhật, Hàn và Filipino. Thay đổi ngôn ngữ có hiệu lực sau khi khởi động lại, kèm tùy chọn khởi động lại ngay.

### Báo lỗi

- Nút «Báo lỗi» chuẩn bị một báo cáo kỹ thuật: phiên bản phần mềm, Python, Windows và yt-dlp, các cài đặt vô hại và những dòng nhật ký cuối. Thư mục, tên người dùng và địa chỉ e-mail của bạn được che đi.
## Cài đặt

- **Trình cài đặt (khuyến nghị)**: tải `yt-dlp-gui-setup-X.Y.Z.exe` từ [trang các bản phát hành](https://github.com/harlockSuites/YT-dlp-GUI/releases) rồi chạy. Windows 10 hoặc 11 (64 bit), không cần quyền quản trị; không cần Python.
- **Bản di động**: tải `yt-dlp-gui-portable-X.Y.Z.zip`, giải nén ở bất cứ đâu rồi chạy `yt-dlp-gui.exe`; cài đặt nằm trong thư mục đó.
- **Từ mã nguồn**: xem các mục «Yêu cầu» và «Bắt đầu nhanh» bên dưới.
- **Cảnh báo Windows SmartScreen**: trình cài đặt chưa được ký số nên Windows có thể hiện «Windows đã bảo vệ PC của bạn». Bấm «Thông tin thêm», rồi «Vẫn chạy». Để kiểm tra tính xác thực của tệp, hãy so sánh tổng SHA-256 của nó với tổng trong `SHA256SUMS.txt` được công bố cùng mỗi bản phát hành:

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

- Không có gì được gửi tự động: bạn xem lại và chỉnh sửa báo cáo, rồi mở trang phiếu GitHub đã điền sẵn (hoặc sao chép báo cáo).

## Yêu cầu

- Windows
- [Python 3](https://www.python.org/) có Tkinter (đã gồm trong bản cài chuẩn)
- `yt-dlp.exe` và nên có [ffmpeg](https://ffmpeg.org/): trình hướng dẫn cài đặt tải chúng ở lần chạy đầu tiên

## Bắt đầu nhanh

1. Tải hoặc sao chép kho mã này và vào thư mục của nó.
2. Chạy `yt-dlp-gui.bat` (hoặc `pythonw yt-dlp-gui.pyw`).
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
