#!/usr/bin/env python3
"""
Instalador de Dependências da Interface Web - Rob-DET 2.0

Instala apenas as dependências necessárias para a interface web.
"""

import sys
import subprocess

print("=" * 60)
print("Rob-DET 2.0 - Instalador da Interface Web")
print("=" * 60)
print()

def verificar_flask():
    """Verifica se Flask está instalado."""
    try:
        import flask
        print(f"✅ Flask {flask.__version__} já instalado")
        return True
    except ImportError:
        print("❌ Flask não encontrado")
        return False

def instalar_dependencias():
    """Instala Flask e Flask-CORS."""
    print("\n📦 Instalando dependências da interface web...")
    print("   Isso pode demorar alguns minutos...")
    print()

    dependencias = [
        'Flask>=3.0.0',
        'Flask-CORS>=4.0.0'
    ]

    try:
        for dep in dependencias:
            print(f"⏳ Instalando {dep}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", dep],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"✅ {dep} instalado")

        print("\n" + "=" * 60)
        print("✅ INSTALAÇÃO CONCLUÍDA!")
        print("=" * 60)
        print()
        print("🎉 A interface web está pronta para usar!")
        print()
        print("📝 Para iniciar:")
        print("   1. Execute: python web_app.py")
        print("   2. Ou no Windows: duplo-clique em INICIAR_WEB.bat")
        print("   3. Acesse: http://localhost:5000")
        print()

        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro ao instalar dependências: {e}")
        print("\n💡 Tente manualmente:")
        print("   pip install Flask Flask-CORS")
        return False

    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return False

def main():
    """Função principal."""
    if verificar_flask():
        print("\n✅ Dependências já instaladas!")
        print("\n📝 Para iniciar a interface web:")
        print("   python web_app.py")
        print("\n   Ou acesse: http://localhost:5000")
        return 0

    resposta = input("\nDeseja instalar as dependências agora? (S/n): ").strip().lower()

    if resposta in ['s', 'sim', 'y', 'yes', '']:
        if instalar_dependencias():
            return 0
        else:
            return 1
    else:
        print("\n❌ Instalação cancelada.")
        print("   Execute novamente quando estiver pronto.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Instalação interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
