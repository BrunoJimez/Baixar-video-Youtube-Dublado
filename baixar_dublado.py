#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
baixar_dublado.py
=================

Baixa vídeos do YouTube com a faixa de áudio DUBLADA em português brasileiro
(pt-BR), sempre na melhor qualidade de vídeo disponível.

Como funciona (a mesma lógica que voce validou no Linux Mint, automatizada):

  1. Descobre o yt-dlp, o ffmpeg e um runtime de JavaScript (deno/node/bun).
  2. Sonda o video com "yt-dlp -J" tentando varias estrategias em sequencia
     (cookies do navegador -> clientes alternativos -> sem cookies), porque a
     lista de formatos que o YouTube devolve depende de conseguir passar pela
     barreira do PO Token / SABR.
  3. Na primeira estrategia que expuser audio em portugues, escolhe:
        a) melhor video-only  +  melhor audio-only [pt-BR]        (ideal)
        b) ou o melhor formato ja mesclado (HLS/m3u8) marcado [pt-BR]
  4. Baixa com as MESMAS opcoes usadas na sondagem (os IDs de formato mudam de
     estrategia para estrategia) e mescla em MP4/MKV com o ffmpeg.

Uso rapido:
    py -3 baixar_dublado.py "https://www.youtube.com/watch?v=XXXX"

Veja MANUAL.md para o passo a passo completo.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# --------------------------------------------------------------------------- #
# Configuracao padrao
# --------------------------------------------------------------------------- #

RAIZ = Path(__file__).resolve().parent
PASTA_SAIDA_PADRAO = RAIZ / "vídeos"

# Ordem de preferencia dos codigos de idioma considerados "dublagem brasileira".
IDIOMAS_PADRAO = ["pt-BR", "pt", "pt-PT"]

# No Windows o Firefox e de longe o mais confiavel: Chrome/Edge/Brave usam
# App-Bound Encryption / DPAPI e normalmente falham ao ter os cookies lidos.
NAVEGADORES_PADRAO = ["firefox", "chrome", "edge", "brave", "opera", "vivaldi", "chromium"]

# Runtimes de JS aceitos pelo yt-dlp, em ordem de prioridade.
RUNTIMES_JS = ["deno", "node", "bun", "quickjs"]


# --------------------------------------------------------------------------- #
# Utilidades de terminal
# --------------------------------------------------------------------------- #

def _preparar_console() -> None:
    """Evita UnicodeEncodeError no console do Windows (cp1252)."""
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def titulo(texto: str) -> None:
    print("\n" + "=" * 74)
    print(texto)
    print("=" * 74)


def info(texto: str) -> None:
    print(f"  [ok]    {texto}")


def aviso(texto: str) -> None:
    print(f"  [aviso] {texto}")


def erro(texto: str) -> None:
    print(f"  [ERRO]  {texto}")


# --------------------------------------------------------------------------- #
# Deteccao do ambiente
# --------------------------------------------------------------------------- #

def encontrar_ytdlp() -> list[str] | None:
    """Retorna o comando base do yt-dlp (modulo do Python atual ou executavel)."""
    try:
        import yt_dlp  # noqa: F401
        return [sys.executable, "-m", "yt_dlp"]
    except ImportError:
        pass
    exe = shutil.which("yt-dlp")
    return [exe] if exe else None


def tem_ejs() -> bool:
    """O pacote yt-dlp-ejs traz o script que resolve os desafios de JS."""
    try:
        import yt_dlp_ejs  # noqa: F401
        return True
    except ImportError:
        return False


def runtimes_js_disponiveis() -> list[str]:
    return [r for r in RUNTIMES_JS if shutil.which(r)]


def versao_ytdlp(base: list[str]) -> str:
    try:
        r = subprocess.run(base + ["--version"], capture_output=True, text=True, timeout=120)
        return r.stdout.strip() or "?"
    except Exception:
        return "?"


