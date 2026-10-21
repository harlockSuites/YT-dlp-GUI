# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

[yt-dlp](https://github.com/yt-dlp/yt-dlp) 的图形界面，旨在让每个人都能轻松使用，同时充分发挥它的能力。

> **项目仍在开发中。** 部分功能可能会变化、尚不完整或存在错误。

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

### 安装向导、依赖项与 yt-dlp 更新

- **安装向导**：首次启动时，建议从官方 GitHub 仓库下载 yt-dlp 和 ffmpeg。会校验 SHA-256 校验和，且无需管理员权限。
- **依赖项**：专用窗口检查 ffmpeg、ffprobe、AtomicParsley、MKVToolNix、aria2 和 deno，并可通过 Chocolatey 安装它们。只有 ffmpeg 和 ffprobe 是必需的；deno 建议安装（辅助音轨）；AtomicParsley、MKVToolNix 和 aria2 是可选的：没有它们软件也能运行。
- **更新与诊断**：更新 yt-dlp（`yt-dlp -U`）或替换其可执行文件，显示版本并检查界面所使用的选项。
- **软件更新**：每天检查一次（可关闭），以不显眼的横幅提示新版本；专用窗口会显示更新内容，并打开与您的安装方式（安装程序或便携版）对应的下载。不会自动安装任何内容。选项菜单中的开关（“启动时检查更新”）可开启或关闭自动检查，“检查软件更新…”则可随时手动检查。

### 界面与语言

- 控件会根据窗口宽度自动换行；内容可垂直滚动，检查器的表格还可水平滚动。
- 界面支持 **15 种语言**：法语、英语、西班牙语、葡萄牙语、意大利语、波兰语、匈牙利语、塞尔维亚语、俄语、越南语、中文、印地语、日语、韩语和菲律宾语。更改语言将在重启后生效，也可选择立即重启。

### 报告错误

- “报告错误”按钮会准备一份技术报告：软件、Python、Windows 和 yt-dlp 的版本、无害的设置以及日志的最后几行。您的文件夹、用户名和电子邮件地址会被隐藏。在 GitHub 上提交报告需要一个免费的 GitHub 账号。
## 安装

- **安装程序（推荐）**：从[发布页面](https://github.com/harlockSuites/YT-dlp-GUI/releases)下载 `yt-dlp-gui-setup-X.Y.Z.exe` 并运行。适用于 Windows 10 或 11（64 位），无需管理员权限，也无需 Python。
- **便携版**：下载 `yt-dlp-gui-portable-X.Y.Z.zip`，解压到任意位置并运行 `yt-dlp-gui.exe`；设置保存在该文件夹中。
- **从源代码运行**：请参阅下方的“系统要求”和“快速开始”。
- **卸载**：Windows 设置 › 应用 › 已安装的应用 › yt-dlp GUI，或开始菜单中的“卸载”快捷方式。软件会询问是否一并删除其数据（设置、队列、已下载的 yt-dlp 和 ffmpeg）；您的视频绝不会被删除。由于安装属于各个 Windows 账户，软件只出现在安装它的账户的列表中。便携版只需删除其文件夹。通过 Chocolatey 单独安装的工具（ffmpeg、Deno 等）不会被移除。
- **杀毒软件检测（VirusTotal）**：0.1.6 版本已于 2026 年 10 月 20 日检测。[安装程序](https://www.virustotal.com/gui/file/683b157e1072ae7c2abcff09c1f0d94ac1d36701715682798c10792359fa9bae)被 70 个引擎中的 4 个标记（Arctic Wolf、DeepInstinct、SecureAge、Skyhigh），均为通用启发式检测（“obfuscatedpoly”）；[便携版 ZIP 压缩包](https://www.virustotal.com/gui/file/45cfe1a79d7eb96323634ba1ac6c8247eb5a4e9e79f1519e3f70f7c92b2538c3)未被 66 个引擎中的任何一个标记（0/66），其[启动程序](https://www.virustotal.com/gui/file/0896bf3d524774b4f53224160bf9f216ccb0922ec2b8b5ddc8495b2d2c1680f2)被 71 个引擎中的 2 个标记（SecureAge、Zillya）。很可能是因程序经过压缩且未签名而产生的误报。这些结果仅适用于该版本。如有疑虑，请核对 SHA-256 校验值。
- **Code signing policy**：后续版本的数字签名正在筹备中（拟向 SignPath Foundation 申请）；[代码签名政策](https://github.com/harlockSuites/YT-dlp-GUI/blob/main/docs/CODE_SIGNING_POLICY.md)说明了流程。0.1.4 及之前的版本未签名。
- **Windows SmartScreen 警告**：安装程序没有数字签名，因此 Windows 可能显示“Windows 已保护你的电脑”。请点击“更多信息”，再点击“仍要运行”。若要核实文件的真实性，请将其 SHA-256 校验和与每个版本附带的 `SHA256SUMS.txt` 中的值进行比较：

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

- 不会自动发送任何内容：您先查看并编辑报告，然后打开已预先填写的 GitHub 问题页面（或复制报告）。

## 系统要求

- Windows
- 带 Tkinter 的 [Python 3](https://www.python.org/)（标准安装已包含）
- `yt-dlp.exe`，建议同时安装 [ffmpeg](https://ffmpeg.org/)：安装向导会在首次启动时下载它们

## 快速开始

1. 下载或克隆此仓库并进入其文件夹。
2. 运行 `yt-dlp-gui.bat`（或 `pythonw yt-dlp-gui.pyw`）。
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
