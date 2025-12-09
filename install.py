#!/usr/bin/env python3
"""
Instalador Automático - Rob-DET 2.0

Instalador interativo e amigável para configuração inicial do robô.
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from typing import Optional, List

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


def exibir_boas_vindas():
    """Exibe mensagem de boas-vindas."""
    console.clear()

    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║                    🤖 ROB-DET 2.0                             ║
    ║                                                               ║
    ║        Robô de Automação do Portal DET                       ║
    ║        Instalador Automático e Amigável                      ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """

    console.print(banner, style="bold cyan")
    console.print()
    console.print("Bem-vindo ao instalador do Rob-DET 2.0! 👋", style="bold green")
    console.print()
    console.print("Este instalador irá guiá-lo através de todos os passos necessários")
    console.print("para configurar e executar o robô. Não se preocupe, é bem simples!")
    console.print()

    if not Confirm.ask("Deseja continuar com a instalação?", default=True):
        console.print("\n❌ Instalação cancelada pelo usuário.", style="yellow")
        sys.exit(0)


def verificar_python():
    """Verifica se Python está instalado e na versão correta."""
    console.print("\n[bold cyan]📋 Passo 1: Verificando Python[/bold cyan]")

    try:
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"

        if version.major >= 3 and version.minor >= 11:
            console.print(f"✅ Python {version_str} encontrado!", style="green")
            return True
        else:
            console.print(f"❌ Python {version_str} é muito antigo.", style="red")
            console.print("   Você precisa do Python 3.11 ou superior.")
            console.print("\n   👉 Baixe em: https://www.python.org/downloads/")
            return False
    except Exception as e:
        console.print(f"❌ Erro ao verificar Python: {e}", style="red")
        return False


def verificar_pip():
    """Verifica se pip está disponível."""
    console.print("\n[bold cyan]📦 Passo 2: Verificando pip[/bold cyan]")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        console.print(f"✅ pip encontrado: {result.stdout.strip()}", style="green")
        return True
    except subprocess.CalledProcessError:
        console.print("❌ pip não encontrado!", style="red")
        console.print("\n   👉 Instale com: python -m ensurepip --upgrade")
        return False


def instalar_dependencias():
    """Instala dependências do requirements.txt."""
    console.print("\n[bold cyan]📚 Passo 3: Instalando Dependências[/bold cyan]")

    requirements_file = Path("requirements.txt")

    if not requirements_file.exists():
        console.print("❌ Arquivo requirements.txt não encontrado!", style="red")
        return False

    console.print("Instalando pacotes Python... Isso pode demorar alguns minutos.")
    console.print("☕ Aproveite para pegar um café!", style="yellow")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Instalando pacotes...", total=None)

            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                console.print("✅ Dependências instaladas com sucesso!", style="green")
                return True
            else:
                console.print("❌ Erro ao instalar dependências:", style="red")
                console.print(result.stderr)
                return False

    except Exception as e:
        console.print(f"❌ Erro: {e}", style="red")
        return False


def criar_estrutura_pastas():
    """Cria estrutura de pastas necessárias."""
    console.print("\n[bold cyan]📁 Passo 4: Criando Estrutura de Pastas[/bold cyan]")

    pastas = [
        "config",
        "logs",
        "relatorios",
        "downloads",
        "screenshots",
        "certs"
    ]

    for pasta in pastas:
        path = Path(pasta)
        if not path.exists():
            path.mkdir(parents=True)
            console.print(f"  ✅ Criada: {pasta}/", style="green")
        else:
            console.print(f"  ℹ️  Já existe: {pasta}/", style="blue")

    return True


