#!/usr/bin/env python3
"""
Rob-DET 2.0 - Robô de Automação do Portal DET
Script Principal

Executa consultas automatizadas ao Portal DET (Domicílio Eletrônico Trabalhista).
"""

import sys
import time
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from loguru import logger

from src.config_manager import get_config, ConfigManager
from src.navigation.det_navigator import DETNavigator
from src.det_scraper import DETScraper
from src.models import Cliente
from src.reports.report_generator import ReportGenerator
from src.notifications import EmailNotifier
from src.monitoring import Monitor


class RoboDET:
    """
    Classe principal do robô DET.

    Orquestra navegação, scraping, relatórios e notificações.
    """

    def __init__(self, config: Optional[ConfigManager] = None):
        """
        Inicializa o robô.

        Args:
            config: Gerenciador de configurações (opcional)
        """
        self.config = config or get_config()
        self._configurar_logs()

        self.navigator: Optional[DETNavigator] = None
        self.scraper: Optional[DETScraper] = None
        self.notifier = EmailNotifier(self.config)
        self.monitor = Monitor(self.config)

        # Controle de reinicialização
        self._tentativas_reinicializacao = 0

        logger.info("═" * 60)
        logger.info("ROB-DET 2.0 - Robô de Automação do Portal DET")
        logger.info("═" * 60)

    def _configurar_logs(self) -> None:
        """Configura sistema de logs com loguru."""
        # Remover handler padrão
        logger.remove()

        # Console (se ativado)
        if self.config.logs.log_para_console:
            logger.add(
                sys.stderr,
                format=self.config.logs.formato,
                level=self.config.logs.nivel,
                colorize=self.config.logs.colorir_console
            )

        # Arquivo (se ativado)
        if self.config.logs.log_para_arquivo:
            log_path = Path(self.config.logs.arquivo)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            logger.add(
                str(log_path),
                format=self.config.logs.formato,
                level=self.config.logs.nivel,
                rotation=f"{self.config.logs.max_size_mb} MB",
                retention=self.config.logs.backup_count,
                compression="zip",
                encoding="utf-8"
            )

        logger.info("Sistema de logs configurado")

    def carregar_clientes(self) -> List[Cliente]:
        """
        Carrega lista de clientes do arquivo de configuração.

        Returns:
            Lista de clientes ativos
        """
        try:
            clientes_file = Path("config/clientes.json")

            if not clientes_file.exists():
                logger.warning(f"Arquivo não encontrado: {clientes_file}")
                logger.info("💡 Crie o arquivo copiando: cp config/clientes.json.example config/clientes.json")
                logger.info("   Ou use a opção 5 do menu: python robo.py")
                logger.info("")
                logger.info("⚠️  Usando cliente de exemplo temporário")
                return [
                    Cliente(
                        cnpj="12.345.678/0001-90",
                        razao_social="Empresa Exemplo Ltda"
                    )
                ]

            with open(clientes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validar estrutura do JSON
            if not isinstance(data, dict):
                logger.error(f"Formato inválido em {clientes_file}: esperado dicionário, recebido {type(data).__name__}")
                logger.info("💡 O arquivo deve ter o formato:")
                logger.info('   {"clientes": [...]}')
                logger.info("   Consulte config/clientes.json.example")
                return []

            if 'clientes' not in data:
                logger.error(f"Formato inválido em {clientes_file}: chave 'clientes' não encontrada")
                logger.info("💡 O arquivo deve ter o formato:")
                logger.info('   {"clientes": [...]}')
                logger.info("   Consulte config/clientes.json.example")
                return []

            clientes_data = data.get('clientes', [])

            if not isinstance(clientes_data, list):
                logger.error(f"Formato inválido: 'clientes' deve ser uma lista")
                return []

            # Criar objetos Cliente
            clientes = []
            for idx, c in enumerate(clientes_data):
                try:
                    if not isinstance(c, dict):
                        logger.warning(f"Cliente {idx+1} ignorado: formato inválido (esperado dicionário)")
                        continue

                    cliente = Cliente(**c)
                    clientes.append(cliente)
                except Exception as e:
                    logger.warning(f"Erro ao processar cliente {idx+1}: {e}")
                    continue

            if not clientes:
                logger.warning("Nenhum cliente válido encontrado no arquivo")
                return []

            # Filtrar apenas ativos
            clientes_ativos = [c for c in clientes if c.ativo]

            if not clientes_ativos:
                logger.warning("Nenhum cliente ativo encontrado")
                logger.info(f"Total de clientes: {len(clientes)} (todos inativos)")
                return []

            logger.info(f"✓ {len(clientes_ativos)} cliente(s) ativo(s) carregado(s)")

            # Ordenar por prioridade
            ordem_prioridade = {"alta": 0, "high": 0, "normal": 1, "baixa": 2, "low": 2}
            clientes_ativos.sort(key=lambda c: ordem_prioridade.get(c.prioridade.lower() if c.prioridade else "normal", 1))

            return clientes_ativos

        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON de clientes: {e}")
            logger.error(f"   Arquivo: {clientes_file}")
            logger.error(f"   Linha {e.lineno}, Coluna {e.colno}: {e.msg}")
            logger.info("💡 Verifique se o JSON está bem formatado")
            logger.info("   Use um validador online: https://jsonlint.com/")
            return []

        except Exception as e:
            logger.error(f"Erro ao carregar clientes: {e}")
            logger.exception(e)  # Log da stack trace completa
            logger.info("💡 Verifique o arquivo config/clientes.json")
            logger.info("   Ou consulte o exemplo em config/clientes.json.example")
            return []

    def inicializar_navegador(self) -> bool:
        """
        Inicializa navegador e scraper.

        Returns:
            True se inicializado com sucesso
        """
        try:
            logger.info("Inicializando navegador...")

            # Configurar opções do Chrome
            headless = self.config.chrome.headless
            download_path = self.config.chrome.download_path

            # Criar navigator
            self.navigator = DETNavigator(
                browser='chrome',
                headless=headless,
                download_path=download_path
            )

            self.navigator.start()

            # Criar scraper
            timeout = self.config.execucao.timeout_por_cliente
            self.scraper = DETScraper(
                navigator=self.navigator,
                timeout=timeout
            )

            logger.success("✓ Navegador inicializado")
            return True

        except Exception as e:
            logger.error(f"Erro ao inicializar navegador: {e}")
            return False

    def finalizar_navegador(self) -> None:
        """Finaliza navegador."""
        if self.navigator:
            try:
                self.navigator.stop()
                logger.info("Navegador finalizado")
            except Exception as e:
                logger.warning(f"Erro ao finalizar navegador: {e}")

        self.navigator = None
        self.scraper = None

    def executar(self) -> bool:
        """
        Executa consulta completa para todos os clientes.

        Returns:
            True se executado com sucesso
        """
        inicio = time.time()
        erros = []

        try:
            # Atualizar status
            self.monitor.set_status("running")

            logger.info("\n" + "━" * 60)
            logger.info("INICIANDO EXECUÇÃO")
            logger.info("━" * 60)

            # 1. Carregar clientes
            clientes = self.carregar_clientes()

            if not clientes:
                logger.error("Nenhum cliente para consultar")
                return False

            logger.info(f"Total de clientes: {len(clientes)}")

            # 2. Inicializar navegador
            if not self.inicializar_navegador():
                logger.error("Falha ao inicializar navegador")
                return False

            # 3. Login
            logger.info("\n📝 Realizando login...")

            if not self.scraper.login():
                logger.error("Falha no login")
                self.finalizar_navegador()

                if self.config.recuperacao.reiniciar_apos_falha:
                    return self._tentar_recuperacao()

                return False

            # 4. Consultar cada cliente
            relatorios = []

            for idx, cliente in enumerate(clientes, 1):
                try:
                    logger.info(f"\n[{idx}/{len(clientes)}] Consultando: {cliente.razao_social}")

                    relatorio = self.scraper.consultar_cliente(
                        cliente=cliente,
                        apenas_nao_lidas=self.config.execucao.apenas_nao_lidas
                    )

                    relatorios.append(relatorio)

                    # Delay entre clientes
                    if idx < len(clientes):
                        delay = self.config.execucao.delay_entre_clientes
                        logger.debug(f"Aguardando {delay}s antes do próximo cliente...")
                        time.sleep(delay)

                except Exception as e:
                    logger.error(f"Erro ao consultar {cliente.razao_social}: {e}")
                    erros.append(f"{cliente.razao_social}: {str(e)}")
                    continue

            # 5. Gerar relatórios
            if relatorios:
                self._gerar_relatorios(relatorios)

            # 6. Registrar métricas
            tempo_total = time.time() - inicio
            metrica = self.monitor.registrar_execucao(
                relatorios=relatorios,
                tempo_total=tempo_total,
                erros=erros
            )

            # 7. Enviar notificações
            self._enviar_notificacoes(relatorios, tempo_total, erros)

            # 8. Resumo final
            self._imprimir_resumo_final(relatorios, tempo_total)

            # Sucesso se pelo menos um cliente foi consultado
            sucesso = any(r.sucesso for r in relatorios)

            return sucesso

        except Exception as e:
            logger.error(f"Erro crítico durante execução: {e}")
            logger.exception(e)

            # Capturar screenshot se possível
            if self.config.recuperacao.screenshot_em_erro and self.navigator:
                try:
                    screenshot_path = Path("screenshots") / f"erro_critico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    self.navigator.driver.save_screenshot(str(screenshot_path))
                    logger.info(f"Screenshot salvo: {screenshot_path}")
                except:
                    pass

            # Enviar alerta de erro
            self.notifier.enviar_alerta_erro(
                titulo="Erro Crítico na Execução",
                mensagem=str(e),
                detalhes=None
            )

            return False

        finally:
            # Sempre finalizar navegador
            self.finalizar_navegador()

            # Atualizar status
            self.monitor.set_status("idle")

    def _tentar_recuperacao(self) -> bool:
        """
        Tenta recuperar de falha reinicializando.

        Returns:
            True se recuperado com sucesso
        """
        if self._tentativas_reinicializacao >= self.config.recuperacao.max_reinicializacoes:
            logger.error("Máximo de tentativas de reinicialização atingido")
            return False

        self._tentativas_reinicializacao += 1
        delay = self.config.recuperacao.delay_reinicializacao_segundos

        logger.warning(
            f"⚠️  Tentando recuperar... "
            f"(Tentativa {self._tentativas_reinicializacao}/"
            f"{self.config.recuperacao.max_reinicializacoes})"
        )
        logger.info(f"Aguardando {delay}s antes de reiniciar...")

        time.sleep(delay)

        # Tentar novamente
        return self.executar()

    def _gerar_relatorios(self, relatorios) -> None:
        """Gera relatórios em múltiplos formatos."""
        try:
            logger.info("\n📊 Gerando relatórios...")

            generator = ReportGenerator(config=self.config)

            # Excel
            if self.config.relatorios.gerar_excel:
                excel_path = generator.gerar_relatorio_excel(relatorios)
                if excel_path:
                    logger.success(f"✓ Excel: {excel_path}")

            # CSV
            if self.config.relatorios.gerar_csv:
                csv_path = generator.gerar_relatorio_csv(relatorios)
                if csv_path:
                    logger.success(f"✓ CSV: {csv_path}")

            # JSON
            if self.config.relatorios.gerar_json:
                json_path = generator.gerar_relatorio_json(relatorios)
                if json_path:
                    logger.success(f"✓ JSON: {json_path}")

        except Exception as e:
            logger.error(f"Erro ao gerar relatórios: {e}")

    def _enviar_notificacoes(self, relatorios, tempo_total, erros) -> None:
        """Envia notificações por email."""
        try:
            if not self.config.notificacoes.email_ativo:
                return

            logger.info("\n📧 Enviando notificações...")

            # Alerta de mensagens urgentes
            if self.config.notificacoes.email_enviar_apenas_urgentes:
                self.notifier.enviar_alerta_mensagens_urgentes(relatorios)

            # Resumo da execução
            if self.config.notificacoes.email_enviar_resumo_diario:
                self.notifier.enviar_resumo_execucao(
                    relatorios=relatorios,
                    tempo_total=tempo_total,
                    erros=erros
                )

        except Exception as e:
            logger.error(f"Erro ao enviar notificações: {e}")

    def _imprimir_resumo_final(self, relatorios, tempo_total) -> None:
        """Imprime resumo final da execução."""
        total_clientes = len(relatorios)
        clientes_sucesso = sum(1 for r in relatorios if r.sucesso)
        total_mensagens = sum(r.total_mensagens for r in relatorios)
        total_novas = sum(r.mensagens_novas for r in relatorios)
        total_urgentes = sum(r.mensagens_urgentes for r in relatorios)

        logger.info("\n" + "═" * 60)
        logger.info("RESUMO FINAL")
        logger.info("═" * 60)
        logger.info(f"Clientes consultados:  {clientes_sucesso}/{total_clientes}")
        logger.info(f"Total de mensagens:    {total_mensagens}")
        logger.info(f"Mensagens novas:       {total_novas}")
        logger.info(f"Mensagens urgentes:    {total_urgentes}")
        logger.info(f"Tempo total:           {tempo_total:.1f}s")
        logger.info("═" * 60)

        if clientes_sucesso == total_clientes:
            logger.success("✓ Execução concluída com SUCESSO!")
        elif clientes_sucesso > 0:
            logger.warning("⚠ Execução concluída com SUCESSO PARCIAL")
        else:
            logger.error("❌ Execução FALHOU para todos os clientes")


def main():
    """Função principal."""
    try:
        # Criar robô
        robo = RoboDET()

        # Iniciar heartbeat
        robo.monitor.iniciar_heartbeat()

        try:
            # Executar
            sucesso = robo.executar()

            # Retornar código de saída
            sys.exit(0 if sucesso else 1)

        finally:
            # Parar heartbeat
            robo.monitor.parar_heartbeat()

    except KeyboardInterrupt:
        logger.warning("\n🛑 Interrompido pelo usuário")
        sys.exit(130)

    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        logger.exception(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
