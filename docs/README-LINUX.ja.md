# yt-dlp GUI — Linux 版

[Français](../README-LINUX.md) · [English](README-LINUX.en.md) · [Español](README-LINUX.es.md) · [Português](README-LINUX.pt.md) · [Italiano](README-LINUX.it.md) · [Polski](README-LINUX.pl.md) · [Magyar](README-LINUX.hu.md) · [Srpski](README-LINUX.sr.md) · [Русский](README-LINUX.ru.md) · [Tiếng Việt](README-LINUX.vi.md) · [中文](README-LINUX.zh.md) · [हिन्दी](README-LINUX.hi.md) · [日本語](README-LINUX.ja.md) · [한국어](README-LINUX.ko.md) · [Filipino](README-LINUX.fil.md)

> **プレビュー版です。** この文書は[メインの README](README.ja.md) を補うものです。ソフトウェアは同じですが、ここでは Linux 固有のこと（インストール、Cookie とキーリング、ファイル、トラブルシューティング）だけを扱います。各バージョンの新しい点は [CHANGELOG-linux.md](../CHANGELOG-linux.md) にあります。翻訳はまだ母語話者による確認が必要です。疑わしい場合は、フランス語と英語の文章が優先されます。

## 目次

1. [プレビュー版の状態](#s1)
2. [インストール](#s2)
3. [初回起動と依存関係](#s3)
4. [ブラウザーの Cookie](#s4)
5. [キーリング：手作業での操作](#s5)
6. [ファイルの場所](#s6)
7. [トラブルシューティング](#s7)
8. [不具合を報告](#s8)
9. [開発者向け](#s9)

<a id="s1"></a>

## 1. プレビュー版の状態

Linux 版は、Windows 版 0.1.7（凍結されており、基準として使われています）の動作を再現します。`Linux-vX.Y.Z` というタグの **GitHub プレリリース（pre-release）** として公開され、リポジトリの「最新リリース」として扱われることはありません。

**試したこと**（Debian 12 の仮想マシン、GNOME デスクトップ、Python 3.11、各ブラウザーで本物の YouTube アカウントにログイン済み、2026 年 10 月）：

- **Firefox、Waterfox、Floorp、Zen Browser の Cookie**：ブラウザーが開いていても閉じていても読み取れました。
- **Google Chrome、Chromium、Brave、Vivaldi、Opera、Microsoft Edge の Cookie**：各ブラウザーを一度起動して YouTube にログインした後、ブラウザーを**閉じた状態**で読み取れました（[第 5 節](#s5)参照）。単体のダウンロードもプレイリスト検査も成功しました。
- **LibreWolf**：開いていてログイン済みの間だけ読み取れます（既定では終了時に Cookie を削除します）。
- Firefox の Cookie による**非公開動画**、および 3 本のうち 1 本が非公開のプレイリスト。
- **パッケージ**：AppImage と `.tar.gz` アーカイブは CI が Ubuntu 22.04 でビルドします。`.deb` は Debian 12 でビルド、インストール、起動、削除を確認しました。AppImage、アーカイブ、`.deb` はいずれも仮想マシンで起動し、「メニューにインストール」と「アンインストール」は AppImage でマウス操作して試しました（アイコンをメニューとデスクトップに追加し、その後削除）。
- **言語とフォント**：韓国語フォントのないマシンで韓国語を選択。「Font needed」ウィンドウがフォントを提案し、ダウンロードと検証を経て、ソフトウェアが再起動し、文字が読めるようになりました。

**まだ試していないこと**：

- 他のディストリビューション（Ubuntu、Fedora、Arch、openSUSE など）と、KDE Plasma（KWallet）を含む GNOME 以外のデスクトップ。
- Flatpak や Snap でインストールしたブラウザー（観察した Flatpak 版 LibreWolf のフォルダー構成を除く）。
- Chrome も Chromium もインストールされて**いない**状態での Vivaldi、Opera、Edge（[第 5 節](#s5)参照）。
- aarch64 アーキテクチャ（ソフトウェアは対応していますが、パッケージは x86_64 向けにしかビルドされません）。
- 仮想マシンではない実際の Linux コンピューター（実際のデスクトップとハードウェア）。
- 翻訳：まだ母語話者による確認が必要です。

<a id="s2"></a>

## 2. インストール

### どの形式を選ぶか

| 形式 | 対象 | 管理者権限 | メニューへの項目 |
|---|---|---|---|
| **AppImage** | 最近の 64 ビットのディストリビューションならどれでも | 不要 | 「メニューにインストール」（2.3 節） |
| **`.tar.gz` アーカイブ** | 同上。AppImage や FUSE が不要 | 不要 | 「メニューにインストール」 |
| **`.deb` パッケージ** | Debian、Ubuntu とその派生 | 必要（`sudo`） | 自動 |
| **ソースコード** | 開発者、試用 | 不要 | なし |

動作条件：2022 年以降のディストリビューションの 64 ビット Linux（x86_64）（glibc 2.35 以上）。パッケージは Ubuntu 22.04 でビルドされるためです。

**Linux が初めての方へ**：本当の意味でインストールされ、ソフトウェア管理ツールに表示されるのは `.deb` パッケージだけです。AppImage とアーカイブは普通のファイルまたはフォルダーで、好きな場所に置けます。削除するときは、ほかのファイルと同じように消すだけです（2.2 節と 2.5 節）。設定は別の場所の `~/.local/share/yt-dlp-GUI`（第 6 節）にあり、削除しても残ります。

ファイルは[リリースページ](https://github.com/harlockSuites/YT-dlp-GUI/releases)にあります。「Pre-release」と表示された `Linux-v…` タグを探してください。

### 2.1 ダウンロードの確認

`SHA256SUMS-linux.txt` も同じフォルダーにダウンロードしてから、次を実行します。

```bash
sha256sum -c SHA256SUMS-linux.txt --ignore-missing
```

存在する各ファイルに `OK` と表示されるはずです。これは、お手元のファイルが公開されたものと同一であることを示すだけで、無害であることの証明ではありません。ソースコードと自動ビルドは公開されています。

### 2.2 AppImage

```bash
chmod +x yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

AppImage には FUSE 2 ライブラリが必要です。

| ディストリビューション | パッケージ |
|---|---|
| Debian、Ubuntu 22.04 とその派生 | `libfuse2` |
| Ubuntu 24.04 以降 | `libfuse2t64` |
| Fedora | `fuse-libs` |

FUSE がなくても起動してみてください。自分で一時フォルダーに展開して実行されます。

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage --appimage-extract-and-run
```

AppImage は「インストール」されません。ソフトウェア管理ツールには表示されません。削除するには、ファイルを消します。

```bash
rm yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

AppImage をアイコン付きでアプリケーションメニューに表示するには、**ソフトウェア内の「メニューにインストール…」機能**を使います（2.3 節）。入力するコマンドはありません。

### 2.3 メニューにインストール（管理者権限なし）

ダブルクリックで起動した AppImage は、アプリケーションメニューにアイコンを残しません。ソフトウェアの中で、オプションメニュー ›「**メニューにインストール…**」を選びます。このウィンドウは次のことを行います。

- プログラムを `~/.local/share/yt-dlp-GUI/app/` にコピーします。
- ランチャー `~/.local/share/applications/yt-dlp-gui.desktop` とアイコン `~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png` を書き込みます。
- チェックボックスがオンなら、デスクトップにショートカットを追加します（`gio` ツールがあれば GNOME 向けに「信頼済み」と印を付けます）。
- その後、「更新」（実行中のバージョンをコピーし直します）と「アンインストール」を提供します。

「アンインストール」は、インストールで作られたものだけを削除し、**設定**とダウンロード済みのツールは残します。当方の内部マーカー（`X-YtDlpGui-Installer=1`）がないランチャーは削除されません。

制限：このウィンドウは AppImage とアーカイブから使えます。ソースコードから起動した場合は AppImage を案内し、`.deb` パッケージから起動した場合は、すでにメニューにあることを説明します。

デスクトップのショートカットに警告が出る場合は、アイコンを右クリック ›「起動を許可」を選びます。デスクトップ上にアイコンを表示しないデスクトップ環境（GNOME は既定）もあります。メニューのランチャーはどの場合でも使えます。

手作業ですべて削除するには：

```bash
rm -rf ~/.local/share/yt-dlp-GUI/app ~/.local/share/applications/yt-dlp-gui.desktop ~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png ~/Desktop/yt-dlp-gui.desktop
```

`.deb` パッケージをすでにインストールしている場合は、この機能を使わないでください。ソフトウェアはすでにメニューにあり、2 つ目の「yt-dlp GUI」の項目が現れてしまいます（この方法を選ぶなら、先に `sudo apt remove yt-dlp-gui` で `.deb` を削除してください）。

### 2.4 `.deb` パッケージ

```bash
sudo apt install ./yt-dlp-gui_X.Y.Z_amd64.deb
```

プログラムは `/opt/yt-dlp-gui` に入り、リンク `/usr/bin/yt-dlp-gui`、メニューのランチャー、アイコン、ライセンス（`/usr/share/doc/yt-dlp-gui/`）が一緒に配置されます。依存するのは `libc6 (>= 2.35)` と `libx11-6` です。

削除するには（`~/.local/share/yt-dlp-GUI` にある設定には一切触れません）：

```bash
sudo apt remove yt-dlp-gui
```

### 2.5 `.tar.gz` アーカイブ

```bash
tar xzf yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz
```

```bash
./yt-dlp-gui/yt-dlp-gui
```

設定とツールを**展開したフォルダーの中**に保存したい場合（USB メモリー、痕跡を残さない試用）は、実行ファイルの横に空の `portable.flag` ファイルを作ります。

```bash
touch yt-dlp-gui/portable.flag
```

このファイルがなければ、データは `~/.local/share/yt-dlp-GUI`（第 6 節）に保存されます。

アーカイブは「インストール」されません。ソフトウェア管理ツールには表示されません。削除するには、展開したフォルダーを消します。

```bash
rm -rf yt-dlp-gui
```

### 2.6 ソースコードから

```bash
python3 yt-dlp-gui.pyw
```

ソースコードから起動した場合も、設定とダウンロード済みのツールはインストール版と同じフォルダー（`~/.local/share/yt-dlp-GUI`）に保存されます。ソースコードを再ダウンロードしたり、そのフォルダーを削除したりしても消えません。データをソースコードのフォルダー内に置きたい場合（痕跡を残さない試用）は、`yt-dlp-gui.pyw` の横に空の `portable.flag` ファイルを作ります。

Tkinter 付きの Python 3 が必要です。

| ディストリビューション | パッケージ |
|---|---|
| Debian、Ubuntu とその派生、openSUSE | `python3-tk` |
| Fedora | `python3-tkinter` |
| Arch | `tk` |

### 2.7 更新

毎日の確認（オプションメニューで無効にできます）は、プレリリースを含む `Linux-vX.Y.Z` のバージョンを探し、Windows 版を提案することは**決して**ありません。お使いのインストール形態（AppImage、アーカイブ、`.deb`）に合ったファイルのダウンロードページを開きます。**自動では何もインストールされません**。更新するには：

- **メニューにインストール済みの AppImage またはアーカイブ**：新しい AppImage をダウンロードして起動し、「メニューにインストール… › 更新」を選びます。
- **`.deb`**：`sudo apt install ./new-file.deb`
- **インストールしていないアーカイブ**：新しいアーカイブを古いものの場所に展開します。

### 2.8 データを含めてすべて削除する

プログラムを削除した後（2.3 〜 2.5 節）、設定、キュー、ダウンロード済みのツール（yt-dlp、ffmpeg、deno）も消すには：

```bash
rm -rf ~/.local/share/yt-dlp-GUI
```

ダウンロードした動画がこのフォルダーに入ることはありません。

<a id="s3"></a>

## 3. 初回起動と依存関係

初回起動時、セットアップアシスタントが **yt-dlp**（`yt-dlp_linux`）、**ffmpeg**（yt-dlp 公式ビルドの `.tar.xz` アーカイブ）、**deno** を GitHub のリポジトリからダウンロードするよう提案します。SHA-256 の合計値は検証され、管理者権限は求められず、ファイルは `~/.local/share/yt-dlp-GUI`（yt-dlp）と `~/.local/share/yt-dlp-GUI/bin`（ffmpeg、ffprobe、deno）に保存されます。アシスタントはオプションメニューからいつでも開けます。

必須なのは ffmpeg と ffprobe だけで、deno は推奨です（副音声トラック用）。**AtomicParsley、MKVToolNix、aria2** は任意です。「依存関係」ウィンドウには、お使いのパッケージマネージャーのコマンドが表示され、ターミナルにコピーして使います。ソフトウェアがそれを自分で実行することはありません。同じコマンドは次のとおりです。

| パッケージマネージャー | コマンド |
|---|---|
| apt | `sudo apt install aria2 atomicparsley mkvtoolnix` |
| dnf | `sudo dnf install AtomicParsley aria2 mkvtoolnix` |
| pacman | `sudo pacman -S aria2 atomicparsley mkvtoolnix-cli` |
| zypper | `sudo zypper install AtomicParsley aria2 mkvtoolnix` |

<a id="s4"></a>

## 4. ブラウザーの Cookie

yt-dlp は、選んだブラウザーの Cookie を**ローカルで**読み取ります（副音声トラック、字幕、非公開動画、メンバー限定コンテンツ用）。既定では、Linux で最もよく使われる 5 つのブラウザー（Firefox、Google Chrome、Chromium、Brave、Vivaldi）が表示されます。オプションメニューの「**Cookie 用ブラウザー…**」を選ぶと「Cookie 用ブラウザー」ウィンドウが開き、11 個のブラウザーから選べます。必要なものにチェックを入れてください。✔ は、プロファイルのフォルダーがお使いのコンピューターに存在するブラウザーです。

| ブラウザー | yt-dlp での読み取り名 | キーリング | 探索するプロファイルフォルダー |
|---|---|---|---|
| Firefox | `firefox` | 不要 | `~/.config/mozilla/firefox`、`~/.mozilla/firefox`、Flatpak、Snap |
| Google Chrome | `chrome` | 必要 | `~/.config/google-chrome` |
| Chromium | `chromium` | 必要 | `~/.config/chromium` |
| Brave | `brave` | 必要 | `~/.config/BraveSoftware/Brave-Browser` |
| Vivaldi | `vivaldi` | 必要 | `~/.config/vivaldi` |
| Opera | `opera` | 必要 | `~/.config/opera` |
| Microsoft Edge | `edge` | 必要 | `~/.config/microsoft-edge` |
| LibreWolf、Waterfox、Floorp、Zen Browser | `firefox:` + プロファイルのフォルダー | 不要 | `~/.librewolf`、`~/.config/librewolf` など（ほかも同じ形）、Flatpak を含む |

Firefox の派生ブラウザーには、yt-dlp が知っている名前がありません。ソフトウェアは、それらの `cookies.sqlite` データベースを探し（それぞれのフォルダーの下、最大 3 階層）、最後に使われたプロファイルのフォルダーを yt-dlp に渡します。`XDG_CONFIG_HOME` は、絶対パスのときに尊重されます。

リストの横の**インジケーター**は状態を示します。赤（無効または失敗）、オレンジ（未テストまたは実行中）、緑（Cookie を読み取れた）。↻ ボタンでテストを実行し、ツールチップにエラーの説明が表示されます。**Cookie を 0 個**しか読み取れなかったテストが緑になることはありません。

### よくあるケース

| 表示される内容 | 考えられる原因 | 対処 |
|---|---|---|
| 「Extracted 0 cookies」の後に「Sign in to confirm you're not a bot」 | ブラウザーがディスク上に Cookie を保持していない（LibreWolf は既定で終了時に削除、プロファイルが未ログイン、プライベートモード） | 開いたまま YouTube にログインした状態にするか、プライバシー設定で終了時の Cookie 削除をオフにする |
| Chrome、Chromium、Brave、Vivaldi、Opera、Edge で「Item does not exist!」 | yt-dlp がデスクトップのキーリングでブラウザーの鍵を見つけられなかった | ブラウザーを一度起動して YouTube にログインし、閉じてからテストをやり直す。それでもだめなら[第 5 節](#s5) |
| 「Could not copy Chrome cookie database」または「database is locked」 | ブラウザーが起動中にデータベースをロックしている | ブラウザーを閉じてからテストをやり直す |
| 「Failed to decrypt」 | yt-dlp が取得できなかった鍵で Cookie が暗号化されている | [第 5 節](#s5) |

### ターミナルでブラウザーを試す

正確なエラーを見るには、これが最良の方法です（`IDENTIFIER` は、任意の YouTube 動画の識別子に置き換えてください）。

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

探す行：`Extracted N cookies from chromium`（N は 0 より大きくなければなりません）、`Chosen keyring: GNOMEKEYRING`（選ばれたキーリング）、`cookie version breakdown: {'v10': 0, 'v11': 50, …}`（`v11` の Cookie にはキーリングが必要で、`v10` には不要です）。

Firefox の派生ブラウザーでは、プロファイルのフォルダーを指定します。見つけるには：

```bash
find ~ -name cookies.sqlite -path "*librewolf*" 2>/dev/null
```

Flatpak でインストールした場合は、`~/.var/app` の中を探します。

```bash
find ~/.var/app -name cookies.sqlite 2>/dev/null
```

その後、`cookies.sqlite` を含むフォルダーを使って：

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser "firefox:/path/to/profile" -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

<a id="s5"></a>

## 5. キーリング：手作業での操作

### 何のためのものか

Chromium 系のブラウザー（Chrome、Chromium、Brave、Vivaldi、Opera、Edge）は Cookie を暗号化します。暗号化の鍵は**デスクトップのキーリング**に保管されます。GNOME、XFCE、Cinnamon、MATE などでは GNOME Keyring（または「Secret Service」を介した互換のもの）、KDE では KWallet です。復号するとき、yt-dlp はキーリングにその鍵を要求します。Firefox とその派生ブラウザーには必要ありません。

役に立つ事実が 2 つあります。

- **鍵は、ブラウザーを初めて起動した後にしか存在しません。** 当方の仮想マシンでは、各ブラウザーを一度起動して YouTube にログインしたところ、「Item does not exist!」のエラーは消えました。最初の失敗の正確な原因は確定していません。キーリングは存在し、既定であり、ロック解除されていました。
- **yt-dlp がどのキーリングを使うか**は、検出されたデスクトップ環境（変数 `XDG_CURRENT_DESKTOP` と `DESKTOP_SESSION`）によります。yt-dlp のコード（2026 年 10 月）によると次のとおりです。

| 検出されたデスクトップ | yt-dlp が使うキーリング |
|---|---|
| GNOME、Cinnamon、MATE、XFCE、Pantheon、Unity、Deepin、UKUI | GNOME Keyring（`GNOMEKEYRING`） |
| KDE 4、5、6 | KWallet（`KWALLET`、`KWALLET5`、`KWALLET6`） |
| LXQt、KDE 3、認識できないデスクトップ（ウィンドウマネージャーのみ：sway、i3 など） | なし：平文（`BASICTEXT`） |

最後の場合、yt-dlp は `v10` の Cookie しか読み取りません。ブラウザーが鍵を GNOME Keyring に保管していると、その `v11` の Cookie は復号されません。その場合はターミナルからキーリングを指定する必要があります（5.6 節）。ソフトウェアには、まだこの設定がありません。

キーリングで探される項目は「*名前* Safe Storage」という名前です。yt-dlp のコードによると、Chrome と Vivaldi は **「Chrome Safe Storage」**、Chromium、Opera、Edge は **「Chromium Safe Storage」**、Brave は **「Brave Safe Storage」** です。当方の仮想マシンでは Chrome と Chromium もインストールされて起動済みでした。Vivaldi、Opera、Edge が単独で動くかどうかは分かっていません。

### 5.1 キーリングは存在するか

```bash
ls -la ~/.local/share/keyrings/
```

`login.keyring` というファイル（「login」キーリング）が見えるはずです。次に、**既定**のキーリングはどれでしょうか。

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets --method org.freedesktop.Secret.Service.ReadAlias default
```

応答が `(objectpath '/org/freedesktop/secrets/collection/login',)` なら、既定のキーリングがあります。応答が `'/'` なら**ありません**。5.4 節へ進みます。

### 5.2 ロックされているか

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Locked
```

`(<false>,)`：ロック解除済み。`(<true>,)`：ロック中。Seahorse（5.4 節）で開くとパスワードを尋ねられます。

### 5.3 自分のブラウザーの鍵は入っているか

項目を一覧表示します。

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Items
```

応答には、番号で終わるパス（`…/login/1`、`…/login/2` など）が並びます。それぞれの名前を読むには（番号の一覧は適宜変更してください）：

```bash
for i in 1 2 3 4 5 6; do gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login/$i --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Item Label; done
```

たとえば `Chromium Safe Storage`、`Chrome Safe Storage`、`Brave Safe Storage` が見えるはずです。名前が空のものは無害です。お使いのブラウザーの名前がない場合は、一度起動して YouTube にログインし、閉じてから、このコマンドをもう一度実行してください。

### 5.4 Seahorse でキーリングを作成またはロック解除する

Seahorse（「パスワードと鍵」）と関連ツールをインストールします。正確なコマンドは、ソフトウェアの「Cookie 用ブラウザー」ウィンドウにも表示されます。

| パッケージマネージャー | コマンド |
|---|---|
| apt | `sudo apt install gnome-keyring seahorse libsecret-tools` |
| dnf | `sudo dnf install gnome-keyring seahorse libsecret` |
| pacman | `sudo pacman -S gnome-keyring seahorse libsecret` |
| zypper | `sudo zypper install gnome-keyring seahorse libsecret-tools` |

次に開きます。

```bash
seahorse
```

- **既定のキーリングがない場合**：作成し（「+」ボタン、またはファイル › 新規 › パスワードキーリング メニュー）、名前を「Login」にして、右クリック ›「既定に設定」を選びます。正確な表示名は Seahorse のバージョンによって異なります。
- **ロックされたキーリング**：ダブルクリックまたは右クリック ›「ロック解除」を選び、そのパスワードを入力します（ご自身で入力してください。ソフトウェアがパスワードを求めることはありません）。
- **自動ログイン**：パスワードで保護されたキーリングは、セッション開始時にパスワードを入力しないと自動では開きません。ロック解除するまで（またはセッションとキーリングに同じパスワードを使うまで）ロックされたままです。

その後、**ブラウザーを起動して YouTube にログインし、閉じて**から、テストをやり直します（第 4 節）。

### 5.5 KDE Plasma（KWallet）

KDE では、yt-dlp は KWallet に問い合わせます（`kwallet-query`）。管理ツールの名前は、ディストリビューションにより `kwalletmanager`（または `kwalletmanager5`）です。この構成は、当方のテストでは**試していません**。

### 5.6 yt-dlp にキーリングを指定する（ターミナル）

ソフトウェアは、キーリングの選択を、デスクトップ環境に応じて yt-dlp に任せています。指定するには、ブラウザー名に `+キーリング名` を付けます（値：`gnomekeyring`、`kwallet`、`kwallet5`、`kwallet6`、`basictext`）。

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium+gnomekeyring -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Chromium が実際にどのキーリングを使っているか調べるには（yt-dlp のコードから引いたコマンドで、ここでは試していません）：

```bash
chromium --enable-logging=stderr --v=1 2>&1 | grep key_storage_
```

### 5.7 キーリングなし：`--password-store=basic`（上級者向け、未検証）

Chromium は `--password-store=basic` を受け付けます。この場合、鍵を平文で保管し（固定で広く知られた鍵）、新しい Cookie を `v10` で暗号化します。yt-dlp はこれをキーリングなしで読み取れます（`chromium+basictext`）。**安全性は低くなります**。ファイルを読めるプログラムなら、これらの Cookie を復号できます。このトレードオフを理解している場合だけ使ってください。すでに保存された Cookie は、おそらく再エンコードされないため、ログインし直してください。

### 5.8 最後の手段

キーリングが壊れている場合は、**先にバックアップ**してください。

```bash
cp -a ~/.local/share/keyrings ~/keyrings-backup
```

`login.keyring` を削除すると、そこに保管されている**すべて**のパスワード（Wi-Fi、オンラインアカウントなど）が消えます。結果を理解せずに行わないでください。

<a id="s6"></a>

## 6. ファイルの場所

データフォルダーは `$XDG_DATA_HOME/yt-dlp-GUI`（既定では `~/.local/share/yt-dlp-GUI`）です。ただし、アーカイブの実行ファイル（または `yt-dlp-gui.pyw` スクリプト）の横に `portable.flag` がある場合は、そのフォルダーになります。

| ファイルまたはフォルダー | 内容 |
|---|---|
| `gui-config.json` | 設定（言語、ブラウザー、フォルダー、ブラウザーの選択など） |
| `download-queue.json` | ダウンロードキュー |
| `custom-blocks.json` | カスタムのオプションブロック |
| `yt-dlp` | アシスタントがダウンロードした実行ファイル |
| `bin/` | ffmpeg、ffprobe、deno |
| `cmd/` | yt-dlp の一時的な設定ファイル |
| `app/` | 「メニューにインストール」が作ったプログラムのコピー |
| `~/.local/share/fonts/yt-dlp-GUI/`（データフォルダーの外） | 韓国語・日本語・中国語用にダウンロードした Noto フォント。削除するには：`rm -rf ~/.local/share/fonts/yt-dlp-GUI` |

<a id="s7"></a>

## 7. トラブルシューティング

| 問題 | ヒント |
|---|---|
| AppImage が起動しない | ターミナルから起動してエラーを読む。FUSE 2 をインストールする（2.2 節）か、`--appimage-extract-and-run` を付ける |
| 何も表示されない、またはライブラリのエラー | glibc のバージョンを確認する：`ldd --version` が 2.35 以上であること |
| デスクトップにアイコンがない | GNOME は既定では表示しません。アプリケーションメニューを使ってください |
| デスクトップのショートカットに警告が出る | 右クリック ›「起動を許可」 |
| ホストと仮想マシンの間のドラッグ＆ドロップが動かない | これは VirtualBox（Guest Additions）の機能で、このソフトウェアの機能ではありません |
| 画面の大きさがおかしい | ソフトウェアはシステムのフォント（Tk）に従います。システムのフォントサイズを変えてみてください |
| yt-dlp の更新に失敗する | オプションメニューの「アップデート & 診断」を使う。だめなら `yt-dlp_linux` をダウンロードし、置き換え用のウィンドウで選ぶ（選んだファイルは実行可能になります） |
| 文字の代わりに四角が表示される（韓国語、中国語、日本語など） | システムにこれらの文字を含むフォントがありません。Debian と Ubuntu では `sudo apt install fonts-noto-cjk`（約 90 MB）を実行し、ソフトウェアを閉じて開き直します。ほかのディストリビューションでは、そのディストリビューションの「Noto Sans CJK」パッケージをインストールします。言語を選ぶとき、ソフトウェア自身がフォントをダウンロードすることもできます（韓国語、日本語、中国語。管理者権限は不要） |

<a id="s8"></a>

## 8. 不具合を報告

「不具合を報告」ボタンは、フォルダー、ユーザー名、メールアドレスを伏せた技術レポートを準備します。自動では何も送信されません。Linux では、次の内容も追加してください。

```bash
cat /etc/os-release
```

```bash
echo "$XDG_CURRENT_DESKTOP $XDG_SESSION_TYPE"
```

さらに、ソフトウェアを**どのように**インストールしたか（AppImage、アーカイブ、`.deb`、ソースコード）を書いてください。Cookie の問題では、**ターミナルでのテスト結果**（第 4 節）も添えてください。Cookie そのものは貼り付けないでください。

<a id="s9"></a>

## 9. 開発者向け

テスト（仮想ディスプレイ上で実行するため、実際の画面は不要）：

```bash
xvfb-run -a python3 -X utf8 -m unittest discover -s tests -t .
```

パッケージのビルド（ビルドツール：`pip install -r packaging/requirements-build.txt`、加えて `appimagetool`。そのパスは変数 `APPIMAGETOOL` で指定します）：

```bash
python3 packaging/build_linux.py
```

```bash
python3 packaging/build_deb.py
```

結果は `dist/` に出力されます。互換性を最大にするには、サポート対象で最も古いディストリビューションでビルドしてください（ビルドマシンの glibc が、プログラムを実行するマシンに求められる最低限になります）。`.deb` の役立つ確認：

```bash
lintian dist/yt-dlp-gui_*_amd64.deb
```

既知の形式上のエラーは `dir-or-file-in-opt`（プログラムを `/opt` に含めていること）だけです。

**公開**：`yt-dlp-gui.pyw` の `__version__` を確認し、`CHANGELOG-linux.md` のそのバージョンの節に日付を入れ、コミットしてから、`Linux-vX.Y.Z` タグを作成してプッシュします。ワークフロー「Release Linux」がテストを実行し、AppImage、アーカイブ、`.deb` をビルドし、合計値を計算して、リリースを**プレリリース（pre-release）**として作成します。「最新リリース」にはなりません（Windows 版 0.1.7 の更新確認が、そこで Linux のタグを見つけてはならないためです）。

ライセンス：MIT。リポジトリのほかの部分と同じです（[LICENSE](../LICENSE) を参照）。
