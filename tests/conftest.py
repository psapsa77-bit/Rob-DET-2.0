"""
Fixtures compartilhados para testes - Rob-DET 2.0
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock

from src.models import Cliente, Mensagem, RelatorioConsulta, TipoMensagem, StatusMensagem, PrioridadeMensagem
from src.config_manager import ConfigManager


@pytest.fixture
def temp_dir():
    """Diretório temporário para testes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def config_mock(temp_dir):
    """Mock do ConfigManager com configurações de teste."""
    config = Mock(spec=ConfigManager)

    # Configurações de execução
    config.execucao = Mock()
    config.execucao.horarios = ["08:00", "14:00"]
    config.execucao.dias_semana = [0, 1, 2, 3, 4]
    config.execucao.timeout_por_cliente = 60
    config.execucao.max_tentativas = 2
    config.execucao.delay_entre_clientes = 1.0
    config.execucao.apenas_nao_lidas = True

    # Configurações de Chrome
    config.chrome = Mock()
    config.chrome.headless = True
    config.chrome.download_path = str(temp_dir / "downloads")
    config.chrome.window_size = "1920,1080"

    # Configurações de notificações
    config.notificacoes = Mock()
    config.notificacoes.email_ativo = False
    config.notificacoes.email_servidor = "smtp.gmail.com"
    config.notificacoes.email_porta = 587
    config.notificacoes.email_destinatarios = ["test@example.com"]

    # Configurações de logs
    config.logs = Mock()
    config.logs.nivel = "DEBUG"
    config.logs.arquivo = str(temp_dir / "logs" / "test.log")
    config.logs.max_size_mb = 5
    config.logs.backup_count = 2
    config.logs.log_para_console = False
    config.logs.log_para_arquivo = True
    config.logs.colorir_console = False
    config.logs.formato = "{time} | {level} | {message}"

    # Configurações de monitoramento
    config.monitoramento = Mock()
    config.monitoramento.heartbeat_ativo = False
    config.monitoramento.heartbeat_intervalo_segundos = 60
    config.monitoramento.heartbeat_arquivo = str(temp_dir / "logs" / "heartbeat.json")
    config.monitoramento.metricas_ativo = True
    config.monitoramento.metricas_arquivo = str(temp_dir / "logs" / "metricas.json")
    config.monitoramento.alerta_taxa_falha_acima = 0.3
    config.monitoramento.alerta_tempo_execucao_acima = 300

    # Configurações de recuperação
    config.recuperacao = Mock()
    config.recuperacao.reiniciar_apos_falha = True
    config.recuperacao.max_reinicializacoes = 2
    config.recuperacao.delay_reinicializacao_segundos = 5
    config.recuperacao.screenshot_em_erro = True

    # Configurações de relatórios
    config.relatorios = Mock()
    config.relatorios.gerar_excel = True
    config.relatorios.gerar_csv = True
    config.relatorios.gerar_json = True
    config.relatorios.pasta_saida = str(temp_dir / "relatorios")
    config.relatorios.incluir_timestamp = True

    return config


@pytest.fixture
def cliente_teste():
    """Cliente de teste."""
    return Cliente(
        cnpj="12.345.678/0001-90",
        razao_social="Empresa Teste Ltda",
        ativo=True,
        prioridade="normal"
    )


@pytest.fixture
def clientes_teste():
    """Lista de clientes de teste."""
    return [
        Cliente(cnpj="12.345.678/0001-90", razao_social="Empresa A Ltda", prioridade="alta"),
        Cliente(cnpj="98.765.432/0001-10", razao_social="Empresa B Ltda", prioridade="normal"),
        Cliente(cnpj="11.222.333/0001-44", razao_social="Empresa C Ltda", prioridade="baixa", ativo=False),
    ]


@pytest.fixture
def mensagem_teste():
    """Mensagem de teste."""
    return Mensagem(
        id="msg_001",
        cnpj_destinatario="12.345.678/0001-90",
        data_envio=datetime(2025, 12, 1, 10, 30),
        remetente="Superintendência Regional do Trabalho",
        assunto="Notificação - Fiscalização Trabalhista",
        tipo=TipoMensagem.NOTIFICACAO,
        status=StatusMensagem.NAO_LIDA,
        prioridade=PrioridadeMensagem.NORMAL,
        conteudo="Conteúdo da notificação...",
        prazo_resposta=datetime(2025, 12, 15),
        numero_processo="12345.678/2025",
        possui_anexo=True
    )


