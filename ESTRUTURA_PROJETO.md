# 📂 Estrutura do Projeto - Rob-DET 2.0

Documentação completa da estrutura de diretórios e módulos do robô.

---

## 🗂️ Árvore de Diretórios

```
Rob-DET-2.0/
├── 📄 main.py                          # Ponto de entrada principal
├── 📄 QUICKSTART.md                    # Guia de início rápido
├── 📄 README.md                        # Documentação principal
├── 📄 ANALISE_TECNICA.md              # Análise técnica completa
├── 📄 ESTRUTURA_PROJETO.md            # Este arquivo
├── 📄 LICENSE                          # Licença MIT
├── 📄 requirements.txt                 # Dependências Python
├── 📄 .env.example                     # Template variáveis ambiente
├── 📄 .gitignore                       # Arquivos ignorados Git
│
├── 📁 src/                             # Código-fonte principal
│   ├── 📄 __init__.py
│   │
│   ├── 📁 auth/                        # Autenticação e certificados
│   │   ├── 📄 __init__.py
│   │   ├── 📄 cert_manager.py          # Gerenciamento certificados A1
│   │   ├── 📄 registry_config.py       # Configuração registro Windows
│   │   └── 📄 windows_cert_store.py    # Interface Windows Certificate Store
│   │
│   ├── 📁 navigation/                  # Navegação no portal DET
│   │   ├── 📄 __init__.py
│   │   └── 📄 det_navigator.py         # Navegador Selenium
│   │
│   ├── 📁 extraction/                  # Extração de dados
│   │   ├── 📄 __init__.py
│   │   └── 📄 message_extractor.py     # Extrator de mensagens
│   │
│   ├── 📁 models/                      # Modelos de dados
│   │   └── 📄 __init__.py              # Cliente, Mensagem, Relatório
│   │
│   ├── 📁 reports/                     # Geração de relatórios
│   │   ├── 📄 __init__.py
│   │   └── 📄 report_generator.py      # Excel, CSV, JSON
│   │
│   ├── 📁 utils/                       # Utilitários
│   │   ├── 📄 __init__.py
│   │   ├── 📄 config.py                # Gerenciador de configuração
│   │   └── 📄 logger.py                # Sistema de logging
│   │
│   ├── 📄 det_scraper.py               # Scraper principal DET
│   └── 📄 orchestrator.py              # Orquestrador principal
│
├── 📁 scripts/                         # Scripts auxiliares
│   ├── 📄 README.md                    # Documentação dos scripts
│   ├── 📄 list_certificates.py         # Listar certificados instalados
│   ├── 📄 setup_auto_certificate.py    # Configurar auto-seleção
│   ├── 📄 setup_environment.py         # Setup completo ambiente
│   └── 📄 validate_config.py           # Validar configuração
│
├── 📁 config/                          # Arquivos de configuração
│   ├── 📄 settings.yaml                # Configurações gerais
│   ├── 📄 clients.yaml.example         # Template clientes
│   └── 📄 clientes.json.example        # Template JSON clientes
│
├── 📁 logs/                            # Logs de execução
│   ├── 📄 det_robot.log                # Log principal
│   └── 📁 screenshots/                 # Screenshots de erros
│
├── 📁 data/                            # Dados e exports
│   ├── 📁 exports/                     # Relatórios exportados
│   │   ├── 📄 *.xlsx                   # Relatórios Excel
│   │   ├── 📄 *.csv                    # Relatórios CSV
│   │   └── 📄 *.json                   # Relatórios JSON
│   └── 📄 clientes_estado.json         # Estado dos clientes
│
├── 📁 certs/                           # Certificados digitais (gitignore)
│   └── 📄 *.pfx                        # Certificados A1
│
└── 📁 tests/                           # Testes (futuro)
    └── 📄 __init__.py
```

---

## 📦 Módulos Principais

### 1. **src/models/__init__.py**
Define estruturas de dados principais:

#### Classes:
- **`Cliente`**: Representa empresa com procuração
  - CNPJ, razão social, prioridade
  - Metadados (última consulta, total mensagens)
  - Validação automática de CNPJ

