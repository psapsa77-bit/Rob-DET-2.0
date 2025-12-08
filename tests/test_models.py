"""
Testes Unitários - Models - Rob-DET 2.0
"""

import pytest
from datetime import datetime, timedelta

from src.models import (
    Cliente,
    Mensagem,
    RelatorioConsulta,
    TipoMensagem,
    StatusMensagem,
    PrioridadeMensagem
)


@pytest.mark.unit
class TestCliente:
    """Testes para a classe Cliente."""

    def test_criar_cliente_valido(self):
        """Testa criação de cliente com dados válidos."""
        cliente = Cliente(
            cnpj="12.345.678/0001-90",
            razao_social="Empresa Teste Ltda"
        )

        assert cliente.cnpj == "12.345.678/0001-90"
        assert cliente.razao_social == "Empresa Teste Ltda"
        assert cliente.ativo is True
        assert cliente.prioridade == "normal"
        assert cliente.ultima_consulta is None

    def test_normalizar_cnpj(self):
        """Testa normalização automática de CNPJ."""
        # CNPJ sem formatação
        cliente1 = Cliente(cnpj="12345678000190", razao_social="Teste")
        assert cliente1.cnpj == "12.345.678/0001-90"

        # CNPJ já formatado
        cliente2 = Cliente(cnpj="12.345.678/0001-90", razao_social="Teste")
        assert cliente2.cnpj == "12.345.678/0001-90"

        # CNPJ com formatação parcial
        cliente3 = Cliente(cnpj="12345678/0001-90", razao_social="Teste")
        assert cliente3.cnpj == "12.345.678/0001-90"

    def test_validar_cnpj_invalido(self):
        """Testa validação de CNPJ inválido."""
        with pytest.raises(ValueError, match="CNPJ inválido"):
            Cliente(cnpj="123", razao_social="Teste")

        with pytest.raises(ValueError, match="CNPJ inválido"):
            Cliente(cnpj="", razao_social="Teste")

    def test_validar_razao_social_vazia(self):
        """Testa validação de razão social vazia."""
        with pytest.raises(ValueError, match="Razão social não pode ser vazia"):
            Cliente(cnpj="12.345.678/0001-90", razao_social="")

    def test_prioridades_validas(self):
        """Testa diferentes prioridades."""
        for prioridade in ["alta", "normal", "baixa"]:
            cliente = Cliente(
                cnpj="12.345.678/0001-90",
                razao_social="Teste",
                prioridade=prioridade
            )
            assert cliente.prioridade == prioridade

    def test_atualizar_contadores(self):
        """Testa atualização de contadores."""
        cliente = Cliente(cnpj="12.345.678/0001-90", razao_social="Teste")

        assert cliente.total_mensagens == 0
        assert cliente.mensagens_nao_lidas == 0

        cliente.total_mensagens = 10
        cliente.mensagens_nao_lidas = 5

        assert cliente.total_mensagens == 10
        assert cliente.mensagens_nao_lidas == 5


@pytest.mark.unit
class TestMensagem:
    """Testes para a classe Mensagem."""

    def test_criar_mensagem_valida(self, mensagem_teste):
        """Testa criação de mensagem com dados válidos."""
        assert mensagem_teste.id == "msg_001"
        assert mensagem_teste.cnpj_destinatario == "12.345.678/0001-90"
        assert mensagem_teste.tipo == TipoMensagem.NOTIFICACAO
        assert mensagem_teste.status == StatusMensagem.NAO_LIDA
        assert mensagem_teste.prioridade == PrioridadeMensagem.NORMAL

    def test_is_urgente_por_prioridade(self):
        """Testa detecção de urgência por prioridade."""
        msg = Mensagem(
            id="msg_001",
            cnpj_destinatario="12.345.678/0001-90",
            data_envio=datetime.now(),
            tipo=TipoMensagem.COMUNICADO,
            status=StatusMensagem.NAO_LIDA,
            prioridade=PrioridadeMensagem.URGENTE
        )

        assert msg.is_urgente() is True

    def test_is_urgente_por_tipo(self):
        """Testa detecção de urgência por tipo de mensagem."""
        # Intimação é urgente
        msg1 = Mensagem(
            id="msg_001",
            cnpj_destinatario="12.345.678/0001-90",
            data_envio=datetime.now(),
            tipo=TipoMensagem.INTIMACAO,
            status=StatusMensagem.NAO_LIDA,
            prioridade=PrioridadeMensagem.NORMAL
        )
        assert msg1.is_urgente() is True

        # Autuação é urgente
        msg2 = Mensagem(
            id="msg_002",
            cnpj_destinatario="12.345.678/0001-90",
            data_envio=datetime.now(),
            tipo=TipoMensagem.AUTUACAO,
            status=StatusMensagem.NAO_LIDA,
            prioridade=PrioridadeMensagem.NORMAL
        )
        assert msg2.is_urgente() is True

    def test_is_urgente_por_prazo(self):
        """Testa detecção de urgência por prazo próximo."""
        # Prazo em 3 dias (urgente)
        msg1 = Mensagem(
            id="msg_001",
            cnpj_destinatario="12.345.678/0001-90",
            data_envio=datetime.now(),
            tipo=TipoMensagem.COMUNICADO,
            status=StatusMensagem.NAO_LIDA,
            prioridade=PrioridadeMensagem.NORMAL,
            prazo_resposta=datetime.now() + timedelta(days=3)
        )
        assert msg1.is_urgente() is True

        # Prazo em 10 dias (não urgente)
        msg2 = Mensagem(
            id="msg_002",
            cnpj_destinatario="12.345.678/0001-90",
            data_envio=datetime.now(),
            tipo=TipoMensagem.COMUNICADO,
            status=StatusMensagem.NAO_LIDA,
            prioridade=PrioridadeMensagem.NORMAL,
            prazo_resposta=datetime.now() + timedelta(days=10)
        )
        assert msg2.is_urgente() is False

    def test_is_nova(self):
        """Testa detecção de mensagem nova."""
        msg_nova = Mensagem(
            id="msg_001",
            cnpj_destinatario="12.345.678/0001-90",
            data_envio=datetime.now(),
            tipo=TipoMensagem.COMUNICADO,
            status=StatusMensagem.NAO_LIDA,
            prioridade=PrioridadeMensagem.NORMAL
        )
        assert msg_nova.is_nova() is True

        msg_lida = Mensagem(
            id="msg_002",
            cnpj_destinatario="12.345.678/0001-90",
            data_envio=datetime.now(),
            tipo=TipoMensagem.COMUNICADO,
            status=StatusMensagem.LIDA,
            prioridade=PrioridadeMensagem.NORMAL
        )
        assert msg_lida.is_nova() is False

    def test_to_dict(self, mensagem_teste):
        """Testa conversão para dicionário."""
        dados = mensagem_teste.to_dict()

        assert isinstance(dados, dict)
        assert dados['id'] == "msg_001"
        assert dados['cnpj_destinatario'] == "12.345.678/0001-90"
        assert dados['tipo'] == "notificacao"
        assert dados['status'] == "nao_lida"
        assert dados['prioridade'] == "normal"


