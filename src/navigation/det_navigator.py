"""
Navegador DET - Rob-DET 2.0

Gerencia a navegação no portal DET usando Selenium:
- Inicialização do WebDriver com configurações anti-detecção
- Login com certificado digital
- Seleção de CNPJ via procuração
- Navegação na Caixa Postal
- Tratamento de timeouts e erros
"""

import time
import random
from typing import Optional, List, Dict, Any
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService

from loguru import logger


class DETNavigator:
    """Navegador para o portal DET."""

    # URLs
    BASE_URL = "https://det.sit.trabalho.gov.br/"
    CAIXA_POSTAL_URL = "https://det.sit.trabalho.gov.br/correspondencia/caixaPostal"

    def __init__(
        self,
        browser: str = 'chrome',
        headless: bool = False,
        timeout: int = 30,
        action_delay: float = 1.5
    ):
        """
        Inicializa o navegador.

        Args:
            browser: Navegador (chrome ou edge)
            headless: Modo headless (sem interface gráfica)
            timeout: Timeout padrão em segundos
            action_delay: Delay entre ações (humanizar)
        """
        self.browser = browser
        self.headless = headless
        self.timeout = timeout
        self.action_delay = action_delay

        self.driver: Optional[webdriver.Chrome | webdriver.Edge] = None
        self.wait: Optional[WebDriverWait] = None

        logger.info(f"Navegador: {browser.upper()} | Headless: {headless}")

    def _get_chrome_options(self) -> ChromeOptions:
        """
        Cria opções do Chrome com configurações anti-detecção.

        Returns:
            ChromeOptions configurado
        """
        options = ChromeOptions()

        # Configurações anti-detecção
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Configurações gerais
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')

        # Desabilitar notificações
        prefs = {
            "profile.default_content_setting_values.notifications": 2
        }
        options.add_experimental_option("prefs", prefs)

        # Modo headless
        if self.headless:
            options.add_argument('--headless=new')
            logger.info("Modo headless ativado")

        return options

    def _get_edge_options(self) -> EdgeOptions:
        """
        Cria opções do Edge.

        Returns:
            EdgeOptions configurado
        """
        options = EdgeOptions()

        # Configurações similares ao Chrome
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')

        if self.headless:
            options.add_argument('--headless=new')
            logger.info("Modo headless ativado")

        return options

    def start(self) -> None:
        """
        Inicia o WebDriver.

        Raises:
            RuntimeError: Se não conseguir iniciar o navegador
        """
        try:
            logger.info("Iniciando WebDriver...")

            if self.browser == 'chrome':
                options = self._get_chrome_options()
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)

            elif self.browser == 'edge':
                options = self._get_edge_options()
                service = EdgeService(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service, options=options)

            else:
                raise ValueError(f"Navegador não suportado: {self.browser}")

            # Configurar wait
            self.wait = WebDriverWait(self.driver, self.timeout)

            # Remover propriedade webdriver (anti-detecção)
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })

            logger.success("WebDriver iniciado com sucesso")

        except Exception as e:
            logger.error(f"Falha ao iniciar WebDriver: {e}")
            raise RuntimeError(f"Não foi possível iniciar o navegador: {e}")

    def stop(self) -> None:
        """Fecha o navegador."""
        if self.driver:
            logger.info("Fechando navegador...")
            self.driver.quit()
            self.driver = None
            self.wait = None
            logger.info("Navegador fechado")

    def navigate_to(self, url: str) -> None:
        """
        Navega para uma URL.

        Args:
            url: URL de destino
        """
        if not self.driver:
            raise RuntimeError("WebDriver não iniciado. Chame start() primeiro.")

        logger.info(f"Navegando para: {url}")
        self.driver.get(url)
        self._random_delay()

    def _random_delay(self, min_delay: Optional[float] = None, max_delay: Optional[float] = None) -> None:
        """
        Adiciona delay aleatório para humanizar a automação.

        Args:
            min_delay: Delay mínimo (usa action_delay se None)
            max_delay: Delay máximo (usa action_delay * 2 se None)
        """
        if min_delay is None:
            min_delay = self.action_delay * 0.5

        if max_delay is None:
            max_delay = self.action_delay * 1.5

        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    def wait_for_element(
        self,
        by: By,
        value: str,
        timeout: Optional[int] = None
    ) -> Any:
        """
        Aguarda elemento estar presente.

        Args:
            by: Método de busca (By.ID, By.XPATH, etc.)
            value: Valor do seletor
            timeout: Timeout customizado (usa padrão se None)

        Returns:
            Elemento encontrado

        Raises:
            TimeoutException: Se elemento não for encontrado
        """
        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time)

        try:
            element = wait.until(EC.presence_of_element_located((by, value)))
            logger.debug(f"Elemento encontrado: {value}")
            return element
        except TimeoutException:
            logger.error(f"Timeout ao aguardar elemento: {value}")
            raise

    def wait_for_clickable(
        self,
        by: By,
        value: str,
        timeout: Optional[int] = None
    ) -> Any:
        """
        Aguarda elemento estar clicável.

        Args:
            by: Método de busca
            value: Valor do seletor
            timeout: Timeout customizado

        Returns:
            Elemento clicável

        Raises:
            TimeoutException: Se elemento não ficar clicável
        """
        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time)

        try:
            element = wait.until(EC.element_to_be_clickable((by, value)))
            logger.debug(f"Elemento clicável: {value}")
            return element
        except TimeoutException:
            logger.error(f"Timeout ao aguardar elemento clicável: {value}")
            raise

    def login_with_certificate(self, popup_timeout: int = 15) -> bool:
        """
        Realiza login no DET com certificado digital.

        IMPORTANTE: Este método assume que:
        1. Certificado já está configurado via Registry (auto-seleção), OU
        2. PyWinAuto será usado para manipular o popup (implementar separadamente)

        Args:
            popup_timeout: Tempo para aguardar popup de certificado

        Returns:
            True se login bem-sucedido, False caso contrário
        """
        try:
            logger.info("=" * 60)
            logger.info("Iniciando login no DET")
            logger.info("=" * 60)

            # Navegar para a página de login
            self.navigate_to(self.BASE_URL)

            # Aguardar carregamento da página
            logger.info("Aguardando página de login carregar...")
            time.sleep(3)

            # NOTA: Aqui o certificado deve ser selecionado automaticamente
            # Se configurado via Registry, não haverá popup
            # Caso contrário, será necessário PyWinAuto (implementar em módulo separado)

            logger.info(f"Aguardando {popup_timeout}s para processamento do certificado...")
            time.sleep(popup_timeout)

            # Verificar se login foi bem-sucedido
            # Ajustar seletores conforme estrutura real do portal
            try:
                # Exemplo: verificar se URL mudou ou se algum elemento específico apareceu
                current_url = self.driver.current_url
                logger.info(f"URL atual: {current_url}")

                # Se chegou na página principal (não é mais a página de login)
                if "det.sit.trabalho.gov.br" in current_url and current_url != self.BASE_URL:
                    logger.success("✓ Login realizado com sucesso!")
                    return True
                else:
                    logger.warning("Login pode não ter sido bem-sucedido")
                    return False

            except Exception as e:
                logger.error(f"Erro ao verificar login: {e}")
                return False

        except Exception as e:
            logger.error(f"Erro durante login: {e}")
            return False

    def select_cnpj(self, cnpj: str) -> bool:
        """
        Seleciona CNPJ via dropdown de procuração.

        Args:
            cnpj: CNPJ a selecionar (com ou sem formatação)

        Returns:
            True se selecionado com sucesso, False caso contrário

        Note:
            Seletores precisam ser ajustados conforme estrutura real do portal
        """
        try:
            logger.info(f"Selecionando CNPJ: {cnpj}")

            # Remove formatação para comparação
            cnpj_numbers = ''.join(filter(str.isdigit, cnpj))

            # TODO: Ajustar seletores conforme portal real
            # Exemplo genérico:
            dropdown = self.wait_for_clickable(By.ID, "cnpjSelect", timeout=10)
            dropdown.click()
            self._random_delay()

            # Buscar opção correspondente
            # Implementação depende da estrutura real do dropdown
            logger.info(f"CNPJ {cnpj} selecionado (implementação pendente)")

            return True

        except Exception as e:
            logger.error(f"Erro ao selecionar CNPJ: {e}")
            return False

    def navigate_to_mailbox(self) -> bool:
        """
        Navega para a Caixa Postal.

        Returns:
            True se navegou com sucesso, False caso contrário
        """
        try:
            logger.info("Navegando para Caixa Postal...")
            self.navigate_to(self.CAIXA_POSTAL_URL)

            # Aguardar carregamento
            logger.info("Aguardando carregamento da Caixa Postal...")
            time.sleep(3)

            logger.success("✓ Caixa Postal carregada")
            return True

        except Exception as e:
            logger.error(f"Erro ao navegar para Caixa Postal: {e}")
            return False

    def take_screenshot(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Captura screenshot da página atual.

        Args:
            filename: Nome do arquivo (gera automaticamente se None)

        Returns:
            Caminho do arquivo salvo ou None se falha
        """
        if not self.driver:
            logger.error("WebDriver não iniciado")
            return None

        try:
            from datetime import datetime

            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"

            # Criar diretório se não existir
            screenshot_dir = Path("./logs/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)

            filepath = screenshot_dir / filename
            self.driver.save_screenshot(str(filepath))

            logger.info(f"Screenshot salvo: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Erro ao capturar screenshot: {e}")
            return None

    def __enter__(self):
        """Context manager - entrada."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager - saída."""
        self.stop()


# Exemplo de uso
if __name__ == '__main__':
    # Teste básico
    logger.info("Testando DETNavigator...")

    try:
        # Usar como context manager
        with DETNavigator(browser='chrome', headless=False) as navigator:
            # Navegar para DET
            navigator.navigate_to(navigator.BASE_URL)

            # Aguardar um pouco
            time.sleep(5)

            # Capturar screenshot
            navigator.take_screenshot("teste_det.png")

            logger.success("Teste concluído!")

    except Exception as e:
        logger.error(f"Erro no teste: {e}")
