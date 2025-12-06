"""
Módulo de Configuração - Rob-DET 2.0

Gerenciamento centralizado de configurações do sistema usando:
- Arquivos YAML para configurações estruturadas
- Variáveis de ambiente (.env) para dados sensíveis
- Validação com Pydantic
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class ClientConfig(BaseModel):
    """Configuração de um cliente."""
    cnpj: str = Field(..., description="CNPJ do cliente (formato: 00.000.000/0001-00)")
    razao_social: str = Field(..., description="Razão social do cliente")
    nome_fantasia: Optional[str] = Field(None, description="Nome fantasia")
    active: bool = Field(True, description="Cliente ativo para processamento")
    priority: str = Field("normal", description="Prioridade: high, normal, low")
    email_notificacao: Optional[str] = Field(None, description="Email para notificações")
    observacoes: Optional[str] = Field("", description="Observações adicionais")
    filiais: Optional[List[Dict[str, str]]] = Field(None, description="Lista de filiais")

    @validator('cnpj')
    def validate_cnpj(cls, v):
        """Valida formato do CNPJ."""
        # Remove caracteres não numéricos
        cnpj_numbers = ''.join(filter(str.isdigit, v))
        if len(cnpj_numbers) != 14:
            raise ValueError(f'CNPJ deve ter 14 dígitos: {v}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        """Valida prioridade."""
        valid_priorities = ['high', 'normal', 'low']
        if v not in valid_priorities:
            raise ValueError(f'Prioridade deve ser uma de: {valid_priorities}')
        return v


class AppSettings(BaseSettings):
    """Configurações da aplicação via variáveis de ambiente."""

    # Certificado Digital
    cert_path: str = Field(..., env='CERT_PATH')
    cert_password: Optional[str] = Field(None, env='CERT_PASSWORD')
    use_keyring: bool = Field(True, env='USE_KEYRING')
    keyring_service: str = Field('det_robot', env='KEYRING_SERVICE')

    # Selenium / Navegador
    browser: str = Field('chrome', env='BROWSER')
    headless: bool = Field(False, env='HEADLESS')
    default_timeout: int = Field(30, env='DEFAULT_TIMEOUT')
    action_delay: float = Field(1.5, env='ACTION_DELAY')

    # Portal DET
    det_url: str = Field('https://det.sit.trabalho.gov.br/', env='DET_URL')
    auth_method: str = Field('certificado', env='AUTH_METHOD')

    # Procuração Eletrônica
    contador_cnpj: Optional[str] = Field(None, env='CONTADOR_CNPJ')
    contador_cpf: Optional[str] = Field(None, env='CONTADOR_CPF')

    # Logging
    log_level: str = Field('INFO', env='LOG_LEVEL')
    log_file: str = Field('./logs/det_robot.log', env='LOG_FILE')
    log_max_size: int = Field(10, env='LOG_MAX_SIZE')
    log_backup_count: int = Field(5, env='LOG_BACKUP_COUNT')

    # Banco de Dados
    database_url: str = Field('sqlite:///./data/det_messages.db', env='DATABASE_URL')

    # Exportação
    export_dir: str = Field('./data/exports', env='EXPORT_DIR')
    export_format: str = Field('excel', env='EXPORT_FORMAT')

    # Agendamento
    enable_scheduling: bool = Field(False, env='ENABLE_SCHEDULING')
    schedule_time: str = Field('09:00', env='SCHEDULE_TIME')
    schedule_days: str = Field('0,1,2,3,4', env='SCHEDULE_DAYS')

    # Notificações
    enable_notifications: bool = Field(False, env='ENABLE_NOTIFICATIONS')

    # Debug
    debug: bool = Field(False, env='DEBUG')
    save_error_screenshots: bool = Field(True, env='SAVE_ERROR_SCREENSHOTS')
    screenshot_dir: str = Field('./logs/screenshots', env='SCREENSHOT_DIR')

    # Segurança
    max_execution_time: int = Field(60, env='MAX_EXECUTION_TIME')
    max_retries: int = Field(3, env='MAX_RETRIES')
    retry_delay: int = Field(5, env='RETRY_DELAY')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False


class Config:
    """
    Classe principal de configuração que combina:
    - Configurações de variáveis de ambiente (.env)
    - Configurações estruturadas (YAML)
    - Lista de clientes
    """

    def __init__(
        self,
        env_file: str = '.env',
        settings_file: str = 'config/settings.yaml',
        clients_file: str = 'config/clients.yaml'
    ):
        """
        Inicializa configuração.

        Args:
            env_file: Caminho para arquivo .env
            settings_file: Caminho para settings.yaml
            clients_file: Caminho para clients.yaml
        """
        # Carregar variáveis de ambiente
        load_dotenv(env_file)

        # Carregar configurações da aplicação
        self.app = AppSettings()

        # Carregar configurações estruturadas
        self.settings = self._load_yaml(settings_file)

        # Carregar lista de clientes
        self.clients = self._load_clients(clients_file)

    def _load_yaml(self, filepath: str) -> Dict[str, Any]:
        """
        Carrega arquivo YAML.

        Args:
            filepath: Caminho para o arquivo YAML

        Returns:
            Dicionário com configurações
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {filepath}")

        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def _load_clients(self, filepath: str) -> List[ClientConfig]:
        """
        Carrega e valida lista de clientes.

        Args:
            filepath: Caminho para clients.yaml

        Returns:
            Lista de ClientConfig validados
        """
        path = Path(filepath)
        if not path.exists():
            # Se arquivo não existe, retorna lista vazia
            return []

        data = self._load_yaml(filepath)
        clients_data = data.get('clients', [])

        # Validar cada cliente usando Pydantic
        clients = []
        for client_data in clients_data:
            try:
                client = ClientConfig(**client_data)
                clients.append(client)
            except Exception as e:
                print(f"Erro ao validar cliente {client_data.get('cnpj', 'DESCONHECIDO')}: {e}")

        return clients

    def get_active_clients(self) -> List[ClientConfig]:
        """
        Retorna apenas clientes ativos.

        Returns:
            Lista de clientes ativos
        """
        return [c for c in self.clients if c.active]

    def get_client_by_cnpj(self, cnpj: str) -> Optional[ClientConfig]:
        """
        Busca cliente por CNPJ.

        Args:
            cnpj: CNPJ do cliente (com ou sem formatação)

        Returns:
            ClientConfig ou None se não encontrado
        """
        # Remove caracteres não numéricos para comparação
        cnpj_numbers = ''.join(filter(str.isdigit, cnpj))

        for client in self.clients:
            client_numbers = ''.join(filter(str.isdigit, client.cnpj))
            if client_numbers == cnpj_numbers:
                return client

        return None

    def get_clients_by_priority(self, priority: str) -> List[ClientConfig]:
        """
        Retorna clientes por prioridade.

        Args:
            priority: Prioridade (high, normal, low)

        Returns:
            Lista de clientes com a prioridade especificada
        """
        return [c for c in self.get_active_clients() if c.priority == priority]

    def get_setting(self, path: str, default: Any = None) -> Any:
        """
        Obtém configuração usando notação de ponto.

        Args:
            path: Caminho da configuração (ex: 'det.timeouts.page_load')
            default: Valor padrão se não encontrado

        Returns:
            Valor da configuração

        Example:
            >>> config.get_setting('det.timeouts.page_load')
            30
        """
        keys = path.split('.')
        value = self.settings

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def __repr__(self) -> str:
        """Representação string da configuração."""
        return (
            f"Config(\n"
            f"  Clientes ativos: {len(self.get_active_clients())}\n"
            f"  Navegador: {self.app.browser}\n"
            f"  Headless: {self.app.headless}\n"
            f"  Debug: {self.app.debug}\n"
            f")"
        )


def load_config(
    env_file: str = '.env',
    settings_file: str = 'config/settings.yaml',
    clients_file: str = 'config/clients.yaml'
) -> Config:
    """
    Função helper para carregar configuração.

    Args:
        env_file: Caminho para .env
        settings_file: Caminho para settings.yaml
        clients_file: Caminho para clients.yaml

    Returns:
        Instância de Config

    Example:
        >>> config = load_config()
        >>> print(config.app.browser)
        chrome
    """
    return Config(env_file, settings_file, clients_file)


# Exemplo de uso
if __name__ == '__main__':
    # Teste de carregamento
    try:
        config = load_config()
        print(config)
        print(f"\nClientes ativos: {len(config.get_active_clients())}")

        for client in config.get_active_clients():
            print(f"  - {client.razao_social} ({client.cnpj}) - Prioridade: {client.priority}")

    except Exception as e:
        print(f"Erro ao carregar configuração: {e}")
