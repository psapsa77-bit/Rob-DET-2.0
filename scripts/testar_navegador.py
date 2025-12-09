#!/usr/bin/env python3
"""
Script de Teste do Navegador - Rob-DET 2.0

Testa a abertura do navegador com Selenium e WebDriver.
Útil para diagnosticar problemas antes de executar o robô completo.
"""

import sys
import time
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
except ImportError:
    print("❌ Biblioteca 'rich' não encontrada. Instale com: pip install rich")
    sys.exit(1)

console = Console()


def testar_chrome():
    """Testa abertura do Chrome."""
    console.print("\n[bold cyan]🧪 Testando Google Chrome[/bold cyan]\n")

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager

        console.print("[yellow]⏳ Inicializando ChromeDriver...[/yellow]")
        console.print("[dim]Isso pode demorar na primeira vez (download do driver)[/dim]\n")

        # Configurar opções
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')

        # Instalar e iniciar ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        console.print("[green]✅ Chrome aberto com sucesso![/green]")
        console.print("[yellow]Navegando para Google...[/yellow]\n")

        # Testar navegação
        driver.get("https://www.google.com")

        console.print(f"[green]✅ Navegação OK![/green]")
        console.print(f"[dim]Título da página: {driver.title}[/dim]\n")

        # Aguardar um pouco para o usuário ver
        console.print("[cyan]O navegador vai fechar em 5 segundos...[/cyan]")
        time.sleep(5)

        driver.quit()
        console.print("[green]✅ Chrome fechado corretamente[/green]\n")

        return True, "Chrome funcionando perfeitamente!"

    except ImportError as e:
        return False, f"Dependência faltando: {e}"
    except Exception as e:
        return False, f"Erro: {str(e)}"


def testar_edge():
    """Testa abertura do Edge."""
    console.print("\n[bold cyan]🧪 Testando Microsoft Edge[/bold cyan]\n")

    try:
        from selenium import webdriver
        from selenium.webdriver.edge.service import Service
        from selenium.webdriver.edge.options import Options
        from webdriver_manager.microsoft import EdgeChromiumDriverManager

        console.print("[yellow]⏳ Inicializando EdgeDriver...[/yellow]")
        console.print("[dim]Isso pode demorar na primeira vez (download do driver)[/dim]\n")

        # Configurar opções
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')

        # Instalar e iniciar EdgeDriver
        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)

        console.print("[green]✅ Edge aberto com sucesso![/green]")
        console.print("[yellow]Navegando para Google...[/yellow]\n")

        # Testar navegação
        driver.get("https://www.google.com")

        console.print(f"[green]✅ Navegação OK![/green]")
        console.print(f"[dim]Título da página: {driver.title}[/dim]\n")

        # Aguardar um pouco para o usuário ver
        console.print("[cyan]O navegador vai fechar em 5 segundos...[/cyan]")
        time.sleep(5)

        driver.quit()
        console.print("[green]✅ Edge fechado corretamente[/green]\n")

        return True, "Edge funcionando perfeitamente!"

    except ImportError as e:
        return False, f"Dependência faltando: {e}"
    except Exception as e:
        return False, f"Erro: {str(e)}"


def testar_portal_det():
    """Testa acesso ao portal DET."""
    console.print("\n[bold cyan]🧪 Testando Acesso ao Portal DET[/bold cyan]\n")

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager

        console.print("[yellow]⏳ Abrindo portal DET...[/yellow]\n")

        # Configurar opções
        options = Options()
        options.add_argument('--start-maximized')

        # Iniciar Chrome
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Navegar para DET
        url_det = "https://det.sit.trabalho.gov.br/"
        driver.get(url_det)

        console.print(f"[green]✅ Portal DET carregado![/green]")
        console.print(f"[dim]URL: {driver.current_url}[/dim]")
        console.print(f"[dim]Título: {driver.title}[/dim]\n")

        console.print("[cyan]📸 Você pode ver o navegador aberto?[/cyan]")
        console.print("[cyan]O navegador vai fichar aberto por 10 segundos para você verificar...[/cyan]\n")

        time.sleep(10)

        driver.quit()
        console.print("[green]✅ Teste do portal DET concluído[/green]\n")

        return True, "Portal DET acessível!"

    except Exception as e:
        return False, f"Erro ao acessar DET: {str(e)}"


