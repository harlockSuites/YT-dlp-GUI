# Journal des modifications

Le format s'inspire de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et le projet suit le [versionnage sémantique](https://semver.org/lang/fr/).

## [0.1.0] — en préparation

### Ajouté
- Téléchargeur individuel avec file d'attente (pause, reprise, plage, relance en cas d'échec de format).
- Inspecteur de playlist : règles globales, exceptions par vidéo, éléments masqués ignorés.
- Répertoire intelligent : registre JSON par dossier, détection des vidéos déjà présentes, recherche des informations manquantes sur YouTube.
- Voyant d'état des cookies et bouton de test.
- Interface adaptative (reflux des contrôles, défilement vertical et horizontal).
- Interface en 15 langues.
- Fenêtre de don, icône, logo et bannière.
- Numéro de version affiché dans le titre de la fenêtre principale.
- Suite de tests automatiques (`python -m unittest discover -s tests`).
- Bouton « Signaler un bogue » : rapport technique masqué (dossiers, nom d'utilisateur, e-mails), relu par l'utilisateur puis ouvert sur GitHub ; proposé aussi après une erreur interne.
- Assistant d'installation : télécharge yt-dlp et ffmpeg depuis leurs dépôts officiels GitHub, avec vérification SHA-256 ; s'ouvre au premier lancement si yt-dlp.exe est absent, accessible depuis le menu des options.
- Documentation détaillée en 15 langues : `README.md` (français) et `docs/README.<code>.md`, avec un test qui garde les 15 versions alignées.
- Empaquetage Windows : exécutable PyInstaller, installateur Inno Setup (sans droits administrateur, 10 langues) et version portable `.zip` (`python packaging/build.py`). Les données de l'utilisateur vont dans `%LOCALAPPDATA%\yt-dlp-GUI` (ou à côté de l'exécutable en mode portable).
