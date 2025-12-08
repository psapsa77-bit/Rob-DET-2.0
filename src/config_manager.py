"""
Gerenciador de Configurações - Rob-DET 2.0

Carrega e valida configurações do arquivo settings.json.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class ExecucaoConfig:
    """Configurações de execução."""
    horarios: List[str] = field(default_factory=lambda: ["08:00", "14:00", "18:00"])
    dias_semana: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])
    timeout_por_cliente: int = 180
    max_tentativas: int = 3
    delay_entre_clientes: float = 2.0
    apenas_nao_lidas: bool = True
    extrair_detalhes_completos: bool = False
    download_anexos: bool = False


@dataclass
class ChromeConfig:
    """Configurações do Chrome/navegador."""
    headless: bool = False
    download_path: str = "./downloads"
    window_size: str = "1920,1080"
    user_agent: str = ""
    disable_images: bool = False
    page_load_timeout: int = 60


@dataclass
class NotificacoesConfig:
    """Configurações de notificações."""
    email_ativo: bool = False
    email_servidor: str = "smtp.gmail.com"
    email_porta: int = 587
    email_remetente: str = ""
    email_senha: str = ""
    email_destinatarios: List[str] = field(default_factory=list)
    email_enviar_apenas_urgentes: bool = False
    email_enviar_resumo_diario: bool = True
    whatsapp_ativo: bool = False
    whatsapp_api_url: str = ""
    whatsapp_token: str = ""


@dataclass
class LogsConfig:
    """Configurações de logging."""
    nivel: str = "INFO"
    formato: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
    arquivo: str = "logs/robo_det.log"
    max_size_mb: int = 10
    backup_count: int = 5
    colorir_console: bool = True
    log_para_arquivo: bool = True
    log_para_console: bool = True


@dataclass
class MonitoramentoConfig:
    """Configurações de monitoramento."""
    heartbeat_ativo: bool = True
    heartbeat_intervalo_segundos: int = 300
    heartbeat_arquivo: str = "logs/heartbeat.json"
    metricas_ativo: bool = True
    metricas_arquivo: str = "logs/metricas.json"
    alerta_taxa_falha_acima: float = 0.3
    alerta_tempo_execucao_acima: int = 600


@dataclass
class RecuperacaoConfig:
    """Configurações de recuperação."""
    reiniciar_apos_falha: bool = True
    max_reinicializacoes: int = 3
    delay_reinicializacao_segundos: int = 60
    screenshot_em_erro: bool = True
    salvar_html_em_erro: bool = False


@dataclass
class RelatoriosConfig:
    """Configurações de relatórios."""
    gerar_excel: bool = True
    gerar_csv: bool = True
    gerar_json: bool = True
    pasta_saida: str = "./relatorios"
    incluir_timestamp: bool = True
    separar_por_data: bool = True


class ConfigManager:
    """
    Gerenciador de configurações do sistema.

    Carrega, valida e fornece acesso às configurações do settings.json.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Inicializa o gerenciador de configurações.

        Args:
            config_path: Caminho para o arquivo de configuração
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "settings.json"

        self.config_path = Path(config_path)
        self._raw_config: Dict[str, Any] = {}

        # Configurações tipadas
        self.execucao: ExecucaoConfig
        self.chrome: ChromeConfig
        self.notificacoes: NotificacoesConfig
        self.logs: LogsConfig
        self.monitoramento: MonitoramentoConfig
        self.recuperacao: RecuperacaoConfig
        self.relatorios: RelatoriosConfig

        self.load()

    def load(self) -> None:
        """Carrega configurações do arquivo JSON."""
        try:
            if not self.config_path.exists():
                logger.warning(f"Arquivo de configuração não encontrado: {self.config_path}")
                logger.info("Usando configurações padrão")
                self._raw_config = {}
                self._load_defaults()
                return

            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._raw_config = json.load(f)

            logger.info(f"Configurações carregadas: {self.config_path}")
            self._parse_config()
            self._validate()

        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON: {e}")
            logger.warning("Usando configurações padrão")
            self._load_defaults()

        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
            logger.warning("Usando configurações padrão")
            self._load_defaults()

    def _load_defaults(self) -> None:
        """Carrega configurações padrão."""
        self.execucao = ExecucaoConfig()
        self.chrome = ChromeConfig()
        self.notificacoes = NotificacoesConfig()
        self.logs = LogsConfig()
        self.monitoramento = MonitoramentoConfig()
        self.recuperacao = RecuperacaoConfig()
        self.relatorios = RelatoriosConfig()

    def _parse_config(self) -> None:
        """Converte dicionário para objetos tipados."""
        self.execucao = ExecucaoConfig(**self._raw_config.get('execucao', {}))
        self.chrome = ChromeConfig(**self._raw_config.get('chrome', {}))
        self.notificacoes = NotificacoesConfig(**self._raw_config.get('notificacoes', {}))
        self.logs = LogsConfig(**self._raw_config.get('logs', {}))
        self.monitoramento = MonitoramentoConfig(**self._raw_config.get('monitoramento', {}))
        self.recuperacao = RecuperacaoConfig(**self._raw_config.get('recuperacao', {}))
        self.relatorios = RelatoriosConfig(**self._raw_config.get('relatorios', {}))

    def _validate(self) -> None:
        """Valida configurações."""
        # Validar horários
        for horario in self.execucao.horarios:
            try:
                hora, minuto = horario.split(':')
                if not (0 <= int(hora) < 24 and 0 <= int(minuto) < 60):
                    raise ValueError
            except:
                logger.warning(f"Horário inválido: {horario}")

        # Validar dias da semana (0-6)
        if not all(0 <= dia <= 6 for dia in self.execucao.dias_semana):
            logger.warning("Dias da semana inválidos (use 0-6)")

        # Validar timeouts
        if self.execucao.timeout_por_cliente <= 0:
            logger.warning("Timeout inválido, usando padrão: 180s")
            self.execucao.timeout_por_cliente = 180

        # Validar níveis de log
        niveis_validos = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]
        if self.logs.nivel not in niveis_validos:
            logger.warning(f"Nível de log inválido: {self.logs.nivel}, usando INFO")
            self.logs.nivel = "INFO"

        # Criar diretórios se não existirem
        self._create_directories()

    def _create_directories(self) -> None:
        """Cria diretórios necessários."""
        directories = [
            Path(self.chrome.download_path),
            Path(self.logs.arquivo).parent,
            Path(self.monitoramento.heartbeat_arquivo).parent,
            Path(self.monitoramento.metricas_arquivo).parent,
            Path(self.relatorios.pasta_saida),
            Path("screenshots"),
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def save(self, path: Optional[Path] = None) -> None:
        """
        Salva configurações atuais no arquivo JSON.

        Args:
            path: Caminho de destino (opcional)
        """
        if path is None:
            path = self.config_path

        config_dict = {
            'execucao': self.execucao.__dict__,
            'chrome': self.chrome.__dict__,
            'notificacoes': self.notificacoes.__dict__,
            'logs': self.logs.__dict__,
            'monitoramento': self.monitoramento.__dict__,
            'recuperacao': self.recuperacao.__dict__,
            'relatorios': self.relatorios.__dict__,
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"Configurações salvas: {path}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém valor de configuração por chave.

        Args:
            key: Chave no formato "secao.campo" (ex: "execucao.horarios")
            default: Valor padrão se não encontrado

        Returns:
            Valor da configuração
        """
        try:
            parts = key.split('.')
            value = self._raw_config

            for part in parts:
                value = value[part]

            return value

        except (KeyError, TypeError):
            return default

    def reload(self) -> None:
        """Recarrega configurações do arquivo."""
        logger.info("Recarregando configurações...")
        self.load()


# Singleton global
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """
    Obtém instância singleton do gerenciador de configurações.

    Returns:
        ConfigManager
    """
    global _config_manager

    if _config_manager is None:
        _config_manager = ConfigManager()

    return _config_manager


def reload_config() -> None:
    """Recarrega configurações do singleton."""
    global _config_manager

    if _config_manager is not None:
        _config_manager.reload()
    else:
        _config_manager = ConfigManager()


# Exemplo de uso
if __name__ == '__main__':
    config = get_config()

    print(f"Horários: {config.execucao.horarios}")
    print(f"Headless: {config.chrome.headless}")
    print(f"Email ativo: {config.notificacoes.email_ativo}")
    print(f"Nível de log: {config.logs.nivel}")
