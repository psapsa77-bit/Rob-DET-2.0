"""
DET Scraper - Rob-DET 2.0

Módulo principal de scraping do portal DET.
Coordena autenticação, navegação e extração de dados.
"""

import time
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.navigation.det_navigator import DETNavigator
from src.models import Cliente, Mensagem, RelatorioConsulta, TipoMensagem, StatusMensagem


class DETScraper:
    """
    Scraper principal para o portal DET.

    Responsável por:
    - Autenticação com certificado digital
    - Navegação entre CNPJs via procuração
    - Extração de mensagens da caixa postal
    - Geração de relatórios
    """

    # URLs importantes
    URL_BASE = "https://det.sit.trabalho.gov.br/"
    URL_CAIXA_POSTAL = "https://det.sit.trabalho.gov.br/correspondencia/caixaPostal"

    # Seletores CSS (AJUSTAR conforme HTML real do portal!)
    SELECTORS = {
        # Seleção de empresa
        'dropdown_empresa': 'select[name="empresaSelecionada"]',
        'opcao_empresa': 'option[value="{cnpj}"]',

        # Caixa postal
        'tabela_mensagens': 'table.table-mensagens',
        'linha_mensagem': 'tr.mensagem-item',
        'checkbox_nao_lida': 'input[name="apenasNaoLidas"]',

        # Campos de mensagem
        'msg_data': 'td.data-envio',
        'msg_remetente': 'td.remetente',
        'msg_assunto': 'td.assunto',
        'msg_status': 'td.status',
        'msg_link': 'a.ver-detalhes',

        # Paginação
        'btn_proxima_pagina': 'button.proxima-pagina',
        'numero_pagina': 'span.pagina-atual',
    }

    def __init__(
        self,
        navigator: DETNavigator,
        timeout: int = 30,
        delay_between_actions: float = 1.5
    ):
        """
        Inicializa o scraper.

        Args:
            navigator: Instância do DETNavigator
            timeout: Timeout padrão em segundos
            delay_between_actions: Delay entre ações
        """
        self.navigator = navigator
        self.driver = navigator.driver
        self.timeout = timeout
        self.delay = delay_between_actions

        self.logged_in = False
        self.current_cnpj: Optional[str] = None

        logger.info("DETScraper inicializado")

    def login(self) -> bool:
        """
        Realiza login no portal DET com certificado digital.

        Returns:
            True se login bem-sucedido, False caso contrário
        """
        logger.info("Iniciando login no DET...")

        try:
            # Navegar para página inicial
            self.navigator.navigate_to(self.URL_BASE)

            # Aguardar processamento do certificado
            # O certificado deve ser selecionado automaticamente via Registry
            logger.info("Aguardando seleção automática de certificado...")
            time.sleep(10)  # Aguardar processamento

            # Verificar se login foi bem-sucedido
            # AJUSTAR: verificar elemento que confirma login
            try:
                # Exemplo: aguardar elemento que só aparece após login
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.usuario-logado"))
                )
                logger.success("✓ Login realizado com sucesso!")
                self.logged_in = True
                return True

            except TimeoutException:
                # Tentar verificar pela URL
                current_url = self.driver.current_url
                if "login" not in current_url.lower() and "det.sit.trabalho.gov.br" in current_url:
                    logger.success("✓ Login realizado com sucesso!")
                    self.logged_in = True
                    return True
                else:
                    logger.error("Login não confirmado")
                    return False

        except Exception as e:
            logger.error(f"Erro durante login: {e}")
            return False

    def selecionar_empresa(self, cnpj: str) -> bool:
        """
        Seleciona empresa via dropdown de procuração.

        Args:
            cnpj: CNPJ da empresa a selecionar

        Returns:
            True se selecionado com sucesso, False caso contrário
        """
        if not self.logged_in:
            logger.error("Não está logado no DET")
            return False

        try:
            logger.info(f"Selecionando empresa: {cnpj}")

            # Normalizar CNPJ (apenas números)
            cnpj_numeros = ''.join(filter(str.isdigit, cnpj))

            # Aguardar dropdown de empresa
            wait = WebDriverWait(self.driver, self.timeout)
            dropdown = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.SELECTORS['dropdown_empresa']))
            )

            # Buscar opção do CNPJ
            opcao_selector = self.SELECTORS['opcao_empresa'].format(cnpj=cnpj_numeros)

            try:
                opcao = dropdown.find_element(By.CSS_SELECTOR, opcao_selector)
                opcao.click()

                logger.success(f"✓ Empresa {cnpj} selecionada")
                self.current_cnpj = cnpj

                # Aguardar carregamento
                time.sleep(self.delay)
                return True

            except NoSuchElementException:
                logger.error(f"CNPJ {cnpj} não encontrado no dropdown")
                logger.warning("Verifique se você tem procuração para este CNPJ")
                return False

        except TimeoutException:
            logger.error("Dropdown de empresas não encontrado")
            logger.warning("Possível que não há procuração ou estrutura da página mudou")
            return False

        except Exception as e:
            logger.error(f"Erro ao selecionar empresa: {e}")
            return False

    def acessar_caixa_postal(self) -> bool:
        """
        Navega para a caixa postal.

        Returns:
            True se acessou com sucesso, False caso contrário
        """
        try:
            logger.info("Acessando caixa postal...")

            self.navigator.navigate_to(self.URL_CAIXA_POSTAL)

            # Aguardar tabela de mensagens carregar
            wait = WebDriverWait(self.driver, self.timeout)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.SELECTORS['tabela_mensagens']))
            )

            logger.success("✓ Caixa postal carregada")
            return True

        except TimeoutException:
            logger.warning("Tabela de mensagens não carregou (pode estar vazia)")
            return True  # Não é erro crítico, pode estar vazia

        except Exception as e:
            logger.error(f"Erro ao acessar caixa postal: {e}")
            return False

    def filtrar_apenas_nao_lidas(self) -> bool:
        """
        Aplica filtro para mostrar apenas mensagens não lidas.

        Returns:
            True se filtro aplicado, False caso contrário
        """
        try:
            logger.info("Aplicando filtro: apenas não lidas")

            # Buscar checkbox
            checkbox = self.driver.find_element(By.CSS_SELECTOR, self.SELECTORS['checkbox_nao_lida'])

            # Marcar se não estiver marcado
            if not checkbox.is_selected():
                checkbox.click()
                time.sleep(self.delay)  # Aguardar recarregamento

            logger.success("✓ Filtro aplicado")
            return True

        except NoSuchElementException:
            logger.warning("Checkbox de filtro não encontrado")
            return False

        except Exception as e:
            logger.error(f"Erro ao aplicar filtro: {e}")
            return False

    def extrair_mensagens(self, apenas_nao_lidas: bool = False) -> List[Mensagem]:
        """
        Extrai mensagens da página atual da caixa postal.

        Args:
            apenas_nao_lidas: Se True, extrai apenas não lidas

        Returns:
            Lista de mensagens extraídas
        """
        mensagens = []

        try:
            logger.info("Extraindo mensagens da caixa postal...")

            # Aplicar filtro se necessário
            if apenas_nao_lidas:
                self.filtrar_apenas_nao_lidas()

            # Buscar tabela de mensagens
            try:
                tabela = self.driver.find_element(By.CSS_SELECTOR, self.SELECTORS['tabela_mensagens'])
            except NoSuchElementException:
                logger.warning("Tabela de mensagens não encontrada (caixa vazia?)")
                return []

            # Buscar linhas de mensagens
            linhas = tabela.find_elements(By.CSS_SELECTOR, self.SELECTORS['linha_mensagem'])

            if not linhas:
                logger.info("Nenhuma mensagem encontrada")
                return []

            logger.info(f"Encontradas {len(linhas)} mensagens")

            # Processar cada linha
            for idx, linha in enumerate(linhas, 1):
                try:
                    mensagem = self._extrair_mensagem_da_linha(linha, idx)
                    if mensagem:
                        mensagens.append(mensagem)
                except Exception as e:
                    logger.warning(f"Erro ao processar linha {idx}: {e}")
                    continue

            logger.success(f"✓ Extraídas {len(mensagens)} mensagens")

        except Exception as e:
            logger.error(f"Erro ao extrair mensagens: {e}")

        return mensagens

    def _extrair_mensagem_da_linha(self, linha_element, index: int) -> Optional[Mensagem]:
        """
        Extrai dados de uma mensagem a partir de uma linha da tabela.

        Args:
            linha_element: Elemento HTML da linha
            index: Índice da linha (para ID temporário)

        Returns:
            Mensagem extraída ou None se erro
        """
        try:
            # Extrair campos (AJUSTAR seletores conforme HTML real!)
            data_text = linha_element.find_element(By.CSS_SELECTOR, self.SELECTORS['msg_data']).text.strip()
            remetente = linha_element.find_element(By.CSS_SELECTOR, self.SELECTORS['msg_remetente']).text.strip()
            assunto = linha_element.find_element(By.CSS_SELECTOR, self.SELECTORS['msg_assunto']).text.strip()

            # Status (lida/não lida)
            try:
                status_text = linha_element.find_element(By.CSS_SELECTOR, self.SELECTORS['msg_status']).text.strip().lower()
                status = StatusMensagem.LIDA if 'lida' in status_text else StatusMensagem.NAO_LIDA
            except:
                status = StatusMensagem.NAO_LIDA  # Padrão

            # Link para detalhes
            try:
                link_element = linha_element.find_element(By.CSS_SELECTOR, self.SELECTORS['msg_link'])
                url_detalhes = link_element.get_attribute('href')
            except:
                url_detalhes = None

            # Parsear data
            # AJUSTAR formato conforme portal
            try:
                data_envio = datetime.strptime(data_text, "%d/%m/%Y")
            except:
                data_envio = datetime.now()

            # Classificar tipo de mensagem
            tipo = self._classificar_tipo_mensagem(assunto)

            # Criar mensagem
            mensagem = Mensagem(
                id=f"det_{self.current_cnpj}_{index}_{int(time.time())}",
                cnpj_destinatario=self.current_cnpj or "",
                data_envio=data_envio,
                remetente=remetente,
                assunto=assunto,
                tipo=tipo,
                status=status,
                url_detalhes=url_detalhes
            )

            return mensagem

        except Exception as e:
            logger.error(f"Erro ao extrair mensagem: {e}")
            return None

    def _classificar_tipo_mensagem(self, assunto: str) -> TipoMensagem:
        """
        Classifica tipo de mensagem baseado no assunto.

        Args:
            assunto: Assunto da mensagem

        Returns:
            TipoMensagem
        """
        assunto_lower = assunto.lower()

        keywords_map = {
            TipoMensagem.AUTUACAO: ['autuação', 'auto de infração', 'multa'],
            TipoMensagem.INTIMACAO: ['intimação', 'comparecer'],
            TipoMensagem.NOTIFICACAO: ['notificação', 'aviso'],
            TipoMensagem.COMUNICADO: ['comunicado', 'informação'],
            TipoMensagem.SOLICITACAO: ['solicitação', 'documentos', 'enviar'],
        }

        for tipo, keywords in keywords_map.items():
            if any(keyword in assunto_lower for keyword in keywords):
                return tipo

        return TipoMensagem.OUTRO

    def consultar_cliente(self, cliente: Cliente, apenas_nao_lidas: bool = False) -> RelatorioConsulta:
        """
        Consulta mensagens de um cliente específico.

        Args:
            cliente: Cliente a consultar
            apenas_nao_lidas: Se True, extrai apenas não lidas

        Returns:
            RelatorioConsulta com resultados
        """
        inicio = time.time()

        relatorio = RelatorioConsulta(
            data_consulta=datetime.now(),
            cnpj=cliente.cnpj,
            razao_social=cliente.razao_social
        )

        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Consultando: {cliente.razao_social} ({cliente.cnpj})")
            logger.info(f"{'='*60}")

            # Selecionar empresa
            if not self.selecionar_empresa(cliente.cnpj):
                relatorio.sucesso = False
                relatorio.erro = "Falha ao selecionar empresa"
                return relatorio

            # Acessar caixa postal
            if not self.acessar_caixa_postal():
                relatorio.sucesso = False
                relatorio.erro = "Falha ao acessar caixa postal"
                return relatorio

            # Extrair mensagens
            mensagens = self.extrair_mensagens(apenas_nao_lidas=apenas_nao_lidas)
            relatorio.mensagens = mensagens

            # Calcular estatísticas
            relatorio.calcular_estatisticas()

            # Atualizar cliente
            cliente.ultima_consulta = datetime.now()
            cliente.total_mensagens = relatorio.total_mensagens
            cliente.mensagens_nao_lidas = relatorio.mensagens_novas

            relatorio.sucesso = True

            logger.info(f"\n{relatorio.get_resumo()}")

        except Exception as e:
            logger.error(f"Erro ao consultar cliente: {e}")
            relatorio.sucesso = False
            relatorio.erro = str(e)

        finally:
            relatorio.tempo_execucao = time.time() - inicio
            logger.info(f"Tempo de execução: {relatorio.tempo_execucao:.2f}s")

        return relatorio

    def consultar_multiplos_clientes(
        self,
        clientes: List[Cliente],
        apenas_nao_lidas: bool = False
    ) -> List[RelatorioConsulta]:
        """
        Consulta múltiplos clientes sequencialmente.

        Args:
            clientes: Lista de clientes
            apenas_nao_lidas: Se True, extrai apenas não lidas

        Returns:
            Lista de relatórios
        """
        relatorios = []

        logger.info(f"\n{'='*60}")
        logger.info(f"CONSULTANDO {len(clientes)} CLIENTES")
        logger.info(f"{'='*60}\n")

        for idx, cliente in enumerate(clientes, 1):
            logger.info(f"\nCliente {idx}/{len(clientes)}")

            relatorio = self.consultar_cliente(cliente, apenas_nao_lidas=apenas_nao_lidas)
            relatorios.append(relatorio)

            # Delay entre clientes
            if idx < len(clientes):
                logger.info(f"Aguardando {self.delay}s antes do próximo cliente...")
                time.sleep(self.delay)

        # Resumo final
        self._imprimir_resumo_geral(relatorios)

        return relatorios

    def _imprimir_resumo_geral(self, relatorios: List[RelatorioConsulta]):
        """Imprime resumo geral das consultas."""
        logger.info(f"\n{'='*60}")
        logger.info("RESUMO GERAL")
        logger.info(f"{'='*60}\n")

        total_consultados = len(relatorios)
        total_sucesso = sum(1 for r in relatorios if r.sucesso)
        total_mensagens = sum(r.total_mensagens for r in relatorios)
        total_novas = sum(r.mensagens_novas for r in relatorios)
        total_urgentes = sum(r.mensagens_urgentes for r in relatorios)

        logger.info(f"Clientes consultados: {total_sucesso}/{total_consultados}")
        logger.info(f"Total de mensagens: {total_mensagens}")
        logger.info(f"Mensagens novas: {total_novas}")
        logger.info(f"Mensagens urgentes: {total_urgentes}")

        if total_sucesso < total_consultados:
            logger.warning(f"\n⚠️  {total_consultados - total_sucesso} cliente(s) com erro")

    def logout(self):
        """Realiza logout do portal."""
        logger.info("Logout do DET...")
        self.logged_in = False
        self.current_cnpj = None
        # Navegador será fechado pelo navigator


# Exemplo de uso
if __name__ == '__main__':
    from src.navigation.det_navigator import DETNavigator
    from src.models import Cliente

    # Criar navigator
    navigator = DETNavigator(browser='chrome', headless=False)
    navigator.start()

    try:
        # Criar scraper
        scraper = DETScraper(navigator)

        # Login
        if scraper.login():
            # Cliente de teste
            cliente = Cliente(
                cnpj="12.345.678/0001-90",
                razao_social="Empresa Teste Ltda"
            )

            # Consultar
            relatorio = scraper.consultar_cliente(cliente, apenas_nao_lidas=True)

            print(f"\n{relatorio.get_resumo()}")

    finally:
        navigator.stop()
