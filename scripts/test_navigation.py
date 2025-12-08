#!/usr/bin/env python3
"""
Script de Teste de Navegação - Rob-DET 2.0

Testa o fluxo completo de navegação no portal DET usando Page Objects.

Uso:
    python scripts/test_navigation.py
    python scripts/test_navigation.py --cnpj 12.345.678/0001-90
    python scripts/test_navigation.py --headless
"""

import sys
import argparse
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from rich.console import Console
from rich.panel import Panel

from src.navigation.det_navigator import DETNavigator
from src.pages import LoginPage, HomePage, CaixaPostalPage, MensagemDetalhesPage

console = Console()


def test_login(navigator: DETNavigator) -> bool:
    """
    Testa login no DET.

    Args:
        navigator: Navegador

    Returns:
        True se sucesso, False caso contrário
    """
    console.print("\n[bold cyan]📝 TESTE 1: Login no DET[/bold cyan]")

    login_page = LoginPage(navigator.driver)

    if login_page.realizar_login():
        console.print("[green]✓ Login bem-sucedido![/green]")
        return True
    else:
        console.print("[red]✗ Login falhou[/red]")
        return False


def test_selecao_empresa(navigator: DETNavigator, cnpj: str) -> bool:
    """
    Testa seleção de empresa.

    Args:
        navigator: Navegador
        cnpj: CNPJ a selecionar

    Returns:
        True se sucesso, False caso contrário
    """
    console.print(f"\n[bold cyan]📝 TESTE 2: Seleção de Empresa ({cnpj})[/bold cyan]")

    home_page = HomePage(navigator.driver)

    if home_page.selecionar_empresa(cnpj):
        console.print(f"[green]✓ Empresa {cnpj} selecionada![/green]")
        return True
    else:
        console.print(f"[red]✗ Falha ao selecionar empresa {cnpj}[/red]")
        return False


def test_navegacao_caixa_postal(navigator: DETNavigator) -> bool:
    """
    Testa navegação para caixa postal.

    Args:
        navigator: Navegador

    Returns:
        True se sucesso, False caso contrário
    """
    console.print("\n[bold cyan]📝 TESTE 3: Navegação para Caixa Postal[/bold cyan]")

    home_page = HomePage(navigator.driver)

    if home_page.navegar_para_caixa_postal():
        console.print("[green]✓ Navegou para caixa postal![/green]")
        return True
    else:
        console.print("[red]✗ Falha ao navegar para caixa postal[/red]")
        return False


def test_listagem_mensagens(navigator: DETNavigator) -> int:
    """
    Testa listagem de mensagens.

    Args:
        navigator: Navegador

    Returns:
        Número de mensagens encontradas
    """
    console.print("\n[bold cyan]📝 TESTE 4: Listagem de Mensagens[/bold cyan]")

    caixa_postal = CaixaPostalPage(navigator.driver)

    # Obter total
    total = caixa_postal.obter_total_mensagens()
    console.print(f"[cyan]Total de mensagens na página: {total}[/cyan]")

    if total == 0:
        console.print("[yellow]⚠️  Caixa postal vazia[/yellow]")
        return 0

    # Extrair mensagens
    mensagens = caixa_postal.extrair_mensagens_lista()

    console.print(f"[green]✓ Extraídas {len(mensagens)} mensagens![/green]")

    # Mostrar primeiras 3
    for i, msg in enumerate(mensagens[:3], 1):
        console.print(f"  {i}. {msg['assunto'][:60]}")

    return len(mensagens)


