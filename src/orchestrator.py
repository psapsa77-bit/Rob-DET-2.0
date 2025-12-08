"""
Orquestrador Principal - Rob-DET 2.0

Coordena a execução completa do robô:
- Carregamento de configurações
- Inicialização de componentes
- Execução de consultas
- Geração de relatórios
- Tratamento de erros
"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from src.models import Cliente, RelatorioConsulta
from src.navigation.det_navigator import DETNavigator
from src.det_scraper import DETScraper
from src.reports import gerar_relatorio
from src.utils.config import load_config

console = Console()


class DETOrchestrator:
    """
    Orquestrador principal do robô DET.

    Responsável por coordenar todo o fluxo de execução.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o orquestrador.

        Args:
            config_path: Caminho para arquivo de configuração (usa padrão se None)
        """
        logger.info("Iniciando DETOrchestrator...")

        # Carregar configuração
        self.config = load_config() if not config_path else load_config(config_path)

        # Componentes
        self.navigator: Optional[DETNavigator] = None
        self.scraper: Optional[DETScraper] = None

        # Resultados
        self.relatorios: List[RelatorioConsulta] = []

        logger.info("DETOrchestrator inicializado")

    def inicializar_componentes(self) -> bool:
        """
        Inicializa navegador e scraper.

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            logger.info("Inicializando componentes...")

            # Criar navigator
            self.navigator = DETNavigator(
                browser=self.config.app.browser,
                headless=self.config.app.headless,
                timeout=self.config.app.default_timeout,
                action_delay=self.config.app.action_delay
            )

            # Iniciar navegador
            self.navigator.start()

            # Criar scraper
            self.scraper = DETScraper(
                navigator=self.navigator,
                timeout=self.config.app.default_timeout,
                delay_between_actions=self.config.app.action_delay
            )

            logger.success("✓ Componentes inicializados")
            return True

        except Exception as e:
            logger.error(f"Erro ao inicializar componentes: {e}")
            return False

    def realizar_login(self) -> bool:
        """
        Realiza login no portal DET.

        Returns:
            True se login bem-sucedido, False caso contrário
        """
        if not self.scraper:
            logger.error("Scraper não inicializado")
            return False

        logger.info("Realizando login no DET...")

        try:
            if self.scraper.login():
                logger.success("✓ Login realizado com sucesso")
                return True
            else:
                logger.error("✗ Falha no login")
                return False

        except Exception as e:
            logger.error(f"Erro durante login: {e}")
            return False

    def consultar_clientes(
        self,
        clientes: Optional[List[Cliente]] = None,
        apenas_nao_lidas: bool = False
    ) -> List[RelatorioConsulta]:
        """
        Consulta mensagens de múltiplos clientes.

        Args:
            clientes: Lista de clientes (usa config se None)
            apenas_nao_lidas: Se True, extrai apenas não lidas

        Returns:
            Lista de relatórios
        """
        if not self.scraper:
            logger.error("Scraper não inicializado")
            return []

        # Usar clientes da configuração se não fornecidos
        if clientes is None:
            clientes = [
                Cliente(
                    cnpj=c.cnpj,
                    razao_social=c.razao_social,
                    nome_fantasia=c.nome_fantasia,
                    ativo=c.active,
                    prioridade=c.priority,
                    email_notificacao=c.email_notificacao,
                    observacoes=c.observacoes
                )
                for c in self.config.get_active_clients()
            ]

        if not clientes:
            logger.warning("Nenhum cliente ativo para consultar")
            return []

        logger.info(f"Consultando {len(clientes)} cliente(s)...")

        # Consultar com progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:

            task = progress.add_task(
                "[cyan]Consultando clientes...",
                total=len(clientes)
            )

            for cliente in clientes:
                progress.update(
                    task,
                    description=f"[cyan]Consultando {cliente.razao_social}..."
                )

                relatorio = self.scraper.consultar_cliente(
                    cliente,
                    apenas_nao_lidas=apenas_nao_lidas
                )

                self.relatorios.append(relatorio)
                progress.advance(task)

        return self.relatorios

    def gerar_relatorios_saida(
        self,
        formatos: List[str] = ['excel'],
        output_dir: Optional[str] = None
    ) -> List[str]:
        """
        Gera relatórios de saída nos formatos especificados.

        Args:
            formatos: Lista de formatos (excel, csv, json)
            output_dir: Diretório de saída (usa config se None)

        Returns:
            Lista de caminhos dos arquivos gerados
        """
        if not self.relatorios:
            logger.warning("Nenhum relatório para gerar")
            return []

        if not output_dir:
            output_dir = self.config.app.export_dir

        logger.info(f"Gerando relatórios em {len(formatos)} formato(s)...")

        arquivos_gerados = []

        for formato in formatos:
            try:
                filepath = gerar_relatorio(
                    self.relatorios,
                    formato=formato,
                    output_dir=output_dir
                )
                arquivos_gerados.append(filepath)

                logger.success(f"✓ Relatório {formato.upper()} gerado: {filepath}")

            except Exception as e:
                logger.error(f"Erro ao gerar relatório {formato}: {e}")

        return arquivos_gerados

    def salvar_estado_clientes(self, filepath: str = "data/clientes_estado.json"):
        """
        Salva estado atual dos clientes (última consulta, etc.).

        Args:
            filepath: Caminho do arquivo
        """
        try:
            # Extrair dados dos relatórios
            clientes_estado = []

            for rel in self.relatorios:
                clientes_estado.append({
                    'cnpj': rel.cnpj,
                    'razao_social': rel.razao_social,
                    'ultima_consulta': rel.data_consulta.isoformat(),
                    'total_mensagens': rel.total_mensagens,
                    'mensagens_nao_lidas': rel.mensagens_novas,
                    'mensagens_urgentes': rel.mensagens_urgentes
                })

            # Criar diretório se não existir
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            # Salvar JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(clientes_estado, f, indent=2, ensure_ascii=False)

            logger.info(f"Estado dos clientes salvo em: {filepath}")

        except Exception as e:
            logger.error(f"Erro ao salvar estado dos clientes: {e}")

    def executar_completo(
        self,
        clientes: Optional[List[Cliente]] = None,
        apenas_nao_lidas: bool = False,
        formatos_saida: List[str] = ['excel', 'json']
    ) -> bool:
        """
        Executa fluxo completo do robô.

        Args:
            clientes: Lista de clientes (usa config se None)
            apenas_nao_lidas: Se True, extrai apenas não lidas
            formatos_saida: Formatos de relatório

        Returns:
            True se sucesso, False se erro
        """
        sucesso = False

        try:
            # 1. Inicializar
            if not self.inicializar_componentes():
                return False

            # 2. Login
            if not self.realizar_login():
                return False

            # 3. Consultar clientes
            relatorios = self.consultar_clientes(
                clientes=clientes,
                apenas_nao_lidas=apenas_nao_lidas
            )

            if not relatorios:
                logger.warning("Nenhum relatório gerado")
                return False

            # 4. Gerar relatórios de saída
            arquivos = self.gerar_relatorios_saida(formatos=formatos_saida)

            # 5. Salvar estado
            self.salvar_estado_clientes()

            # Resumo
            self._imprimir_resumo_final(arquivos)

            sucesso = True

        except KeyboardInterrupt:
            logger.warning("\n⚠️  Execução interrompida pelo usuário")
            sucesso = False

        except Exception as e:
            logger.error(f"Erro durante execução: {e}")
            logger.exception(e)
            sucesso = False

        finally:
            # Cleanup
            self.finalizar()

        return sucesso

    def _imprimir_resumo_final(self, arquivos_gerados: List[str]):
        """Imprime resumo final da execução."""
        from rich.panel import Panel
        from rich.table import Table

        # Estatísticas gerais
        total_clientes = len(self.relatorios)
        total_sucesso = sum(1 for r in self.relatorios if r.sucesso)
        total_mensagens = sum(r.total_mensagens for r in self.relatorios)
        total_novas = sum(r.mensagens_novas for r in self.relatorios)
        total_urgentes = sum(r.mensagens_urgentes for r in self.relatorios)

        # Tabela de resumo
        table = Table(title="📊 Resumo da Execução")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="green", justify="right")

        table.add_row("Clientes consultados", f"{total_sucesso}/{total_clientes}")
        table.add_row("Total de mensagens", str(total_mensagens))
        table.add_row("Mensagens novas", str(total_novas))
        table.add_row("Mensagens urgentes", str(total_urgentes))

        console.print()
        console.print(table)

        # Arquivos gerados
        if arquivos_gerados:
            console.print("\n[bold green]📁 Relatórios Gerados:[/bold green]")
            for arquivo in arquivos_gerados:
                console.print(f"  • {arquivo}")

        console.print()

    def finalizar(self):
        """Finaliza componentes e limpa recursos."""
        logger.info("Finalizando componentes...")

        if self.scraper:
            self.scraper.logout()

        if self.navigator:
            self.navigator.stop()

        logger.info("Componentes finalizados")


# Exemplo de uso
if __name__ == '__main__':
    # Criar orquestrador
    orquestrador = DETOrchestrator()

    # Executar
    sucesso = orquestrador.executar_completo(
        apenas_nao_lidas=True,
        formatos_saida=['excel', 'json']
    )

    if sucesso:
        print("\n✅ Execução concluída com sucesso!")
    else:
        print("\n❌ Execução finalizada com erros")
