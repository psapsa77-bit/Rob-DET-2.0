"""
Base Page - Page Object Model

Classe base para todos os Page Objects com funcionalidades comuns:
- Esperas explícitas
- Screenshots
- Logging
- Retry logic
"""

import time
from typing import Optional, Tuple
from pathlib import Path
from datetime import datetime

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException
)
from loguru import logger


class BasePage:
    """
    Classe base para Page Objects.

    Fornece funcionalidades comuns para todas as páginas:
    - Esperas explícitas
    - Localização de elementos
    - Screenshots
    - Retry logic
    """

    def __init__(self, driver: WebDriver, timeout: int = 30):
        """
        Inicializa page object.

        Args:
            driver: WebDriver do Selenium
            timeout: Timeout padrão em segundos
        """
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def find_element(
        self,
        locator: Tuple[By, str],
        timeout: Optional[int] = None
    ) -> WebElement:
        """
        Encontra elemento com espera explícita.

        Args:
            locator: Tupla (By, selector)
            timeout: Timeout customizado

        Returns:
            WebElement encontrado

        Raises:
            TimeoutException: Se elemento não encontrado
        """
        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time)

        try:
            element = wait.until(
                EC.presence_of_element_located(locator)
            )
            logger.debug(f"Elemento encontrado: {locator}")
            return element

        except TimeoutException:
            logger.error(f"Timeout ao buscar elemento: {locator}")
            self.take_screenshot(f"timeout_{locator[1][:30]}")
            raise

    def find_elements(
        self,
        locator: Tuple[By, str],
        timeout: Optional[int] = None
    ) -> list:
        """
        Encontra múltiplos elementos.

        Args:
            locator: Tupla (By, selector)
            timeout: Timeout customizado

        Returns:
            Lista de WebElements
        """
        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time)

        try:
            elements = wait.until(
                EC.presence_of_all_elements_located(locator)
            )
            logger.debug(f"Encontrados {len(elements)} elementos: {locator}")
            return elements

        except TimeoutException:
            logger.warning(f"Nenhum elemento encontrado: {locator}")
            return []

    def wait_for_clickable(
        self,
        locator: Tuple[By, str],
        timeout: Optional[int] = None
    ) -> WebElement:
        """
        Aguarda elemento estar clicável.

        Args:
            locator: Tupla (By, selector)
            timeout: Timeout customizado

        Returns:
            WebElement clicável

        Raises:
            TimeoutException: Se elemento não ficar clicável
        """
        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time)

        try:
            element = wait.until(
                EC.element_to_be_clickable(locator)
            )
            logger.debug(f"Elemento clicável: {locator}")
            return element

        except TimeoutException:
            logger.error(f"Timeout aguardando elemento clicável: {locator}")
            self.take_screenshot(f"not_clickable_{locator[1][:30]}")
            raise

    def click_element(
        self,
        locator: Tuple[By, str],
        retry: int = 3
    ) -> bool:
        """
        Clica em elemento com retry automático.

        Args:
            locator: Tupla (By, selector)
            retry: Número de tentativas

        Returns:
            True se clicou com sucesso, False caso contrário
        """
        for attempt in range(retry):
            try:
                element = self.wait_for_clickable(locator)
                element.click()
                logger.debug(f"Clique realizado: {locator}")
                return True

            except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                logger.warning(f"Tentativa {attempt + 1}/{retry} falhou: {e}")
                time.sleep(1)

                if attempt == retry - 1:
                    logger.error(f"Falha ao clicar após {retry} tentativas")
                    self.take_screenshot(f"click_failed_{locator[1][:30]}")
                    return False

        return False

    def send_keys(
        self,
        locator: Tuple[By, str],
        text: str,
        clear_first: bool = True
    ) -> bool:
        """
        Envia texto para elemento.

        Args:
            locator: Tupla (By, selector)
            text: Texto a enviar
            clear_first: Se True, limpa campo antes

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            element = self.find_element(locator)

            if clear_first:
                element.clear()

            element.send_keys(text)
            logger.debug(f"Texto enviado para {locator}: {text}")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar texto: {e}")
            self.take_screenshot(f"send_keys_failed_{locator[1][:30]}")
            return False

    def get_text(
        self,
        locator: Tuple[By, str],
        timeout: Optional[int] = None
    ) -> Optional[str]:
        """
        Obtém texto de elemento.

        Args:
            locator: Tupla (By, selector)
            timeout: Timeout customizado

        Returns:
            Texto do elemento ou None
        """
        try:
            element = self.find_element(locator, timeout=timeout)
            text = element.text.strip()
            logger.debug(f"Texto obtido de {locator}: {text[:50]}")
            return text

        except Exception as e:
            logger.warning(f"Erro ao obter texto: {e}")
            return None

    def get_attribute(
        self,
        locator: Tuple[By, str],
        attribute: str
    ) -> Optional[str]:
        """
        Obtém atributo de elemento.

        Args:
            locator: Tupla (By, selector)
            attribute: Nome do atributo

        Returns:
            Valor do atributo ou None
        """
        try:
            element = self.find_element(locator)
            value = element.get_attribute(attribute)
            logger.debug(f"Atributo {attribute} de {locator}: {value}")
            return value

        except Exception as e:
            logger.warning(f"Erro ao obter atributo: {e}")
            return None

    def is_element_present(
        self,
        locator: Tuple[By, str],
        timeout: int = 5
    ) -> bool:
        """
        Verifica se elemento está presente.

        Args:
            locator: Tupla (By, selector)
            timeout: Timeout reduzido

        Returns:
            True se presente, False caso contrário
        """
        try:
            self.find_element(locator, timeout=timeout)
            return True
        except TimeoutException:
            return False

    def wait_for_page_load(self, timeout: Optional[int] = None):
        """
        Aguarda página carregar completamente.

        Args:
            timeout: Timeout customizado
        """
        wait_time = timeout or self.timeout

        try:
            WebDriverWait(self.driver, wait_time).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            logger.debug("Página carregada completamente")

        except TimeoutException:
            logger.warning("Timeout aguardando carregamento da página")

    def scroll_to_element(self, locator: Tuple[By, str]):
        """
        Rola página até elemento.

        Args:
            locator: Tupla (By, selector)
        """
        try:
            element = self.find_element(locator)
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                element
            )
            time.sleep(0.5)  # Aguardar scroll
            logger.debug(f"Rolado até elemento: {locator}")

        except Exception as e:
            logger.warning(f"Erro ao rolar até elemento: {e}")

    def take_screenshot(self, name: str = "screenshot") -> Optional[str]:
        """
        Captura screenshot da página.

        Args:
            name: Nome base do arquivo

        Returns:
            Caminho do arquivo ou None
        """
        try:
            # Criar diretório
            screenshot_dir = Path("./logs/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)

            # Nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = screenshot_dir / filename

            # Capturar
            self.driver.save_screenshot(str(filepath))
            logger.info(f"Screenshot salvo: {filepath}")

            return str(filepath)

        except Exception as e:
            logger.error(f"Erro ao salvar screenshot: {e}")
            return None

    def get_current_url(self) -> str:
        """Retorna URL atual."""
        return self.driver.current_url

    def get_page_title(self) -> str:
        """Retorna título da página."""
        return self.driver.title

    def refresh_page(self):
        """Atualiza a página."""
        logger.info("Atualizando página...")
        self.driver.refresh()
        self.wait_for_page_load()

    def execute_script(self, script: str, *args):
        """
        Executa JavaScript.

        Args:
            script: Script JavaScript
            *args: Argumentos para o script

        Returns:
            Resultado do script
        """
        return self.driver.execute_script(script, *args)
