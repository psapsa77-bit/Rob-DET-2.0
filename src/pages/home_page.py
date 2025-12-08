"""
Home Page - Page Object

Página inicial do portal DET após login.
"""

from selenium.webdriver.common.by import By
from loguru import logger

from .base_page import BasePage


class HomePage(BasePage):
    """
    Page Object para página inicial do DET.

    Responsável por:
    - Seleção de empresa (CNPJ via procuração)
    - Navegação para caixa postal
    - Verificação de perfil
    """

    # URL
    URL = "https://det.sit.trabalho.gov.br/home"

    # Seletores (AJUSTAR conforme HTML real!)
    SELECTORS = {
        # Seleção de empresa
        'dropdown_empresa': (By.CSS_SELECTOR, "select#empresa, select[name='empresa'], select.select-empresa"),
        'opcao_empresa': (By.CSS_SELECTOR, "option[value*='{cnpj}']"),
        'btn_confirmar_empresa': (By.CSS_SELECTOR, "button.confirmar-empresa, button[type='submit']"),

        # Navegação
        'menu_caixa_postal': (By.CSS_SELECTOR, "a[href*='caixaPostal'], a[href*='correspondencia']"),
        'link_caixa_postal': (By.XPATH, "//a[contains(text(), 'Caixa Postal') or contains(text(), 'Correspondência')]"),

        # Informações
        'empresa_selecionada': (By.CSS_SELECTOR, ".empresa-atual, .cnpj-selecionado"),
        'nome_usuario': (By.CSS_SELECTOR, ".nome-usuario, .user-name"),

        # Notificações
        'contador_mensagens': (By.CSS_SELECTOR, ".badge-mensagens, .contador-mensagens"),
        'alerta_pendencias': (By.CSS_SELECTOR, ".alert-pendencias"),
    }

    def navegar(self):
        """Navega para página inicial."""
        logger.info(f"Navegando para home: {self.URL}")
        self.driver.get(self.URL)
        self.wait_for_page_load()

    def get_empresa_atual(self) -> str:
        """
        Obtém CNPJ da empresa atualmente selecionada.

        Returns:
            CNPJ da empresa ou string vazia
        """
        try:
            empresa = self.get_text(self.SELECTORS['empresa_selecionada'])
            if empresa:
                logger.info(f"Empresa atual: {empresa}")
                return empresa
            return ""

        except Exception as e:
            logger.warning(f"Não foi possível obter empresa atual: {e}")
            return ""

    def selecionar_empresa(self, cnpj: str) -> bool:
        """
        Seleciona empresa no dropdown de procuração.

        Args:
            cnpj: CNPJ da empresa (com ou sem formatação)

        Returns:
            True se selecionado com sucesso, False caso contrário
        """
        logger.info(f"Selecionando empresa: {cnpj}")

        try:
            # Normalizar CNPJ (apenas números)
            cnpj_numeros = ''.join(filter(str.isdigit, cnpj))

            # Verificar se já está selecionada
            empresa_atual = self.get_empresa_atual()
            if cnpj_numeros in empresa_atual or cnpj in empresa_atual:
                logger.info("✓ Empresa já está selecionada")
                return True

            # Encontrar dropdown
            if not self.is_element_present(self.SELECTORS['dropdown_empresa'], timeout=10):
                logger.warning("Dropdown de empresa não encontrado")
                logger.info("Possível que não há procuração ou apenas uma empresa")
                return True  # Não é erro crítico

            # Clicar no dropdown
            if not self.click_element(self.SELECTORS['dropdown_empresa']):
                return False

            # Construir seletor da opção
            opcao_selector = self.SELECTORS['opcao_empresa'][1].format(cnpj=cnpj_numeros)
            opcao_locator = (By.CSS_SELECTOR, opcao_selector)

            # Tentar também com CNPJ formatado
            if not self.is_element_present(opcao_locator, timeout=3):
                opcao_selector = self.SELECTORS['opcao_empresa'][1].format(cnpj=cnpj)
                opcao_locator = (By.CSS_SELECTOR, opcao_selector)

            # Clicar na opção
            if not self.click_element(opcao_locator):
                logger.error(f"CNPJ {cnpj} não encontrado no dropdown")
                logger.warning("Verifique se você tem procuração para este CNPJ")
                self.take_screenshot(f"cnpj_nao_encontrado_{cnpj_numeros}")
                return False

            # Confirmar seleção (se houver botão)
            if self.is_element_present(self.SELECTORS['btn_confirmar_empresa'], timeout=2):
                self.click_element(self.SELECTORS['btn_confirmar_empresa'])

            logger.success(f"✓ Empresa {cnpj} selecionada")
            return True

        except Exception as e:
            logger.error(f"Erro ao selecionar empresa: {e}")
            self.take_screenshot(f"erro_selecionar_empresa_{cnpj}")
            return False

    def navegar_para_caixa_postal(self) -> bool:
        """
        Navega para a caixa postal.

        Returns:
            True se navegou com sucesso, False caso contrário
        """
        logger.info("Navegando para Caixa Postal...")

        try:
            # Tentar pelo menu
            if self.is_element_present(self.SELECTORS['menu_caixa_postal'], timeout=5):
                logger.info("Menu Caixa Postal encontrado")
                return self.click_element(self.SELECTORS['menu_caixa_postal'])

            # Tentar pelo link (XPath)
            if self.is_element_present(self.SELECTORS['link_caixa_postal'], timeout=5):
                logger.info("Link Caixa Postal encontrado")
                return self.click_element(self.SELECTORS['link_caixa_postal'])

            # Navegação direta (fallback)
            logger.warning("Menu não encontrado, navegando diretamente")
            url_caixa_postal = "https://det.sit.trabalho.gov.br/correspondencia/caixaPostal"
            self.driver.get(url_caixa_postal)
            self.wait_for_page_load()
            return True

        except Exception as e:
            logger.error(f"Erro ao navegar para caixa postal: {e}")
            self.take_screenshot("erro_navegar_caixa_postal")
            return False

    def get_contador_mensagens(self) -> int:
        """
        Obtém número de mensagens não lidas (se disponível).

        Returns:
            Número de mensagens ou 0
        """
        try:
            contador_text = self.get_text(self.SELECTORS['contador_mensagens'], timeout=5)
            if contador_text and contador_text.isdigit():
                contador = int(contador_text)
                logger.info(f"Contador de mensagens: {contador}")
                return contador
            return 0

        except Exception:
            return 0

    def verificar_pendencias(self) -> bool:
        """
        Verifica se há alertas de pendências.

        Returns:
            True se há pendências, False caso contrário
        """
        if self.is_element_present(self.SELECTORS['alerta_pendencias'], timeout=3):
            alerta = self.get_text(self.SELECTORS['alerta_pendencias'])
            logger.warning(f"⚠️ Pendência detectada: {alerta}")
            return True

        return False
