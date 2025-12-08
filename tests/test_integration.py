"""
Testes de Integração - Rob-DET 2.0

Testes de integração que validam o fluxo completo do robô.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from main import RoboDET
from src.monitoring import Monitor
from src.notifications import EmailNotifier


@pytest.mark.integration
class TestFluxoCompleto:
    """Testes de integração do fluxo completo."""

    @patch('main.DETNavigator')
    @patch('main.DETScraper')
    def test_execucao_completa_sucesso(
        self,
        mock_scraper_class,
        mock_navigator_class,
        config_mock,
        cliente_teste,
        relatorio_teste,
        temp_dir,
        monkeypatch
    ):
        """Testa execução completa com sucesso."""
        # Configurar mocks
        mock_navigator = MagicMock()
        mock_navigator_class.return_value = mock_navigator

        mock_scraper = MagicMock()
        mock_scraper.login.return_value = True
        mock_scraper.consultar_cliente.return_value = relatorio_teste
        mock_scraper_class.return_value = mock_scraper

        # Mock do carregamento de clientes
        monkeypatch.setattr(
            'main.Path',
            lambda x: temp_dir if x == "config/clientes.json" else Path(x)
        )

        # Criar robô com config de teste
        with patch('main.get_config', return_value=config_mock):
            robo = RoboDET(config=config_mock)

            # Mock do carregamento de clientes
            robo.carregar_clientes = Mock(return_value=[cliente_teste])

            # Executar
            sucesso = robo.executar()

        # Verificações
        assert sucesso is True
        mock_navigator_class.assert_called_once()
        mock_navigator.start.assert_called_once()
        mock_scraper.login.assert_called_once()
        mock_scraper.consultar_cliente.assert_called_once()
        mock_navigator.stop.assert_called()

    @patch('main.DETNavigator')
    @patch('main.DETScraper')
    def test_execucao_falha_login(
        self,
        mock_scraper_class,
        mock_navigator_class,
        config_mock,
        cliente_teste
    ):
        """Testa tratamento de falha no login."""
        # Mock do navegador e scraper
        mock_navigator = MagicMock()
        mock_navigator_class.return_value = mock_navigator

        mock_scraper = MagicMock()
        mock_scraper.login.return_value = False  # Login falha
        mock_scraper_class.return_value = mock_scraper

        # Criar robô
        with patch('main.get_config', return_value=config_mock):
            robo = RoboDET(config=config_mock)
            robo.carregar_clientes = Mock(return_value=[cliente_teste])

            # Desabilitar recuperação para teste
            robo.config.recuperacao.reiniciar_apos_falha = False

            # Executar
            sucesso = robo.executar()

        # Verificações
        assert sucesso is False
        mock_scraper.login.assert_called_once()
        mock_navigator.stop.assert_called()  # Navegador deve ser finalizado

    @patch('main.DETNavigator')
    @patch('main.DETScraper')
    def test_execucao_multiplos_clientes(
        self,
        mock_scraper_class,
        mock_navigator_class,
        config_mock,
        clientes_teste,
        relatorio_teste
    ):
        """Testa execução com múltiplos clientes."""
        # Mock do navegador e scraper
        mock_navigator = MagicMock()
        mock_navigator_class.return_value = mock_navigator

        mock_scraper = MagicMock()
        mock_scraper.login.return_value = True
        mock_scraper.consultar_cliente.return_value = relatorio_teste
        mock_scraper_class.return_value = mock_scraper

        # Criar robô
        with patch('main.get_config', return_value=config_mock):
            robo = RoboDET(config=config_mock)

            # Filtrar apenas clientes ativos
            clientes_ativos = [c for c in clientes_teste if c.ativo]
            robo.carregar_clientes = Mock(return_value=clientes_ativos)

            # Executar
            sucesso = robo.executar()

        # Verificações
        assert sucesso is True
        # Deve ter consultado apenas clientes ativos (2)
        assert mock_scraper.consultar_cliente.call_count == 2


@pytest.mark.integration
class TestMonitoring:
    """Testes de integração do sistema de monitoramento."""

    def test_heartbeat_lifecycle(self, config_mock, temp_dir):
        """Testa ciclo de vida do heartbeat."""
        import time

        # Ativar heartbeat no config de teste
        config_mock.monitoramento.heartbeat_ativo = True
        config_mock.monitoramento.heartbeat_intervalo_segundos = 1

        monitor = Monitor(config_mock)

        # Iniciar heartbeat
        monitor.iniciar_heartbeat()
        monitor.set_status("running")

        # Aguardar um pouco
        time.sleep(2)

        # Verificar se arquivo foi criado
        heartbeat_file = Path(config_mock.monitoramento.heartbeat_arquivo)
        assert heartbeat_file.exists()

        # Parar heartbeat
        monitor.parar_heartbeat()

    def test_registrar_metricas(self, config_mock, relatorio_teste, temp_dir):
        """Testa registro de métricas."""
        monitor = Monitor(config_mock)

        # Registrar execução
        metrica = monitor.registrar_execucao(
            relatorios=[relatorio_teste],
            tempo_total=45.5,
            erros=[]
        )

        # Verificações
        assert metrica is not None
        assert metrica.total_clientes == 1
        assert metrica.clientes_sucesso == 1
        assert metrica.total_mensagens == 3
        assert metrica.mensagens_novas == 2

        # Verificar se arquivo foi criado
        metricas_file = Path(config_mock.monitoramento.metricas_arquivo)
        assert metricas_file.exists()


@pytest.mark.integration
class TestNotifications:
    """Testes de integração do sistema de notificações."""

    def test_montar_html_resumo(self, config_mock, relatorio_teste):
        """Testa montagem de HTML de resumo."""
        notifier = EmailNotifier(config_mock)

        html = notifier._montar_html_resumo(
            total_clientes=1,
            clientes_sucesso=1,
            total_mensagens=3,
            total_novas=2,
            total_urgentes=2,
            tempo_total=45.5,
            relatorios=[relatorio_teste],
            erros=[]
        )

        # Verificações
        assert isinstance(html, str)
        assert "Empresa Teste Ltda" in html
        assert "12.345.678/0001-90" in html
        assert "45.0s" in html or "45s" in html

    def test_montar_html_urgentes(self, config_mock, relatorio_teste):
        """Testa montagem de HTML de mensagens urgentes."""
        notifier = EmailNotifier(config_mock)

        html = notifier._montar_html_urgentes([relatorio_teste])

        # Verificações
        assert isinstance(html, str)
        assert "Urgentes" in html or "urgente" in html.lower()


@pytest.mark.integration
@pytest.mark.slow
class TestRecuperacaoFalhas:
    """Testes de recuperação após falhas."""

    @patch('main.DETNavigator')
    @patch('main.DETScraper')
    @patch('time.sleep')  # Mock sleep para acelerar teste
    def test_recuperacao_apos_falha_login(
        self,
        mock_sleep,
        mock_scraper_class,
        mock_navigator_class,
        config_mock,
        cliente_teste
    ):
        """Testa recuperação automática após falha no login."""
        # Configurar navegador
        mock_navigator = MagicMock()
        mock_navigator_class.return_value = mock_navigator

        # Configurar scraper para falhar primeiro e depois funcionar
        mock_scraper = MagicMock()
        mock_scraper.login.side_effect = [False, True]  # Falha na 1ª, sucesso na 2ª
        mock_scraper.consultar_cliente.return_value = Mock(sucesso=True)
        mock_scraper_class.return_value = mock_scraper

        # Habilitar recuperação
        config_mock.recuperacao.reiniciar_apos_falha = True
        config_mock.recuperacao.max_reinicializacoes = 2

        with patch('main.get_config', return_value=config_mock):
            robo = RoboDET(config=config_mock)
            robo.carregar_clientes = Mock(return_value=[cliente_teste])

            # Executar
            sucesso = robo.executar()

        # Verificações
        assert sucesso is True
        # Deve ter tentado login 2 vezes (1 falha + 1 sucesso na recuperação)
        assert mock_scraper.login.call_count == 2


@pytest.mark.integration
class TestReportGeneration:
    """Testes de geração de relatórios."""

    def test_gerar_relatorios_multiplos_formatos(
        self,
        config_mock,
        relatorio_teste,
        temp_dir
    ):
        """Testa geração de relatórios em múltiplos formatos."""
        from src.reports.report_generator import ReportGenerator

        # Configurar pasta de saída
        config_mock.relatorios.pasta_saida = str(temp_dir / "relatorios")

        generator = ReportGenerator(config=config_mock)

        # Gerar relatórios
        excel_path = generator.gerar_relatorio_excel([relatorio_teste])
        csv_path = generator.gerar_relatorio_csv([relatorio_teste])
        json_path = generator.gerar_relatorio_json([relatorio_teste])

        # Verificações
        assert excel_path and Path(excel_path).exists()
        assert csv_path and Path(csv_path).exists()
        assert json_path and Path(json_path).exists()
