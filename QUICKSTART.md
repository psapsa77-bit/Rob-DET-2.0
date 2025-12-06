# 🚀 Guia de Início Rápido - Rob-DET 2.0

Comece a usar o robô de automação DET em **5 passos simples**!

---

## ⚡ Configuração Rápida (15 minutos)

### Pré-requisitos

Antes de começar, certifique-se de ter:
- ✅ **Windows 10/11**
- ✅ **Python 3.11+** instalado
- ✅ **Certificado Digital A1** (e-CNPJ) instalado no Windows
- ✅ **Google Chrome** ou Microsoft Edge
- ✅ **Procuração Eletrônica** ativa no SPE para os CNPJs dos clientes

---

## 📋 Passo a Passo

### 1️⃣ Clone o Repositório

```bash
git clone <seu-repositorio> Rob-DET-2.0
cd Rob-DET-2.0
```

### 2️⃣ Crie e Ative o Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows PowerShell)
venv\Scripts\Activate.ps1

# OU Ativar (Windows CMD)
venv\Scripts\activate.bat
```

### 3️⃣ Execute o Setup Automático

**⚠️ IMPORTANTE: Execute como Administrador!**

```powershell
# Clique direito no PowerShell > "Executar como Administrador"
cd C:\caminho\para\Rob-DET-2.0

# Ativar ambiente virtual
venv\Scripts\Activate.ps1

# Executar setup
python scripts/setup_environment.py
```

**O setup automático irá:**
- ✅ Verificar versão do Python
- ✅ Instalar todas as dependências
- ✅ Criar arquivos de configuração (.env, clients.yaml)
- ✅ Listar seus certificados digitais
- ✅ Configurar auto-seleção de certificado no navegador

**Siga as instruções interativas!**

### 4️⃣ Configure seus Clientes

Edite o arquivo `config/clients.yaml`:

```yaml
clients:
  - cnpj: "12.345.678/0001-90"
    razao_social: "Minha Empresa Ltda"
    active: true
    priority: high
    email_notificacao: "contato@empresa.com"

  - cnpj: "98.765.432/0001-10"
    razao_social: "Outra Empresa S.A."
    active: true
    priority: normal
```

### 5️⃣ Valide a Configuração

```bash
python scripts/validate_config.py --full
```

**Você deve ver:**
```
✅ Todas as 6 verificações passaram!
🎉 Ambiente configurado corretamente!
```

---

## 🎯 Executar o Robô

### Teste Inicial (Modo Debug)

```bash
# Primeiro teste com navegador visível
python main.py --debug --no-headless
```

### Processar Todos os Clientes

```bash
python main.py
```

### Processar CNPJ Específico

```bash
python main.py --cnpj 12.345.678/0001-90
```

### Modo Headless (Produção)

Edite `.env`:
```env
HEADLESS=true
```

Depois execute:
```bash
python main.py
```

---

## 🔧 Comandos Úteis

### Listar Certificados Digitais

```bash
python scripts/list_certificates.py
```

### Buscar Certificado por CNPJ

```bash
python scripts/list_certificates.py --cnpj 12.345.678/0001-90
```

### Reconfigurar Certificado

```bash
# Execute como Administrador
python scripts/setup_auto_certificate.py
```

### Verificar Configuração

```bash
python scripts/validate_config.py
```

---

## 🆘 Solução de Problemas Comuns

### ❌ "Nenhum certificado encontrado"

**Causa:** Certificado A1 não instalado ou não tem chave privada.

**Solução:**
1. Abra `certmgr.msc` (Windows + R)
2. Vá em **Pessoal > Certificados**
3. Verifique se seu certificado está lá
4. Clique com direito > Propriedades > deve mostrar que tem chave privada

### ❌ "Permissão negada ao configurar registro"

**Causa:** Script não executado como Administrador.

**Solução:**
1. Feche o PowerShell/CMD
2. Clique direito > **"Executar como Administrador"**
3. Execute o script novamente

### ❌ "Certificado não é selecionado automaticamente"

**Causa:** Navegador não foi completamente fechado após configuração.

**Solução:**
1. Abra o **Gerenciador de Tarefas** (Ctrl + Shift + Esc)
2. Encerre **TODOS** os processos do Chrome/Edge
3. Abra o navegador novamente
4. Acesse o portal DET

### ❌ "ModuleNotFoundError: No module named 'selenium'"

**Causa:** Dependências não instaladas.

**Solução:**
```bash
pip install -r requirements.txt
```

### ❌ "ChromeDriver não encontrado"

**Causa:** WebDriver Manager ainda não baixou o driver.

**Solução:**
- O download é automático na primeira execução
- Aguarde o download completar
- Se falhar, execute: `pip install --upgrade webdriver-manager`

---

## 📁 Estrutura de Arquivos Importantes

```
Rob-DET-2.0/
├── .env                    # ⚙️ Configurações sensíveis (EDITAR!)
├── config/
│   └── clients.yaml       # 👥 Lista de clientes (EDITAR!)
├── main.py                # 🚀 Executar o robô
├── scripts/               # 🔧 Scripts de configuração
│   ├── setup_environment.py
│   ├── list_certificates.py
│   ├── setup_auto_certificate.py
│   └── validate_config.py
├── logs/                  # 📝 Logs de execução
└── data/
    └── exports/           # 📊 Relatórios exportados
