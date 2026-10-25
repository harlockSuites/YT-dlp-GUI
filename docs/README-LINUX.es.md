# yt-dlp GUI — versión para Linux

[Français](../README-LINUX.md) · [English](README-LINUX.en.md) · [Español](README-LINUX.es.md) · [Português](README-LINUX.pt.md) · [Italiano](README-LINUX.it.md) · [Polski](README-LINUX.pl.md) · [Magyar](README-LINUX.hu.md) · [Srpski](README-LINUX.sr.md) · [Русский](README-LINUX.ru.md) · [Tiếng Việt](README-LINUX.vi.md) · [中文](README-LINUX.zh.md) · [हिन्दी](README-LINUX.hi.md) · [日本語](README-LINUX.ja.md) · [한국어](README-LINUX.ko.md) · [Filipino](README-LINUX.fil.md)

> **Versión preliminar.** Este documento complementa el [README principal](README.es.md): es el mismo programa, pero aquí solo se trata lo propio de Linux (instalación, cookies y llaveros, archivos, solución de problemas). Las novedades de cada versión están en [CHANGELOG-linux.md](../CHANGELOG-linux.md). Las traducciones aún deben revisarlas hablantes nativos; en caso de duda, prevalecen los textos en francés e inglés.

## Contenido

1. [Estado de la versión preliminar](#s1)
2. [Instalar](#s2)
3. [Primer inicio y dependencias](#s3)
4. [Cookies del navegador](#s4)
5. [Llaveros: operaciones manuales](#s5)
6. [Dónde están los archivos](#s6)
7. [Solución de problemas](#s7)
8. [Informar de un error](#s8)
9. [Para desarrolladores](#s9)

<a id="s1"></a>

## 1. Estado de la versión preliminar

La versión para Linux reproduce el comportamiento de la versión de Windows 0.1.8 (congelada, usada como modelo). Se publica como **versión preliminar de GitHub** con etiquetas `Linux-vX.Y.Z`: nunca se presenta como la «última versión» del repositorio.

**Lo que se ha probado** (máquina virtual Debian 12, escritorio GNOME, Python 3.11, una cuenta real de YouTube con sesión iniciada en cada navegador, octubre de 2026):

- **Cookies de Firefox, Waterfox, Floorp y Zen Browser**: leídas con el navegador abierto o cerrado.
- **Cookies de Google Chrome, Chromium, Brave, Vivaldi, Opera y Microsoft Edge**: leídas con el navegador **cerrado**, tras abrir cada navegador una vez e iniciar sesión en YouTube (véase la [sección 5](#s5)). La descarga individual y el Inspector de listas de reproducción funcionaron.
- **LibreWolf**: solo se leen mientras está abierto y con la sesión iniciada (por defecto borra sus cookies al cerrarse).
- **Vídeo privado** con las cookies de Firefox, y una lista de tres vídeos con uno privado.
- **Paquetes**: el AppImage y el archivo comprimido `.tar.gz` los construye la CI en Ubuntu 22.04; el `.deb` se construyó, instaló, abrió y quitó en Debian 12; el AppImage, el archivo comprimido y el `.deb` se abrieron en la máquina virtual, y «Instalar en el menú» / «Desinstalar» se probaron con el ratón usando el AppImage (icono añadido y luego quitado del menú y del Escritorio).
- **Idioma y fuente**: coreano elegido en una máquina sin fuente coreana; la ventana «Font needed» ofrece la fuente, se descarga y se verifica, el programa se reinicia y el texto es legible.

**Lo que aún no se ha probado**:

- otras distribuciones (Ubuntu, Fedora, Arch, openSUSE…) y escritorios distintos de GNOME, incluido KDE Plasma (KWallet);
- navegadores instalados como Flatpak o Snap (salvo la estructura de LibreWolf en Flatpak, que se observó);
- Vivaldi, Opera o Edge **sin** Chrome ni Chromium instalados (véase la [sección 5](#s5));
- la arquitectura aarch64 (el programa la admite, pero los paquetes solo se construyen para x86_64);
- un ordenador Linux real, fuera de una máquina virtual (escritorio y hardware reales);
- las traducciones: aún deben revisarlas hablantes nativos.

<a id="s2"></a>

## 2. Instalar

### Qué formato elegir

| Formato | Para quién | Derechos de administrador | Entrada en el menú |
|---|---|---|---|
| **AppImage** | cualquier distribución reciente de 64 bits | no | «Instalar en el menú» (sección 2.3) |
| **Archivo comprimido `.tar.gz`** | igual, sin AppImage ni FUSE | no | «Instalar en el menú» |
| **Paquete `.deb`** | Debian, Ubuntu y derivadas | sí (`sudo`) | automática |
| **Código fuente** | desarrolladores, pruebas | no | ninguna |

Requisitos: Linux de 64 bits (x86_64) de una distribución de 2022 o más reciente (glibc 2.35 o superior), porque los paquetes se construyen en Ubuntu 22.04.

**Si empieza con Linux**: solo el paquete `.deb` se instala «de verdad» y aparece en el gestor de programas. El AppImage y el archivo comprimido son archivos o carpetas normales, guardados donde quiera: para quitarlos basta con borrarlos como cualquier otro archivo (secciones 2.2 y 2.5). Sus ajustes se guardan aparte, en `~/.local/share/yt-dlp-GUI` (sección 6), y sobreviven a ese borrado.

Los archivos están en la [página de versiones publicadas](https://github.com/harlockSuites/YT-dlp-GUI/releases): busque las etiquetas `Linux-v…`, marcadas como «Pre-release».

### 2.1 Verificar la descarga

Descargue también `SHA256SUMS-linux.txt` en la misma carpeta y después:

```bash
sha256sum -c SHA256SUMS-linux.txt --ignore-missing
```

Cada archivo presente debe mostrar `OK`. Esto demuestra que su archivo es idéntico al publicado, no que sea inofensivo: el código fuente y la construcción automática son públicos.

### 2.2 AppImage

```bash
chmod +x yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

El AppImage necesita la biblioteca FUSE 2:

| Distribución | Paquete |
|---|---|
| Debian, Ubuntu 22.04 y derivadas | `libfuse2` |
| Ubuntu 24.04 y posteriores | `libfuse2t64` |
| Fedora | `fuse-libs` |

Sin FUSE, ejecútelo igualmente: se extrae solo en una carpeta temporal:

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage --appimage-extract-and-run
```

El AppImage no se «instala»: no aparece en el gestor de programas. Para quitarlo, borre el archivo:

```bash
rm yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

Para encontrar el AppImage en el menú de aplicaciones, con su icono, use la función **«Instalar en el menú…» del programa** (sección 2.3): no hay ningún comando que escribir.

### 2.3 Instalar en el menú (sin administrador)

Un AppImage abierto con doble clic no deja ningún icono en el menú de aplicaciones. En el programa: menú de opciones › **«Instalar en el menú…»**. La ventana:

- copia el programa en `~/.local/share/yt-dlp-GUI/app/`;
- escribe el lanzador `~/.local/share/applications/yt-dlp-gui.desktop` y el icono `~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png`;
- añade, si la casilla está marcada, un acceso directo en el Escritorio (marcado como «de confianza» para GNOME cuando existe la herramienta `gio`);
- después ofrece «Actualizar» (copia de nuevo la versión que se está ejecutando) y «Desinstalar».

«Desinstalar» solo quita lo que creó la instalación y **conserva sus ajustes** y las herramientas descargadas. Un lanzador sin nuestra marca interna (`X-YtDlpGui-Installer=1`) nunca se borra.

Límites: la ventana está disponible desde el AppImage y el archivo comprimido. Desde el código fuente le remite al AppImage; desde el paquete `.deb` explica que el programa ya está en el menú.

Mientras el programa no esté en el menú, el AppImage y el archivo comprimido ofrecen por sí mismos esta instalación al arrancar, en una ventana «¿Instalar en el menú?»: «Sí, instalar…» abre la ventana anterior, «Más tarde» volverá a preguntar en el próximo arranque y «No volver a preguntar» detiene las invitaciones (la función sigue en el menú de opciones).

Si el acceso directo del Escritorio muestra una advertencia: clic derecho en el icono › «Permitir lanzar». Algunos escritorios (GNOME por defecto) no muestran iconos en el Escritorio: el lanzador del menú funciona en todos los casos.

Para quitarlo todo a mano:

```bash
rm -rf ~/.local/share/yt-dlp-GUI/app ~/.local/share/applications/yt-dlp-gui.desktop ~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png ~/Desktop/yt-dlp-gui.desktop
```

Si el paquete `.deb` ya está instalado, no use esta función: el programa ya está en el menú y aparecería una segunda entrada «yt-dlp GUI» (quite antes el `.deb` con `sudo apt remove yt-dlp-gui` si prefiere este método).

### 2.4 Paquete `.deb`

```bash
sudo apt install ./yt-dlp-gui_X.Y.Z_amd64.deb
```

El programa va a `/opt/yt-dlp-gui`, con el enlace `/usr/bin/yt-dlp-gui`, el lanzador del menú, el icono y la licencia (`/usr/share/doc/yt-dlp-gui/`). Depende de `libc6 (>= 2.35)` y de `libx11-6`.

Para quitarlo (sus ajustes, en `~/.local/share/yt-dlp-GUI`, nunca se tocan):

```bash
sudo apt remove yt-dlp-gui
```

### 2.5 Archivo comprimido `.tar.gz`

```bash
tar xzf yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz
```

```bash
./yt-dlp-gui/yt-dlp-gui
```

Para que los ajustes y las herramientas queden **dentro de la carpeta extraída** (memoria USB, prueba sin dejar rastro), cree un archivo vacío `portable.flag` junto al ejecutable:

```bash
touch yt-dlp-gui/portable.flag
```

Sin este archivo, los datos van a `~/.local/share/yt-dlp-GUI` (sección 6).

El archivo comprimido no se «instala»: no aparece en el gestor de programas. Para quitarlo, borre la carpeta extraída:

```bash
rm -rf yt-dlp-gui
```

### 2.6 Desde el código fuente

```bash
python3 yt-dlp-gui.pyw
```

Desde el código fuente, los ajustes y las herramientas descargadas van a la misma carpeta que en las versiones instaladas (`~/.local/share/yt-dlp-GUI`): volver a descargar el código o borrar su carpeta no los borra. Para mantener los datos dentro de la carpeta del código (prueba sin dejar rastro), cree un archivo vacío `portable.flag` junto a `yt-dlp-gui.pyw`.

Hace falta Python 3 con Tkinter:

| Distribución | Paquete |
|---|---|
| Debian, Ubuntu y derivadas, openSUSE | `python3-tk` |
| Fedora | `python3-tkinter` |
| Arch | `tk` |

### 2.7 Actualizaciones

Una comprobación diaria (que se puede desactivar en el menú de opciones) busca las versiones `Linux-vX.Y.Z`, incluidas las preliminares, y **nunca** propone una versión de Windows. Abre la página de descarga del archivo que corresponde a su instalación (AppImage, archivo comprimido o `.deb`); **no se instala nada automáticamente**. Para actualizar:

- **AppImage o archivo comprimido instalado en el menú**: descargue el nuevo AppImage, ejecútelo y luego «Instalar en el menú… › Actualizar»;
- **`.deb`**: `sudo apt install ./new-file.deb`;
- **archivo comprimido no instalado**: extraiga el nuevo archivo comprimido en lugar del anterior.

### 2.8 Quitarlo todo, datos incluidos

Tras quitar el programa (secciones 2.3 a 2.5), para borrar además sus ajustes, la cola y las herramientas descargadas (yt-dlp, ffmpeg, deno):

```bash
rm -rf ~/.local/share/yt-dlp-GUI
```

Sus vídeos descargados nunca están en esta carpeta.

<a id="s3"></a>

## 3. Primer inicio y dependencias

En el primer inicio, el asistente de instalación propone descargar **yt-dlp** (`yt-dlp_linux`), **ffmpeg** (el archivo comprimido `.tar.xz` de las compilaciones oficiales de yt-dlp) y **deno** desde sus repositorios de GitHub. Se verifican las sumas SHA-256, no se piden derechos de administrador, y los archivos van a `~/.local/share/yt-dlp-GUI` (yt-dlp) y a `~/.local/share/yt-dlp-GUI/bin` (ffmpeg, ffprobe, deno). Sigue disponible en el menú de opciones.

Solo ffmpeg y ffprobe son imprescindibles; deno es recomendable (pistas de audio secundarias). **AtomicParsley, MKVToolNix y aria2** son opcionales: la ventana «Dependencias» muestra el comando de su gestor de paquetes, para copiarlo en un terminal. El programa nunca lo ejecuta por sí mismo. Los mismos comandos:

| Gestor de paquetes | Comando |
|---|---|
| apt | `sudo apt install aria2 atomicparsley mkvtoolnix` |
| dnf | `sudo dnf install AtomicParsley aria2 mkvtoolnix` |
| pacman | `sudo pacman -S aria2 atomicparsley mkvtoolnix-cli` |
| zypper | `sudo zypper install AtomicParsley aria2 mkvtoolnix` |

<a id="s4"></a>

## 4. Cookies del navegador

yt-dlp lee las cookies **en local**, en el navegador que elija (pistas de audio secundarias, subtítulos, vídeos privados, contenido para miembros). Por defecto, el programa propone los cinco navegadores más usados en Linux (Firefox, Google Chrome, Chromium, Brave, Vivaldi). La entrada **«Navegadores para cookies…»** del menú de opciones abre la ventana «Navegadores para cookies», que ofrece 11: marque los que necesite; una ✔ señala los que tienen su carpeta de perfil en su ordenador.

| Navegador | Lo lee yt-dlp como | Llavero | Carpetas de perfil buscadas |
|---|---|---|---|
| Firefox | `firefox` | no | `~/.config/mozilla/firefox`, `~/.mozilla/firefox`, Flatpak, Snap |
| Google Chrome | `chrome` | sí | `~/.config/google-chrome` |
| Chromium | `chromium` | sí | `~/.config/chromium` |
| Brave | `brave` | sí | `~/.config/BraveSoftware/Brave-Browser` |
| Vivaldi | `vivaldi` | sí | `~/.config/vivaldi` |
| Opera | `opera` | sí | `~/.config/opera` |
| Microsoft Edge | `edge` | sí | `~/.config/microsoft-edge` |
| LibreWolf, Waterfox, Floorp, Zen Browser | `firefox:` + carpeta del perfil | no | `~/.librewolf`, `~/.config/librewolf`… (igual para los demás), Flatpak incluido |

Los derivados de Firefox no tienen un nombre que yt-dlp conozca: el programa busca su base `cookies.sqlite` (hasta tres niveles bajo sus carpetas) y entrega a yt-dlp la carpeta del perfil usado más recientemente. Se respeta `XDG_CONFIG_HOME` cuando es absoluta.

El **indicador** junto a la lista muestra el estado: rojo (desactivado o con error), naranja (sin probar o en curso), verde (cookies leídas). El botón ↻ lanza una prueba; la información emergente explica el error. Una prueba que lee **0 cookies** nunca es verde.

### Casos frecuentes

| Lo que ve | Causa probable | Qué hacer |
|---|---|---|
| «Extracted 0 cookies» y luego «Sign in to confirm you're not a bot» | el navegador no guarda ninguna cookie en el disco (LibreWolf las borra al cerrarse por defecto; perfil sin sesión iniciada; modo privado) | dejarlo abierto y con la sesión de YouTube iniciada, o desactivar el borrado de cookies al cerrar en sus ajustes de privacidad |
| «Item does not exist!» con Chrome, Chromium, Brave, Vivaldi, Opera o Edge | yt-dlp no encontró la clave del navegador en el llavero del escritorio | abrir el navegador una vez, iniciar sesión en YouTube, cerrarlo y repetir la prueba; si no, [sección 5](#s5) |
| «Could not copy Chrome cookie database» o «database is locked» | el navegador bloquea su base de datos mientras se ejecuta | cerrarlo y repetir la prueba |
| «Failed to decrypt» | cookies cifradas con una clave que yt-dlp no obtuvo | [sección 5](#s5) |

### Probar un navegador desde un terminal

Es la mejor forma de ver el error exacto (sustituya `IDENTIFIER` por el identificador de cualquier vídeo de YouTube):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Líneas que hay que buscar: `Extracted N cookies from chromium` (N debe ser mayor que 0), `Chosen keyring: GNOMEKEYRING` (el llavero elegido) y `cookie version breakdown: {'v10': 0, 'v11': 50, …}` (las cookies `v11` necesitan el llavero, las `v10` no).

Para un derivado de Firefox, indique la carpeta del perfil. Para encontrarla:

```bash
find ~ -name cookies.sqlite -path "*librewolf*" 2>/dev/null
```

En una instalación Flatpak, busque en `~/.var/app`:

```bash
find ~/.var/app -name cookies.sqlite 2>/dev/null
```

Después, con la carpeta que contiene `cookies.sqlite`:

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser "firefox:/path/to/profile" -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

<a id="s5"></a>

## 5. Llaveros: operaciones manuales

### Para qué sirve

Los navegadores de la familia Chromium (Chrome, Chromium, Brave, Vivaldi, Opera, Edge) cifran sus cookies. La clave de cifrado se guarda en el **llavero del escritorio**: GNOME Keyring (o un equivalente compatible, mediante el «Secret Service») en GNOME, XFCE, Cinnamon, MATE…, KWallet en KDE. Para descifrar, yt-dlp pide esa clave al llavero. Firefox y sus derivados no lo necesitan.

Dos datos útiles:

- **La clave solo existe después de abrir el navegador por primera vez.** En nuestra máquina virtual, el error «Item does not exist!» desapareció cuando cada navegador se abrió una vez y se inició sesión en YouTube. La causa exacta del primer fallo no se llegó a establecer con certeza: el llavero existía, era el predeterminado y estaba desbloqueado.
- **Qué llavero usa yt-dlp** depende del escritorio detectado (variables `XDG_CURRENT_DESKTOP` y `DESKTOP_SESSION`), según el código de yt-dlp (octubre de 2026):

| Escritorio detectado | Llavero que usa yt-dlp |
|---|---|
| GNOME, Cinnamon, MATE, XFCE, Pantheon, Unity, Deepin, UKUI | GNOME Keyring (`GNOMEKEYRING`) |
| KDE 4, 5, 6 | KWallet (`KWALLET`, `KWALLET5`, `KWALLET6`) |
| LXQt, KDE 3, escritorio no reconocido (gestores de ventanas solos: sway, i3…) | ninguno: texto simple (`BASICTEXT`) |

En el último caso, yt-dlp solo lee cookies `v10`: si su navegador guarda su clave en GNOME Keyring, sus cookies `v11` no se descifrarán. Entonces hay que imponer el llavero desde un terminal (sección 5.6); el programa todavía no ofrece este ajuste.

Los elementos que se buscan en el llavero se llaman «*nombre* Safe Storage». Según el código de yt-dlp, es **«Chrome Safe Storage»** para Chrome y Vivaldi, **«Chromium Safe Storage»** para Chromium, Opera y Edge, **«Brave Safe Storage»** para Brave. En nuestra máquina virtual, Chrome y Chromium también estaban instalados y se habían abierto: no sabemos si Vivaldi, Opera o Edge funcionarían solos.

### 5.1 ¿Existe el llavero?

```bash
ls -la ~/.local/share/keyrings/
```

Debe ver un archivo `login.keyring` (el llavero «login»). A continuación, ¿cuál es el llavero **predeterminado**?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets --method org.freedesktop.Secret.Service.ReadAlias default
```

Respuesta `(objectpath '/org/freedesktop/secrets/collection/login',)`: hay un llavero predeterminado. Respuesta `'/'`: **ninguno**, pase a la sección 5.4.

### 5.2 ¿Está bloqueado?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Locked
```

`(<false>,)`: desbloqueado. `(<true>,)`: bloqueado; ábralo con Seahorse (sección 5.4), que le pedirá su contraseña.

### 5.3 ¿Está en él la clave de mi navegador?

Liste los elementos:

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Items
```

La respuesta da rutas que terminan en un número (`…/login/1`, `…/login/2`…). Para leer el nombre de cada una (adapte la lista de números):

```bash
for i in 1 2 3 4 5 6; do gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login/$i --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Item Label; done
```

Debería ver, por ejemplo, `Chromium Safe Storage`, `Chrome Safe Storage` o `Brave Safe Storage`. Los nombres vacíos son inofensivos. Si falta el nombre de su navegador: ábralo una vez, inicie sesión en YouTube, ciérrelo y vuelva a lanzar este comando.

### 5.4 Crear o desbloquear un llavero con Seahorse

Instale Seahorse («Contraseñas y claves») y las herramientas asociadas. El comando exacto también está en la ventana «Navegadores para cookies» del programa:

| Gestor de paquetes | Comando |
|---|---|
| apt | `sudo apt install gnome-keyring seahorse libsecret-tools` |
| dnf | `sudo dnf install gnome-keyring seahorse libsecret` |
| pacman | `sudo pacman -S gnome-keyring seahorse libsecret` |
| zypper | `sudo zypper install gnome-keyring seahorse libsecret-tools` |

Después ábralo:

```bash
seahorse
```

- **Sin llavero predeterminado**: cree uno (botón «+» o menú Archivo › Nuevo › llavero de contraseñas), llámelo «Login» y haga clic derecho sobre él › «Establecer como predeterminado». Los nombres exactos varían según la versión de Seahorse.
- **Llavero bloqueado**: doble clic o clic derecho › «Desbloquear» y escriba su contraseña (escríbala usted; el programa nunca la pide).
- **Inicio de sesión automático**: un llavero protegido con contraseña no puede abrirse solo si no escribe ninguna contraseña al iniciar la sesión; seguirá bloqueado hasta que lo desbloquee (o hasta que use la misma contraseña para la sesión y para el llavero).

Después **abra el navegador, inicie sesión en YouTube, ciérrelo** y repita la prueba (sección 4).

### 5.5 KDE Plasma (KWallet)

En KDE, yt-dlp consulta KWallet (`kwallet-query`). El gestor se llama `kwalletmanager` (o `kwalletmanager5`) según la distribución. Esta configuración **no se ha probado** en nuestras pruebas.

### 5.6 Imponer el llavero a yt-dlp (terminal)

El programa deja que yt-dlp elija el llavero según el escritorio. Para forzarlo, añada `+LLAVERO` al nombre del navegador (valores: `gnomekeyring`, `kwallet`, `kwallet5`, `kwallet6`, `basictext`):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium+gnomekeyring -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Para saber qué llavero usa realmente un Chromium (comando tomado del código de yt-dlp, no probado aquí):

```bash
chromium --enable-logging=stderr --v=1 2>&1 | grep key_storage_
```

### 5.7 Sin llavero: `--password-store=basic` (avanzado, no probado)

Chromium acepta `--password-store=basic`: entonces guarda su clave en claro (una clave fija y conocida) y cifra sus cookies nuevas como `v10`, que yt-dlp lee sin llavero (`chromium+basictext`). **Es menos seguro**: cualquier programa que pueda leer sus archivos puede descifrar esas cookies. Úselo solo si entiende este compromiso; las cookies ya guardadas probablemente no se vuelven a codificar: inicie sesión de nuevo.

### 5.8 Último recurso

Si un llavero está dañado, **haga primero una copia de seguridad**:

```bash
cp -a ~/.local/share/keyrings ~/keyrings-backup
```

Borrar `login.keyring` elimina **todas** las contraseñas que contiene (Wi-Fi, cuentas en línea…): no lo haga sin entender las consecuencias.

<a id="s6"></a>

## 6. Dónde están los archivos

La carpeta de datos es `$XDG_DATA_HOME/yt-dlp-GUI` (por defecto `~/.local/share/yt-dlp-GUI`), salvo que `portable.flag` esté junto al ejecutable del archivo (o del script `yt-dlp-gui.pyw`).

| Archivo o carpeta | Contenido |
|---|---|
| `gui-config.json` | ajustes (idioma, navegador, carpetas, selección de navegadores…) |
| `download-queue.json` | cola de descargas |
| `custom-blocks.json` | bloques de opciones personalizados |
| `yt-dlp` | ejecutable descargado por el asistente |
| `bin/` | ffmpeg, ffprobe, deno |
| `cmd/` | archivos de configuración temporales de yt-dlp |
| `app/` | copia del programa hecha por «Instalar en el menú» |
| `~/.local/share/fonts/yt-dlp-GUI/` (fuera de la carpeta de datos) | fuente Noto descargada para el coreano, el japonés o el chino; para quitarla: `rm -rf ~/.local/share/fonts/yt-dlp-GUI` |

<a id="s7"></a>

## 7. Solución de problemas

| Problema | Pista |
|---|---|
| El AppImage no arranca | ejecutarlo desde un terminal para leer el error; instalar FUSE 2 (sección 2.2) o añadir `--appimage-extract-and-run` |
| No se muestra nada, o error de biblioteca | comprobar la versión de glibc: `ldd --version` debe indicar 2.35 o superior |
| No hay icono en el Escritorio | GNOME no muestra ninguno por defecto; use el menú de aplicaciones |
| Acceso directo del Escritorio con una advertencia | clic derecho › «Permitir lanzar» |
| El arrastrar y soltar entre el anfitrión y una máquina virtual no funciona | es una función de VirtualBox (Guest Additions), no del programa |
| La interfaz tiene un tamaño incorrecto | el programa sigue las fuentes del sistema (Tk); pruebe otro tamaño de fuente del sistema |
| Falla la actualización de yt-dlp | use «Actualización y Diagnóstico» en el menú de opciones; si no, descargue `yt-dlp_linux` y elíjalo en la ventana de sustitución (el archivo elegido se vuelve ejecutable) |
| Cuadrados en lugar del texto (coreano, chino, japonés…) | ninguna fuente del sistema contiene esos caracteres; en Debian y Ubuntu: `sudo apt install fonts-noto-cjk` (~90 MB), y después cerrar y volver a abrir el programa; en otras distribuciones, instalar el paquete «Noto Sans CJK» de la distribución; el programa también puede descargar la fuente por sí mismo (coreano, japonés, chino) al elegir el idioma, sin derechos de administrador |

<a id="s8"></a>

## 8. Informar de un error

El botón «Informar de un error» prepara un informe técnico en el que se ocultan sus carpetas, su nombre de usuario y sus direcciones de correo; no se envía nada automáticamente. Para Linux, añada:

```bash
cat /etc/os-release
```

```bash
echo "$XDG_CURRENT_DESKTOP $XDG_SESSION_TYPE"
```

e indique **cómo** instaló el programa (AppImage, archivo comprimido, `.deb`, código fuente) y, si el problema son las cookies, **el resultado de la prueba en el terminal** (sección 4), sin pegar sus cookies.

<a id="s9"></a>

## 9. Para desarrolladores

Pruebas (con una pantalla virtual, sin necesidad de pantalla real):

```bash
xvfb-run -a python3 -X utf8 -m unittest discover -s tests -t .
```

Construir los paquetes (herramientas de construcción: `pip install -r packaging/requirements-build.txt`, más `appimagetool`, cuya ruta se indica con la variable `APPIMAGETOOL`):

```bash
python3 packaging/build_linux.py
```

```bash
python3 packaging/build_deb.py
```

Los resultados están en `dist/`. Para la mejor compatibilidad, construya en la distribución más antigua admitida (la glibc de la máquina de construcción es el mínimo exigido a las máquinas que ejecutan el programa). Comprobaciones útiles del `.deb`:

```bash
lintian dist/yt-dlp-gui_*_amd64.deb
```

El único error de forma conocido es `dir-or-file-in-opt` (programa incluido en `/opt`).

**Publicar**: comprobar `__version__` en `yt-dlp-gui.pyw`, fechar la sección de la versión en `CHANGELOG-linux.md`, hacer el commit y después crear y subir la etiqueta `Linux-vX.Y.Z`. El flujo «Release Linux» ejecuta las pruebas, construye el AppImage, el archivo comprimido y el `.deb`, calcula las sumas y crea la versión como **versión preliminar**, nunca como «última versión» (la comprobación de actualizaciones de la versión de Windows 0.1.8 no debe encontrar ahí ninguna etiqueta de Linux).

Licencia: MIT, como el resto del repositorio (véase [LICENSE](../LICENSE)).
