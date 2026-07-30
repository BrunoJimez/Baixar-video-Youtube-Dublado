@echo off
chcp 65001 >nul
title Diagnostico do ambiente
cd /d "%~dp0"
py -3 "%~dp0baixar_dublado.py" --checar
echo.
pause
