#!/usr/bin/env python3
"""
Verificador de Dependências - Rob-DET 2.0

Verifica se todas as dependências necessárias estão instaladas
antes de executar o robô.
"""

import sys
import subprocess
from typing import List, Tuple


def verificar_dependencias() -> Tuple[bool, List[str]]:
    """
    Verifica se as dependências principais estão instaladas.

    Returns:
        Tuple[bool, List[str]]: (todas_ok, lista_faltando)
    """
    dependencias_principais = [
        'selenium',
        'webdriver_manager',
        'loguru',
        'rich',
        'pydantic',
        'schedule',
        'requests',
        'pandas',
        'openpyxl'
    ]

    faltando = []

    for dep in dependencias_principais:
        try:
            __import__(dep)
        except ImportError:
            faltando.append(dep)

    return len(faltando) == 0, faltando


def instalar_dependencias() -> bool:
    """
    Tenta instalar as dependências do requirements.txt.

    Returns:
        bool: True se instalação bem-sucedida
    """
    from pathlib import Path

    requirements_file = Path(__file__).parent.parent.parent / "requirements.txt"

    if not requirements_file.exists():
        print(f"❌ Arquivo não encontrado: {requirements_file}")
        return False

    try:
        print("\n📦 Instalando dependências...")
        print("⏳ Isso pode demorar alguns minutos...\n")

        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        print("✅ Dependências instaladas com sucesso!\n")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


def verificar_ou_instalar(auto_instalar: bool = True) -> bool:
    """
    Verifica dependências e opcionalmente instala se faltarem.

    Args:
        auto_instalar: Se True, tenta instalar automaticamente

    Returns:
        bool: True se todas as dependências estão OK
    """
    todas_ok, faltando = verificar_dependencias()

    if todas_ok:
        return True

    # Mostrar dependências faltando
    print("\n" + "="*60)
    print("⚠️  DEPENDÊNCIAS FALTANDO")
    print("="*60)
    print(f"\nFaltam {len(faltando)} dependência(s):")
    for dep in faltando:
        print(f"  • {dep}")
    print()

    if not auto_instalar:
        print("❌ Execute: pip install -r requirements.txt")
        print("   Ou execute: python install.py")
        return False

    # Perguntar ao usuário
    resposta = input("Deseja instalar as dependências agora? (S/n): ").strip().lower()

    if resposta in ['s', 'sim', 'y', 'yes', '']:
        if instalar_dependencias():
            # Verificar novamente
            todas_ok, faltando = verificar_dependencias()

            if todas_ok:
                print("✅ Todas as dependências estão instaladas!\n")
                return True
            else:
                print(f"❌ Ainda faltam: {', '.join(faltando)}")
                print("   Execute manualmente: pip install -r requirements.txt")
                return False
        else:
            return False
    else:
        print("\n❌ Não é possível continuar sem as dependências.")
        print("   Execute: pip install -r requirements.txt")
        print("   Ou execute: python install.py")
        return False


if __name__ == "__main__":
    # Teste
    print("🔍 Verificando dependências...\n")

    todas_ok, faltando = verificar_dependencias()

    if todas_ok:
        print("✅ Todas as dependências estão instaladas!")
    else:
        print(f"❌ Faltam {len(faltando)} dependência(s):")
        for dep in faltando:
            print(f"  • {dep}")
        print("\nExecute: pip install -r requirements.txt")