- **`Mensagem`**: Representa mensagem do DET
  - ID, data, remetente, assunto
  - Tipo (Autuação, Intimação, etc.)
  - Status (lida/não lida)
  - Prioridade e urgência
  - Prazo de resposta

- **`RelatorioConsulta`**: Relatório de consulta
  - Estatísticas (total, novas, urgentes)
  - Lista de mensagens
  - Tempo de execução
  - Resumo textual

#### Enums:
- **`TipoMensagem`**: Autuação, Intimação, Notificação, etc.
- **`StatusMensagem`**: Não lida, Lida, Arquivada
- **`PrioridadeMensagem`**: Urgente, Alta, Normal, Baixa

---

### 2. **src/det_scraper.py**
Scraper principal do portal DET:

#### Classe `DETScraper`:
- **Autenticação**: Login com certificado digital
- **Seleção de Empresa**: Troca entre CNPJs via procuração
- **Navegação**: Acesso à caixa postal
- **Extração**: Scraping de mensagens
- **Classificação**: Tipo e prioridade de mensagens
- **Multi-cliente**: Consulta sequencial de múltiplos CNPJs

#### Métodos principais:
```python
scraper = DETScraper(navigator)
scraper.login()                                  # Login com certificado
scraper.selecionar_empresa("12.345.678/0001-90") # Selecionar CNPJ
scraper.acessar_caixa_postal()                  # Acessar caixa postal
mensagens = scraper.extrair_mensagens()          # Extrair mensagens
relatorio = scraper.consultar_cliente(cliente)   # Consulta completa
```

---

### 3. **src/orchestrator.py**
Orquestrador que coordena todo o fluxo:

#### Classe `DETOrchestrator`:
- **Inicialização**: Setup de componentes
- **Login**: Autenticação automática
- **Consultas**: Processamento de múltiplos clientes
- **Relatórios**: Geração em múltiplos formatos
- **Estado**: Persistência de dados

#### Fluxo completo:
```python
orquestrador = DETOrchestrator()

# Execução completa
orquestrador.executar_completo(
    apenas_nao_lidas=True,
    formatos_saida=['excel', 'json']
)
```

---

### 4. **src/reports/report_generator.py**
Sistema de geração de relatórios:

#### Geradores:
- **`ExcelReportGenerator`**: Relatórios Excel com múltiplas abas
  - Resumo geral
  - Todas as mensagens
  - Mensagens novas
  - Mensagens urgentes
  - Estatísticas por cliente

- **`CSVReportGenerator`**: Relatórios CSV simples
  - Formato delimitado por ponto-e-vírgula
  - UTF-8 com BOM (compatível Excel)

- **`JSONReportGenerator`**: Relatórios JSON estruturados
  - Dados completos
  - Metadados de geração

#### Uso:
```python
from src.reports import gerar_relatorio

arquivo = gerar_relatorio(
    relatorios,
    formato='excel',
    output_dir='./data/exports'
)
```

---

### 5. **src/navigation/det_navigator.py**
Navegador Selenium para o portal DET:

#### Classe `DETNavigator`:
- **WebDriver**: Configuração anti-detecção
- **Navegação**: URLs e elementos
- **Waits**: Timeouts inteligentes
- **Screenshots**: Captura em caso de erro
- **Context Manager**: Gerenciamento automático de recursos

#### Recursos:
- Auto-download de ChromeDriver
- Delays humanizados
- Waits explícitos
- Modo headless
- Anti-detecção de bot

---

### 6. **src/auth/windows_cert_store.py**
Interface com Windows Certificate Store:

#### Classe `WindowsCertificateStore`:
- **Listagem**: Certificados via PowerShell
- **Extração**: CNPJ/CPF do Subject
- **Validação**: Verificação de expiração
- **Busca**: Por CNPJ, CN ou thumbprint
- **Filtragem**: e-CNPJ, e-CPF, válidos

#### Uso:
```python
from src.auth.windows_cert_store import WindowsCertificateStore

store = WindowsCertificateStore()
certs = store.find_by_cnpj("12.345.678/0001-90")
valid_certs = store.get_valid_certificates()
```

---

### 7. **src/auth/registry_config.py**
Configuração do registro do Windows:

