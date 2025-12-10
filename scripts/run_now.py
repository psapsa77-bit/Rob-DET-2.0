#!/usr/bin/env python3
"""
Script de Execução Manual - Rob-DET 2.0

Executa o robô imediatamente (fora do agendamento).
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Verificar dependências primeiro
try:
    from src.utils.check_dependencies import verificar_ou_instalar

    if not verificar_ou_instalar(auto_instalar=True):
        print("\n❌ Não é possível executar sem as dependências instaladas.")
        print("\n💡 Soluções:")
        print("   1. Execute: python install.py")
        print("   2. Ou execute: pip install -r requirements.txt")
        sys.exit(1)

except Exception as e:
    print(f"\n❌ Erro ao verificar dependências: {e}")
    print("\n💡 Execute: pip install -r requirements.txt")
    sys.exit(1)

# Agora importar o main (dependências já verificadas)
try:
    from main import main
except ImportError as e:
    print(f"\n❌ Erro ao importar módulos: {e}")
    print("\n💡 Verifique se todas as dependências estão instaladas:")
    print("   python install.py")
    sys.exit(1)


if __name__ == '__main__':
    print("═" * 60)
    print("ROB-DET 2.0 - Execução Manual")
    print("═" * 60)
    print()

    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
