@echo off
chcp 65001 >nul
title Baixar video dublado em portugues (pt-BR)
cd /d "%~dp0"

echo ============================================================
echo  BAIXADOR DE VIDEOS DUBLADOS EM PORTUGUES (pt-BR)
echo ============================================================
echo.
echo  Cole a URL do video do YouTube e pressione ENTER.
echo  (para colar: clique com o botao direito dentro desta janela)
echo.

set "URL="
set /p URL=URL:

if "%URL%"=="" (
    echo.
    echo Nenhuma URL informada. Encerrando.
    echo.
    pause
    exit /b 1
)

echo.
py -3 "%~dp0baixar_dublado.py" "%URL%"

echo.
echo ============================================================
echo  Os arquivos ficam na pasta:  %~dp0vídeos
echo ============================================================
pause
