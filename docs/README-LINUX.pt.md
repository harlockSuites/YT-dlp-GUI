# yt-dlp GUI — versão para Linux

[Français](../README-LINUX.md) · [English](README-LINUX.en.md) · [Español](README-LINUX.es.md) · [Português](README-LINUX.pt.md) · [Italiano](README-LINUX.it.md) · [Polski](README-LINUX.pl.md) · [Magyar](README-LINUX.hu.md) · [Srpski](README-LINUX.sr.md) · [Русский](README-LINUX.ru.md) · [Tiếng Việt](README-LINUX.vi.md) · [中文](README-LINUX.zh.md) · [हिन्दी](README-LINUX.hi.md) · [日本語](README-LINUX.ja.md) · [한국어](README-LINUX.ko.md) · [Filipino](README-LINUX.fil.md)

> **Pré-lançamento.** Este documento complementa o [README principal](README.pt.md): é o mesmo programa, mas aqui só se trata do que é específico do Linux (instalação, cookies e chaveiros, arquivos, solução de problemas). As novidades de cada versão estão em [CHANGELOG-linux.md](../CHANGELOG-linux.md). As traduções ainda precisam ser revisadas por falantes nativos; em caso de dúvida, valem os textos em francês e inglês.

## Sumário

1. [Estado do pré-lançamento](#s1)
2. [Instalar](#s2)
3. [Primeira execução e dependências](#s3)
4. [Cookies do navegador](#s4)
5. [Chaveiros: operações manuais](#s5)
6. [Onde estão os arquivos](#s6)
7. [Solução de problemas](#s7)
8. [Relatar um erro](#s8)
9. [Para desenvolvedores](#s9)

<a id="s1"></a>

## 1. Estado do pré-lançamento

A versão para Linux reproduz o comportamento da versão para Windows 0.1.7 (congelada, usada como modelo). Ela é publicada como **pré-lançamento do GitHub** com etiquetas `Linux-vX.Y.Z`: nunca é apresentada como a «última versão» do repositório.

**O que foi testado** (máquina virtual Debian 12, ambiente GNOME, Python 3.11, uma conta real do YouTube com sessão iniciada em cada navegador, outubro de 2026):

- **Cookies do Firefox, Waterfox, Floorp e Zen Browser**: lidos com o navegador aberto ou fechado.
- **Cookies do Google Chrome, Chromium, Brave, Vivaldi, Opera e Microsoft Edge**: lidos com o navegador **fechado**, depois de abrir cada navegador uma vez e fazer login no YouTube nele (veja a [seção 5](#s5)). O download individual e o Inspetor de playlists funcionaram.
- **LibreWolf**: lidos somente enquanto ele está aberto e com a sessão iniciada (por padrão ele apaga os cookies ao fechar).
- **Vídeo privado** com os cookies do Firefox, e uma playlist de três vídeos com um privado.
- **Pacotes**: o AppImage e o arquivo compactado `.tar.gz` são construídos pela CI no Ubuntu 22.04; o `.deb` foi construído, instalado, iniciado e removido no Debian 12; o AppImage, o arquivo compactado e o `.deb` foram iniciados na máquina virtual, e «Instalar no menu» / «Desinstalar» foram testados com o mouse usando o AppImage (ícone adicionado e depois removido do menu e da Área de Trabalho).
- **Idioma e fonte**: coreano escolhido numa máquina sem fonte coreana; a janela «Font needed» oferece a fonte, ela é baixada e verificada, o programa reinicia e o texto fica legível.

**O que ainda não foi testado**:

- outras distribuições (Ubuntu, Fedora, Arch, openSUSE…) e ambientes que não sejam o GNOME, incluindo o KDE Plasma (KWallet);
- navegadores instalados como Flatpak ou Snap (exceto a estrutura do LibreWolf em Flatpak, que foi observada);
- Vivaldi, Opera ou Edge **sem** Chrome nem Chromium instalados (veja a [seção 5](#s5));
- a arquitetura aarch64 (o programa a prevê, mas os pacotes só são construídos para x86_64);
- um computador Linux real, fora de uma máquina virtual (ambiente e hardware reais);
- as traduções: ainda precisam ser revisadas por falantes nativos.

<a id="s2"></a>

## 2. Instalar

### Qual formato escolher

| Formato | Para quem | Direitos de administrador | Entrada no menu |
|---|---|---|---|
| **AppImage** | qualquer distribuição recente de 64 bits | não | «Instalar no menu» (seção 2.3) |
| **Arquivo compactado `.tar.gz`** | idem, sem AppImage nem FUSE | não | «Instalar no menu» |
| **Pacote `.deb`** | Debian, Ubuntu e derivadas | sim (`sudo`) | automática |
| **Código-fonte** | desenvolvedores, testes | não | nenhuma |

Requisitos: Linux de 64 bits (x86_64) de uma distribuição de 2022 ou mais recente (glibc 2.35 ou superior), porque os pacotes são construídos no Ubuntu 22.04.

**Se você está começando no Linux**: só o pacote `.deb` é instalado «de verdade» e aparece no gerenciador de programas. O AppImage e o arquivo compactado são arquivos ou pastas comuns, guardados onde você quiser: para removê-los, basta apagá-los como qualquer outro arquivo (seções 2.2 e 2.5). As configurações ficam à parte, em `~/.local/share/yt-dlp-GUI` (seção 6), e sobrevivem a essa exclusão.

Os arquivos estão na [página de versões publicadas](https://github.com/harlockSuites/YT-dlp-GUI/releases): procure as etiquetas `Linux-v…`, marcadas como «Pre-release».

### 2.1 Verificar o download

Baixe também `SHA256SUMS-linux.txt` na mesma pasta e depois:

```bash
sha256sum -c SHA256SUMS-linux.txt --ignore-missing
```

Cada arquivo presente deve mostrar `OK`. Isso prova que o seu arquivo é idêntico ao publicado, não que seja inofensivo: o código-fonte e a construção automática são públicos.

### 2.2 AppImage

```bash
chmod +x yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

O AppImage precisa da biblioteca FUSE 2:

| Distribuição | Pacote |
|---|---|
| Debian, Ubuntu 22.04 e derivadas | `libfuse2` |
| Ubuntu 24.04 e mais recentes | `libfuse2t64` |
| Fedora | `fuse-libs` |

Sem FUSE, execute-o mesmo assim: ele se extrai sozinho numa pasta temporária:

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage --appimage-extract-and-run
```

O AppImage não é «instalado»: não aparece no gerenciador de programas. Para removê-lo, apague o arquivo:

```bash
rm yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

Para encontrar o AppImage no menu de aplicativos, com o seu ícone, use a função **«Instalar no menu…» do programa** (seção 2.3): não há nenhum comando para digitar.

### 2.3 Instalar no menu (sem administrador)

Um AppImage aberto com duplo clique não deixa nenhum ícone no menu de aplicativos. No programa: menu de opções › **«Instalar no menu…»**. A janela:

- copia o programa para `~/.local/share/yt-dlp-GUI/app/`;
- grava o lançador `~/.local/share/applications/yt-dlp-gui.desktop` e o ícone `~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png`;
- adiciona, se a caixa estiver marcada, um atalho na Área de Trabalho (marcado como «confiável» para o GNOME quando a ferramenta `gio` existe);
- depois oferece «Atualizar» (copia de novo a versão que está em execução) e «Desinstalar».

«Desinstalar» só remove o que a instalação criou e **mantém as suas configurações** e as ferramentas baixadas. Um lançador sem a nossa marca interna (`X-YtDlpGui-Installer=1`) nunca é apagado.

Limites: a janela está disponível a partir do AppImage e do arquivo compactado. A partir do código-fonte, ela indica o AppImage; a partir do pacote `.deb`, explica que o programa já está no menu.

Se o atalho da Área de Trabalho mostrar um aviso: clique com o botão direito no ícone › «Permitir execução». Alguns ambientes (o GNOME por padrão) não mostram ícones na Área de Trabalho: o lançador do menu funciona em todos os casos.

Para remover tudo à mão:

```bash
rm -rf ~/.local/share/yt-dlp-GUI/app ~/.local/share/applications/yt-dlp-gui.desktop ~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png ~/Desktop/yt-dlp-gui.desktop
```

Se o pacote `.deb` já estiver instalado, não use esta função: o programa já está no menu e apareceria uma segunda entrada «yt-dlp GUI» (remova antes o `.deb` com `sudo apt remove yt-dlp-gui` se preferir este método).

### 2.4 Pacote `.deb`

```bash
sudo apt install ./yt-dlp-gui_X.Y.Z_amd64.deb
```

O programa vai para `/opt/yt-dlp-gui`, com o link `/usr/bin/yt-dlp-gui`, o lançador do menu, o ícone e a licença (`/usr/share/doc/yt-dlp-gui/`). Ele depende de `libc6 (>= 2.35)` e de `libx11-6`.

Para removê-lo (as suas configurações, em `~/.local/share/yt-dlp-GUI`, nunca são tocadas):

```bash
sudo apt remove yt-dlp-gui
```

### 2.5 Arquivo compactado `.tar.gz`

```bash
tar xzf yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz
```

```bash
./yt-dlp-gui/yt-dlp-gui
```

Para manter as configurações e as ferramentas **dentro da pasta extraída** (pen drive, teste sem deixar rastros), crie um arquivo vazio `portable.flag` ao lado do executável:

```bash
touch yt-dlp-gui/portable.flag
```

Sem esse arquivo, os dados vão para `~/.local/share/yt-dlp-GUI` (seção 6).

O arquivo compactado não é «instalado»: não aparece no gerenciador de programas. Para removê-lo, apague a pasta extraída:

```bash
rm -rf yt-dlp-gui
```

### 2.6 A partir do código-fonte

```bash
python3 yt-dlp-gui.pyw
```

A partir do código-fonte, as configurações e as ferramentas baixadas vão para a mesma pasta das versões instaladas (`~/.local/share/yt-dlp-GUI`): baixar o código de novo ou apagar a sua pasta não as apaga. Para manter os dados dentro da pasta do código (teste sem deixar rastros), crie um arquivo vazio `portable.flag` ao lado de `yt-dlp-gui.pyw`.

É preciso ter o Python 3 com Tkinter:

| Distribuição | Pacote |
|---|---|
| Debian, Ubuntu e derivadas, openSUSE | `python3-tk` |
| Fedora | `python3-tkinter` |
| Arch | `tk` |

### 2.7 Atualizações

Uma verificação diária (que pode ser desativada no menu de opções) procura as versões `Linux-vX.Y.Z`, inclusive os pré-lançamentos, e **nunca** oferece uma versão para Windows. Ela abre a página de download do arquivo que corresponde à sua instalação (AppImage, arquivo compactado ou `.deb`); **nada é instalado automaticamente**. Para atualizar:

- **AppImage ou arquivo compactado instalado no menu**: baixe o novo AppImage, execute-o e depois «Instalar no menu… › Atualizar»;
- **`.deb`**: `sudo apt install ./new-file.deb`;
- **arquivo compactado não instalado**: extraia o novo arquivo compactado no lugar do antigo.

### 2.8 Remover tudo, dados inclusive

Depois de remover o programa (seções 2.3 a 2.5), para apagar também as suas configurações, a fila e as ferramentas baixadas (yt-dlp, ffmpeg, deno):

```bash
rm -rf ~/.local/share/yt-dlp-GUI
```

Os seus vídeos baixados nunca ficam nessa pasta.

<a id="s3"></a>

## 3. Primeira execução e dependências

Na primeira execução, o assistente de instalação propõe baixar o **yt-dlp** (`yt-dlp_linux`), o **ffmpeg** (o arquivo compactado `.tar.xz` das compilações oficiais do yt-dlp) e o **deno** a partir dos seus repositórios do GitHub. As somas SHA-256 são verificadas, não se pedem direitos de administrador, e os arquivos vão para `~/.local/share/yt-dlp-GUI` (yt-dlp) e `~/.local/share/yt-dlp-GUI/bin` (ffmpeg, ffprobe, deno). Ele continua disponível no menu de opções.

Só o ffmpeg e o ffprobe são indispensáveis; o deno é recomendado (faixas de áudio secundárias). **AtomicParsley, MKVToolNix e aria2** são opcionais: a janela «Dependências» mostra o comando do seu gerenciador de pacotes, para copiar num terminal. O programa nunca o executa sozinho. Os mesmos comandos:

| Gerenciador de pacotes | Comando |
|---|---|
| apt | `sudo apt install aria2 atomicparsley mkvtoolnix` |
| dnf | `sudo dnf install AtomicParsley aria2 mkvtoolnix` |
| pacman | `sudo pacman -S aria2 atomicparsley mkvtoolnix-cli` |
| zypper | `sudo zypper install AtomicParsley aria2 mkvtoolnix` |

<a id="s4"></a>

## 4. Cookies do navegador

O yt-dlp lê os cookies **localmente**, no navegador que você escolher (faixas de áudio secundárias, legendas, vídeos privados, conteúdo para membros). Por padrão, o programa oferece os cinco navegadores mais usados no Linux (Firefox, Google Chrome, Chromium, Brave, Vivaldi). A entrada **«Navegadores para cookies…»** do menu de opções abre a janela «Navegadores para cookies», que oferece 11: marque os de que precisa; um ✔ indica aqueles cuja pasta de perfil existe no seu computador.

| Navegador | Lido pelo yt-dlp como | Chaveiro | Pastas de perfil procuradas |
|---|---|---|---|
| Firefox | `firefox` | não | `~/.config/mozilla/firefox`, `~/.mozilla/firefox`, Flatpak, Snap |
| Google Chrome | `chrome` | sim | `~/.config/google-chrome` |
| Chromium | `chromium` | sim | `~/.config/chromium` |
| Brave | `brave` | sim | `~/.config/BraveSoftware/Brave-Browser` |
| Vivaldi | `vivaldi` | sim | `~/.config/vivaldi` |
| Opera | `opera` | sim | `~/.config/opera` |
| Microsoft Edge | `edge` | sim | `~/.config/microsoft-edge` |
| LibreWolf, Waterfox, Floorp, Zen Browser | `firefox:` + pasta do perfil | não | `~/.librewolf`, `~/.config/librewolf`… (mesmo esquema para os outros), Flatpak incluído |

Os derivados do Firefox não têm um nome que o yt-dlp conheça: o programa procura o banco `cookies.sqlite` deles (até três níveis dentro das suas pastas) e entrega ao yt-dlp a pasta do perfil usado mais recentemente. `XDG_CONFIG_HOME` é respeitada quando é absoluta.

O **indicador** ao lado da lista mostra o estado: vermelho (desativado ou com falha), laranja (não testado ou em andamento), verde (cookies lidos). O botão ↻ executa um teste; a dica explica o erro. Um teste que lê **0 cookies** nunca fica verde.

### Casos frequentes

| O que você vê | Causa provável | O que fazer |
|---|---|---|
| «Extracted 0 cookies» e depois «Sign in to confirm you're not a bot» | o navegador não guarda nenhum cookie no disco (o LibreWolf os apaga ao fechar por padrão; perfil sem sessão iniciada; modo privado) | deixá-lo aberto e com a sessão do YouTube iniciada, ou desativar a exclusão de cookies ao fechar nas configurações de privacidade dele |
| «Item does not exist!» com Chrome, Chromium, Brave, Vivaldi, Opera ou Edge | o yt-dlp não encontrou a chave do navegador no chaveiro da área de trabalho | abrir o navegador uma vez, fazer login no YouTube, fechá-lo e repetir o teste; se não resolver, [seção 5](#s5) |
| «Could not copy Chrome cookie database» ou «database is locked» | o navegador bloqueia o banco de dados enquanto está em execução | fechá-lo e repetir o teste |
| «Failed to decrypt» | cookies criptografados com uma chave que o yt-dlp não obteve | [seção 5](#s5) |

### Testar um navegador a partir de um terminal

É a melhor forma de ver o erro exato (substitua `IDENTIFIER` pelo identificador de qualquer vídeo do YouTube):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Linhas a procurar: `Extracted N cookies from chromium` (N deve ser maior que 0), `Chosen keyring: GNOMEKEYRING` (o chaveiro escolhido) e `cookie version breakdown: {'v10': 0, 'v11': 50, …}` (os cookies `v11` precisam do chaveiro, os `v10` não).

Para um derivado do Firefox, informe a pasta do perfil. Para encontrá-la:

```bash
find ~ -name cookies.sqlite -path "*librewolf*" 2>/dev/null
```

Numa instalação Flatpak, procure em `~/.var/app`:

```bash
find ~/.var/app -name cookies.sqlite 2>/dev/null
```

Depois, com a pasta que contém `cookies.sqlite`:

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser "firefox:/path/to/profile" -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

<a id="s5"></a>

## 5. Chaveiros: operações manuais

### Para que serve

Os navegadores da família Chromium (Chrome, Chromium, Brave, Vivaldi, Opera, Edge) criptografam os cookies. A chave de criptografia fica guardada no **chaveiro da área de trabalho**: GNOME Keyring (ou um equivalente compatível, pelo «Secret Service») no GNOME, XFCE, Cinnamon, MATE…, KWallet no KDE. Para descriptografar, o yt-dlp pede essa chave ao chaveiro. O Firefox e os seus derivados não precisam dele.

Dois fatos úteis:

- **A chave só existe depois que o navegador é aberto pela primeira vez.** Na nossa máquina virtual, o erro «Item does not exist!» desapareceu quando cada navegador foi aberto uma vez e o login no YouTube foi feito nele. A causa exata da primeira falha não foi estabelecida com certeza: o chaveiro existia, era o padrão e estava desbloqueado.
- **Qual chaveiro o yt-dlp usa** depende do ambiente de área de trabalho detectado (variáveis `XDG_CURRENT_DESKTOP` e `DESKTOP_SESSION`), segundo o código do yt-dlp (outubro de 2026):

| Ambiente detectado | Chaveiro usado pelo yt-dlp |
|---|---|
| GNOME, Cinnamon, MATE, XFCE, Pantheon, Unity, Deepin, UKUI | GNOME Keyring (`GNOMEKEYRING`) |
| KDE 4, 5, 6 | KWallet (`KWALLET`, `KWALLET5`, `KWALLET6`) |
| LXQt, KDE 3, ambiente não reconhecido (gerenciadores de janelas sozinhos: sway, i3…) | nenhum: texto simples (`BASICTEXT`) |

No último caso, o yt-dlp só lê cookies `v10`: se o seu navegador guarda a chave no GNOME Keyring, os cookies `v11` dele não serão descriptografados. É preciso então impor o chaveiro a partir de um terminal (seção 5.6); o programa ainda não oferece essa opção.

Os itens procurados no chaveiro chamam-se «*nome* Safe Storage». Segundo o código do yt-dlp, é **«Chrome Safe Storage»** para Chrome e Vivaldi, **«Chromium Safe Storage»** para Chromium, Opera e Edge, **«Brave Safe Storage»** para o Brave. Na nossa máquina virtual, Chrome e Chromium também estavam instalados e tinham sido abertos: não sabemos se Vivaldi, Opera ou Edge funcionariam sozinhos.

### 5.1 O chaveiro existe?

```bash
ls -la ~/.local/share/keyrings/
```

Você deve ver um arquivo `login.keyring` (o chaveiro «login»). Em seguida, qual chaveiro é o **padrão**?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets --method org.freedesktop.Secret.Service.ReadAlias default
```

Resposta `(objectpath '/org/freedesktop/secrets/collection/login',)`: há um chaveiro padrão. Resposta `'/'`: **nenhum**, passe para a seção 5.4.

### 5.2 Está bloqueado?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Locked
```

`(<false>,)`: desbloqueado. `(<true>,)`: bloqueado; abra-o com o Seahorse (seção 5.4), que pedirá a senha dele.

### 5.3 A chave do meu navegador está nele?

Liste os itens:

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Items
```

A resposta dá caminhos terminados por um número (`…/login/1`, `…/login/2`…). Para ler o nome de cada um (adapte a lista de números):

```bash
for i in 1 2 3 4 5 6; do gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login/$i --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Item Label; done
```

Você deve ver, por exemplo, `Chromium Safe Storage`, `Chrome Safe Storage` ou `Brave Safe Storage`. Nomes vazios são inofensivos. Se o nome do seu navegador estiver faltando: abra-o uma vez, faça login no YouTube, feche-o e execute este comando de novo.

### 5.4 Criar ou desbloquear um chaveiro com o Seahorse

Instale o Seahorse («Senhas e chaves») e as ferramentas associadas. O comando exato também está na janela «Navegadores para cookies» do programa:

| Gerenciador de pacotes | Comando |
|---|---|
| apt | `sudo apt install gnome-keyring seahorse libsecret-tools` |
| dnf | `sudo dnf install gnome-keyring seahorse libsecret` |
| pacman | `sudo pacman -S gnome-keyring seahorse libsecret` |
| zypper | `sudo zypper install gnome-keyring seahorse libsecret-tools` |

Depois abra-o:

```bash
seahorse
```

- **Sem chaveiro padrão**: crie um (botão «+» ou menu Arquivo › Novo › chaveiro de senhas), dê a ele o nome «Login» e clique com o botão direito nele › «Definir como padrão». Os nomes exatos variam conforme a versão do Seahorse.
- **Chaveiro bloqueado**: duplo clique ou botão direito › «Desbloquear» e digite a senha dele (digite você mesmo; o programa nunca a pede).
- **Login automático**: um chaveiro protegido por senha não pode abrir sozinho se você não digitar nenhuma senha ao iniciar a sessão; ele fica bloqueado até você desbloqueá-lo (ou até usar a mesma senha para a sessão e para o chaveiro).

Depois **abra o navegador, faça login no YouTube, feche-o** e repita o teste (seção 4).

### 5.5 KDE Plasma (KWallet)

No KDE, o yt-dlp consulta o KWallet (`kwallet-query`). O gerenciador chama-se `kwalletmanager` (ou `kwalletmanager5`) conforme a distribuição. Essa configuração **não foi testada** nos nossos testes.

### 5.6 Impor o chaveiro ao yt-dlp (terminal)

O programa deixa o yt-dlp escolher o chaveiro conforme o ambiente. Para forçá-lo, acrescente `+CHAVEIRO` ao nome do navegador (valores: `gnomekeyring`, `kwallet`, `kwallet5`, `kwallet6`, `basictext`):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium+gnomekeyring -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Para saber qual chaveiro um Chromium usa de fato (comando tirado do código do yt-dlp, não testado aqui):

```bash
chromium --enable-logging=stderr --v=1 2>&1 | grep key_storage_
```

### 5.7 Sem chaveiro: `--password-store=basic` (avançado, não testado)

O Chromium aceita `--password-store=basic`: ele passa a guardar a chave em claro (uma chave fixa e conhecida) e criptografa os cookies novos como `v10`, que o yt-dlp lê sem chaveiro (`chromium+basictext`). **É menos seguro**: qualquer programa que consiga ler os seus arquivos pode descriptografar esses cookies. Só use se entender essa troca; os cookies já salvos provavelmente não são recodificados: faça login de novo.

### 5.8 Último recurso

Se um chaveiro estiver corrompido, **faça primeiro uma cópia de segurança**:

```bash
cp -a ~/.local/share/keyrings ~/keyrings-backup
```

Apagar `login.keyring` elimina **todas** as senhas que ele contém (Wi-Fi, contas online…): não faça isso sem entender as consequências.

<a id="s6"></a>

## 6. Onde estão os arquivos

A pasta de dados é `$XDG_DATA_HOME/yt-dlp-GUI` (por padrão `~/.local/share/yt-dlp-GUI`), a menos que `portable.flag` esteja ao lado do executável do arquivo compactado (ou do script `yt-dlp-gui.pyw`).

| Arquivo ou pasta | Conteúdo |
|---|---|
| `gui-config.json` | configurações (idioma, navegador, pastas, escolha de navegadores…) |
| `download-queue.json` | fila de downloads |
| `custom-blocks.json` | blocos de opções personalizados |
| `yt-dlp` | executável baixado pelo assistente |
| `bin/` | ffmpeg, ffprobe, deno |
| `cmd/` | arquivos de configuração temporários do yt-dlp |
| `app/` | cópia do programa feita por «Instalar no menu» |
| `~/.local/share/fonts/yt-dlp-GUI/` (fora da pasta de dados) | fonte Noto baixada para coreano, japonês ou chinês; para removê-la: `rm -rf ~/.local/share/fonts/yt-dlp-GUI` |

<a id="s7"></a>

## 7. Solução de problemas

| Problema | Pista |
|---|---|
| O AppImage não inicia | executá-lo num terminal para ler o erro; instalar o FUSE 2 (seção 2.2) ou acrescentar `--appimage-extract-and-run` |
| Nada aparece, ou erro de biblioteca | verificar a versão da glibc: `ldd --version` deve indicar 2.35 ou superior |
| Sem ícone na Área de Trabalho | o GNOME não mostra nenhum por padrão; use o menu de aplicativos |
| Atalho da Área de Trabalho com um aviso | botão direito › «Permitir execução» |
| Arrastar e soltar entre a máquina hospedeira e uma máquina virtual não funciona | é um recurso do VirtualBox (Guest Additions), não do programa |
| A interface está com o tamanho errado | o programa segue as fontes do sistema (Tk); tente outro tamanho de fonte do sistema |
| A atualização do yt-dlp falha | use «Atualização & Diagnóstico» no menu de opções; senão, baixe `yt-dlp_linux` e escolha-o na janela de substituição (o arquivo escolhido se torna executável) |
| Quadrados no lugar do texto (coreano, chinês, japonês…) | nenhuma fonte do sistema contém esses caracteres; no Debian e no Ubuntu: `sudo apt install fonts-noto-cjk` (~90 MB), depois feche e abra de novo o programa; em outras distribuições, instale o pacote «Noto Sans CJK» da distribuição; o programa também pode baixar a fonte sozinho (coreano, japonês, chinês) ao escolher o idioma, sem direitos de administrador |

<a id="s8"></a>

## 8. Relatar um erro

O botão «Relatar um erro» prepara um relatório técnico em que as suas pastas, o seu nome de usuário e os seus endereços de e-mail ficam ocultos; nada é enviado automaticamente. Para o Linux, acrescente:

```bash
cat /etc/os-release
```

```bash
echo "$XDG_CURRENT_DESKTOP $XDG_SESSION_TYPE"
```

e diga **como** você instalou o programa (AppImage, arquivo compactado, `.deb`, código-fonte) e, num problema de cookies, **o resultado do teste no terminal** (seção 4), sem colar os seus cookies.

<a id="s9"></a>

## 9. Para desenvolvedores

Testes (com uma tela virtual, sem precisar de tela real):

```bash
xvfb-run -a python3 -X utf8 -m unittest discover -s tests -t .
```

Construir os pacotes (ferramentas de construção: `pip install -r packaging/requirements-build.txt`, mais o `appimagetool`, cujo caminho é indicado pela variável `APPIMAGETOOL`):

```bash
python3 packaging/build_linux.py
```

```bash
python3 packaging/build_deb.py
```

Os resultados ficam em `dist/`. Para a melhor compatibilidade, construa na distribuição mais antiga suportada (a glibc da máquina de construção é o mínimo exigido das máquinas que executam o programa). Verificações úteis do `.deb`:

```bash
lintian dist/yt-dlp-gui_*_amd64.deb
```

O único erro de forma conhecido é `dir-or-file-in-opt` (programa incluído em `/opt`).

**Publicar**: verificar `__version__` em `yt-dlp-gui.pyw`, datar a seção da versão em `CHANGELOG-linux.md`, fazer o commit e depois criar e enviar a etiqueta `Linux-vX.Y.Z`. O fluxo «Release Linux» executa os testes, constrói o AppImage, o arquivo compactado e o `.deb`, calcula as somas e cria a versão como **pré-lançamento**, nunca como «última versão» (a verificação de atualizações da versão para Windows 0.1.7 não deve encontrar ali nenhuma etiqueta do Linux).

Licença: MIT, como o resto do repositório (veja [LICENSE](../LICENSE)).
