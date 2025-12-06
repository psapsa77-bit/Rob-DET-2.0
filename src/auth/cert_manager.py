"""
Gerenciador de Certificados Digitais - Rob-DET 2.0

Gerencia certificados digitais A1 (.pfx) para autenticação no portal DET:
- Carregamento e validação de certificados
- Extração de informações (titular, validade, etc.)
- Gerenciamento seguro de senhas via keyring
- Auto-seleção de certificado (Registry ou PyWinAuto)
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import keyring
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from loguru import logger


class CertificateManager:
    """Gerenciador de certificados digitais A1."""

    def __init__(
        self,
        cert_path: str,
        password: Optional[str] = None,
        use_keyring: bool = True,
        keyring_service: str = 'det_robot'
    ):
        """
        Inicializa o gerenciador de certificados.

        Args:
            cert_path: Caminho para o arquivo .pfx
            password: Senha do certificado (se None, tenta keyring)
            use_keyring: Se True, usa keyring do sistema para senha
            keyring_service: Nome do serviço no keyring

        Raises:
            FileNotFoundError: Se certificado não existe
            ValueError: Se senha está incorreta
        """
        self.cert_path = Path(cert_path)
        self.use_keyring = use_keyring
        self.keyring_service = keyring_service

        # Verificar se arquivo existe
        if not self.cert_path.exists():
            raise FileNotFoundError(f"Certificado não encontrado: {cert_path}")

        # Obter senha
        self.password = self._get_password(password)

        # Carregar certificado
        self.certificate = None
        self.private_key = None
        self.cert_info: Dict[str, Any] = {}

        self._load_certificate()

    def _get_password(self, password: Optional[str]) -> str:
        """
        Obtém senha do certificado (de parâmetro ou keyring).

        Args:
            password: Senha fornecida diretamente

        Returns:
            Senha do certificado

        Raises:
            ValueError: Se senha não foi fornecida e não está no keyring
        """
        if password:
            logger.info("Usando senha fornecida diretamente")
            return password

        if self.use_keyring:
            logger.info(f"Buscando senha no keyring (serviço: {self.keyring_service})")
            stored_password = keyring.get_password(self.keyring_service, 'cert_password')

            if stored_password:
                logger.success("Senha recuperada do keyring")
                return stored_password
            else:
                logger.warning("Senha não encontrada no keyring")

        raise ValueError(
            "Senha do certificado não fornecida. "
            "Configure CERT_PASSWORD no .env ou salve no keyring."
        )

    def save_password_to_keyring(self, password: str) -> None:
        """
        Salva senha no keyring do sistema.

        Args:
            password: Senha a ser salva

        Example:
            >>> cert_mgr = CertificateManager('cert.pfx', password='minha_senha')
            >>> cert_mgr.save_password_to_keyring('minha_senha')
        """
        keyring.set_password(self.keyring_service, 'cert_password', password)
        logger.success(f"Senha salva no keyring (serviço: {self.keyring_service})")

    def _load_certificate(self) -> None:
        """
        Carrega o certificado .pfx e extrai informações.

        Raises:
            ValueError: Se não foi possível carregar o certificado
        """
        try:
            logger.info(f"Carregando certificado: {self.cert_path}")

            # Ler arquivo .pfx
            with open(self.cert_path, 'rb') as f:
                pfx_data = f.read()

            # Carregar certificado com senha
            private_key, certificate, additional_certs = serialization.pkcs12.load_key_and_certificates(
                pfx_data,
                self.password.encode(),
                backend=default_backend()
            )

            self.private_key = private_key
            self.certificate = certificate

            # Extrair informações do certificado
            self._extract_certificate_info()

            logger.success(f"Certificado carregado: {self.cert_info['subject_cn']}")
            logger.info(f"Validade: {self.cert_info['valid_from']} até {self.cert_info['valid_to']}")

            # Verificar validade
            self._check_validity()

        except ValueError as e:
            logger.error("Senha do certificado incorreta ou certificado inválido")
            raise ValueError(f"Falha ao carregar certificado: {e}")
        except Exception as e:
            logger.error(f"Erro ao carregar certificado: {e}")
            raise

    def _extract_certificate_info(self) -> None:
        """Extrai informações do certificado."""
        if not self.certificate:
            return

        # Subject
        subject = self.certificate.subject
        subject_cn = subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value

        # Issuer
        issuer = self.certificate.issuer
        issuer_cn = issuer.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value

        # Datas de validade
        valid_from = self.certificate.not_valid_before_utc
        valid_to = self.certificate.not_valid_after_utc

        # Serial number
        serial_number = self.certificate.serial_number

        self.cert_info = {
            'subject_cn': subject_cn,
            'issuer_cn': issuer_cn,
            'valid_from': valid_from.strftime('%d/%m/%Y'),
            'valid_to': valid_to.strftime('%d/%m/%Y'),
            'serial_number': serial_number,
            'is_valid': self._is_certificate_valid(),
        }

    def _is_certificate_valid(self) -> bool:
        """
        Verifica se certificado está dentro do período de validade.

        Returns:
            True se válido, False se expirado
        """
        if not self.certificate:
            return False

        now = datetime.now(self.certificate.not_valid_after_utc.tzinfo)
        return self.certificate.not_valid_before_utc <= now <= self.certificate.not_valid_after_utc

    def _check_validity(self) -> None:
        """Verifica e avisa sobre validade do certificado."""
        if not self.cert_info['is_valid']:
            logger.error("⚠️ CERTIFICADO EXPIRADO!")
            logger.error(f"Válido até: {self.cert_info['valid_to']}")
            raise ValueError("Certificado digital expirado")

        # Calcular dias até expiração
        valid_to = datetime.strptime(self.cert_info['valid_to'], '%d/%m/%Y')
        days_until_expiry = (valid_to - datetime.now()).days

        if days_until_expiry <= 30:
            logger.warning(f"⚠️ Certificado expira em {days_until_expiry} dias!")
        elif days_until_expiry <= 60:
            logger.info(f"Certificado expira em {days_until_expiry} dias")

    def get_info(self) -> Dict[str, Any]:
        """
        Retorna informações do certificado.

        Returns:
            Dicionário com informações do certificado

        Example:
            >>> info = cert_mgr.get_info()
            >>> print(info['subject_cn'])
            EMPRESA EXEMPLO LTDA:12345678000190
        """
        return self.cert_info.copy()

    def get_certificate_path(self) -> str:
        """
        Retorna caminho absoluto do certificado.

        Returns:
            Caminho do certificado
        """
        return str(self.cert_path.absolute())

    def __repr__(self) -> str:
        """Representação string do gerenciador."""
        if self.cert_info:
            return (
                f"CertificateManager(\n"
                f"  Titular: {self.cert_info['subject_cn']}\n"
                f"  Emissor: {self.cert_info['issuer_cn']}\n"
                f"  Válido: {self.cert_info['valid_from']} até {self.cert_info['valid_to']}\n"
                f"  Status: {'✓ Válido' if self.cert_info['is_valid'] else '✗ Expirado'}\n"
                f")"
            )
        return "CertificateManager(não carregado)"


# Exemplo de uso
if __name__ == '__main__':
    import sys

    # Teste de carregamento
    if len(sys.argv) < 2:
        print("Uso: python cert_manager.py <caminho_certificado.pfx>")
        sys.exit(1)

    cert_path = sys.argv[1]

    try:
        # Opção 1: Senha direto (não recomendado para produção)
        # cert_mgr = CertificateManager(cert_path, password='senha123')

        # Opção 2: Usando keyring
        cert_mgr = CertificateManager(cert_path, use_keyring=True)

        print(cert_mgr)
        print("\nInformações completas:")
        for key, value in cert_mgr.get_info().items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"Erro: {e}")
