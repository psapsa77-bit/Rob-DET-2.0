#!/usr/bin/env python3
"""
Script de Execução Manual - Rob-DET 2.0

Executa o robô imediatamente (fora do agendamento).
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import main

if __name__ == '__main__':
    print("═" * 60)
    print("ROB-DET 2.0 - Execução Manual")
    print("═" * 60)
    print()

    main()