def checar_ambiente() -> int:
    """Modo --checar: diagnostico completo da maquina."""
    titulo("DIAGNOSTICO DO AMBIENTE")
    problemas = 0

    print(f"  Python           : {sys.version.split()[0]}  ({sys.executable})")
    if sys.version_info < (3, 9):
        erro("Python 3.9+ e necessario.")
        problemas += 1

    base = encontrar_ytdlp()
    if base:
        info(f"yt-dlp           : {versao_ytdlp(base)}   via {' '.join(base[1:]) or base[0]}")
    else:
        erro("yt-dlp NAO encontrado.  Instale com:  py -3 -m pip install -U yt-dlp")
        problemas += 1

    if tem_ejs():
        info("yt-dlp-ejs       : instalado (resolve os desafios de JS do YouTube)")
    else:
        aviso("yt-dlp-ejs NAO instalado -> formatos podem faltar.")
        aviso("  Instale com:  py -3 -m pip install -U yt-dlp-ejs")

    rt = runtimes_js_disponiveis()
    if rt:
        info(f"Runtime de JS    : {', '.join(rt)}")
    else:
        erro("Nenhum runtime de JS (deno/node/bun). Sem ele o YouTube esconde formatos.")
        erro("  Instale o Deno:  winget install DenoLand.Deno    (ou Node.js)")
        problemas += 1

    ff = shutil.which("ffmpeg")
    if ff:
        info(f"ffmpeg           : {ff}")
    else:
        erro("ffmpeg NAO encontrado (necessario para mesclar video + audio).")
        erro("  Instale com:  winget install Gyan.FFmpeg")
        problemas += 1

    print()
    print("  Navegadores com perfil detectado (fonte dos cookies):")
    local = os.environ.get("LOCALAPPDATA", "")
    roaming = os.environ.get("APPDATA", "")
    perfis = {
        "firefox": Path(roaming) / "Mozilla" / "Firefox" / "Profiles",
        "chrome": Path(local) / "Google" / "Chrome" / "User Data",
        "edge": Path(local) / "Microsoft" / "Edge" / "User Data",
        "brave": Path(local) / "BraveSoftware" / "Brave-Browser" / "User Data",
        "vivaldi": Path(local) / "Vivaldi" / "User Data",
        "chromium": Path(local) / "Chromium" / "User Data",
    }
    for nome, caminho in perfis.items():
        marca = "presente" if caminho.exists() else "ausente "
        extra = ""
        if nome != "firefox" and caminho.exists():
            extra = "  (no Windows a leitura de cookies costuma falhar)"
        print(f"    - {nome:<9} {marca}{extra}")

    print()
    if problemas:
        erro(f"{problemas} problema(s) bloqueante(s) encontrado(s). Veja MANUAL.md secao 2.")
    else:
        info("Ambiente pronto para baixar dublagens em pt-BR.")
    return 1 if problemas else 0


# --------------------------------------------------------------------------- #
# Estrategias de extracao
# --------------------------------------------------------------------------- #

class Estrategia:
    """Um conjunto de opcoes de extracao a ser tentado."""

    def __init__(self, descricao: str, cookies_de: str | None = None,
                 cliente: str | None = None):
        self.descricao = descricao
        self.cookies_de = cookies_de
        self.cliente = cliente

    def argumentos(self) -> list[str]:
        args: list[str] = []
        if self.cookies_de:
            args += ["--cookies-from-browser", self.cookies_de]
        if self.cliente:
            args += ["--extractor-args", f"youtube:player_client={self.cliente}"]
        return args


def montar_estrategias(navegadores: list[str], arquivo_cookies: str | None) -> list[Estrategia]:
    est: list[Estrategia] = []
    if arquivo_cookies:
        # Tratado fora daqui (opcao global), mas mantemos as variacoes de cliente.
        est.append(Estrategia("arquivo de cookies + cliente padrao"))
        est.append(Estrategia("arquivo de cookies + cliente web_safari", cliente="web_safari"))
        est.append(Estrategia("arquivo de cookies + cliente web", cliente="web"))
    else:
        for nav in navegadores:
            est.append(Estrategia(f"cookies do {nav} + cliente padrao", cookies_de=nav))
            est.append(Estrategia(f"cookies do {nav} + cliente web_safari",
                                  cookies_de=nav, cliente="web_safari"))
    # Ultimos recursos, sem cookies.
    est.append(Estrategia("sem cookies + cliente android", cliente="android"))
    est.append(Estrategia("sem cookies + cliente padrao"))
    return est


# --------------------------------------------------------------------------- #
# Sondagem e escolha de formatos
# --------------------------------------------------------------------------- #

