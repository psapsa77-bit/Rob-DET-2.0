#!/usr/bin/env python3
"""
Script de Configuração Automática de Certificado Digital - Rob-DET 2.0

Configura o registro do Windows para auto-seleção de certificado digital
no Chrome/Edge para o portal DET.

IMPORTANTE: Requer execução como Administrador!

Uso:
    # Modo interativo
    python scripts/setup_auto_certificate.py

    # Modo direto
    python scripts/setup_auto_certificate.py --browser chrome --thumbprint ABC123...

    # Remover configuração
    python scripts/setup_auto_certificate.py --remove
"""

import sys
import argparse
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from src.auth.windows_cert_store import WindowsCertificateStore
from src.auth.registry_config import RegistryConfigurator

console = Console()


def check_admin() -> bool:
    """
    Verifica se está executando como administrador.

    Returns:
        True se admin, False caso contrário
    """
    import ctypes
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def select_certificate_interactive() -> tuple:
    """
    Permite ao usuário selecionar um certificado interativamente.

    Returns:
        Tupla (CertificateInfo, issuer_cn) ou (None, None)
    """
    console.print("\n[bold cyan]🔍 Buscando certificados válidos...[/bold cyan]\n")

    store = WindowsCertificateStore()
    certs = store.get_valid_certificates()

    if not certs:
        console.print("[red]❌ Nenhum certificado válido encontrado![/red]")
        console.print("\n[yellow]Verifique se você tem certificados digitais válidos instalados.[/yellow]")
        return None, None

    # Filtrar apenas e-CNPJ (mais comum para DET)
    ecnpj_certs = [c for c in certs if c.cnpj]

    if ecnpj_certs:
        console.print(f"[green]✅ Encontrados {len(ecnpj_certs)} certificados e-CNPJ válidos[/green]\n")
        certs_to_show = ecnpj_certs
    else:
        console.print(f"[yellow]⚠️  Nenhum e-CNPJ encontrado. Mostrando todos os certificados ({len(certs)})[/yellow]\n")
        certs_to_show = certs

    # Criar tabela
    table = Table(title="📜 Selecione um Certificado")
    table.add_column("#", style="cyan", width=3)
    table.add_column("Common Name", style="yellow", no_wrap=False, width=35)
    table.add_column("CNPJ/CPF", style="green", width=20)
    table.add_column("Válido até", style="magenta", width=12)
    table.add_column("Emissor", style="dim", width=25)

    for idx, cert in enumerate(certs_to_show, 1):
        documento = cert.cnpj or cert.cpf or "N/A"
        cn_display = cert.subject_cn[:32] + "..." if len(cert.subject_cn) > 35 else cert.subject_cn
        issuer_display = cert.issuer_cn[:22] + "..." if len(cert.issuer_cn) > 25 else cert.issuer_cn

        table.add_row(
            str(idx),
            cn_display,
            documento,
            cert.valid_to,
            issuer_display
        )

    console.print(table)

    # Solicitar seleção
    cert_num = Prompt.ask(
        "\n🎯 Selecione o número do certificado",
        choices=[str(i) for i in range(1, len(certs_to_show) + 1)],
        default="1"
    )

    selected_cert = certs_to_show[int(cert_num) - 1]

    # Mostrar detalhes do certificado selecionado
    details = f"""
[bold cyan]Certificado Selecionado:[/bold cyan]

[yellow]CN:[/yellow] {selected_cert.subject_cn}
[yellow]Documento:[/yellow] {selected_cert.cnpj or selected_cert.cpf or 'N/A'}
[yellow]Emissor:[/yellow] {selected_cert.issuer_cn}
[green]Válido até:[/green] {selected_cert.valid_to}
[magenta]Thumbprint:[/magenta] {selected_cert.thumbprint}
    """

    console.print(Panel(details, border_style="cyan"))

    if not Confirm.ask("\n✅ Confirma este certificado?", default=True):
        console.print("[yellow]Operação cancelada[/yellow]")
        return None, None

    return selected_cert, selected_cert.issuer_cn


def configure_registry(
    browser: str,
    cert_thumbprint: str,
    issuer_cn: str,
    url_pattern: str = "https://det.sit.trabalho.gov.br"
) -> bool:
    """
    Configura o registro do Windows.

    Args:
        browser: chrome ou edge
        cert_thumbprint: Thumbprint do certificado
        issuer_cn: Common Name do emissor
        url_pattern: Padrão de URL

    Returns:
        True se sucesso, False caso contrário
    """
    console.print(f"\n[bold cyan]⚙️  Configurando registro do Windows para {browser.upper()}...[/bold cyan]\n")

    configurator = RegistryConfigurator(browser)

    # Verificar se está como admin
    if not configurator._is_admin():
        console.print("[red]❌ ERRO: Este script precisa ser executado como Administrador![/red]\n")
        console.print("[yellow]📝 Como executar como Administrador:[/yellow]")
        console.print("   1. Abra o PowerShell ou CMD como Administrador")
        console.print("   2. Navegue até a pasta do projeto")
        console.print("   3. Execute: python scripts/setup_auto_certificate.py\n")
        return False

    # Configurar
    success = configurator.configure_auto_select(
        url_pattern=url_pattern,
        issuer_cn=issuer_cn
    )

    if success:
        console.print(f"\n[green]✅ Configuração concluída com sucesso![/green]\n")

        instructions = f"""
[bold]📋 Próximos Passos:[/bold]

1. [yellow]Feche TODOS os processos do {browser.title()}[/yellow]
   - Verifique no Gerenciador de Tarefas
   - Encerre todas as janelas e abas

2. [cyan]Abra o {browser.title()} novamente[/cyan]

3. [green]Acesse: {url_pattern}[/green]

4. [magenta]O certificado deve ser selecionado automaticamente![/magenta]

[dim]Se não funcionar, verifique:[/dim]
[dim]• O navegador foi completamente fechado e reaberto[/dim]
[dim]• Você tem permissões para acessar o certificado[/dim]
[dim]• O certificado está válido e instalado corretamente[/dim]
        """

        console.print(Panel(instructions, title="✅ Sucesso!", border_style="green"))
        return True

    else:
        console.print("\n[red]❌ Falha na configuração![/red]")
        return False


