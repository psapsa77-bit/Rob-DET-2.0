"""
Geradores de Relatórios - Rob-DET 2.0

Exporta dados de consultas em diferentes formatos.
"""

import json
import csv
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

from loguru import logger
import pandas as pd

from src.models import RelatorioConsulta, Mensagem


class ReportGenerator(ABC):
    """Classe base para geradores de relatórios."""

    def __init__(self, output_dir: str = "./data/exports"):
        """
        Inicializa gerador de relatórios.

        Args:
            output_dir: Diretório de saída
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def gerar(
        self,
        relatorios: List[RelatorioConsulta],
        filename: Optional[str] = None
    ) -> str:
        """
        Gera relatório.

        Args:
            relatorios: Lista de relatórios
            filename: Nome do arquivo (sem extensão)

        Returns:
            Caminho do arquivo gerado
        """
        pass

    def _gerar_nome_arquivo(self, prefixo: str, extensao: str) -> str:
        """
        Gera nome de arquivo com timestamp.

        Args:
            prefixo: Prefixo do arquivo
            extensao: Extensão (com ponto)

        Returns:
            Nome do arquivo
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefixo}_{timestamp}{extensao}"


class ExcelReportGenerator(ReportGenerator):
    """Gerador de relatórios em Excel."""

    def gerar(
        self,
        relatorios: List[RelatorioConsulta],
        filename: Optional[str] = None
    ) -> str:
        """
        Gera relatório em Excel com múltiplas abas.

        Args:
            relatorios: Lista de relatórios
            filename: Nome do arquivo (sem extensão)

        Returns:
            Caminho do arquivo Excel gerado
        """
        if not filename:
            filename = self._gerar_nome_arquivo("relatorio_det", ".xlsx")
        else:
            filename = f"{filename}.xlsx"

        filepath = self.output_dir / filename

        logger.info(f"Gerando relatório Excel: {filepath}")

        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Aba 1: Resumo geral
                self._criar_aba_resumo(writer, relatorios)

                # Aba 2: Todas as mensagens
                self._criar_aba_mensagens(writer, relatorios)

                # Aba 3: Apenas mensagens novas
                self._criar_aba_mensagens_novas(writer, relatorios)

                # Aba 4: Mensagens urgentes
                self._criar_aba_mensagens_urgentes(writer, relatorios)

                # Aba 5: Estatísticas por cliente
                self._criar_aba_estatisticas(writer, relatorios)

            logger.success(f"✓ Relatório Excel gerado: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Erro ao gerar relatório Excel: {e}")
            raise

    def _criar_aba_resumo(self, writer: pd.ExcelWriter, relatorios: List[RelatorioConsulta]):
        """Cria aba de resumo geral."""
        dados = []

        for rel in relatorios:
            dados.append({
                'Data Consulta': rel.data_consulta.strftime("%d/%m/%Y %H:%M"),
                'CNPJ': rel.cnpj,
                'Razão Social': rel.razao_social,
                'Status': '✓ Sucesso' if rel.sucesso else '✗ Erro',
                'Total Mensagens': rel.total_mensagens,
                'Mensagens Novas': rel.mensagens_novas,
                'Mensagens Urgentes': rel.mensagens_urgentes,
                'Com Prazo': rel.mensagens_com_prazo,
                'Prazos Vencidos': rel.prazos_vencidos,
                'Tempo (s)': f"{rel.tempo_execucao:.2f}",
                'Erro': rel.erro or ''
            })

        df = pd.DataFrame(dados)
        df.to_excel(writer, sheet_name='Resumo', index=False)

        # Formatar
        worksheet = writer.sheets['Resumo']
        worksheet.column_dimensions['A'].width = 18
        worksheet.column_dimensions['B'].width = 20
        worksheet.column_dimensions['C'].width = 35
        worksheet.column_dimensions['L'].width = 40

    def _criar_aba_mensagens(self, writer: pd.ExcelWriter, relatorios: List[RelatorioConsulta]):
        """Cria aba com todas as mensagens."""
        dados = []

        for rel in relatorios:
            for msg in rel.mensagens:
                dados.append({
                    'CNPJ Destinatário': msg.cnpj_destinatario,
                    'Razão Social': rel.razao_social,
                    'Data Envio': msg.data_envio.strftime("%d/%m/%Y"),
                    'Remetente': msg.remetente,
                    'Assunto': msg.assunto,
                    'Tipo': msg.tipo.value,
                    'Status': msg.status.value,
                    'Prioridade': msg.prioridade.value,
                    'Urgente': '🔴 Sim' if msg.is_urgente() else 'Não',
                    'Prazo Resposta': msg.prazo_resposta.strftime("%d/%m/%Y") if msg.prazo_resposta else '',
                    'Prazo Vencido': '⏰ Sim' if msg.has_prazo_vencido() else 'Não',
                    'Anexo': 'Sim' if msg.possui_anexo else 'Não',
                    'URL': msg.url_detalhes or ''
                })

        if dados:
            df = pd.DataFrame(dados)
            df.to_excel(writer, sheet_name='Todas Mensagens', index=False)

            # Formatar
            worksheet = writer.sheets['Todas Mensagens']
            worksheet.column_dimensions['A'].width = 20
            worksheet.column_dimensions['B'].width = 35
            worksheet.column_dimensions['E'].width = 50
        else:
            # Criar aba vazia
            pd.DataFrame({'Info': ['Nenhuma mensagem encontrada']}).to_excel(
                writer, sheet_name='Todas Mensagens', index=False
            )

    def _criar_aba_mensagens_novas(self, writer: pd.ExcelWriter, relatorios: List[RelatorioConsulta]):
        """Cria aba com mensagens novas (não lidas)."""
        dados = []

        for rel in relatorios:
            for msg in rel.mensagens:
                if msg.is_nova():
                    dados.append({
                        'CNPJ': msg.cnpj_destinatario,
                        'Empresa': rel.razao_social,
                        'Data': msg.data_envio.strftime("%d/%m/%Y"),
                        'Remetente': msg.remetente,
                        'Assunto': msg.assunto,
                        'Tipo': msg.tipo.value,
                        'Urgente': '🔴' if msg.is_urgente() else '',
                        'Prazo': msg.prazo_resposta.strftime("%d/%m/%Y") if msg.prazo_resposta else ''
                    })

        if dados:
            df = pd.DataFrame(dados)
            df.to_excel(writer, sheet_name='Mensagens Novas', index=False)
        else:
            pd.DataFrame({'Info': ['Nenhuma mensagem nova']}).to_excel(
                writer, sheet_name='Mensagens Novas', index=False
            )

    def _criar_aba_mensagens_urgentes(self, writer: pd.ExcelWriter, relatorios: List[RelatorioConsulta]):
        """Cria aba com mensagens urgentes."""
        dados = []

        for rel in relatorios:
            for msg in rel.mensagens:
                if msg.is_urgente():
                    dados.append({
                        'CNPJ': msg.cnpj_destinatario,
                        'Empresa': rel.razao_social,
                        'Data': msg.data_envio.strftime("%d/%m/%Y"),
                        'Tipo': msg.tipo.value,
                        'Assunto': msg.assunto,
                        'Prazo': msg.prazo_resposta.strftime("%d/%m/%Y") if msg.prazo_resposta else 'N/A',
                        'Vencido': '⏰' if msg.has_prazo_vencido() else '',
                        'Status': msg.status.value
                    })

        if dados:
            df = pd.DataFrame(dados)
            df.to_excel(writer, sheet_name='Urgentes', index=False)
        else:
            pd.DataFrame({'Info': ['Nenhuma mensagem urgente']}).to_excel(
                writer, sheet_name='Urgentes', index=False
            )

    def _criar_aba_estatisticas(self, writer: pd.ExcelWriter, relatorios: List[RelatorioConsulta]):
        """Cria aba com estatísticas por cliente."""
        dados = []

        for rel in relatorios:
            # Contar por tipo
            tipos_count = {}
            for msg in rel.mensagens:
                tipo = msg.tipo.value
                tipos_count[tipo] = tipos_count.get(tipo, 0) + 1

            dados.append({
                'CNPJ': rel.cnpj,
                'Razão Social': rel.razao_social,
                'Total': rel.total_mensagens,
                'Novas': rel.mensagens_novas,
                'Urgentes': rel.mensagens_urgentes,
                'Autuações': tipos_count.get('Autuação', 0),
                'Intimações': tipos_count.get('Intimação', 0),
                'Notificações': tipos_count.get('Notificação', 0),
                'Comunicados': tipos_count.get('Comunicado', 0),
                'Outros': tipos_count.get('Outro', 0),
                'Última Consulta': rel.data_consulta.strftime("%d/%m/%Y %H:%M")
            })

        df = pd.DataFrame(dados)
        df.to_excel(writer, sheet_name='Estatísticas', index=False)


