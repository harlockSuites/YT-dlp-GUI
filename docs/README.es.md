# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

Interfaz gráfica para [yt-dlp](https://github.com/yt-dlp/yt-dlp), pensada para que sea accesible a todos y aproveche al máximo sus capacidades.

> **Proyecto en desarrollo.** Algunas funciones pueden cambiar, estar incompletas o contener errores.

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## Funciones

### Descargador individual y cola

- **Opciones**: calidad máxima (hasta 4K), solo audio (MP3), subtítulos (formatos vtt, srt, ass), incrustación de subtítulos y miniatura, idioma de audio principal, pistas de audio secundarias (archivo MKV multipista) y una biblioteca de «bloques de script» (posprocesado, exportación, red, comportamiento) que puede ampliar con sus propios bloques.
- **Varias pistas de audio**: en el archivo MKV, cada pista de audio lleva la etiqueta de su idioma («spa», «eng»…); su reproductor la muestra en el menú de audio.
- **Comando generado**: el comando de yt-dlp correspondiente a sus elecciones se muestra en directo.
- **Cola**: añada la URL actual y luego ejecute toda la cola, desde un elemento, un solo vídeo o un intervalo; pausa y reanudación, omitir el elemento en curso, detener con limpieza de los archivos parciales. La cola se conserva entre sesiones.
- **Nombres de archivo existentes**: un vídeo individual cuyo nombre ya existe en la carpeta de destino recibe un sufijo (`_2`, `_3`…) para no sobrescribir nada. Una lista de reproducción descargada desde este descargador no se renumera: los vídeos que ya están en la carpeta se omiten («has already been downloaded»).

### Inspector de listas de reproducción

- **Análisis** de una lista de reproducción: cada vídeo aparece con sus pistas de audio y subtítulos disponibles; los elementos ocultos, privados o eliminados se ignoran sin bloquear el resto.
- **Reglas globales** (calidad, solo audio, formato e incrustación de subtítulos, miniatura, numeración, idiomas, bloques de script, carpeta de salida) con **excepciones por vídeo** para el idioma principal, las pistas secundarias y los subtítulos.
- **Código de colores**: rojo cuando falta el idioma principal, naranja cuando falta una pista secundaria o un subtítulo.
- **Descarga de la selección** con registro, pausa, reanudación y omisión; si las pistas solicitadas no existen, el vídeo se reintenta sin ellas y después un **resumen** indica qué se logró, qué se ajustó o qué falló.

### Directorio inteligente y registro

- **Directorio inteligente**: yt-dlp omite los vídeos ya descargados gracias a un registro guardado en la carpeta de salida. El archivo `.yt-dlp-registre.json` contiene el identificador, la URL, el título, la duración, el nombre de archivo y la fecha de cada vídeo; `.yt-dlp-archive.txt`, leído por yt-dlp, se deriva de él.
- **Comprobación retroactiva**: si hay vídeos de la selección que ya están en la carpeta pero no figuran en el registro, una ventana propone registrarlos y omitirlos (comparando los títulos). Puede desmarcar los falsos positivos.
- **Actualizar el registro**: cuenta los vídeos de la carpeta, los del registro y los que faltan, y luego busca en YouTube la información que falta (título y duración mediante ffprobe). No se registra nada sin su confirmación, y dos botones abren el archivo local o el enlace de YouTube encontrado para que pueda comprobarlo.

![yt-dlp GUI](img/registry.en.png)

### Cookies del navegador

- Elija el navegador (Chrome, Firefox, Edge, Brave, Opera) cuyas cookies lee yt-dlp en local: son necesarias para las pistas de audio secundarias y algunos subtítulos. **Se recomienda Firefox.**
- **Resultados de nuestras pruebas** (Windows 11, octubre de 2026, cuenta de YouTube iniciada en cada navegador): **Firefox** funciona, con el navegador abierto o cerrado. **Opera** solo funciona **con el navegador cerrado**: bloquea su base de cookies mientras está abierto y yt-dlp muestra entonces «Could not copy Chrome cookie database». **Chrome, Edge y Brave** fallan incluso cerrados: cifran sus cookies de una forma que yt-dlp no siempre sabe leer. Estos límites proceden de los navegadores y de yt-dlp, no del programa, y pueden cambiar con sus actualizaciones.
- Si su navegador está configurado para **borrar las cookies al cerrarse** (o navega en modo privado), no queda ninguna cookie en el disco: yt-dlp no puede recuperar nada, ni con Chrome, Edge, Brave ni Firefox. Con Chrome, Edge y Brave es una trampa: hay que cerrar el navegador, y eso borra las cookies. Desactive esa opción o conserve las cookies de youtube.com y google.com.
- Un **indicador** muestra el estado: rojo si está desactivado o ha fallado, naranja si no se ha probado o está en curso, verde si las cookies están cargadas. El botón ↻ lanza una prueba y la información emergente explica el estado o el error.

### Asistente de instalación, dependencias y actualizaciones de yt-dlp

- **Asistente de instalación**: en el primer inicio propone descargar yt-dlp y ffmpeg desde sus repositorios oficiales de GitHub. Se verifica la suma SHA-256 y no se necesitan permisos de administrador.
- **Dependencias**: la ventana dedicada comprueba ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 y deno, y puede instalarlos con Chocolatey. Solo ffmpeg y ffprobe son imprescindibles; deno se recomienda (pistas de audio secundarias); AtomicParsley, MKVToolNix y aria2 son opcionales: el programa funciona sin ellos.
- **Actualización y diagnóstico**: actualiza yt-dlp (`yt-dlp -U`) o sustituye su ejecutable, muestra su versión y comprueba las opciones que usa la interfaz.
- **Actualización del programa**: una comprobación diaria (desactivable) avisa de una nueva versión con un banner discreto; la ventana dedicada muestra las novedades y abre la descarga que corresponde a su instalación (instalador o versión portable). No se instala nada automáticamente. Un interruptor del menú de opciones («Buscar actualizaciones al iniciar») activa o desactiva la comprobación automática, y «Buscar una actualización del programa…» la ejecuta a petición.

### Interfaz e idiomas

- Los controles se reorganizan según el ancho de la ventana; el contenido se desplaza en vertical y la tabla del inspector también en horizontal.
- Interfaz en **15 idiomas**: francés, inglés, español, portugués, italiano, polaco, húngaro, serbio, ruso, vietnamita, chino, hindi, japonés, coreano y filipino. El cambio de idioma se aplica al reiniciar, con la posibilidad de reiniciar de inmediato.

### Informar de un error

- El botón «Informar de un error» prepara un informe técnico: versiones del programa, de Python, de Windows y de yt-dlp, ajustes inofensivos y las últimas líneas del registro. Se ocultan sus carpetas, su nombre de usuario y sus direcciones de correo. Enviar el informe en GitHub requiere una cuenta de GitHub gratuita.
- No se envía nada automáticamente: usted revisa y edita el informe y luego abre una página de incidencia de GitHub ya rellenada (o copia el informe).

## Instalación

- **Instalador (recomendado)**: descargue `yt-dlp-gui-setup-X.Y.Z.exe` desde la [página de versiones](https://github.com/harlockSuites/YT-dlp-GUI/releases) y ejecútelo. Windows 10 u 11 (64 bits), sin permisos de administrador; no hace falta Python.
- **Versión portable**: descargue `yt-dlp-gui-portable-X.Y.Z.zip`, descomprímalo donde quiera y ejecute `yt-dlp-gui.exe`; los ajustes se quedan en esa carpeta.
- **Desde el código fuente**: consulte las secciones «Requisitos» e «Inicio rápido» más abajo.
- **Desinstalación**: Configuración de Windows › Aplicaciones › Aplicaciones instaladas › yt-dlp GUI, o el acceso directo «Desinstalar» del menú Inicio. El programa ofrece eliminar también sus datos (ajustes, cola, yt-dlp y ffmpeg descargados); sus vídeos nunca se eliminan. Como la instalación es propia de cada cuenta de Windows, el programa solo aparece en la lista de la cuenta que lo instaló. En la versión portable, basta con eliminar su carpeta. Las herramientas instaladas aparte con Chocolatey (ffmpeg, Deno…) no se quitan.
- **Análisis antivirus (VirusTotal)**: la versión 0.1.6 se analizó el 20 de octubre de 2026. El [instalador](https://www.virustotal.com/gui/file/683b157e1072ae7c2abcff09c1f0d94ac1d36701715682798c10792359fa9bae) es señalado por 4 de 70 motores (Arctic Wolf, DeepInstinct, SecureAge, Skyhigh) con detecciones heurísticas genéricas («obfuscatedpoly»); el [archivo ZIP portable](https://www.virustotal.com/gui/file/45cfe1a79d7eb96323634ba1ac6c8247eb5a4e9e79f1519e3f70f7c92b2538c3) no es señalado por ninguno de los 66 motores (0/66) y su [lanzador](https://www.virustotal.com/gui/file/0896bf3d524774b4f53224160bf9f216ccb0922ec2b8b5ddc8495b2d2c1680f2) lo es por 2 de 71 (SecureAge, Zillya). Probablemente son falsos positivos por un programa comprimido y sin firmar. Estos resultados solo valen para esta versión. En caso de duda, compruebe la suma SHA-256.
- **Code signing policy**: se está preparando la firma digital de las próximas versiones (solicitud a la SignPath Foundation); la [política de firma de código](https://github.com/harlockSuites/YT-dlp-GUI/blob/main/docs/CODE_SIGNING_POLICY.md) describe el proceso. Las versiones hasta la 0.1.4 no están firmadas.
- **Aviso de Windows SmartScreen**: el instalador no está firmado digitalmente, por lo que Windows puede mostrar «Windows protegió su PC». Haga clic en «Más información» y luego en «Ejecutar de todas formas». Para comprobar la autenticidad del archivo, compare su suma SHA-256 con la de `SHA256SUMS.txt`, publicada con cada versión:

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

## Avisos de Windows y de los navegadores

Este programa es gratuito, lo publica una sola persona y sus archivos **todavía no están firmados digitalmente**. Un archivo nuevo, que casi nadie ha descargado, no tiene «reputación»: por eso los navegadores y Windows muestran avisos **incluso para un programa seguro**. Un aviso no demuestra que un archivo sea peligroso, y su ausencia no demuestra que sea seguro: así puede comprobarlo usted mismo.

- **Navegador** (Firefox, Chrome, Edge, Brave): la descarga puede marcarse como «poco común» o como «contiene un virus o software malicioso». Es un análisis automático de la reputación del archivo. Compruebe primero la suma de comprobación (abajo); si coincide, puede elegir la opción que permite o conserva la descarga.
- **Windows SmartScreen**: «Windows protegió su PC» → haga clic en «Más información» y luego en «Ejecutar de todas formas», **después** de comprobar la suma de comprobación.
- **Antivirus**: algunos motores muestran detecciones genéricas (véase el análisis antivirus más arriba). Para ver el análisis de su archivo, pegue su suma SHA-256 en la barra de búsqueda de [VirusTotal](https://www.virustotal.com/): si el archivo ya es conocido, obtiene el informe sin subirlo.
- **Compruebe su descarga**: descargue también `SHA256SUMS.txt` de la misma página de versión, abra PowerShell en la carpeta de los archivos y ejecute el comando siguiente: compara cada archivo con la suma publicada y muestra `OK` o `DIFFERENT`. Si un archivo es `DIFFERENT`, no lo ejecute.

```powershell
Get-Content .\SHA256SUMS.txt | ForEach-Object { $h, $n = $_ -split '\s+\*?', 2; if ((Get-FileHash $n -Algorithm SHA256).Hash -eq $h.ToUpper()) { "$n : OK" } else { "$n : DIFFERENT" } }
```

- Esta comprobación demuestra que su archivo es **idéntico** al publicado en GitHub; por sí sola no demuestra que sea inofensivo. El código fuente y la compilación automática de los archivos ([GitHub Actions](https://github.com/harlockSuites/YT-dlp-GUI/actions)) son públicos, y se está preparando una firma digital (véase la «Code signing policy»).

## Requisitos

- Windows
- [Python 3](https://www.python.org/) con Tkinter (incluido en la instalación estándar)
- `yt-dlp.exe` y, preferiblemente, [ffmpeg](https://ffmpeg.org/): el asistente de instalación los descarga en el primer inicio

## Inicio rápido

1. Descargue o clone este repositorio y vaya a su carpeta.
2. Ejecute `yt-dlp-gui.bat` (o `pythonw yt-dlp-gui.pyw`).
3. En el primer inicio, deje que el asistente instale yt-dlp y ffmpeg; sigue disponible en el menú de opciones.
4. Pegue una URL, elija sus opciones y luego descargue, añada a la cola o abra el inspector para una lista de reproducción.

## Privacidad y uso responsable

- Este software no envía ningún dato al autor ni contiene telemetría. Las conexiones de red pasan por yt-dlp (sitios de vídeo), el asistente de instalación (GitHub) y la herramienta de registro (búsqueda en YouTube). Una comprobación automática de actualizaciones también contacta con GitHub al iniciar (como máximo una vez al día); puede desactivarla desde «Buscar actualizaciones al iniciar».
- Sus cookies permanecen en su ordenador: yt-dlp las lee en local desde el navegador elegido.
- Use esta herramienta respetando los derechos de autor, las condiciones de uso de los sitios y las leyes de su país, y descargue solo lo que tenga derecho a descargar.

## Desarrollo

Las pruebas (traducciones, registro, construcción de comandos, interfaz, asistente de instalación, documentación) se ejecutan con:

```bash
python -X utf8 -m unittest discover -s tests -t .
```

También se ejecutan automáticamente en GitHub con cada envío. El número de versión se define con `__version__` en `yt-dlp-gui.pyw` y debe coincidir con el encabezado de [CHANGELOG.md](../CHANGELOG.md). Los archivos de traducción de la interfaz están en `lang/` y los de esta documentación en `docs/`; las revisiones de hablantes nativos son bienvenidas.

## Apoyar el proyecto

Usar esta interfaz es, ha sido y seguirá siendo gratuito y de libre acceso para cualquiera. Si la herramienta le resulta especialmente útil, puede apoyar el proyecto en [Ko-fi](https://ko-fi.com/harlocksuites).

## Agradecimientos

Gracias a la comunidad que actualiza con regularidad [yt-dlp](https://github.com/yt-dlp/yt-dlp), sin el cual nada de esto sería posible.

## Licencia

El código se publica bajo licencia [MIT](../LICENSE). El icono, el logotipo y el banner «Harlock S.» (archivo `yt-dlp-gui.ico` y carpeta `assets/`) son creaciones originales generadas por IA a petición del autor. Forman la identidad visual del proyecto y no están cubiertos por la licencia MIT: no los reutilice en otro proyecto ni de forma que pueda inducir a confusión.
