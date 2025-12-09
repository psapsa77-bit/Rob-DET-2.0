@echo off
REM Script de Atalho para Executar o Rob-DET 2.0
REM Dê um duplo-clique neste arquivo para executar o robô

title Rob-DET 2.0 - Menu Principal

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERRO] Python nao encontrado!
    echo.
    echo Por favor, instale o Python 3.11 ou superior:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Marque a opcao "Add Python to PATH" durante a instalacao
    echo.
    pause
    exit /b 1
)

REM Executar interface amigável
python robo.py

REM Se houve erro
if errorlevel 1 (
    echo.
    echo [ERRO] Houve um problema ao executar o robo.
    echo.
    echo Solucoes:
    echo 1. Execute o instalador: python install.py
    echo 2. Verifique se as dependencias estao instaladas
    echo 3. Consulte o arquivo INICIO_RAPIDO.md
    echo.
)

pause
