"""
Login Page - Page Object

Página de login do portal DET com certificado digital.
"""

import time
from selenium.webdriver.common.by import By
from loguru import logger

from .base_page import BasePage


class LoginPage(BasePage):
    """
    Page Object para página de login do DET.

    Responsável por:
    - Detectar botão de login com certificado
    - Aguardar seleção de certificado
    - Verificar login bem-sucedido
    """

    # URL
    URL = "https://det.sit.trabalho.gov.br/"

    # Seletores (AJUSTAR conforme HTML real!)
    # Estes são exemplos genéricos que precisam ser ajustados
    SELECTORS = {
        # Botões de login
        'btn_login_certificado': (By.CSS_SELECTOR, "button[id*='certificado'], a[href*='certificado']"),
        'btn_login_govbr': (By.CSS_SELECTOR, "button[id*='govbr'], a[href*='govbr']"),

        # Indicadores de login
        'usuario_logado': (By.CSS_SELECTOR, ".usuario-logado, .user-info, #username"),
        'menu_principal': (By.CSS_SELECTOR, "nav.menu-principal, .main-nav"),
        'logo_det': (By.CSS_SELECTOR, ".logo-det, img[alt*='DET']"),

        # Mensagens
        'erro_login': (By.CSS_SELECTOR, ".alert-error, .erro-login"),
        'msg_selecione_certificado': (By.CSS_SELECTOR, ".msg-certificado"),
    }

    def navegar(self):
        """Navega para página de login."""
        logger.info(f"Navegando para: {self.URL}")
        self.driver.get(self.URL)
        self.wait_for_page_load()
        time.sleep(2)  # Aguardar carregamento completo

    def clicar_login_certificado(self) -> bool:
        """
        Clica no botão de login com certificado.

        Returns:
            True se clicou com sucesso, False caso contrário
        """
        logger.info("Procurando botão de login com certificado...")

        try:
            # Tentar encontrar botão
            if self.is_element_present(self.SELECTORS['btn_login_certificado'], timeout=5):
                logger.info("Botão de login com certificado encontrado")
                return self.click_element(self.SELECTORS['btn_login_certificado'])
            else:
                logger.warning("Botão de login com certificado não encontrado")
                logger.info("Possível que já esteja na página de seleção de certificado")
                return True

        except Exception as e:
            logger.error(f"Erro ao clicar em login com certificado: {e}")
            self.take_screenshot("erro_login_certificado")
            return False

    def aguardar_selecao_certificado(self, timeout: int = 20) -> bool:
        """
        Aguarda seleção de certificado (popup do Windows ou browser).

        Args:
            timeout: Tempo máximo de espera

        Returns:
            True se completado, False se timeout

        Note:
            O popup de certificado é elemento nativo do Windows/Browser,
            não acessível via Selenium. Esta função apenas aguarda.
        """
        logger.info(f"Aguardando seleção de certificado ({timeout}s)...")
        logger.info("Certificado deve ser selecionado automaticamente (via Registry)")

        time.sleep(timeout)

        logger.info("Período de espera concluído")
        return True

    def verificar_login_sucesso(self) -> bool:
        """
        Verifica se login foi bem-sucedido.

        Verifica múltiplos indicadores:
        1. Elemento de usuário logado
        2. Menu principal
        3. URL mudou
        4. Não há mensagem de erro

        Returns:
            True se logado, False caso contrário
        """
        logger.info("Verificando se login foi bem-sucedido...")

        # Verificar se há erro
        if self.is_element_present(self.SELECTORS['erro_login'], timeout=3):
            erro_msg = self.get_text(self.SELECTORS['erro_login'])
            logger.error(f"Erro de login detectado: {erro_msg}")
            self.take_screenshot("erro_login")
            return False

        # Verificar indicadores de sucesso
        indicadores_sucesso = [
            ('usuario_logado', "Usuário logado"),
            ('menu_principal', "Menu principal"),
        ]

        for key, descricao in indicadores_sucesso:
            if self.is_element_present(self.SELECTORS[key], timeout=5):
                logger.success(f"✓ {descricao} detectado")
                return True

        # Verificar URL
        url_atual = self.get_current_url()
        if "login" not in url_atual.lower() and self.URL in url_atual:
            logger.success("✓ URL indica login bem-sucedido")
            return True

        logger.warning("Não foi possível confirmar login")
        self.take_screenshot("login_incerto")
        return False

    def realizar_login(self) -> bool:
        """
        Executa fluxo completo de login.

        Returns:
            True se login bem-sucedido, False caso contrário
        """
        try:
            # 1. Navegar para página
            self.navegar()

            # 2. Clicar em login com certificado (se necessário)
            if not self.clicar_login_certificado():
                return False

            # 3. Aguardar seleção de certificado
            self.aguardar_selecao_certificado()

            # 4. Verificar sucesso
            if self.verificar_login_sucesso():
                logger.success("✓ Login realizado com sucesso!")
                return True
            else:
                logger.error("✗ Login falhou")
                return False

        except Exception as e:
            logger.error(f"Erro durante login: {e}")
            self.take_screenshot("erro_login_exception")
            return False

    def verificar_ja_logado(self) -> bool:
        """
        Verifica se já está logado (sessão ativa).

        Returns:
            True se já logado, False caso contrário
        """
        logger.info("Verificando se já está logado...")

        # Navegar para página inicial
        self.navegar()

        # Verificar indicadores
        if self.verificar_login_sucesso():
            logger.info("✓ Sessão já está ativa")
            return True
        else:
            logger.info("Não está logado")
            return False
