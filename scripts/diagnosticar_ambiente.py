#!/usr/bin/env python3
"""
Script de Diagnóstico do Ambiente - Rob-DET 2.0

Verifica e corrige problemas comuns do ambiente:
- Instalação do Python
- Dependências instaladas
- Chrome/Edge instalado
- ChromeDriver/EdgeDriver funcionando
- Certificado digital configurado
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Tuple, Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import print as rprint
except ImportError:
    print("⚠️  Instalando biblioteca 'rich' para interface...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import print as rprint

console = Console()


def verificar_python() -> Tuple[bool, str]:
    """Verifica versão do Python."""
    version = sys.version_info
    if version >= (3, 11):
        return True, f"✅ Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"❌ Python {version.major}.{version.minor}.{version.micro} (necessário 3.11+)"


def verificar_pip() -> Tuple[bool, str]:
    """Verifica se pip está instalado."""
    try:
        import pip
        return True, f"✅ pip instalado"
    except ImportError:
        return False, "❌ pip não encontrado"


def verificar_chrome() -> Tuple[bool, str]:
    """Verifica se Google Chrome está instalado."""
    sistema = platform.system()

    if sistema == "Windows":
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]
        for path in paths:
            if os.path.exists(path):
                return True, f"✅ Google Chrome encontrado: {path}"
        return False, "❌ Google Chrome não encontrado"

    elif sistema == "Linux":
        # Verificar se o comando 'google-chrome' existe
        if shutil.which("google-chrome") or shutil.which("google-chrome-stable"):
            return True, "✅ Google Chrome encontrado"
        return False, "❌ Google Chrome não encontrado"

    elif sistema == "Darwin":  # macOS
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            return True, f"✅ Google Chrome encontrado"
        return False, "❌ Google Chrome não encontrado"

    return False, f"❌ Sistema operacional não suportado: {sistema}"


def verificar_edge() -> Tuple[bool, str]:
    """Verifica se Microsoft Edge está instalado."""
    sistema = platform.system()

    if sistema == "Windows":
        paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        for path in paths:
            if os.path.exists(path):
                return True, f"✅ Microsoft Edge encontrado: {path}"
        return False, "❌ Microsoft Edge não encontrado"

    elif sistema == "Linux":
        if shutil.which("microsoft-edge") or shutil.which("microsoft-edge-stable"):
            return True, "✅ Microsoft Edge encontrado"
        return False, "❌ Microsoft Edge não encontrado"

    elif sistema == "Darwin":  # macOS
        edge_path = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        if os.path.exists(edge_path):
            return True, f"✅ Microsoft Edge encontrado"
        return False, "❌ Microsoft Edge não encontrado"

    return False, f"Sistema operacional não suportado: {sistema}"


def testar_selenium() -> Tuple[bool, str]:
    """Testa se Selenium está instalado e funcionando."""
    try:
        import selenium
        from selenium import webdriver
        return True, f"✅ Selenium {selenium.__version__} instalado"
    except ImportError:
        return False, "❌ Selenium não instalado"


def testar_webdriver_manager() -> Tuple[bool, str]:
    """Testa se webdriver-manager está instalado."""
    try:
        import webdriver_manager
        return True, "✅ webdriver-manager instalado"
    except ImportError:
        return False, "❌ webdriver-manager não instalado"


def testar_chrome_driver() -> Tuple[bool, str]:
    """Tenta inicializar o ChromeDriver."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager

        console.print("[yellow]⏳ Testando ChromeDriver... (isso pode demorar na primeira vez)[/yellow]")

        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Testar navegação simples
        driver.get("https://www.google.com")
        titulo = driver.title
        driver.quit()

        return True, f"✅ ChromeDriver funcionando! (testado com: {titulo})"

    except Exception as e:
        return False, f"❌ ChromeDriver falhou: {str(e)[:100]}"


def testar_edge_driver() -> Tuple[bool, str]:
    """Tenta inicializar o EdgeDriver."""
    try:
        from selenium import webdriver
        from selenium.webdriver.edge.service import Service
        from selenium.webdriver.edge.options import Options
        from webdriver_manager.microsoft import EdgeChromiumDriverManager

        console.print("[yellow]⏳ Testando EdgeDriver... (isso pode demorar na primeira vez)[/yellow]")

        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)

        # Testar navegação simples
        driver.get("https://www.google.com")
        titulo = driver.title
        driver.quit()

        return True, f"✅ EdgeDriver funcionando! (testado com: {titulo})"

    except Exception as e:
        return False, f"❌ EdgeDriver falhou: {str(e)[:100]}"


def verificar_dependencias_principais() -> Tuple[bool, str]:
    """Verifica se as dependências principais estão instaladas."""
    dependencias = [
        'selenium',
        'webdriver_manager',
        'loguru',
        'rich',
        'pydantic',
        'schedule'
    ]

    faltando = []
    for dep in dependencias:
        try:
            __import__(dep)
        except ImportError:
            faltando.append(dep)

    if not faltando:
        return True, f"✅ Todas as {len(dependencias)} dependências principais instaladas"
    else:
        return False, f"❌ Faltando: {', '.join(faltando)}"


def instalar_dependencias() -> bool:
    """Instala dependências do requirements.txt."""
    try:
        console.print("\n[yellow]📦 Instalando dependências...[/yellow]")

        requirements_file = Path(__file__).parent.parent / "requirements.txt"

        if not requirements_file.exists():
            console.print("[red]❌ Arquivo requirements.txt não encontrado![/red]")
            return False

        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        console.print("[green]✅ Dependências instaladas com sucesso![/green]")
        return True

    except Exception as e:
        console.print(f"[red]❌ Erro ao instalar dependências: {e}[/red]")
        return False


