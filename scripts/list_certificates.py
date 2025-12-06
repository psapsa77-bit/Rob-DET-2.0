#!/usr/bin/env python3
"""
Script para listar certificados digitais instalados no Windows.

Uso:
    python scripts/list_certificates.py
    python scripts/list_certificates.py --cnpj 12345678000190
    python scripts/list_certificates.py --export certs.json
"""

import sys
import json
import argparse
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from src.auth.windows_cert_store import WindowsCertificateStore, CertificateInfo

console = Console()


def print_certificate_details(cert: CertificateInfo) -> None:
    """
    Exibe detalhes completos de um certificado.

    Args:
        cert: Certificado a exibir
    """
    status_emoji = "✅" if cert.is_valid else "❌"
    doc_type = "e-CNPJ" if cert.cnpj else "e-CPF" if cert.cpf else "Outro"
    documento = cert.cnpj or cert.cpf or "N/A"

    details = f"""
[bold cyan]Common Name:[/bold cyan] {cert.subject_cn}
[bold cyan]Emissor:[/bold cyan] {cert.issuer_cn}

[bold yellow]Tipo:[/bold yellow] {doc_type}
[bold yellow]Documento:[/bold yellow] {documento}

[bold green]Válido de:[/bold green] {cert.valid_from}
[bold green]Válido até:[/bold green] {cert.valid_to}
[bold green]Status:[/bold green] {status_emoji} {'Válido' if cert.is_valid else 'Expirado'}

[bold magenta]Serial Number:[/bold magenta] {cert.serial_number}
[bold magenta]Thumbprint:[/bold magenta] {cert.thumbprint}
[bold magenta]Store:[/bold magenta] {cert.store_location}
    """

    console.print(Panel(details, title=f"📜 Certificado #{cert.serial_number[:8]}", border_style="cyan"))


def list_all_certificates() -> None:
    """Lista todos os certificados instalados."""
    console.print("\n[bold cyan]🔍 Buscando certificados instalados...[/bold cyan]\n")

    store = WindowsCertificateStore()
    certs = store.list_certificates()

    if not certs:
        console.print("[yellow]⚠️  Nenhum certificado encontrado![/yellow]")
        console.print("\n[dim]Verifique se você tem certificados digitais instalados no Windows.[/dim]")
        return

    # Criar tabela
    table = Table(title=f"📋 Certificados Digitais ({len(certs)} encontrados)")
    table.add_column("#", style="dim", width=3)
    table.add_column("Common Name", style="cyan", no_wrap=False, width=35)
    table.add_column("Tipo", style="yellow", width=8)
    table.add_column("Documento", style="yellow", width=20)
    table.add_column("Válido até", style="green", width=12)
    table.add_column("Status", justify="center", width=8)

    for idx, cert in enumerate(certs, 1):
        doc_type = "e-CNPJ" if cert.cnpj else "e-CPF" if cert.cpf else "Outro"
        documento = cert.cnpj or cert.cpf or "N/A"
        status = "✅" if cert.is_valid else "❌"
        status_color = "green" if cert.is_valid else "red"

        # Truncar CN se muito longo
        cn_display = cert.subject_cn[:32] + "..." if len(cert.subject_cn) > 35 else cert.subject_cn

        table.add_row(
            str(idx),
            cn_display,
            doc_type,
            documento,
            cert.valid_to,
            f"[{status_color}]{status}[/{status_color}]"
        )

    console.print(table)

    # Estatísticas
    valid_count = sum(1 for c in certs if c.is_valid)
    cnpj_count = sum(1 for c in certs if c.cnpj)
    cpf_count = sum(1 for c in certs if c.cpf)
    expired_count = len(certs) - valid_count

    stats = f"""
[bold]Total de certificados:[/bold] {len(certs)}
[green]✅ Válidos:[/green] {valid_count}
[red]❌ Expirados:[/red] {expired_count}

[yellow]📊 Por tipo:[/yellow]
  • e-CNPJ: {cnpj_count}
  • e-CPF: {cpf_count}
  • Outros: {len(certs) - cnpj_count - cpf_count}
    """

    console.print(Panel(stats, title="📊 Estatísticas", border_style="green"))

    # Perguntar se deseja ver detalhes
    if Confirm.ask("\n🔎 Deseja ver detalhes de algum certificado?"):
        cert_num = Prompt.ask(
            "Digite o número do certificado",
            choices=[str(i) for i in range(1, len(certs) + 1)]
        )
        print_certificate_details(certs[int(cert_num) - 1])


