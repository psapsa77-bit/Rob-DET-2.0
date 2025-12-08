"""
Sistema de Monitoramento - Rob-DET 2.0

Monitora execução, heartbeat e coleta métricas de performance.
"""

import json
import threading
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from loguru import logger

from src.config_manager import ConfigManager
from src.models import RelatorioConsulta


@dataclass
class Metrica:
    """Métrica de uma execução."""
    timestamp: str
    total_clientes: int
    clientes_sucesso: int
    clientes_falha: int
    taxa_sucesso: float
    total_mensagens: int
    mensagens_novas: int
    mensagens_urgentes: int
    tempo_total_segundos: float
    tempo_medio_por_cliente: float
    erros: List[str]


@dataclass
class Heartbeat:
    """Heartbeat do robô."""
    timestamp: str
    status: str  # "running", "idle", "error"
    ultima_execucao: Optional[str]
    proxima_execucao: Optional[str]
    versao: str = "2.0"


class Monitor:
    """
    Monitor de execução e performance do robô.

    Registra métricas, heartbeat e alertas.
    """

    def __init__(self, config: ConfigManager):
        """
        Inicializa o monitor.

        Args:
            config: Gerenciador de configurações
        """
        self.config = config
        self.heartbeat_ativo = config.monitoramento.heartbeat_ativo
        self.heartbeat_intervalo = config.monitoramento.heartbeat_intervalo_segundos
        self.heartbeat_arquivo = Path(config.monitoramento.heartbeat_arquivo)
        self.metricas_arquivo = Path(config.monitoramento.metricas_arquivo)

        # Thread de heartbeat
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._heartbeat_running = False

        # Status atual
        self._status = "idle"
        self._ultima_execucao: Optional[datetime] = None
        self._proxima_execucao: Optional[datetime] = None

        # Histórico de métricas (em memória)
        self._historico_metricas: List[Metrica] = []

        logger.info("Monitor inicializado")

    def iniciar_heartbeat(self) -> None:
        """Inicia thread de heartbeat."""
        if not self.heartbeat_ativo:
            logger.debug("Heartbeat desativado")
            return

        if self._heartbeat_running:
            logger.warning("Heartbeat já está rodando")
            return

        self._heartbeat_running = True
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True,
            name="HeartbeatThread"
        )
        self._heartbeat_thread.start()
        logger.info("✓ Heartbeat iniciado")

    def parar_heartbeat(self) -> None:
        """Para thread de heartbeat."""
        if not self._heartbeat_running:
            return

        self._heartbeat_running = False
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=5)

        logger.info("Heartbeat parado")

    def _heartbeat_loop(self) -> None:
        """Loop de heartbeat (roda em thread separada)."""
        while self._heartbeat_running:
            try:
                self._atualizar_heartbeat()
                time.sleep(self.heartbeat_intervalo)
            except Exception as e:
                logger.error(f"Erro no heartbeat: {e}")
                time.sleep(60)  # Esperar 1 minuto em caso de erro

    def _atualizar_heartbeat(self) -> None:
        """Atualiza arquivo de heartbeat."""
        try:
            heartbeat = Heartbeat(
                timestamp=datetime.now().isoformat(),
                status=self._status,
                ultima_execucao=self._ultima_execucao.isoformat() if self._ultima_execucao else None,
                proxima_execucao=self._proxima_execucao.isoformat() if self._proxima_execucao else None
            )

            # Criar diretório se não existir
            self.heartbeat_arquivo.parent.mkdir(parents=True, exist_ok=True)

            # Salvar JSON
            with open(self.heartbeat_arquivo, 'w', encoding='utf-8') as f:
                json.dump(asdict(heartbeat), f, indent=2, ensure_ascii=False)

            logger.debug(f"Heartbeat atualizado: {self._status}")

        except Exception as e:
            logger.error(f"Erro ao atualizar heartbeat: {e}")

    def set_status(self, status: str) -> None:
        """
        Define status atual do robô.

        Args:
            status: "running", "idle", "error"
        """
        self._status = status
        logger.debug(f"Status alterado: {status}")

    def set_proxima_execucao(self, proxima: datetime) -> None:
        """
        Define próxima execução agendada.

        Args:
            proxima: Data/hora da próxima execução
        """
        self._proxima_execucao = proxima

    def registrar_execucao(
        self,
        relatorios: List[RelatorioConsulta],
        tempo_total: float,
        erros: List[str] = None
    ) -> Metrica:
        """
        Registra métricas de uma execução.

        Args:
            relatorios: Relatórios gerados
            tempo_total: Tempo total em segundos
            erros: Lista de erros ocorridos

        Returns:
            Métrica registrada
        """
        try:
            # Calcular estatísticas
            total_clientes = len(relatorios)
            clientes_sucesso = sum(1 for r in relatorios if r.sucesso)
            clientes_falha = total_clientes - clientes_sucesso
            taxa_sucesso = clientes_sucesso / total_clientes if total_clientes > 0 else 0.0

            total_mensagens = sum(r.total_mensagens for r in relatorios)
            mensagens_novas = sum(r.mensagens_novas for r in relatorios)
            mensagens_urgentes = sum(r.mensagens_urgentes for r in relatorios)

            tempo_medio = tempo_total / total_clientes if total_clientes > 0 else 0.0

            # Criar métrica
            metrica = Metrica(
                timestamp=datetime.now().isoformat(),
                total_clientes=total_clientes,
                clientes_sucesso=clientes_sucesso,
                clientes_falha=clientes_falha,
                taxa_sucesso=taxa_sucesso,
                total_mensagens=total_mensagens,
                mensagens_novas=mensagens_novas,
                mensagens_urgentes=mensagens_urgentes,
                tempo_total_segundos=tempo_total,
                tempo_medio_por_cliente=tempo_medio,
                erros=erros or []
            )

            # Adicionar ao histórico
            self._historico_metricas.append(metrica)

            # Salvar em arquivo
            self._salvar_metrica(metrica)

            # Atualizar última execução
            self._ultima_execucao = datetime.now()

            # Verificar alertas
            self._verificar_alertas(metrica)

            logger.info(
                f"Métrica registrada: {clientes_sucesso}/{total_clientes} clientes, "
                f"{mensagens_novas} novas, {tempo_total:.1f}s"
            )

            return metrica

        except Exception as e:
            logger.error(f"Erro ao registrar métrica: {e}")
            raise

    def _salvar_metrica(self, metrica: Metrica) -> None:
        """Salva métrica em arquivo JSON."""
        try:
            # Criar diretório se não existir
            self.metricas_arquivo.parent.mkdir(parents=True, exist_ok=True)

            # Carregar métricas existentes
            metricas_existentes = []
            if self.metricas_arquivo.exists():
                with open(self.metricas_arquivo, 'r', encoding='utf-8') as f:
                    metricas_existentes = json.load(f)

            # Adicionar nova métrica
            metricas_existentes.append(asdict(metrica))

            # Manter apenas últimas 1000 métricas
            if len(metricas_existentes) > 1000:
                metricas_existentes = metricas_existentes[-1000:]

            # Salvar
            with open(self.metricas_arquivo, 'w', encoding='utf-8') as f:
                json.dump(metricas_existentes, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Erro ao salvar métrica: {e}")

    def _verificar_alertas(self, metrica: Metrica) -> None:
        """Verifica se métricas atingem limiares de alerta."""
        try:
            # Alerta: Taxa de falha alta
            if metrica.taxa_sucesso < (1 - self.config.monitoramento.alerta_taxa_falha_acima):
                logger.warning(
                    f"⚠️  ALERTA: Taxa de sucesso baixa ({metrica.taxa_sucesso:.1%}) - "
                    f"{metrica.clientes_falha} de {metrica.total_clientes} falharam"
                )

            # Alerta: Tempo de execução alto
            if metrica.tempo_total_segundos > self.config.monitoramento.alerta_tempo_execucao_acima:
                logger.warning(
                    f"⚠️  ALERTA: Tempo de execução alto ({metrica.tempo_total_segundos:.0f}s) - "
                    f"limite: {self.config.monitoramento.alerta_tempo_execucao_acima}s"
                )

            # Alerta: Muitos erros
            if len(metrica.erros) > 5:
                logger.warning(
                    f"⚠️  ALERTA: {len(metrica.erros)} erros encontrados durante execução"
                )

        except Exception as e:
            logger.error(f"Erro ao verificar alertas: {e}")

    def get_estatisticas_periodo(
        self,
        dias: int = 7
    ) -> Dict[str, Any]:
        """
        Obtém estatísticas de um período.

        Args:
            dias: Número de dias para análise

        Returns:
            Dicionário com estatísticas
        """
        try:
            # Carregar métricas do arquivo
            if not self.metricas_arquivo.exists():
                return {}

            with open(self.metricas_arquivo, 'r', encoding='utf-8') as f:
                todas_metricas = json.load(f)

            # Filtrar por período
            data_limite = datetime.now() - timedelta(days=dias)
            metricas_periodo = [
                m for m in todas_metricas
                if datetime.fromisoformat(m['timestamp']) >= data_limite
            ]

            if not metricas_periodo:
                return {}

            # Calcular estatísticas
            total_execucoes = len(metricas_periodo)
            total_clientes = sum(m['total_clientes'] for m in metricas_periodo)
            total_sucesso = sum(m['clientes_sucesso'] for m in metricas_periodo)
            total_mensagens = sum(m['total_mensagens'] for m in metricas_periodo)
            total_novas = sum(m['mensagens_novas'] for m in metricas_periodo)
            total_urgentes = sum(m['mensagens_urgentes'] for m in metricas_periodo)

            taxa_sucesso_media = total_sucesso / total_clientes if total_clientes > 0 else 0.0
            tempo_total = sum(m['tempo_total_segundos'] for m in metricas_periodo)
            tempo_medio_execucao = tempo_total / total_execucoes if total_execucoes > 0 else 0.0

            return {
                'periodo_dias': dias,
                'total_execucoes': total_execucoes,
                'total_clientes_consultados': total_clientes,
                'taxa_sucesso_media': taxa_sucesso_media,
                'total_mensagens': total_mensagens,
                'total_mensagens_novas': total_novas,
                'total_mensagens_urgentes': total_urgentes,
                'tempo_total_segundos': tempo_total,
                'tempo_medio_execucao_segundos': tempo_medio_execucao,
                'media_mensagens_por_execucao': total_mensagens / total_execucoes if total_execucoes > 0 else 0,
            }

        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return {}

    def gerar_relatorio_performance(self) -> str:
        """
        Gera relatório de performance em texto.

        Returns:
            Relatório formatado
        """
        try:
            stats_7d = self.get_estatisticas_periodo(7)
            stats_30d = self.get_estatisticas_periodo(30)

            if not stats_7d:
                return "Nenhuma métrica disponível"

            relatorio = f"""
╔═══════════════════════════════════════════════════════════╗
║         RELATÓRIO DE PERFORMANCE - ROB-DET 2.0            ║
╚═══════════════════════════════════════════════════════════╝

📊 ÚLTIMOS 7 DIAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Execuções:              {stats_7d['total_execucoes']}
  Clientes consultados:   {stats_7d['total_clientes_consultados']}
  Taxa de sucesso:        {stats_7d['taxa_sucesso_media']:.1%}
  Total de mensagens:     {stats_7d['total_mensagens']}
  Mensagens novas:        {stats_7d['total_mensagens_novas']}
  Mensagens urgentes:     {stats_7d['total_mensagens_urgentes']}
  Tempo médio/execução:   {stats_7d['tempo_medio_execucao_segundos']:.1f}s
  Média msg/execução:     {stats_7d['media_mensagens_por_execucao']:.1f}
"""

            if stats_30d:
                relatorio += f"""
📊 ÚLTIMOS 30 DIAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Execuções:              {stats_30d['total_execucoes']}
  Clientes consultados:   {stats_30d['total_clientes_consultados']}
  Taxa de sucesso:        {stats_30d['taxa_sucesso_media']:.1%}
  Total de mensagens:     {stats_30d['total_mensagens']}
  Mensagens novas:        {stats_30d['total_mensagens_novas']}
  Mensagens urgentes:     {stats_30d['total_mensagens_urgentes']}
  Tempo médio/execução:   {stats_30d['tempo_medio_execucao_segundos']:.1f}s
"""

            # Status atual
            relatorio += f"""
🔄 STATUS ATUAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Status:                 {self._status.upper()}
  Última execução:        {self._ultima_execucao.strftime('%d/%m/%Y %H:%M:%S') if self._ultima_execucao else 'Nunca'}
  Próxima execução:       {self._proxima_execucao.strftime('%d/%m/%Y %H:%M:%S') if self._proxima_execucao else 'Não agendada'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

            return relatorio

        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return f"Erro ao gerar relatório: {e}"


# Exemplo de uso
if __name__ == '__main__':
    from src.config_manager import get_config

    config = get_config()
    monitor = Monitor(config)

    # Iniciar heartbeat
    monitor.iniciar_heartbeat()
    monitor.set_status("running")

    # Simular execução
    time.sleep(5)

    # Parar
    monitor.set_status("idle")
    monitor.parar_heartbeat()

    # Ver estatísticas
    print(monitor.gerar_relatorio_performance())