def main():
    """Função principal."""
    console.clear()

    # Banner
    console.print(Panel.fit(
        "[bold cyan]🧪 TESTE DE NAVEGADOR - ROB-DET 2.0[/bold cyan]\n\n"
        "Este script vai testar se o Selenium consegue abrir\n"
        "o navegador corretamente no seu computador.",
        border_style="cyan"
    ))

    # Menu
    console.print("\n[bold]Escolha o que deseja testar:[/bold]\n")
    console.print("[cyan]1.[/cyan] Testar Google Chrome")
    console.print("[cyan]2.[/cyan] Testar Microsoft Edge")
    console.print("[cyan]3.[/cyan] Testar acesso ao Portal DET (com Chrome)")
    console.print("[cyan]4.[/cyan] Testar todos")
    console.print("[cyan]0.[/cyan] Sair\n")

    escolha = console.input("[cyan]Digite sua escolha:[/cyan] ").strip()

    if escolha == "1":
        sucesso, mensagem = testar_chrome()
    elif escolha == "2":
        sucesso, mensagem = testar_edge()
    elif escolha == "3":
        sucesso, mensagem = testar_portal_det()
    elif escolha == "4":
        # Testar todos
        console.print("\n[bold]Testando todos os navegadores...[/bold]")

        resultados = []

        # Chrome
        sucesso_chrome, msg_chrome = testar_chrome()
        resultados.append(("Chrome", sucesso_chrome, msg_chrome))

        # Edge
        sucesso_edge, msg_edge = testar_edge()
        resultados.append(("Edge", sucesso_edge, msg_edge))

        # Portal DET
        sucesso_det, msg_det = testar_portal_det()
        resultados.append(("Portal DET", sucesso_det, msg_det))

        # Resumo
        console.print("\n" + "="*60)
        console.print("[bold]RESUMO DOS TESTES[/bold]")
        console.print("="*60 + "\n")

        for nome, sucesso, msg in resultados:
            status = "[green]✅" if sucesso else "[red]❌"
            console.print(f"{status} {nome}:[/] {msg}")

        # Verificar se pelo menos um funcionou
        if any(r[1] for r in resultados):
            console.print("\n[bold green]✅ Pelo menos um navegador está funcionando![/bold green]")
            sucesso = True
            mensagem = "Testes concluídos"
        else:
            console.print("\n[bold red]❌ Nenhum navegador funcionou[/bold red]")
            sucesso = False
            mensagem = "Execute: python scripts/diagnosticar_ambiente.py"
    elif escolha == "0":
        console.print("\n[yellow]Saindo...[/yellow]")
        return True
    else:
        console.print("\n[red]❌ Opção inválida[/red]")
        return False

    # Resultado final
    console.print()
    if sucesso:
        console.print(Panel.fit(
            f"[bold green]✅ TESTE BEM-SUCEDIDO![/bold green]\n\n"
            f"{mensagem}\n\n"
            f"[cyan]Próximo passo:[/cyan] Execute o robô com:\n"
            f"[yellow]python robo.py[/yellow]",
            border_style="green",
            title="🎉 Sucesso"
        ))
    else:
        console.print(Panel.fit(
            f"[bold red]❌ TESTE FALHOU[/bold red]\n\n"
            f"{mensagem}\n\n"
            f"[yellow]Execute o diagnóstico completo:[/yellow]\n"
            f"[cyan]python scripts/diagnosticar_ambiente.py[/cyan]",
            border_style="red",
            title="⚠️  Erro"
        ))

    return sucesso


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
