# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

A graphical interface for [yt-dlp](https://github.com/yt-dlp/yt-dlp), designed to make it accessible to everyone while making full use of its capabilities.

> **Work in progress.** Some features may change, be incomplete or contain bugs. The software is currently available for Windows; **a Linux version will be released in the medium term.**

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## Features

### Single downloader and queue

- **Options**: maximum quality (up to 4K), audio only (MP3), subtitles (vtt, srt, ass formats), embedding of subtitles and thumbnail, main audio language, secondary audio tracks (multi-track MKV file) and a library of "script blocks" (post-processing, export, network, behavior) that you can extend with your own blocks.
- **Multiple audio tracks**: in the MKV file, the audio tracks do not carry the name of their language. Your player may show them as "Track 1", "Track 2"… or without a language label. This is a known limitation.
- **Generated command**: the yt-dlp command matching your choices is displayed live.
- **Queue**: add the current URL, then run the whole queue, from one item onward, a single video or a range; pause and resume, skip the current item, stop with cleanup of partial files. The queue is kept between sessions.

### Playlist inspector

- **Analysis** of a playlist: each video is listed with its available audio tracks and subtitles; hidden, private or deleted items are ignored without blocking the rest.
- **Global rules** (quality, audio only, subtitle format and embedding, thumbnail, numbering, languages, script blocks, output folder) with **per-video exceptions** for the main language, secondary tracks and subtitles.
- **Color code**: red when the main language is missing, orange when a secondary track or a subtitle is missing.
- **Downloading the selection** with a log, pause, resume and skip; if requested tracks do not exist, the video is retried without them, then a **summary** shows what succeeded, was adjusted or failed.

### Smart directory and registry

- **Smart directory**: yt-dlp skips videos that were already downloaded thanks to a registry stored in the output folder. The `.yt-dlp-registre.json` file holds each video's ID, URL, title, duration, file name and date; `.yt-dlp-archive.txt`, read by yt-dlp, is derived from it.
- **Retroactive check**: if videos in the selection are already in the folder but missing from the registry, a window offers to register and skip them (by comparing titles). You can untick false matches.
- **Update the registry**: counts the videos in the folder, those in the registry and those missing, then looks up the missing information on YouTube (title, and duration via ffprobe). Nothing is registered without your confirmation, and two buttons open the local file or the YouTube link found so you can check.

![yt-dlp GUI](img/registry.en.png)

### Browser cookies

- Choose the browser (Chrome, Firefox, Edge, Brave, Opera) whose cookies yt-dlp reads locally: they are needed for secondary audio tracks and some subtitles. **Firefox is recommended.**
- **Our test results** (Windows 11, October 2026, YouTube account signed in on each browser): **Firefox** works, whether the browser is open or closed. **Opera** works **only with the browser closed**: it locks its cookie database while open, and yt-dlp then shows "Could not copy Chrome cookie database". **Chrome, Edge and Brave** fail even when closed: they encrypt their cookies in a way yt-dlp cannot always read. These limits come from the browsers and yt-dlp, not from this software, and may change with their updates.
- If your browser is set to **delete cookies when it closes** (or you browse in private mode), no cookie remains on disk to read: yt-dlp cannot recover anything, whether with Chrome, Edge, Brave or Firefox. With Chrome, Edge and Brave this is a trap: the browser must be closed, which then erases the cookies. Turn that option off, or keep the cookies of youtube.com and google.com.
- A **status light** shows the state: red if disabled or failed, orange if untested or in progress, green if the cookies are loaded. The ↻ button runs a test and the tooltip explains the state or the error.

### Setup assistant, dependencies and yt-dlp updates

- **Setup assistant**: on first launch, it offers to download yt-dlp and ffmpeg from their official GitHub repositories. The SHA-256 checksum is verified and no administrator rights are needed.
- **Dependencies**: the dedicated window checks ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 and deno, and can install them with Chocolatey.
- **Update and diagnostics**: updates yt-dlp (`yt-dlp -U`) or replaces its executable, shows its version and checks the options used by the GUI.
- **Software update**: a daily check (can be turned off) signals a new version with a discreet banner; the dedicated window shows what's new and opens the download matching your installation (installer or portable version). Nothing is installed automatically. A switch in the options menu ("Check for updates at startup") turns the automatic check on or off, and "Check for a software update…" runs it on demand.

### Interface and languages

- Controls wrap according to the window width; the content scrolls vertically, and the inspector table also scrolls horizontally.
- Interface in **15 languages**: French, English, Spanish, Portuguese, Italian, Polish, Hungarian, Serbian, Russian, Vietnamese, Chinese, Hindi, Japanese, Korean and Filipino. A language change applies at restart, with the option to restart right away.

### Report a bug

- The "Report a bug" button prepares a technical report: versions of the software, Python, Windows and yt-dlp, harmless settings and the last log lines. Your folders, user name and e-mail addresses are masked.
## Installation

- **Installer (recommended)**: download `yt-dlp-gui-setup-X.Y.Z.exe` from the [releases page](https://github.com/harlockSuites/YT-dlp-GUI/releases) and run it. Windows 10 or 11 (64-bit), no administrator rights needed; Python is not required.
- **Portable version**: download `yt-dlp-gui-portable-X.Y.Z.zip`, extract it anywhere and run `yt-dlp-gui.exe`; settings stay in that folder.
- **From source**: see the "Requirements" and "Quick start" sections below.
- **Windows SmartScreen warning**: the installer is not digitally signed, so Windows may show "Windows protected your PC". Click "More info", then "Run anyway". To check the file's authenticity, compare its SHA-256 sum with the one in `SHA256SUMS.txt`, published with every release:

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

- Nothing is sent automatically: you review and edit the report, then open a pre-filled GitHub issue page (or copy the report).

## Requirements

- Windows
- [Python 3](https://www.python.org/) with Tkinter (included in the standard installation)
- `yt-dlp.exe` and preferably [ffmpeg](https://ffmpeg.org/): the setup assistant downloads them on first launch

## Quick start

1. Download or clone this repository and go to its folder.
2. Run `yt-dlp-gui.bat` (or `pythonw yt-dlp-gui.pyw`).
3. On first launch, let the assistant install yt-dlp and ffmpeg; it stays available in the options menu.
4. Paste a URL, choose your options, then download, add to the queue or open the inspector for a playlist.

## Privacy and responsible use

- This software sends no data to the author and contains no telemetry. Network connections go through yt-dlp (video sites), the setup assistant (GitHub) and the registry tool (YouTube search). An automatic update check also contacts GitHub at startup (at most once a day); you can turn it off from "Check for updates at startup".
- Your cookies stay on your computer: yt-dlp reads them locally from the chosen browser.
- Use this tool in compliance with copyright, the terms of use of the sites and the laws of your country, and only download what you are allowed to download.

## Development

The tests (translations, registry, command building, interface, setup assistant, documentation) are run with:

```bash
python -X utf8 -m unittest discover -s tests -t .
```

They also run automatically on GitHub with every push. The version number is defined by `__version__` in `yt-dlp-gui.pyw` and must match the header of [CHANGELOG.md](../CHANGELOG.md). The interface translation files are in `lang/` and those of this documentation in `docs/`; reviews by native speakers are welcome.

## Support the project

Using this GUI is, has always been and will remain free and open to everyone. If the tool is particularly useful to you, you can support the project on [Ko-fi](https://ko-fi.com/harlocksuites).

## Acknowledgements

Thanks to the community that regularly updates [yt-dlp](https://github.com/yt-dlp/yt-dlp), without which none of this would be possible.

## License

The code is released under the [MIT](../LICENSE) license. The icon, logo and "Harlock S." banner (`yt-dlp-gui.ico` file and `assets/` folder) are original creations generated by AI at the author's request. They form the project's visual identity and are not covered by the MIT license: please do not reuse them for another project or in a way that could cause confusion.
