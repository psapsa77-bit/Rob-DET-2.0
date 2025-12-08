"""
Page Objects - Rob-DET 2.0

Implementação do Page Object Model para o portal DET.
"""

from .base_page import BasePage
from .login_page import LoginPage
from .home_page import HomePage
from .caixa_postal_page import CaixaPostalPage
from .mensagem_detalhes_page import MensagemDetalhesPage

__all__ = [
    'BasePage',
    'LoginPage',
    'HomePage',
    'CaixaPostalPage',
    'MensagemDetalhesPage'
]
