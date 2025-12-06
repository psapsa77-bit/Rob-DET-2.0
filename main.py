#!/usr/bin/env python3
"""
Rob-DET 2.0 - Robô de Automação DET (Domicílio Eletrônico Trabalhista)

Ponto de entrada principal da aplicação.
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.utils.config import load_config, ClientConfig
from src.utils.logger import setup_logging, log_step, log_success, log_warning
from src.auth.cert_manager import CertificateManager
from src.navigation.det_navigator import DETNavigator
from src.extraction.message_extractor import MessageExtractor

console = Console()


def print_banner():
    """Exibe banner da aplicação."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║                    🤖 ROB-DET 2.0                             ║
    ║                                                               ║
    ║        Robô de Automação do Portal DET                       ║
    ║        Domicílio Eletrônico Trabalhista                      ║
    ║                                                               ║
    ║        Versão: 2.0.0-alpha                                   ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def process_client(
    client: ClientConfig,
    navigator: DETNavigator,
    config: any
) -> dict:
    """
    Processa um cliente específico.

    Args:
        client: Configuração do cliente
        navigator: Navegador DET
        config: Configuração global

    Returns:
        Dicionário com resultado do processamento
    """
    result = {
        'cnpj': client.cnpj,
        'razao_social': client.razao_social,
        'success': False,
        'messages_count': 0,
        'new_messages_count': 0,
        'error': None
    }

    try:
        log_step(
            f"Processando cliente: {client.razao_social}",
            f"CNPJ: {client.cnpj} | Prioridade: {client.priority}"
        )

        # Selecionar CNPJ (se necessário)
        # TODO: Implementar seleção via procuração
        # navigator.select_cnpj(client.cnpj)

        # Navegar para Caixa Postal
        if not navigator.navigate_to_mailbox():
            result['error'] = 'Falha ao navegar para Caixa Postal'
            return result

        # Extrair mensagens
        extractor = MessageExtractor(navigator.driver)
        messages = extractor.extract_messages(only_new=config.app.debug)

        result['messages_count'] = len(messages)
        result['new_messages_count'] = sum(1 for m in messages if m.is_new())
        result['success'] = True

        log_success(
            f"Cliente {client.razao_social} processado - "
            f"{result['new_messages_count']} mensagens novas de {result['messages_count']}"
        )

        # TODO: Exportar dados, notificar, etc.

        return result

    except Exception as e:
        logger.error(f"Erro ao processar cliente {client.razao_social}: {e}")
        result['error'] = str(e)
        return result


def main(args):
    """
    Função principal da aplicação.

    Args:
        args: Argumentos da linha de comando
    """
    try:
        # Banner
        print_banner()

        # Carregar configuração
        log_step("Carregando configurações")
        config = load_config()

        # Configurar logging
        setup_logging(
            log_file=config.app.log_file if not args.no_log else None,
            log_level=config.app.log_level if not args.debug else 'DEBUG',
            console_output=True
        )

        logger.info(f"Configuração carregada: {len(config.clients)} clientes")

        # Carregar certificado digital
        log_step("Carregando certificado digital")

        try:
            cert_manager = CertificateManager(
                cert_path=config.app.cert_path,
                use_keyring=config.app.use_keyring,
                keyring_service=config.app.keyring_service
            )

            cert_info = cert_manager.get_info()
            logger.info(f"Certificado: {cert_info['subject_cn']}")
            logger.info(f"Validade: {cert_info['valid_from']} até {cert_info['valid_to']}")

        except Exception as e:
            logger.error(f"Falha ao carregar certificado: {e}")
            logger.info("\nConfigure o certificado:")
            logger.info("1. Copie o arquivo .pfx para a pasta certs/")
            logger.info("2. Configure CERT_PATH no arquivo .env")
            logger.info("3. Configure a senha usando keyring ou CERT_PASSWORD")
            return 1

        # Determinar clientes a processar
        if args.cnpj:
            # Cliente específico
            client = config.get_client_by_cnpj(args.cnpj)
            if not client:
                logger.error(f"Cliente não encontrado: {args.cnpj}")
                return 1
            clients_to_process = [client]
        else:
            # Todos os clientes ativos
            clients_to_process = config.get_active_clients()

        if not clients_to_process:
            logger.warning("Nenhum cliente ativo para processar")
            return 0

        logger.info(f"Clientes a processar: {len(clients_to_process)}")

        # Iniciar navegador
        log_step("Iniciando navegador")

        with DETNavigator(
            browser=config.app.browser,
            headless=config.app.headless and not args.no_headless,
            timeout=config.app.default_timeout
        ) as navigator:

            # Login no DET
            log_step("Realizando login no DET")

            if not navigator.login_with_certificate():
                logger.error("Falha no login")
                logger.info("\nVerifique:")
                logger.info("1. Certificado está configurado corretamente")
                logger.info("2. Auto-seleção via Registry está configurada (ou use PyWinAuto)")
                logger.info("3. Certificado é válido para o portal DET")
                return 1

            # Processar clientes
            results = []

            for i, client in enumerate(clients_to_process, 1):
                logger.info(f"\n{'=' * 60}")
                logger.info(f"Cliente {i}/{len(clients_to_process)}")
                logger.info(f"{'=' * 60}")

                result = process_client(client, navigator, config)
                results.append(result)

                # Delay entre clientes
                if i < len(clients_to_process):
                    import time
                    delay = config.get_setting('processing.action_delay', 2.0)
                    logger.info(f"Aguardando {delay}s antes do próximo cliente...")
                    time.sleep(delay)

            # Resumo final
            log_step("Resumo da Execução")

            table = Table(title="Resultados")
            table.add_column("Cliente", style="cyan")
            table.add_column("CNPJ", style="yellow")
            table.add_column("Mensagens", justify="right", style="green")
            table.add_column("Novas", justify="right", style="red")
            table.add_column("Status", justify="center")

            for result in results:
                status = "✓" if result['success'] else "✗"
                status_color = "green" if result['success'] else "red"

                table.add_row(
                    result['razao_social'],
                    result['cnpj'],
                    str(result['messages_count']),
                    str(result['new_messages_count']),
                    f"[{status_color}]{status}[/{status_color}]"
                )

            console.print(table)

            # Estatísticas gerais
            total_clients = len(results)
            successful = sum(1 for r in results if r['success'])
            total_messages = sum(r['messages_count'] for r in results)
            total_new = sum(r['new_messages_count'] for r in results)

            stats = f"""
            Clientes processados: {successful}/{total_clients}
            Total de mensagens: {total_messages}
            Mensagens novas: {total_new}
            """

            console.print(Panel(stats, title="Estatísticas", border_style="green"))

            log_success("Execução concluída!")

        return 0

    except KeyboardInterrupt:
        logger.warning("\n⚠️ Execução interrompida pelo usuário")
        return 130

    except Exception as e:
        logger.exception(f"Erro fatal: {e}")
        return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Rob-DET 2.0 - Robô de Automação DET',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--cnpj',
        help='CNPJ específico para processar (caso contrário, processa todos)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Ativar modo debug (log detalhado)'
    )

    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Forçar navegador visível (mesmo se configurado headless)'
    )

    parser.add_argument(
        '--no-log',
        action='store_true',
        help='Não salvar logs em arquivo'
    )

    parser.add_argument(
        '--only-new',
        action='store_true',
        help='Processar apenas mensagens novas'
    )

    args = parser.parse_args()

    sys.exit(main(args))
