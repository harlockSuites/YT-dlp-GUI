# yt-dlp GUI — Linux 版本

[Français](../README-LINUX.md) · [English](README-LINUX.en.md) · [Español](README-LINUX.es.md) · [Português](README-LINUX.pt.md) · [Italiano](README-LINUX.it.md) · [Polski](README-LINUX.pl.md) · [Magyar](README-LINUX.hu.md) · [Srpski](README-LINUX.sr.md) · [Русский](README-LINUX.ru.md) · [Tiếng Việt](README-LINUX.vi.md) · [中文](README-LINUX.zh.md) · [हिन्दी](README-LINUX.hi.md) · [日本語](README-LINUX.ja.md) · [한국어](README-LINUX.ko.md) · [Filipino](README-LINUX.fil.md)

> **预览版。** 本文档是[主 README](README.zh.md) 的补充：软件是同一个，但这里只介绍 Linux 特有的内容（安装、Cookie 与密钥环、文件、故障排除）。每个版本的新变化见 [CHANGELOG-linux.md](../CHANGELOG-linux.md)。翻译仍需由母语者审校；如有疑问，以法语和英语文本为准。

## 目录

1. [预览版的状态](#s1)
2. [安装](#s2)
3. [首次启动与依赖项](#s3)
4. [浏览器 Cookie](#s4)
5. [密钥环：手动操作](#s5)
6. [文件在哪里](#s6)
7. [故障排除](#s7)
8. [报告错误](#s8)
9. [面向开发者](#s9)

<a id="s1"></a>

## 1. 预览版的状态

Linux 版本复现 Windows 版本 0.1.7（已冻结，用作模型）的行为。它以 **GitHub 预发布版（pre-release）** 的形式发布，标签为 `Linux-vX.Y.Z`：从不被当作仓库的“最新发布版”。

**已经试过的内容**（Debian 12 虚拟机，GNOME 桌面，Python 3.11，每个浏览器中都登录了真实的 YouTube 账号，2026 年 10 月）：

- **Firefox、Waterfox、Floorp 和 Zen Browser 的 Cookie**：浏览器打开或关闭时都能读取。
- **Google Chrome、Chromium、Brave、Vivaldi、Opera 和 Microsoft Edge 的 Cookie**：在浏览器**关闭**时读取，前提是每个浏览器都已启动过一次并在其中登录了 YouTube（见[第 5 节](#s5)）。单个下载和播放列表检查器均成功。
- **LibreWolf**：只有在它打开并已登录时才能读取（默认情况下它会在关闭时删除 Cookie）。
- 使用 Firefox 的 Cookie 下载**私享视频**，以及包含三个视频（其中一个为私享）的播放列表。
- **软件包**：AppImage 和 `.tar.gz` 压缩包由 CI 在 Ubuntu 22.04 上构建；`.deb` 已在 Debian 12 上构建、安装、启动并卸载；“安装到菜单”已用真实的 AppImage 在一次性的主目录中试过。

**尚未试过的内容**：

- 其他发行版（Ubuntu、Fedora、Arch、openSUSE……）以及 GNOME 以外的桌面，包括 KDE Plasma（KWallet）；
- 以 Flatpak 或 Snap 方式安装的浏览器（Flatpak 版 LibreWolf 的目录布局除外，已观察过）；
- **未安装** Chrome 或 Chromium 时的 Vivaldi、Opera 或 Edge（见[第 5 节](#s5)）；
- aarch64 架构（软件支持，但软件包只为 x86_64 构建）；
- 在真实桌面上用鼠标操作“安装到菜单”窗口（目前通过程序测试）；
- 翻译：仍需由母语者审校。

<a id="s2"></a>

## 2. 安装

### 选择哪种格式

| 格式 | 适合谁 | 管理员权限 | 菜单项 |
|---|---|---|---|
| **AppImage** | 任何较新的 64 位发行版 | 否 | “安装到菜单”（2.3 节） |
| **`.tar.gz` 压缩包** | 同上，无需 AppImage 或 FUSE | 否 | “安装到菜单” |
| **`.deb` 软件包** | Debian、Ubuntu 及其衍生版 | 是（`sudo`） | 自动 |
| **源代码** | 开发者、试用 | 否 | 无 |

要求：来自 2022 年或更新发行版的 64 位 Linux（x86_64）（glibc 2.35 或更高），因为软件包是在 Ubuntu 22.04 上构建的。

**如果您刚接触 Linux**：只有 `.deb` 软件包是“真正”安装的，也只有它会出现在软件管理器中。AppImage 和压缩包只是普通文件或文件夹，您可以放在任何地方：要移除它们，像删除其他文件一样删除即可（2.2 和 2.5 节）。它们的设置单独保存在 `~/.local/share/yt-dlp-GUI`（第 6 节），删除后依然保留。

文件在[发布页面](https://github.com/harlockSuites/YT-dlp-GUI/releases)：查找带有“Pre-release”标记的 `Linux-v…` 标签。

### 2.1 验证下载

把 `SHA256SUMS-linux.txt` 也下载到同一文件夹，然后：

```bash
sha256sum -c SHA256SUMS-linux.txt --ignore-missing
```

每个存在的文件都应显示 `OK`。这证明您的文件与发布的文件完全一致，但不证明它无害：源代码和自动构建过程都是公开的。

### 2.2 AppImage

```bash
chmod +x yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

AppImage 需要 FUSE 2 库：

| 发行版 | 软件包 |
|---|---|
| Debian、Ubuntu 22.04 及其衍生版 | `libfuse2` |
| Ubuntu 24.04 及更新版本 | `libfuse2t64` |
| Fedora | `fuse-libs` |

没有 FUSE 也可以启动它：它会自行解压到一个临时文件夹：

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage --appimage-extract-and-run
```

AppImage 并不“安装”：它不会出现在软件管理器中。要移除它，删除该文件即可：

```bash
rm yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

### 2.3 安装到菜单（无需管理员）

双击启动的 AppImage 不会在应用程序菜单中留下图标。在软件中：选项菜单 › **“安装到菜单…”**。该窗口：

- 把程序复制到 `~/.local/share/yt-dlp-GUI/app/`；
- 写入启动器 `~/.local/share/applications/yt-dlp-gui.desktop` 和图标 `~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png`；
- 如果勾选了该选项，会在桌面上添加快捷方式（存在 `gio` 工具时会为 GNOME 标记为“可信”）；
- 然后提供“更新”（重新复制正在运行的版本）和“卸载”。

“卸载”只移除安装时创建的内容，并**保留您的设置**和已下载的工具。没有我们内部标记（`X-YtDlpGui-Installer=1`）的启动器永远不会被删除。

限制：该窗口可从 AppImage 和压缩包使用。从源代码运行时，它会引导您使用 AppImage；从 `.deb` 软件包运行时，它会说明软件已经在菜单中。

如果桌面快捷方式显示警告：右键单击图标 › “允许启动”。有些桌面（GNOME 默认）不在桌面上显示图标：菜单中的启动器在任何情况下都可用。

手动移除全部内容：

```bash
rm -rf ~/.local/share/yt-dlp-GUI/app ~/.local/share/applications/yt-dlp-gui.desktop ~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png ~/Desktop/yt-dlp-gui.desktop
```

### 2.4 `.deb` 软件包

```bash
sudo apt install ./yt-dlp-gui_X.Y.Z_amd64.deb
```

程序安装到 `/opt/yt-dlp-gui`，同时有链接 `/usr/bin/yt-dlp-gui`、菜单启动器、图标和许可证（`/usr/share/doc/yt-dlp-gui/`）。它依赖 `libc6 (>= 2.35)` 和 `libx11-6`。

要移除它（您位于 `~/.local/share/yt-dlp-GUI` 的设置绝不会被触及）：

```bash
sudo apt remove yt-dlp-gui
```

### 2.5 `.tar.gz` 压缩包

```bash
tar xzf yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz
```

```bash
./yt-dlp-gui/yt-dlp-gui
```

要让设置和工具保留在**解压后的文件夹内**（U 盘、不留痕迹的试用），请在可执行文件旁创建一个空的 `portable.flag` 文件：

```bash
touch yt-dlp-gui/portable.flag
```

没有此文件时，数据保存在 `~/.local/share/yt-dlp-GUI`（第 6 节）。

压缩包并不“安装”：它不会出现在软件管理器中。要移除它，删除解压后的文件夹：

```bash
rm -rf yt-dlp-gui
```

### 2.6 从源代码运行

```bash
python3 yt-dlp-gui.pyw
```

从源代码运行时，设置和已下载的工具与已安装版本保存在同一个文件夹（`~/.local/share/yt-dlp-GUI`）：重新下载源代码或删除其文件夹都不会清除它们。要把数据保留在源代码文件夹内（不留痕迹的试用），请在 `yt-dlp-gui.pyw` 旁创建一个空的 `portable.flag` 文件。

需要带 Tkinter 的 Python 3：

| 发行版 | 软件包 |
|---|---|
| Debian、Ubuntu 及其衍生版、openSUSE | `python3-tk` |
| Fedora | `python3-tkinter` |
| Arch | `tk` |

### 2.7 更新

每日检查（可在选项菜单中关闭）会查找 `Linux-vX.Y.Z` 版本（包括预发布版），并且**绝不**推荐 Windows 版本。它会打开与您的安装方式相符的文件（AppImage、压缩包或 `.deb`）的下载页面；**不会自动安装任何内容**。要更新：

- **已安装到菜单的 AppImage 或压缩包**：下载新的 AppImage，启动它，然后“安装到菜单… › 更新”；
- **`.deb`**：`sudo apt install ./new-file.deb`；
- **未安装的压缩包**：把新压缩包解压到旧压缩包的位置。

### 2.8 全部移除，包括数据

移除程序之后（2.3 至 2.5 节），如需一并清除设置、队列和已下载的工具（yt-dlp、ffmpeg、deno）：

```bash
rm -rf ~/.local/share/yt-dlp-GUI
```

您下载的视频绝不会保存在这个文件夹中。

<a id="s3"></a>

## 3. 首次启动与依赖项

首次启动时，安装向导会提议从 GitHub 仓库下载 **yt-dlp**（`yt-dlp_linux`）、**ffmpeg**（yt-dlp 官方构建的 `.tar.xz` 压缩包）和 **deno**。SHA-256 校验和会被验证，不要求管理员权限，文件保存到 `~/.local/share/yt-dlp-GUI`（yt-dlp）和 `~/.local/share/yt-dlp-GUI/bin`（ffmpeg、ffprobe、deno）。向导仍可在选项菜单中使用。

只有 ffmpeg 和 ffprobe 是必需的；deno 推荐安装（用于次要音轨）。**AtomicParsley、MKVToolNix 和 aria2** 是可选的：“依赖项”窗口会显示您的包管理器的命令，供您复制到终端中。软件绝不会自己运行它。同样的命令：

| 包管理器 | 命令 |
|---|---|
| apt | `sudo apt install aria2 atomicparsley mkvtoolnix` |
| dnf | `sudo dnf install AtomicParsley aria2 mkvtoolnix` |
| pacman | `sudo pacman -S aria2 atomicparsley mkvtoolnix-cli` |
| zypper | `sudo zypper install AtomicParsley aria2 mkvtoolnix` |

<a id="s4"></a>

## 4. 浏览器 Cookie

yt-dlp **在本地**读取您所选浏览器中的 Cookie（次要音轨、字幕、私享视频、会员专属内容）。默认情况下，软件提供 Linux 上最常用的五个浏览器（Firefox、Google Chrome、Chromium、Brave、Vivaldi）。选项菜单中的 **“Cookie 浏览器…”** 会打开“用于 Cookie 的浏览器”窗口，其中提供 11 个浏览器：勾选您需要的；带 ✔ 的是其配置文件夹存在于您电脑上的浏览器。

| 浏览器 | yt-dlp 读取时的名称 | 密钥环 | 搜索的配置文件夹 |
|---|---|---|---|
| Firefox | `firefox` | 否 | `~/.config/mozilla/firefox`、`~/.mozilla/firefox`、Flatpak、Snap |
| Google Chrome | `chrome` | 是 | `~/.config/google-chrome` |
| Chromium | `chromium` | 是 | `~/.config/chromium` |
| Brave | `brave` | 是 | `~/.config/BraveSoftware/Brave-Browser` |
| Vivaldi | `vivaldi` | 是 | `~/.config/vivaldi` |
| Opera | `opera` | 是 | `~/.config/opera` |
| Microsoft Edge | `edge` | 是 | `~/.config/microsoft-edge` |
| LibreWolf、Waterfox、Floorp、Zen Browser | `firefox:` + 配置文件夹 | 否 | `~/.librewolf`、`~/.config/librewolf`……（其余浏览器同理），包括 Flatpak |

Firefox 的衍生浏览器没有 yt-dlp 认识的名称：软件会查找它们的 `cookies.sqlite` 数据库（在其文件夹下最多三层），并把最近使用的配置文件夹交给 yt-dlp。当 `XDG_CONFIG_HOME` 是绝对路径时会被遵循。

列表旁的**指示灯**显示状态：红色（已禁用或失败）、橙色（未测试或进行中）、绿色（已读取 Cookie）。↻ 按钮运行测试；提示框会解释错误。读取到 **0 个 Cookie** 的测试永远不会显示为绿色。

### 常见情况

| 您看到的内容 | 可能的原因 | 该怎么做 |
|---|---|---|
| “Extracted 0 cookies”，然后是“Sign in to confirm you're not a bot” | 浏览器没有在磁盘上保留任何 Cookie（LibreWolf 默认在关闭时删除它们；配置文件从未登录；隐私模式） | 保持它打开并已登录 YouTube，或在其隐私设置中关闭“关闭时删除 Cookie” |
| Chrome、Chromium、Brave、Vivaldi、Opera 或 Edge 出现“Item does not exist!” | yt-dlp 没有在桌面密钥环中找到浏览器的密钥 | 启动浏览器一次，登录 YouTube，关闭它，再运行测试；否则见[第 5 节](#s5) |
| “Could not copy Chrome cookie database”或“database is locked” | 浏览器运行时会锁定其数据库 | 关闭它，然后再运行测试 |
| “Failed to decrypt” | Cookie 使用了 yt-dlp 没有获得的密钥加密 | [第 5 节](#s5) |

### 在终端中测试浏览器

这是查看确切错误的最佳方式（把 `IDENTIFIER` 替换为任意 YouTube 视频的标识符）：

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

需要留意的行：`Extracted N cookies from chromium`（N 必须大于 0）、`Chosen keyring: GNOMEKEYRING`（所选的密钥环）以及 `cookie version breakdown: {'v10': 0, 'v11': 50, …}`（`v11` Cookie 需要密钥环，`v10` 不需要）。

对于 Firefox 的衍生浏览器，请给出配置文件夹。查找方法：

```bash
find ~ -name cookies.sqlite -path "*librewolf*" 2>/dev/null
```

在 Flatpak 安装中，请在 `~/.var/app` 中查找：

```bash
find ~/.var/app -name cookies.sqlite 2>/dev/null
```

然后，使用包含 `cookies.sqlite` 的文件夹：

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser "firefox:/path/to/profile" -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

<a id="s5"></a>

## 5. 密钥环：手动操作

### 它有什么用

Chromium 系浏览器（Chrome、Chromium、Brave、Vivaldi、Opera、Edge）会加密自己的 Cookie。加密密钥保存在**桌面密钥环**中：在 GNOME、XFCE、Cinnamon、MATE 等桌面上是 GNOME Keyring（或通过“Secret Service”的兼容替代品），在 KDE 上是 KWallet。解密时，yt-dlp 会向密钥环索取这个密钥。Firefox 及其衍生浏览器不需要它。

两个有用的事实：

- **密钥只有在浏览器首次启动之后才存在。** 在我们的虚拟机中，当每个浏览器都启动过一次并在其中登录 YouTube 后，“Item does not exist!”错误就消失了。第一次失败的确切原因没有得到确定：密钥环存在，是默认密钥环，并且已解锁。
- **yt-dlp 使用哪个密钥环**取决于检测到的桌面环境（变量 `XDG_CURRENT_DESKTOP` 和 `DESKTOP_SESSION`），依据 yt-dlp 的代码（2026 年 10 月）：

| 检测到的桌面 | yt-dlp 使用的密钥环 |
|---|---|
| GNOME、Cinnamon、MATE、XFCE、Pantheon、Unity、Deepin、UKUI | GNOME Keyring（`GNOMEKEYRING`） |
| KDE 4、5、6 | KWallet（`KWALLET`、`KWALLET5`、`KWALLET6`） |
| LXQt、KDE 3、无法识别的桌面（仅有窗口管理器：sway、i3……） | 无：纯文本（`BASICTEXT`） |

在最后一种情况下，yt-dlp 只读取 `v10` Cookie：如果您的浏览器把密钥存放在 GNOME Keyring 中，它的 `v11` Cookie 将无法解密。这时需要在终端中强制指定密钥环（5.6 节）；软件目前还没有提供这个设置。

在密钥环中查找的条目名为“*名称* Safe Storage”。根据 yt-dlp 的代码，Chrome 和 Vivaldi 对应 **“Chrome Safe Storage”**，Chromium、Opera 和 Edge 对应 **“Chromium Safe Storage”**，Brave 对应 **“Brave Safe Storage”**。在我们的虚拟机中，Chrome 和 Chromium 也已安装并启动过：我们不知道 Vivaldi、Opera 或 Edge 单独使用时是否能正常工作。

### 5.1 密钥环存在吗？

```bash
ls -la ~/.local/share/keyrings/
```

您应该看到一个 `login.keyring` 文件（名为“login”的密钥环）。接下来，哪个密钥环是**默认**密钥环？

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets --method org.freedesktop.Secret.Service.ReadAlias default
```

返回 `(objectpath '/org/freedesktop/secrets/collection/login',)`：存在默认密钥环。返回 `'/'`：**没有**，请转到 5.4 节。

### 5.2 它被锁定了吗？

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Locked
```

`(<false>,)`：已解锁。`(<true>,)`：已锁定；用 Seahorse（5.4 节）打开它，它会询问密码。

### 5.3 我的浏览器的密钥在里面吗？

列出条目：

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Items
```

返回结果给出以数字结尾的路径（`…/login/1`、`…/login/2`……）。要读取每一项的名称（请调整数字列表）：

```bash
for i in 1 2 3 4 5 6; do gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login/$i --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Item Label; done
```

您应该能看到，例如 `Chromium Safe Storage`、`Chrome Safe Storage` 或 `Brave Safe Storage`。空名称是无害的。如果缺少您的浏览器的名称：启动它一次，登录 YouTube，关闭它，然后再次运行这个命令。

### 5.4 用 Seahorse 创建或解锁密钥环

安装 Seahorse（“密码和密钥”）和相关工具。确切的命令在软件的“用于 Cookie 的浏览器”窗口中也有：

| 包管理器 | 命令 |
|---|---|
| apt | `sudo apt install gnome-keyring seahorse libsecret-tools` |
| dnf | `sudo dnf install gnome-keyring seahorse libsecret` |
| pacman | `sudo pacman -S gnome-keyring seahorse libsecret` |
| zypper | `sudo zypper install gnome-keyring seahorse libsecret-tools` |

然后打开它：

```bash
seahorse
```

- **没有默认密钥环**：创建一个（“+”按钮或 文件 › 新建 › 密码密钥环 菜单），命名为“Login”，然后右键单击它 › “设为默认”。具体的菜单文字因 Seahorse 版本而异。
- **密钥环已锁定**：双击或右键单击 › “解锁”，然后输入它的密码（请您自己输入，软件从不索取）。
- **自动登录**：受密码保护的密钥环无法自行打开，如果您在会话开始时不输入任何密码；它会一直保持锁定，直到您解锁它（或者直到您为会话和密钥环使用同一个密码）。

然后**启动浏览器，登录 YouTube，关闭它**，再运行测试（第 4 节）。

### 5.5 KDE Plasma（KWallet）

在 KDE 上，yt-dlp 会查询 KWallet（`kwallet-query`）。管理器根据发行版称为 `kwalletmanager`（或 `kwalletmanager5`）。这种配置在我们的测试中**尚未试过**。

### 5.6 对 yt-dlp 强制指定密钥环（终端）

软件让 yt-dlp 根据桌面环境自行选择密钥环。要强制指定，请在浏览器名称后加上 `+密钥环`（取值：`gnomekeyring`、`kwallet`、`kwallet5`、`kwallet6`、`basictext`）：

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium+gnomekeyring -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

要知道某个 Chromium 实际使用哪个密钥环（命令取自 yt-dlp 的代码，此处未试过）：

```bash
chromium --enable-logging=stderr --v=1 2>&1 | grep key_storage_
```

### 5.7 不使用密钥环：`--password-store=basic`（高级，未试过）

Chromium 接受 `--password-store=basic`：此时它以明文保存密钥（一个固定、众所周知的密钥），并把新的 Cookie 加密为 `v10`，yt-dlp 无需密钥环即可读取（`chromium+basictext`）。**这样不太安全**：任何能读取您文件的程序都能解密这些 Cookie。只有在理解这种取舍时才使用；已保存的 Cookie 可能不会被重新编码：请重新登录。

### 5.8 最后手段

如果密钥环已损坏，**请先备份**：

```bash
cp -a ~/.local/share/keyrings ~/keyrings-backup
```

删除 `login.keyring` 会清除其中保存的**所有**密码（Wi-Fi、在线账号……）：在不了解后果的情况下请不要这样做。

<a id="s6"></a>

## 6. 文件在哪里

数据文件夹是 `$XDG_DATA_HOME/yt-dlp-GUI`（默认 `~/.local/share/yt-dlp-GUI`），除非 `portable.flag` 位于压缩包的可执行文件（或 `yt-dlp-gui.pyw` 脚本）旁边。

| 文件或文件夹 | 内容 |
|---|---|
| `gui-config.json` | 设置（语言、浏览器、文件夹、浏览器选择……） |
| `download-queue.json` | 下载队列 |
| `custom-blocks.json` | 自定义选项块 |
| `yt-dlp` | 由向导下载的可执行文件 |
| `bin/` | ffmpeg、ffprobe、deno |
| `cmd/` | yt-dlp 的临时配置文件 |
| `app/` | “安装到菜单”制作的程序副本 |

<a id="s7"></a>

## 7. 故障排除

| 问题 | 线索 |
|---|---|
| AppImage 无法启动 | 从终端启动以读取错误；安装 FUSE 2（2.2 节）或添加 `--appimage-extract-and-run` |
| 什么都不显示，或出现库错误 | 检查 glibc 版本：`ldd --version` 必须显示 2.35 或更高 |
| 桌面上没有图标 | GNOME 默认不显示；请使用应用程序菜单 |
| 桌面快捷方式带有警告 | 右键单击 › “允许启动” |
| 主机与虚拟机之间的拖放不起作用 | 这是 VirtualBox（Guest Additions）的功能，不是本软件的 |
| 界面大小不对 | 软件遵循系统字体（Tk）；请尝试其他系统字体大小 |
| yt-dlp 更新失败 | 使用选项菜单中的“更新与诊断”；否则下载 `yt-dlp_linux` 并在替换窗口中选择它（所选文件会被设为可执行） |

<a id="s8"></a>

## 8. 报告错误

“报告错误”按钮会准备一份技术报告，其中您的文件夹、用户名和电子邮件地址都会被隐去；不会自动发送任何内容。对于 Linux，请再补充：

```bash
cat /etc/os-release
```

```bash
echo "$XDG_CURRENT_DESKTOP $XDG_SESSION_TYPE"
```

并说明您是**如何**安装软件的（AppImage、压缩包、`.deb`、源代码），如果是 Cookie 问题，还要附上**终端测试的结果**（第 4 节），但不要粘贴您的 Cookie。

<a id="s9"></a>

## 9. 面向开发者

测试（在虚拟显示器上，无需真实屏幕）：

```bash
xvfb-run -a python3 -X utf8 -m unittest discover -s tests -t .
```

构建软件包（构建工具：`pip install -r packaging/requirements-build.txt`，另加 `appimagetool`，其路径由变量 `APPIMAGETOOL` 给出）：

```bash
python3 packaging/build_linux.py
```

```bash
python3 packaging/build_deb.py
```

结果位于 `dist/`。为获得最佳兼容性，请在受支持的最旧发行版上构建（构建机器的 glibc 是对运行该程序的机器所要求的最低版本）。`.deb` 的实用检查：

```bash
lintian dist/yt-dlp-gui_*_amd64.deb
```

唯一已知的格式错误是 `dir-or-file-in-opt`（程序打包在 `/opt` 中）。

**发布**：检查 `yt-dlp-gui.pyw` 中的 `__version__`，在 `CHANGELOG-linux.md` 中为该版本的小节标注日期，提交，然后创建并推送 `Linux-vX.Y.Z` 标签。“Release Linux”工作流会运行测试，构建 AppImage、压缩包和 `.deb`，计算校验和，并把发布创建为**预发布版（pre-release）**，绝不是“最新发布版”（Windows 版本 0.1.7 的更新检查不应在那里找到 Linux 标签）。

许可证：MIT，与仓库的其余部分相同（见 [LICENSE](../LICENSE)）。