def normalizar_idioma(valor: object) -> str:
    return str(valor or "").replace("_", "-").strip().lower()


def pontuar_idioma(idioma: object, desejados: list[str]) -> int | None:
    """Menor = melhor. None quando o idioma nao serve."""
    alvo = normalizar_idioma(idioma)
    if not alvo:
        return None
    for i, d in enumerate(desejados):
        dn = normalizar_idioma(d)
        if alvo == dn:
            return i
    # pt-BR pedido, formato veio como "pt" ou "pt-br-x-dub": aceita pela raiz.
    raiz_desejadas = {normalizar_idioma(d).split("-")[0] for d in desejados}
    if alvo.split("-")[0] in raiz_desejadas:
        return len(desejados)
    return None


def eh_video(f: dict) -> bool:
    return (f.get("vcodec") or "none") != "none"


def eh_audio(f: dict) -> bool:
    return (f.get("acodec") or "none") != "none"


def eh_imagem(f: dict) -> bool:
    return (f.get("vcodec") or "") == "images" or f.get("ext") == "mhtml"


def num(v: object) -> float:
    try:
        return float(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


def sondar(base: list[str], url: str, est: Estrategia, globais: list[str],
           tempo_limite: int) -> tuple[dict | None, str]:
    """Roda 'yt-dlp -J' e devolve (info_json, mensagem_de_erro)."""
    cmd = base + globais + est.argumentos() + ["-J", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=tempo_limite)
    except subprocess.TimeoutExpired:
        return None, "tempo limite excedido"
    saida = (r.stdout or "").strip()
    if saida.startswith("\ufeff"):
        saida = saida[1:]
    if not saida:
        linhas = [l for l in (r.stderr or "").splitlines() if "ERROR" in l or "error" in l]
        return None, (linhas[-1].strip() if linhas else "sem resposta do yt-dlp")
    try:
        return json.loads(saida), ""
    except json.JSONDecodeError:
        return None, "resposta do yt-dlp nao e um JSON valido"


def idiomas_de_audio(dados: dict) -> list[str]:
    langs: list[str] = []
    for f in dados.get("formats") or []:
        if eh_imagem(f) or not eh_audio(f):
            continue
        lang = f.get("language")
        if lang and lang not in langs:
            langs.append(str(lang))
    return langs


def escolher(dados: dict, idiomas: list[str], max_altura: int | None,
             codec: str) -> dict | None:
    """
    Escolhe a melhor combinacao com audio no idioma pedido.

    Devolve dict com: modo, spec, resumo e detalhes dos formatos.
    """
    formatos = [f for f in (dados.get("formats") or []) if not eh_imagem(f)]

    def altura_ok(f: dict) -> bool:
        if max_altura is None:
            return True
        return num(f.get("height")) <= max_altura

    def codec_ok(f: dict) -> bool:
        vc = str(f.get("vcodec") or "")
        if codec == "h264":
            return vc.startswith(("avc1", "h264"))
        if codec == "vp9":
            return vc.startswith("vp")
        if codec == "av1":
            return vc.startswith("av01")
        return True

    # ---- Caminho A: audio-only no idioma + melhor video-only -------------- #
    audios = []
    for f in formatos:
        if eh_audio(f) and not eh_video(f):
            p = pontuar_idioma(f.get("language"), idiomas)
            if p is not None:
                audios.append((p, f))
    videos = [f for f in formatos
              if eh_video(f) and not eh_audio(f) and altura_ok(f) and codec_ok(f)]
    if not videos:  # o filtro de codec pode ter zerado a lista
        videos = [f for f in formatos if eh_video(f) and not eh_audio(f) and altura_ok(f)]

    if audios and videos:
        audios.sort(key=lambda pf: (pf[0], -num(pf[1].get("abr")), -num(pf[1].get("tbr"))))
        melhor_audio = audios[0][1]
        videos.sort(key=lambda f: (-num(f.get("height")), -num(f.get("fps")), -num(f.get("tbr"))))
        melhor_video = videos[0]
        return {
            "modo": "separado",
            "spec": f"{melhor_video['format_id']}+{melhor_audio['format_id']}",
            "video": melhor_video,
            "audio": melhor_audio,
            "idioma": melhor_audio.get("language"),
        }

    # ---- Caminho B: formato ja mesclado (HLS) no idioma -------------------- #
    mesclados = []
    for f in formatos:
        if eh_audio(f) and eh_video(f) and altura_ok(f):
            p = pontuar_idioma(f.get("language"), idiomas)
            if p is not None:
                mesclados.append((p, f))
    if mesclados:
        mesclados.sort(key=lambda pf: (pf[0], -num(pf[1].get("height")),
                                       -num(pf[1].get("tbr"))))
        f = mesclados[0][1]
        return {
            "modo": "mesclado",
            "spec": str(f["format_id"]),
            "video": f,
            "audio": f,
            "idioma": f.get("language"),
        }

    return None


def escolher_original(dados: dict, max_altura: int | None) -> dict | None:
    """Reserva para --aceitar-original: melhor qualidade em qualquer idioma."""
    formatos = [f for f in (dados.get("formats") or []) if not eh_imagem(f)]

    def altura_ok(f: dict) -> bool:
        return max_altura is None or num(f.get("height")) <= max_altura

    videos = [f for f in formatos if eh_video(f) and not eh_audio(f) and altura_ok(f)]
    audios = [f for f in formatos if eh_audio(f) and not eh_video(f)]
    if videos and audios:
        videos.sort(key=lambda f: (-num(f.get("height")), -num(f.get("fps")), -num(f.get("tbr"))))
        audios.sort(key=lambda f: (-num(f.get("abr")), -num(f.get("tbr"))))
        return {"modo": "separado", "spec": f"{videos[0]['format_id']}+{audios[0]['format_id']}",
                "video": videos[0], "audio": audios[0], "idioma": audios[0].get("language")}
    mesclados = [f for f in formatos if eh_audio(f) and eh_video(f) and altura_ok(f)]
    if mesclados:
        mesclados.sort(key=lambda f: (-num(f.get("height")), -num(f.get("tbr"))))
        f = mesclados[0]
        return {"modo": "mesclado", "spec": str(f["format_id"]),
                "video": f, "audio": f, "idioma": f.get("language")}
    return None


def escolher_container(escolha: dict, container: str) -> str:
    if container != "auto":
        return container
    if escolha["modo"] == "mesclado":
        return "mp4"
    ev = escolha["video"].get("ext")
    ea = escolha["audio"].get("ext")
    if ev == ea and ev in ("mp4", "webm"):
        return ev
    if ea in ("m4a", "mp4") and ev == "mp4":
        return "mp4"
    return "mkv"  # mistura de familias: mkv aceita tudo sem recodificar


def tamanho_legivel(f: dict) -> str:
    b = f.get("filesize") or f.get("filesize_approx")
    if not b:
        return "?"
    v = float(b)
    for u in ("B", "KiB", "MiB", "GiB"):
        if v < 1024 or u == "GiB":
            return f"{v:.1f} {u}"
        v /= 1024
    return "?"


def descrever(f: dict) -> str:
    partes = [str(f.get("format_id"))]
    if f.get("height"):
        partes.append(f"{f.get('width')}x{f.get('height')}")
    if f.get("fps"):
        partes.append(f"{int(num(f.get('fps')))}fps")
    vc, ac = f.get("vcodec") or "", f.get("acodec") or ""
    if vc and vc != "none":
        partes.append(vc)
    if ac and ac != "none":
        partes.append(ac)
    if f.get("tbr"):
        partes.append(f"{int(num(f.get('tbr')))}k")
    partes.append(f"~{tamanho_legivel(f)}")
    partes.append(str(f.get("protocol") or ""))
    return "  ".join(p for p in partes if p)


# --------------------------------------------------------------------------- #
# Download
# --------------------------------------------------------------------------- #

def baixar(base: list[str], url: str, est: Estrategia, globais: list[str],
           escolha: dict, pasta: Path, container: str, legendas: bool,
           simular: bool, extras: list[str]) -> tuple[int, str | None]:
    pasta.mkdir(parents=True, exist_ok=True)
    marca = str(escolha.get("idioma") or "audio")
    modelo = str(pasta / f"%(title).120B [%(id)s] [{marca}].%(ext)s")

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
        arq_caminho = tmp.name

    cmd = base + globais + est.argumentos() + [
        "-f", escolha["spec"],
        "-o", modelo,
        "--merge-output-format", container,
        "--no-mtime",
        "--concurrent-fragments", "8",
        "--retries", "10",
        "--fragment-retries", "20",
        "--embed-metadata",
        "--print-to-file", "after_move:filepath", arq_caminho,
    ]
    if legendas:
        cmd += ["--write-subs", "--write-auto-subs",
                "--sub-langs", "pt-BR,pt,pt-orig", "--embed-subs"]
    if simular:
        cmd += ["--simulate"]
    cmd += extras + [url]

    print()
    print("  Comando executado:")
    print("    " + " ".join(f'"{c}"' if " " in c else c for c in cmd))
    print()

    ret = subprocess.run(cmd).returncode

    caminho_final = None
    try:
        texto = Path(arq_caminho).read_text(encoding="utf-8", errors="replace").strip()
        if texto:
            caminho_final = texto.splitlines()[-1].strip()
    except Exception:
        pass
    finally:
        try:
            os.unlink(arq_caminho)
        except OSError:
            pass
    return ret, caminho_final


def conferir_arquivo(caminho: str) -> None:
    """Mostra as trilhas do arquivo final usando ffprobe, se disponivel."""
    ffprobe = shutil.which("ffprobe")
    if not ffprobe or not Path(caminho).exists():
        return
    cmd = [ffprobe, "-v", "error", "-show_entries",
           "stream=index,codec_type,codec_name,width,height,channels:stream_tags=language",
           "-of", "json", caminho]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
        dados = json.loads(r.stdout or "{}")
    except Exception:
        return
    print("  Trilhas dentro do arquivo final:")
    for s in dados.get("streams", []):
        tipo = s.get("codec_type")
        desc = [f"#{s.get('index')}", str(tipo), str(s.get("codec_name"))]
        if tipo == "video" and s.get("width"):
            desc.append(f"{s.get('width')}x{s.get('height')}")
        if tipo == "audio" and s.get("channels"):
            desc.append(f"{s.get('channels')}ch")
        lang = (s.get("tags") or {}).get("language")
        if lang:
            desc.append(f"lang={lang}")
        print("    - " + "  ".join(desc))


# --------------------------------------------------------------------------- #
# Fluxo principal por URL
# --------------------------------------------------------------------------- #

def processar(url: str, args: argparse.Namespace, base: list[str],
              globais: list[str]) -> bool:
    titulo(f"VIDEO: {url}")

    estrategias = montar_estrategias(args.navegador, args.cookies)
    dados_ok: dict | None = None
    est_ok: Estrategia | None = None
    escolha: dict | None = None
    reserva: tuple[dict, Estrategia] | None = None

    for est in estrategias:
        print(f"\n  -> Tentando: {est.descricao}")
        dados, msg = sondar(base, url, est, globais, args.tempo_limite)
        if dados is None:
            aviso(f"falhou: {msg}")
            continue

        langs = idiomas_de_audio(dados)
        info(f"formatos obtidos. Idiomas de audio: {', '.join(langs) or 'nenhum'}")

        cand = escolher(dados, args.idiomas, args.max_altura, args.codec)
        if cand:
            info(f"dublagem encontrada: [{cand['idioma']}]")
            dados_ok, est_ok, escolha = dados, est, cand
            break

        if reserva is None and escolher_original(dados, args.max_altura):
            reserva = (dados, est)
        aviso(f"esta estrategia nao expos audio em {'/'.join(args.idiomas)}; "
              "tentando a proxima")

    if escolha is None:
        if reserva and args.aceitar_original:
            dados_ok, est_ok = reserva
            escolha = escolher_original(dados_ok, args.max_altura)
            aviso("Sem dublagem em portugues. Baixando o audio original "
                  "(--aceitar-original ativo).")
        elif reserva:
            dados_ok, est_ok = reserva
            erro("Este video NAO oferece faixa de audio em portugues "
                 f"({', '.join(args.idiomas)}).")
            print(f"      Idiomas disponiveis: {', '.join(idiomas_de_audio(dados_ok)) or 'nenhum'}")
            print("      Use --aceitar-original para baixar no idioma original.")
            return False
        else:
            erro("Nao foi possivel obter nenhum formato de audio/video para este video.")
            print("      Rode 'py -3 baixar_dublado.py --checar' e veja MANUAL.md secao 6.")
            return False

    assert dados_ok is not None and est_ok is not None

    # ---- Relatorio da escolha -------------------------------------------- #
    print()
    print(f"  Titulo   : {dados_ok.get('title')}")
    dur = int(num(dados_ok.get("duration")))
    if dur:
        print(f"  Duracao  : {dur // 60}min {dur % 60}s")
    print(f"  Canal    : {dados_ok.get('uploader') or '?'}")
    print(f"  Idioma   : {escolha['idioma']}  "
          f"({'faixa separada' if escolha['modo'] == 'separado' else 'HLS ja mesclado'})")
    print(f"  Video    : {descrever(escolha['video'])}")
    if escolha["modo"] == "separado":
        print(f"  Audio    : {descrever(escolha['audio'])}")
    print(f"  Formato  : -f {escolha['spec']}")

    if args.listar:
        print()
        print("  Formatos com audio em portugues disponiveis:")
        for f in dados_ok.get("formats") or []:
            if eh_imagem(f) or not eh_audio(f):
                continue
            if pontuar_idioma(f.get("language"), args.idiomas) is not None:
                print(f"    - {descrever(f)}   [{f.get('language')}]")
        print("\n  (modo --listar: nada foi baixado)")
        return True

    container = escolher_container(escolha, args.container)
    print(f"  Saida    : {args.saida}  (container {container})")

    ret, caminho = baixar(base, url, est_ok, globais, escolha, args.saida,
                          container, args.legendas, args.simular, args.extra)

    print()
    if ret != 0:
        erro(f"yt-dlp terminou com codigo {ret}. Veja as mensagens acima.")
        return False
    if args.simular:
        info("Simulacao concluida (nada foi gravado).")
        return True
    if caminho:
        info(f"Arquivo salvo em: {caminho}")
        tam = Path(caminho).stat().st_size if Path(caminho).exists() else 0
        if tam:
            print(f"          Tamanho: {tam / (1024 * 1024):.1f} MiB")
        conferir_arquivo(caminho)
    else:
        info(f"Download concluido. Confira a pasta: {args.saida}")
    return True


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def montar_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="baixar_dublado.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Baixa videos do YouTube com a dublagem em portugues brasileiro "
                    "na melhor qualidade disponivel.",
        epilog="""Exemplos:
  py -3 baixar_dublado.py --checar
  py -3 baixar_dublado.py "https://www.youtube.com/watch?v=GtOGurrUPmQ"
  py -3 baixar_dublado.py --listar "URL"
  py -3 baixar_dublado.py --navegador chrome --max-altura 1080 "URL"
  py -3 baixar_dublado.py --arquivo lista.txt --saida "D:\\Videos"
  py -3 baixar_dublado.py --playlist "URL_DA_PLAYLIST"
""")
    p.add_argument("urls", nargs="*", help="uma ou mais URLs do YouTube")
    p.add_argument("--arquivo", metavar="LISTA.TXT",
                   help="arquivo de texto com uma URL por linha")
    p.add_argument("--saida", type=Path, default=PASTA_SAIDA_PADRAO,
                   metavar="PASTA", help=f"pasta de destino (padrao: {PASTA_SAIDA_PADRAO})")
    p.add_argument("--navegador", default=",".join(NAVEGADORES_PADRAO), metavar="LISTA",
                   help="navegadores dos quais tentar ler cookies, em ordem "
                        "(ex.: firefox  |  firefox:perfil  |  nenhum)")
    p.add_argument("--cookies", metavar="COOKIES.TXT",
                   help="usa um arquivo cookies.txt em vez do navegador")
    p.add_argument("--idiomas", default=",".join(IDIOMAS_PADRAO), metavar="LISTA",
                   help=f"codigos de idioma aceitos, em ordem (padrao: {','.join(IDIOMAS_PADRAO)})")
    p.add_argument("--max-altura", type=int, default=None, metavar="N",
                   help="limita a resolucao vertical (ex.: 1080). Padrao: sem limite")
    p.add_argument("--codec", choices=["auto", "h264", "vp9", "av1"], default="auto",
                   help="preferencia de codec de video (h264 = maxima compatibilidade)")
    p.add_argument("--container", choices=["auto", "mp4", "mkv", "webm"], default="auto",
                   help="container final (padrao: auto)")
    p.add_argument("--legendas", action="store_true",
                   help="tambem baixa e embute legendas em portugues")
    p.add_argument("--playlist", action="store_true",
                   help="processa a playlist inteira quando a URL tiver uma lista")
    p.add_argument("--aceitar-original", action="store_true",
                   help="se nao houver dublagem em portugues, baixa no idioma original")
    p.add_argument("--listar", action="store_true",
                   help="apenas mostra os formatos dublados, sem baixar")
    p.add_argument("--simular", action="store_true",
                   help="faz tudo menos gravar o arquivo (--simulate do yt-dlp)")
    p.add_argument("--checar", action="store_true",
                   help="diagnostica o ambiente (Python, yt-dlp, ffmpeg, JS, navegadores)")
    p.add_argument("--tempo-limite", type=int, default=300, metavar="SEG",
                   help="tempo maximo de cada sondagem (padrao: 300s)")
    p.add_argument("--componentes-remotos", action="store_true",
                   help="permite ao yt-dlp buscar o solucionador de JS no GitHub "
                        "(use se o yt-dlp-ejs nao estiver instalado)")
    p.add_argument("--extra", nargs=argparse.REMAINDER, default=[], metavar="...",
                   help="tudo depois desta flag e repassado cru ao yt-dlp")
    return p


