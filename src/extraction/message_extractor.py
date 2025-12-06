"""
Extrator de Mensagens - Rob-DET 2.0

Extrai mensagens da Caixa Postal do DET:
- Scraping de tabela de mensagens
- Identificação de mensagens novas
- Classificação por tipo/urgência
- Exportação de dados
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from loguru import logger


class Message:
    """Representa uma mensagem do DET."""

    def __init__(self, data: Dict[str, Any]):
        """
        Inicializa mensagem.

        Args:
            data: Dicionário com dados da mensagem
        """
        self.id = data.get('id', '')
        self.data_envio = data.get('data_envio', '')
        self.remetente = data.get('remetente', '')
        self.assunto = data.get('assunto', '')
        self.tipo = data.get('tipo', '')
        self.status = data.get('status', 'não lida')  # lida, não lida
        self.urgente = data.get('urgente', False)

    def is_new(self) -> bool:
        """Verifica se mensagem é nova (não lida)."""
        return self.status == 'não lida'

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            'id': self.id,
            'data_envio': self.data_envio,
            'remetente': self.remetente,
            'assunto': self.assunto,
            'tipo': self.tipo,
            'status': self.status,
            'urgente': self.urgente
        }

    def __repr__(self) -> str:
        urgente_flag = "🔴 " if self.urgente else ""
        nova_flag = "📩 " if self.is_new() else "📧 "
        return f"{nova_flag}{urgente_flag}{self.assunto} ({self.data_envio})"


class MessageExtractor:
    """Extrator de mensagens da Caixa Postal do DET."""

    def __init__(self, driver: WebDriver):
        """
        Inicializa extrator.

        Args:
            driver: WebDriver do Selenium
        """
        self.driver = driver

    def extract_messages(self, only_new: bool = False) -> List[Message]:
        """
        Extrai mensagens da página atual.

        Args:
            only_new: Se True, retorna apenas mensagens não lidas

        Returns:
            Lista de mensagens extraídas

        Note:
            Seletores precisam ser ajustados conforme estrutura real do portal
        """
        try:
            logger.info("Extraindo mensagens da Caixa Postal...")

            # Obter HTML da página
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # TODO: Ajustar seletores conforme estrutura real
            # Exemplo genérico de extração de tabela
            messages = []

            # Buscar tabela de mensagens (ajustar seletor)
            table = soup.find('table', {'class': 'mensagens'})

            if not table:
                logger.warning("Tabela de mensagens não encontrada")
                return []

            # Iterar sobre linhas
            rows = table.find_all('tr')[1:]  # Pular cabeçalho

            for row in rows:
                cols = row.find_all('td')

                if len(cols) < 4:
                    continue

                # Extrair dados (ajustar índices conforme tabela real)
                message_data = {
                    'id': cols[0].text.strip(),
                    'data_envio': cols[1].text.strip(),
                    'remetente': cols[2].text.strip(),
                    'assunto': cols[3].text.strip(),
                    'tipo': self._classify_message_type(cols[3].text.strip()),
                    'status': self._get_message_status(row),
                    'urgente': self._is_urgent(cols[3].text.strip())
                }

                message = Message(message_data)

                # Filtrar se necessário
                if only_new and not message.is_new():
                    continue

                messages.append(message)

            logger.success(f"✓ Extraídas {len(messages)} mensagens")

            if only_new:
                new_count = sum(1 for m in messages if m.is_new())
                logger.info(f"Mensagens novas: {new_count}")

            return messages

        except Exception as e:
            logger.error(f"Erro ao extrair mensagens: {e}")
            return []

    def _classify_message_type(self, subject: str) -> str:
        """
        Classifica tipo de mensagem baseado no assunto.

        Args:
            subject: Assunto da mensagem

        Returns:
            Tipo da mensagem
        """
        subject_lower = subject.lower()

        if 'autuação' in subject_lower or 'auto de infração' in subject_lower:
            return 'Autuação'
        elif 'intimação' in subject_lower:
            return 'Intimação'
        elif 'notificação' in subject_lower:
            return 'Notificação'
        elif 'comunicado' in subject_lower:
            return 'Comunicado'
        else:
            return 'Outro'

    def _is_urgent(self, subject: str) -> bool:
        """
        Identifica se mensagem é urgente.

        Args:
            subject: Assunto da mensagem

        Returns:
            True se urgente, False caso contrário
        """
        urgent_keywords = [
            'urgente',
            'prazo',
            'imediato',
            'autuação',
            'intimação'
        ]

        subject_lower = subject.lower()
        return any(keyword in subject_lower for keyword in urgent_keywords)

    def _get_message_status(self, row_element: Any) -> str:
        """
        Determina status da mensagem (lida/não lida).

        Args:
            row_element: Elemento HTML da linha

        Returns:
            Status da mensagem
        """
        # Exemplo: verificar se tem classe 'nao-lida' ou 'unread'
        classes = row_element.get('class', [])

        if 'nao-lida' in classes or 'unread' in classes:
            return 'não lida'
        else:
            return 'lida'

    def count_new_messages(self) -> int:
        """
        Conta apenas mensagens novas.

        Returns:
            Número de mensagens não lidas
        """
        messages = self.extract_messages()
        return sum(1 for m in messages if m.is_new())

    def export_to_dict_list(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """
        Exporta mensagens para lista de dicionários.

        Args:
            messages: Lista de mensagens

        Returns:
            Lista de dicionários
        """
        return [m.to_dict() for m in messages]


# Exemplo de uso
if __name__ == '__main__':
    # Teste de classificação
    test_messages = [
        {'id': '1', 'data_envio': '01/12/2025', 'remetente': 'SIT', 'assunto': 'Notificação de Autuação'},
        {'id': '2', 'data_envio': '02/12/2025', 'remetente': 'SIT', 'assunto': 'Intimação Urgente'},
        {'id': '3', 'data_envio': '03/12/2025', 'remetente': 'SIT', 'assunto': 'Comunicado geral'},
    ]

    for msg_data in test_messages:
        msg = Message(msg_data)
        print(msg)
        print(f"  Tipo: {msg.tipo}")
        print(f"  Urgente: {msg.urgente}")
        print()
