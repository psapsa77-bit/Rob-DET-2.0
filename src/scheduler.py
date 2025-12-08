"""
Sistema de Agendamento - Rob-DET 2.0

Gerencia execução agendada do robô em horários definidos.
"""

import schedule
import time
import signal
import sys
from typing import Callable, Optional, List
from datetime import datetime, timedelta
from loguru import logger

from src.config_manager import ConfigManager


class RobotScheduler:
    """
    Agendador de execuções do robô.

    Gerencia horários, dias da semana e execução automática.
    """

    def __init__(
        self,
        config: ConfigManager,
        funcao_execucao: Callable[[], None]
    ):
        """
        Inicializa o agendador.

        Args:
            config: Gerenciador de configurações
            funcao_execucao: Função a ser executada nos horários agendados
        """
        self.config = config
        self.funcao_execucao = funcao_execucao

        self.horarios = config.execucao.horarios
        self.dias_semana = config.execucao.dias_semana

        self._running = False
        self._setup_signal_handlers()

        logger.info("Agendador inicializado")

    def _setup_signal_handlers(self) -> None:
        """Configura handlers para sinais de interrupção."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame) -> None:
        """Handler para SIGINT e SIGTERM."""
        logger.warning(f"\n🛑 Sinal de interrupção recebido ({signum})")
        self.stop()
        sys.exit(0)

    def agendar_execucoes(self) -> None:
        """Agenda execuções conforme configuração."""
        schedule.clear()

        for horario in self.horarios:
            try:
                # Validar formato HH:MM
                hora, minuto = horario.split(':')
                hora_int = int(hora)
                minuto_int = int(minuto)

                if not (0 <= hora_int < 24 and 0 <= minuto_int < 60):
                    logger.warning(f"Horário inválido ignorado: {horario}")
                    continue

                # Agendar para cada dia da semana configurado
                for dia in self.dias_semana:
                    dia_nome = self._get_dia_nome(dia)

                    # Criar job agendado
                    job = schedule.every()

                    # Selecionar dia da semana
                    if dia == 0:
                        job = job.monday
                    elif dia == 1:
                        job = job.tuesday
                    elif dia == 2:
                        job = job.wednesday
                    elif dia == 3:
                        job = job.thursday
                    elif dia == 4:
                        job = job.friday
                    elif dia == 5:
                        job = job.saturday
                    elif dia == 6:
                        job = job.sunday

                    # Definir horário
                    job.at(horario).do(self._executar_com_log)

                    logger.info(f"✓ Agendado: {dia_nome} às {horario}")

            except ValueError as e:
                logger.error(f"Erro ao agendar horário {horario}: {e}")
                continue

        if not schedule.get_jobs():
            logger.warning("Nenhuma execução foi agendada!")
        else:
            logger.success(f"✓ {len(schedule.get_jobs())} execução(ões) agendada(s)")

    def _get_dia_nome(self, dia: int) -> str:
        """Retorna nome do dia da semana."""
        dias = {
            0: "Segunda-feira",
            1: "Terça-feira",
            2: "Quarta-feira",
            3: "Quinta-feira",
            4: "Sexta-feira",
            5: "Sábado",
            6: "Domingo"
        }
        return dias.get(dia, f"Dia {dia}")

    def _executar_com_log(self) -> None:
        """Wrapper que adiciona logs na execução agendada."""
        logger.info("━" * 60)
        logger.info(f"⏰ EXECUÇÃO AGENDADA INICIADA - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        logger.info("━" * 60)

        try:
            self.funcao_execucao()

        except Exception as e:
            logger.error(f"Erro durante execução agendada: {e}")

        finally:
            logger.info("━" * 60)
            logger.info("✓ Execução agendada finalizada")
            logger.info("━" * 60)

    def get_proxima_execucao(self) -> Optional[datetime]:
        """
        Retorna data/hora da próxima execução agendada.

        Returns:
            datetime da próxima execução ou None
        """
        jobs = schedule.get_jobs()

        if not jobs:
            return None

        # Pegar próximo job
        proximo_job = min(jobs, key=lambda j: j.next_run)
        return proximo_job.next_run

    def executar_manual(self) -> None:
        """Executa manualmente (fora do agendamento)."""
        logger.info("▶️  EXECUÇÃO MANUAL")
        self._executar_com_log()

    def start(self, bloqueante: bool = True) -> None:
        """
        Inicia o loop de agendamento.

        Args:
            bloqueante: Se True, bloqueia até interrupção
        """
        if self._running:
            logger.warning("Agendador já está rodando")
            return

        self._running = True
        logger.success("🚀 Agendador iniciado")

        proxima = self.get_proxima_execucao()
        if proxima:
            logger.info(f"⏭️  Próxima execução: {proxima.strftime('%d/%m/%Y %H:%M:%S')}")

        if bloqueante:
            self._run_loop()
        else:
            logger.info("Modo não-bloqueante: use run_pending() manualmente")

    def _run_loop(self) -> None:
        """Loop principal do agendador."""
        try:
            while self._running:
                schedule.run_pending()
                time.sleep(1)

        except KeyboardInterrupt:
            logger.warning("\n🛑 Interrompido pelo usuário")
            self.stop()

        except Exception as e:
            logger.error(f"Erro no loop do agendador: {e}")
            self.stop()

    def run_pending(self) -> None:
        """Executa jobs pendentes (para uso não-bloqueante)."""
        schedule.run_pending()

    def stop(self) -> None:
        """Para o agendador."""
        if not self._running:
            return

        self._running = False
        logger.info("⏸️  Agendador parado")

    def is_running(self) -> bool:
        """Verifica se agendador está rodando."""
        return self._running

    def listar_agendamentos(self) -> List[str]:
        """
        Lista todos os agendamentos ativos.

        Returns:
            Lista com descrição dos jobs
        """
        jobs = schedule.get_jobs()

        if not jobs:
            return ["Nenhum agendamento ativo"]

        agendamentos = []
        for job in jobs:
            agendamentos.append(
                f"{job.next_run.strftime('%A %H:%M')} "
                f"(próxima: {job.next_run.strftime('%d/%m/%Y %H:%M')})"
            )

        return agendamentos

    def cancelar_todos(self) -> None:
        """Cancela todos os agendamentos."""
        schedule.clear()
        logger.info("Todos os agendamentos foram cancelados")


class AgendadorSimples:
    """
    Agendador simplificado para uso direto.

    Útil para testes e execuções simples.
    """

    @staticmethod
    def executar_periodicamente(
        funcao: Callable[[], None],
        intervalo_minutos: int = 60
    ) -> None:
        """
        Executa função periodicamente.

        Args:
            funcao: Função a executar
            intervalo_minutos: Intervalo em minutos
        """
        schedule.every(intervalo_minutos).minutes.do(funcao)

        logger.info(f"Agendado: executar a cada {intervalo_minutos} minutos")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)

        except KeyboardInterrupt:
            logger.info("Agendamento interrompido")

    @staticmethod
    def executar_horarios(
        funcao: Callable[[], None],
        horarios: List[str]
    ) -> None:
        """
        Executa função em horários específicos todos os dias.

        Args:
            funcao: Função a executar
            horarios: Lista de horários (formato "HH:MM")
        """
        for horario in horarios:
            schedule.every().day.at(horario).do(funcao)
            logger.info(f"Agendado: todos os dias às {horario}")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)

        except KeyboardInterrupt:
            logger.info("Agendamento interrompido")


# Exemplo de uso
if __name__ == '__main__':
    from src.config_manager import get_config

    def exemplo_execucao():
        """Função de exemplo."""
        print(f"✓ Executado em {datetime.now().strftime('%H:%M:%S')}")

    # Usar agendador completo
    config = get_config()
    agendador = RobotScheduler(config, exemplo_execucao)
    agendador.agendar_execucoes()

    print("\nAgendamentos:")
    for ag in agendador.listar_agendamentos():
        print(f"  - {ag}")

    print("\nPressione Ctrl+C para parar")
    agendador.start()
