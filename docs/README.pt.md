# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

Interface gráfica para o [yt-dlp](https://github.com/yt-dlp/yt-dlp), pensada para torná-lo acessível a todos e aproveitar ao máximo as suas capacidades.

> **Projeto em desenvolvimento.** Alguns recursos podem mudar, estar incompletos ou conter erros.

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## Recursos

### Downloader individual e fila

- **Opções**: qualidade máxima (até 4K), somente áudio (MP3), legendas (formatos vtt, srt, ass), incorporação de legendas e miniatura, idioma de áudio principal, faixas de áudio secundárias (arquivo MKV com várias faixas) e uma biblioteca de «blocos de script» (pós-processamento, exportação, rede, comportamento) que você pode ampliar com seus próprios blocos.
- **Comando gerado**: o comando do yt-dlp correspondente às suas escolhas é exibido em tempo real.
- **Fila**: adicione a URL atual e depois execute toda a fila, a partir de um item, um único vídeo ou um intervalo; pausa e retomada, pular o item atual, parar com limpeza dos arquivos parciais. A fila é mantida entre as sessões.

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

- Escolha o navegador (Chrome, Firefox, Edge, Brave, Opera) cujos cookies o yt-dlp lê localmente: eles são necessários para as faixas de áudio secundárias e algumas legendas. Com Chrome, Edge ou Brave, feche completamente o navegador antes de baixar: ele bloqueia o banco de cookies enquanto está aberto, e o yt-dlp exibe então «Could not copy Chrome cookie database». O Firefox não tem essa limitação.
- Um **indicador** mostra o estado: vermelho se desativado ou com falha, laranja se não testado ou em andamento, verde se os cookies foram carregados. O botão ↻ executa um teste e a dica explica o estado ou o erro.

### Assistente de instalação, dependências e atualizações do yt-dlp

- **Assistente de instalação**: na primeira execução, propõe baixar o yt-dlp e o ffmpeg de seus repositórios oficiais no GitHub. A soma SHA-256 é verificada e não são necessários direitos de administrador.
- **Dependências**: a janela dedicada verifica ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 e deno, e pode instalá-los com o Chocolatey.
- **Atualização e diagnóstico**: atualiza o yt-dlp (`yt-dlp -U`) ou substitui o seu executável, mostra a versão e verifica as opções usadas pela interface.
- **Atualização do programa**: uma verificação diária (desativável) avisa sobre uma nova versão com um aviso discreto; a janela dedicada mostra as novidades e abre o download correspondente à sua instalação (instalador ou versão portátil). Nada é instalado automaticamente. Um interruptor no menu de opções («Verificar atualizações ao iniciar») ativa ou desativa a verificação automática, e «Procurar atualização do programa…» a executa sob demanda.

### Interface e idiomas

- Os controles se reorganizam conforme a largura da janela; o conteúdo rola na vertical e a tabela do inspetor também na horizontal.
- Interface em **15 idiomas**: francês, inglês, espanhol, português, italiano, polonês, húngaro, sérvio, russo, vietnamita, chinês, híndi, japonês, coreano e filipino. A troca de idioma vale após reiniciar, com a possibilidade de reiniciar imediatamente.

### Relatar um erro

- O botão «Relatar um erro» prepara um relatório técnico: versões do programa, do Python, do Windows e do yt-dlp, configurações inofensivas e as últimas linhas do registro. Suas pastas, seu nome de usuário e seus e-mails são ocultados.
## Instalação

- **Instalador (recomendado)**: baixe `yt-dlp-gui-setup-X.Y.Z.exe` na [página de versões](https://github.com/harlockSuites/YT-dlp-GUI/releases) e execute-o. Windows 10 ou 11 (64 bits), sem direitos de administrador; o Python não é necessário.
- **Versão portátil**: baixe `yt-dlp-gui-portable-X.Y.Z.zip`, extraia onde quiser e execute `yt-dlp-gui.exe`; as configurações ficam nessa pasta.
- **A partir do código-fonte**: veja as seções «Requisitos» e «Início rápido» abaixo.
- **Aviso do Windows SmartScreen**: o instalador não é assinado digitalmente, então o Windows pode exibir «O Windows protegeu o computador». Clique em «Mais informações» e depois em «Executar assim mesmo». Para verificar a autenticidade do arquivo, compare a soma SHA-256 com a de `SHA256SUMS.txt`, publicada com cada versão:

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

- Nada é enviado automaticamente: você revisa e edita o relatório e depois abre uma página de ticket do GitHub já preenchida (ou copia o relatório).

## Requisitos

- Windows
- [Python 3](https://www.python.org/) com Tkinter (incluído na instalação padrão)
- `yt-dlp.exe` e, de preferência, o [ffmpeg](https://ffmpeg.org/): o assistente de instalação os baixa na primeira execução

## Início rápido

1. Baixe ou clone este repositório e vá até a sua pasta.
2. Execute `yt-dlp-gui.bat` (ou `pythonw yt-dlp-gui.pyw`).
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
