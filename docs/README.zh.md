# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

[yt-dlp](https://github.com/yt-dlp/yt-dlp) 的图形界面，旨在让每个人都能轻松使用，同时充分发挥它的能力。

> **项目仍在开发中。** 部分功能可能会变化、尚不完整或存在错误。已提供 Windows 版；同时提供 **Linux 预览版**，测试较少。

🐧 **Linux** : [README-LINUX (français)](../README-LINUX.md) · [README-LINUX (English)](README-LINUX.en.md)

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## 功能

### 单个下载与队列

- **选项**：最高画质（最高 4K）、仅音频（MP3）、字幕（vtt、srt、ass 格式）、嵌入字幕和缩略图、主音频语言、次要音轨（多音轨 MKV 文件），以及可用自己的模块扩充的“脚本模块”库（后处理、导出、网络、行为）。
- **多条音轨**：在 MKV 文件中，每条音轨都带有其语言标签（“zho”“eng”等）；播放器会在音频菜单中显示。
- **生成的命令**：与您的选择对应的 yt-dlp 命令会实时显示。
- **队列**：添加当前 URL，然后运行整个队列、从某一项开始、只运行一个视频或一个范围；支持暂停和继续、跳过当前项、停止并清理未完成的文件。队列会在会话之间保留。
- **已存在的文件名**：名称已存在于目标文件夹的单个视频会加上后缀（`_2`、`_3`…），以免覆盖任何文件。通过此下载器下载的播放列表不会重新编号：文件夹中已有的视频会被跳过（“has already been downloaded”）。

### 播放列表检查器

- **分析**播放列表：每个视频都会列出可用的音轨和字幕；隐藏、私享或已删除的项目会被忽略，不会阻碍其余内容。
- **全局规则**（画质、仅音频、字幕格式与嵌入、缩略图、编号、语言、脚本模块、输出文件夹），并可为主语言、次要音轨和字幕设置**按视频的例外**。
- **颜色标记**：缺少主语言时为红色，缺少次要音轨或字幕时为橙色。
- **下载所选内容**，带日志、暂停、继续和跳过；如果请求的音轨不存在，视频会在不含它们的情况下重试，随后由**汇总**显示哪些成功、哪些被调整、哪些失败。

### 智能目录与登记

- **智能目录**：yt-dlp 借助保存在输出文件夹中的登记文件跳过已下载的视频。`.yt-dlp-registre.json` 文件记录每个视频的标识符、URL、标题、时长、文件名和日期；yt-dlp 读取的 `.yt-dlp-archive.txt` 由它派生而来。
- **回溯检查**：如果所选视频已在文件夹中但未登记，会弹出窗口建议将其登记并跳过（通过比较标题）。您可以取消勾选误判项。
- **更新登记**：统计文件夹中的视频、登记中的视频和缺失的视频，然后在 YouTube 上查找缺失的信息（标题，以及通过 ffprobe 获取的时长）。未经您确认不会登记任何内容，两个按钮可打开本地文件或找到的 YouTube 链接以便核对。

![yt-dlp GUI](img/registry.en.png)

### 浏览器 Cookie

- 选择 yt-dlp 在本地读取其 Cookie 的浏览器（Chrome、Firefox、Edge、Brave、Opera）：次要音轨和部分字幕需要它们。**推荐使用 Firefox。**
- **我们的测试结果**（Windows 11，2026 年 10 月，每个浏览器均已登录 YouTube 账号）：**Firefox** 无论浏览器打开还是关闭都能用。**Opera** **只有在浏览器关闭时**才能用：打开时它会锁定 Cookie 数据库，此时 yt-dlp 会显示“Could not copy Chrome cookie database”。**Chrome、Edge 和 Brave** 即使关闭也会失败：它们对 Cookie 的加密方式 yt-dlp 并不总能读取。这些限制来自浏览器和 yt-dlp，而非本软件，并可能随它们的更新而改变。
- 如果浏览器设置为**关闭时删除 Cookie**（或使用无痕模式），磁盘上就没有可读取的 Cookie：无论使用 Chrome、Edge、Brave 还是 Firefox，yt-dlp 都无法获取。对于 Chrome、Edge 和 Brave，这是个陷阱：必须先关闭浏览器，而关闭又会清除 Cookie。请关闭该选项，或保留 youtube.com 和 google.com 的 Cookie。
- **指示灯**显示状态：禁用或失败为红色，未测试或进行中为橙色，Cookie 已加载为绿色。↻ 按钮运行测试，提示文字会说明状态或错误。
- **在 Linux 上（预览版）**：默认提供 Firefox、Google Chrome、Chromium、Brave 和 Vivaldi，它们是该系统上最常用的；在选项菜单的“用于 Cookie 的浏览器”窗口中最多可勾选 11 个浏览器（还有 Opera、Microsoft Edge、LibreWolf、Waterfox、Floorp 和 Zen Browser）。Chromium 系浏览器用桌面密钥环（GNOME Keyring、KWallet）保护 Cookie：密钥环必须处于解锁状态，也就是说需要已打开的图形会话。目前只用已登录的 YouTube 账号试过读取 Firefox 的 Cookie（包括私享视频）；**推荐使用 Firefox**。

### 安装向导、依赖项与 yt-dlp 更新

- **安装向导**：首次启动时，建议从官方 GitHub 仓库下载 yt-dlp 和 ffmpeg。会校验 SHA-256 校验和，且无需管理员权限。
- **依赖项**：专用窗口检查 ffmpeg、ffprobe、AtomicParsley、MKVToolNix、aria2 和 deno，并可通过 Chocolatey 安装它们。只有 ffmpeg 和 ffprobe 是必需的；deno 建议安装（辅助音轨）；AtomicParsley、MKVToolNix 和 aria2 是可选的：没有它们软件也能运行。在 Linux 上，安装向导会下载 ffmpeg、ffprobe 和 deno（校验 SHA-256，无需管理员权限）；对于 AtomicParsley、MKVToolNix 和 aria2，窗口会显示包管理器（apt、dnf、pacman 或 zypper）的命令，可复制到终端中执行。
- **更新与诊断**：更新 yt-dlp（`yt-dlp -U`）或替换其可执行文件，显示版本并检查界面所使用的选项。
- **软件更新**：每天检查一次（可关闭），以不显眼的横幅提示新版本；专用窗口会显示更新内容，并打开与您的安装方式（安装程序或便携版）对应的下载。不会自动安装任何内容。选项菜单中的开关（“启动时检查更新”）可开启或关闭自动检查，“检查软件更新…”则可随时手动检查。在 Linux 上，则是与您的架构对应的 AppImage 或 `.tar.gz` 压缩包。

### 界面与语言

- 控件会根据窗口宽度自动换行；内容可垂直滚动，检查器的表格还可水平滚动。
- 界面支持 **15 种语言**：法语、英语、西班牙语、葡萄牙语、意大利语、波兰语、匈牙利语、塞尔维亚语、俄语、越南语、中文、印地语、日语、韩语和菲律宾语。更改语言将在重启后生效，也可选择立即重启。

### 报告错误

- “报告错误”按钮会准备一份技术报告：软件、Python、操作系统和 yt-dlp 的版本、无害的设置以及日志的最后几行。您的文件夹、用户名和电子邮件地址会被隐藏。在 GitHub 上提交报告需要一个免费的 GitHub 账号。
- 不会自动发送任何内容：您先查看并编辑报告，然后打开已预先填写的 GitHub 问题页面（或复制报告）。

## 安装

- **安装程序（推荐）**：从[发布页面](https://github.com/harlockSuites/YT-dlp-GUI/releases)下载 `yt-dlp-gui-setup-X.Y.Z.exe` 并运行。适用于 Windows 10 或 11（64 位），无需管理员权限，也无需 Python。
- **便携版**：下载 `yt-dlp-gui-portable-X.Y.Z.zip`，解压到任意位置并运行 `yt-dlp-gui.exe`；设置保存在该文件夹中。
- **Linux，AppImage（预览版）**：从[发布页面](https://github.com/harlockSuites/YT-dlp-GUI/releases)下载 `yt-dlp-gui-X.Y.Z-x86_64.AppImage`，赋予可执行权限（`chmod +x`）后运行。需要 `libfuse2`（软件包 `libfuse2` 或 `fuse-libs`）；没有时请加上 `--appimage-extract-and-run` 运行。
- **Linux，压缩包（预览版）**：下载 `yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz`，解压（`tar xzf`）后运行 `./yt-dlp-gui/yt-dlp-gui`。设置和已下载的工具位于 `~/.local/share/yt-dlp-GUI`；卸载时，请删除该文件夹以及软件的文件或文件夹。
- **Linux，添加到应用程序菜单（预览版）**：在 AppImage 或压缩包中运行时，选项菜单 ›“安装到菜单”会把程序复制到 `~/.local/share/yt-dlp-GUI/app`，把启动器和图标加入桌面菜单，并可按需在桌面添加快捷方式，无需管理员权限。同一窗口还可更新或卸载；您的设置会保留。
- **Linux，.deb 软件包（预览版）**：在 Debian、Ubuntu 及其衍生版上，下载 `yt-dlp-gui_X.Y.Z_amd64.deb`，用 `sudo apt install ./yt-dlp-gui_X.Y.Z_amd64.deb` 安装。程序会带着图标出现在应用程序菜单中；`sudo apt remove yt-dlp-gui` 可将其移除，您的设置（`~/.local/share/yt-dlp-GUI`）会保留。
- **Linux，系统要求与校验**：64 位 Linux（x86_64），发行版为 2022 年或更新（glibc 2.35 或更高）。要校验文件，请同时下载 `SHA256SUMS-linux.txt`，并在同一文件夹中运行：`sha256sum -c SHA256SUMS-linux.txt --ignore-missing`。Linux 文件单独发布，位于标签以“Linux-v”开头的版本中（在 GitHub 上标为“Pre-release”）；页面默认显示的版本是 Windows 版。
- **从源代码运行**：请参阅下方的“系统要求”和“快速开始”。
- **卸载**：Windows 设置 › 应用 › 已安装的应用 › yt-dlp GUI，或开始菜单中的“卸载”快捷方式。软件会询问是否一并删除其数据（设置、队列、已下载的 yt-dlp 和 ffmpeg）；您的视频绝不会被删除。由于安装属于各个 Windows 账户，软件只出现在安装它的账户的列表中。便携版只需删除其文件夹。通过 Chocolatey 单独安装的工具（ffmpeg、Deno 等）不会被移除。
- **杀毒软件检测（VirusTotal）**：0.1.7 版本已于 2026 年 10 月 21 日检测。[安装程序](https://www.virustotal.com/gui/file/7177f2dc75c3b5309b2d6b96a2104d578dbaf67a0c8ed28af286aa37159df91c)被 69 个引擎中的 4 个标记（Arctic Wolf、Microsoft、SecureAge、Skyhigh），均为通用启发式检测；[便携版的启动程序](https://www.virustotal.com/gui/file/6889bde864b341a948dc23c01e29eba3c63315145705eb0d5bb24a4964b0735a)被 70 个中的 5 个标记（Arctic Wolf、CrowdStrike Falcon、Microsoft、SecureAge、Zillya），[便携版 ZIP 压缩包](https://www.virustotal.com/gui/file/7fd0a4bb101ca4b4c513ff42e0782cc2371304c643bf03cb3ccd8e9abdb43706)被 66 个中的 1 个标记（Zillya，针对压缩包本身）。很可能是因程序经过压缩且未签名而产生的误报。这些结果仅适用于该版本。如有疑虑，请核对 SHA-256 校验值。
- **Code signing policy**：文件没有数字签名。向 SignPath Foundation 提出的免费签名申请已于 2026 年 10 月 19 日被拒绝（项目的公开知名度尚不足），以后可以再次申请。若获得证书，预期的流程见[代码签名政策](https://github.com/harlockSuites/YT-dlp-GUI/blob/main/docs/CODE_SIGNING_POLICY.md)。
- **Windows SmartScreen 警告**：安装程序没有数字签名，因此 Windows 可能显示“Windows 已保护你的电脑”。请点击“更多信息”，再点击“仍要运行”。若要核实文件的真实性，请将其 SHA-256 校验和与每个版本附带的 `SHA256SUMS.txt` 中的值进行比较：

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

## Windows 和浏览器的警告

本软件免费，由一个人发布，其文件**尚未进行数字签名**。几乎没人下载过的新文件没有“信誉”：因此浏览器和 Windows 即使对**安全的软件**也会显示警告。警告不能证明文件危险，没有警告也不能证明文件安全：下面是自行验证的方法。

- **浏览器**（Firefox、Chrome、Edge、Brave）：下载可能被标记为“不常见”或“包含病毒或恶意软件”。这是对文件信誉的自动检查。请先核对下面的校验和；若一致，可以选择允许或保留该下载的选项。
- **Windows SmartScreen**：“Windows 已保护你的电脑”→ 在核对校验和**之后**，点击“更多信息”，再点击“仍要运行”。
- **Microsoft Defender（Windows 安全中心）**：它可能隔离或删除该文件，并显示“Trojan:Win32/Wacatac.C!ml”。后缀 `!ml` 表示由机器学习自动检测，常见于新的、未签名的文件；这些检测已作为误报报告给 Microsoft。核对 SHA-256 校验值（见下文）之后，可以还原该文件：Windows 安全中心 › 病毒和威胁防护 › 保护历史记录 › 打开该项 › 操作 › “在设备上允许”（或“还原”）。请不要关闭 Windows 的保护，也不要添加比这一个文件更宽泛的排除项。
- **杀毒软件**：少数引擎显示通用检测（见上文的杀毒软件检测）。要查看你的文件的检测结果，请把它的 SHA-256 校验值粘贴到 [VirusTotal](https://www.virustotal.com/) 的搜索栏：如果该文件已为人所知，无需上传即可得到报告。
- **核对你的下载**：从同一发布页面一并下载 `SHA256SUMS.txt`，在文件所在文件夹中打开 PowerShell，运行下面的命令：它把每个文件与已发布的校验值比较，显示 `OK` 或 `DIFFERENT`。若某个文件显示 `DIFFERENT`，请不要运行它。

```powershell
Get-Content .\SHA256SUMS.txt | ForEach-Object { $h, $n = $_ -split '\s+\*?', 2; if ((Get-FileHash $n -Algorithm SHA256).Hash -eq $h.ToUpper()) { "$n : OK" } else { "$n : DIFFERENT" } }
```

- 此核对证明你的文件与 GitHub 上发布的文件**完全相同**；仅凭它并不能证明文件无害。源代码和文件的自动构建（[GitHub Actions](https://github.com/harlockSuites/YT-dlp-GUI/actions)）是公开的，目前还没有数字签名：向 SignPath Foundation 提交的申请已于 2026 年 10 月 19 日被拒绝（见“Code signing policy”）。

## 系统要求

- Windows 10 或 11，或 64 位 Linux（预览版）
- 带 Tkinter 的 [Python 3](https://www.python.org/)（标准安装已包含）（Linux 上：软件包 `python3-tk`）
- `yt-dlp.exe`，建议同时安装 [ffmpeg](https://ffmpeg.org/)：安装向导会在首次启动时下载它们（Linux 上为 `yt-dlp`，没有 `.exe`）

## 快速开始

1. 下载或克隆此仓库并进入其文件夹。
2. 运行 `yt-dlp-gui.bat`（或 `pythonw yt-dlp-gui.pyw`）。在 Linux 上：`python3 yt-dlp-gui.pyw`。
3. 首次启动时，让向导安装 yt-dlp 和 ffmpeg；之后仍可在选项菜单中打开它。
4. 粘贴 URL，选择选项，然后下载、加入队列，或为播放列表打开检查器。

## 隐私与负责任使用

- 本软件不会向作者发送任何数据，也不含遥测。网络连接通过 yt-dlp（视频网站）、安装向导（GitHub）和登记工具（YouTube 搜索）进行。自动检查更新也会在启动时连接 GitHub（每天最多一次）；可在“启动时检查更新”中关闭。
- 您的 Cookie 保留在您的电脑上：yt-dlp 在本地从所选浏览器读取它们。
- 请在遵守版权、网站使用条款和您所在国家法律的前提下使用本工具，只下载您有权下载的内容。

## 开发

测试（翻译、登记、命令构建、界面、安装向导、文档）通过以下命令运行：

```bash
python -X utf8 -m unittest discover -s tests -t .
```

每次推送时它们也会在 GitHub 上自动运行。版本号由 `yt-dlp-gui.pyw` 中的 `__version__` 定义，并且必须与 [CHANGELOG.md](../CHANGELOG.md) 的标题一致。界面翻译文件位于 `lang/`，本文档的翻译位于 `docs/`；欢迎母语人士审校。

## 支持本项目

使用此界面过去、现在和将来都是免费的，任何人都可以自由使用。如果这款工具对您特别有用，欢迎在 [Ko-fi](https://ko-fi.com/harlocksuites) 上支持本项目。

## 致谢

感谢定期更新 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 的社区，没有它就没有这一切。

## 许可证

代码以 [MIT](../LICENSE) 许可证发布。图标、标志和“Harlock S.”横幅（`yt-dlp-gui.ico` 文件和 `assets/` 文件夹）是应作者要求由 AI 生成的原创作品。它们构成项目的视觉标识，不在 MIT 许可证范围内：请勿将其用于其他项目，也不要以可能造成混淆的方式使用。
