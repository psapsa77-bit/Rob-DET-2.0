"""
Sistema de Retry - Rob-DET 2.0

Decoradores e funções para retry automático de operações.
"""

import time
import functools
from typing import Callable, Tuple, Type, Optional
from loguru import logger

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    ElementNotInteractableException
)


# Exceções que devem acionar retry
RETRYABLE_EXCEPTIONS = (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)


def retry_on_exception(
    max_attempts: int = 3,
    delay: float = 2.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = RETRYABLE_EXCEPTIONS,
    on_retry: Optional[Callable] = None
):
    """
    Decorator para retry automático em caso de exceção.

    Args:
        max_attempts: Número máximo de tentativas
        delay: Delay inicial entre tentativas (segundos)
        backoff: Multiplicador de backoff exponencial
        exceptions: Tupla de exceções que devem acionar retry
        on_retry: Callback executado a cada retry

    Example:
        >>> @retry_on_exception(max_attempts=3, delay=2)
        ... def fazer_algo():
        ...     # código que pode falhar
        ...     pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Falha após {max_attempts} tentativas: "
                            f"{func.__name__}: {type(e).__name__}: {e}"
                        )
                        raise

                    logger.warning(
                        f"Tentativa {attempt}/{max_attempts} falhou: "
                        f"{func.__name__}: {type(e).__name__}: {e}"
                    )

                    # Executar callback se fornecido
                    if on_retry:
                        try:
                            on_retry(attempt, e)
                        except Exception as callback_error:
                            logger.warning(f"Erro no callback de retry: {callback_error}")

                    # Aguardar antes de retry
                    logger.info(f"Aguardando {current_delay:.1f}s antes de retry...")
                    time.sleep(current_delay)

                    # Backoff exponencial
                    current_delay *= backoff

        return wrapper
    return decorator


def retry_on_false(
    max_attempts: int = 3,
    delay: float = 2.0,
    backoff: float = 1.5
):
    """
    Decorator para retry quando função retorna False.

    Args:
        max_attempts: Número máximo de tentativas
        delay: Delay inicial entre tentativas
        backoff: Multiplicador de backoff

    Example:
        >>> @retry_on_false(max_attempts=3)
        ... def tentar_clicar():
        ...     return element.click()  # Retorna False se falhar
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                result = func(*args, **kwargs)

                if result:
                    return result

                if attempt == max_attempts:
                    logger.error(
                        f"Falha após {max_attempts} tentativas: "
                        f"{func.__name__} retornou False"
                    )
                    return False

                logger.warning(
                    f"Tentativa {attempt}/{max_attempts} falhou: "
                    f"{func.__name__} retornou False"
                )

                logger.info(f"Aguardando {current_delay:.1f}s antes de retry...")
                time.sleep(current_delay)
                current_delay *= backoff

            return False

        return wrapper
    return decorator


def retry_with_callback(
    max_attempts: int = 3,
    delay: float = 2.0,
    before_retry: Optional[Callable] = None,
    after_retry: Optional[Callable] = None
):
    """
    Decorator para retry com callbacks customizados.

    Args:
        max_attempts: Número máximo de tentativas
        delay: Delay entre tentativas
        before_retry: Callback executado antes de cada retry
        after_retry: Callback executado após retry (sucesso ou falha)

    Example:
        >>> def refresh_page():
        ...     driver.refresh()
        ...
        >>> @retry_with_callback(before_retry=refresh_page)
        ... def extrair_dados():
        ...     return scraper.extract()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    # Executar callback antes do retry
                    if attempt > 1 and before_retry:
                        logger.info(f"Executando before_retry (tentativa {attempt})...")
                        before_retry()

                    result = func(*args, **kwargs)

                    # Sucesso - executar callback
                    if after_retry:
                        after_retry(success=True, attempt=attempt)

                    return result

                except Exception as e:
                    if attempt == max_attempts:
                        # Última tentativa - executar callback e re-raise
                        if after_retry:
                            after_retry(success=False, attempt=attempt, error=e)
                        raise

                    logger.warning(
                        f"Tentativa {attempt}/{max_attempts} falhou: {e}"
                    )
                    time.sleep(delay)

        return wrapper
    return decorator


class RetryContext:
    """
    Context manager para operações com retry.

    Example:
        >>> with RetryContext(max_attempts=3) as ctx:
        ...     for attempt in ctx:
        ...         if elemento.click():
        ...             break
    """

    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 2.0,
        backoff: float = 1.5
    ):
        """
        Inicializa context de retry.

        Args:
            max_attempts: Número máximo de tentativas
            delay: Delay inicial
            backoff: Multiplicador de backoff
        """
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff = backoff
        self.current_attempt = 0
        self.current_delay = delay

    def __enter__(self):
        """Entra no context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sai do context."""
        return False  # Não suprimir exceções

    def __iter__(self):
        """Itera sobre tentativas."""
        return self

    def __next__(self):
        """Próxima tentativa."""
        self.current_attempt += 1

        if self.current_attempt > self.max_attempts:
            raise StopIteration

        if self.current_attempt > 1:
            logger.info(
                f"Retry {self.current_attempt}/{self.max_attempts} "
                f"(aguardando {self.current_delay:.1f}s)"
            )
            time.sleep(self.current_delay)
            self.current_delay *= self.backoff

        return self.current_attempt


def execute_with_retry(
    func: Callable,
    max_attempts: int = 3,
    delay: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = RETRYABLE_EXCEPTIONS
):
    """
    Executa função com retry (versão funcional, não decorator).

    Args:
        func: Função a executar
        max_attempts: Número máximo de tentativas
        delay: Delay entre tentativas
        exceptions: Exceções que acionam retry

    Returns:
        Resultado da função

    Example:
        >>> resultado = execute_with_retry(
        ...     lambda: elemento.click(),
        ...     max_attempts=3
        ... )
    """
    current_delay = delay

    for attempt in range(1, max_attempts + 1):
        try:
            return func()

        except exceptions as e:
            if attempt == max_attempts:
                raise

            logger.warning(f"Tentativa {attempt}/{max_attempts} falhou: {e}")
            time.sleep(current_delay)
            current_delay *= 1.5

    raise RuntimeError("execute_with_retry: não deveria chegar aqui")


# Exemplo de uso
if __name__ == '__main__':
    # Teste dos decoradores
    import random

    @retry_on_exception(max_attempts=3, delay=1)
    def funcao_que_pode_falhar():
        """Função de teste que falha aleatoriamente."""
        if random.random() < 0.7:
            raise TimeoutException("Timeout aleatório")
        return "Sucesso!"

    @retry_on_false(max_attempts=3, delay=1)
    def funcao_que_retorna_false():
        """Função de teste que retorna False aleatoriamente."""
        return random.random() > 0.7

    # Testar
    try:
        resultado1 = funcao_que_pode_falhar()
        print(f"Resultado 1: {resultado1}")
    except Exception as e:
        print(f"Falhou após retries: {e}")

    resultado2 = funcao_que_retorna_false()
    print(f"Resultado 2: {resultado2}")

    # Testar context manager
    with RetryContext(max_attempts=3, delay=1) as ctx:
        for attempt in ctx:
            print(f"Tentativa {attempt}")
            if random.random() > 0.7:
                print("Sucesso!")
                break
