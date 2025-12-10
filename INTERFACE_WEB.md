# 🌐 Interface Web - Rob-DET 2.0

> Interface web moderna e intuitiva para gerenciar o robô DET através do navegador

---

## 🚀 Como Iniciar

### **Opção 1: Windows (Duplo-Clique)**

1. Duplo-clique no arquivo `INICIAR_WEB.bat`
2. Aguarde o servidor iniciar
3. Abra seu navegador em: **http://localhost:5000**

### **Opção 2: Linha de Comando**

```bash
python web_app.py
```

Depois acesse: **http://localhost:5000**

---

## 📋 Funcionalidades

### **1. Dashboard**

- ✅ Visão geral dos clientes
- ✅ Status do robô em tempo real
- ✅ Botão para executar consulta
- ✅ Acompanhamento de progresso
- ✅ Informações da última execução

### **2. Gerenciamento de Clientes** 👥

**Adicionar Cliente:**
1. Clique em "Novo Cliente"
2. Preencha:
   - CNPJ (obrigatório)
   - Razão Social (obrigatório)
   - Nome Fantasia (opcional)
   - Email para notificações (opcional)
   - Prioridade: Alta, Normal ou Baixa
   - Status: Ativo ou Inativo
   - Observações (opcional)
3. Clique em "Salvar"

**Editar Cliente:**
1. Na tabela de clientes, clique no botão de edição (lápis)
2. Modifique os campos desejados
3. Clique em "Atualizar"

**Excluir Cliente:**
1. Clique no botão de exclusão (lixeira)
2. Confirme a exclusão

### **3. Execução do Robô** 🤖

**Executar Consulta:**
1. No Dashboard, clique em "Executar Robô"
2. Confirme a execução
3. Acompanhe o progresso em tempo real
4. Veja o log de mensagens

**O que acontece:**
- ✅ O navegador abre automaticamente
- ✅ Acessa o portal DET
- ✅ Consulta cada cliente ativo
- ✅ Extrai as mensagens
- ✅ Gera relatório Excel
- ✅ Atualiza o status na interface

### **4. Relatórios** 📊

- ✅ Lista todos os relatórios gerados
- ✅ Informações: nome, data, tamanho
- ✅ Download direto pelo navegador
- ✅ Arquivos em formato Excel (.xlsx)

---

## 🎯 Fluxo de Uso Completo

1. **Primeira vez:**
   ```bash
   # Instalar dependências
   python instalar_dependencias.py

   # Iniciar interface web
   python web_app.py
   ```

2. **Adicionar seus clientes:**
   - Acesse: http://localhost:5000/clientes
   - Adicione cada CNPJ que deseja monitorar

3. **Executar consulta:**
   - Volte ao Dashboard
   - Clique em "Executar Robô"
   - Aguarde a conclusão

4. **Baixar relatórios:**
   - Acesse: http://localhost:5000/relatorios
   - Baixe o arquivo Excel mais recente

---

## 🔧 API REST

A interface web expõe uma API REST que você pode usar:

### **Clientes**

**Listar todos:**
```
GET /api/clientes
```

**Adicionar:**
```
POST /api/clientes
Content-Type: application/json

{
  "cnpj": "12.345.678/0001-90",
  "razao_social": "EMPRESA EXEMPLO LTDA",
  "nome_fantasia": "Exemplo",
  "ativo": true,
  "prioridade": "alta",
  "email_notificacao": "contato@exemplo.com"
}
```

**Atualizar:**
```
PUT /api/clientes/{cnpj}
Content-Type: application/json

{
  "razao_social": "NOVO NOME LTDA",
  "ativo": false
}
```

**Excluir:**
```
DELETE /api/clientes/{cnpj}
```

### **Execução**

**Executar robô:**
```
POST /api/executar
```

**Status da execução:**
```
GET /api/status
```

Retorna:
```json
{
  "running": true,
  "progress": 45,
  "current_client": "Empresa XYZ",
  "total_clients": 10,
  "messages": ["Iniciando...", "Cliente 1/10"],
  "start_time": "2025-12-10T14:30:00",
  "last_execution": {
    "timestamp": "2025-12-10T14:00:00",
    "success": true
  }
}
```

---

## 💡 Dicas e Truques

### **Acessar de outros computadores na rede:**

Edite `web_app.py`, linha final:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

Depois acesse de outro PC usando:
```
http://[IP-DO-SERVIDOR]:5000
```

### **Executar em background (Linux/Mac):**

```bash
nohup python web_app.py > web_app.log 2>&1 &
```

### **Usar outra porta:**

Edite `web_app.py`, última linha:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Altere para a porta desejada
```

---

## ⚠️ Problemas Comuns

### **"Address already in use"**

Outra aplicação está usando a porta 5000. Soluções:
1. Feche a aplicação que está usando a porta
2. Ou mude a porta do Rob-DET (veja dicas acima)

### **Página não carrega**

1. Verifique se o servidor está rodando
2. Verifique o endereço: `http://localhost:5000` (não `https`)
3. Tente outro navegador

### **Erro ao executar robô**

1. Verifique se as dependências estão instaladas
2. Execute o diagnóstico: `python scripts/diagnosticar_ambiente.py`
3. Veja os logs no console do servidor

---

## 🎨 Tecnologias Utilizadas

- **Flask 3.0+**: Framework web Python
- **Bootstrap 5.3**: Framework CSS responsivo
- **Bootstrap Icons**: Ícones
- **JavaScript Vanilla**: Interatividade
- **JSON**: Armazenamento de dados

---

## 📸 Screenshots

### Dashboard
![Dashboard](https://via.placeholder.com/800x400?text=Dashboard+-+Status+e+Controle)

### Gerenciamento de Clientes
![Clientes](https://via.placeholder.com/800x400?text=Gerenciamento+de+Clientes)

### Relatórios
![Relatórios](https://via.placeholder.com/800x400?text=Lista+de+Relatorios)

---

## 🔐 Segurança

**IMPORTANTE:** Esta interface é apenas para uso local/interno. Não exponha na internet sem:

1. ✅ Adicionar autenticação (login/senha)
2. ✅ Usar HTTPS
3. ✅ Configurar firewall
4. ✅ Validar todas as entradas
5. ✅ Trocar a SECRET_KEY em produção

---

## 📝 Suporte

Problemas ou dúvidas?

1. Consulte o `INICIO_RAPIDO.md`
2. Execute diagnóstico: `python scripts/diagnosticar_ambiente.py`
3. Verifique os logs no console
4. Crie uma issue no GitHub

---

**Desenvolvido com ❤️ para facilitar o gerenciamento do DET**
