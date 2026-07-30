# -*- coding: utf-8 -*-
"""Testa a logica de selecao de formatos sem tocar na rede."""
import sys
sys.path.insert(0, r"C:\Projeto_Claude\Youtu_Baixar")
from baixar_dublado import escolher, escolher_container, escolher_original

IDS = ["pt-BR", "pt", "pt-PT"]

# --- Caso 1: audio pt-BR como faixa separada (Caminho A) ------------------- #
caso1 = {"formats": [
    {"format_id": "sb0", "ext": "mhtml", "vcodec": "images", "acodec": "none"},
    {"format_id": "140", "ext": "m4a", "vcodec": "none", "acodec": "mp4a.40.2",
     "abr": 129, "tbr": 129, "language": "en-US"},
    {"format_id": "140-1", "ext": "m4a", "vcodec": "none", "acodec": "mp4a.40.2",
     "abr": 129, "tbr": 129, "language": "pt-BR"},
    {"format_id": "251-1", "ext": "webm", "vcodec": "none", "acodec": "opus",
     "abr": 101, "tbr": 101, "language": "pt-BR"},
    {"format_id": "137", "ext": "mp4", "vcodec": "avc1.640028", "acodec": "none",
     "height": 1080, "fps": 25, "tbr": 818},
    {"format_id": "313", "ext": "webm", "vcodec": "vp9", "acodec": "none",
     "height": 2160, "fps": 25, "tbr": 12000},
    {"format_id": "96-8", "ext": "mp4", "vcodec": "avc1.640028", "acodec": "mp4a.40.2",
     "height": 1080, "fps": 25, "tbr": 3821, "language": "pt-BR"},
]}
e = escolher(caso1, IDS, None, "auto")
print("caso1 modo:", e["modo"], "| spec:", e["spec"], "| container:",
      escolher_container(e, "auto"))
assert e["modo"] == "separado", e
assert e["spec"] == "313+140-1", e          # melhor video 4K + melhor audio pt-BR (aac 129k)
assert escolher_container(e, "auto") == "mkv"  # webm(video) + m4a(audio) -> mkv

# --- Caso 2: mesmo caso, mas limitado a 1080p e forcando h264 ------------- #
e = escolher(caso1, IDS, 1080, "h264")
print("caso2 modo:", e["modo"], "| spec:", e["spec"], "| container:",
      escolher_container(e, "auto"))
assert e["spec"] == "137+140-1", e
assert escolher_container(e, "auto") == "mp4"  # mp4 + m4a -> mp4

# --- Caso 3: so HLS mesclado tem pt-BR (Caminho B, os videos reais) ------- #
caso3 = {"formats": [
    {"format_id": "140", "ext": "m4a", "vcodec": "none", "acodec": "mp4a.40.2",
     "abr": 129, "tbr": 129, "language": "en-US"},
    {"format_id": "137", "ext": "mp4", "vcodec": "avc1.640028", "acodec": "none",
     "height": 1080, "fps": 25, "tbr": 818},
    {"format_id": "95-8", "ext": "mp4", "vcodec": "avc1", "acodec": "mp4a.40.2",
     "height": 720, "fps": 25, "tbr": 630, "language": "pt-BR"},
    {"format_id": "96-8", "ext": "mp4", "vcodec": "avc1", "acodec": "mp4a.40.2",
     "height": 1080, "fps": 25, "tbr": 3821, "language": "pt-BR"},
]}
e = escolher(caso3, IDS, None, "auto")
print("caso3 modo:", e["modo"], "| spec:", e["spec"])
assert e["modo"] == "mesclado" and e["spec"] == "96-8", e

# --- Caso 4: nenhum audio em portugues -> None, e reserva funciona -------- #
caso4 = {"formats": [
    {"format_id": "140", "ext": "m4a", "vcodec": "none", "acodec": "mp4a.40.2",
     "abr": 129, "tbr": 129, "language": "en-US"},
    {"format_id": "137", "ext": "mp4", "vcodec": "avc1", "acodec": "none",
     "height": 1080, "fps": 25, "tbr": 818},
]}
assert escolher(caso4, IDS, None, "auto") is None
r = escolher_original(caso4, None)
print("caso4 reserva:", r["spec"], "| idioma:", r["idioma"])
assert r["spec"] == "137+140"

# --- Caso 5: idioma marcado apenas como "pt" (raiz) ----------------------- #
caso5 = {"formats": [
    {"format_id": "140-2", "ext": "m4a", "vcodec": "none", "acodec": "mp4a.40.2",
     "abr": 129, "tbr": 129, "language": "pt"},
    {"format_id": "137", "ext": "mp4", "vcodec": "avc1", "acodec": "none",
     "height": 1080, "fps": 25, "tbr": 818},
]}
e = escolher(caso5, IDS, None, "auto")
print("caso5 spec:", e["spec"], "| idioma:", e["idioma"])
assert e["spec"] == "137+140-2"

# --- Caso 6: prefere pt-BR quando ha pt-BR E pt ------------------------- #
caso6 = {"formats": [
    {"format_id": "A-pt", "ext": "m4a", "vcodec": "none", "acodec": "mp4a.40.2",
     "abr": 200, "tbr": 200, "language": "pt-PT"},
    {"format_id": "A-br", "ext": "m4a", "vcodec": "none", "acodec": "mp4a.40.2",
     "abr": 129, "tbr": 129, "language": "pt-BR"},
    {"format_id": "137", "ext": "mp4", "vcodec": "avc1", "acodec": "none",
     "height": 1080, "fps": 25, "tbr": 818},
]}
e = escolher(caso6, IDS, None, "auto")
print("caso6 spec:", e["spec"], "| idioma:", e["idioma"])
assert e["spec"] == "137+A-br", e   # pt-BR ganha mesmo com bitrate menor

print("\nTODOS OS TESTES PASSARAM")
