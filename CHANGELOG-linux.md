# Journal des modifications — version Linux

Ce journal est celui de la **version Linux** de yt-dlp GUI : ses étiquettes sont de la forme `Linux-vX.Y.Z` et ses versions sont publiées comme **préversions GitHub**. La version Windows a son propre journal, [CHANGELOG.md](CHANGELOG.md), et ses propres étiquettes (`vX.Y.Z`) : elle est figée à la 0.1.7 et sert de modèle au comportement et aux fonctionnalités de la version Linux.

Le format s'inspire de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et le projet suit le [versionnage sémantique](https://semver.org/lang/fr/).

## [0.1.1] — non publiée

### Ajouté
- **Navigateurs pour les cookies, au choix** : par défaut, les listes proposent les cinq navigateurs les plus utilisés sous Linux (Firefox, Google Chrome, Chromium, Brave, Vivaldi). La fenêtre « Navigateurs pour les cookies » du menu des options propose 11 navigateurs (Opera, Microsoft Edge, LibreWolf, Waterfox, Floorp et Zen Browser en plus) : l'utilisateur coche ceux dont il a besoin ; un ✔ marque ceux dont le dossier de profil existe sur l'ordinateur ; « Rétablir les cinq par défaut » revient au départ. Le choix est enregistré (réglage `linux_browsers`) et le navigateur déjà sélectionné reste toujours dans la liste.
- LibreWolf, Waterfox, Floorp et Zen Browser, dérivés de Firefox, sont lus par le dossier de leur profil (`--cookies-from-browser firefox:/chemin`, y compris les installations Flatpak). Le logiciel cherche leur base de cookies (`cookies.sqlite`, jusqu'à trois niveaux sous leurs dossiers habituels : anciens `~/.nom` et récents `~/.config/nom`, Flatpak compris) et donne à yt-dlp le dossier du profil le plus récemment utilisé. Agencement relevé et confirmé pour LibreWolf en Flatpak (VM, 2026-10-23 : `config/librewolf/librewolf/<profil>`, `.librewolf` étant vide) ; Waterfox, Floorp et Zen restent à confirmer sur une machine qui les a installés.
- 3 clés de traduction (fenêtre de choix) dans les 15 langues, à faire relire ; puce « Cookies » des 15 README mise à jour.

### Modifié
- Sous Linux, les listes ne proposent plus d'office sept navigateurs (dont Edge, Opera) : ce sont les cinq par défaut, ou le choix de l'utilisateur. Windows n'est pas concerné.
- Les messages d'aide sur les cookies nomment le navigateur proprement (« Zen Browser », « Google Chrome »).

### Vérifié
- Lecture des cookies de Firefox avec un compte YouTube connecté, dans la VM : vidéo privée téléchargée par le téléchargeur individuel et par l'Inspecteur de playlist ; playlist de trois vidéos dont une privée. Les autres navigateurs n'ont pas encore été essayés avec un compte connecté.

## [0.1.0] — 2026-10-23

### Ajouté
- **Première version Linux (préversion)**, portée du comportement de la version Windows 0.1.7 (essayée sous Debian 12, Python 3.11, Tk 8.6, puis sous un écran virtuel Xvfb ; aucun essai sur un bureau réel ni avec un compte YouTube).
  - Paquets : AppImage `yt-dlp-gui-X.Y.Z-x86_64.AppImage` et archive `yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz` (PyInstaller, construits sur Ubuntu 22.04, donc glibc 2.35 ou plus), avec `SHA256SUMS-linux.txt`. `packaging/build_linux.py`, `AppRun`, lanceur `.desktop` et icône PNG (extraite du `.ico`). L'AppImage demande `libfuse2`, sinon `--appimage-extract-and-run`.
  - Couche de plateforme dans `yt-dlp-gui.pyw` : fenêtres de console, arrêt d'un arbre de processus (groupe de processus), pause et reprise (`SIGSTOP` / `SIGCONT`), ouverture d'un fichier (`xdg-open`), liste des processus (`/proc`), dossier des données `$XDG_DATA_HOME/yt-dlp-GUI` (par défaut `~/.local/share/yt-dlp-GUI`).
  - Assistant d'installation : yt-dlp (`yt-dlp_linux`), ffmpeg (archive `.tar.xz`) et Deno téléchargés depuis leurs dépôts officiels, somme SHA-256 vérifiée, droit d'exécution donné, sans administrateur ; une ligne « indisponible » quand l'architecture n'a pas de téléchargement officiel. Architectures : x86_64 et aarch64 (les paquets du logiciel lui-même ne sont construits que pour x86_64).
  - Fenêtre Dépendances sans Chocolatey : pour AtomicParsley, MKVToolNix et aria2, la commande du gestionnaire de paquets (apt, dnf, pacman ou zypper) s'affiche avec un bouton « Copier » ; le logiciel ne la lance jamais.
  - Cookies : Firefox, Chromium, Chrome, Brave, Edge, Opera et Vivaldi sont proposés ; note sur le trousseau de clés du bureau (GNOME Keyring, KWallet) pour les navigateurs de la famille Chromium ; messages d'aide propres à Linux. Seule la lecture d'un profil Firefox a été essayée.
  - Interface : molette de la souris sous X11 (boutons 4 et 5, y compris pour les listes déroulantes, et Maj + molette), polices système de Tk, thème `clam`, icône de fenêtre PNG et classe de fenêtre `yt-dlp-gui`. L'avertissement sur les miniatures dans l'Explorateur Windows n'est pas affiché, et la fenêtre « remplacer yt-dlp » propose tous les fichiers (sans `.exe`) et rend le fichier choisi exécutable.
  - Mise à jour du logiciel : la recherche parcourt les releases dont l'étiquette est `Linux-vX.Y.Z` (préversions comprises) et n'en propose jamais une de la version Windows ; types d'installation « appimage » et « portable » ; le téléchargement proposé correspond à l'architecture (`yt-dlp-gui-X.Y.Z-<arch>.AppImage` ou `yt-dlp-gui-linux-X.Y.Z-<arch>.tar.gz`). Comme sous Windows, rien n'est installé automatiquement.
  - 12 clés de traduction (fenêtre Dépendances, assistant, cookies) et 1 clé pour le dialogue de remplacement de yt-dlp, dans les 15 langues. Les traductions sont à relire par des locuteurs natifs.
- Documentation : section Linux dans les 15 README (préversion annoncée dans le bandeau, puces d'installation AppImage et archive, configuration requise et vérification `sha256sum -c`, où trouver les fichiers, cookies, dépendances, prérequis et démarrage rapide).
- Publication : une version Linux est une **préversion GitHub** d'étiquette `Linux-vX.Y.Z`, jamais la « dernière version » du dépôt : la recherche de mise à jour de la version Windows 0.1.7, qui interroge la dernière version, n'est donc pas affectée. Le workflow `release.yml` de cette branche ne construit que Linux ; `packaging/release_tools.py` accepte `--prefix Linux-v`, `--changelog CHANGELOG-linux.md` et `--platform linux` ; `appimagetool` 1.9.1 est téléchargé avec sa somme SHA-256 fixée.
- Tests : la suite passe sous Windows et sous Debian 12 (Xvfb) ; le chargeur de tests donne explicitement son chargeur à `importlib` (l'extension `.pyw` n'est reconnue que par Windows) ; nouveaux fichiers `tests/test_platform.py`, `tests/test_linux_support.py` et `tests/test_linux_package.py`. Le workflow « Tests » tourne aussi sous Ubuntu (Xvfb) et sur la branche `Linux`.
