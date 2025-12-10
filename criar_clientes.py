#!/usr/bin/env python3
"""
Criador de Arquivo de Clientes - Rob-DET 2.0

Script auxiliar para criar config/clientes.json de forma guiada.
"""

import sys
import json
from pathlib import Path

try:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
except ImportError:
    print("❌ Biblioteca 'rich' não instalada")
    print("Execute: pip install rich")
    sys.exit(1)

console = Console()


def criar_cliente_interativo():
    """Cria um cliente de forma interativa."""
    console.print("\n[bold cyan]➕ Adicionar Novo Cliente[/bold cyan]\n")

    cnpj = Prompt.ask("CNPJ (com ou sem formatação)")
    razao_social = Prompt.ask("Razão Social")
    nome_fantasia = Prompt.ask("Nome Fantasia", default="")
    email = Prompt.ask("Email para notificações", default="")

    prioridade = Prompt.ask(
        "Prioridade",
        choices=["alta", "normal", "baixa"],
        default="normal"
    )

    ativo = Confirm.ask("Cliente ativo?", default=True)

    observacoes = Prompt.ask("Observações (opcional)", default="")

    return {
        "cnpj": cnpj,
        "razao_social": razao_social,
        "nome_fantasia": nome_fantasia,
        "ativo": ativo,
        "prioridade": prioridade,
        "email_notificacao": email,
        "observacoes": observacoes,
        "filiais": []
    }


def criar_arquivo_clientes():
    """Cria arquivo config/clientes.json."""
    console.clear()

    console.print(Panel.fit(
        "[bold cyan]📋 CRIADOR DE ARQUIVO DE CLIENTES[/bold cyan]\n\n"
        "Este assistente vai te ajudar a criar o arquivo\n"
        "config/clientes.json com seus clientes.",
        border_style="cyan"
    ))

    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    clientes_file = config_dir / "clientes.json"

    # Verificar se já existe
    if clientes_file.exists():
        console.print("\n[yellow]⚠️  O arquivo config/clientes.json já existe![/yellow]")
        console.print(f"   Caminho: {clientes_file.absolute()}\n")

        if not Confirm.ask("Deseja sobrescrever?", default=False):
            console.print("\n[yellow]Operação cancelada.[/yellow]")
            return False

    # Perguntar quantos clientes
    console.print("\n[bold]Quantos clientes você quer adicionar?[/bold]")
    console.print("[dim]Você pode adicionar mais depois editando o arquivo ou usando o menu.[/dim]\n")

    try:
        num_clientes = int(Prompt.ask("Número de clientes", default="1"))
    except ValueError:
        console.print("[red]❌ Número inválido[/red]")
        return False

    # Coletar clientes
    clientes = []

    for i in range(num_clientes):
        console.print(f"\n[bold]Cliente {i+1}/{num_clientes}:[/bold]")
        cliente = criar_cliente_interativo()
        clientes.append(cliente)

        console.print(f"\n[green]✅ Cliente '{cliente['razao_social']}' adicionado[/green]")

    # Criar estrutura do JSON
    dados = {
        "clientes": clientes,
        "configuracoes": {
            "consultar_apenas_ativos": True,
            "ordem_processamento": "priority",
            "delay_entre_clientes_segundos": 10,
            "incluir_filiais": True,
            "notificar_apenas_novas": True,
            "tipos_mensagem_notificar": [
                "Autuação",
                "Intimação",
                "Notificação"
            ]
        }
    }

    # Salvar arquivo
    try:
        with open(clientes_file, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

        console.print("\n" + "="*60)
        console.print("[bold green]✅ ARQUIVO CRIADO COM SUCESSO![/bold green]")
        console.print("="*60)
        console.print(f"\n📄 Arquivo: {clientes_file.absolute()}")
        console.print(f"👥 Clientes adicionados: {len(clientes)}")
        console.print()

        # Mostrar resumo
        ativos = sum(1 for c in clientes if c['ativo'])
        console.print("[bold]Resumo:[/bold]")
        console.print(f"  • Total: {len(clientes)} cliente(s)")
        console.print(f"  • Ativos: {ativos} cliente(s)")
        console.print(f"  • Inativos: {len(clientes) - ativos} cliente(s)")
        console.print()

        console.print("[cyan]💡 Próximos passos:[/cyan]")
        console.print("   1. Execute: python robo.py")
        console.print("   2. Escolha opção 1 para executar o robô")
        console.print()

        return True

    except Exception as e:
        console.print(f"\n[red]❌ Erro ao salvar arquivo: {e}[/red]")
        return False


def copiar_exemplo():
    """Copia o arquivo de exemplo."""
    console.print("\n[bold cyan]📋 Copiar Arquivo de Exemplo[/bold cyan]\n")

    exemplo = Path("config/clientes.json.example")
    destino = Path("config/clientes.json")

    if not exemplo.exists():
        console.print(f"[red]❌ Arquivo de exemplo não encontrado: {exemplo}[/red]")
        return False

    if destino.exists():
        console.print("[yellow]⚠️  O arquivo config/clientes.json já existe![/yellow]")
        if not Confirm.ask("Deseja sobrescrever?", default=False):
            console.print("\n[yellow]Operação cancelada.[/yellow]")
            return False

    try:
        import shutil
        shutil.copy2(exemplo, destino)

        console.print(f"\n[green]✅ Arquivo copiado com sucesso![/green]")
        console.print(f"   De: {exemplo}")
        console.print(f"   Para: {destino}")
        console.print()
        console.print("[yellow]⚠️  IMPORTANTE: Edite o arquivo e coloque seus CNPJs reais![/yellow]")
        console.print()

        return True

    except Exception as e:
        console.print(f"\n[red]❌ Erro ao copiar arquivo: {e}[/red]")
        return False


def main():
    """Função principal."""
    console.clear()

    console.print(Panel.fit(
        "[bold cyan]📋 CONFIGURADOR DE CLIENTES - ROB-DET 2.0[/bold cyan]",
        border_style="cyan"
    ))

    console.print("\n[bold]Escolha uma opção:[/bold]\n")
    console.print("1. Criar arquivo de clientes interativamente (recomendado)")
    console.print("2. Copiar arquivo de exemplo")
    console.print("0. Cancelar\n")

    opcao = Prompt.ask("Opção", choices=["0", "1", "2"], default="1")

    if opcao == "0":
        console.print("\n[yellow]Operação cancelada.[/yellow]")
        return 0

    elif opcao == "1":
        sucesso = criar_arquivo_clientes()

    elif opcao == "2":
        sucesso = copiar_exemplo()

    else:
        console.print("\n[red]Opção inválida[/red]")
        return 1

    return 0 if sucesso else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Operação cancelada pelo usuário[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]❌ Erro inesperado: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