def configurar_certificado():
    """Guia o usuário na configuração do certificado."""
    console.print("\n[bold cyan]🔐 Passo 5: Configurando Certificado Digital[/bold cyan]")

    console.print("\n[yellow]IMPORTANTE:[/yellow] Você precisa de um Certificado Digital A1 (e-CNPJ ou e-CPF).")
    console.print("O certificado deve estar instalado no Windows.")

    if not Confirm.ask("\nVocê já tem o certificado instalado?", default=False):
        console.print("\n📖 Como instalar o certificado:")
        console.print("  1. Abra o arquivo .pfx do certificado")
        console.print("  2. Siga o assistente de importação")
        console.print("  3. Digite a senha do certificado")
        console.print("  4. Escolha 'Repositório de Usuário Pessoal'")
        console.print("\n  👉 Depois de instalar, execute este instalador novamente.")
        return False

    # Listar certificados
    console.print("\n📜 Listando certificados instalados...")

    try:
        result = subprocess.run(
            [sys.executable, "scripts/list_certificates.py"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            console.print(result.stdout)

            if Confirm.ask("\nDeseja configurar auto-seleção de certificado?", default=True):
                console.print("\n⚙️  Configurando auto-seleção...")

                result = subprocess.run(
                    [sys.executable, "scripts/setup_auto_certificate.py"],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    console.print("✅ Auto-seleção configurada!", style="green")
                    return True
                else:
                    console.print("⚠️  Não foi possível configurar auto-seleção.", style="yellow")
                    console.print("   O robô tentará selecionar automaticamente durante a execução.")
                    return True
        else:
            console.print("⚠️  Não foi possível listar certificados.", style="yellow")
            console.print("   Certifique-se de que o certificado está instalado.")
            return Confirm.ask("\nDeseja continuar mesmo assim?", default=True)

    except Exception as e:
        console.print(f"⚠️  Erro ao configurar certificado: {e}", style="yellow")
        return Confirm.ask("\nDeseja continuar mesmo assim?", default=True)


def configurar_clientes():
    """Guia o usuário na configuração de clientes."""
    console.print("\n[bold cyan]👥 Passo 6: Configurando Clientes[/bold cyan]")

    console.print("\nVamos adicionar os clientes (CNPJs) que você quer monitorar.")
    console.print("[yellow]Lembre-se:[/yellow] Você precisa ter procuração eletrônica ativa para cada CNPJ!")

    clientes = []

    while True:
        console.print(f"\n[bold]Cliente #{len(clientes) + 1}[/bold]")

        cnpj = Prompt.ask("  Digite o CNPJ (apenas números ou formatado)")
        if not cnpj:
            break

        # Limpar CNPJ
        cnpj_numeros = ''.join(filter(str.isdigit, cnpj))

        if len(cnpj_numeros) != 14:
            console.print("  ❌ CNPJ inválido! Deve ter 14 dígitos.", style="red")
            continue

        razao_social = Prompt.ask("  Razão Social da empresa")
        if not razao_social:
            razao_social = f"Empresa {cnpj_numeros[:8]}"

        prioridade = Prompt.ask(
            "  Prioridade",
            choices=["alta", "normal", "baixa"],
            default="normal"
        )

        # Formatar CNPJ
        cnpj_formatado = f"{cnpj_numeros[:2]}.{cnpj_numeros[2:5]}.{cnpj_numeros[5:8]}/{cnpj_numeros[8:12]}-{cnpj_numeros[12:]}"

        clientes.append({
            "cnpj": cnpj_formatado,
            "razao_social": razao_social,
            "ativo": True,
            "prioridade": prioridade
        })

        console.print(f"  ✅ Cliente adicionado: {razao_social}", style="green")

        if not Confirm.ask("\nDeseja adicionar outro cliente?", default=True):
            break

    if not clientes:
        console.print("\n⚠️  Nenhum cliente adicionado. Adicionando exemplo...", style="yellow")
        clientes.append({
            "cnpj": "12.345.678/0001-90",
            "razao_social": "Empresa Exemplo Ltda",
            "ativo": False,
            "prioridade": "normal"
        })

    # Salvar clientes.json
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    arquivo_clientes = config_dir / "clientes.json"

    with open(arquivo_clientes, 'w', encoding='utf-8') as f:
        json.dump({"clientes": clientes}, f, indent=2, ensure_ascii=False)

    console.print(f"\n✅ Arquivo salvo: {arquivo_clientes}", style="green")
    return True


def configurar_settings():
    """Guia o usuário na configuração geral."""
    console.print("\n[bold cyan]⚙️  Passo 7: Configurações Gerais[/bold cyan]")

    # Carregar template
    template_file = Path("config/settings.json.example")
    if template_file.exists():
        with open(template_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    else:
        # Settings padrão
        settings = {
            "execucao": {
                "horarios": [],
                "dias_semana": [0, 1, 2, 3, 4],
                "timeout_por_cliente": 180,
                "apenas_nao_lidas": True
            },
            "chrome": {
                "headless": False,
                "download_path": "./downloads"
            },
            "notificacoes": {
                "email_ativo": False,
                "email_servidor": "smtp.gmail.com",
                "email_porta": 587,
                "email_remetente": "",
                "email_senha": "",
                "email_destinatarios": []
            },
            "logs": {
                "nivel": "INFO",
                "arquivo": "logs/robo_det.log"
            }
        }

    # Horários de execução
    console.print("\n📅 [bold]Horários de Execução[/bold]")
    console.print("Em que horários você quer que o robô execute automaticamente?")
    console.print("(Formato: HH:MM, exemplo: 08:00)")

    horarios = []
    exemplos = ["08:00", "14:00", "18:00"]

    for i, exemplo in enumerate(exemplos, 1):
        if Confirm.ask(f"\nAdicionar horário {exemplo}?", default=(i == 1)):
            horarios.append(exemplo)

    if Confirm.ask("\nDeseja adicionar mais horários manualmente?", default=False):
        while True:
            horario = Prompt.ask("  Horário (HH:MM) ou Enter para finalizar")
            if not horario:
                break

            try:
                h, m = horario.split(':')
                if 0 <= int(h) < 24 and 0 <= int(m) < 60:
                    horarios.append(horario)
                    console.print(f"  ✅ Horário {horario} adicionado", style="green")
                else:
                    console.print("  ❌ Horário inválido!", style="red")
            except:
                console.print("  ❌ Formato inválido! Use HH:MM", style="red")

    settings["execucao"]["horarios"] = horarios if horarios else ["08:00", "14:00"]

    # Modo headless
    console.print("\n🖥️  [bold]Modo de Execução[/bold]")
    settings["chrome"]["headless"] = not Confirm.ask(
        "Deseja ver o navegador enquanto o robô executa? (Recomendado para iniciantes)",
        default=True
    )

    if settings["chrome"]["headless"]:
        console.print("  ℹ️  O robô executará em modo invisível (headless)")
    else:
        console.print("  ℹ️  O navegador ficará visível durante a execução")

    # Email (simplificado)
    console.print("\n📧 [bold]Notificações por Email[/bold]")
    settings["notificacoes"]["email_ativo"] = Confirm.ask(
        "Deseja receber notificações por email?",
        default=False
    )

    if settings["notificacoes"]["email_ativo"]:
        console.print("\n[yellow]Para configurar email:[/yellow]")
        console.print("  1. Use Gmail com senha de app: https://myaccount.google.com/apppasswords")
        console.print("  2. Ou Outlook com senha normal")

        settings["notificacoes"]["email_remetente"] = Prompt.ask("\n  Seu email")
        settings["notificacoes"]["email_senha"] = Prompt.ask("  Senha (não será exibida)", password=True)

        destinatarios_str = Prompt.ask("  Emails que receberão notificações (separados por vírgula)")
        settings["notificacoes"]["email_destinatarios"] = [
            email.strip() for email in destinatarios_str.split(',') if email.strip()
        ]

    # Salvar settings.json
    config_file = Path("config/settings.json")

    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

    console.print(f"\n✅ Configurações salvas: {config_file}", style="green")
    return True


def resumo_instalacao():
    """Exibe resumo da instalação."""
    console.print("\n" + "=" * 60)
    console.print("[bold green]🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO![/bold green]")
    console.print("=" * 60)

    console.print("\n[bold]📝 Resumo:[/bold]")
    console.print("  ✅ Dependências instaladas")
    console.print("  ✅ Estrutura de pastas criada")
    console.print("  ✅ Certificado configurado")
    console.print("  ✅ Clientes configurados")
    console.print("  ✅ Settings configurado")

    console.print("\n[bold cyan]🚀 Próximos Passos:[/bold cyan]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Ação", style="cyan")
    table.add_column("Comando")

    table.add_row("1. Testar o robô", "python scripts/run_now.py")
    table.add_row("2. Ver estatísticas", "python scripts/show_stats.py")
    table.add_row("3. Instalar agendamento", "python scripts/install_task_scheduler.py")
    table.add_row("4. Ajustar configurações", "Edite config/settings.json")

    console.print(table)

    console.print("\n[bold yellow]💡 Dicas:[/bold yellow]")
    console.print("  • Execute o robô manualmente primeiro para testar")
    console.print("  • Verifique se os CNPJs aparecem no portal DET")
    console.print("  • Consulte o README.md para mais informações")
    console.print("  • Em caso de dúvidas, veja docs/MANUAL_USUARIO.md")

    console.print("\n[bold green]Boa sorte! 🍀[/bold green]")


def main():
    """Função principal do instalador."""
    try:
        exibir_boas_vindas()

        # Passo 1: Verificar Python
        if not verificar_python():
            console.print("\n❌ Instalação abortada.", style="red")
            return 1

        # Passo 2: Verificar pip
        if not verificar_pip():
            console.print("\n❌ Instalação abortada.", style="red")
            return 1

        # Passo 3: Instalar dependências
        if not Confirm.ask("\nDeseja instalar as dependências agora?", default=True):
            console.print("\n⚠️  Pulando instalação de dependências.", style="yellow")
            console.print("   Execute manualmente: pip install -r requirements.txt")
        else:
            if not instalar_dependencias():
                if not Confirm.ask("\nDeseja continuar mesmo assim?", default=False):
                    return 1

        # Passo 4: Criar pastas
        criar_estrutura_pastas()

        # Passo 5: Certificado
        if not configurar_certificado():
            if not Confirm.ask("\nDeseja continuar sem configurar o certificado?", default=False):
                return 1

        # Passo 6: Clientes
        configurar_clientes()

        # Passo 7: Settings
        configurar_settings()

        # Resumo
        resumo_instalacao()

        return 0

    except KeyboardInterrupt:
        console.print("\n\n❌ Instalação cancelada pelo usuário.", style="yellow")
        return 130

    except Exception as e:
        console.print(f"\n❌ Erro durante instalação: {e}", style="red")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
