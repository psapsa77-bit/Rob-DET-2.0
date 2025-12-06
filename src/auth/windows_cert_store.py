"""
Windows Certificate Store - Rob-DET 2.0

Módulo para interação com o Windows Certificate Store:
- Listagem de certificados instalados
- Extração de informações (CN, CNPJ, validade)
- Busca de certificados específicos por filtros
- Suporte a certificados A1 (e-CNPJ, e-CPF)
"""

import platform
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from loguru import logger

# Verificar se está no Windows
if platform.system() != 'Windows':
    raise OSError("Este módulo só funciona no Windows")

# Importações Windows-específicas
import subprocess
import json


@dataclass
class CertificateInfo:
    """Informações de um certificado digital."""

    subject_cn: str  # Common Name
    issuer_cn: str  # Emissor
    serial_number: str
    thumbprint: str  # Impressão digital (hash único)
    valid_from: str
    valid_to: str
    cnpj: Optional[str] = None
    cpf: Optional[str] = None
    is_valid: bool = True
    store_location: str = "CurrentUser"  # ou LocalMachine

    def __str__(self) -> str:
        status = "✓ Válido" if self.is_valid else "✗ Expirado"
        documento = self.cnpj or self.cpf or "N/A"
        return (
            f"CN: {self.subject_cn}\n"
            f"Documento: {documento}\n"
            f"Validade: {self.valid_from} até {self.valid_to}\n"
            f"Status: {status}\n"
            f"Thumbprint: {thumbprint[:16]}..."
        )


