@echo off
chcp 65001 >nul
title Instalar requisitos - Baixador de videos dublados
cd /d "%~dp0"

echo ============================================================
echo  INSTALANDO / ATUALIZANDO OS REQUISITOS
echo ============================================================
echo.

py -3 --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado.
    echo        Instale em https://www.python.org/downloads/windows/
    echo        e marque "Add python.exe to PATH" durante a instalacao.
    echo.
    pause
    exit /b 1
)

echo -- Instalando yt-dlp e yt-dlp-ejs no Python padrao...
py -3 -m pip install --upgrade pip
py -3 -m pip install --upgrade yt-dlp yt-dlp-ejs
echo.

where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo [AVISO] ffmpeg nao encontrado no PATH.
    echo         Instale com:  winget install Gyan.FFmpeg
    echo         Depois FECHE e ABRA este arquivo de novo.
) else (
    echo -- ffmpeg encontrado.
)
echo.

where deno >nul 2>&1
if errorlevel 1 (
    where node >nul 2>&1
    if errorlevel 1 (
        echo [AVISO] Nenhum runtime de JavaScript encontrado.
        echo         Instale o Deno com:  winget install DenoLand.Deno
    ) else (
        echo -- node encontrado (serve como runtime de JavaScript).
    )
) else (
    echo -- deno encontrado.
)
echo.

echo ============================================================
echo  DIAGNOSTICO FINAL
echo ============================================================
py -3 "%~dp0baixar_dublado.py" --checar
echo.
pause
