"""
Testes Unitários - ConfigManager - Rob-DET 2.0
"""

import pytest
import json
from pathlib import Path

from src.config_manager import (
    ConfigManager,
    ExecucaoConfig,
    ChromeConfig,
    NotificacoesConfig,
    LogsConfig,
    get_config,
    reload_config
)


@pytest.mark.unit
class TestConfigManager:
    """Testes para ConfigManager."""

    def test_load_default_config(self, temp_dir):
        """Testa carregamento de configuração padrão quando arquivo não existe."""
        config = ConfigManager(config_path=temp_dir / "nonexistent.json")

        assert config.execucao.horarios == ["08:00", "14:00", "18:00"]
        assert config.chrome.headless is False
        assert config.logs.nivel == "INFO"

    def test_load_from_file(self, arquivo_settings_teste):
        """Testa carregamento de configuração de arquivo."""
        config = ConfigManager(config_path=arquivo_settings_teste)

        assert config.execucao.horarios == ["08:00", "14:00"]
        assert config.execucao.dias_semana == [0, 1, 2, 3, 4]
        assert config.execucao.timeout_por_cliente == 60
        assert config.chrome.headless is True

    def test_validate_horarios(self, temp_dir):
        """Testa validação de horários."""
        settings_data = {
            "execucao": {
                "horarios": ["08:00", "25:00", "14:00"],  # 25:00 é inválido
            }
        }

        arquivo = temp_dir / "settings.json"
        with open(arquivo, 'w') as f:
            json.dump(settings_data, f)

        # Deve carregar sem erro, mas logar warning
        config = ConfigManager(config_path=arquivo)
        assert config.execucao is not None

    def test_validate_dias_semana(self, temp_dir):
        """Testa validação de dias da semana."""
        settings_data = {
            "execucao": {
                "dias_semana": [0, 1, 2, 7, 8],  # 7 e 8 são inválidos
            }
        }

        arquivo = temp_dir / "settings.json"
        with open(arquivo, 'w') as f:
            json.dump(settings_data, f)

        # Deve carregar sem erro, mas logar warning
        config = ConfigManager(config_path=arquivo)
        assert config.execucao is not None

    def test_get_method(self, arquivo_settings_teste):
        """Testa método get() para acessar valores."""
        config = ConfigManager(config_path=arquivo_settings_teste)

        assert config.get("execucao.horarios") == ["08:00", "14:00"]
        assert config.get("chrome.headless") is True
        assert config.get("inexistente.campo", default="valor_padrao") == "valor_padrao"

    def test_save_config(self, temp_dir):
        """Testa salvamento de configuração."""
        config = ConfigManager()

        # Modificar config
        config.execucao.horarios = ["09:00", "15:00"]

        # Salvar
        save_path = temp_dir / "saved_config.json"
        config.save(save_path)

        assert save_path.exists()

        # Carregar novamente
        config2 = ConfigManager(config_path=save_path)
        assert config2.execucao.horarios == ["09:00", "15:00"]

    def test_reload_config(self, arquivo_settings_teste):
        """Testa reload de configuração."""
        config = ConfigManager(config_path=arquivo_settings_teste)

        original_horarios = config.execucao.horarios.copy()

        # Modificar arquivo
        with open(arquivo_settings_teste, 'r') as f:
            data = json.load(f)

        data['execucao']['horarios'] = ["10:00", "16:00"]

        with open(arquivo_settings_teste, 'w') as f:
            json.dump(data, f)

        # Reload
        config.reload()

        assert config.execucao.horarios == ["10:00", "16:00"]
        assert config.execucao.horarios != original_horarios

    def test_create_directories(self, temp_dir):
        """Testa criação automática de diretórios."""
        settings_data = {
            "chrome": {"download_path": str(temp_dir / "downloads")},
            "logs": {"arquivo": str(temp_dir / "logs" / "app.log")},
            "monitoramento": {
                "heartbeat_arquivo": str(temp_dir / "logs" / "heartbeat.json"),
                "metricas_arquivo": str(temp_dir / "logs" / "metricas.json")
            },
            "relatorios": {"pasta_saida": str(temp_dir / "relatorios")}
        }

        arquivo = temp_dir / "settings.json"
        with open(arquivo, 'w') as f:
            json.dump(settings_data, f)

        config = ConfigManager(config_path=arquivo)

        # Diretórios devem ter sido criados
        assert (temp_dir / "downloads").exists()
        assert (temp_dir / "logs").exists()
        assert (temp_dir / "relatorios").exists()
        assert (temp_dir / "screenshots").exists()


@pytest.mark.unit
class TestDataclasses:
    """Testes para dataclasses de configuração."""

    def test_execucao_config_defaults(self):
        """Testa valores padrão de ExecucaoConfig."""
        config = ExecucaoConfig()

        assert config.horarios == ["08:00", "14:00", "18:00"]
        assert config.dias_semana == [0, 1, 2, 3, 4]
        assert config.timeout_por_cliente == 180
        assert config.max_tentativas == 3
        assert config.apenas_nao_lidas is True

    def test_chrome_config_defaults(self):
        """Testa valores padrão de ChromeConfig."""
        config = ChromeConfig()

        assert config.headless is False
        assert config.download_path == "./downloads"
        assert config.window_size == "1920,1080"
        assert config.page_load_timeout == 60

    def test_notificacoes_config_defaults(self):
        """Testa valores padrão de NotificacoesConfig."""
        config = NotificacoesConfig()

        assert config.email_ativo is False
        assert config.email_servidor == "smtp.gmail.com"
        assert config.email_porta == 587
        assert config.email_destinatarios == []

    def test_logs_config_defaults(self):
        """Testa valores padrão de LogsConfig."""
        config = LogsConfig()

        assert config.nivel == "INFO"
        assert config.arquivo == "logs/robo_det.log"
        assert config.max_size_mb == 10
        assert config.backup_count == 5
        assert config.colorir_console is True


@pytest.mark.unit
class TestSingleton:
    """Testes para singleton global."""

    def test_get_config_singleton(self):
        """Testa que get_config() retorna mesma instância."""
        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_reload_config_singleton(self):
        """Testa reload do singleton."""
        config1 = get_config()
        original_id = id(config1)

        reload_config()

        config2 = get_config()
        # Deve ser mesma instância (singleton), mas recarregada
        assert config2 is not None