def search_by_cnpj(cnpj: str) -> None:
    """
    Busca certificados por CNPJ.

    Args:
        cnpj: CNPJ a buscar
    """
    console.print(f"\n[bold cyan]🔍 Buscando certificados para CNPJ: {cnpj}[/bold cyan]\n")

    store = WindowsCertificateStore()
    certs = store.find_by_cnpj(cnpj)

    if not certs:
        console.print(f"[yellow]⚠️  Nenhum certificado encontrado para CNPJ {cnpj}[/yellow]")
        return

    console.print(f"[green]✅ Encontrados {len(certs)} certificado(s)[/green]\n")

    for cert in certs:
        print_certificate_details(cert)


def export_certificates(output_file: str) -> None:
    """
    Exporta lista de certificados para JSON.

    Args:
        output_file: Arquivo de saída
    """
    console.print(f"\n[bold cyan]💾 Exportando certificados para {output_file}...[/bold cyan]\n")

    store = WindowsCertificateStore()
    certs = store.list_certificates()

    if not certs:
        console.print("[yellow]⚠️  Nenhum certificado para exportar[/yellow]")
        return

    # Converter para dicionário
    certs_data = []
    for cert in certs:
        certs_data.append({
            'subject_cn': cert.subject_cn,
            'issuer_cn': cert.issuer_cn,
            'serial_number': cert.serial_number,
            'thumbprint': cert.thumbprint,
            'valid_from': cert.valid_from,
            'valid_to': cert.valid_to,
            'cnpj': cert.cnpj,
            'cpf': cert.cpf,
            'is_valid': cert.is_valid,
            'store_location': cert.store_location
        })

    # Salvar JSON
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(certs_data),
            'certificates': certs_data
        }, f, indent=2, ensure_ascii=False)

    console.print(f"[green]✅ {len(certs_data)} certificados exportados para {output_file}[/green]")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Lista certificados digitais instalados no Windows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python scripts/list_certificates.py
  python scripts/list_certificates.py --cnpj 12.345.678/0001-90
  python scripts/list_certificates.py --export data/certificates.json
        """
    )

    parser.add_argument(
        '--cnpj',
        help='Buscar certificados de um CNPJ específico'
    )

    parser.add_argument(
        '--export',
        help='Exportar lista de certificados para arquivo JSON'
    )

    parser.add_argument(
        '--valid-only',
        action='store_true',
        help='Listar apenas certificados válidos'
    )

    args = parser.parse_args()

    # Banner
    console.print("\n[bold cyan]" + "=" * 60 + "[/bold cyan]")
    console.print("[bold cyan]  📜 GERENCIADOR DE CERTIFICADOS DIGITAIS - Rob-DET 2.0[/bold cyan]")
    console.print("[bold cyan]" + "=" * 60 + "[/bold cyan]\n")

    try:
        if args.cnpj:
            # Buscar por CNPJ
            search_by_cnpj(args.cnpj)

        elif args.export:
            # Exportar para JSON
            export_certificates(args.export)

        else:
            # Listar todos
            list_all_certificates()

            # Se flag --valid-only, filtrar
            if args.valid_only:
                console.print("\n[dim]Mostrando apenas certificados válidos[/dim]")

    except Exception as e:
        console.print(f"\n[red]❌ Erro: {e}[/red]")
        if '--debug' in sys.argv:
            raise
        return 1

    console.print("\n[dim]Concluído![/dim]\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
