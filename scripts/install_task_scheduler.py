#!/usr/bin/env python3
"""
Instalador no Windows Task Scheduler - Rob-DET 2.0

Cria tarefas agendadas no Windows Task Scheduler para execução automática do robô.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from src.config_manager import get_config


def criar_tarefa_windows(
    nome_tarefa: str,
    script_path: Path,
    horario: str,
    dias_semana: list,
    descricao: str = ""
) -> bool:
    """
    Cria tarefa agendada no Windows Task Scheduler.

    Args:
        nome_tarefa: Nome da tarefa
        script_path: Caminho para o script Python
        horario: Horário no formato "HH:MM"
        dias_semana: Lista de dias (0=Segunda, 6=Domingo)
        descricao: Descrição da tarefa

    Returns:
        True se criado com sucesso
    """
    try:
        # Mapeamento de dias da semana
        dias_map = {
            0: "MON",
            1: "TUE",
            2: "WED",
            3: "THU",
            4: "FRI",
            5: "SAT",
            6: "SUN"
        }

        # Converter dias para formato do schtasks
        dias_str = ",".join([dias_map[d] for d in dias_semana if d in dias_map])

        if not dias_str:
            logger.error("Nenhum dia da semana válido")
            return False

        # Obter caminho do Python
        python_exe = sys.executable

        # Caminho completo do script
        script_abs = script_path.resolve()

        # Diretório de trabalho
        work_dir = script_abs.parent.parent

        # Comando a executar
        comando = f'"{python_exe}" "{script_abs}"'

        # XML da tarefa (mais flexível que schtasks /create)
        xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>{descricao or 'Rob-DET 2.0 - Execução Agendada'}</Description>
    <Author>{os.environ.get('USERNAME', 'Sistema')}</Author>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>{datetime.now().strftime('%Y-%m-%d')}T{horario}:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByWeek>
        <DaysOfWeek>
          {' '.join([f'<{dias_map[d]}/>' for d in dias_semana if d in dias_map])}
        </DaysOfWeek>
        <WeeksInterval>1</WeeksInterval>
      </ScheduleByWeek>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_exe}</Command>
      <Arguments>"{script_abs}"</Arguments>
      <WorkingDirectory>{work_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

        # Salvar XML temporário
        xml_temp = Path("temp_task.xml")
        with open(xml_temp, 'w', encoding='utf-16') as f:
            f.write(xml_content)

        try:
            # Deletar tarefa existente (se houver)
            os.system(f'schtasks /delete /tn "{nome_tarefa}" /f >nul 2>&1')

            # Criar tarefa a partir do XML
            result = os.system(
                f'schtasks /create /tn "{nome_tarefa}" /xml "{xml_temp}" /f'
            )

            if result == 0:
                logger.success(f"✓ Tarefa '{nome_tarefa}' criada: {dias_str} às {horario}")
                return True
            else:
                logger.error(f"Falha ao criar tarefa (código: {result})")
                return False

        finally:
            # Remover XML temporário
            if xml_temp.exists():
                xml_temp.unlink()

    except Exception as e:
        logger.error(f"Erro ao criar tarefa: {e}")
        return False


def instalar_tarefas():
    """Instala todas as tarefas configuradas no Windows Task Scheduler."""
    try:
        # Verificar se está no Windows
        if sys.platform != 'win32':
            logger.error("Este script só funciona no Windows")
            return False

        logger.info("═" * 60)
        logger.info("INSTALADOR - Windows Task Scheduler")
        logger.info("═" * 60)
        logger.info()

        # Carregar configuração
        config = get_config()

        horarios = config.execucao.horarios
        dias_semana = config.execucao.dias_semana

        # Caminho do script de execução agendada
        script_path = Path(__file__).parent / "run_scheduled.py"

        if not script_path.exists():
            logger.error(f"Script não encontrado: {script_path}")
            return False

        logger.info(f"Script: {script_path}")
        logger.info(f"Horários: {', '.join(horarios)}")
        logger.info(f"Dias: {dias_semana}")
        logger.info()

        # Criar uma tarefa para cada horário
        tarefas_criadas = 0

        for idx, horario in enumerate(horarios, 1):
            nome_tarefa = f"RobDET_Exec_{idx}_{horario.replace(':', '')}"

            descricao = (
                f"Rob-DET 2.0 - Execução automática às {horario}. "
                f"Consulta mensagens do portal DET para múltiplos clientes."
            )

            if criar_tarefa_windows(
                nome_tarefa=nome_tarefa,
                script_path=script_path,
                horario=horario,
                dias_semana=dias_semana,
                descricao=descricao
            ):
                tarefas_criadas += 1

        logger.info()
        logger.info("═" * 60)
        logger.success(f"✓ {tarefas_criadas} tarefa(s) instalada(s) com sucesso!")
        logger.info("═" * 60)
        logger.info()
        logger.info("Para gerenciar as tarefas:")
        logger.info("  1. Abra o 'Agendador de Tarefas' do Windows")
        logger.info("  2. Procure por 'RobDET_Exec_*'")
        logger.info("  3. Clique com botão direito → Propriedades para editar")
        logger.info()
        logger.info("Para desinstalar:")
        logger.info("  python scripts/uninstall_task_scheduler.py")
        logger.info()

        return tarefas_criadas > 0

    except Exception as e:
        logger.error(f"Erro durante instalação: {e}")
        logger.exception(e)
        return False


def main():
    """Função principal."""
    try:
        sucesso = instalar_tarefas()
        sys.exit(0 if sucesso else 1)

    except KeyboardInterrupt:
        logger.warning("\n🛑 Instalação cancelada")
        sys.exit(130)


if __name__ == '__main__':
    main()
