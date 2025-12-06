"""
Módulo de Logging - Rob-DET 2.0

Configuração centralizada de logging usando Loguru com suporte a:
- Rotação de arquivos
- Níveis de log configuráveis
- Formatação rica para terminal
- Screenshots em caso de erro
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger
from rich.console import Console

# Console rico para output formatado
console = Console()


def setup_logging(
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "1 month",
    console_output: bool = True
) -> None:
    """
    Configura o sistema de logging global.

    Args:
        log_file: Caminho para o arquivo de log (None = sem arquivo)
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        rotation: Tamanho máximo antes de rotacionar (ex: "10 MB")
        retention: Tempo de retenção dos logs antigos (ex: "1 month")
        console_output: Se True, exibe logs no console

    Example:
        >>> setup_logging(
        ...     log_file="./logs/det_robot.log",
        ...     log_level="INFO",
        ...     rotation="10 MB"
        ... )
    """
    # Remove handlers padrão
    logger.remove()

    # Formato de log
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Console output
    if console_output:
        logger.add(
            sys.stdout,
            format=log_format,
            level=log_level,
            colorize=True,
        )

    # File output
    if log_file:
        # Criar diretório de logs se não existir
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            format=log_format,
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip",  # Comprimir logs antigos
            encoding="utf-8",
        )

    logger.info(f"Logging configurado - Nível: {log_level}")


def get_logger(name: str) -> logger:
    """
    Retorna um logger com contexto específico.

    Args:
        name: Nome do módulo/contexto

    Returns:
        Logger configurado

    Example:
        >>> log = get_logger(__name__)
        >>> log.info("Mensagem de teste")
    """
    return logger.bind(name=name)


def log_error_with_screenshot(
    error: Exception,
    driver: Optional[object] = None,
    screenshot_dir: str = "./logs/screenshots"
) -> None:
    """
    Registra erro e salva screenshot se driver estiver disponível.

    Args:
        error: Exceção capturada
        driver: WebDriver do Selenium (opcional)
        screenshot_dir: Diretório para salvar screenshots

    Example:
        >>> try:
        ...     # código que pode falhar
        ...     pass
        ... except Exception as e:
        ...     log_error_with_screenshot(e, driver)
    """
    from datetime import datetime

    logger.error(f"Erro capturado: {type(error).__name__}: {str(error)}")

    if driver:
        try:
            # Criar diretório se não existir
            screenshot_path = Path(screenshot_dir)
            screenshot_path.mkdir(parents=True, exist_ok=True)

            # Nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = screenshot_path / f"error_{timestamp}.png"

            # Salvar screenshot
            driver.save_screenshot(str(filename))
            logger.info(f"Screenshot salvo: {filename}")

        except Exception as screenshot_error:
            logger.warning(f"Falha ao salvar screenshot: {screenshot_error}")


def log_step(step_name: str, details: Optional[str] = None) -> None:
    """
    Registra um passo da execução com formatação destacada.

    Args:
        step_name: Nome do passo
        details: Detalhes adicionais (opcional)

    Example:
        >>> log_step("Acessando portal DET", "URL: https://det.sit.trabalho.gov.br")
    """
    separator = "=" * 60
    logger.info(separator)
    logger.info(f"▶ {step_name}")
    if details:
        logger.info(f"  {details}")
    logger.info(separator)


def log_success(message: str) -> None:
    """
    Registra mensagem de sucesso com destaque.

    Args:
        message: Mensagem de sucesso

    Example:
        >>> log_success("Login realizado com sucesso!")
    """
    logger.success(f"✓ {message}")


def log_warning(message: str) -> None:
    """
    Registra aviso com destaque.

    Args:
        message: Mensagem de aviso

    Example:
        >>> log_warning("Certificado expira em 30 dias")
    """
    logger.warning(f"⚠ {message}")


# Configuração padrão ao importar o módulo
if __name__ != "__main__":
    setup_logging(
        log_file="./logs/det_robot.log",
        log_level="INFO",
        console_output=True
    )
