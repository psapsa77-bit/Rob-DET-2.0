#!/usr/bin/env python3
"""
Script de Execução Agendada - Rob-DET 2.0

Executa o robô de forma agendada conforme configuração em settings.json.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from src.config_manager import get_config
from src.scheduler import RobotScheduler
from main import RoboDET


def executar_robo():
    """Função chamada pelo agendador para executar o robô."""
    try:
        robo = RoboDET()
        robo.monitor.iniciar_heartbeat()

        try:
            robo.executar()
        finally:
            robo.monitor.parar_heartbeat()

    except Exception as e:
        logger.error(f"Erro na execução agendada: {e}")
        logger.exception(e)


def main():
    """Função principal do script."""
    try:
        logger.info("═" * 60)
        logger.info("ROB-DET 2.0 - Execução Agendada")
        logger.info("═" * 60)

        # Carregar configuração
        config = get_config()

        logger.info(f"Horários configurados: {', '.join(config.execucao.horarios)}")
        logger.info(f"Dias da semana: {config.execucao.dias_semana}")

        # Criar agendador
        agendador = RobotScheduler(
            config=config,
            funcao_execucao=executar_robo
        )

        # Agendar execuções
        agendador.agendar_execucoes()

        # Listar agendamentos
        logger.info("\n📅 Agendamentos ativos:")
        for agendamento in agendador.listar_agendamentos():
            logger.info(f"  • {agendamento}")

        # Iniciar loop de agendamento
        logger.info("\n⏰ Agendador em execução...")
        logger.info("Pressione Ctrl+C para parar\n")

        agendador.start(bloqueante=True)

    except KeyboardInterrupt:
        logger.info("\n🛑 Agendador interrompido pelo usuário")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Erro fatal no agendador: {e}")
        logger.exception(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
