"""
Caixa Postal Page - Page Object

Página de listagem de mensagens do DET.
"""

import time
from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from loguru import logger

from .base_page import BasePage


class CaixaPostalPage(BasePage):
    """
    Page Object para caixa postal do DET.

    Responsável por:
    - Listar mensagens
    - Filtrar mensagens
    - Clicar em mensagem para ver detalhes
    - Paginação
    """

    # URL
    URL = "https://det.sit.trabalho.gov.br/correspondencia/caixaPostal"

    # Seletores (AJUSTAR conforme HTML real!)
    SELECTORS = {
        # Tabela de mensagens
        'tabela_mensagens': (By.CSS_SELECTOR, "table.mensagens, table#tabelaMensagens, .lista-mensagens table"),
        'linha_mensagem': (By.CSS_SELECTOR, "tr.mensagem, tbody tr"),
        'mensagem_item': (By.CSS_SELECTOR, ".mensagem-item, .correspondencia-item"),

        # Campos da mensagem na lista
        'msg_data': (By.CSS_SELECTOR, "td.data, .data-envio, td:nth-child(1)"),
        'msg_remetente': (By.CSS_SELECTOR, "td.remetente, .remetente, td:nth-child(2)"),
        'msg_assunto': (By.CSS_SELECTOR, "td.assunto, .assunto, td:nth-child(3)"),
        'msg_status': (By.CSS_SELECTOR, "td.status, .status, td:nth-child(4)"),
        'msg_link_detalhes': (By.CSS_SELECTOR, "a.ver-detalhes, .link-mensagem, a[href*='detalhes']"),

        # Indicadores
        'icone_nao_lida': (By.CSS_SELECTOR, ".nao-lida, .unread, .badge-new"),
        'icone_anexo': (By.CSS_SELECTOR, ".tem-anexo, .has-attachment, i.fa-paperclip"),
        'icone_urgente': (By.CSS_SELECTOR, ".urgente, .priority-high"),

        # Filtros
        'checkbox_nao_lidas': (By.CSS_SELECTOR, "input[name='apenasNaoLidas'], #checkNaoLidas"),
        'filtro_data_inicio': (By.CSS_SELECTOR, "input[name='dataInicio'], #dataInicio"),
        'filtro_data_fim': (By.CSS_SELECTOR, "input[name='dataFim'], #dataFim"),
        'btn_filtrar': (By.CSS_SELECTOR, "button.filtrar, button[type='submit']"),
        'btn_limpar_filtro': (By.CSS_SELECTOR, "button.limpar-filtro, button.clear-filter"),

        # Paginação
        'btn_proxima_pagina': (By.CSS_SELECTOR, ".proxima, .next, button[aria-label='Próxima']"),
        'btn_pagina_anterior': (By.CSS_SELECTOR, ".anterior, .previous, button[aria-label='Anterior']"),
        'numero_pagina_atual': (By.CSS_SELECTOR, ".pagina-atual, .current-page"),
        'total_paginas': (By.CSS_SELECTOR, ".total-paginas, .total-pages"),

        # Mensagens de status
        'msg_caixa_vazia': (By.CSS_SELECTOR, ".caixa-vazia, .no-messages"),
        'msg_sem_resultados': (By.CSS_SELECTOR, ".sem-resultados, .no-results"),
        'loading': (By.CSS_SELECTOR, ".loading, .spinner, .carregando"),
    }

    def navegar(self):
        """Navega para caixa postal."""
        logger.info(f"Navegando para caixa postal: {self.URL}")
        self.driver.get(self.URL)
        self.wait_for_page_load()
        self.aguardar_carregamento()

    def aguardar_carregamento(self, timeout: int = 15):
        """
        Aguarda caixa postal carregar completamente.

        Args:
            timeout: Timeout em segundos
        """
        logger.info("Aguardando caixa postal carregar...")

        # Aguardar spinner desaparecer
        if self.is_element_present(self.SELECTORS['loading'], timeout=2):
            logger.info("Aguardando carregamento...")
            time.sleep(3)

        # Aguardar tabela aparecer OU mensagem de caixa vazia
        tabela_presente = self.is_element_present(self.SELECTORS['tabela_mensagens'], timeout=timeout)
        caixa_vazia = self.is_element_present(self.SELECTORS['msg_caixa_vazia'], timeout=2)

        if tabela_presente:
            logger.success("✓ Tabela de mensagens carregada")
        elif caixa_vazia:
            logger.info("ℹ️ Caixa postal está vazia")
        else:
            logger.warning("Não foi possível confirmar carregamento")

    def filtrar_apenas_nao_lidas(self) -> bool:
        """
        Aplica filtro para mostrar apenas mensagens não lidas.

        Returns:
            True se filtro aplicado, False caso contrário
        """
        logger.info("Aplicando filtro: apenas não lidas")

        try:
            if not self.is_element_present(self.SELECTORS['checkbox_nao_lidas'], timeout=5):
                logger.warning("Checkbox de filtro não encontrado")
                return False

            # Obter checkbox
            checkbox = self.find_element(self.SELECTORS['checkbox_nao_lidas'])

            # Verificar se já está marcado
            if not checkbox.is_selected():
                logger.info("Marcando checkbox não lidas")
                self.click_element(self.SELECTORS['checkbox_nao_lidas'])

                # Aguardar recarregamento
                self.aguardar_carregamento()

            logger.success("✓ Filtro aplicado")
            return True

        except Exception as e:
            logger.error(f"Erro ao aplicar filtro: {e}")
            return False

    def obter_total_mensagens(self) -> int:
        """
        Obtém número total de mensagens na lista.

        Returns:
            Número de mensagens
        """
        try:
            # Verificar se caixa está vazia
            if self.is_element_present(self.SELECTORS['msg_caixa_vazia'], timeout=2):
                logger.info("Caixa postal vazia")
                return 0

            # Contar linhas na tabela
            linhas = self.find_elements(self.SELECTORS['linha_mensagem'], timeout=5)

            # Filtrar linhas válidas (excluir cabeçalho)
            linhas_validas = [l for l in linhas if l.get_attribute('class') and 'header' not in l.get_attribute('class').lower()]

            total = len(linhas_validas)
            logger.info(f"Total de mensagens na página: {total}")

            return total

        except Exception as e:
            logger.warning(f"Erro ao contar mensagens: {e}")
            return 0

    def extrair_mensagens_lista(self) -> List[Dict[str, Any]]:
        """
        Extrai dados básicos de todas as mensagens da lista.

        Returns:
            Lista de dicionários com dados das mensagens
        """
        logger.info("Extraindo mensagens da lista...")

        mensagens = []

        try:
            # Verificar se há mensagens
            total = self.obter_total_mensagens()
            if total == 0:
                return mensagens

            # Buscar linhas
            linhas = self.find_elements(self.SELECTORS['linha_mensagem'], timeout=10)

            # Processar cada linha
            for idx, linha in enumerate(linhas, 1):
                try:
                    # Verificar se é linha válida (não é cabeçalho)
                    classe = linha.get_attribute('class') or ''
                    if 'header' in classe.lower() or 'thead' in linha.tag_name.lower():
                        continue

                    # Extrair dados
                    dados = self._extrair_dados_linha(linha, idx)

                    if dados:
                        mensagens.append(dados)

                except Exception as e:
                    logger.warning(f"Erro ao processar linha {idx}: {e}")
                    continue

            logger.success(f"✓ Extraídas {len(mensagens)} mensagens")

        except Exception as e:
            logger.error(f"Erro ao extrair mensagens: {e}")
            self.take_screenshot("erro_extrair_mensagens")

        return mensagens

    def _extrair_dados_linha(self, linha_element, index: int) -> Dict[str, Any]:
        """
        Extrai dados de uma linha da tabela.

        Args:
            linha_element: WebElement da linha
            index: Índice da linha

        Returns:
            Dicionário com dados ou None
        """
        try:
            # Buscar células dentro da linha
            colunas = linha_element.find_elements(By.TAG_NAME, "td")

            if len(colunas) < 3:
                return None

            # Extrair textos (ajustar índices conforme tabela real)
            data_text = colunas[0].text.strip() if len(colunas) > 0 else ""
            remetente = colunas[1].text.strip() if len(colunas) > 1 else ""
            assunto = colunas[2].text.strip() if len(colunas) > 2 else ""

            # Status (se disponível)
            status_text = ""
            if len(colunas) > 3:
                status_text = colunas[3].text.strip()

            # Buscar link de detalhes
            link_detalhes = ""
            try:
                link_element = linha_element.find_element(By.CSS_SELECTOR, "a")
                link_detalhes = link_element.get_attribute('href')
            except:
                pass

            # Verificar indicadores
            nao_lida = self._verificar_indicador_linha(linha_element, 'icone_nao_lida')
            tem_anexo = self._verificar_indicador_linha(linha_element, 'icone_anexo')
            urgente = self._verificar_indicador_linha(linha_element, 'icone_urgente')

            dados = {
                'index': index,
                'data': data_text,
                'remetente': remetente,
                'assunto': assunto,
                'status': status_text,
                'nao_lida': nao_lida,
                'tem_anexo': tem_anexo,
                'urgente': urgente,
                'link_detalhes': link_detalhes,
                'linha_element': linha_element  # Guardar referência
            }

            logger.debug(f"Mensagem {index}: {assunto[:50]}")

            return dados

        except Exception as e:
            logger.error(f"Erro ao extrair dados da linha: {e}")
            return None

    def _verificar_indicador_linha(self, linha_element, indicador_key: str) -> bool:
        """
        Verifica se um indicador está presente na linha.

        Args:
            linha_element: WebElement da linha
            indicador_key: Chave do seletor em SELECTORS

        Returns:
            True se indicador presente, False caso contrário
        """
        try:
            selector = self.SELECTORS[indicador_key][1]
            elementos = linha_element.find_elements(By.CSS_SELECTOR, selector)
            return len(elementos) > 0
        except:
            return False

    def clicar_mensagem(self, index: int) -> bool:
        """
        Clica em uma mensagem específica para ver detalhes.

        Args:
            index: Índice da mensagem (1-based)

        Returns:
            True se clicou com sucesso, False caso contrário
        """
        logger.info(f"Clicando em mensagem {index}...")

        try:
            # Buscar linhas
            linhas = self.find_elements(self.SELECTORS['linha_mensagem'])

            # Filtrar linhas válidas
            linhas_validas = [l for l in linhas if 'header' not in (l.get_attribute('class') or '').lower()]

            if index < 1 or index > len(linhas_validas):
                logger.error(f"Índice inválido: {index}")
                return False

            # Obter linha (index é 1-based, lista é 0-based)
            linha = linhas_validas[index - 1]

            # Buscar link dentro da linha
            try:
                link = linha.find_element(*self.SELECTORS['msg_link_detalhes'])
                link.click()
                logger.success(f"✓ Clicou em mensagem {index}")
                time.sleep(2)  # Aguardar navegação
                return True

            except:
                # Fallback: clicar na linha inteira
                linha.click()
                logger.info(f"Clicou na linha {index} (fallback)")
                time.sleep(2)
                return True

        except Exception as e:
            logger.error(f"Erro ao clicar em mensagem: {e}")
            self.take_screenshot(f"erro_clicar_mensagem_{index}")
            return False

    def tem_proxima_pagina(self) -> bool:
        """
        Verifica se há próxima página.

        Returns:
            True se há próxima página, False caso contrário
        """
        try:
            btn = self.find_element(self.SELECTORS['btn_proxima_pagina'], timeout=3)

            # Verificar se botão está habilitado
            disabled = btn.get_attribute('disabled')
            classe = btn.get_attribute('class') or ''

            return not disabled and 'disabled' not in classe.lower()

        except:
            return False

    def ir_proxima_pagina(self) -> bool:
        """
        Navega para próxima página.

        Returns:
            True se navegou, False caso contrário
        """
        if not self.tem_proxima_pagina():
            logger.info("Não há próxima página")
            return False

        logger.info("Navegando para próxima página...")

        if self.click_element(self.SELECTORS['btn_proxima_pagina']):
            self.aguardar_carregamento()
            return True

        return False

    def limpar_filtros(self) -> bool:
        """
        Limpa todos os filtros aplicados.

        Returns:
            True se limpou, False caso contrário
        """
        logger.info("Limpando filtros...")

        if self.is_element_present(self.SELECTORS['btn_limpar_filtro'], timeout=3):
            if self.click_element(self.SELECTORS['btn_limpar_filtro']):
                self.aguardar_carregamento()
                logger.success("✓ Filtros limpos")
                return True

        return False
