"""
Interface Web - Rob-DET 2.0

Aplicação Flask para gerenciar o robô DET via navegador.
"""

from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional

from src.models import Cliente
from src.config_manager import get_config


app = Flask(__name__)
app.config['SECRET_KEY'] = 'rob-det-2.0-secret-key-change-in-production'
app.config['JSON_AS_ASCII'] = False

# Estado global da execução
execution_state = {
    'running': False,
    'progress': 0,
    'current_client': None,
    'total_clients': 0,
    'messages': [],
    'start_time': None,
    'last_execution': None
}


def carregar_clientes() -> List[Dict]:
    """Carrega clientes do arquivo JSON."""
    try:
        clientes_file = Path("config/clientes.json")

        if not clientes_file.exists():
            return []

        with open(clientes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data.get('clientes', [])

    except Exception as e:
        print(f"Erro ao carregar clientes: {e}")
        return []


def salvar_clientes(clientes: List[Dict]) -> bool:
    """Salva clientes no arquivo JSON."""
    try:
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)

        clientes_file = config_dir / "clientes.json"

        # Carregar configurações existentes ou usar padrão
        configuracoes = {
            "consultar_apenas_ativos": True,
            "ordem_processamento": "priority",
            "delay_entre_clientes_segundos": 10,
            "incluir_filiais": True,
            "notificar_apenas_novas": True,
            "tipos_mensagem_notificar": ["Autuação", "Intimação", "Notificação"]
        }

        if clientes_file.exists():
            with open(clientes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'configuracoes' in data:
                    configuracoes = data['configuracoes']

        # Salvar
        dados = {
            "clientes": clientes,
            "configuracoes": configuracoes
        }

        with open(clientes_file, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

        return True

    except Exception as e:
        print(f"Erro ao salvar clientes: {e}")
        return False


@app.route('/')
def index():
    """Página principal - Dashboard."""
    clientes = carregar_clientes()
    total = len(clientes)
    ativos = sum(1 for c in clientes if c.get('ativo', True))

    return render_template('index.html',
                         total_clientes=total,
                         clientes_ativos=ativos,
                         execution_state=execution_state)


@app.route('/clientes')
def clientes_page():
    """Página de gerenciamento de clientes."""
    clientes = carregar_clientes()
    return render_template('clientes.html', clientes=clientes)


@app.route('/api/clientes', methods=['GET'])
def get_clientes():
    """API: Retorna lista de clientes."""
    clientes = carregar_clientes()
    return jsonify({'success': True, 'clientes': clientes})


@app.route('/api/clientes', methods=['POST'])
def add_cliente():
    """API: Adiciona novo cliente."""
    try:
        dados = request.json

        # Validar campos obrigatórios
        if not dados.get('cnpj'):
            return jsonify({'success': False, 'error': 'CNPJ é obrigatório'}), 400

        if not dados.get('razao_social'):
            return jsonify({'success': False, 'error': 'Razão Social é obrigatória'}), 400

        # Criar cliente
        cliente = {
            'cnpj': dados.get('cnpj'),
            'razao_social': dados.get('razao_social'),
            'nome_fantasia': dados.get('nome_fantasia', ''),
            'ativo': dados.get('ativo', True),
            'prioridade': dados.get('prioridade', 'normal'),
            'email_notificacao': dados.get('email_notificacao', ''),
            'observacoes': dados.get('observacoes', ''),
            'filiais': dados.get('filiais', [])
        }

        # Carregar clientes existentes
        clientes = carregar_clientes()

        # Verificar se CNPJ já existe
        if any(c.get('cnpj') == cliente['cnpj'] for c in clientes):
            return jsonify({'success': False, 'error': 'CNPJ já cadastrado'}), 400

        # Adicionar
        clientes.append(cliente)

        # Salvar
        if salvar_clientes(clientes):
            return jsonify({'success': True, 'cliente': cliente})
        else:
            return jsonify({'success': False, 'error': 'Erro ao salvar'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/clientes/<cnpj>', methods=['PUT'])
def update_cliente(cnpj):
    """API: Atualiza cliente existente."""
    try:
        dados = request.json
        clientes = carregar_clientes()

        # Encontrar cliente
        cliente_idx = None
        for idx, c in enumerate(clientes):
            if c.get('cnpj') == cnpj:
                cliente_idx = idx
                break

        if cliente_idx is None:
            return jsonify({'success': False, 'error': 'Cliente não encontrado'}), 404

        # Atualizar
        clientes[cliente_idx].update({
            'razao_social': dados.get('razao_social', clientes[cliente_idx].get('razao_social')),
            'nome_fantasia': dados.get('nome_fantasia', clientes[cliente_idx].get('nome_fantasia')),
            'ativo': dados.get('ativo', clientes[cliente_idx].get('ativo')),
            'prioridade': dados.get('prioridade', clientes[cliente_idx].get('prioridade')),
            'email_notificacao': dados.get('email_notificacao', clientes[cliente_idx].get('email_notificacao')),
            'observacoes': dados.get('observacoes', clientes[cliente_idx].get('observacoes')),
            'filiais': dados.get('filiais', clientes[cliente_idx].get('filiais', []))
        })

        # Salvar
        if salvar_clientes(clientes):
            return jsonify({'success': True, 'cliente': clientes[cliente_idx]})
        else:
            return jsonify({'success': False, 'error': 'Erro ao salvar'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/clientes/<cnpj>', methods=['DELETE'])
def delete_cliente(cnpj):
    """API: Remove cliente."""
    try:
        clientes = carregar_clientes()

        # Filtrar (remover)
        clientes_novos = [c for c in clientes if c.get('cnpj') != cnpj]

        if len(clientes_novos) == len(clientes):
            return jsonify({'success': False, 'error': 'Cliente não encontrado'}), 404

        # Salvar
        if salvar_clientes(clientes_novos):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Erro ao salvar'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/executar', methods=['POST'])
def executar_robo():
    """API: Executa o robô."""
    global execution_state

    if execution_state['running']:
        return jsonify({'success': False, 'error': 'Robô já está em execução'}), 400

    # Iniciar execução em thread separada
    def run():
        global execution_state
        try:
            execution_state['running'] = True
            execution_state['start_time'] = datetime.now().isoformat()
            execution_state['messages'] = []

            from main import RoboDET

            robo = RoboDET()
            robo.monitor.iniciar_heartbeat()

            try:
                sucesso = robo.executar()
                execution_state['last_execution'] = {
                    'timestamp': datetime.now().isoformat(),
                    'success': sucesso
                }
            finally:
                robo.monitor.parar_heartbeat()

        except Exception as e:
            execution_state['messages'].append(f"Erro: {str(e)}")

        finally:
            execution_state['running'] = False

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    return jsonify({'success': True, 'message': 'Execução iniciada'})


@app.route('/api/status', methods=['GET'])
def get_status():
    """API: Retorna status da execução."""
    return jsonify(execution_state)


@app.route('/relatorios')
def relatorios_page():
    """Página de relatórios."""
    # Listar relatórios disponíveis
    relatorios_dir = Path("relatorios")
    relatorios = []

    if relatorios_dir.exists():
        for file in sorted(relatorios_dir.glob("*.xlsx"), reverse=True):
            relatorios.append({
                'nome': file.name,
                'data': datetime.fromtimestamp(file.stat().st_mtime).strftime('%d/%m/%Y %H:%M'),
                'tamanho': f"{file.stat().st_size / 1024:.1f} KB"
            })

    return render_template('relatorios.html', relatorios=relatorios)


@app.route('/download/<filename>')
def download_relatorio(filename):
    """Download de relatório."""
    file_path = Path("relatorios") / filename

    if not file_path.exists():
        return "Arquivo não encontrado", 404

    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    print("=" * 60)
    print("🌐 Rob-DET 2.0 - Interface Web")
    print("=" * 60)
    print()
    print("Servidor iniciando em: http://localhost:5000")
    print()
    print("Pressione Ctrl+C para parar")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