@pytest.mark.unit
class TestRelatorioConsulta:
    """Testes para a classe RelatorioConsulta."""

    def test_criar_relatorio(self, cliente_teste):
        """Testa criação de relatório."""
        relatorio = RelatorioConsulta(
            data_consulta=datetime.now(),
            cnpj=cliente_teste.cnpj,
            razao_social=cliente_teste.razao_social
        )

        assert relatorio.cnpj == cliente_teste.cnpj
        assert relatorio.razao_social == cliente_teste.razao_social
        assert relatorio.mensagens == []
        assert relatorio.sucesso is False

    def test_calcular_estatisticas(self, relatorio_teste):
        """Testa cálculo de estatísticas."""
        assert relatorio_teste.total_mensagens == 3
        assert relatorio_teste.mensagens_novas == 2  # 2 não lidas
        assert relatorio_teste.mensagens_urgentes == 2  # Intimação + Autuação

    def test_calcular_estatisticas_vazio(self):
        """Testa cálculo com lista vazia."""
        relatorio = RelatorioConsulta(
            data_consulta=datetime.now(),
            cnpj="12.345.678/0001-90",
            razao_social="Teste"
        )

        relatorio.calcular_estatisticas()

        assert relatorio.total_mensagens == 0
        assert relatorio.mensagens_novas == 0
        assert relatorio.mensagens_urgentes == 0

    def test_get_resumo(self, relatorio_teste):
        """Testa geração de resumo."""
        resumo = relatorio_teste.get_resumo()

        assert isinstance(resumo, str)
        assert "Empresa Teste Ltda" in resumo
        assert "12.345.678/0001-90" in resumo
        assert "Total: 3" in resumo
        assert "Novas: 2" in resumo
        assert "Urgentes: 2" in resumo

    def test_to_dict(self, relatorio_teste):
        """Testa conversão para dicionário."""
        dados = relatorio_teste.to_dict()

        assert isinstance(dados, dict)
        assert dados['cnpj'] == "12.345.678/0001-90"
        assert dados['razao_social'] == "Empresa Teste Ltda"
        assert dados['total_mensagens'] == 3
        assert dados['mensagens_novas'] == 2
        assert dados['mensagens_urgentes'] == 2
        assert dados['sucesso'] is True
        assert isinstance(dados['mensagens'], list)
        assert len(dados['mensagens']) == 3


@pytest.mark.unit
class TestEnums:
    """Testes para os Enums."""

    def test_tipo_mensagem_values(self):
        """Testa valores do enum TipoMensagem."""
        assert TipoMensagem.INTIMACAO.value == "intimacao"
        assert TipoMensagem.NOTIFICACAO.value == "notificacao"
        assert TipoMensagem.AUTUACAO.value == "autuacao"
        assert TipoMensagem.COMUNICADO.value == "comunicado"
        assert TipoMensagem.SOLICITACAO.value == "solicitacao"
        assert TipoMensagem.OUTRO.value == "outro"

    def test_status_mensagem_values(self):
        """Testa valores do enum StatusMensagem."""
        assert StatusMensagem.NAO_LIDA.value == "nao_lida"
        assert StatusMensagem.LIDA.value == "lida"
        assert StatusMensagem.ARQUIVADA.value == "arquivada"

    def test_prioridade_mensagem_values(self):
        """Testa valores do enum PrioridadeMensagem."""
        assert PrioridadeMensagem.URGENTE.value == "urgente"
        assert PrioridadeMensagem.ALTA.value == "alta"
        assert PrioridadeMensagem.NORMAL.value == "normal"
        assert PrioridadeMensagem.BAIXA.value == "baixa"
