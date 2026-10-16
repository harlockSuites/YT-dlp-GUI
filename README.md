# yt-dlp GUI

Interface graphique pour [yt-dlp](https://github.com/yt-dlp/yt-dlp), pensée pour rendre son utilisation accessible à tous tout en exploitant pleinement ses capacités.

> **Projet en cours de développement.** Certaines fonctionnalités peuvent changer, être incomplètes ou contenir des bogues.

## Fonctionnalités

- **Téléchargeur individuel** : qualité maximale, audio seul, sous-titres (format au choix, intégrés ou non), miniature intégrée, langue principale, pistes audio secondaires et blocs de script.
- **File d'attente** : lancement de toute la file, à partir d'un élément ou d'une plage, avec pause et reprise.
- **Inspecteur de playlist** : analyse d'une playlist, disponibilité des pistes audio et des sous-titres par vidéo, règles globales avec exceptions par vidéo, éléments masqués ou privés ignorés.
- **Répertoire intelligent** : un registre propre à chaque dossier (`.yt-dlp-registre.json`) mémorise les vidéos déjà téléchargées pour ne pas les retélécharger. Un outil de mise à jour retrouve les vidéos déjà présentes dans un dossier et recherche leurs informations manquantes sur YouTube, avec confirmation avant toute inscription.
- **Cookies du navigateur** : voyant d'état et bouton de test pour vérifier que les cookies sont bien lisibles.
- **Interface adaptative** : les contrôles se replient selon la largeur de la fenêtre, avec défilement vertical et horizontal si nécessaire.
- **15 langues** : français, anglais, espagnol, portugais, italien, polonais, hongrois, serbe, russe, vietnamien, chinois, hindi, japonais, coréen et filipino.

## Prérequis

- Windows
- [Python 3](https://www.python.org/) avec Tkinter (inclus dans l'installation standard)
- `yt-dlp.exe`, à placer dans le même dossier que le logiciel
- Recommandé : [ffmpeg](https://ffmpeg.org/) (fusion des flux, intégration des sous-titres et des miniatures, durée des fichiers pour l'outil de registre)

La fenêtre « Options, Mise à jour & Dépendances » du logiciel vérifie les outils utiles (ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2, deno) et aide à les installer.

## Utilisation

1. Place `yt-dlp.exe` à côté de `yt-dlp-gui.pyw`.
2. Lance `yt-dlp-gui.bat` (ou `pythonw yt-dlp-gui.pyw`).
3. La langue se change depuis le menu des options.

## Structure

| Élément | Rôle |
|---|---|
| `yt-dlp-gui.pyw` | Application principale |
| `lang/` | Fichiers de traduction (un fichier JSON par langue) |
| `assets/` | Logo et bannière |
| `yt-dlp-gui.bat` | Lanceur Windows |

## Développement

Les tests (traductions, registre, construction des commandes, interface) se lancent avec :

```bash
python -X utf8 -m unittest discover -s tests -t .
```

Ils tournent aussi automatiquement sur GitHub à chaque envoi. Le numéro de version est défini par `__version__` dans `yt-dlp-gui.pyw` et doit correspondre à l'en-tête de `CHANGELOG.md`.

## Gratuit et libre

L'utilisation de ce GUI est, a été et restera gratuite et libre d'accès à quiconque. Si l'outil vous est particulièrement utile, vous pouvez soutenir le projet sur [Ko-fi](https://ko-fi.com/harlocksuites).

## Remerciements

Merci à la communauté qui met régulièrement à jour [yt-dlp](https://github.com/yt-dlp/yt-dlp), sans lequel rien de cela ne serait possible.

## Licence

Le code est publié sous licence [MIT](LICENSE). Le logo et la bannière « Harlock S. » (dossier `assets/`) sont la marque personnelle de l'auteur et ne sont pas couverts par cette licence : tous droits réservés.
