"""
Modelos de Dados - Rob-DET 2.0

Define as estruturas de dados principais do sistema:
- Cliente (empresa com procuração)
- Mensagem do DET
- Relatório de consulta
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class TipoMensagem(Enum):
    """Tipos de mensagens do DET."""
    AUTUACAO = "Autuação"
    INTIMACAO = "Intimação"
    NOTIFICACAO = "Notificação"
    COMUNICADO = "Comunicado"
    SOLICITACAO = "Solicitação"
    OUTRO = "Outro"


class PrioridadeMensagem(Enum):
    """Prioridade de mensagens."""
    URGENTE = "urgente"
    ALTA = "alta"
    NORMAL = "normal"
    BAIXA = "baixa"


class StatusMensagem(Enum):
    """Status de leitura da mensagem."""
    NAO_LIDA = "não lida"
    LIDA = "lida"
    ARQUIVADA = "arquivada"


@dataclass
class Cliente:
    """
    Representa um cliente (empresa) com procuração para acesso ao DET.

    Attributes:
        cnpj: CNPJ da empresa
        razao_social: Razão social
        nome_fantasia: Nome fantasia (opcional)
        ativo: Se o cliente está ativo para consulta
        prioridade: Prioridade de processamento
        email_notificacao: Email para notificações
        observacoes: Observações sobre o cliente
        filiais: Lista de CNPJs de filiais
    """
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    ativo: bool = True
    prioridade: str = "normal"  # high, normal, low
    email_notificacao: Optional[str] = None
    observacoes: Optional[str] = None
    filiais: List[str] = field(default_factory=list)

    # Metadados
    ultima_consulta: Optional[datetime] = None
    total_mensagens: int = 0
    mensagens_nao_lidas: int = 0

    def __post_init__(self):
        """Valida dados após inicialização."""
        # Normalizar CNPJ
        self.cnpj = self._normalizar_cnpj(self.cnpj)

        # Validar prioridade
        if self.prioridade not in ['high', 'normal', 'low']:
            self.prioridade = 'normal'

    @staticmethod
    def _normalizar_cnpj(cnpj: str) -> str:
        """
        Normaliza CNPJ para formato padrão.

        Args:
            cnpj: CNPJ com ou sem formatação

        Returns:
            CNPJ formatado: 00.000.000/0001-00
        """
        # Remove caracteres não numéricos
        numeros = ''.join(filter(str.isdigit, cnpj))

        if len(numeros) != 14:
            raise ValueError(f"CNPJ inválido: {cnpj}")

        # Formata
        return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            'cnpj': self.cnpj,
            'razao_social': self.razao_social,
            'nome_fantasia': self.nome_fantasia,
            'ativo': self.ativo,
            'prioridade': self.prioridade,
            'email_notificacao': self.email_notificacao,
            'observacoes': self.observacoes,
            'filiais': self.filiais,
            'ultima_consulta': self.ultima_consulta.isoformat() if self.ultima_consulta else None,
            'total_mensagens': self.total_mensagens,
            'mensagens_nao_lidas': self.mensagens_nao_lidas
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Cliente':
        """Cria instância a partir de dicionário."""
        # Converter ultima_consulta de string para datetime
        if data.get('ultima_consulta'):
            data['ultima_consulta'] = datetime.fromisoformat(data['ultima_consulta'])

        return cls(**data)


@dataclass
class Mensagem:
    """
    Representa uma mensagem recebida no DET.

    Attributes:
        id: ID único da mensagem
        cnpj_destinatario: CNPJ do destinatário
        data_envio: Data de envio
        data_recebimento: Data de recebimento
        remetente: Órgão remetente
        assunto: Assunto da mensagem
        conteudo: Conteúdo/resumo da mensagem
        tipo: Tipo da mensagem
        prioridade: Prioridade
        status: Status de leitura
        possui_anexo: Se possui anexo
        anexos: Lista de anexos
        prazo_resposta: Data limite para resposta (se aplicável)
        numero_processo: Número de processo relacionado
        tags: Tags para categorização
    """
    id: str
    cnpj_destinatario: str
    data_envio: datetime
    remetente: str
    assunto: str
    tipo: TipoMensagem = TipoMensagem.OUTRO
    status: StatusMensagem = StatusMensagem.NAO_LIDA
    prioridade: PrioridadeMensagem = PrioridadeMensagem.NORMAL

    # Campos opcionais
    data_recebimento: Optional[datetime] = None
    conteudo: Optional[str] = None
    possui_anexo: bool = False
    anexos: List[str] = field(default_factory=list)
    prazo_resposta: Optional[datetime] = None
    numero_processo: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # Metadados
    url_detalhes: Optional[str] = None
    data_leitura: Optional[datetime] = None
    data_extracao: datetime = field(default_factory=datetime.now)

    def is_nova(self) -> bool:
        """Verifica se mensagem é nova (não lida)."""
        return self.status == StatusMensagem.NAO_LIDA

    def is_urgente(self) -> bool:
        """Verifica se mensagem é urgente."""
        # Urgente se:
        # 1. Prioridade é urgente
        # 2. É intimação ou autuação
        # 3. Tem prazo próximo (menos de 5 dias)

        if self.prioridade == PrioridadeMensagem.URGENTE:
            return True

        if self.tipo in [TipoMensagem.INTIMACAO, TipoMensagem.AUTUACAO]:
            return True

        if self.prazo_resposta:
            dias_restantes = (self.prazo_resposta - datetime.now()).days
            if dias_restantes <= 5:
                return True

        return False

    def has_prazo_vencido(self) -> bool:
        """Verifica se prazo está vencido."""
        if not self.prazo_resposta:
            return False

        return datetime.now() > self.prazo_resposta

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            'id': self.id,
            'cnpj_destinatario': self.cnpj_destinatario,
            'data_envio': self.data_envio.isoformat(),
            'data_recebimento': self.data_recebimento.isoformat() if self.data_recebimento else None,
            'remetente': self.remetente,
            'assunto': self.assunto,
            'conteudo': self.conteudo,
            'tipo': self.tipo.value,
            'prioridade': self.prioridade.value,
            'status': self.status.value,
            'possui_anexo': self.possui_anexo,
            'anexos': self.anexos,
            'prazo_resposta': self.prazo_resposta.isoformat() if self.prazo_resposta else None,
            'numero_processo': self.numero_processo,
            'tags': self.tags,
            'url_detalhes': self.url_detalhes,
            'data_leitura': self.data_leitura.isoformat() if self.data_leitura else None,
            'data_extracao': self.data_extracao.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Mensagem':
        """Cria instância a partir de dicionário."""
        # Converter strings para datetime
        data['data_envio'] = datetime.fromisoformat(data['data_envio'])

        if data.get('data_recebimento'):
            data['data_recebimento'] = datetime.fromisoformat(data['data_recebimento'])

        if data.get('prazo_resposta'):
            data['prazo_resposta'] = datetime.fromisoformat(data['prazo_resposta'])

        if data.get('data_leitura'):
            data['data_leitura'] = datetime.fromisoformat(data['data_leitura'])

        if data.get('data_extracao'):
            data['data_extracao'] = datetime.fromisoformat(data['data_extracao'])

        # Converter strings para Enums
        data['tipo'] = TipoMensagem(data['tipo'])
        data['prioridade'] = PrioridadeMensagem(data['prioridade'])
        data['status'] = StatusMensagem(data['status'])

        return cls(**data)


@dataclass
class RelatorioConsulta:
    """
    Representa um relatório de consulta ao DET.

    Attributes:
        data_consulta: Data/hora da consulta
        cnpj: CNPJ consultado
        razao_social: Razão social
        total_mensagens: Total de mensagens encontradas
        mensagens_novas: Mensagens não lidas
        mensagens_urgentes: Mensagens urgentes
        sucesso: Se a consulta foi bem-sucedida
        erro: Mensagem de erro (se houver)
        mensagens: Lista de mensagens encontradas
    """
    data_consulta: datetime
    cnpj: str
    razao_social: str
    sucesso: bool = True

    # Estatísticas
    total_mensagens: int = 0
    mensagens_novas: int = 0
    mensagens_urgentes: int = 0
    mensagens_com_prazo: int = 0
    prazos_vencidos: int = 0

    # Dados
    mensagens: List[Mensagem] = field(default_factory=list)
    erro: Optional[str] = None

    # Metadados
    tempo_execucao: float = 0.0  # em segundos

    def calcular_estatisticas(self):
        """Calcula estatísticas baseadas nas mensagens."""
        self.total_mensagens = len(self.mensagens)
        self.mensagens_novas = sum(1 for m in self.mensagens if m.is_nova())
        self.mensagens_urgentes = sum(1 for m in self.mensagens if m.is_urgente())
        self.mensagens_com_prazo = sum(1 for m in self.mensagens if m.prazo_resposta)
        self.prazos_vencidos = sum(1 for m in self.mensagens if m.has_prazo_vencido())

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            'data_consulta': self.data_consulta.isoformat(),
            'cnpj': self.cnpj,
            'razao_social': self.razao_social,
            'sucesso': self.sucesso,
            'total_mensagens': self.total_mensagens,
            'mensagens_novas': self.mensagens_novas,
            'mensagens_urgentes': self.mensagens_urgentes,
            'mensagens_com_prazo': self.mensagens_com_prazo,
            'prazos_vencidos': self.prazos_vencidos,
            'mensagens': [m.to_dict() for m in self.mensagens],
            'erro': self.erro,
            'tempo_execucao': self.tempo_execucao
        }

    def get_resumo(self) -> str:
        """Retorna resumo textual do relatório."""
        if not self.sucesso:
            return f"❌ Erro ao consultar {self.razao_social}: {self.erro}"

        resumo_parts = [
            f"✅ {self.razao_social} ({self.cnpj})",
            f"📧 Total: {self.total_mensagens}",
        ]

        if self.mensagens_novas > 0:
            resumo_parts.append(f"🆕 Novas: {self.mensagens_novas}")

        if self.mensagens_urgentes > 0:
            resumo_parts.append(f"🔴 Urgentes: {self.mensagens_urgentes}")

        if self.prazos_vencidos > 0:
            resumo_parts.append(f"⏰ Prazos vencidos: {self.prazos_vencidos}")

        return " | ".join(resumo_parts)
