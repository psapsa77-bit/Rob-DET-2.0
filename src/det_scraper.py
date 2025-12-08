"""
DET Scraper - Rob-DET 2.0

Módulo principal de scraping do portal DET.
Coordena autenticação, navegação e extração de dados.
"""

import time
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from src.navigation.det_navigator import DETNavigator
from src.models import Cliente, Mensagem, RelatorioConsulta, TipoMensagem, StatusMensagem, PrioridadeMensagem
from src.pages import LoginPage, HomePage, CaixaPostalPage, MensagemDetalhesPage


class DETScraper:
    """
    Scraper principal para o portal DET.

    Responsável por:
    - Autenticação com certificado digital
    - Navegação entre CNPJs via procuração
    - Extração de mensagens da caixa postal
    - Geração de relatórios

    Utiliza Page Object Model para organização:
    - LoginPage: Autenticação com certificado
    - HomePage: Seleção de empresa e navegação
    - CaixaPostalPage: Listagem de mensagens
    - MensagemDetalhesPage: Detalhes e anexos
    """

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

        # Inicializar Page Objects
        self.login_page = LoginPage(self.driver)
        self.home_page = HomePage(self.driver)
        self.caixa_postal_page = CaixaPostalPage(self.driver)
        self.detalhes_page = MensagemDetalhesPage(self.driver)

        logger.info("DETScraper inicializado com Page Objects")

    def login(self) -> bool:
        """
        Realiza login no portal DET com certificado digital.

        Returns:
            True se login bem-sucedido, False caso contrário
        """
        logger.info("Iniciando login no DET...")

        try:
            # Utilizar LoginPage para realizar login
            sucesso = self.login_page.realizar_login()

            if sucesso:
                self.logged_in = True
                logger.success("✓ Login realizado com sucesso!")
            else:
                logger.error("❌ Falha no login")

            return sucesso

        except Exception as e:
            logger.error(f"Erro durante login: {e}")
            self.login_page.take_screenshot("erro_login")
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

            # Utilizar HomePage para selecionar empresa
            sucesso = self.home_page.selecionar_empresa(cnpj)

            if sucesso:
                self.current_cnpj = cnpj
                logger.success(f"✓ Empresa {cnpj} selecionada")
                time.sleep(self.delay)  # Aguardar carregamento
            else:
                logger.error(f"❌ Falha ao selecionar empresa {cnpj}")

            return sucesso

        except Exception as e:
            logger.error(f"Erro ao selecionar empresa: {e}")
            self.home_page.take_screenshot(f"erro_selecionar_empresa_{cnpj}")
            return False

    def acessar_caixa_postal(self) -> bool:
        """
        Navega para a caixa postal.

        Returns:
            True se acessou com sucesso, False caso contrário
        """
        try:
            logger.info("Acessando caixa postal...")

            # Utilizar HomePage para navegar para caixa postal
            sucesso = self.home_page.navegar_para_caixa_postal()

            if sucesso:
                logger.success("✓ Caixa postal acessada")
                time.sleep(self.delay)
            else:
                logger.error("❌ Falha ao acessar caixa postal")

            return sucesso

        except Exception as e:
            logger.error(f"Erro ao acessar caixa postal: {e}")
            self.home_page.take_screenshot("erro_acessar_caixa_postal")
            return False

    def filtrar_apenas_nao_lidas(self) -> bool:
        """
        Aplica filtro para mostrar apenas mensagens não lidas.

        Returns:
            True se filtro aplicado, False caso contrário
        """
        try:
            logger.info("Aplicando filtro: apenas não lidas")

            # Utilizar CaixaPostalPage para aplicar filtro
            sucesso = self.caixa_postal_page.aplicar_filtro_nao_lidas()

            if sucesso:
                logger.success("✓ Filtro aplicado")
                time.sleep(self.delay)
            else:
                logger.warning("⚠️  Filtro não disponível")

            return sucesso

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

            # Obter total de mensagens
            total = self.caixa_postal_page.obter_total_mensagens()
            logger.info(f"Total de mensagens na página: {total}")

            if total == 0:
                logger.info("Nenhuma mensagem encontrada")
                return []

            # Extrair dados brutos das mensagens
            mensagens_raw = self.caixa_postal_page.extrair_mensagens_lista()

            logger.info(f"Encontradas {len(mensagens_raw)} mensagens")

            # Converter para objetos Mensagem
            for idx, msg_data in enumerate(mensagens_raw, 1):
                try:
                    mensagem = self._converter_para_mensagem(msg_data, idx)
                    if mensagem:
                        mensagens.append(mensagem)
                except Exception as e:
                    logger.warning(f"Erro ao processar mensagem {idx}: {e}")
                    continue

            logger.success(f"✓ Extraídas {len(mensagens)} mensagens")

        except Exception as e:
            logger.error(f"Erro ao extrair mensagens: {e}")
            self.caixa_postal_page.take_screenshot("erro_extrair_mensagens")

        return mensagens

    def _converter_para_mensagem(self, msg_data: Dict[str, Any], index: int) -> Optional[Mensagem]:
        """
        Converte dados brutos extraídos para objeto Mensagem.

        Args:
            msg_data: Dicionário com dados da mensagem
            index: Índice da mensagem

        Returns:
            Objeto Mensagem ou None se erro
        """
        try:
            # Parsear data de envio
            data_envio = datetime.now()
            if msg_data.get('data_envio'):
                try:
                    # Tentar diferentes formatos de data
                    data_text = msg_data['data_envio']
                    for formato in ["%d/%m/%Y", "%d/%m/%Y %H:%M", "%Y-%m-%d"]:
                        try:
                            data_envio = datetime.strptime(data_text, formato)
                            break
                        except:
                            continue
                except:
                    pass

            # Parsear prazo de resposta
            prazo_resposta = None
            if msg_data.get('prazo_resposta'):
                try:
                    prazo_text = msg_data['prazo_resposta']
                    for formato in ["%d/%m/%Y", "%d/%m/%Y %H:%M", "%Y-%m-%d"]:
                        try:
                            prazo_resposta = datetime.strptime(prazo_text, formato)
                            break
                        except:
                            continue
                except:
                    pass

            # Determinar status
            status = StatusMensagem.NAO_LIDA
            if msg_data.get('status'):
                status_text = msg_data['status'].lower()
                if 'lida' in status_text:
                    status = StatusMensagem.LIDA

            # Classificar tipo de mensagem
            assunto = msg_data.get('assunto', '')
            tipo = self._classificar_tipo_mensagem(assunto)

            # Determinar prioridade
            prioridade = PrioridadeMensagem.NORMAL
            if msg_data.get('urgente') or msg_data.get('prioridade_alta'):
                prioridade = PrioridadeMensagem.URGENTE
            elif tipo in [TipoMensagem.INTIMACAO, TipoMensagem.AUTUACAO]:
                prioridade = PrioridadeMensagem.ALTA

            # Criar mensagem
            mensagem = Mensagem(
                id=f"det_{self.current_cnpj}_{index}_{int(time.time())}",
                cnpj_destinatario=self.current_cnpj or "",
                data_envio=data_envio,
                remetente=msg_data.get('remetente', ''),
                assunto=assunto,
                tipo=tipo,
                status=status,
                prioridade=prioridade,
                prazo_resposta=prazo_resposta,
                numero_processo=msg_data.get('numero_processo', ''),
                possui_anexo=msg_data.get('possui_anexo', False),
                url_detalhes=msg_data.get('url_detalhes', '')
            )

            return mensagem

        except Exception as e:
            logger.error(f"Erro ao converter mensagem: {e}")
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

    def extrair_detalhes_mensagem(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Extrai detalhes completos de uma mensagem específica.

        Args:
            index: Índice da mensagem na lista (1-based)

        Returns:
            Dicionário com detalhes completos ou None se erro
        """
        try:
            logger.info(f"Extraindo detalhes da mensagem {index}...")

            # Clicar na mensagem
            if not self.caixa_postal_page.clicar_mensagem(index):
                logger.error(f"Falha ao clicar na mensagem {index}")
                return None

            # Aguardar carregamento da página de detalhes
            time.sleep(self.delay)

            # Extrair detalhes completos
            detalhes = self.detalhes_page.extrair_detalhes_completos()

            logger.success(f"✓ Detalhes extraídos: {detalhes['assunto'][:60]}")

            # Voltar para lista
            if self.detalhes_page.voltar_para_lista():
                time.sleep(self.delay)
            else:
                logger.warning("Não foi possível voltar para lista")

            return detalhes

        except Exception as e:
            logger.error(f"Erro ao extrair detalhes da mensagem: {e}")
            self.detalhes_page.take_screenshot(f"erro_detalhes_msg_{index}")
            return None

    def download_anexos_mensagem(self, index: int) -> int:
        """
        Faz download de todos os anexos de uma mensagem.

        Args:
            index: Índice da mensagem na lista (1-based)

        Returns:
            Número de anexos baixados com sucesso
        """
        try:
            logger.info(f"Iniciando download de anexos da mensagem {index}...")

            # Clicar na mensagem
            if not self.caixa_postal_page.clicar_mensagem(index):
                logger.error(f"Falha ao clicar na mensagem {index}")
                return 0

            time.sleep(self.delay)

            # Download de anexos
            total_baixados = self.detalhes_page.download_todos_anexos()

            logger.success(f"✓ {total_baixados} anexo(s) baixado(s)")

            # Voltar para lista
            self.detalhes_page.voltar_para_lista()
            time.sleep(self.delay)

            return total_baixados

        except Exception as e:
            logger.error(f"Erro ao baixar anexos: {e}")
            return 0

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