@pytest.fixture
def mensagens_teste():
    """Lista de mensagens de teste."""
    return [
        Mensagem(
            id="msg_001",
            cnpj_destinatario="12.345.678/0001-90",
            data_envio=datetime(2025, 12, 1),
            remetente="SRT",
            assunto="Intimação",
            tipo=TipoMensagem.INTIMACAO,
            status=StatusMensagem.NAO_LIDA,
            prioridade=PrioridadeMensagem.URGENTE
        ),
        Mensagem(
            id="msg_002",
            cnpj_destinatario="12.345.678/0001-90",
            data_envio=datetime(2025, 12, 2),
            remetente="SRT",
            assunto="Comunicado",
            tipo=TipoMensagem.COMUNICADO,
            status=StatusMensagem.LIDA,
            prioridade=PrioridadeMensagem.NORMAL
        ),
        Mensagem(
            id="msg_003",
            cnpj_destinatario="12.345.678/0001-90",
            data_envio=datetime(2025, 12, 3),
            remetente="SRT",
            assunto="Autuação - Multa",
            tipo=TipoMensagem.AUTUACAO,
            status=StatusMensagem.NAO_LIDA,
            prioridade=PrioridadeMensagem.ALTA,
            prazo_resposta=datetime(2025, 12, 10)
        ),
    ]


@pytest.fixture
def relatorio_teste(cliente_teste, mensagens_teste):
    """Relatório de consulta de teste."""
    relatorio = RelatorioConsulta(
        data_consulta=datetime(2025, 12, 8, 14, 0),
        cnpj=cliente_teste.cnpj,
        razao_social=cliente_teste.razao_social
    )

    relatorio.mensagens = mensagens_teste
    relatorio.sucesso = True
    relatorio.tempo_execucao = 45.5
    relatorio.calcular_estatisticas()

    return relatorio


@pytest.fixture
def mock_webdriver():
    """Mock do Selenium WebDriver."""
    driver = MagicMock()
    driver.current_url = "https://det.sit.trabalho.gov.br/"
    driver.title = "DET - Domicílio Eletrônico Trabalhista"
    driver.page_source = "<html><body>Test</body></html>"

    # Mock de elementos
    element = MagicMock()
    element.text = "Test Element"
    element.is_displayed.return_value = True
    element.is_enabled.return_value = True

    driver.find_element.return_value = element
    driver.find_elements.return_value = [element]

    return driver


@pytest.fixture
def arquivo_clientes_teste(temp_dir):
    """Arquivo de clientes de teste."""
    clientes_data = {
        "clientes": [
            {
                "cnpj": "12.345.678/0001-90",
                "razao_social": "Empresa Teste A Ltda",
                "ativo": True,
                "prioridade": "alta"
            },
            {
                "cnpj": "98.765.432/0001-10",
                "razao_social": "Empresa Teste B Ltda",
                "ativo": True,
                "prioridade": "normal"
            }
        ]
    }

    config_dir = temp_dir / "config"
    config_dir.mkdir(exist_ok=True)

    arquivo = config_dir / "clientes.json"
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(clientes_data, f, indent=2, ensure_ascii=False)

    return arquivo


@pytest.fixture
def arquivo_settings_teste(temp_dir):
    """Arquivo settings.json de teste."""
    settings_data = {
        "execucao": {
            "horarios": ["08:00", "14:00"],
            "dias_semana": [0, 1, 2, 3, 4],
            "timeout_por_cliente": 60
        },
        "chrome": {
            "headless": True,
            "download_path": str(temp_dir / "downloads")
        },
        "logs": {
            "nivel": "DEBUG",
            "arquivo": str(temp_dir / "logs" / "test.log")
        }
    }

    config_dir = temp_dir / "config"
    config_dir.mkdir(exist_ok=True)

    arquivo = config_dir / "settings.json"
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(settings_data, f, indent=2, ensure_ascii=False)

    return arquivo


# Markers personalizados
def pytest_configure(config):
    """Configuração de markers personalizados."""
    config.addinivalue_line("markers", "unit: Testes unitários")
    config.addinivalue_line("markers", "integration: Testes de integração")
    config.addinivalue_line("markers", "slow: Testes lentos")
    config.addinivalue_line("markers", "selenium: Testes que usam Selenium")
