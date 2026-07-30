# Baixador de vídeos do YouTube dublados em português (pt-BR) — Windows

Programa: **`baixar_dublado.py`**
Pasta do projeto: `C:\Projeto_Claude\Youtu_Baixar`
Pasta dos vídeos baixados: `C:\Projeto_Claude\Youtu_Baixar\vídeos`

Este programa é a versão Windows (e automatizada) daquele processo que você
descobriu no Linux Mint: usar os **cookies do navegador** para derrubar a barreira
do **PO Token**, deixar o **runtime de JavaScript** resolver os desafios do player
e então escolher a faixa de áudio **`[pt-BR]`** na **maior qualidade de vídeo**
disponível.

A diferença é que aqui você não precisa mais rodar `-F`, ler a tabela e escolher
o ID na mão (`96-8`, `94-4`, ...). O programa faz isso sozinho.

---

## 1. Índice

1. [Índice](#1-índice)
2. [O que o programa faz por dentro](#2-o-que-o-programa-faz-por-dentro)
3. [Requisitos (e o que já está instalado na sua máquina)](#3-requisitos-e-o-que-já-está-instalado-na-sua-máquina)
4. [Instalação — passo a passo](#4-instalação--passo-a-passo)
5. [Como usar — o jeito fácil (duplo clique)](#5-como-usar--o-jeito-fácil-duplo-clique)
6. [Como usar — pelo terminal (todas as opções)](#6-como-usar--pelo-terminal-todas-as-opções)
7. [Teste real já executado](#7-teste-real-já-executado)
8. [Sobre "qualidade máxima": o que esperar](#8-sobre-qualidade-máxima-o-que-esperar)
9. [Solução de problemas](#9-solução-de-problemas)
10. [Manutenção (manter atualizado)](#10-manutenção-manter-atualizado)
11. [Arquivos do projeto](#11-arquivos-do-projeto)

---

## 2. O que o programa faz por dentro

Quatro etapas, na mesma ordem em que você fez manualmente no Linux:

**Etapa 1 — Detecta o ambiente.**
Acha o `yt-dlp`, o `ffmpeg` e um runtime de JavaScript (`deno`, `node`, `bun` ou
`quickjs`). Sem runtime de JS o YouTube esconde os formatos e só sobram os
*storyboards* (`sb0`, `sb1`...) — exatamente o sintoma que você viu.

**Etapa 2 — Sonda o vídeo tentando várias estratégias, em ordem.**
Ele roda `yt-dlp -J` (que devolve todos os metadados em JSON) repetidamente:

| Ordem | Estratégia |
|-------|-----------|
| 1 | cookies do Firefox + cliente padrão |
| 2 | cookies do Firefox + cliente `web_safari` |
| 3 | cookies do Chrome + cliente padrão |
| 4 | cookies do Chrome + cliente `web_safari` |
| ... | (mesma coisa para Edge, Brave, Opera, Vivaldi, Chromium) |
| penúltima | sem cookies + cliente `android` |
| última | sem cookies + cliente padrão |

Ele **para na primeira estratégia que expor áudio em português**. Se nenhuma
expuser, ele te diz quais idiomas existem no vídeo.

Isso é importante: os IDs de formato (`94-4`, `96-8`...) **mudam de estratégia
para estratégia**. Por isso o download é feito com exatamente as mesmas opções
usadas na sondagem que deu certo — um erro clássico é sondar de um jeito e baixar
de outro, e aí o ID não existe mais.

**Etapa 3 — Escolhe os formatos.**
Duas possibilidades, nesta prioridade:

- **Caminho A (ideal):** o YouTube expõe uma faixa de **áudio separada** em
  `[pt-BR]` (formato "audio only"). O programa combina
  `melhor vídeo (maior resolução) + melhor áudio pt-BR` → `-f 137+140-1`, por
  exemplo. Aqui dá para pegar 1080p, 1440p, 4K etc.
- **Caminho B:** o áudio pt-BR só existe **já colado ao vídeo** dentro do
  manifesto HLS (`m3u8`) — foi o caso dos formatos `91-8`, `96-8` que apareceram
  no seu teste do Linux. O programa então pega o `m3u8` de **maior resolução** com
  a marca `[pt-BR]`.

**Etapa 4 — Baixa, mescla e confere.**
Baixa com 8 fragmentos em paralelo, mescla vídeo+áudio com o `ffmpeg`, embute os
metadados e, no fim, roda o `ffprobe` para **mostrar as trilhas que ficaram dentro
do arquivo** — é a sua prova de que a dublagem realmente entrou (você verá
`lang=por`).

O nome do arquivo sai assim:

```
Titulo do vídeo [IDdoVídeo] [pt-BR].mp4
```

---

## 3. Requisitos (e o que já está instalado na sua máquina)

Verificado nesta máquina (Windows 10 Pro, usuário `Hugo`) em 29/07/2026:

| Requisito | Situação | Observação |
|-----------|----------|-----------|
| Python 3.9+ | ✅ 3.14.0 e 3.13.7 | `py -3` → 3.14.0 |
| `yt-dlp` | ✅ 2026.07.04 | instalado nos dois Pythons |
| `yt-dlp-ejs` | ✅ 0.8.0 | resolve os desafios de JS (obrigatório na versão pip) |
| `ffmpeg` | ✅ `C:\ffmpeg\bin\ffmpeg.exe` | mescla vídeo + áudio |
| Runtime de JS | ✅ `node` v22.19.0 | **não precisa instalar o Deno**: o yt-dlp aceita `node` |
| Firefox | ✅ funciona para cookies | **44 cookies lidos com sucesso** |
| Chrome / Edge / Brave | ⚠️ falham | veja abaixo |

> ### Atenção — o ponto mais importante no Windows
> No Linux o `--cookies-from-browser chrome` funciona. **No Windows não.**
> O Chrome (127+) e o Edge usam *App-Bound Encryption* e o Brave usa DPAPI de um
> jeito que o `yt-dlp` não consegue abrir. Nesta máquina os erros foram:
>
> - Chrome/Edge: `Could not copy Chrome cookie database`
> - Brave: `Failed to decrypt with DPAPI`
>
> **Use o Firefox** como fonte de cookies no Windows. É o caminho que funciona, e
> ele funciona até com o navegador aberto. O programa já tenta o Firefox primeiro.
>
> Você **não precisa** estar logado no YouTube; bastam os cookies anônimos de
> sessão. Mas se abrir o YouTube no Firefox pelo menos uma vez, melhor ainda.

---

## 4. Instalação — passo a passo

Na sua máquina **tudo já está instalado e testado** — você pode ir direto para a
seção 5. Os passos abaixo servem para reinstalar, ou para montar isso em outro PC.

### Passo 4.1 — Python

1. Baixe em <https://www.python.org/downloads/windows/>.
2. Na primeira tela do instalador, **marque `Add python.exe to PATH`**.
3. Confira abrindo o PowerShell e rodando:

```bash
py -3 --version
```

### Passo 4.2 — ffmpeg

No PowerShell:

```bash
winget install Gyan.FFmpeg
```

Depois **feche e reabra o PowerShell** (para o PATH atualizar) e confira:

```bash
ffmpeg -version
```

### Passo 4.3 — Runtime de JavaScript

Se você já tem o **Node.js** (`node --version` funciona), **está resolvido** — o
programa detecta e usa o `node` automaticamente. Se não tiver nenhum:

```bash
winget install DenoLand.Deno
```

### Passo 4.4 — yt-dlp e o solucionador de desafios

```bash
py -3 -m pip install --upgrade yt-dlp yt-dlp-ejs
```

> O `yt-dlp-ejs` é fácil de esquecer e causa um erro confuso. Sem ele, o yt-dlp
> avisa `Remote component challenge solver script (node) was skipped` e devolve
> **só imagens**. Foi exatamente o que aconteceu aqui antes de instalá-lo.

### Passo 4.5 — Firefox

Instale o Firefox (se ainda não tiver), abra-o e visite o YouTube uma vez.

```bash
winget install Mozilla.Firefox
```

### Passo 4.6 — Conferir tudo de uma vez

Dê **duplo clique** em `3-Checar-Ambiente.bat`, ou rode:

```bash
py -3 C:\Projeto_Claude\Youtu_Baixar\baixar_dublado.py --checar
```

Você deve terminar com a linha:
`[ok]    Ambiente pronto para baixar dublagens em pt-BR.`

---

## 5. Como usar — o jeito fácil (duplo clique)

1. Abra a pasta `C:\Projeto_Claude\Youtu_Baixar`.
2. Dê **duplo clique** em **`2-Baixar-Video.bat`**.
3. Cole a URL do vídeo (clique com o **botão direito** dentro da janela preta
   para colar) e pressione **ENTER**.
4. Acompanhe o progresso. Ao terminar, o arquivo estará em
   `C:\Projeto_Claude\Youtu_Baixar\vídeos`.

Os três atalhos:

| Arquivo | Para quê |
|---------|----------|
| `1-Instalar-Requisitos.bat` | instala/atualiza `yt-dlp` + `yt-dlp-ejs` e checa o resto |
| `2-Baixar-Video.bat` | pede a URL e baixa dublado em pt-BR |
| `3-Checar-Ambiente.bat` | só o diagnóstico |

---

## 6. Como usar — pelo terminal (todas as opções)

Abra o PowerShell e vá para a pasta:

```bash
cd C:\Projeto_Claude\Youtu_Baixar
```

### Uso básico

```bash
py -3 baixar_dublado.py "https://www.youtube.com/watch?v=GtOGurrUPmQ"
```

> **Sempre coloque a URL entre aspas duplas.** URLs do YouTube têm `&` (por
> exemplo `...&list=...&index=2`), e sem as aspas o PowerShell corta a URL ali.

### Ver o que existe antes de baixar (equivale ao seu `-F`)

```bash
py -3 baixar_dublado.py --listar "URL_DO_VIDEO"
```

### Tabela de opções

| Opção | O que faz |
|-------|-----------|
| `--listar` | mostra os formatos dublados e **não baixa** |
| `--simular` | faz tudo, menos gravar o arquivo |
| `--checar` | diagnóstico do ambiente |
| `--saida "PASTA"` | muda a pasta de destino (padrão: `.\vídeos`) |
| `--navegador firefox` | fonte dos cookies. Aceita lista (`firefox,chrome`), perfil (`firefox:default-release`) ou `nenhum` |
| `--cookies arq.txt` | usa um arquivo `cookies.txt` em vez do navegador |
| `--idiomas pt-BR,pt` | idiomas aceitos, em ordem de preferência |
| `--max-altura 1080` | limita a resolução (útil para não baixar 1,2 GB) |
| `--codec h264` | força H.264 — máxima compatibilidade com TVs e editores |
| `--container mp4` | força o container final (`auto`, `mp4`, `mkv`, `webm`) |
| `--legendas` | baixa e embute legendas em português |
| `--playlist` | baixa a **playlist inteira** (o padrão é só o vídeo da URL) |
| `--aceitar-original` | se não houver dublagem pt-BR, baixa no idioma original |
| `--arquivo lista.txt` | lê várias URLs de um arquivo (uma por linha) |
| `--extra ...` | tudo depois disso vai cru para o `yt-dlp` (deve ser a **última** opção, com a URL antes) |

### Exemplos práticos

Limitar a 1080p (economiza espaço e tempo):

```bash
py -3 baixar_dublado.py --max-altura 1080 "URL_DO_VIDEO"
```

Máxima compatibilidade (H.264 em MP4 — toca em qualquer TV/celular):

```bash
py -3 baixar_dublado.py --codec h264 --container mp4 "URL_DO_VIDEO"
```

Vídeo dublado **com legendas** em português embutidas:

```bash
py -3 baixar_dublado.py --legendas "URL_DO_VIDEO"
```

Baixar uma playlist inteira dublada:

```bash
py -3 baixar_dublado.py --playlist "https://www.youtube.com/playlist?list=PLyQSN7X0ro203puVhQsmCj9qhlFQ-As8e"
```

Vários vídeos de uma vez — crie um `lista.txt` com uma URL por linha:

```bash
py -3 baixar_dublado.py --arquivo lista.txt
```

Salvar em outro disco:

```bash
py -3 baixar_dublado.py --saida "D:\Videos Dublados" "URL_DO_VIDEO"
```

Se o vídeo não tiver dublagem e você quiser mesmo assim:

```bash
py -3 baixar_dublado.py --aceitar-original "URL_DO_VIDEO"
```

---

## 7. Teste real já executado

O programa foi testado com o vídeo que você pediu:

```
https://www.youtube.com/watch?v=GtOGurrUPmQ&list=PLyQSN7X0ro203puVhQsmCj9qhlFQ-As8e&index=2
```

**Resultado:**

| Item | Valor |
|------|-------|
| Título | 8.01x - Lect 1 - Powers of 10, Units, Dimensions, Uncertainties, Scaling Arguments |
| Canal | Lectures by Walter Lewin. They will make you ♥ Physics. |
| Duração | 38 min 1 s |
| Estratégia que funcionou | cookies do Firefox + cliente padrão (1ª tentativa) |
| Idiomas de áudio no vídeo | en-US, fr-FR, es-US, de-DE, hi, **pt-BR**, ja, id, it |
| Formato escolhido | `94-4` — 640x480, 30 fps, H.264 + AAC, 628 kbps (HLS já mesclado) |
| Arquivo gerado | `8.01x - Lect 1 - Powers of 10, Units, Dimensions, Uncertainties, Scaling Arguments [GtOGurrUPmQ] [pt-BR].mp4` |
| Tamanho | 89,8 MiB |
| Conferência do `ffprobe` | `audio aac 2ch lang=por` · `video h264 640x480` |

O arquivo está em `C:\Projeto_Claude\Youtu_Baixar\vídeos`.

Note que a URL trazia `&list=...&index=2`: o programa usa `--no-playlist` por
padrão, então baixou **só esse vídeo**, e não a playlist toda.

---

## 8. Sobre "qualidade máxima": o que esperar

O programa sempre pega a maior resolução **que tenha áudio em pt-BR**. Mas o
limite é do vídeo, não do programa:

- **O vídeo do teste é antigo e 4:3.** A maior resolução que existe nele é
  640x480. Não há 1080p para baixar — o `--listar` mostra isso: `91-4` (144p),
  `92-4` (240p), `93-4` (360p) e `94-4` (480p). O programa pegou o `94-4`.
- Em vídeos modernos, o áudio pt-BR normalmente vem **como faixa separada**, e aí
  o programa combina com o melhor vídeo disponível (1080p, 1440p, 4K...) — o
  "Caminho A" da seção 2.
- Quando o áudio pt-BR só existe dentro do HLS (como no teste, e como no seu
  `96-8` do Linux), a resolução máxima da dublagem pode ser **menor** que a do
  vídeo em inglês. Isso é uma limitação do YouTube. O programa avisa qual formato
  escolheu, e o `--listar` mostra todas as opções dubladas.

**Dica:** vídeos com dublagem automática do YouTube em geral trazem `[pt-BR]`.
Se o vídeo não tem dublagem nenhuma, o programa diz isso claramente e lista os
idiomas que existem — em vez de baixar em inglês sem avisar.

---

## 9. Solução de problemas

### "Este vídeo NÃO oferece faixa de áudio em português"
O vídeo realmente não tem dublagem. O programa lista os idiomas disponíveis.
Use `--aceitar-original` se quiser baixar no idioma original.

### "Nenhum runtime de JS (deno/node/bun)"
Instale o Deno: `winget install DenoLand.Deno`. Reabra o PowerShell depois.

### Só apareceram formatos de imagem / "Only images are available"
Falta o `yt-dlp-ejs`:

```bash
py -3 -m pip install --upgrade yt-dlp-ejs
```

### "Could not copy Chrome cookie database" / "Failed to decrypt with DPAPI"
É o Chrome/Edge/Brave no Windows (App-Bound Encryption / DPAPI). **Use o
Firefox** — o programa já tenta o Firefox primeiro, então essas mensagens no meio
do caminho são inofensivas. Se quiser silenciá-las:

```bash
py -3 baixar_dublado.py --navegador firefox "URL_DO_VIDEO"
```

Se você faz questão do Chrome, exporte um `cookies.txt` com uma extensão de
navegador e use `--cookies cookies.txt`.

### "This video is DRM protected"
Aparece quando o cliente `tv` é usado. O programa não usa esse cliente, então
ignore — mas se surgir, significa que aquela via específica está bloqueada, e a
sondagem já parte para a próxima estratégia sozinha.

### "requires a GVS PO Token which was not provided"
É a barreira que você já conhece. Solução: cookies do Firefox (o programa faz).
Se persistir, abra o YouTube no Firefox, dê play em qualquer vídeo, e tente de
novo.

### "SABR-only streaming experiment"
O YouTube está forçando o protocolo SABR nessa sessão. As estratégias com cookies
costumam contornar. Se não, atualize o yt-dlp (seção 10) — esse é um jogo de
gato e rato, e o yt-dlp é atualizado com frequência.

### "HTTP Error 403"
Cookies velhos. Abra o Firefox, acesse o YouTube e rode de novo.

### O download começa e para no meio
Já há 10 tentativas e 20 por fragmento configuradas. Se a rede estiver instável,
reduza o paralelismo:

```bash
py -3 baixar_dublado.py "URL_DO_VIDEO" --extra --concurrent-fragments 2
```

(a URL precisa vir antes do `--extra`, porque essa opção repassa tudo o que vem
depois dela direto para o `yt-dlp`)

### Erro de acentos no terminal
Rode antes: `$env:PYTHONUTF8="1"` (os `.bat` já cuidam disso com `chcp 65001`).

### `py` não é reconhecido
O Python não está no PATH. Reinstale marcando `Add python.exe to PATH`.

---

## 10. Manutenção (manter atualizado)

O YouTube muda as travas com frequência. Quando algo parar de funcionar, **o
primeiro passo é sempre atualizar**:

```bash
py -3 -m pip install --upgrade yt-dlp yt-dlp-ejs
```

Ou simplesmente dê duplo clique em `1-Instalar-Requisitos.bat`.

Vale atualizar mais ou menos uma vez por mês, ou sempre que aparecer um erro novo.

---

## 11. Arquivos do projeto

```
C:\Projeto_Claude\Youtu_Baixar\
├── baixar_dublado.py          <- o programa
├── MANUAL.md                  <- este manual
├── 1-Instalar-Requisitos.bat  <- instala/atualiza tudo
├── 2-Baixar-Video.bat         <- pede a URL e baixa (duplo clique)
├── 3-Checar-Ambiente.bat      <- diagnóstico
├── teste_selecao.py           <- testa a lógica de escolha de formatos (sem rede)
└── vídeos\                    <- os vídeos baixados ficam aqui
```

Se algum dia você mexer no `baixar_dublado.py`, rode o teste para conferir que a
escolha de formatos continua correta (ele não usa internet):

```bash
py -3 C:\Projeto_Claude\Youtu_Baixar\teste_selecao.py
```

Ele deve terminar com `TODOS OS TESTES PASSARAM`.

---

### Nota legal

Baixe apenas conteúdo que você tem direito de baixar: vídeos próprios, material
com licença livre (o caso das aulas do MIT usadas no teste), ou vídeos cujo
download é permitido pelo detentor dos direitos. Os Termos de Serviço do YouTube
restringem downloads não autorizados — a responsabilidade pelo uso é sua.