#### Classe `RegistryConfigurator`:
- **Auto-seleção**: Configuração para Chrome/Edge
- **Registro**: Modificação de `HKLM\SOFTWARE\Policies`
- **Validação**: Verificação de configuração
- **Remoção**: Limpeza de configurações

#### Configuração:
```python
from src.auth.registry_config import RegistryConfigurator

config = RegistryConfigurator('chrome')
config.configure_auto_select(
    url_pattern="https://det.sit.trabalho.gov.br",
    issuer_cn="AC SERASA RFB v5"
)
```

---

## 🔧 Scripts Auxiliares

### **scripts/setup_environment.py**
Setup completo automatizado:
- Verifica Python e sistema
- Instala dependências
- Cria arquivos de configuração
- Configura certificados
- Valida tudo

### **scripts/list_certificates.py**
Gerenciamento de certificados:
- Lista certificados instalados
- Busca por CNPJ
- Exporta para JSON
- Interface interativa

### **scripts/setup_auto_certificate.py**
Configuração de auto-seleção:
- Seleção interativa de certificado
- Configuração do registro
- Verificação e remoção
- Modo administrador

### **scripts/validate_config.py**
Validação de configuração:
- Verifica pacotes
- Valida arquivos
- Testa certificados
- Verifica registro
- Testa acesso ao DET

---

## 📊 Configurações

### **config/settings.yaml**
Configurações gerais do sistema:
- Portal DET (URLs, seletores, timeouts)
- Selenium (browser, opções, headless)
- Certificado (método, timeouts)
- Processamento (delays, retry logic)
- Logging (níveis, rotação)
- Exportação (formatos, diretórios)

### **config/clients.yaml**
Lista de clientes (YAML):
```yaml
clients:
  - cnpj: "12.345.678/0001-90"
    razao_social: "EMPRESA EXEMPLO LTDA"
    active: true
    priority: high
```

### **config/clientes.json**
Lista de clientes (JSON):
```json
{
  "clientes": [
    {
      "cnpj": "12.345.678/0001-90",
      "razao_social": "EMPRESA EXEMPLO LTDA",
      "ativo": true,
      "prioridade": "high"
    }
  ]
}
```

### **.env**
Variáveis de ambiente sensíveis:
```env
CERT_PATH=./certs/certificado.pfx
USE_KEYRING=true
BROWSER=chrome
HEADLESS=false
```

---

## 📈 Fluxo de Execução

### 1. **Setup Inicial** (Uma vez)
```bash
python scripts/setup_environment.py
```

### 2. **Configuração**
- Editar `.env`
- Editar `config/clients.yaml` ou `config/clientes.json`

### 3. **Validação**
```bash
python scripts/validate_config.py --full
```

### 4. **Execução**
```bash
python main.py
```

### 5. **Relatórios**
Gerados automaticamente em `data/exports/`:
- Excel: Múltiplas abas com análise completa
- CSV: Dados tabulares
- JSON: Dados estruturados

---

## 🔄 Ciclo de Desenvolvimento

### Adicionar Novo Cliente
1. Editar `config/clients.yaml`
2. Adicionar CNPJ e dados
3. Executar: `python main.py`

### Modificar Seletores CSS
1. Inspecionar portal DET com DevTools
2. Atualizar `DETScraper.SELECTORS` em `src/det_scraper.py`
3. Testar extração

### Adicionar Novo Tipo de Mensagem
1. Adicionar em `TipoMensagem` (src/models/__init__.py)
2. Atualizar `_classificar_tipo_mensagem` (src/det_scraper.py)
3. Ajustar relatórios se necessário

---

## 🧪 Testes

### Teste Manual
```bash
# Debug com navegador visível
python main.py --debug --no-headless

# Cliente específico
python main.py --cnpj 12.345.678/0001-90
```

### Validação Completa
```bash
python scripts/validate_config.py --full
```

---

## 📚 Documentação Relacionada

- **[README.md](README.md)** - Documentação principal
- **[QUICKSTART.md](QUICKSTART.md)** - Guia de início rápido
- **[ANALISE_TECNICA.md](ANALISE_TECNICA.md)** - Análise técnica
- **[scripts/README.md](scripts/README.md)** - Documentação dos scripts

---

**Versão:** 2.0.0
**Última atualização:** 06/12/2025
