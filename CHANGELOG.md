# Journal des modifications

Le format s'inspire de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et le projet suit le [versionnage sémantique](https://semver.org/lang/fr/).

## [Non publié]

### Ajouté
- Installateur et désinstalleur : quand yt-dlp GUI est encore ouvert, une fenêtre propose « Forcer la fermeture » (fermeture normale d'abord, puis forcée au bout de 5 secondes, téléchargements en cours interrompus), « J'ai fermé le logiciel » (revérifie) ou « Annuler ». Auparavant, il fallait fermer le logiciel soi-même. En mode silencieux, rien n'est demandé : le logiciel n'est fermé qu'avec `/FORCECLOSE=1`, sinon l'installation ou la désinstallation s'arrête. Textes dans les 14 langues de l'installateur.
- Formulaire « Signaler un bogue » (et README, 15 langues) : mention qu'envoyer le rapport demande un compte GitHub gratuit.
- Vidéo privée : quand yt-dlp répond « Private video », un conseil clair s'affiche dans le journal (téléchargeur individuel, file d'attente, inspecteurs) : la vidéo est privée, seuls son propriétaire et les comptes invités la voient ; si elle vous appartient, vérifier que le navigateur choisi est connecté au bon compte YouTube (ou en choisir un dans le cadre Cookies quand ils sont désactivés). 15 langues.
- Téléchargeur individuel : « Inspecter » sur une adresse de playlist affiche maintenant le titre de la playlist, le nombre de vidéos et celles qui sont indisponibles (privées, supprimées ou masquées, donc impossibles à télécharger), au lieu de « Erreur : réponse JSON invalide » (une seule requête rapide, `--flat-playlist`, 15 langues). Les deux écritures d'adresse sont reconnues (« …/playlist?list=… » et l'adresse brute « …/show/VL… » d'une série, dont le titre est alors indiqué « sans titre »). Le téléchargement de la playlist n'est pas modifié.
- Cookies : Edge, Chrome et Brave, qui ne fonctionnent pas sous Windows (cookies chiffrés d'une façon que yt-dlp ne lit pas, même navigateur fermé), sont masqués par défaut dans toutes les listes de navigateurs (Windows seulement ; visibles par défaut ailleurs). Le menu des options a une entrée « Navigateurs pour les cookies… » avec une case pour les afficher à nouveau et une phrase qui explique ce choix (15 langues) ; les listes ouvertes se mettent à jour tout de suite. Un navigateur déjà choisi dans les réglages reste dans la liste tant qu'on ne l'a pas changé.

### Corrigé
- Inspecteur de playlist : la liste des vidéos est maintenant demandée avec les cookies du navigateur choisi. Sans eux, une vidéo privée appartenant au compte connecté n'avait pas de titre et était ignorée comme « masquée », même avec le bon compte (la playlist semblait avoir une vidéo de moins ; une adresse de vidéo privée donnait « Aucune vidéo trouvée »). Même correction pour l'adresse d'une vidéo privée seule : son champ « disponibilité » vaut « private » pour son propriétaire, ce qui la faisait ignorer ; seules les vidéos réservées aux abonnés ou aux membres payants le sont encore. Quand la liste échoue, la raison (cookies verrouillés, vidéo indisponible…) s'affiche dans le journal, sans lignes en double.
- File d'attente : le texte des éléments (en attente, en cours, en erreur) était gris clair sur le fond blanc du tableau et presque illisible ; il est maintenant foncé (contraste vérifié par un test).
- Fenêtre de mise à jour : les messages longs, comme celui d'une absence de connexion, passent à la ligne selon la largeur de la fenêtre au lieu de déborder.
- Messages sans connexion : la recherche de mise à jour et l'assistant d'installation affichent « Pas de connexion à Internet. Vérifiez votre connexion (câble, Wi-Fi, VPN ou pare-feu), puis réessayez. » (ou « le serveur ne répond pas », « impossible de joindre le serveur ») au lieu de « [Errno 11001] getaddrinfo failed » ; le détail technique reste entre parenthèses. 15 langues.
- Analyse d'une vidéo dans le téléchargeur individuel : « Pistes audio : info » s'affichait pour une vidéo sans langue déclarée (par exemple une vidéo privée analysée avec le bon compte), car la ligne « [info] Available formats for … » de yt-dlp était lue comme un code de langue ; seules les lignes du tableau des formats comptent maintenant.
- Inspecteur de playlist : fermer la fenêtre pendant une analyse ouvrait trois boîtes « Erreur interne » (une par action de fin d'analyse planifiée après la fermeture). Ces actions sont maintenant ignorées quand la fenêtre n'existe plus.

## [0.1.6] — 2026-10-20

### Ajouté
- Fenêtre Dépendances : une note explique que seuls ffmpeg et ffprobe sont indispensables, que Deno est recommandé (pistes audio secondaires) et qu'AtomicParsley, MKVToolNix et aria2 sont facultatifs. Ces trois outils absents s'affichent « – Facultatif » en gris au lieu de « ✘ Absent » en rouge, Deno « ○ Recommandé », et l'absence de Chocolatey est présentée comme une information et non plus comme un avertissement rouge. Colonnes « Statut » et « Rôle » élargies (textes coupés). README (15 langues) : même précision dans la puce « Dépendances ».
- Arrêter (ou sauter) une playlist déjà en partie téléchargée ouvre une question : « Oui » supprime tout, y compris les vidéos déjà terminées ; « Non » supprime seulement la vidéo en cours et conserve les autres ; « Annuler » poursuit le téléchargement ; il est mis en pause pendant la question, pour que rien de plus ne soit téléchargé ni oublié par la suppression globale, et ne reprend que si l'on annule (téléchargeur individuel et file d'attente, 15 langues). Auparavant, un arrêt supprimait aussi les vidéos terminées de la playlist.
- README (15 langues) : note sur les noms de fichiers existants du téléchargeur individuel (suffixe `_2`, `_3`… pour une vidéo seule ; une playlist n'est pas renumérotée et ignore les vidéos déjà présentes).

### Corrigé
- Bilan de fin de file de téléchargement : il plantait (« KeyError: 'sauté' ») dès qu'une vidéo avait été sautée, et la fenêtre ne s'affichait pas. Le statut « sauté » est maintenant affiché, avec son nombre dans le résumé (15 langues). Le défaut existait depuis la première version.
- Fenêtre de téléchargement : sauter une vidéo pendant une pause relançait bien la suivante, mais le bouton restait sur « Reprendre » ; il est remis sur « Pause ».
- Fenêtre principale : le bandeau des dépendances n'affiche plus les outils facultatifs (AtomicParsley, MKVToolNix, aria2) comme des dépendances manquantes en orange ; s'ils sont seuls absents, c'est une simple information en gris (« le logiciel fonctionne sans »), et l'avertissement ne liste que les outils indispensables (15 langues).
- Fenêtre Dépendances sans Chocolatey : une phrase explique pourquoi « Tout installer » est grisé et quoi faire (bouton « Site officiel » de chaque outil ; Deno s'installe sans Chocolatey).
- Téléchargeur individuel : une playlist terminée avec quelques vidéos indisponibles (supprimées, privées…) n'affiche plus « ✘ Échec ou annulé » alors que les autres sont téléchargées ; le message indique « Playlist terminée : N vidéo(s) téléchargée(s), M indisponible(s) ou en erreur » (15 langues). Un arrêt demandé en cours de route reste un échec, et un élément de la file d'attente dans ce cas reste en erreur pour que l'utilisateur décide de le relancer.
- Conseil pour les vidéos à restriction d'âge reformulé : il ne dit plus seulement « réessayez » alors que le téléchargement réussit ; il précise que la qualité peut être réduite tant que le compte n'est pas vérifié pour l'âge (15 langues).
- Les fichiers de commande temporaires laissés par un arrêt brutal (Gestionnaire des tâches) sont supprimés à chaque démarrage : leur nom porte maintenant le numéro du processus qui les a créés, et un fichier dont le processus ne tourne plus est supprimé tout de suite, sans toucher à ceux d'une autre fenêtre du logiciel. Les anciens fichiers, sans numéro, partent après une minute.

## [0.1.5] — 2026-10-19

### Ajouté
- Molette de la souris : elle fait maintenant défiler la zone défilante sous le pointeur où qu'il soit (étiquettes, cadres, boutons, listes de langues, lignes du tableau de l'inspecteur) au lieu de ne fonctionner que sur quelques contrôles ; une liste déroulante survolée fait défiler la page sans changer sa valeur, et les tableaux et zones de texte gardent leur propre défilement.
- Champ URL : quand du texte a été collé autour de l'adresse (par exemple « Inspection : https://… » suivi d'un journal), le logiciel prend la première adresse `http(s)` du texte, corrige le champ à l'écran et l'utilise pour l'analyse, le téléchargement, la file d'attente et la playlist avancée.
- File d'attente : bouton « Relancer les erreurs » (remet en attente tous les éléments en erreur et relance la file).
- Fenêtre principale : encadré sous le champ URL qui affiche, une fois l'analyse terminée, le titre, la durée, la chaîne et les langues audio et de sous-titres détectées (ou l'échec de l'analyse) ; il disparaît quand l'URL change.
- Deno est installable par l'assistant d'installation (téléchargement depuis les versions officielles, somme SHA-256 vérifiée, dossier de données du logiciel), sans Chocolatey ni droits administrateur.

### Corrigé
- « Tout installer (admin) » n'utilise plus un PowerShell masqué avec contournement de la politique d'exécution, montage que des antivirus de comportement bloquaient : l'élévation passe par ShellExecute (« runas ») et une fenêtre visible. Le bouton est désactivé, avec une explication, quand Chocolatey est absent ; un refus de l'élévation est signalé.
- Antivirus : quand Windows refuse d'ouvrir un fichier bloqué (« le fichier contient un virus ou un logiciel potentiellement indésirable », WinError 225), le logiciel explique la marche à suivre (exclure le dossier de données, restaurer depuis la quarantaine) au lieu d'afficher une « Erreur interne ». Le remplacement de `yt-dlp.exe`, de ffmpeg et de Deno réessaie plusieurs fois quand l'antivirus analyse encore le fichier (WinError 32).
- Fenêtre principale : le journal ne recouvre plus les boutons de la file d'attente, y compris au démarrage. Quand la fenêtre est basse, la page s'allonge et se parcourt avec la barre de défilement ; seuls les tableaux (file, journal) se réduisent, à la souris, et jamais jusqu'à cacher les boutons.
- Fenêtres de choix des pistes audio secondaires et des sous-titres : elles s'ouvrent toujours près de la case cliquée mais sont décalées pour tenir entièrement dans l'écran ; sur un petit écran leur hauteur est limitée, la liste défile et les boutons de validation restent visibles.
- Cookies : conseils explicites dans le journal (et l'infobulle du voyant) quand YouTube refuse les cookies (« cookies no longer valid » : session renouvelée, se reconnecter dans le navigateur), pour une vidéo à restriction d'âge (selon que les cookies sont activés ou non) et quand YouTube demande de confirmer que l'on n'est pas un robot. La file d'attente affiche aussi le conseil quand la vidéo a été téléchargée en mode dégradé.
- Inspecteur de playlist : les sous-titres téléchargés à part (sans « Intégrer ST ») portent maintenant exactement le nom de la vidéo, avec son préfixe de numérotation et son suffixe `_2`, `_3`… ; ils recevaient auparavant le titre seul.
- Fermer la fenêtre de téléchargement (ou arrêter) après un téléchargement terminé ne supprime plus les fichiers de la dernière vidéo : les sous-titres séparés, miniatures et fichiers définitifs étaient effacés par le nettoyage des fichiers partiels. Ce nettoyage n'a désormais lieu que si yt-dlp tournait encore, et la liste est vidée dès qu'une vidéo se termine sans erreur.
- Nettoyage à l'arrêt ou au saut : le sous-titre que yt-dlp venait d'annoncer (« Writing video subtitles to ») est suivi dès l'annonce ; il restait sur le disque quand l'arrêt tombait entre l'annonce et le début du téléchargement.
- Sauter ou arrêter une vidéo ne supprime plus les fichiers des autres vidéos du dossier : les recherches de repli du nettoyage (par suffixe comme `.fr.srt` ou `.E02.mkv`, et les `*.part` / `*.ytdl` du dossier) ne touchent désormais que les fichiers écrits depuis le début de la vidéo interrompue.
- Réglages : un dossier ou un navigateur mémorisé n'écrase plus les autres réglages quand le fichier de configuration est momentanément verrouillé (antivirus) : la lecture est réessayée et, si elle échoue, rien n'est écrit.
- Sauter ou arrêter une vidéo en cours supprime tout ce qui la concerne, y compris le fichier déjà fusionné (MKV avec ses pistes audio) ou converti ; seuls les sous-titres étaient supprimés quand l'arrêt tombait après la fusion.
- Dossiers et navigateurs mémorisés tout de suite (fenêtre principale et inspecteur de playlist), plus seulement à la fermeture : un arrêt brutal ou un redémarrage ne les fait plus perdre. L'inspecteur retrouve son dernier dossier de destination, sinon celui de la fenêtre principale.
- Avertissement sur les cookies (session YouTube renouvelée) reformulé : le téléchargement continue, mais s'il se répète les pistes audio secondaires et les sous-titres peuvent être ignorés automatiquement ; reconnexion (ou redémarrage du navigateur) conseillée.
- Antivirus : les téléchargements lancent yt-dlp avec une ligne de commande courte (`--config-locations` vers un fichier temporaire du dossier de données, supprimé ensuite) au lieu d'un long sélecteur de format sur la ligne de commande. Un antivirus de comportement (RAV : « Suspicious.Argument ») bloquait certaines combinaisons de plusieurs pistes audio à cause de ses arguments. Les options transmises à yt-dlp sont strictement les mêmes (accents, barres obliques inverses et crochets vérifiés).
- Cookies Edge, Chrome, Brave et Opera : quand la base de cookies est verrouillée, le logiciel indique si le navigateur est encore en cours d'exécution, y compris en arrière-plan alors que sa fenêtre est fermée (nombre de processus), et explique comment le terminer (Gestionnaire des tâches, réglage « Continuer à exécuter des applications en arrière-plan »).

## [0.1.4] — 2026-10-18

### Corrigé
- Pistes audio multiples (MKV) : yt-dlp reçoit `--embed-metadata`, ce qui étiquette chaque piste avec sa langue (`fra`, `eng`…) au lieu de « Piste 1 », « Piste 2 ». Appliqué à la fenêtre principale, à l'inspecteur de playlist, à la file d'attente et au bloc « Multi-pistes audio (MKV) ».
- Sous-titres intégrés (« Intégrer ST ») : avec `--write-auto-subs`, yt-dlp n'ajoute plus `--write-subs` de lui-même quand on demande `--embed-subs`. Les sous-titres rédigés par l'auteur étaient donc ignorés (« There are no subtitles for the requested languages ») sur les vidéos qui en ont. Le logiciel demande maintenant les deux types et supprime les fichiers `.srt` après intégration (fenêtre principale et inspecteur de playlist).

## [0.1.3] — 2026-10-17

### Ajouté
- Désinstallation : le désinstalleur propose de supprimer aussi les données du logiciel (réglages, file d'attente, yt-dlp et ffmpeg téléchargés, dossier `%LOCALAPPDATA%\yt-dlp-GUI`), « Non » par défaut ; les vidéos téléchargées ne sont jamais supprimées. En mode silencieux, les données sont conservées sauf avec `/DELETEDATA=1`. Message traduit dans les 14 langues de l'installateur.
- Installateur et désinstalleur : le logiciel en cours d'exécution est détecté (mutex nommé) et l'utilisateur est invité à le fermer ; nom affiché explicite dans « Applications installées ».
- README (15 langues) : puce « Désinstallation » (chemin dans Windows, installation propre à chaque compte, version portable, outils Chocolatey conservés) et note sur les pistes audio du MKV sans nom de langue.

### Modifié
- Cookies : note sous le menu des navigateurs (Chrome, Edge et Brave : lecture souvent impossible même fermés ; Opera : détection seulement navigateur fermé) et résultats d'essais dans les README ; Firefox est recommandé.

## [0.1.2] — 2026-10-17

### Corrigé
- Deno installé par Chocolatey depuis un autre compte administrateur (dossier `lib\deno`, absent du PATH de l'utilisateur courant) restait signalé « absent ». Le logiciel cherche désormais aussi dans le dossier du paquet Chocolatey et dans les emplacements usuels (`.deno`, WinGet, Scoop, Program Files), et ajoute le dossier trouvé à son PATH pour que yt-dlp utilise Deno.

## [0.1.1] — 2026-10-17

### Ajouté
- Installateur : 14 langues au lieu de 10 (ajout du chinois simplifié, du vietnamien, du serbe latin et du hindi). Une page d'accueil indique en filipino que le logiciel est disponible en filipino : Inno Setup n'a aucune traduction pour cette langue.
- README : une version Linux est annoncée à moyen terme (français et anglais).

### Corrigé
- Cookies : la fenêtre principale reçoit le même cadre que l'inspecteur (voyant d'état et bouton de test). Quand Chrome, Edge ou Brave verrouille sa base de cookies (« Could not copy Chrome cookie database »), le logiciel explique quoi faire (fermer complètement le navigateur, ou utiliser Firefox) dans le test, l'inspection, les téléchargements et l'analyse de playlist. Firefox est désormais recommandé dans les avertissements, les messages d'aide et les README, qui expliquent aussi qu'aucun navigateur ne peut fournir de cookies s'il est réglé pour les supprimer à la fermeture (piège particulier de Chrome, Edge et Brave, qu'il faut fermer pour lire leurs cookies).
- Outils installés après le lancement du logiciel (Deno, ffmpeg…) : le PATH est relu depuis le registre, donc ils ne sont plus signalés « absents » et sont trouvés par yt-dlp.
- La fenêtre principale s'ouvre à une taille confortable (980 x 930, adaptée à l'écran) au lieu de la taille minimale, et retient la taille choisie.

## [0.1.0] — 2026-10-16

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
- Publication automatique : l'étiquette `vX.Y.Z` déclenche un workflow GitHub qui lance les tests, construit l'installateur et la version portable, calcule les sommes SHA-256 et crée la release avec les notes du CHANGELOG.
- Notification de mise à jour : vérification quotidienne (désactivable) de la dernière release GitHub, bandeau discret, fenêtre « Rechercher une mise à jour du logiciel… » avec les nouveautés et le téléchargement adapté à l'installation ; rien n'est installé automatiquement.
- Interrupteur « Vérifier les mises à jour au démarrage » dans le menu des options. Licence : l'icône, le logo et la bannière sont précisés comme créations originales générées par IA, hors licence MIT.
- Documentation : section « Installation » (installateur, version portable, avertissement SmartScreen et vérification SHA-256) et captures d'écran, dans les 15 langues.
