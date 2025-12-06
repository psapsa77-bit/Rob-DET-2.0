#!/usr/bin/env python3
"""
Script de Setup Completo do Ambiente - Rob-DET 2.0

Configura todo o ambiente necessário para executar o robô:
1. Verifica e instala dependências
2. Configura arquivos de ambiente (.env, clients.yaml)
3. Lista e configura certificados digitais
4. Configura auto-seleção de certificado
5. Valida configuração final

Uso:
    python scripts/setup_environment.py
    python scripts/setup_environment.py --skip-cert  # Pula configuração de certificado
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class EnvironmentSetup:
    """Gerenciador de setup do ambiente."""

    def __init__(self):
        """Inicializa o setup."""
        self.project_root = Path(__file__).parent.parent
        self.errors = []
        self.warnings = []

    def print_banner(self):
        """Exibe banner do setup."""
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║              🚀 ROB-DET 2.0 - SETUP DO AMBIENTE                  ║
║                                                                  ║
║         Configuração automática de certificado digital           ║
║                   e ambiente de execução                         ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """
        console.print(banner, style="bold cyan")

    def check_python_version(self) -> bool:
        """Verifica versão do Python."""
        console.print("\n[bold cyan]1️⃣  Verificando versão do Python...[/bold cyan]")

        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 11):
            console.print(f"[red]❌ Python {version.major}.{version.minor} detectado[/red]")
            console.print("[yellow]⚠️  Python 3.11+ é recomendado[/yellow]")
            self.warnings.append("Python < 3.11")
            return False

        console.print(f"[green]✅ Python {version.major}.{version.minor}.{version.micro}[/green]")
        return True

    def check_platform(self) -> bool:
        """Verifica se está no Windows."""
        console.print("\n[bold cyan]2️⃣  Verificando sistema operacional...[/bold cyan]")

        import platform
        if platform.system() != 'Windows':
            console.print(f"[red]❌ Sistema: {platform.system()}[/red]")
            console.print("[yellow]⚠️  Este robô requer Windows (certificado A1)[/yellow]")
            self.errors.append("Não é Windows")
            return False

        console.print(f"[green]✅ Windows {platform.release()}[/green]")
        return True

    def install_dependencies(self) -> bool:
        """Instala dependências do requirements.txt."""
        console.print("\n[bold cyan]3️⃣  Instalando dependências Python...[/bold cyan]")

        requirements_file = self.project_root / 'requirements.txt'

        if not requirements_file.exists():
            console.print("[red]❌ requirements.txt não encontrado[/red]")
            self.errors.append("requirements.txt não encontrado")
            return False

        # Perguntar se deve instalar
        if not Confirm.ask("\n📦 Instalar dependências do requirements.txt?", default=True):
            console.print("[yellow]⚠️  Pulando instalação de dependências[/yellow]")
            self.warnings.append("Dependências não instaladas")
            return True

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Instalando pacotes...", total=None)

                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    console.print(f"[red]❌ Erro ao instalar dependências:[/red]")
                    console.print(f"[dim]{result.stderr}[/dim]")
                    self.errors.append("Falha ao instalar dependências")
                    return False

            console.print("[green]✅ Dependências instaladas com sucesso[/green]")
            return True

        except Exception as e:
            console.print(f"[red]❌ Erro: {e}[/red]")
            self.errors.append(str(e))
            return False

    def setup_env_file(self) -> bool:
        """Configura arquivo .env."""
        console.print("\n[bold cyan]4️⃣  Configurando arquivo .env...[/bold cyan]")

        env_file = self.project_root / '.env'
        env_example = self.project_root / '.env.example'

        if env_file.exists():
            console.print("[yellow]⚠️  Arquivo .env já existe[/yellow]")
            if not Confirm.ask("Deseja sobrescrever?", default=False):
                console.print("[dim]Mantendo .env existente[/dim]")
                return True

        if not env_example.exists():
            console.print("[red]❌ .env.example não encontrado[/red]")
            self.errors.append(".env.example não encontrado")
            return False

        # Copiar .env.example para .env
        shutil.copy(env_example, env_file)
        console.print(f"[green]✅ Arquivo .env criado: {env_file}[/green]")

        # Sugerir edição
        console.print("\n[yellow]📝 IMPORTANTE: Edite o arquivo .env com suas configurações[/yellow]")
        console.print(f"[dim]   Caminho: {env_file}[/dim]")

        return True

    def setup_clients_file(self) -> bool:
        """Configura arquivo clients.yaml."""
        console.print("\n[bold cyan]5️⃣  Configurando arquivo clients.yaml...[/bold cyan]")

        clients_file = self.project_root / 'config' / 'clients.yaml'
        clients_example = self.project_root / 'config' / 'clients.yaml.example'

        if clients_file.exists():
            console.print("[yellow]⚠️  Arquivo clients.yaml já existe[/yellow]")
            if not Confirm.ask("Deseja sobrescrever?", default=False):
                console.print("[dim]Mantendo clients.yaml existente[/dim]")
                return True

        if not clients_example.exists():
            console.print("[red]❌ clients.yaml.example não encontrado[/red]")
            self.errors.append("clients.yaml.example não encontrado")
            return False

        # Copiar exemplo
        shutil.copy(clients_example, clients_file)
        console.print(f"[green]✅ Arquivo clients.yaml criado: {clients_file}[/green]")

        console.print("\n[yellow]📝 IMPORTANTE: Edite clients.yaml com os CNPJs dos seus clientes[/yellow]")
        console.print(f"[dim]   Caminho: {clients_file}[/dim]")

        return True

    def list_certificates(self) -> bool:
        """Lista certificados disponíveis."""
        console.print("\n[bold cyan]6️⃣  Verificando certificados digitais instalados...[/bold cyan]")

        try:
            from src.auth.windows_cert_store import WindowsCertificateStore

            store = WindowsCertificateStore()
            certs = store.get_valid_certificates()

            if not certs:
                console.print("[red]❌ Nenhum certificado válido encontrado[/red]")
                console.print("\n[yellow]📝 Instale um certificado digital A1 antes de continuar[/yellow]")
                self.errors.append("Nenhum certificado válido")
                return False

            ecnpj_count = sum(1 for c in certs if c.cnpj)
            console.print(f"[green]✅ Encontrados {len(certs)} certificados válidos ({ecnpj_count} e-CNPJ)[/green]")

            # Mostrar resumo
            if ecnpj_count > 0:
                console.print("\n[bold]Certificados e-CNPJ encontrados:[/bold]")
                for cert in [c for c in certs if c.cnpj][:3]:  # Mostrar até 3
                    console.print(f"  • {cert.subject_cn[:50]} (CNPJ: {cert.cnpj})")

                if ecnpj_count > 3:
                    console.print(f"  ... e mais {ecnpj_count - 3}")

            return True

        except Exception as e:
            console.print(f"[red]❌ Erro ao listar certificados: {e}[/red]")
            self.errors.append(str(e))
            return False

    def configure_auto_certificate(self) -> bool:
        """Configura auto-seleção de certificado."""
        console.print("\n[bold cyan]7️⃣  Configuração de auto-seleção de certificado...[/bold cyan]")

        if not Confirm.ask("\n🔐 Deseja configurar auto-seleção de certificado agora?", default=True):
            console.print("[yellow]⚠️  Pulando configuração de certificado[/yellow]")
            console.print("[dim]Execute depois: python scripts/setup_auto_certificate.py[/dim]")
            self.warnings.append("Certificado não configurado")
            return True

        # Verificar se é admin
        import ctypes
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except:
            is_admin = False

        if not is_admin:
            console.print("\n[red]❌ Requer permissões de Administrador para configurar registro[/red]")
            console.print("\n[yellow]📝 Execute este comando como Administrador:[/yellow]")
            console.print("[cyan]   python scripts/setup_auto_certificate.py[/cyan]")
            self.warnings.append("Não executado como admin - certificado não configurado")
            return True

        # Executar script de configuração
        console.print("\n[dim]Executando script de configuração de certificado...[/dim]")
        console.print("[yellow]⚠️  Siga as instruções interativas[/yellow]\n")

        try:
            result = subprocess.run(
                [sys.executable, 'scripts/setup_auto_certificate.py'],
                cwd=self.project_root
            )

            if result.returncode == 0:
                console.print("\n[green]✅ Certificado configurado[/green]")
                return True
            else:
                console.print("\n[yellow]⚠️  Configuração de certificado não concluída[/yellow]")
                self.warnings.append("Configuração de certificado falhou")
                return True

        except Exception as e:
            console.print(f"\n[red]❌ Erro: {e}[/red]")
            self.warnings.append(str(e))
            return True

    def create_directories(self) -> bool:
        """Cria diretórios necessários."""
        console.print("\n[bold cyan]8️⃣  Criando diretórios do projeto...[/bold cyan]")

        directories = [
            'logs',
            'logs/screenshots',
            'data',
            'data/exports',
            'certs',
        ]

        for dir_name in directories:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            console.print(f"[dim]  ✓ {dir_name}/[/dim]")

        console.print("[green]✅ Diretórios criados[/green]")
        return True

    def print_summary(self):
        """Exibe resumo do setup."""
        console.print("\n" + "=" * 70)
        console.print("[bold cyan]📊 RESUMO DO SETUP[/bold cyan]")
        console.print("=" * 70 + "\n")

        if not self.errors and not self.warnings:
            console.print("[bold green]✅ Setup concluído com sucesso![/bold green]\n")

            next_steps = """
[bold]🎯 Próximos Passos:[/bold]

1. [yellow]Edite o arquivo .env[/yellow]
   Caminho: .env
   Configure: CERT_PATH, navegador, etc.

2. [yellow]Edite o arquivo clients.yaml[/yellow]
   Caminho: config/clients.yaml
   Adicione os CNPJs dos seus clientes

3. [cyan]Teste a configuração:[/cyan]
   python scripts/list_certificates.py

4. [green]Execute o robô:[/green]
   python main.py --debug

[dim]Documentação completa: README.md e ANALISE_TECNICA.md[/dim]
            """

            console.print(Panel(next_steps, title="✅ Sucesso!", border_style="green"))

        else:
            if self.errors:
                console.print("[bold red]❌ Erros encontrados:[/bold red]")
                for error in self.errors:
                    console.print(f"  • {error}")
                console.print()

            if self.warnings:
                console.print("[bold yellow]⚠️  Avisos:[/bold yellow]")
                for warning in self.warnings:
                    console.print(f"  • {warning}")
                console.print()

            console.print("[yellow]⚠️  Setup concluído com ressalvas[/yellow]")
            console.print("[dim]Corrija os erros acima antes de executar o robô[/dim]")

    def run(self, skip_cert: bool = False) -> int:
        """
        Executa o setup completo.

        Args:
            skip_cert: Se True, pula configuração de certificado

        Returns:
            0 se sucesso, 1 se erro
        """
        self.print_banner()

        steps = [
            self.check_python_version,
            self.check_platform,
            self.install_dependencies,
            self.setup_env_file,
            self.setup_clients_file,
            self.create_directories,
            self.list_certificates,
        ]

        if not skip_cert:
            steps.append(self.configure_auto_certificate)

        # Executar steps
        for step in steps:
            try:
                if not step():
                    # Continuar mesmo com falhas não-críticas
                    pass
            except KeyboardInterrupt:
                console.print("\n\n[yellow]⚠️  Setup interrompido pelo usuário[/yellow]")
                return 130
            except Exception as e:
                console.print(f"\n[red]❌ Erro inesperado: {e}[/red]")
                self.errors.append(str(e))

        # Resumo
        self.print_summary()

        return 0 if not self.errors else 1


def main():
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Setup completo do ambiente Rob-DET 2.0'
    )

    parser.add_argument(
        '--skip-cert',
        action='store_true',
        help='Pular configuração de certificado'
    )

    args = parser.parse_args()

    setup = EnvironmentSetup()
    return setup.run(skip_cert=args.skip_cert)


if __name__ == '__main__':
    sys.exit(main())
