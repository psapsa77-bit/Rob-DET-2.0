@echo off
REM Inicia a Interface Web do Rob-DET 2.0

title Rob-DET 2.0 - Interface Web

echo.
echo ====================================
echo  Rob-DET 2.0 - Interface Web
echo ====================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Por favor, instale o Python 3.11 ou superior.
    echo.
    pause
    exit /b 1
)

REM Verificar se Flask está instalado
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [AVISO] Flask nao encontrado!
    echo.
    echo Instalando dependencias da interface web...
    echo (Isso so acontece na primeira vez)
    echo.
    python instalar_web.py
    if errorlevel 1 (
        echo.
        echo [ERRO] Falha ao instalar dependencias.
        echo.
        echo Execute manualmente:
        echo   python instalar_web.py
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Iniciando servidor web...
echo.
echo [!] A interface sera aberta em: http://localhost:5000
echo.
echo Pressione Ctrl+C para parar o servidor
echo.
echo ====================================
echo.

REM Iniciar aplicação Flask
python web_app.py

if errorlevel 1 (
    echo.
    echo [ERRO] Houve um problema ao iniciar o servidor.
    echo.
    echo Solucoes:
    echo 1. Verifique se a porta 5000 esta livre
    echo 2. Execute: python instalar_web.py
    echo 3. Consulte INTERFACE_WEB.md
    echo.
)

pause
