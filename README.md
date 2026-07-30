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
