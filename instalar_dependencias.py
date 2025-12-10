#!/usr/bin/env python3
"""
Instalador Rápido de Dependências - Rob-DET 2.0

Script simples para instalar apenas as dependências do projeto,
sem configuração adicional.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Função principal."""
    print("="*60)
    print("ROB-DET 2.0 - Instalador Rápido de Dependências")
    print("="*60)
    print()

    # Verificar se requirements.txt existe
    requirements_file = Path(__file__).parent / "requirements.txt"

    if not requirements_file.exists():
        print(f"❌ Arquivo não encontrado: {requirements_file}")
        print("\nVerifique se você está no diretório correto do projeto.")
        return 1

    print("📦 Este script irá instalar todas as dependências necessárias.")
    print(f"📄 Arquivo: {requirements_file}")
    print()

    resposta = input("Deseja continuar? (S/n): ").strip().lower()

    if resposta not in ['s', 'sim', 'y', 'yes', '']:
        print("\n❌ Instalação cancelada.")
        return 0

    print("\n⏳ Instalando dependências...")
    print("   Isso pode demorar alguns minutos...\n")

    try:
        # Instalar com pip
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            stdout=sys.stdout,
            stderr=sys.stderr
        )

        print("\n" + "="*60)
        print("✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print()
        print("🎉 Todas as dependências foram instaladas.")
        print()
        print("📝 Próximos passos:")
        print("   1. Execute: python robo.py")
        print("   2. Escolha a opção 7 para testar o navegador")
        print("   3. Escolha a opção 1 para executar o robô")
        print()

        return 0

    except subprocess.CalledProcessError as e:
        print("\n" + "="*60)
        print("❌ ERRO DURANTE A INSTALAÇÃO")
        print("="*60)
        print(f"\nCódigo de erro: {e.returncode}")
        print("\n💡 Possíveis soluções:")
        print("   1. Verifique sua conexão com a internet")
        print("   2. Tente executar como administrador")
        print("   3. Atualize o pip: python -m pip install --upgrade pip")
        print("   4. Tente instalar manualmente: pip install -r requirements.txt")
        print()

        return 1

    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        print("\n💡 Tente executar manualmente:")
        print("   pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Instalação interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
