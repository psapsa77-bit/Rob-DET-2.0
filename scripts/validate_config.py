#!/usr/bin/env python3
"""
Script de Validação da Configuração - Rob-DET 2.0

Valida toda a configuração do ambiente antes de executar o robô:
- Dependências instaladas
- Arquivos de configuração
- Certificados digitais
- Registro do Windows
- Acesso ao portal DET

Uso:
    python scripts/validate_config.py
    python scripts/validate_config.py --full  # Inclui teste de acesso ao DET
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


class ConfigValidator:
    """Validador de configuração."""

    def __init__(self):
        """Inicializa o validador."""
        self.project_root = Path(__file__).parent.parent
        self.checks: List[Tuple[str, bool, str]] = []  # (nome, sucesso, mensagem)

    def add_check(self, name: str, success: bool, message: str = ""):
        """
        Adiciona resultado de verificação.

        Args:
            name: Nome da verificação
            success: Se passou
            message: Mensagem adicional
        """
        self.checks.append((name, success, message))

    def check_python_packages(self) -> bool:
        """Verifica se pacotes Python estão instalados."""
        console.print("\n[bold cyan]📦 Verificando pacotes Python...[/bold cyan]")

        required_packages = [
            'selenium',
            'webdriver_manager',
            'loguru',
            'rich',
            'pydantic',
            'cryptography',
            'beautifulsoup4',
            'pyyaml',
            'python-dotenv'
        ]

        all_installed = True

        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                console.print(f"[green]  ✓ {package}[/green]")
            except ImportError:
                console.print(f"[red]  ✗ {package} - NÃO INSTALADO[/red]")
                all_installed = False

        self.add_check(
            "Pacotes Python",
            all_installed,
            "Todos os pacotes instalados" if all_installed else "Pacotes faltando"
        )

        return all_installed

    def check_config_files(self) -> bool:
        """Verifica arquivos de configuração."""
        console.print("\n[bold cyan]📄 Verificando arquivos de configuração...[/bold cyan]")

        files_to_check = {
            '.env': False,  # False = opcional
            'config/settings.yaml': True,  # True = obrigatório
            'config/clients.yaml': False,
        }

        all_ok = True

        for file_path, required in files_to_check.items():
            full_path = self.project_root / file_path
            exists = full_path.exists()

            if exists:
                console.print(f"[green]  ✓ {file_path}[/green]")
            else:
                if required:
                    console.print(f"[red]  ✗ {file_path} - OBRIGATÓRIO[/red]")
                    all_ok = False
                else:
                    console.print(f"[yellow]  ⚠ {file_path} - opcional[/yellow]")

        self.add_check(
            "Arquivos de configuração",
            all_ok,
            "Todos os arquivos encontrados" if all_ok else "Arquivos faltando"
        )

        return all_ok

    def check_directories(self) -> bool:
        """Verifica se diretórios necessários existem."""
        console.print("\n[bold cyan]📁 Verificando diretórios...[/bold cyan]")

        directories = [
            'logs',
            'data',
            'config',
            'src',
        ]

        all_ok = True

        for dir_name in directories:
            dir_path = self.project_root / dir_name
            exists = dir_path.exists() and dir_path.is_dir()

            if exists:
                console.print(f"[green]  ✓ {dir_name}/[/green]")
            else:
                console.print(f"[red]  ✗ {dir_name}/ - NÃO ENCONTRADO[/red]")
                all_ok = False

        self.add_check(
            "Diretórios",
            all_ok,
            "Estrutura OK" if all_ok else "Diretórios faltando"
        )

        return all_ok

    def check_certificates(self) -> bool:
        """Verifica certificados digitais."""
        console.print("\n[bold cyan]🔐 Verificando certificados digitais...[/bold cyan]")

        try:
            import platform
            if platform.system() != 'Windows':
                console.print("[yellow]  ⚠ Não é Windows - pulando verificação[/yellow]")
                self.add_check("Certificados", True, "N/A (não-Windows)")
                return True

            from src.auth.windows_cert_store import WindowsCertificateStore

            store = WindowsCertificateStore()
            certs = store.get_valid_certificates()

            if not certs:
                console.print("[red]  ✗ Nenhum certificado válido encontrado[/red]")
                self.add_check("Certificados", False, "Nenhum certificado válido")
                return False

            ecnpj_count = sum(1 for c in certs if c.cnpj)
            console.print(f"[green]  ✓ {len(certs)} certificados válidos ({ecnpj_count} e-CNPJ)[/green]")

            self.add_check(
                "Certificados",
                True,
                f"{ecnpj_count} e-CNPJ válidos"
            )

            return True

        except Exception as e:
            console.print(f"[red]  ✗ Erro: {e}[/red]")
            self.add_check("Certificados", False, str(e))
            return False

    def check_registry_config(self) -> bool:
        """Verifica configuração do registro do Windows."""
        console.print("\n[bold cyan]🔧 Verificando registro do Windows...[/bold cyan]")

        try:
            import platform
            if platform.system() != 'Windows':
                console.print("[yellow]  ⚠ Não é Windows - pulando verificação[/yellow]")
                self.add_check("Registro", True, "N/A (não-Windows)")
                return True

            from src.auth.registry_config import RegistryConfigurator

            # Verificar Chrome
            chrome_config = RegistryConfigurator('chrome')
            chrome_ok = chrome_config.verify_configuration()

            if chrome_ok:
                console.print("[green]  ✓ Chrome - auto-seleção configurada[/green]")
            else:
                console.print("[yellow]  ⚠ Chrome - auto-seleção NÃO configurada[/yellow]")

            # Verificar Edge
            try:
                edge_config = RegistryConfigurator('edge')
                edge_ok = edge_config.verify_configuration()

                if edge_ok:
                    console.print("[green]  ✓ Edge - auto-seleção configurada[/green]")
                else:
                    console.print("[dim]  ○ Edge - auto-seleção não configurada[/dim]")
            except:
                edge_ok = False

            at_least_one = chrome_ok or edge_ok

            self.add_check(
                "Registro Windows",
                at_least_one,
                "Configurado" if at_least_one else "Não configurado"
            )

            return True  # Não bloqueia se não configurado

        except Exception as e:
            console.print(f"[red]  ✗ Erro: {e}[/red]")
            self.add_check("Registro Windows", False, str(e))
            return True  # Não bloqueia

    def check_chrome_driver(self) -> bool:
        """Verifica se ChromeDriver está disponível."""
        console.print("\n[bold cyan]🌐 Verificando ChromeDriver...[/bold cyan]")

        try:
            from selenium import webdriver
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service

            # Tentar obter ChromeDriver
            driver_path = ChromeDriverManager().install()
            console.print(f"[green]  ✓ ChromeDriver encontrado[/green]")
            console.print(f"[dim]    {driver_path}[/dim]")

            self.add_check("ChromeDriver", True, "Disponível")
            return True

        except Exception as e:
            console.print(f"[red]  ✗ Erro: {e}[/red]")
            self.add_check("ChromeDriver", False, str(e))
            return False

    def test_det_access(self) -> bool:
        """Testa acesso ao portal DET (opcional)."""
        console.print("\n[bold cyan]🌍 Testando acesso ao portal DET...[/bold cyan]")

        try:
            import requests

            response = requests.get(
                'https://det.sit.trabalho.gov.br/',
                timeout=10,
                allow_redirects=True
            )

            if response.status_code == 200:
                console.print("[green]  ✓ Portal DET acessível[/green]")
                self.add_check("Acesso DET", True, "Portal acessível")
                return True
            else:
                console.print(f"[yellow]  ⚠ Status: {response.status_code}[/yellow]")
                self.add_check("Acesso DET", False, f"HTTP {response.status_code}")
                return False

        except Exception as e:
            console.print(f"[red]  ✗ Erro: {e}[/red]")
            self.add_check("Acesso DET", False, str(e))
            return False

    def print_summary(self):
        """Exibe resumo das verificações."""
        console.print("\n" + "=" * 70)
        console.print("[bold cyan]📊 RESUMO DA VALIDAÇÃO[/bold cyan]")
        console.print("=" * 70 + "\n")

        # Criar tabela
        table = Table(title="Resultados")
        table.add_column("Verificação", style="cyan", no_wrap=False)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Detalhes", style="dim")

        for name, success, message in self.checks:
            status = "✅" if success else "❌"
            status_color = "green" if success else "red"

            table.add_row(
                name,
                f"[{status_color}]{status}[/{status_color}]",
                message
            )

        console.print(table)

        # Estatísticas
        total = len(self.checks)
        passed = sum(1 for _, success, _ in self.checks if success)
        failed = total - passed

        if failed == 0:
            console.print(f"\n[bold green]✅ Todas as {total} verificações passaram![/bold green]")
            console.print("\n[green]🎉 Ambiente configurado corretamente![/green]")
            console.print("[dim]Você pode executar: python main.py[/dim]")
        else:
            console.print(f"\n[bold yellow]⚠️  {passed}/{total} verificações passaram[/bold yellow]")
            console.print(f"[red]❌ {failed} verificação(ões) falharam[/red]\n")

            console.print("[yellow]📝 Corrija os problemas acima antes de executar o robô[/yellow]")
            console.print("[dim]Execute: python scripts/setup_environment.py[/dim]")

        return failed == 0

    def run(self, full: bool = False) -> int:
        """
        Executa validação completa.

        Args:
            full: Se True, inclui testes opcionais

        Returns:
            0 se tudo OK, 1 se problemas
        """
        # Banner
        console.print("\n[bold cyan]" + "=" * 70 + "[/bold cyan]")
        console.print("[bold cyan]  ✅ VALIDAÇÃO DE CONFIGURAÇÃO - Rob-DET 2.0[/bold cyan]")
        console.print("[bold cyan]" + "=" * 70 + "[/bold cyan]")

        # Executar verificações
        self.check_python_packages()
        self.check_config_files()
        self.check_directories()
        self.check_certificates()
        self.check_registry_config()
        self.check_chrome_driver()

        if full:
            self.test_det_access()

        # Resumo
        all_ok = self.print_summary()

        return 0 if all_ok else 1


def main():
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Valida configuração do Rob-DET 2.0'
    )

    parser.add_argument(
        '--full',
        action='store_true',
        help='Executa verificações completas (inclui teste de acesso ao DET)'
    )

    args = parser.parse_args()

    validator = ConfigValidator()
    return validator.run(full=args.full)


if __name__ == '__main__':
    sys.exit(main())
