#!/usr/bin/env python3
"""
Visualizador de Estatísticas - Rob-DET 2.0

Exibe estatísticas de execução, heartbeat e métricas.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.config_manager import get_config
from src.monitoring import Monitor


console = Console()


def mostrar_heartbeat():
    """Mostra status do heartbeat."""
    try:
        config = get_config()
        heartbeat_file = Path(config.monitoramento.heartbeat_arquivo)

        if not heartbeat_file.exists():
            console.print("[yellow]⚠️  Nenhum heartbeat encontrado[/yellow]")
            return

        with open(heartbeat_file, 'r', encoding='utf-8') as f:
            heartbeat = json.load(f)

        # Status com cores
        status = heartbeat.get('status', 'unknown').upper()
        status_colors = {
            'RUNNING': 'green',
            'IDLE': 'blue',
            'ERROR': 'red'
        }
        status_color = status_colors.get(status, 'white')

        # Parsear datas
        timestamp = heartbeat.get('timestamp', '')
        ultima_exec = heartbeat.get('ultima_execucao', '')
        proxima_exec = heartbeat.get('proxima_execucao', '')

        try:
            timestamp_dt = datetime.fromisoformat(timestamp)
            timestamp_str = timestamp_dt.strftime('%d/%m/%Y %H:%M:%S')
        except:
            timestamp_str = timestamp

        try:
            if ultima_exec:
                ultima_dt = datetime.fromisoformat(ultima_exec)
                ultima_str = ultima_dt.strftime('%d/%m/%Y %H:%M:%S')
            else:
                ultima_str = "Nunca"
        except:
            ultima_str = ultima_exec or "Nunca"

        try:
            if proxima_exec:
                proxima_dt = datetime.fromisoformat(proxima_exec)
                proxima_str = proxima_dt.strftime('%d/%m/%Y %H:%M:%S')
            else:
                proxima_str = "Não agendada"
        except:
            proxima_str = proxima_exec or "Não agendada"

        # Montar painel
        info = f"""
[bold]Status:[/bold] [{status_color}]{status}[/{status_color}]
[bold]Última atualização:[/bold] {timestamp_str}
[bold]Última execução:[/bold] {ultima_str}
[bold]Próxima execução:[/bold] {proxima_str}
[bold]Versão:[/bold] {heartbeat.get('versao', '2.0')}
        """

        console.print(Panel(info, title="🔄 Heartbeat", border_style=status_color))

    except Exception as e:
        console.print(f"[red]Erro ao ler heartbeat: {e}[/red]")


def mostrar_estatisticas():
    """Mostra estatísticas de execução."""
    try:
        config = get_config()
        monitor = Monitor(config)

        # Estatísticas 7 dias
        stats_7d = monitor.get_estatisticas_periodo(7)

        if not stats_7d:
            console.print("[yellow]⚠️  Nenhuma métrica disponível[/yellow]")
            return

        # Tabela de estatísticas
        table = Table(title="📊 Estatísticas dos Últimos 7 Dias", show_header=True)
        table.add_column("Métrica", style="cyan", width=30)
        table.add_column("Valor", style="green", justify="right")

        table.add_row("Total de execuções", str(stats_7d['total_execucoes']))
        table.add_row("Clientes consultados", str(stats_7d['total_clientes_consultados']))
        table.add_row(
            "Taxa de sucesso",
            f"{stats_7d['taxa_sucesso_media']:.1%}",
            style="green" if stats_7d['taxa_sucesso_media'] > 0.9 else "yellow"
        )
        table.add_row("Total de mensagens", str(stats_7d['total_mensagens']))
        table.add_row("Mensagens novas", str(stats_7d['total_mensagens_novas']))
        table.add_row(
            "Mensagens urgentes",
            str(stats_7d['total_mensagens_urgentes']),
            style="red" if stats_7d['total_mensagens_urgentes'] > 0 else "green"
        )
        table.add_row(
            "Tempo médio/execução",
            f"{stats_7d['tempo_medio_execucao_segundos']:.1f}s"
        )
        table.add_row(
            "Média mensagens/execução",
            f"{stats_7d['media_mensagens_por_execucao']:.1f}"
        )

        console.print(table)

        # Estatísticas 30 dias
        stats_30d = monitor.get_estatisticas_periodo(30)

        if stats_30d:
            console.print()
            table_30d = Table(title="📊 Estatísticas dos Últimos 30 Dias", show_header=True)
            table_30d.add_column("Métrica", style="cyan", width=30)
            table_30d.add_column("Valor", style="green", justify="right")

            table_30d.add_row("Total de execuções", str(stats_30d['total_execucoes']))
            table_30d.add_row("Clientes consultados", str(stats_30d['total_clientes_consultados']))
            table_30d.add_row("Taxa de sucesso", f"{stats_30d['taxa_sucesso_media']:.1%}")
            table_30d.add_row("Total de mensagens", str(stats_30d['total_mensagens']))
            table_30d.add_row("Mensagens novas", str(stats_30d['total_mensagens_novas']))

            console.print(table_30d)

    except Exception as e:
        console.print(f"[red]Erro ao calcular estatísticas: {e}[/red]")


def mostrar_configuracao():
    """Mostra configuração atual."""
    try:
        config = get_config()

        info = f"""
[bold]Execução:[/bold]
  • Horários: {', '.join(config.execucao.horarios)}
  • Dias da semana: {config.execucao.dias_semana}
  • Timeout por cliente: {config.execucao.timeout_por_cliente}s
  • Apenas não lidas: {config.execucao.apenas_nao_lidas}

[bold]Navegador:[/bold]
  • Headless: {config.chrome.headless}
  • Download: {config.chrome.download_path}

[bold]Notificações:[/bold]
  • Email ativo: {config.notificacoes.email_ativo}
  • Destinatários: {len(config.notificacoes.email_destinatarios)}

[bold]Logs:[/bold]
  • Nível: {config.logs.nivel}
  • Arquivo: {config.logs.arquivo}
  • Tamanho máx: {config.logs.max_size_mb} MB

[bold]Monitoramento:[/bold]
  • Heartbeat: {config.monitoramento.heartbeat_ativo}
  • Métricas: {config.monitoramento.metricas_ativo}
        """

        console.print(Panel(info, title="⚙️  Configuração Atual", border_style="blue"))

    except Exception as e:
        console.print(f"[red]Erro ao ler configuração: {e}[/red]")


def main():
    """Função principal."""
    try:
        console.print("\n[bold cyan]═" * 30 + "[/bold cyan]")
        console.print("[bold cyan]ROB-DET 2.0 - Dashboard de Estatísticas[/bold cyan]")
        console.print("[bold cyan]═" * 30 + "[/bold cyan]\n")

        # Mostrar heartbeat
        mostrar_heartbeat()
        console.print()

        # Mostrar estatísticas
        mostrar_estatisticas()
        console.print()

        # Mostrar configuração
        mostrar_configuracao()

        console.print()

    except KeyboardInterrupt:
        console.print("\n[yellow]🛑 Interrompido[/yellow]")
        sys.exit(130)

    except Exception as e:
        console.print(f"\n[red]❌ Erro: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()
