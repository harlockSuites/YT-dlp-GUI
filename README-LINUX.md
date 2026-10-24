# yt-dlp GUI — version Linux

[Français](README-LINUX.md) · [English](docs/README-LINUX.en.md)

> **Préversion.** Ce document complète le [README principal](README.md) : c'est le même logiciel, mais ici on ne parle que de ce qui est propre à Linux (installation, cookies et trousseaux de clés, fichiers, dépannage). Les nouveautés de chaque version sont dans [CHANGELOG-linux.md](CHANGELOG-linux.md). Les autres langues viendront après relecture du français et de l'anglais.

## Sommaire

1. [État de la préversion](#1-état-de-la-préversion)
2. [Installer](#2-installer)
3. [Premier lancement et dépendances](#3-premier-lancement-et-dépendances)
4. [Cookies du navigateur](#4-cookies-du-navigateur)
5. [Trousseaux de clés : manœuvres à la main](#5-trousseaux-de-clés--manœuvres-à-la-main)
6. [Où sont les fichiers](#6-où-sont-les-fichiers)
7. [Dépannage](#7-dépannage)
8. [Signaler un bogue](#8-signaler-un-bogue)
9. [Pour les développeurs](#9-pour-les-développeurs)

## 1. État de la préversion

La version Linux reprend le comportement de la version Windows 0.1.7 (figée, qui sert de modèle). Elle est publiée comme **préversion GitHub** sous des étiquettes `Linux-vX.Y.Z` : elle n'est jamais présentée comme « dernière version » du dépôt.

**Ce qui a été essayé** (machine virtuelle Debian 12, bureau GNOME, Python 3.11, vrai compte YouTube connecté dans chaque navigateur, octobre 2026) :

- **Cookies de Firefox, Waterfox, Floorp et Zen Browser** : lus navigateur ouvert ou fermé.
- **Cookies de Google Chrome, Chromium, Brave, Vivaldi, Opera et Microsoft Edge** : lus navigateur **fermé**, après avoir lancé chaque navigateur une fois et s'y être connecté à YouTube (voir [la section 5](#5-trousseaux-de-clés--manœuvres-à-la-main)). Téléchargement individuel et Inspecteur de playlist réussis.
- **LibreWolf** : lu seulement quand il est ouvert et connecté (il supprime ses cookies à sa fermeture par défaut).
- **Vidéo privée** avec les cookies de Firefox, et playlist de trois vidéos dont une privée.
- **Paquets** : l'AppImage et l'archive `.tar.gz` sont construites par la CI sur Ubuntu 22.04 ; le `.deb` a été construit, installé, lancé et retiré sous Debian 12 ; « Installer dans le menu » a été essayé avec la vraie AppImage dans un dossier personnel jetable.

**Ce qui n'a pas encore été essayé** :

- les autres distributions (Ubuntu, Fedora, Arch, openSUSE…) et les bureaux autres que GNOME, KDE Plasma (KWallet) compris ;
- les navigateurs en Flatpak ou Snap (sauf l'agencement de LibreWolf en Flatpak, relevé) ;
- Vivaldi, Opera ou Edge **sans** Chrome ni Chromium installés (voir [la section 5](#5-trousseaux-de-clés--manœuvres-à-la-main)) ;
- l'architecture aarch64 (le logiciel la prévoit, mais les paquets ne sont construits que pour x86_64) ;
- la fenêtre « Installer dans le menu » manipulée à la souris sur un vrai bureau (elle est testée par programme) ;
- les traductions : elles sont à faire relire par des locuteurs natifs.

## 2. Installer

### Quel format choisir

| Format | Pour qui | Droits administrateur | Entrée dans le menu |
|---|---|---|---|
| **AppImage** | toute distribution 64 bits récente | non | « Installer dans le menu » (section 2.3) |
| **Archive `.tar.gz`** | idem, sans AppImage ni FUSE | non | « Installer dans le menu » |
| **Paquet `.deb`** | Debian, Ubuntu et dérivés | oui (`sudo`) | automatique |
| **Sources** | développeurs, essais | non | aucune |

Configuration requise : Linux 64 bits (x86_64) d'une distribution de 2022 ou plus récente (glibc 2.35 ou plus), car les paquets sont construits sur Ubuntu 22.04.

Les fichiers sont sur la page des [versions publiées](https://github.com/harlockSuites/YT-dlp-GUI/releases) : cherchez les étiquettes `Linux-v…`, marquées « Pre-release ».

### 2.1 Vérifier le téléchargement

Téléchargez aussi `SHA256SUMS-linux.txt` dans le même dossier, puis :

```bash
sha256sum -c SHA256SUMS-linux.txt --ignore-missing
```

Chaque fichier présent doit afficher `OK`. Cela prouve que votre fichier est identique à celui publié, pas qu'il est sans danger : le code source et la construction automatique sont publics.

### 2.2 AppImage

```bash
chmod +x yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

L'AppImage demande la bibliothèque FUSE 2 :

| Distribution | Paquet |
|---|---|
| Debian, Ubuntu 22.04 et dérivés | `libfuse2` |
| Ubuntu 24.04 et plus récent | `libfuse2t64` |
| Fedora | `fuse-libs` |

Sans FUSE, lancez-la quand même, elle s'extrait d'elle-même dans un dossier temporaire :

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage --appimage-extract-and-run
```

### 2.3 Installer dans le menu (sans administrateur)

Une AppImage lancée par double-clic ne laisse pas d'icône dans le menu des applications. Dans le logiciel : menu des options › **« Installer dans le menu… »**. La fenêtre :

- copie le programme dans `~/.local/share/yt-dlp-GUI/app/` ;
- écrit le lanceur `~/.local/share/applications/yt-dlp-gui.desktop` et l'icône `~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png` ;
- ajoute, si la case est cochée, un raccourci sur le Bureau (marqué « de confiance » pour GNOME quand l'outil `gio` existe) ;
- propose ensuite « Mettre à jour » (elle recopie la version qui tourne) et « Désinstaller ».

« Désinstaller » ne retire que ce que l'installation a créé et **garde vos réglages** et vos outils téléchargés. Un lanceur qui n'a pas notre marque interne (`X-YtDlpGui-Installer=1`) n'est jamais supprimé.

Limites : la fenêtre est disponible depuis l'AppImage et l'archive. Depuis les sources, elle renvoie vers l'AppImage ; depuis le paquet `.deb`, elle explique que le logiciel est déjà dans le menu.

Si le raccourci du Bureau affiche un avertissement : clic droit sur l'icône › « Autoriser le lancement ». Certains bureaux (GNOME par défaut) n'affichent pas d'icônes sur le Bureau : le lanceur du menu fonctionne dans tous les cas.

Pour tout retirer à la main :

```bash
rm -rf ~/.local/share/yt-dlp-GUI/app ~/.local/share/applications/yt-dlp-gui.desktop ~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png ~/Desktop/yt-dlp-gui.desktop
```

### 2.4 Paquet `.deb`

```bash
sudo apt install ./yt-dlp-gui_X.Y.Z_amd64.deb
```

Le programme va dans `/opt/yt-dlp-gui`, avec le lien `/usr/bin/yt-dlp-gui`, le lanceur du menu, l'icône et la licence (`/usr/share/doc/yt-dlp-gui/`). Il dépend de `libc6 (>= 2.35)` et de `libx11-6`.

Pour le retirer (vos réglages, dans `~/.local/share/yt-dlp-GUI`, ne sont jamais touchés) :

```bash
sudo apt remove yt-dlp-gui
```

### 2.5 Archive `.tar.gz`

```bash
tar xzf yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz
```

```bash
./yt-dlp-gui/yt-dlp-gui
```

Pour que les réglages et les outils restent **dans le dossier extrait** (clé USB, essai sans trace), créez un fichier vide `portable.flag` à côté de l'exécutable :

```bash
touch yt-dlp-gui/portable.flag
```

Sans ce fichier, les données vont dans `~/.local/share/yt-dlp-GUI` (section 6).

### 2.6 Depuis les sources

```bash
python3 yt-dlp-gui.pyw
```

Il faut Python 3 avec Tkinter :

| Distribution | Paquet |
|---|---|
| Debian, Ubuntu et dérivés, openSUSE | `python3-tk` |
| Fedora | `python3-tkinter` |
| Arch | `tk` |

### 2.7 Mises à jour

Une vérification quotidienne (désactivable dans le menu des options) cherche les versions `Linux-vX.Y.Z`, préversions comprises, et ne propose **jamais** une version Windows. Elle ouvre la page de téléchargement du fichier qui correspond à votre installation (AppImage, archive ou `.deb`) ; **rien n'est installé automatiquement**. Pour mettre à jour :

- **AppImage ou archive installée dans le menu** : téléchargez la nouvelle AppImage, lancez-la, puis « Installer dans le menu… › Mettre à jour » ;
- **`.deb`** : `sudo apt install ./nouveau-fichier.deb` ;
- **archive non installée** : extrayez la nouvelle archive à la place de l'ancienne.

### 2.8 Tout désinstaller, données comprises

Après avoir retiré le programme (sections 2.3 à 2.5), pour effacer aussi vos réglages, la file d'attente et les outils téléchargés (yt-dlp, ffmpeg, deno) :

```bash
rm -rf ~/.local/share/yt-dlp-GUI
```

Vos vidéos téléchargées ne sont jamais dans ce dossier.

## 3. Premier lancement et dépendances

Au premier lancement, l'assistant d'installation propose de télécharger **yt-dlp** (`yt-dlp_linux`), **ffmpeg** (archive `.tar.xz` des constructions officielles de yt-dlp) et **deno**, depuis leurs dépôts GitHub. Les sommes SHA-256 sont vérifiées, aucun droit administrateur n'est demandé, et les fichiers vont dans `~/.local/share/yt-dlp-GUI` (yt-dlp) et `~/.local/share/yt-dlp-GUI/bin` (ffmpeg, ffprobe, deno). Il reste accessible dans le menu des options.

Seuls ffmpeg et ffprobe sont indispensables ; deno est recommandé (pistes audio secondaires). **AtomicParsley, MKVToolNix et aria2** sont facultatifs : le logiciel affiche, dans la fenêtre « Dépendances », la commande de votre gestionnaire de paquets, à copier dans un terminal. Il ne la lance jamais lui-même. Les mêmes commandes :

| Gestionnaire | Commande |
|---|---|
| apt | `sudo apt install aria2 atomicparsley mkvtoolnix` |
| dnf | `sudo dnf install AtomicParsley aria2 mkvtoolnix` |
| pacman | `sudo pacman -S aria2 atomicparsley mkvtoolnix-cli` |
| zypper | `sudo zypper install AtomicParsley aria2 mkvtoolnix` |

## 4. Cookies du navigateur

yt-dlp lit les cookies **en local**, dans le navigateur choisi (pistes audio secondaires, sous-titres, vidéos privées, contenus réservés aux membres). Par défaut, le logiciel propose les cinq navigateurs les plus utilisés sous Linux (Firefox, Google Chrome, Chromium, Brave, Vivaldi). La fenêtre **« Navigateurs pour les cookies »** du menu des options en propose 11 : cochez ceux dont vous avez besoin ; un ✔ marque ceux dont le dossier de profil existe sur votre ordinateur.

| Navigateur | Lu par yt-dlp comme | Trousseau de clés | Dossiers de profil cherchés |
|---|---|---|---|
| Firefox | `firefox` | non | `~/.config/mozilla/firefox`, `~/.mozilla/firefox`, Flatpak, Snap |
| Google Chrome | `chrome` | oui | `~/.config/google-chrome` |
| Chromium | `chromium` | oui | `~/.config/chromium` |
| Brave | `brave` | oui | `~/.config/BraveSoftware/Brave-Browser` |
| Vivaldi | `vivaldi` | oui | `~/.config/vivaldi` |
| Opera | `opera` | oui | `~/.config/opera` |
| Microsoft Edge | `edge` | oui | `~/.config/microsoft-edge` |
| LibreWolf, Waterfox, Floorp, Zen Browser | `firefox:` + dossier du profil | non | `~/.librewolf`, `~/.config/librewolf`… (même schéma pour les autres), Flatpak compris |

Les dérivés de Firefox n'ont pas de nom reconnu par yt-dlp : le logiciel cherche leur base `cookies.sqlite` (jusqu'à trois niveaux sous leurs dossiers) et donne à yt-dlp le dossier du profil le plus récemment utilisé. `XDG_CONFIG_HOME` est respecté quand il est absolu.

Le **voyant** à côté de la liste indique l'état : rouge (désactivé ou en échec), orange (non testé ou en cours), vert (cookies lus). Le bouton ↻ lance un test ; l'infobulle explique l'erreur. Un test qui lit **0 cookie** n'est jamais vert.

### Cas fréquents

| Ce que vous voyez | Cause probable | Que faire |
|---|---|---|
| « Extracted 0 cookies » puis « Sign in to confirm you're not a bot » | le navigateur ne garde aucun cookie sur le disque (LibreWolf les supprime à sa fermeture par défaut ; profil jamais connecté ; mode privé) | le laisser ouvert et connecté à YouTube, ou désactiver la suppression des cookies à la fermeture dans ses réglages de vie privée |
| « Item does not exist! » avec Chrome, Chromium, Brave, Vivaldi, Opera ou Edge | yt-dlp n'a pas trouvé la clé du navigateur dans le trousseau de clés du bureau | lancer le navigateur une fois, s'y connecter à YouTube, le fermer, refaire le test ; sinon [section 5](#5-trousseaux-de-clés--manœuvres-à-la-main) |
| « Could not copy Chrome cookie database » ou « database is locked » | le navigateur verrouille sa base pendant qu'il tourne | le fermer, puis refaire le test |
| « Failed to decrypt » | cookies chiffrés avec une clé que yt-dlp n'a pas obtenue | [section 5](#5-trousseaux-de-clés--manœuvres-à-la-main) |

### Tester un navigateur depuis un terminal

C'est le meilleur moyen de voir l'erreur exacte (remplacez `IDENTIFIANT` par celui de n'importe quelle vidéo YouTube) :

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIANT"
```

Lignes à repérer : `Extracted N cookies from chromium` (N doit être supérieur à 0), `Chosen keyring: GNOMEKEYRING` (le trousseau choisi), et `cookie version breakdown: {'v10': 0, 'v11': 50, …}` (les cookies `v11` demandent le trousseau, les `v10` non).

Pour un dérivé de Firefox, donnez le dossier du profil. Pour le trouver :

```bash
find ~ -name cookies.sqlite -path "*librewolf*" 2>/dev/null
```

Dans une installation Flatpak, cherchez dans `~/.var/app` :

```bash
find ~/.var/app -name cookies.sqlite 2>/dev/null
```

Puis, avec le dossier qui contient `cookies.sqlite` :

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser "firefox:/chemin/du/profil" -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIANT"
```

## 5. Trousseaux de clés : manœuvres à la main

### À quoi ça sert

Les navigateurs de la famille Chromium (Chrome, Chromium, Brave, Vivaldi, Opera, Edge) chiffrent leurs cookies. La clé de chiffrement est rangée dans le **trousseau de clés du bureau** : GNOME Keyring (ou un équivalent compatible, via le service « Secret Service ») sous GNOME, XFCE, Cinnamon, MATE…, KWallet sous KDE. Pour déchiffrer, yt-dlp demande cette clé au trousseau. Firefox et ses dérivés n'en ont pas besoin.

Deux faits utiles :

- **La clé n'existe qu'après le premier lancement du navigateur.** Dans notre machine virtuelle, l'erreur « Item does not exist! » a disparu quand chaque navigateur a été lancé une fois et connecté à YouTube. La cause exacte du premier échec n'a pas été établie avec certitude : le trousseau existait, était par défaut et déverrouillé.
- **Quel trousseau yt-dlp utilise** dépend du bureau détecté (variables `XDG_CURRENT_DESKTOP` et `DESKTOP_SESSION`), d'après le code de yt-dlp (octobre 2026) :

| Bureau détecté | Trousseau utilisé par yt-dlp |
|---|---|
| GNOME, Cinnamon, MATE, XFCE, Pantheon, Unity, Deepin, UKUI | GNOME Keyring (`GNOMEKEYRING`) |
| KDE 4, 5, 6 | KWallet (`KWALLET`, `KWALLET5`, `KWALLET6`) |
| LXQt, KDE 3, bureau non reconnu (gestionnaires de fenêtres seuls : sway, i3…) | aucun : texte simple (`BASICTEXT`) |

Dans le dernier cas, yt-dlp ne lit que les cookies `v10` : si votre navigateur, lui, range sa clé dans GNOME Keyring, ses cookies `v11` ne seront pas déchiffrés. Il faut alors imposer le trousseau dans un terminal (section 5.6) ; le logiciel ne propose pas encore ce réglage.

Les éléments cherchés dans le trousseau s'appellent « *nom* Safe Storage ». D'après le code de yt-dlp, c'est **« Chrome Safe Storage »** pour Chrome et Vivaldi, **« Chromium Safe Storage »** pour Chromium, Opera et Edge, **« Brave Safe Storage »** pour Brave. Dans notre machine virtuelle, Chrome et Chromium étaient aussi installés et lancés : on ne sait pas si Vivaldi, Opera ou Edge fonctionneraient seuls.

### 5.1 Le trousseau existe-t-il ?

```bash
ls -la ~/.local/share/keyrings/
```

Vous devez voir un fichier `login.keyring` (nom du trousseau « Connexion »/« login »). Ensuite, quel trousseau est le trousseau **par défaut** ?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets --method org.freedesktop.Secret.Service.ReadAlias default
```

Réponse `(objectpath '/org/freedesktop/secrets/collection/login',)` : il y a un trousseau par défaut. Réponse `'/'` : **aucun**, passez à la section 5.4.

### 5.2 Est-il verrouillé ?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Locked
```

`(<false>,)` : déverrouillé. `(<true>,)` : verrouillé ; ouvrez-le avec Seahorse (section 5.4), qui demande son mot de passe.

### 5.3 La clé de mon navigateur y est-elle ?

Listez les éléments :

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Items
```

La réponse donne des chemins se terminant par un numéro (`…/login/1`, `…/login/2`…). Pour lire le nom de chacun (adaptez la liste de numéros) :

```bash
for i in 1 2 3 4 5 6; do gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login/$i --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Item Label; done
```

Vous devez voir, par exemple, `Chromium Safe Storage`, `Chrome Safe Storage` ou `Brave Safe Storage`. Les noms vides sont sans conséquence. Si le nom de votre navigateur manque : lancez-le une fois, connectez-vous à YouTube, fermez-le, puis relancez cette commande.

### 5.4 Créer ou déverrouiller un trousseau avec Seahorse

Installez Seahorse (« Mots de passe et clés ») et les outils associés. La commande exacte est aussi dans la fenêtre « Navigateurs pour les cookies » du logiciel :

| Gestionnaire | Commande |
|---|---|
| apt | `sudo apt install gnome-keyring seahorse libsecret-tools` |
| dnf | `sudo dnf install gnome-keyring seahorse libsecret` |
| pacman | `sudo pacman -S gnome-keyring seahorse libsecret` |
| zypper | `sudo zypper install gnome-keyring seahorse libsecret-tools` |

Puis ouvrez-le :

```bash
seahorse
```

- **Pas de trousseau par défaut** : créez-en un (bouton « + » ou menu Fichier › Nouveau › trousseau de mots de passe), nommez-le « Connexion », puis faites un clic droit dessus › « Définir par défaut ». Les libellés exacts varient selon la version de Seahorse.
- **Trousseau verrouillé** : double-clic ou clic droit › « Déverrouiller », puis saisissez son mot de passe (saisissez-le vous-même, le logiciel ne le demande jamais).
- **Ouverture de session automatique** : un trousseau protégé par un mot de passe ne peut pas s'ouvrir tout seul si vous ne tapez aucun mot de passe à l'ouverture de la session ; il restera verrouillé jusqu'à ce que vous le déverrouilliez (ou que vous utilisiez le même mot de passe pour la session et pour le trousseau).

Ensuite, **lancez le navigateur, connectez-vous à YouTube, fermez-le**, et refaites le test (section 4).

### 5.5 KDE Plasma (KWallet)

Sous KDE, yt-dlp interroge KWallet (`kwallet-query`). Le gestionnaire s'appelle `kwalletmanager` (ou `kwalletmanager5`) selon la distribution. Cette configuration **n'a pas été essayée** par nos tests.

### 5.6 Imposer le trousseau à yt-dlp (terminal)

Le logiciel laisse yt-dlp choisir le trousseau selon le bureau. Pour le forcer, ajoutez `+TROUSSEAU` au nom du navigateur (valeurs : `gnomekeyring`, `kwallet`, `kwallet5`, `kwallet6`, `basictext`) :

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium+gnomekeyring -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIANT"
```

Pour savoir quel trousseau un Chromium utilise réellement (commande tirée du code de yt-dlp, non essayée ici) :

```bash
chromium --enable-logging=stderr --v=1 2>&1 | grep key_storage_
```

### 5.7 Sans trousseau : `--password-store=basic` (avancé, non essayé)

Chromium accepte `--password-store=basic` : il range alors sa clé en clair (une clé fixe, connue) et chiffre ses nouveaux cookies en `v10`, que yt-dlp lit sans trousseau (`chromium+basictext`). **C'est moins sûr** : n'importe quel programme qui lit vos fichiers peut déchiffrer ces cookies. Ne l'utilisez que si vous comprenez ce compromis ; les cookies déjà enregistrés ne sont sans doute pas ré-encodés : reconnectez-vous.

### 5.8 Dernier recours

Si un trousseau est corrompu, **sauvegardez-le d'abord** :

```bash
cp -a ~/.local/share/keyrings ~/keyrings-sauvegarde
```

Supprimer `login.keyring` efface **tous** les mots de passe qu'il contient (Wi-Fi, comptes en ligne…) : ne le faites pas sans en avoir compris les conséquences.

## 6. Où sont les fichiers

Le dossier de données est `$XDG_DATA_HOME/yt-dlp-GUI` (par défaut `~/.local/share/yt-dlp-GUI`), sauf si `portable.flag` est à côté de l'exécutable de l'archive.

| Fichier ou dossier | Contenu |
|---|---|
| `gui-config.json` | réglages (langue, navigateur, dossiers, choix des navigateurs…) |
| `download-queue.json` | file d'attente |
| `custom-blocks.json` | blocs d'options personnalisés |
| `yt-dlp` | exécutable téléchargé par l'assistant |
| `bin/` | ffmpeg, ffprobe, deno |
| `cmd/` | fichiers de configuration éphémères de yt-dlp |
| `app/` | copie du programme faite par « Installer dans le menu » |

## 7. Dépannage

| Problème | Piste |
|---|---|
| L'AppImage ne démarre pas | la lancer depuis un terminal pour lire l'erreur ; installer FUSE 2 (section 2.2) ou ajouter `--appimage-extract-and-run` |
| Rien ne s'affiche, ou erreur de bibliothèque | vérifier la version de la glibc : `ldd --version` doit indiquer 2.35 ou plus |
| Pas d'icône sur le Bureau | GNOME n'en affiche pas par défaut ; utiliser le menu des applications |
| Raccourci du Bureau avec un avertissement | clic droit › « Autoriser le lancement » |
| Le glisser-déposer entre la machine hôte et une machine virtuelle ne marche pas | c'est une fonction de VirtualBox (Additions invité), pas du logiciel |
| L'interface est mal dimensionnée | le logiciel suit les polices du système (Tk) ; essayez une autre taille de police système |
| La mise à jour de yt-dlp échoue | utiliser « Mise à jour & Diagnostic » du menu des options ; sinon télécharger `yt-dlp_linux` et le choisir dans la fenêtre de remplacement (le fichier choisi est rendu exécutable) |

## 8. Signaler un bogue

Le bouton « Signaler un bogue » prépare un rapport technique dont vos dossiers, votre nom d'utilisateur et vos adresses e-mail sont masqués ; rien n'est envoyé automatiquement. Ajoutez-y, pour Linux :

```bash
cat /etc/os-release
```

```bash
echo "$XDG_CURRENT_DESKTOP $XDG_SESSION_TYPE"
```

et dites **comment** vous avez installé le logiciel (AppImage, archive, `.deb`, sources) et, pour un problème de cookies, **le résultat du test depuis un terminal** (section 4), sans coller vos cookies.

## 9. Pour les développeurs

Tests (sous un écran virtuel, sans affichage réel) :

```bash
xvfb-run -a python3 -X utf8 -m unittest discover -s tests -t .
```

Construire les paquets (outils de construction : `pip install -r packaging/requirements-build.txt`, plus `appimagetool` dont le chemin est donné par la variable `APPIMAGETOOL`) :

```bash
python3 packaging/build_linux.py
```

```bash
python3 packaging/build_deb.py
```

Les résultats sont dans `dist/`. Pour la meilleure compatibilité, construisez sur la plus ancienne distribution prise en charge (la glibc de la machine de construction est le minimum exigé des machines qui exécutent le programme). Vérifications utiles du `.deb` :

```bash
lintian dist/yt-dlp-gui_*_amd64.deb
```

La seule erreur de forme connue est `dir-or-file-in-opt` (programme embarqué dans `/opt`).

**Publier** : vérifier `__version__` dans `yt-dlp-gui.pyw`, dater la section de la version dans `CHANGELOG-linux.md`, commiter, puis créer et pousser l'étiquette `Linux-vX.Y.Z`. Le workflow « Release Linux » lance les tests, construit l'AppImage, l'archive et le `.deb`, calcule les sommes et crée la release en **préversion**, jamais « dernière version » (la recherche de mise à jour de la version Windows 0.1.7 ne doit pas y trouver d'étiquette Linux).

Licence : MIT, comme le reste du dépôt (voir [LICENSE](LICENSE)).