def test_detalhes_mensagem(navigator: DETNavigator) -> bool:
    """
    Testa visualização de detalhes de mensagem.

    Args:
        navigator: Navegador

    Returns:
        True se sucesso, False caso contrário
    """
    console.print("\n[bold cyan]📝 TESTE 5: Detalhes de Mensagem[/bold cyan]")

    caixa_postal = CaixaPostalPage(navigator.driver)

    # Clicar na primeira mensagem
    console.print("Clicando na primeira mensagem...")
    if not caixa_postal.clicar_mensagem(1):
        console.print("[red]✗ Falha ao clicar em mensagem[/red]")
        return False

    # Extrair detalhes
    detalhes_page = MensagemDetalhesPage(navigator.driver)
    detalhes = detalhes_page.extrair_detalhes_completos()

    console.print(f"[green]✓ Detalhes extraídos![/green]")
    console.print(f"  Assunto: {detalhes['assunto'][:60]}")
    console.print(f"  Remetente: {detalhes['remetente']}")
    console.print(f"  Data: {detalhes['data_envio']}")

    if detalhes['possui_anexo']:
        console.print(f"  📎 Anexos: {len(detalhes['anexos'])}")

    # Voltar para lista
    console.print("\nVoltando para lista...")
    if detalhes_page.voltar_para_lista():
        console.print("[green]✓ Voltou para lista![/green]")
        return True
    else:
        console.print("[yellow]⚠️  Não foi possível voltar[/yellow]")
        return False


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Testa navegação no portal DET'
    )

    parser.add_argument(
        '--cnpj',
        default='12.345.678/0001-90',
        help='CNPJ para testar seleção'
    )

    parser.add_argument(
        '--headless',
        action='store_true',
        help='Executar em modo headless'
    )

    parser.add_argument(
        '--skip-login',
        action='store_true',
        help='Pular teste de login (assumir já logado)'
    )

    args = parser.parse_args()

    # Banner
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         🧪 TESTE DE NAVEGAÇÃO - Rob-DET 2.0                  ║
║                                                              ║
║         Testando Page Objects e fluxo de navegação          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")

    # Criar navigator
    console.print("\n[bold]Iniciando navegador...[/bold]")
    navigator = DETNavigator(
        browser='chrome',
        headless=args.headless,
        timeout=30
    )

    try:
        navigator.start()
        console.print("[green]✓ Navegador iniciado![/green]")

        # Testes
        resultados = {}

        # Teste 1: Login
        if not args.skip_login:
            resultados['login'] = test_login(navigator)
            if not resultados['login']:
                console.print("\n[red]❌ Login falhou. Abortando testes.[/red]")
                return 1
        else:
            console.print("\n[yellow]⏭️  Pulando teste de login[/yellow]")
            resultados['login'] = True

        # Teste 2: Seleção de empresa
        if args.cnpj:
            resultados['selecao_empresa'] = test_selecao_empresa(navigator, args.cnpj)

        # Teste 3: Navegação caixa postal
        resultados['caixa_postal'] = test_navegacao_caixa_postal(navigator)

        if not resultados['caixa_postal']:
            console.print("\n[red]❌ Não foi possível acessar caixa postal. Abortando.[/red]")
            return 1

        # Teste 4: Listagem de mensagens
        total_mensagens = test_listagem_mensagens(navigator)
        resultados['listagem'] = total_mensagens > 0

        # Teste 5: Detalhes de mensagem (apenas se houver mensagens)
        if total_mensagens > 0:
            resultados['detalhes'] = test_detalhes_mensagem(navigator)
        else:
            console.print("\n[yellow]⏭️  Pulando teste de detalhes (sem mensagens)[/yellow]")

        # Resumo
        console.print("\n" + "=" * 70)
        console.print("[bold cyan]📊 RESUMO DOS TESTES[/bold cyan]")
        console.print("=" * 70)

        total_testes = len(resultados)
        testes_ok = sum(1 for r in resultados.values() if r)

        for nome, resultado in resultados.items():
            status = "[green]✓[/green]" if resultado else "[red]✗[/red]"
            console.print(f"  {status} {nome.replace('_', ' ').title()}")

        console.print()

        if testes_ok == total_testes:
            console.print(
                f"[bold green]🎉 Todos os {total_testes} testes passaram![/bold green]"
            )
            return 0
        else:
            console.print(
                f"[bold yellow]⚠️  {testes_ok}/{total_testes} testes passaram[/bold yellow]"
            )
            return 1

    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Testes interrompidos pelo usuário[/yellow]")
        return 130

    except Exception as e:
        console.print(f"\n[red]❌ Erro durante testes: {e}[/red]")
        logger.exception(e)
        return 1

    finally:
        console.print("\n[dim]Fechando navegador...[/dim]")
        navigator.stop()


if __name__ == '__main__':
    sys.exit(main())
