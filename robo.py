#!/usr/bin/env python3
"""
Rob-DET 2.0 - Interface Simples e Amigável

Interface de linha de comando simplificada para usuários leigos.
"""

import sys
import subprocess
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()


def exibir_menu_principal():
    """Exibe menu principal."""
    console.clear()

    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                    🤖 ROB-DET 2.0                             ║
    ║              Robô de Automação do Portal DET                 ║
    ╚═══════════════════════════════════════════════════════════════╝
    """

    console.print(banner, style="bold cyan")
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Opção", style="bold cyan", width=4)
    table.add_column("Descrição", style="white")

    table.add_row("1", "🚀 Executar Robô AGORA (consulta imediata)")
    table.add_row("2", "⏰ Instalar Execução Automática (agendar)")
    table.add_row("3", "📊 Ver Estatísticas e Relatórios")
    table.add_row("4", "⚙️  Configurar Certificado")
    table.add_row("5", "👥 Gerenciar Clientes (adicionar/remover)")
    table.add_row("6", "📧 Configurar Notificações por Email")
    table.add_row("7", "🧪 Testar Navegador (diagnóstico)")
    table.add_row("8", "🔍 Verificar Instalação")
    table.add_row("9", "📖 Ajuda e Documentação")
    table.add_row("0", "❌ Sair")

    console.print(table)
    console.print()

    return Prompt.ask(
        "Escolha uma opção",
        choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        default="1"
    )


def executar_agora():
    """Executa o robô imediatamente."""
    console.print("\n[bold green]🚀 Executando Robô...[/bold green]")
    console.print()

    # Verificar se clientes estão configurados
    clientes_file = Path("config/clientes.json")
    if not clientes_file.exists():
        console.print("❌ Arquivo de clientes não encontrado!", style="red")
        console.print("\n👉 Execute a opção 5 para adicionar clientes primeiro.")
        input("\nPressione Enter para voltar ao menu...")
        return

    console.print("📝 Iniciando consulta ao portal DET...")
    console.print("⏳ Isso pode levar alguns minutos dependendo da quantidade de clientes.")
    console.print()

    try:
        result = subprocess.run(
            [sys.executable, "scripts/run_now.py"],
            check=False
        )

        console.print()
        if result.returncode == 0:
            console.print("✅ Execução concluída com sucesso!", style="green")
        else:
            console.print("⚠️  Execução finalizada com avisos.", style="yellow")

    except KeyboardInterrupt:
        console.print("\n\n⚠️  Execução interrompida pelo usuário.", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Erro: {e}", style="red")

    input("\nPressione Enter para voltar ao menu...")


def instalar_agendamento():
    """Instala execução automática no Windows."""
    console.print("\n[bold cyan]⏰ Instalar Execução Automática[/bold cyan]")
    console.print()

    console.print("Isso irá configurar o Windows para executar o robô automaticamente")
    console.print("nos horários que você definiu no arquivo de configuração.")
    console.print()

    if not Confirm.ask("Deseja continuar?", default=True):
        return

    try:
        console.print("\n⚙️  Instalando tarefas agendadas...")

        result = subprocess.run(
            [sys.executable, "scripts/install_task_scheduler.py"],
            capture_output=True,
            text=True
        )

        console.print(result.stdout)

        if result.returncode == 0:
            console.print("\n✅ Tarefas instaladas com sucesso!", style="green")
            console.print("\n💡 Dica: Abra o 'Agendador de Tarefas' do Windows")
            console.print("   e procure por 'RobDET_Exec' para ver suas tarefas.")
        else:
            console.print("\n❌ Erro ao instalar tarefas.", style="red")
            console.print(result.stderr)

    except Exception as e:
        console.print(f"\n❌ Erro: {e}", style="red")

    input("\nPressione Enter para voltar ao menu...")


def ver_estatisticas():
    """Exibe estatísticas e relatórios."""
    console.print("\n[bold cyan]📊 Estatísticas e Relatórios[/bold cyan]")
    console.print()

    try:
        subprocess.run([sys.executable, "scripts/show_stats.py"])
    except Exception as e:
        console.print(f"\n❌ Erro: {e}", style="red")

    input("\nPressione Enter para voltar ao menu...")


def configurar_certificado():
    """Configura o certificado digital."""
    console.print("\n[bold cyan]🔐 Configurar Certificado Digital[/bold cyan]")
    console.print()

    table = Table(show_header=False, box=None)
    table.add_column("Opção", style="cyan", width=4)
    table.add_column("Descrição")

    table.add_row("1", "Ver certificados instalados")
    table.add_row("2", "Configurar auto-seleção de certificado")
    table.add_row("3", "Como instalar um certificado")
    table.add_row("0", "Voltar")

    console.print(table)
    console.print()

    opcao = Prompt.ask("Escolha uma opção", choices=["0", "1", "2", "3"], default="1")

    if opcao == "0":
        return
    elif opcao == "1":
        console.print("\n📜 Certificados instalados:\n")
        try:
            subprocess.run([sys.executable, "scripts/list_certificates.py"])
        except Exception as e:
            console.print(f"❌ Erro: {e}", style="red")

    elif opcao == "2":
        console.print("\n⚙️  Configurando auto-seleção...\n")
        try:
            subprocess.run([sys.executable, "scripts/setup_auto_certificate.py"])
        except Exception as e:
            console.print(f"❌ Erro: {e}", style="red")

    elif opcao == "3":
        console.print("\n[bold]📖 Como Instalar um Certificado Digital:[/bold]")
        console.print()
        console.print("1. Localize o arquivo .pfx do seu certificado")
        console.print("2. Clique duas vezes no arquivo")
        console.print("3. Escolha 'Usuário Atual' e clique em Avançar")
        console.print("4. Confirme o caminho do arquivo e clique em Avançar")
        console.print("5. Digite a senha do certificado")
        console.print("6. Marque 'Incluir todas as propriedades estendidas'")
        console.print("7. Escolha 'Repositório de Certificados Pessoais'")
        console.print("8. Clique em Concluir")
        console.print()
        console.print("✅ Pronto! O certificado está instalado.")

    input("\nPressione Enter para voltar ao menu...")


def gerenciar_clientes():
    """Gerencia lista de clientes."""
    console.print("\n[bold cyan]👥 Gerenciar Clientes[/bold cyan]")
    console.print()

    clientes_file = Path("config/clientes.json")

    if not clientes_file.exists():
        console.print("⚠️  Arquivo de clientes não encontrado.", style="yellow")
        console.print("   Será criado um novo arquivo.")

    console.print("\n[yellow]💡 Dica:[/yellow] Use o instalador para adicionar clientes facilmente:")
    console.print("   python install.py")
    console.print()
    console.print("Ou edite manualmente o arquivo: config/clientes.json")

    if Confirm.ask("\nDeseja abrir o arquivo agora?", default=True):
        try:
            if sys.platform == 'win32':
                subprocess.run(["notepad", str(clientes_file)])
            else:
                subprocess.run(["nano", str(clientes_file)])
        except:
            console.print(f"\n📝 Edite manualmente: {clientes_file}")

    input("\nPressione Enter para voltar ao menu...")


def configurar_email():
    """Configura notificações por email."""
    console.print("\n[bold cyan]📧 Configurar Notificações por Email[/bold cyan]")
    console.print()

    console.print("As notificações por email são configuradas no arquivo:")
    console.print("[bold]config/settings.json[/bold]")
    console.print()

    console.print("[bold]Como configurar:[/bold]")
    console.print("1. Abra o arquivo config/settings.json")
    console.print("2. Localize a seção 'notificacoes'")
    console.print("3. Altere:")
    console.print("   • email_ativo: true")
    console.print("   • email_remetente: seu_email@gmail.com")
    console.print("   • email_senha: sua_senha_de_app")
    console.print("   • email_destinatarios: ['email1@exemplo.com', 'email2@exemplo.com']")
    console.print()

    console.print("[yellow]📖 Para Gmail:[/yellow]")
    console.print("  1. Ative a verificação em 2 etapas")
    console.print("  2. Gere uma senha de app em:")
    console.print("     https://myaccount.google.com/apppasswords")
    console.print("  3. Use a senha de app no campo 'email_senha'")

    if Confirm.ask("\nDeseja abrir o arquivo de configuração?", default=True):
        settings_file = Path("config/settings.json")
        try:
            if sys.platform == 'win32':
                subprocess.run(["notepad", str(settings_file)])
            else:
                subprocess.run(["nano", str(settings_file)])
        except:
            console.print(f"\n📝 Edite manualmente: {settings_file}")

    input("\nPressione Enter para voltar ao menu...")


def verificar_instalacao():
    """Verifica se tudo está instalado corretamente."""
    console.print("\n[bold cyan]🔍 Verificando Instalação[/bold cyan]")
    console.print()

    # Python
    console.print("🐍 Python:", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        console.print(f"✅ {version.major}.{version.minor}.{version.micro}", style="green")
    else:
        console.print(f"❌ {version.major}.{version.minor}.{version.micro} (precisa 3.11+)", style="red")

    # Dependências
    console.print("📦 Dependências:", end=" ")
    try:
        import selenium
        import loguru
        import openpyxl
        console.print("✅ Instaladas", style="green")
    except ImportError as e:
        console.print(f"❌ Faltando: {e.name}", style="red")

    # Estrutura de pastas
    console.print("📁 Estrutura:", end=" ")
    pastas_necessarias = ["config", "logs", "relatorios", "downloads", "screenshots"]
    todas_existem = all(Path(p).exists() for p in pastas_necessarias)
    if todas_existem:
        console.print("✅ OK", style="green")
    else:
        console.print("⚠️  Faltando algumas pastas", style="yellow")

    # Arquivos de configuração
    console.print("⚙️  Configuração:", end=" ")
    if Path("config/settings.json").exists() and Path("config/clientes.json").exists():
        console.print("✅ OK", style="green")
    else:
        console.print("⚠️  Faltando arquivos", style="yellow")

    # Certificado
    console.print("🔐 Certificado:", end=" ")
    try:
        result = subprocess.run(
            [sys.executable, "scripts/list_certificates.py"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "Certificados encontrados" in result.stdout:
            console.print("✅ Instalado", style="green")
        else:
            console.print("⚠️  Não detectado", style="yellow")
    except:
        console.print("⚠️  Não verificado", style="yellow")

    console.print()
    console.print("[bold]Resultado:[/bold]")
    if todas_existem and Path("config/settings.json").exists():
        console.print("✅ Sistema pronto para uso!", style="green")
    else:
        console.print("⚠️  Execute o instalador: python install.py", style="yellow")

    input("\nPressione Enter para voltar ao menu...")


def exibir_ajuda():
    """Exibe ajuda e documentação."""
    console.print("\n[bold cyan]📖 Ajuda e Documentação[/bold cyan]")
    console.print()

    console.print("[bold]📚 Documentação Disponível:[/bold]")
    console.print()
    console.print("  • README.md - Guia completo do projeto")
    console.print("  • QUICKSTART.md - Guia de início rápido")
    console.print("  • docs/MANUAL_USUARIO.md - Manual detalhado")
    console.print("  • docs/TROUBLESHOOTING.md - Solução de problemas")
    console.print()

    console.print("[bold]🆘 Problemas Comuns:[/bold]")
    console.print()
    console.print("1. [yellow]Certificado não é selecionado:[/yellow]")
    console.print("   → Execute: python scripts/setup_auto_certificate.py")
    console.print()
    console.print("2. [yellow]CNPJ não aparece:[/yellow]")
    console.print("   → Verifique se tem procuração eletrônica ativa")
    console.print()
    console.print("3. [yellow]Erro de timeout:[/yellow]")
    console.print("   → Aumente o timeout em config/settings.json")
    console.print()

    console.print("[bold]💬 Suporte:[/bold]")
    console.print("  • Email: suporte@exemplo.com")
    console.print("  • GitHub Issues: github.com/seu-usuario/Rob-DET-2.0/issues")

    input("\nPressione Enter para voltar ao menu...")


def testar_navegador():
    """Testa o navegador e diagnostica problemas."""
    console.print("\n[bold cyan]🧪 Teste de Navegador e Diagnóstico[/bold cyan]")
    console.print()

    console.print("Este teste irá:")
    console.print("  1. Verificar se Chrome/Edge está instalado")
    console.print("  2. Testar se o WebDriver funciona")
    console.print("  3. Abrir o navegador para você ver")
    console.print()

    if not Confirm.ask("Deseja executar o teste?", default=True):
        return

    try:
        console.print("\n⏳ Executando teste...")
        console.print("[dim]Isso pode demorar alguns segundos...[/dim]\n")

        result = subprocess.run(
            [sys.executable, "scripts/testar_navegador.py"],
            check=False
        )

        console.print()
        if result.returncode == 0:
            console.print("✅ Teste concluído!", style="green")
        else:
            console.print("❌ Teste encontrou problemas.", style="red")
            console.print("\n💡 Execute o diagnóstico completo:")
            console.print("   [cyan]python scripts/diagnosticar_ambiente.py[/cyan]")

    except Exception as e:
        console.print(f"\n❌ Erro ao executar teste: {e}", style="red")

    input("\nPressione Enter para voltar ao menu...")


def main():
    """Função principal."""
    while True:
        try:
            opcao = exibir_menu_principal()

            if opcao == "0":
                console.print("\n👋 Até logo!", style="cyan")
                break
            elif opcao == "1":
                executar_agora()
            elif opcao == "2":
                instalar_agendamento()
            elif opcao == "3":
                ver_estatisticas()
            elif opcao == "4":
                configurar_certificado()
            elif opcao == "5":
                gerenciar_clientes()
            elif opcao == "6":
                configurar_email()
            elif opcao == "7":
                testar_navegador()
            elif opcao == "8":
                verificar_instalacao()
            elif opcao == "9":
                exibir_ajuda()

        except KeyboardInterrupt:
            console.print("\n\n👋 Até logo!", style="cyan")
            break
        except Exception as e:
            console.print(f"\n❌ Erro: {e}", style="red")
            input("\nPressione Enter para continuar...")

    return 0


if __name__ == '__main__':
    sys.exit(main())
