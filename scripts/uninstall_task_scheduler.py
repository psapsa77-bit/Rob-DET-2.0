#!/usr/bin/env python3
"""
Desinstalador do Windows Task Scheduler - Rob-DET 2.0

Remove todas as tarefas do Rob-DET do Windows Task Scheduler.
"""

import sys
import os
from loguru import logger


def desinstalar_tarefas():
    """Remove todas as tarefas do Rob-DET do Task Scheduler."""
    try:
        # Verificar se está no Windows
        if sys.platform != 'win32':
            logger.error("Este script só funciona no Windows")
            return False

        logger.info("═" * 60)
        logger.info("DESINSTALADOR - Windows Task Scheduler")
        logger.info("═" * 60)
        logger.info()

        logger.info("Removendo tarefas do Rob-DET...")

        # Listar tarefas existentes
        result = os.popen('schtasks /query /fo LIST /v | findstr /C:"RobDET_"').read()

        if not result.strip():
            logger.warning("Nenhuma tarefa do Rob-DET encontrada")
            return True

        # Contar tarefas
        tarefas = [linha for linha in result.split('\n') if 'RobDET_' in linha]
        total_tarefas = len(tarefas)

        logger.info(f"Encontradas {total_tarefas} tarefa(s)")

        # Deletar todas as tarefas que começam com RobDET_
        result_code = os.system('schtasks /delete /tn "RobDET_*" /f')

        if result_code == 0:
            logger.success(f"✓ {total_tarefas} tarefa(s) removida(s) com sucesso!")
            return True
        else:
            logger.error("Falha ao remover tarefas")
            return False

    except Exception as e:
        logger.error(f"Erro durante desinstalação: {e}")
        return False


def main():
    """Função principal."""
    try:
        sucesso = desinstalar_tarefas()
        sys.exit(0 if sucesso else 1)

    except KeyboardInterrupt:
        logger.warning("\n🛑 Desinstalação cancelada")
        sys.exit(130)


if __name__ == '__main__':
    main()