def main(argv: list[str]) -> int:
    _preparar_console()
    parser = montar_parser()
    args = parser.parse_args(argv)

    if args.checar:
        return checar_ambiente()

    urls: list[str] = list(args.urls)
    if args.arquivo:
        conteudo = Path(args.arquivo).read_text(encoding="utf-8", errors="replace")
        urls += [l.strip() for l in conteudo.splitlines()
                 if l.strip() and not l.strip().startswith("#")]
    if not urls:
        parser.print_help()
        print("\n  Informe pelo menos uma URL (ou use --arquivo / --checar).")
        return 2

    base = encontrar_ytdlp()
    if base is None:
        erro("yt-dlp nao encontrado. Instale com:  py -3 -m pip install -U yt-dlp")
        return 3
    if shutil.which("ffmpeg") is None:
        erro("ffmpeg nao encontrado. Instale com:  winget install Gyan.FFmpeg")
        return 3

    # Normaliza listas passadas como texto.
    args.idiomas = [x.strip() for x in str(args.idiomas).split(",") if x.strip()]
    if str(args.navegador).lower() in ("nenhum", "none", ""):
        args.navegador = []
    else:
        args.navegador = [x.strip() for x in str(args.navegador).split(",") if x.strip()]
    if args.cookies:
        args.navegador = []
    args.saida = Path(args.saida)

    # Opcoes aplicadas a todas as chamadas do yt-dlp.
    globais: list[str] = ["--ignore-config"]
    globais += ["--yes-playlist"] if args.playlist else ["--no-playlist"]
    for rt in runtimes_js_disponiveis():
        globais += ["--js-runtimes", rt]
    if args.componentes_remotos or not tem_ejs():
        globais += ["--remote-components", "ejs:github"]
    if args.cookies:
        globais += ["--cookies", args.cookies]

    titulo("BAIXADOR DE VIDEOS DUBLADOS EM PORTUGUES (pt-BR)")
    print(f"  yt-dlp   : {versao_ytdlp(base)}")
    print(f"  Runtime JS: {', '.join(runtimes_js_disponiveis()) or 'NENHUM (formatos podem faltar)'}")
    print(f"  Idiomas  : {', '.join(args.idiomas)}")
    print(f"  Destino  : {args.saida}")
    print(f"  URLs     : {len(urls)}")

    falhas = 0
    for url in urls:
        try:
            if not processar(url, args, base, globais):
                falhas += 1
        except KeyboardInterrupt:
            print("\n  Interrompido pelo usuario.")
            return 130
        except Exception as exc:  # nao deixa uma URL ruim derrubar o lote
            erro(f"erro inesperado: {exc!r}")
            falhas += 1

    titulo("RESUMO")
    print(f"  Total: {len(urls)}   Sucesso: {len(urls) - falhas}   Falhas: {falhas}")
    return 0 if falhas == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
