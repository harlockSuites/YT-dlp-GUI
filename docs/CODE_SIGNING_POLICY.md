<!--
  Avant de publier cette page et d'envoyer la demande à la SignPath Foundation :
  1. activer l'authentification à deux facteurs sur le compte GitHub harlockSuites et sur le compte SignPath ;
  2. relire la section « Status » : la retirer quand les premières versions signées existent ;
  3. lier cette page depuis le README (terme « Code signing policy ») et depuis les notes de release.
-->

# Code signing policy

Free code signing provided by [SignPath.io](https://signpath.io), certificate by [SignPath Foundation](https://signpath.org).

> **Status:** code signing for yt-dlp GUI is being set up. Versions up to 0.1.4 are **not** signed. This page describes how signed releases will be produced.

## Scope

Only the Windows binaries of this project are signed, and only when they are built from this repository's source code:

- `yt-dlp-gui.exe` (the application, built with PyInstaller);
- `yt-dlp-gui-setup-X.Y.Z.exe` (the installer, built with Inno Setup).

Third-party components that are bundled unchanged (the Python runtime, libraries, and the yt-dlp and FFmpeg builds downloaded by the setup assistant) are not signed by this project.

Product name and product version attributes of every signed file are set by the build: product name `yt-dlp GUI`, product version equal to the version of the release.

## Team roles

The project is maintained by one person, who holds all roles:

- **Committers and reviewers:** [harlockSuites](https://github.com/harlockSuites). Contributions from other people are reviewed by the maintainer before they are merged.
- **Approvers:** [harlockSuites](https://github.com/harlockSuites). Every release is approved manually before its files are signed.

All team members use multi-factor authentication on GitHub and on SignPath.

## How a release is signed

1. A release is created by pushing a tag `vX.Y.Z` that matches the version in the source code.
2. The [release workflow](../.github/workflows/release.yml) runs the automated tests, then builds the files on a GitHub-hosted runner from the tagged commit.
3. The built files are submitted to SignPath for signing. Signing requires the manual approval of an approver.
4. The signed files are published on the [GitHub Releases](https://github.com/harlockSuites/YT-dlp-GUI/releases) page together with a `SHA256SUMS.txt` file.

Build scripts and workflow files are part of the source code and are reviewed like any other change.

## Privacy policy

yt-dlp GUI does not collect, store or send personal data to its author. It contains no telemetry, no analytics and no user accounts. It connects to other systems only in these cases:

- **GitHub**, to check once per day at startup whether a new version of yt-dlp GUI exists (this check can be turned off in the options menu), and to download yt-dlp and FFmpeg builds, verified with their published checksums, when the user runs the setup assistant.
- **The video sites chosen by the user**, through yt-dlp. If the user selects a browser for cookies, the cookies are read locally and used only by yt-dlp for its requests to the site being downloaded from.
- **YouTube**, when the user starts the registry tool, to search for missing video information.
- **Web pages opened in the user's browser**, only when the user clicks the matching button: the bug report page (a pre-filled GitHub issue that the user reviews and submits) and the donation page.

Like any web request, these connections reveal the user's IP address to the server contacted. The privacy policies of GitHub, of the video sites used, and of the third-party components yt-dlp and FFmpeg apply to their own services. See also the "Privacy and responsible use" section of the [README](../README.md).

## Installation, system changes and uninstallation

The installer installs for the current user by default, without administrator rights, in `%LOCALAPPDATA%\Programs\yt-dlp GUI`, and the application stores its settings in `%LOCALAPPDATA%\yt-dlp-GUI`. Installing optional dependencies with Chocolatey is started only by the user, from the dependencies window, and Windows asks for administrator approval first. The uninstaller removes the application and offers to delete its data; downloaded videos are never deleted.

## Reporting a problem with a signed file

If you believe that a file signed under this policy violates it, please [open an issue](https://github.com/harlockSuites/YT-dlp-GUI/issues) or write to [support@signpath.io](mailto:support@signpath.io) with a concise report and proof.
