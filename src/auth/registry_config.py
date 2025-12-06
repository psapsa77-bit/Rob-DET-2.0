"""
Configurador de Registro do Windows - Rob-DET 2.0

Configura o registro do Windows para auto-seleção de certificado digital
em Chrome e Edge, eliminando a necessidade de popup manual.

IMPORTANTE: Requer permissões de administrador para modificar o registro.
"""

import os
import sys
import json
import platform
from typing import Optional, Dict, Any
from loguru import logger

# Importar winreg apenas no Windows
if platform.system() == 'Windows':
    import winreg as reg
else:
    logger.warning("Este módulo só funciona no Windows")


class RegistryConfigurator:
    """Configurador de registro do Windows para auto-seleção de certificado."""

    # Caminhos de registro
    CHROME_POLICY_PATH = r"SOFTWARE\Policies\Google\Chrome"
    EDGE_POLICY_PATH = r"SOFTWARE\Policies\Microsoft\Edge"

    # Chave de configuração
    AUTO_SELECT_KEY = "AutoSelectCertificateForUrls"

    def __init__(self, browser: str = 'chrome'):
        """
        Inicializa configurador.

        Args:
            browser: Navegador (chrome ou edge)

        Raises:
            ValueError: Se browser não é chrome ou edge
            OSError: Se não estiver no Windows
        """
        if platform.system() != 'Windows':
            raise OSError("Configuração de registro só funciona no Windows")

        if browser not in ['chrome', 'edge']:
            raise ValueError("Browser deve ser 'chrome' ou 'edge'")

        self.browser = browser
        self.policy_path = (
            self.CHROME_POLICY_PATH if browser == 'chrome'
            else self.EDGE_POLICY_PATH
        )

        logger.info(f"Configurador de registro iniciado para {browser.upper()}")

    def _is_admin(self) -> bool:
        """
        Verifica se o script está rodando como administrador.

        Returns:
            True se administrador, False caso contrário
        """
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def configure_auto_select(
        self,
        url_pattern: str = "https://det.sit.trabalho.gov.br",
        issuer_cn: Optional[str] = None,
        subject_cn: Optional[str] = None
    ) -> bool:
        """
        Configura auto-seleção de certificado no registro.

        Args:
            url_pattern: Padrão de URL para auto-seleção
            issuer_cn: Common Name do emissor do certificado (ex: "AC SERASA RFB v5")
            subject_cn: Common Name do titular (opcional)

        Returns:
            True se configurado com sucesso, False caso contrário

        Example:
            >>> configurator = RegistryConfigurator('chrome')
            >>> configurator.configure_auto_select(
            ...     url_pattern="https://det.sit.trabalho.gov.br",
            ...     issuer_cn="AC SERASA RFB v5"
            ... )
        """
        if not self._is_admin():
            logger.error("❌ Permissões de administrador necessárias!")
            logger.info("Execute o script como administrador (Run as Administrator)")
            return False

        try:
            # Criar configuração JSON
            config = {
                "pattern": url_pattern,
                "filter": {}
            }

            # Adicionar filtro de emissor
            if issuer_cn:
                config["filter"]["ISSUER"] = {"CN": issuer_cn}

            # Adicionar filtro de titular
            if subject_cn:
                config["filter"]["SUBJECT"] = {"CN": subject_cn}

            logger.info(f"Configuração: {json.dumps(config, indent=2)}")

            # Abrir/criar chave de política
            with reg.CreateKeyEx(
                reg.HKEY_LOCAL_MACHINE,
                self.policy_path,
                0,
                reg.KEY_WRITE
            ) as policy_key:

                # Configurar valor
                json_config = json.dumps([config])  # Deve ser um array
                reg.SetValueEx(
                    policy_key,
                    self.AUTO_SELECT_KEY,
                    0,
                    reg.REG_SZ,
                    json_config
                )

                logger.success(f"✓ Registro configurado para {self.browser.upper()}")
                logger.info(f"Caminho: HKLM\\{self.policy_path}\\{self.AUTO_SELECT_KEY}")
                return True

        except PermissionError:
            logger.error("❌ Permissão negada. Execute como administrador!")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao configurar registro: {e}")
            return False

    def remove_auto_select(self) -> bool:
        """
        Remove configuração de auto-seleção do registro.

        Returns:
            True se removido com sucesso, False caso contrário
        """
        if not self._is_admin():
            logger.error("❌ Permissões de administrador necessárias!")
            return False

        try:
            with reg.OpenKey(
                reg.HKEY_LOCAL_MACHINE,
                self.policy_path,
                0,
                reg.KEY_WRITE
            ) as policy_key:
                reg.DeleteValue(policy_key, self.AUTO_SELECT_KEY)

            logger.success(f"✓ Configuração removida de {self.browser.upper()}")
            return True

        except FileNotFoundError:
            logger.warning("Configuração não existe no registro")
            return True
        except PermissionError:
            logger.error("❌ Permissão negada. Execute como administrador!")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao remover configuração: {e}")
            return False

    def get_current_config(self) -> Optional[str]:
        """
        Obtém configuração atual do registro.

        Returns:
            JSON string da configuração atual ou None se não existe
        """
        try:
            with reg.OpenKey(
                reg.HKEY_LOCAL_MACHINE,
                self.policy_path,
                0,
                reg.KEY_READ
            ) as policy_key:
                value, _ = reg.QueryValueEx(policy_key, self.AUTO_SELECT_KEY)
                return value

        except FileNotFoundError:
            logger.info("Nenhuma configuração encontrada no registro")
            return None
        except Exception as e:
            logger.error(f"Erro ao ler registro: {e}")
            return None

    def verify_configuration(self) -> bool:
        """
        Verifica se configuração está presente e válida.

        Returns:
            True se configurado corretamente, False caso contrário
        """
        config = self.get_current_config()

        if not config:
            logger.warning("❌ Auto-seleção NÃO configurada")
            return False

        try:
            # Validar JSON
            parsed = json.loads(config)
            if isinstance(parsed, list) and len(parsed) > 0:
                logger.success("✓ Auto-seleção configurada corretamente")
                logger.info(f"Configuração atual: {json.dumps(parsed, indent=2)}")
                return True
        except json.JSONDecodeError:
            logger.error("❌ Configuração inválida no registro")
            return False

        return False


