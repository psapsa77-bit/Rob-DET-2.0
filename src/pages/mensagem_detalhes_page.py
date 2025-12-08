"""
Mensagem Detalhes Page - Page Object

Página de detalhes de uma mensagem do DET.
"""

import time
from typing import List, Dict, Any, Optional
from selenium.webdriver.common.by import By
from loguru import logger

from .base_page import BasePage


class MensagemDetalhesPage(BasePage):
    """
    Page Object para página de detalhes de mensagem.

    Responsável por:
    - Extrair dados completos da mensagem
    - Identificar anexos
    - Fazer download de anexos (se necessário)
    - Voltar para lista
    """

    # Seletores (AJUSTAR conforme HTML real!)
    SELECTORS = {
        # Informações principais
        'titulo_mensagem': (By.CSS_SELECTOR, "h1.titulo, .mensagem-titulo, h2"),
        'data_envio': (By.CSS_SELECTOR, ".data-envio, .data-recebimento"),
        'remetente': (By.CSS_SELECTOR, ".remetente, .de"),
        'destinatario': (By.CSS_SELECTOR, ".destinatario, .para"),
        'assunto': (By.CSS_SELECTOR, ".assunto, .subject"),
        'numero_processo': (By.CSS_SELECTOR, ".numero-processo, .processo"),

        # Conteúdo
        'conteudo_mensagem': (By.CSS_SELECTOR, ".conteudo-mensagem, .mensagem-corpo, .message-body"),
        'detalhes_adicionais': (By.CSS_SELECTOR, ".detalhes, .informacoes-adicionais"),

        # Prazo
        'prazo_resposta': (By.CSS_SELECTOR, ".prazo-resposta, .prazo, .deadline"),
        'dias_restantes': (By.CSS_SELECTOR, ".dias-restantes, .days-left"),
        'alerta_prazo_vencido': (By.CSS_SELECTOR, ".prazo-vencido, .overdue"),

        # Anexos
        'secao_anexos': (By.CSS_SELECTOR, ".anexos, .attachments, #secao-anexos"),
        'lista_anexos': (By.CSS_SELECTOR, ".lista-anexos ul, .attachments-list"),
        'item_anexo': (By.CSS_SELECTOR, ".anexo-item, .attachment-item, li.anexo"),
        'link_download_anexo': (By.CSS_SELECTOR, "a.download, a[href*='download']"),
        'nome_anexo': (By.CSS_SELECTOR, ".nome-arquivo, .filename"),
        'tamanho_anexo': (By.CSS_SELECTOR, ".tamanho-arquivo, .filesize"),

        # Ações
        'btn_voltar': (By.CSS_SELECTOR, ".voltar, .back, button[onclick*='voltar']"),
        'btn_responder': (By.CSS_SELECTOR, ".responder, .reply"),
        'btn_imprimir': (By.CSS_SELECTOR, ".imprimir, .print"),
        'btn_marcar_lida': (By.CSS_SELECTOR, ".marcar-lida, .mark-read"),

        # Status
        'badge_urgente': (By.CSS_SELECTOR, ".badge-urgente, .urgent"),
        'badge_tipo': (By.CSS_SELECTOR, ".badge-tipo, .message-type"),
        'status_leitura': (By.CSS_SELECTOR, ".status-leitura, .read-status"),
    }

    def aguardar_carregamento(self, timeout: int = 15):
        """
        Aguarda página de detalhes carregar.

        Args:
            timeout: Timeout em segundos
        """
        logger.info("Aguardando detalhes da mensagem carregar...")

        # Aguardar título ou conteúdo aparecer
        titulo_presente = self.is_element_present(self.SELECTORS['titulo_mensagem'], timeout=timeout)
        conteudo_presente = self.is_element_present(self.SELECTORS['conteudo_mensagem'], timeout=timeout)

        if titulo_presente or conteudo_presente:
            logger.success("✓ Detalhes da mensagem carregados")
        else:
            logger.warning("Não foi possível confirmar carregamento dos detalhes")
            self.take_screenshot("detalhes_nao_carregados")

    def extrair_detalhes_completos(self) -> Dict[str, Any]:
        """
        Extrai todos os detalhes da mensagem.

        Returns:
            Dicionário com dados completos da mensagem
        """
        logger.info("Extraindo detalhes completos da mensagem...")

        detalhes = {
            'titulo': '',
            'data_envio': '',
            'remetente': '',
            'destinatario': '',
            'assunto': '',
            'numero_processo': '',
            'conteudo': '',
            'prazo_resposta': '',
            'dias_restantes': '',
            'prazo_vencido': False,
            'urgente': False,
            'tipo': '',
            'possui_anexo': False,
            'anexos': [],
            'status_leitura': '',
            'url': self.get_current_url()
        }

        try:
            # Aguardar carregamento
            self.aguardar_carregamento()

            # Extrair campos principais
            detalhes['titulo'] = self.get_text(self.SELECTORS['titulo_mensagem']) or ''
            detalhes['data_envio'] = self.get_text(self.SELECTORS['data_envio']) or ''
            detalhes['remetente'] = self.get_text(self.SELECTORS['remetente']) or ''
            detalhes['destinatario'] = self.get_text(self.SELECTORS['destinatario']) or ''
            detalhes['assunto'] = self.get_text(self.SELECTORS['assunto']) or detalhes['titulo']
            detalhes['numero_processo'] = self.get_text(self.SELECTORS['numero_processo']) or ''

            # Conteúdo
            detalhes['conteudo'] = self.get_text(self.SELECTORS['conteudo_mensagem']) or ''

            # Prazo
            detalhes['prazo_resposta'] = self.get_text(self.SELECTORS['prazo_resposta']) or ''
            detalhes['dias_restantes'] = self.get_text(self.SELECTORS['dias_restantes']) or ''
            detalhes['prazo_vencido'] = self.is_element_present(self.SELECTORS['alerta_prazo_vencido'], timeout=2)

            # Status
            detalhes['urgente'] = self.is_element_present(self.SELECTORS['badge_urgente'], timeout=2)
            detalhes['tipo'] = self.get_text(self.SELECTORS['badge_tipo']) or ''
            detalhes['status_leitura'] = self.get_text(self.SELECTORS['status_leitura']) or ''

            # Anexos
            if self.is_element_present(self.SELECTORS['secao_anexos'], timeout=3):
                detalhes['possui_anexo'] = True
                detalhes['anexos'] = self.extrair_anexos()

            logger.success("✓ Detalhes extraídos com sucesso")
            logger.info(f"Assunto: {detalhes['assunto'][:60]}")

        except Exception as e:
            logger.error(f"Erro ao extrair detalhes: {e}")
            self.take_screenshot("erro_extrair_detalhes")

        return detalhes

    def extrair_anexos(self) -> List[Dict[str, str]]:
        """
        Extrai informações dos anexos.

        Returns:
            Lista de anexos com nome, tamanho e link
        """
        logger.info("Extraindo anexos...")

        anexos = []

        try:
            # Buscar itens de anexo
            itens_anexo = self.find_elements(self.SELECTORS['item_anexo'], timeout=5)

            if not itens_anexo:
                logger.info("Nenhum anexo encontrado")
                return anexos

            logger.info(f"Encontrados {len(itens_anexo)} anexo(s)")

            # Processar cada anexo
            for idx, item in enumerate(itens_anexo, 1):
                try:
                    # Nome do arquivo
                    nome = ""
                    try:
                        nome_element = item.find_element(*self.SELECTORS['nome_anexo'])
                        nome = nome_element.text.strip()
                    except:
                        nome = f"anexo_{idx}"

                    # Tamanho
                    tamanho = ""
                    try:
                        tamanho_element = item.find_element(*self.SELECTORS['tamanho_anexo'])
                        tamanho = tamanho_element.text.strip()
                    except:
                        pass

                    # Link de download
                    link_download = ""
                    try:
                        link_element = item.find_element(*self.SELECTORS['link_download_anexo'])
                        link_download = link_element.get_attribute('href')
                    except:
                        pass

                    anexo = {
                        'nome': nome,
                        'tamanho': tamanho,
                        'link_download': link_download,
                        'index': idx
                    }

                    anexos.append(anexo)
                    logger.info(f"  • {nome} ({tamanho})")

                except Exception as e:
                    logger.warning(f"Erro ao processar anexo {idx}: {e}")
                    continue

            logger.success(f"✓ Extraídos {len(anexos)} anexo(s)")

        except Exception as e:
            logger.error(f"Erro ao extrair anexos: {e}")

        return anexos

    def download_anexo(self, index: int) -> bool:
        """
        Faz download de um anexo específico.

        Args:
            index: Índice do anexo (1-based)

        Returns:
            True se download iniciado, False caso contrário

        Note:
            O download será feito pelo navegador para o diretório configurado.
        """
        logger.info(f"Iniciando download do anexo {index}...")

        try:
            # Buscar itens de anexo
            itens_anexo = self.find_elements(self.SELECTORS['item_anexo'])

            if index < 1 or index > len(itens_anexo):
                logger.error(f"Índice de anexo inválido: {index}")
                return False

            # Obter item (index é 1-based)
            item = itens_anexo[index - 1]

            # Buscar e clicar no link de download
            link_download = item.find_element(*self.SELECTORS['link_download_anexo'])
            link_download.click()

            logger.success(f"✓ Download do anexo {index} iniciado")
            time.sleep(2)  # Aguardar início do download

            return True

        except Exception as e:
            logger.error(f"Erro ao fazer download do anexo: {e}")
            self.take_screenshot(f"erro_download_anexo_{index}")
            return False

    def download_todos_anexos(self) -> int:
        """
        Faz download de todos os anexos.

        Returns:
            Número de anexos baixados com sucesso
        """
        logger.info("Baixando todos os anexos...")

        anexos = self.extrair_anexos()
        sucesso = 0

        for anexo in anexos:
            if self.download_anexo(anexo['index']):
                sucesso += 1
                time.sleep(2)  # Delay entre downloads

        logger.info(f"Downloads concluídos: {sucesso}/{len(anexos)}")
        return sucesso

    def voltar_para_lista(self) -> bool:
        """
        Volta para a lista de mensagens.

        Returns:
            True se voltou, False caso contrário
        """
        logger.info("Voltando para lista de mensagens...")

        try:
            # Tentar botão voltar
            if self.is_element_present(self.SELECTORS['btn_voltar'], timeout=5):
                if self.click_element(self.SELECTORS['btn_voltar']):
                    time.sleep(2)
                    logger.success("✓ Voltou para lista")
                    return True

            # Fallback: usar navegação do browser
            logger.info("Botão voltar não encontrado, usando navegação do browser")
            self.driver.back()
            time.sleep(2)
            logger.info("Navegação back executada")
            return True

        except Exception as e:
            logger.error(f"Erro ao voltar para lista: {e}")
            return False

    def marcar_como_lida(self) -> bool:
        """
        Marca mensagem como lida (se houver botão).

        Returns:
            True se marcou, False caso contrário
        """
        logger.info("Marcando mensagem como lida...")

        if self.is_element_present(self.SELECTORS['btn_marcar_lida'], timeout=3):
            return self.click_element(self.SELECTORS['btn_marcar_lida'])

        logger.info("Botão marcar como lida não disponível")
        return False
