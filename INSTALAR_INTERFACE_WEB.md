# 🚀 Como Instalar a Interface Web - Rob-DET 2.0

> **Instalação rápida em 2 passos!**

---

## ⚡ Instalação Rápida

### **Passo 1: Instalar Dependências da Interface Web**

Execute um dos comandos abaixo:

**Opção A - Instalador Automático (Recomendado):**
```bash
python instalar_web.py
```

**Opção B - Manual:**
```bash
pip install Flask Flask-CORS
```

### **Passo 2: Iniciar a Interface**

**No Windows:**
- Duplo-clique em `INICIAR_WEB.bat`

**Linha de comando (qualquer SO):**
```bash
python web_app.py
```

### **Passo 3: Acessar**

Abra seu navegador em:
```
http://localhost:5000
```

---

## ✅ Verificação

Se tudo estiver OK, você verá:
```
════════════════════════════════════════════════════════════
🌐 Rob-DET 2.0 - Interface Web
════════════════════════════════════════════════════════════

Servidor iniciando em: http://localhost:5000

Pressione Ctrl+C para parar
════════════════════════════════════════════════════════════
 * Serving Flask app 'web_app'
 * Debug mode: on
```

---

## ❌ Problemas Comuns

### **Erro: "No module named 'flask'"**

**Solução:**
```bash
python instalar_web.py
```

### **Erro: "No module named 'src.models'"**

Você precisa instalar as dependências principais primeiro:
```bash
python instalar_dependencias.py
```

### **Erro: "Address already in use"**

A porta 5000 já está em uso. Soluções:

1. **Feche o programa que está usando a porta**
2. **Ou mude a porta** editando `web_app.py` (última linha):
   ```python
   app.run(debug=True, host='0.0.0.0', port=8080)  # Mude para 8080
   ```

### **Página não carrega no navegador**

1. Verifique se o servidor está rodando (veja o console)
2. Use `http://localhost:5000` (não `https`)
3. Tente outro navegador
4. Desative temporariamente firewall/antivírus

---

## 🔄 Ordem Completa de Instalação (Do Zero)

Se você está começando do zero, siga esta ordem:

```bash
# 1. Instalar dependências principais do robô
python instalar_dependencias.py

# 2. Instalar dependências da interface web
python instalar_web.py

# 3. (Opcional) Criar arquivo de clientes
python criar_clientes.py

# 4. Testar o navegador
python robo.py
# Escolha opção 7

# 5. Iniciar interface web
python web_app.py

# 6. Acessar no navegador
# http://localhost:5000
```

---

## 📝 Uso Depois de Instalado

Toda vez que quiser usar a interface web:

**Windows:**
```
Duplo-clique em INICIAR_WEB.bat
```

**Linux/Mac:**
```bash
python web_app.py
```

---

## 💡 Dicas

### **Executar em Background (Linux/Mac)**

```bash
nohup python web_app.py > web.log 2>&1 &
```

### **Acessar de Outros Computadores na Rede**

1. Edite `web_app.py`, última linha:
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

2. Descubra seu IP:
   - Windows: `ipconfig`
   - Linux/Mac: `ifconfig` ou `ip addr`

3. Acesse de outro PC:
   ```
   http://[SEU-IP]:5000
   ```
   Exemplo: `http://192.168.1.100:5000`

---

## 🆘 Suporte

Se ainda tiver problemas:

1. Execute o diagnóstico completo:
   ```bash
   python scripts/diagnosticar_ambiente.py
   ```

2. Consulte a documentação:
   - `INTERFACE_WEB.md` - Guia completo da interface
   - `INICIO_RAPIDO.md` - Guia geral do projeto

3. Verifique os logs no console onde você executou `python web_app.py`

---

**Desenvolvido com ❤️ para facilitar sua vida!**
