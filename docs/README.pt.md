# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

Interface gráfica para o [yt-dlp](https://github.com/yt-dlp/yt-dlp), pensada para torná-lo acessível a todos e aproveitar ao máximo as suas capacidades.

> **Projeto em desenvolvimento.** Alguns recursos podem mudar, estar incompletos ou conter erros. Disponível para Windows; também é oferecida **uma versão de pré-lançamento para Linux**, menos testada.

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## Recursos

### Downloader individual e fila

- **Opções**: qualidade máxima (até 4K), somente áudio (MP3), legendas (formatos vtt, srt, ass), incorporação de legendas e miniatura, idioma de áudio principal, faixas de áudio secundárias (arquivo MKV com várias faixas) e uma biblioteca de «blocos de script» (pós-processamento, exportação, rede, comportamento) que você pode ampliar com seus próprios blocos.
- **Várias faixas de áudio**: no arquivo MKV, cada faixa de áudio traz a etiqueta do seu idioma («por», «eng»…); seu player a exibe no menu de áudio.
- **Comando gerado**: o comando do yt-dlp correspondente às suas escolhas é exibido em tempo real.
- **Fila**: adicione a URL atual e depois execute toda a fila, a partir de um item, um único vídeo ou um intervalo; pausa e retomada, pular o item atual, parar com limpeza dos arquivos parciais. A fila é mantida entre as sessões.
- **Nomes de arquivo existentes**: um vídeo avulso cujo nome já existe na pasta de destino recebe um sufixo (`_2`, `_3`…) para não sobrescrever nada. Uma playlist baixada por este downloader não é renumerada: os vídeos já presentes na pasta são ignorados («has already been downloaded»).

### Inspetor de playlists

- **Análise** de uma playlist: cada vídeo é listado com suas faixas de áudio e legendas disponíveis; itens ocultos, privados ou excluídos são ignorados sem bloquear o restante.
- **Regras globais** (qualidade, somente áudio, formato e incorporação de legendas, miniatura, numeração, idiomas, blocos de script, pasta de saída) com **exceções por vídeo** para o idioma principal, as faixas secundárias e as legendas.
- **Código de cores**: vermelho quando falta o idioma principal, laranja quando falta uma faixa secundária ou uma legenda.
- **Download da seleção** com registro, pausa, retomada e salto; se as faixas pedidas não existirem, o vídeo é repetido sem elas e depois um **resumo** mostra o que deu certo, foi ajustado ou falhou.

### Diretório inteligente e registro

- **Diretório inteligente**: o yt-dlp pula os vídeos já baixados graças a um registro guardado na pasta de saída. O arquivo `.yt-dlp-registre.json` contém o identificador, a URL, o título, a duração, o nome do arquivo e a data de cada vídeo; `.yt-dlp-archive.txt`, lido pelo yt-dlp, é derivado dele.
- **Verificação retroativa**: se vídeos da seleção já estiverem na pasta sem constar no registro, uma janela propõe registrá-los e pulá-los (comparando os títulos). Você pode desmarcar os falsos positivos.
- **Atualizar o registro**: conta os vídeos da pasta, os do registro e os que faltam, e depois procura no YouTube as informações ausentes (título e duração via ffprobe). Nada é registrado sem a sua confirmação, e dois botões abrem o arquivo local ou o link do YouTube encontrado para você conferir.

![yt-dlp GUI](img/registry.en.png)

### Cookies do navegador

- Escolha o navegador (Chrome, Firefox, Edge, Brave, Opera) cujos cookies o yt-dlp lê localmente: eles são necessários para as faixas de áudio secundárias e algumas legendas. **Recomendamos o Firefox.**
- **Resultados dos nossos testes** (Windows 11, outubro de 2026, conta do YouTube conectada em cada navegador): o **Firefox** funciona, com o navegador aberto ou fechado. O **Opera** só funciona **com o navegador fechado**: ele bloqueia o banco de cookies enquanto está aberto, e o yt-dlp exibe então «Could not copy Chrome cookie database». **Chrome, Edge e Brave** falham mesmo fechados: eles criptografam os cookies de um modo que o yt-dlp nem sempre consegue ler. Esses limites vêm dos navegadores e do yt-dlp, não do programa, e podem mudar com as atualizações deles.
- Se o seu navegador está configurado para **apagar os cookies ao fechar** (ou você navega em modo privado), não resta nenhum cookie no disco: o yt-dlp não consegue recuperar nada, nem com Chrome, Edge, Brave ou Firefox. Com Chrome, Edge e Brave isso é uma armadilha: é preciso fechar o navegador, o que apaga os cookies. Desative essa opção ou mantenha os cookies de youtube.com e google.com.
- Um **indicador** mostra o estado: vermelho se desativado ou com falha, laranja se não testado ou em andamento, verde se os cookies foram carregados. O botão ↻ executa um teste e a dica explica o estado ou o erro.
- **No Linux (pré-lançamento)**: são oferecidos Firefox, Chromium, Chrome, Brave, Edge, Opera e Vivaldi. Os navegadores da família Chromium protegem seus cookies com o chaveiro da área de trabalho (GNOME Keyring, KWallet): ele precisa estar desbloqueado, ou seja, com uma sessão gráfica aberta. Só a leitura de um perfil do Firefox foi testada; **o Firefox é recomendado**.

### Assistente de instalação, dependências e atualizações do yt-dlp

- **Assistente de instalação**: na primeira execução, propõe baixar o yt-dlp e o ffmpeg de seus repositórios oficiais no GitHub. A soma SHA-256 é verificada e não são necessários direitos de administrador.
- **Dependências**: a janela dedicada verifica ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 e deno, e pode instalá-los com o Chocolatey. Apenas o ffmpeg e o ffprobe são indispensáveis; o deno é recomendado (faixas de áudio secundárias); AtomicParsley, MKVToolNix e aria2 são opcionais: o programa funciona sem eles. No Linux, o assistente baixa ffmpeg, ffprobe e deno (soma SHA-256 verificada, sem direitos de administrador); para AtomicParsley, MKVToolNix e aria2, a janela mostra o comando do seu gerenciador de pacotes (apt, dnf, pacman ou zypper) para copiar em um terminal.
- **Atualização e diagnóstico**: atualiza o yt-dlp (`yt-dlp -U`) ou substitui o seu executável, mostra a versão e verifica as opções usadas pela interface.
- **Atualização do programa**: uma verificação diária (desativável) avisa sobre uma nova versão com um aviso discreto; a janela dedicada mostra as novidades e abre o download correspondente à sua instalação (instalador ou versão portátil). Nada é instalado automaticamente. Um interruptor no menu de opções («Verificar atualizações ao iniciar») ativa ou desativa a verificação automática, e «Procurar atualização do programa…» a executa sob demanda. No Linux, trata-se do AppImage ou do arquivo `.tar.gz` correspondente à sua arquitetura.

### Interface e idiomas

- Os controles se reorganizam conforme a largura da janela; o conteúdo rola na vertical e a tabela do inspetor também na horizontal.
- Interface em **15 idiomas**: francês, inglês, espanhol, português, italiano, polonês, húngaro, sérvio, russo, vietnamita, chinês, híndi, japonês, coreano e filipino. A troca de idioma vale após reiniciar, com a possibilidade de reiniciar imediatamente.

### Relatar um erro

- O botão «Relatar um erro» prepara um relatório técnico: versões do programa, do Python, do sistema e do yt-dlp, configurações inofensivas e as últimas linhas do registro. Suas pastas, seu nome de usuário e seus e-mails são ocultados. Enviar o relatório no GitHub exige uma conta gratuita do GitHub.
- Nada é enviado automaticamente: você revisa e edita o relatório e depois abre uma página de ticket do GitHub já preenchida (ou copia o relatório).

## Instalação

- **Instalador (recomendado)**: baixe `yt-dlp-gui-setup-X.Y.Z.exe` na [página de versões](https://github.com/harlockSuites/YT-dlp-GUI/releases) e execute-o. Windows 10 ou 11 (64 bits), sem direitos de administrador; o Python não é necessário.
- **Versão portátil**: baixe `yt-dlp-gui-portable-X.Y.Z.zip`, extraia onde quiser e execute `yt-dlp-gui.exe`; as configurações ficam nessa pasta.
- **Linux, AppImage (pré-lançamento)**: baixe `yt-dlp-gui-X.Y.Z-x86_64.AppImage` na [página de versões](https://github.com/harlockSuites/YT-dlp-GUI/releases), torne-o executável (`chmod +x`) e execute-o. Ele precisa do `libfuse2` (pacote `libfuse2` ou `fuse-libs`); sem ele, execute-o com `--appimage-extract-and-run`.
- **Linux, arquivo compactado (pré-lançamento)**: baixe `yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz`, extraia-o (`tar xzf`) e execute `./yt-dlp-gui/yt-dlp-gui`. As configurações e as ferramentas baixadas ficam em `~/.local/share/yt-dlp-GUI`; para desinstalar, apague essa pasta e o arquivo ou a pasta do programa.
- **Linux, requisitos e verificação**: Linux de 64 bits (x86_64) de uma distribuição de 2022 ou mais recente (glibc 2.35 ou superior). Para verificar um arquivo, baixe também `SHA256SUMS-linux.txt` e execute, na mesma pasta: `sha256sum -c SHA256SUMS-linux.txt --ignore-missing`. Os arquivos do Linux são publicados à parte, nas versões cuja etiqueta começa por «Linux-v» (marcadas como «Pre-release» no GitHub); a versão exibida por padrão na página é a do Windows.
- **A partir do código-fonte**: veja as seções «Requisitos» e «Início rápido» abaixo.
- **Desinstalação**: Configurações do Windows › Aplicativos › Aplicativos instalados › yt-dlp GUI, ou o atalho «Desinstalar» do menu Iniciar. O programa oferece excluir também os seus dados (configurações, fila, yt-dlp e ffmpeg baixados); seus vídeos nunca são excluídos. Como a instalação é própria de cada conta do Windows, o programa só aparece na lista da conta que o instalou. Na versão portátil, basta excluir a pasta. As ferramentas instaladas à parte com o Chocolatey (ffmpeg, Deno…) não são removidas.
- **Análise antivírus (VirusTotal)**: a versão 0.1.7 foi analisada em 21 de outubro de 2026. O [instalador](https://www.virustotal.com/gui/file/7177f2dc75c3b5309b2d6b96a2104d578dbaf67a0c8ed28af286aa37159df91c) é sinalizado por 4 de 69 mecanismos (Arctic Wolf, Microsoft, SecureAge, Skyhigh) com detecções heurísticas genéricas; o [inicializador da versão portátil](https://www.virustotal.com/gui/file/6889bde864b341a948dc23c01e29eba3c63315145705eb0d5bb24a4964b0735a) é sinalizado por 5 de 70 (Arctic Wolf, CrowdStrike Falcon, Microsoft, SecureAge, Zillya) e o [arquivo ZIP portátil](https://www.virustotal.com/gui/file/7fd0a4bb101ca4b4c513ff42e0782cc2371304c643bf03cb3ccd8e9abdb43706) por 1 de 66 (Zillya, sobre o próprio arquivo). Provavelmente são falsos positivos causados por um programa compactado e não assinado. Esses resultados valem apenas para esta versão. Em caso de dúvida, confira a soma SHA-256.
- **Code signing policy**: os arquivos não são assinados digitalmente. Um pedido de assinatura gratuita à SignPath Foundation foi recusado em 19 de outubro de 2026 (o projeto ainda tem pouca visibilidade pública) e poderá ser refeito; a [política de assinatura de código](https://github.com/harlockSuites/YT-dlp-GUI/blob/main/docs/CODE_SIGNING_POLICY.md) descreve o processo previsto caso um certificado seja obtido.
- **Aviso do Windows SmartScreen**: o instalador não é assinado digitalmente, então o Windows pode exibir «O Windows protegeu o computador». Clique em «Mais informações» e depois em «Executar assim mesmo». Para verificar a autenticidade do arquivo, compare a soma SHA-256 com a de `SHA256SUMS.txt`, publicada com cada versão:

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

## Avisos do Windows e dos navegadores

Este programa é gratuito, publicado por uma única pessoa, e seus arquivos **ainda não são assinados digitalmente**. Um arquivo novo, que quase ninguém baixou, não tem «reputação»: por isso os navegadores e o Windows mostram avisos **mesmo para um programa seguro**. Um aviso não prova que um arquivo seja perigoso, e a sua ausência não prova que seja seguro: veja como verificar você mesmo.

- **Navegador** (Firefox, Chrome, Edge, Brave): o download pode ser marcado como «incomum» ou como «contém um vírus ou software malicioso». É uma análise automática da reputação do arquivo. Verifique primeiro a soma de verificação (abaixo); se coincidir, você pode escolher a opção que permite ou mantém o download.
- **Windows SmartScreen**: «O Windows protegeu o seu PC» → clique em «Mais informações» e depois em «Executar assim mesmo», **depois** de verificar a soma de verificação.
- **Microsoft Defender (Segurança do Windows)**: ele pode colocar o arquivo em quarentena ou excluí-lo, indicando «Trojan:Win32/Wacatac.C!ml». O sufixo `!ml` designa uma detecção automática por aprendizado de máquina, comum em um arquivo novo e não assinado; essas detecções foram informadas à Microsoft como falsos positivos. Depois de verificar a soma SHA-256 (abaixo), você pode restaurar o arquivo: Segurança do Windows › Proteção contra vírus e ameaças › Histórico de proteção › abra o item › Ações › «Permitir no dispositivo» (ou «Restaurar»). Não desative a proteção do Windows nem adicione uma exclusão mais ampla do que este único arquivo.
- **Antivírus**: alguns mecanismos mostram detecções genéricas (veja a análise antivírus acima). Para ver a análise do seu arquivo, cole a soma SHA-256 dele na barra de busca do [VirusTotal](https://www.virustotal.com/): se o arquivo já for conhecido, você obtém o relatório sem enviá-lo.
- **Verifique o seu download**: baixe também `SHA256SUMS.txt` da mesma página de versão, abra o PowerShell na pasta dos arquivos e execute o comando abaixo: ele compara cada arquivo com a soma publicada e mostra `OK` ou `DIFFERENT`. Se um arquivo for `DIFFERENT`, não o execute.

```powershell
Get-Content .\SHA256SUMS.txt | ForEach-Object { $h, $n = $_ -split '\s+\*?', 2; if ((Get-FileHash $n -Algorithm SHA256).Hash -eq $h.ToUpper()) { "$n : OK" } else { "$n : DIFFERENT" } }
```

- Esta verificação prova que o seu arquivo é **idêntico** ao publicado no GitHub; por si só, não prova que ele seja inofensivo. O código-fonte e a compilação automática dos arquivos ([GitHub Actions](https://github.com/harlockSuites/YT-dlp-GUI/actions)) são públicos, e ainda não há assinatura digital: um pedido à SignPath Foundation foi recusado em 19 de outubro de 2026 (veja a «Code signing policy»).

## Requisitos

- Windows 10 ou 11, ou Linux de 64 bits (pré-lançamento)
- [Python 3](https://www.python.org/) com Tkinter (incluído na instalação padrão) (no Linux: o pacote `python3-tk`)
- `yt-dlp.exe` e, de preferência, o [ffmpeg](https://ffmpeg.org/): o assistente de instalação os baixa na primeira execução (no Linux: `yt-dlp`, sem `.exe`)

## Início rápido

1. Baixe ou clone este repositório e vá até a sua pasta.
2. Execute `yt-dlp-gui.bat` (ou `pythonw yt-dlp-gui.pyw`). No Linux: `python3 yt-dlp-gui.pyw`.
3. Na primeira execução, deixe o assistente instalar o yt-dlp e o ffmpeg; ele continua disponível no menu de opções.
4. Cole uma URL, escolha suas opções e depois baixe, adicione à fila ou abra o inspetor para uma playlist.

## Privacidade e uso responsável

- Este software não envia nenhum dado ao autor e não contém telemetria. As conexões de rede passam pelo yt-dlp (sites de vídeo), pelo assistente de instalação (GitHub) e pela ferramenta de registro (busca no YouTube). Uma verificação automática de atualizações também contata o GitHub ao iniciar (no máximo uma vez por dia); você pode desativá-la em «Verificar atualizações ao iniciar».
- Seus cookies ficam no seu computador: o yt-dlp os lê localmente no navegador escolhido.
- Use esta ferramenta respeitando os direitos autorais, os termos de uso dos sites e as leis do seu país, e baixe apenas o que você tem o direito de baixar.

## Desenvolvimento

Os testes (traduções, registro, montagem dos comandos, interface, assistente de instalação, documentação) são executados com:

```bash
python -X utf8 -m unittest discover -s tests -t .
```

Eles também rodam automaticamente no GitHub a cada envio. O número da versão é definido por `__version__` em `yt-dlp-gui.pyw` e deve corresponder ao cabeçalho de [CHANGELOG.md](../CHANGELOG.md). Os arquivos de tradução da interface ficam em `lang/` e os desta documentação em `docs/`; revisões de falantes nativos são bem-vindas.

## Apoiar o projeto

Usar esta interface é, sempre foi e continuará sendo gratuito e de livre acesso para qualquer pessoa. Se a ferramenta for especialmente útil para você, pode apoiar o projeto no [Ko-fi](https://ko-fi.com/harlocksuites).

## Agradecimentos

Obrigado à comunidade que atualiza regularmente o [yt-dlp](https://github.com/yt-dlp/yt-dlp), sem o qual nada disto seria possível.

## Licença

O código é publicado sob a licença [MIT](../LICENSE). O ícone, o logotipo e o banner «Harlock S.» (arquivo `yt-dlp-gui.ico` e pasta `assets/`) são criações originais geradas por IA a pedido do autor. Formam a identidade visual do projeto e não são cobertos pela licença MIT: não os reutilize em outro projeto nem de modo que possa causar confusão.
