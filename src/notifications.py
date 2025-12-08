"""
Sistema de Notificações - Rob-DET 2.0

Envia notificações por email sobre execuções do robô.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from loguru import logger

from src.config_manager import ConfigManager
from src.models import RelatorioConsulta


class EmailNotifier:
    """
    Notificador por email.

    Envia emails com resumos de execução, alertas e relatórios.
    """

    def __init__(self, config: ConfigManager):
        """
        Inicializa o notificador.

        Args:
            config: Gerenciador de configurações
        """
        self.config = config
        self.smtp_server = config.notificacoes.email_servidor
        self.smtp_port = config.notificacoes.email_porta
        self.remetente = config.notificacoes.email_remetente
        self.senha = config.notificacoes.email_senha
        self.destinatarios = config.notificacoes.email_destinatarios
        self.ativo = config.notificacoes.email_ativo

    def enviar_resumo_execucao(
        self,
        relatorios: List[RelatorioConsulta],
        tempo_total: float,
        erros: List[str] = None
    ) -> bool:
        """
        Envia email com resumo da execução.

        Args:
            relatorios: Lista de relatórios gerados
            tempo_total: Tempo total de execução em segundos
            erros: Lista de erros ocorridos

        Returns:
            True se enviado com sucesso
        """
        if not self.ativo:
            logger.debug("Notificações por email desativadas")
            return False

        if not self.destinatarios:
            logger.warning("Nenhum destinatário configurado")
            return False

        try:
            # Calcular estatísticas
            total_clientes = len(relatorios)
            clientes_sucesso = sum(1 for r in relatorios if r.sucesso)
            total_mensagens = sum(r.total_mensagens for r in relatorios)
            total_novas = sum(r.mensagens_novas for r in relatorios)
            total_urgentes = sum(r.mensagens_urgentes for r in relatorios)

            # Montar corpo do email
            assunto = f"[Rob-DET] Execução {datetime.now().strftime('%d/%m/%Y %H:%M')}"

            corpo_html = self._montar_html_resumo(
                total_clientes=total_clientes,
                clientes_sucesso=clientes_sucesso,
                total_mensagens=total_mensagens,
                total_novas=total_novas,
                total_urgentes=total_urgentes,
                tempo_total=tempo_total,
                relatorios=relatorios,
                erros=erros or []
            )

            # Enviar email
            return self._enviar_email(
                assunto=assunto,
                corpo_html=corpo_html,
                destinatarios=self.destinatarios
            )

        except Exception as e:
            logger.error(f"Erro ao enviar email de resumo: {e}")
            return False

    def enviar_alerta_mensagens_urgentes(
        self,
        relatorios: List[RelatorioConsulta]
    ) -> bool:
        """
        Envia alerta sobre mensagens urgentes encontradas.

        Args:
            relatorios: Relatórios com mensagens urgentes

        Returns:
            True se enviado com sucesso
        """
        if not self.ativo:
            return False

        # Filtrar apenas relatórios com mensagens urgentes
        com_urgentes = [r for r in relatorios if r.mensagens_urgentes > 0]

        if not com_urgentes:
            return False

        try:
            total_urgentes = sum(r.mensagens_urgentes for r in com_urgentes)

            assunto = f"🚨 [Rob-DET] {total_urgentes} Mensagem(ns) URGENTE(S) - {datetime.now().strftime('%d/%m/%Y')}"

            corpo_html = self._montar_html_urgentes(com_urgentes)

            return self._enviar_email(
                assunto=assunto,
                corpo_html=corpo_html,
                destinatarios=self.destinatarios,
                prioridade_alta=True
            )

        except Exception as e:
            logger.error(f"Erro ao enviar alerta de urgentes: {e}")
            return False

    def enviar_alerta_erro(
        self,
        titulo: str,
        mensagem: str,
        detalhes: Optional[str] = None,
        screenshot_path: Optional[Path] = None
    ) -> bool:
        """
        Envia alerta de erro crítico.

        Args:
            titulo: Título do erro
            mensagem: Mensagem de erro
            detalhes: Detalhes adicionais
            screenshot_path: Caminho para screenshot

        Returns:
            True se enviado com sucesso
        """
        if not self.ativo:
            return False

        try:
            assunto = f"❌ [Rob-DET] ERRO: {titulo}"

            corpo_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #d32f2f;">Erro no Rob-DET</h2>

                <div style="background-color: #ffebee; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #c62828; margin-top: 0;">{titulo}</h3>
                    <p style="color: #333;"><strong>Mensagem:</strong> {mensagem}</p>
                    <p style="color: #666;"><strong>Data/Hora:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>

                {f'<div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;"><pre style="margin: 0;">{detalhes}</pre></div>' if detalhes else ''}

                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="color: #999; font-size: 12px;">Rob-DET 2.0 - Robô de Automação DET</p>
            </body>
            </html>
            """

            anexos = []
            if screenshot_path and screenshot_path.exists():
                anexos.append(screenshot_path)

            return self._enviar_email(
                assunto=assunto,
                corpo_html=corpo_html,
                destinatarios=self.destinatarios,
                anexos=anexos,
                prioridade_alta=True
            )

        except Exception as e:
            logger.error(f"Erro ao enviar alerta de erro: {e}")
            return False

    def _montar_html_resumo(
        self,
        total_clientes: int,
        clientes_sucesso: int,
        total_mensagens: int,
        total_novas: int,
        total_urgentes: int,
        tempo_total: float,
        relatorios: List[RelatorioConsulta],
        erros: List[str]
    ) -> str:
        """Monta HTML do resumo de execução."""

        # Status geral
        status_cor = "#4caf50" if clientes_sucesso == total_clientes else "#ff9800"
        status_texto = "✓ Sucesso" if clientes_sucesso == total_clientes else "⚠ Parcial"

        # Tabela de clientes
        linhas_clientes = ""
        for rel in relatorios:
            status_icon = "✓" if rel.sucesso else "✗"
            status_class = "success" if rel.sucesso else "error"

            linhas_clientes += f"""
            <tr class="{status_class}">
                <td>{status_icon}</td>
                <td>{rel.razao_social}</td>
                <td>{rel.cnpj}</td>
                <td>{rel.total_mensagens}</td>
                <td><strong>{rel.mensagens_novas}</strong></td>
                <td style="color: #d32f2f;"><strong>{rel.mensagens_urgentes}</strong></td>
                <td>{rel.tempo_execucao:.1f}s</td>
            </tr>
            """

        # Seção de erros
        secao_erros = ""
        if erros:
            lista_erros = "".join(f"<li>{erro}</li>" for erro in erros)
            secao_erros = f"""
            <div style="background-color: #ffebee; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #d32f2f; margin-top: 0;">⚠ Erros Encontrados</h3>
                <ul style="color: #333;">
                    {lista_erros}
                </ul>
            </div>
            """

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: {status_cor}; color: white; padding: 20px; border-radius: 5px; }}
                .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
                .stat-box {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; flex: 1; }}
                .stat-value {{ font-size: 32px; font-weight: bold; color: #1976d2; }}
                .stat-label {{ color: #666; font-size: 14px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background-color: #1976d2; color: white; padding: 12px; text-align: left; }}
                td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                tr.success td:first-child {{ color: #4caf50; font-weight: bold; }}
                tr.error td:first-child {{ color: #d32f2f; font-weight: bold; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 style="margin: 0;">Rob-DET - Resumo de Execução</h1>
                <p style="margin: 10px 0 0 0;">
                    {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')} | {status_texto}
                </p>
            </div>

            <div class="stats">
                <div class="stat-box">
                    <div class="stat-value">{clientes_sucesso}/{total_clientes}</div>
                    <div class="stat-label">Clientes Consultados</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{total_mensagens}</div>
                    <div class="stat-label">Total de Mensagens</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{total_novas}</div>
                    <div class="stat-label">Mensagens Novas</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" style="color: #d32f2f;">{total_urgentes}</div>
                    <div class="stat-label">Mensagens Urgentes</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{tempo_total:.0f}s</div>
                    <div class="stat-label">Tempo Total</div>
                </div>
            </div>

            {secao_erros}

            <h2>Detalhes por Cliente</h2>
            <table>
                <thead>
                    <tr>
                        <th>Status</th>
                        <th>Razão Social</th>
                        <th>CNPJ</th>
                        <th>Total</th>
                        <th>Novas</th>
                        <th>Urgentes</th>
                        <th>Tempo</th>
                    </tr>
                </thead>
                <tbody>
                    {linhas_clientes}
                </tbody>
            </table>

            <div class="footer">
                <p>Rob-DET 2.0 - Robô de Automação do Portal DET</p>
                <p>Este é um email automático. Não responda.</p>
            </div>
        </body>
        </html>
        """

        return html

    def _montar_html_urgentes(self, relatorios: List[RelatorioConsulta]) -> str:
        """Monta HTML de alerta de mensagens urgentes."""

        linhas = ""
        for rel in relatorios:
            # Filtrar mensagens urgentes
            urgentes = [m for m in rel.mensagens if m.is_urgente()]

            for msg in urgentes:
                prazo_texto = msg.prazo_resposta.strftime('%d/%m/%Y') if msg.prazo_resposta else "Não informado"

                linhas += f"""
                <tr>
                    <td>{rel.razao_social}</td>
                    <td>{rel.cnpj}</td>
                    <td><strong>{msg.assunto}</strong></td>
                    <td>{msg.tipo.value}</td>
                    <td>{msg.data_envio.strftime('%d/%m/%Y')}</td>
                    <td style="color: #d32f2f;"><strong>{prazo_texto}</strong></td>
                </tr>
                """

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .alert {{ background-color: #d32f2f; color: white; padding: 20px; border-radius: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background-color: #f44336; color: white; padding: 12px; text-align: left; }}
                td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                .footer {{ margin-top: 30px; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="alert">
                <h1 style="margin: 0;">🚨 Mensagens Urgentes Detectadas</h1>
                <p style="margin: 10px 0 0 0;">{datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
            </div>

            <p style="margin: 20px 0; font-size: 16px;">
                <strong>Atenção!</strong> As seguintes mensagens requerem ação imediata:
            </p>

            <table>
                <thead>
                    <tr>
                        <th>Empresa</th>
                        <th>CNPJ</th>
                        <th>Assunto</th>
                        <th>Tipo</th>
                        <th>Data Envio</th>
                        <th>Prazo</th>
                    </tr>
                </thead>
                <tbody>
                    {linhas}
                </tbody>
            </table>

            <div class="footer">
                <p>Rob-DET 2.0 - Robô de Automação do Portal DET</p>
                <p>Este é um email automático. Não responda.</p>
            </div>
        </body>
        </html>
        """

        return html

    def _enviar_email(
        self,
        assunto: str,
        corpo_html: str,
        destinatarios: List[str],
        anexos: List[Path] = None,
        prioridade_alta: bool = False
    ) -> bool:
        """
        Envia email via SMTP.

        Args:
            assunto: Assunto do email
            corpo_html: Corpo em HTML
            destinatarios: Lista de emails destinatários
            anexos: Lista de arquivos para anexar
            prioridade_alta: Se True, marca como alta prioridade

        Returns:
            True se enviado com sucesso
        """
        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = self.remetente
            msg['To'] = ', '.join(destinatarios)
            msg['Subject'] = assunto

            if prioridade_alta:
                msg['X-Priority'] = '1'
                msg['Importance'] = 'high'

            # Adicionar corpo HTML
            msg.attach(MIMEText(corpo_html, 'html', 'utf-8'))

            # Adicionar anexos
            if anexos:
                for anexo_path in anexos:
                    if not anexo_path.exists():
                        continue

                    with open(anexo_path, 'rb') as f:
                        parte = MIMEBase('application', 'octet-stream')
                        parte.set_payload(f.read())

                    encoders.encode_base64(parte)
                    parte.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {anexo_path.name}'
                    )
                    msg.attach(parte)

            # Enviar via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.remetente, self.senha)
                server.send_message(msg)

            logger.success(f"✓ Email enviado: {assunto}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("Falha na autenticação SMTP - verifique email/senha")
            return False

        except smtplib.SMTPException as e:
            logger.error(f"Erro SMTP: {e}")
            return False

        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False


# Exemplo de uso
if __name__ == '__main__':
    from src.config_manager import get_config

    config = get_config()
    notifier = EmailNotifier(config)

    # Teste
    print(f"Email ativo: {notifier.ativo}")
    print(f"Destinatários: {notifier.destinatarios}")
