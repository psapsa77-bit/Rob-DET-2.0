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

echo Iniciando servidor web...
echo.
echo A interface sera aberta em: http://localhost:5000
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

REM Iniciar aplicação Flask
python web_app.py

pause