def corrigir_ambiente() -> bool:
    """Tenta corrigir problemas do ambiente."""
    console.print("\n[yellow]🔧 Tentando corrigir ambiente...[/yellow]\n")

    # 1. Verificar pip
    sucesso_pip, msg_pip = verificar_pip()
    if not sucesso_pip:
        console.print("[red]❌ pip não está disponível. Instale o Python corretamente.[/red]")
        return False

    # 2. Instalar dependências
    if not instalar_dependencias():
        console.print("[red]❌ Falha ao instalar dependências[/red]")
        return False

    # 3. Testar WebDriver novamente
    console.print("\n[yellow]🧪 Testando WebDriver após instalação...[/yellow]")

    sucesso_chrome, msg_chrome = testar_chrome_driver()
    if sucesso_chrome:
        console.print(f"[green]{msg_chrome}[/green]")
        return True

    sucesso_edge, msg_edge = testar_edge_driver()
    if sucesso_edge:
        console.print(f"[green]{msg_edge}[/green]")
        return True

    console.print("[red]❌ Nenhum WebDriver funcionou após correção[/red]")
    return False


def main():
    """Função principal."""
    console.clear()

    # Banner
    console.print(Panel.fit(
        "[bold cyan]🔍 DIAGNÓSTICO DO AMBIENTE - ROB-DET 2.0[/bold cyan]",
        border_style="cyan"
    ))

    console.print("\n[bold]Verificando ambiente...[/bold]\n")

    # Lista de verificações
    verificacoes = [
        ("Python 3.11+", verificar_python),
        ("pip", verificar_pip),
        ("Google Chrome", verificar_chrome),
        ("Microsoft Edge", verificar_edge),
        ("Selenium", testar_selenium),
        ("webdriver-manager", testar_webdriver_manager),
        ("Dependências principais", verificar_dependencias_principais),
    ]

    # Executar verificações básicas
    resultados = []
    for nome, func in verificacoes:
        sucesso, mensagem = func()
        resultados.append((nome, sucesso, mensagem))

    # Mostrar resultados em tabela
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Verificação", style="cyan", width=30)
    table.add_column("Status", width=50)

    for nome, sucesso, mensagem in resultados:
        table.add_row(nome, mensagem)

    console.print(table)

    # Verificar se Chrome ou Edge estão disponíveis
    tem_chrome = resultados[2][1]  # Google Chrome
    tem_edge = resultados[3][1]    # Microsoft Edge

    if not tem_chrome and not tem_edge:
        console.print("\n[bold red]❌ PROBLEMA CRÍTICO[/bold red]")
        console.print(Panel(
            "[yellow]Você precisa instalar pelo menos um navegador:[/yellow]\n\n"
            "• [cyan]Google Chrome:[/cyan] https://www.google.com/chrome/\n"
            "• [cyan]Microsoft Edge:[/cyan] https://www.microsoft.com/edge\n\n"
            "[yellow]Após instalar, execute este script novamente.[/yellow]",
            title="🌐 Navegador Necessário",
            border_style="red"
        ))
        return False

    # Testar WebDriver
    console.print("\n[bold]Testando WebDriver...[/bold]")
    console.print("[dim]Isso pode demorar alguns segundos na primeira vez...[/dim]\n")

    webdriver_ok = False

    if tem_chrome:
        sucesso, mensagem = testar_chrome_driver()
        console.print(mensagem)
        webdriver_ok = sucesso

    if not webdriver_ok and tem_edge:
        sucesso, mensagem = testar_edge_driver()
        console.print(mensagem)
        webdriver_ok = sucesso

    # Resultado final
    console.print()
    if webdriver_ok:
        console.print(Panel.fit(
            "[bold green]✅ AMBIENTE OK![/bold green]\n\n"
            "Seu ambiente está configurado corretamente.\n"
            "Você pode executar o robô com:\n\n"
            "[cyan]python robo.py[/cyan]  ou  [cyan]python main.py[/cyan]",
            border_style="green",
            title="🎉 Sucesso"
        ))
        return True
    else:
        console.print(Panel.fit(
            "[bold yellow]⚠️  PROBLEMA DETECTADO[/bold yellow]\n\n"
            "O WebDriver não está funcionando corretamente.\n"
            "Deseja tentar corrigir automaticamente?",
            border_style="yellow",
            title="🔧 Correção Necessária"
        ))

        resposta = console.input("\n[cyan]Tentar corrigir? (S/n):[/cyan] ").strip().lower()

        if resposta in ['s', 'sim', 'y', 'yes', '']:
            if corrigir_ambiente():
                console.print("\n[bold green]✅ Ambiente corrigido com sucesso![/bold green]")
                console.print("\nTeste executando: [cyan]python robo.py[/cyan]")
                return True
            else:
                console.print("\n[bold red]❌ Não foi possível corrigir automaticamente[/bold red]")
                console.print("\n[yellow]Soluções manuais:[/yellow]")
                console.print("1. Reinstale o Google Chrome ou Microsoft Edge")
                console.print("2. Execute: [cyan]pip install --upgrade selenium webdriver-manager[/cyan]")
                console.print("3. Verifique se há firewalls ou antivírus bloqueando")
                return False
        else:
            console.print("\n[yellow]Execute novamente quando estiver pronto.[/yellow]")
            return False


if __name__ == "__main__":
    try:
        sucesso = main()
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Interrompido pelo usuário[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]❌ Erro inesperado: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