def configure_for_det(
    browser: str = 'chrome',
    issuer_cn: str = "AC SERASA RFB v5"
) -> bool:
    """
    Helper function para configurar auto-seleção para o portal DET.

    Args:
        browser: Navegador (chrome ou edge)
        issuer_cn: CN do emissor do certificado

    Returns:
        True se sucesso, False caso contrário

    Example:
        >>> configure_for_det('chrome', 'AC SERASA RFB v5')
    """
    if platform.system() != 'Windows':
        logger.error("Esta função só funciona no Windows")
        return False

    configurator = RegistryConfigurator(browser)

    logger.info("=" * 60)
    logger.info("Configurando auto-seleção de certificado para DET")
    logger.info("=" * 60)

    success = configurator.configure_auto_select(
        url_pattern="https://det.sit.trabalho.gov.br",
        issuer_cn=issuer_cn
    )

    if success:
        logger.success("\n✓ Configuração concluída!")
        logger.info("\nPróximos passos:")
        logger.info("1. Feche TODOS os processos do navegador")
        logger.info("2. Abra o navegador novamente")
        logger.info("3. Acesse o portal DET")
        logger.info("4. O certificado deve ser selecionado automaticamente")
    else:
        logger.error("\n✗ Falha na configuração")
        logger.info("Execute este script como Administrador")

    return success


# Exemplo de uso
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Configurar auto-seleção de certificado')
    parser.add_argument(
        '--browser',
        choices=['chrome', 'edge'],
        default='chrome',
        help='Navegador para configurar (padrão: chrome)'
    )
    parser.add_argument(
        '--issuer',
        default='AC SERASA RFB v5',
        help='Common Name do emissor do certificado'
    )
    parser.add_argument(
        '--remove',
        action='store_true',
        help='Remover configuração existente'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verificar configuração atual'
    )

    args = parser.parse_args()

    if platform.system() != 'Windows':
        print("❌ Este script só funciona no Windows")
        sys.exit(1)

    configurator = RegistryConfigurator(args.browser)

    if args.verify:
        # Verificar configuração
        configurator.verify_configuration()

    elif args.remove:
        # Remover configuração
        if configurator.remove_auto_select():
            print("✓ Configuração removida com sucesso")
        else:
            print("✗ Falha ao remover configuração")
            sys.exit(1)

    else:
        # Configurar auto-seleção
        if not configure_for_det(args.browser, args.issuer):
            sys.exit(1)