class CSVReportGenerator(ReportGenerator):
    """Gerador de relatórios em CSV."""

    def gerar(
        self,
        relatorios: List[RelatorioConsulta],
        filename: Optional[str] = None
    ) -> str:
        """
        Gera relatório em CSV.

        Args:
            relatorios: Lista de relatórios
            filename: Nome do arquivo (sem extensão)

        Returns:
            Caminho do arquivo CSV gerado
        """
        if not filename:
            filename = self._gerar_nome_arquivo("relatorio_det", ".csv")
        else:
            filename = f"{filename}.csv"

        filepath = self.output_dir / filename

        logger.info(f"Gerando relatório CSV: {filepath}")

        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    'CNPJ', 'Razão Social', 'Data Envio', 'Remetente',
                    'Assunto', 'Tipo', 'Status', 'Urgente', 'Prazo Resposta'
                ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()

                for rel in relatorios:
                    for msg in rel.mensagens:
                        writer.writerow({
                            'CNPJ': msg.cnpj_destinatario,
                            'Razão Social': rel.razao_social,
                            'Data Envio': msg.data_envio.strftime("%d/%m/%Y"),
                            'Remetente': msg.remetente,
                            'Assunto': msg.assunto,
                            'Tipo': msg.tipo.value,
                            'Status': msg.status.value,
                            'Urgente': 'Sim' if msg.is_urgente() else 'Não',
                            'Prazo Resposta': msg.prazo_resposta.strftime("%d/%m/%Y") if msg.prazo_resposta else ''
                        })

            logger.success(f"✓ Relatório CSV gerado: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Erro ao gerar relatório CSV: {e}")
            raise