def remove_configuration(browser: str) -> bool:
    """
    Remove configuração do registro.

    Args:
        browser: chrome ou edge

    Returns:
        True se sucesso, False caso contrário
    """
    console.print(f"\n[bold yellow]🗑️  Removendo configuração do {browser.upper()}...[/bold yellow]\n")

    configurator = RegistryConfigurator(browser)

    if not configurator._is_admin():
        console.print("[red]❌ ERRO: Requer permissões de Administrador![/red]")
        return False

    success = configurator.remove_auto_select()

    if success:
        console.print("[green]✅ Configuração removida com sucesso![/green]")
    else:
        console.print("[red]❌ Falha ao remover configuração![/red]")

    return success


def verify_configuration(browser: str) -> None:
    """
    Verifica configuração atual do registro.

    Args:
        browser: chrome ou edge
    """
    console.print(f"\n[bold cyan]🔍 Verificando configuração do {browser.upper()}...[/bold cyan]\n")

    configurator = RegistryConfigurator(browser)
    config = configurator.get_current_config()

    if config:
        console.print("[green]✅ Configuração encontrada no registro:[/green]\n")
        console.print(f"[dim]{config}[/dim]\n")

        if configurator.verify_configuration():
            console.print("[green]✓ Configuração válida e ativa[/green]")
        else:
            console.print("[yellow]⚠️  Configuração pode estar incorreta[/yellow]")
    else:
        console.print("[yellow]⚠️  Nenhuma configuração de auto-seleção encontrada[/yellow]")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Configura auto-seleção de certificado digital para o DET',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Modo interativo (recomendado)
  python scripts/setup_auto_certificate.py

  # Configurar com thumbprint específico
  python scripts/setup_auto_certificate.py --browser chrome --thumbprint ABC123...

  # Verificar configuração atual
  python scripts/setup_auto_certificate.py --verify

  # Remover configuração
  python scripts/setup_auto_certificate.py --remove

IMPORTANTE: Execute como Administrador!
        """
    )

    parser.add_argument(
        '--browser',
        choices=['chrome', 'edge'],
        default='chrome',
        help='Navegador a configurar (padrão: chrome)'
    )

    parser.add_argument(
        '--thumbprint',
        help='Thumbprint do certificado (modo não-interativo)'
    )

    parser.add_argument(
        '--issuer',
        help='Common Name do emissor (ex: "AC SERASA RFB v5")'
    )

    parser.add_argument(
        '--remove',
        action='store_true',
        help='Remover configuração existente'
    )

    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verificar configuração atual'
    )

    args = parser.parse_args()

    # Banner
    console.print("\n[bold cyan]" + "=" * 70 + "[/bold cyan]")
    console.print("[bold cyan]  🔐 CONFIGURAÇÃO DE CERTIFICADO DIGITAL - Rob-DET 2.0[/bold cyan]")
    console.print("[bold cyan]" + "=" * 70 + "[/bold cyan]\n")

    # Verificar se está no Windows
    import platform
    if platform.system() != 'Windows':
        console.print("[red]❌ Este script só funciona no Windows![/red]")
        return 1

    # Verificar se é admin (exceto para --verify)
    if not args.verify and not check_admin():
        console.print("[red]❌ ERRO: Este script precisa ser executado como Administrador![/red]\n")
        console.print("[yellow]📝 Como executar:[/yellow]")
        console.print("   1. Clique com botão direito no PowerShell ou CMD")
        console.print("   2. Selecione 'Executar como Administrador'")
        console.print("   3. Navegue até a pasta do projeto")
        console.print("   4. Execute novamente este script\n")
        return 1

    try:
        if args.verify:
            # Verificar configuração
            verify_configuration(args.browser)

        elif args.remove:
            # Remover configuração
            if Confirm.ask(f"\n⚠️  Confirma remoção da configuração do {args.browser.upper()}?"):
                remove_configuration(args.browser)
            else:
                console.print("[yellow]Operação cancelada[/yellow]")

        elif args.thumbprint and args.issuer:
            # Modo direto (não-interativo)
            configure_registry(
                browser=args.browser,
                cert_thumbprint=args.thumbprint,
                issuer_cn=args.issuer
            )

        else:
            # Modo interativo (padrão)
            console.print("[bold]🎯 Modo Interativo - Seleção de Certificado[/bold]\n")

            # Selecionar certificado
            cert, issuer_cn = select_certificate_interactive()

            if not cert:
                return 1

            # Configurar registro
            success = configure_registry(
                browser=args.browser,
                cert_thumbprint=cert.thumbprint,
                issuer_cn=issuer_cn
            )

            if not success:
                return 1

    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Operação cancelada pelo usuário[/yellow]")
        return 130

    except Exception as e:
        console.print(f"\n[red]❌ Erro: {e}[/red]")
        if '--debug' in sys.argv:
            raise
        return 1

    console.print("\n[dim]Concluído![/dim]\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