class WindowsCertificateStore:
    """Gerenciador do Windows Certificate Store."""

    def __init__(self):
        """Inicializa o gerenciador."""
        if platform.system() != 'Windows':
            raise OSError("Este módulo requer Windows")

        logger.info("Windows Certificate Store Manager iniciado")

    def list_certificates(
        self,
        store_location: str = "CurrentUser",
        store_name: str = "My"
    ) -> List[CertificateInfo]:
        """
        Lista certificados do Windows Certificate Store.

        Args:
            store_location: LocalMachine ou CurrentUser
            store_name: Nome do store (My = Pessoal)

        Returns:
            Lista de CertificateInfo

        Example:
            >>> store = WindowsCertificateStore()
            >>> certs = store.list_certificates()
            >>> for cert in certs:
            ...     print(cert.subject_cn)
        """
        try:
            logger.info(f"Listando certificados de {store_location}\\{store_name}")

            # Usar PowerShell para listar certificados
            ps_script = f"""
            Get-ChildItem -Path Cert:\\{store_location}\\{store_name} |
            Where-Object {{$_.HasPrivateKey -eq $true}} |
            Select-Object Subject, Issuer, SerialNumber, Thumbprint, NotBefore, NotAfter |
            ConvertTo-Json
            """

            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            if result.returncode != 0:
                logger.error(f"Erro ao executar PowerShell: {result.stderr}")
                return []

            # Parse JSON
            output = result.stdout.strip()
            if not output or output == '':
                logger.warning("Nenhum certificado encontrado")
                return []

            # Tratar tanto um certificado quanto múltiplos
            try:
                certs_data = json.loads(output)
                if not isinstance(certs_data, list):
                    certs_data = [certs_data]
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao parsear JSON: {e}")
                return []

            # Converter para CertificateInfo
            certificates = []
            for cert_data in certs_data:
                try:
                    cert_info = self._parse_certificate_data(cert_data, store_location)
                    certificates.append(cert_info)
                except Exception as e:
                    logger.warning(f"Erro ao processar certificado: {e}")
                    continue

            logger.success(f"Encontrados {len(certificates)} certificados")
            return certificates

        except Exception as e:
            logger.error(f"Erro ao listar certificados: {e}")
            return []

    def _parse_certificate_data(
        self,
        cert_data: Dict[str, Any],
        store_location: str
    ) -> CertificateInfo:
        """
        Parseia dados do certificado.

        Args:
            cert_data: Dados do PowerShell
            store_location: Localização do store

        Returns:
            CertificateInfo
        """
        # Extrair Subject CN
        subject = cert_data.get('Subject', '')
        subject_cn = self._extract_cn(subject)

        # Extrair Issuer CN
        issuer = cert_data.get('Issuer', '')
        issuer_cn = self._extract_cn(issuer)

        # Datas de validade
        valid_from_str = cert_data.get('NotBefore', '')
        valid_to_str = cert_data.get('NotAfter', '')

        # Converter datas do formato PowerShell
        valid_from = self._parse_powershell_date(valid_from_str)
        valid_to = self._parse_powershell_date(valid_to_str)

        # Verificar se está válido
        now = datetime.now()
        is_valid = valid_from <= now <= valid_to if (valid_from and valid_to) else False

        # Extrair CNPJ/CPF do Subject
        cnpj = self._extract_cnpj(subject)
        cpf = self._extract_cpf(subject)

        return CertificateInfo(
            subject_cn=subject_cn,
            issuer_cn=issuer_cn,
            serial_number=cert_data.get('SerialNumber', ''),
            thumbprint=cert_data.get('Thumbprint', ''),
            valid_from=valid_from.strftime('%d/%m/%Y') if valid_from else 'N/A',
            valid_to=valid_to.strftime('%d/%m/%Y') if valid_to else 'N/A',
            cnpj=cnpj,
            cpf=cpf,
            is_valid=is_valid,
            store_location=store_location
        )

    def _extract_cn(self, subject: str) -> str:
        """
        Extrai Common Name do Subject/Issuer.

        Args:
            subject: String do Subject/Issuer

        Returns:
            Common Name
        """
        # Formato: CN=Nome, OU=..., etc
        match = re.search(r'CN=([^,]+)', subject)
        return match.group(1).strip() if match else subject

    def _extract_cnpj(self, subject: str) -> Optional[str]:
        """
        Extrai CNPJ do Subject.

        Args:
            subject: String do Subject

        Returns:
            CNPJ formatado ou None
        """
        # Padrão: 14 dígitos
        match = re.search(r'(\d{14})', subject)
        if match:
            cnpj = match.group(1)
            # Formatar: 00.000.000/0001-00
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        return None

    def _extract_cpf(self, subject: str) -> Optional[str]:
        """
        Extrai CPF do Subject.

        Args:
            subject: String do Subject

        Returns:
            CPF formatado ou None
        """
        # Padrão: 11 dígitos (se não for CNPJ)
        match = re.search(r'(?<!\d)(\d{11})(?!\d)', subject)
        if match:
            cpf = match.group(1)
            # Formatar: 000.000.000-00
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return None

    def _parse_powershell_date(self, date_str: str) -> Optional[datetime]:
        """
        Parseia data do PowerShell.

        Args:
            date_str: String de data do PowerShell

        Returns:
            datetime ou None
        """
        if not date_str:
            return None

        # Formatos possíveis do PowerShell
        formats = [
            '%m/%d/%Y %I:%M:%S %p',  # 12/06/2025 10:30:00 AM
            '%d/%m/%Y %H:%M:%S',      # 06/12/2025 10:30:00
            '%Y-%m-%d %H:%M:%S',      # 2025-12-06 10:30:00
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        logger.warning(f"Não foi possível parsear data: {date_str}")
        return None

    def find_by_cnpj(self, cnpj: str) -> List[CertificateInfo]:
        """
        Busca certificados por CNPJ.

        Args:
            cnpj: CNPJ (com ou sem formatação)

        Returns:
            Lista de certificados encontrados
        """
        # Remove formatação
        cnpj_numbers = ''.join(filter(str.isdigit, cnpj))

        all_certs = self.list_certificates()

        matches = []
        for cert in all_certs:
            if cert.cnpj:
                cert_cnpj_numbers = ''.join(filter(str.isdigit, cert.cnpj))
                if cert_cnpj_numbers == cnpj_numbers:
                    matches.append(cert)

        logger.info(f"Encontrados {len(matches)} certificados para CNPJ {cnpj}")
        return matches

    def find_by_cn(self, cn: str, partial: bool = True) -> List[CertificateInfo]:
        """
        Busca certificados por Common Name.

        Args:
            cn: Common Name
            partial: Se True, busca parcial (contém)

        Returns:
            Lista de certificados encontrados
        """
        all_certs = self.list_certificates()

        matches = []
        for cert in all_certs:
            if partial:
                if cn.lower() in cert.subject_cn.lower():
                    matches.append(cert)
            else:
                if cn.lower() == cert.subject_cn.lower():
                    matches.append(cert)

        logger.info(f"Encontrados {len(matches)} certificados para CN '{cn}'")
        return matches

    def get_valid_certificates(self) -> List[CertificateInfo]:
        """
        Retorna apenas certificados válidos.

        Returns:
            Lista de certificados válidos
        """
        all_certs = self.list_certificates()
        valid = [cert for cert in all_certs if cert.is_valid]

        logger.info(f"Certificados válidos: {len(valid)} de {len(all_certs)}")
        return valid

    def get_certificate_by_thumbprint(self, thumbprint: str) -> Optional[CertificateInfo]:
        """
        Busca certificado por thumbprint (hash único).

        Args:
            thumbprint: Thumbprint do certificado

        Returns:
            CertificateInfo ou None
        """
        all_certs = self.list_certificates()

        for cert in all_certs:
            if cert.thumbprint.lower() == thumbprint.lower():
                return cert

        return None


# Exemplo de uso
if __name__ == '__main__':
    from rich.console import Console
    from rich.table import Table

    console = Console()

    try:
        # Criar gerenciador
        store = WindowsCertificateStore()

        # Listar todos os certificados
        print("\n" + "=" * 80)
        print("CERTIFICADOS DIGITAIS INSTALADOS NO WINDOWS")
        print("=" * 80 + "\n")

        certs = store.list_certificates()

        if not certs:
            console.print("[yellow]Nenhum certificado encontrado![/yellow]")
        else:
            # Criar tabela
            table = Table(title=f"Certificados Encontrados ({len(certs)})")
            table.add_column("CN", style="cyan", no_wrap=False)
            table.add_column("Documento", style="yellow")
            table.add_column("Validade", style="green")
            table.add_column("Status", justify="center")

            for cert in certs:
                documento = cert.cnpj or cert.cpf or "N/A"
                status = "✓" if cert.is_valid else "✗"
                status_color = "green" if cert.is_valid else "red"

                table.add_row(
                    cert.subject_cn[:60],
                    documento,
                    f"{cert.valid_from} - {cert.valid_to}",
                    f"[{status_color}]{status}[/{status_color}]"
                )

            console.print(table)

            # Estatísticas
            valid_count = sum(1 for c in certs if c.is_valid)
            cnpj_count = sum(1 for c in certs if c.cnpj)
            cpf_count = sum(1 for c in certs if c.cpf)

            print(f"\nEstatísticas:")
            print(f"  Total: {len(certs)}")
            print(f"  Válidos: {valid_count}")
            print(f"  e-CNPJ: {cnpj_count}")
            print(f"  e-CPF: {cpf_count}")

    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")