class JSONReportGenerator(ReportGenerator):
    """Gerador de relatórios em JSON."""

    def gerar(
        self,
        relatorios: List[RelatorioConsulta],
        filename: Optional[str] = None
    ) -> str:
        """
        Gera relatório em JSON.

        Args:
            relatorios: Lista de relatórios
            filename: Nome do arquivo (sem extensão)

        Returns:
            Caminho do arquivo JSON gerado
        """
        if not filename:
            filename = self._gerar_nome_arquivo("relatorio_det", ".json")
        else:
            filename = f"{filename}.json"

        filepath = self.output_dir / filename

        logger.info(f"Gerando relatório JSON: {filepath}")

        try:
            dados = {
                'data_geracao': datetime.now().isoformat(),
                'total_clientes': len(relatorios),
                'total_mensagens': sum(r.total_mensagens for r in relatorios),
                'total_novas': sum(r.mensagens_novas for r in relatorios),
                'total_urgentes': sum(r.mensagens_urgentes for r in relatorios),
                'relatorios': [r.to_dict() for r in relatorios]
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)

            logger.success(f"✓ Relatório JSON gerado: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Erro ao gerar relatório JSON: {e}")
            raise


# Função helper
def gerar_relatorio(
    relatorios: List[RelatorioConsulta],
    formato: str = 'excel',
    output_dir: str = "./data/exports",
    filename: Optional[str] = None
) -> str:
    """
    Gera relatório no formato especificado.

    Args:
        relatorios: Lista de relatórios
        formato: Formato (excel, csv, json)
        output_dir: Diretório de saída
        filename: Nome do arquivo (sem extensão)

    Returns:
        Caminho do arquivo gerado

    Example:
        >>> relatorios = [...]
        >>> filepath = gerar_relatorio(relatorios, formato='excel')
    """
    generators = {
        'excel': ExcelReportGenerator,
        'csv': CSVReportGenerator,
        'json': JSONReportGenerator
    }

    if formato not in generators:
        raise ValueError(f"Formato inválido: {formato}. Opções: {list(generators.keys())}")

    generator = generators[formato](output_dir=output_dir)
    return generator.gerar(relatorios, filename=filename)