```

---

## ⚙️ Configurações Principais (.env)

### Certificado Digital
```env
# Caminho do certificado (se usar .pfx local)
CERT_PATH=./certs/certificado.pfx

# Usar keyring para senha (recomendado)
USE_KEYRING=true
```

### Navegador
```env
# Navegador (chrome ou edge)
BROWSER=chrome

# Modo headless (true/false)
HEADLESS=false

# Timeout padrão (segundos)
DEFAULT_TIMEOUT=30
```

### Procuração
```env
# CNPJ do contador/escritório
CONTADOR_CNPJ=00.000.000/0001-00
```

---

## 📊 Exemplo de Execução

```
╔══════════════════════════════════════════════════════════════╗
║                    🤖 ROB-DET 2.0                             ║
║        Robô de Automação do Portal DET                       ║
╚══════════════════════════════════════════════════════════════╝

2025-12-06 10:00:00 | INFO  | Carregando configurações...
2025-12-06 10:00:01 | INFO  | Configuração carregada: 5 clientes
2025-12-06 10:00:02 | INFO  | Certificado: EMPRESA EXEMPLO LTDA
2025-12-06 10:00:03 | INFO  | Iniciando WebDriver...
2025-12-06 10:00:05 | INFO  | Realizando login no DET...
2025-12-06 10:00:15 | SUCCESS | ✓ Login realizado com sucesso!

════════════════════════════════════════════════════════════
Cliente 1/5
════════════════════════════════════════════════════════════
2025-12-06 10:00:20 | INFO  | Processando: EMPRESA A LTDA
2025-12-06 10:00:25 | SUCCESS | ✓ 3 mensagens novas encontradas

📋 Resultados
┌─────────────────┬────────────────────┬───────────┬───────┬────────┐
│ Cliente         │ CNPJ               │ Mensagens │ Novas │ Status │
├─────────────────┼────────────────────┼───────────┼───────┼────────┤
│ EMPRESA A LTDA  │ 12.345.678/0001-90 │     15    │   3   │   ✓    │
│ EMPRESA B S.A.  │ 98.765.432/0001-10 │     8     │   1   │   ✓    │
└─────────────────┴────────────────────┴───────────┴───────┴────────┘

✅ Execução concluída!
```

---

## 🔄 Fluxo de Trabalho Diário

### Setup Inicial (Uma vez)
```bash
# 1. Setup completo (como admin)
python scripts/setup_environment.py

# 2. Editar configurações
# - .env
# - config/clients.yaml

# 3. Validar
python scripts/validate_config.py
```

### Uso Diário
```bash
# Ativar ambiente
venv\Scripts\activate

# Executar robô
python main.py

# Ver logs
type logs\det_robot.log
```

### Manutenção
```bash
# Verificar certificados
python scripts/list_certificates.py

# Validar configuração
python scripts/validate_config.py

# Atualizar dependências
pip install --upgrade -r requirements.txt
```

---

## 🎓 Próximos Passos

Agora que você configurou o robô:

1. 📖 Leia a **[Documentação Completa](README.md)**
2. 🔍 Consulte a **[Análise Técnica](ANALISE_TECNICA.md)**
3. 🛠️ Explore os **[Scripts](scripts/README.md)**
4. ⚙️ Personalize as **[Configurações](config/settings.yaml)**
5. 🚀 **Execute e teste!**

---

## 💡 Dicas

✅ **Execute sempre em modo `--debug` na primeira vez**
✅ **Mantenha o navegador fechado ao configurar certificado**
✅ **Valide a configuração antes de cada execução importante**
✅ **Monitore os logs em `logs/det_robot.log`**
✅ **Faça backup das configurações (`config/` e `.env`)**
✅ **Atualize regularmente as dependências**

---

## 📞 Suporte

- **Issues**: GitHub Issues do projeto
- **Documentação**: `README.md` e `ANALISE_TECNICA.md`
- **Scripts**: `scripts/README.md`

---

**🎉 Pronto para começar!**

Execute: `python main.py --debug`

---

**Versão:** 2.0.0
**Última atualização:** 06/12/2025
