# Análise Técnica - Robô de Automação DET (Domicílio Eletrônico Trabalhista)

## 1. VISÃO GERAL DO PROJETO

O Domicílio Eletrônico Trabalhista (DET) é um sistema federal gerenciado pela Secretaria de Inspeção do Trabalho (SIT) do Ministério do Trabalho e Emprego, que permite comunicação eletrônica entre a Auditoria-Fiscal do Trabalho e empregadores.

**URL do Portal:** https://det.sit.trabalho.gov.br/

### Objetivo do Robô
Automatizar o acesso ao portal DET para consultar mensagens recebidas na Caixa Postal de múltiplos CNPJs de clientes, utilizando procuração eletrônica (SPE - Sistema de Procuração Eletrônica).

---

## 2. ANÁLISE DE VIABILIDADE TÉCNICA

### 2.1. Métodos de Autenticação Disponíveis

#### Opção 1: Certificado Digital e-CNPJ (A1)
**Viabilidade: ⭐⭐⭐⭐ (RECOMENDADO)**

- **Vantagens:**
  - Automação totalmente possível
  - Não requer interação do usuário após configuração inicial
  - Ideal para ambientes corporativos
  - Permite acesso via procuração eletrônica (SPE)

- **Desafios:**
  - Popup de seleção de certificado é elemento nativo do Windows
  - Requer configuração de registro do Windows OU automação com pywinauto
  - Necessita gerenciamento seguro do certificado e senha

- **Solução Técnica:**
  ```
  1. Configurar auto-seleção via Registro do Windows (método preferencial)
  2. OU usar pywinauto para automação do popup
  3. Gerenciar certificado .pfx e senha de forma segura
  ```

#### Opção 2: Gov.br (Conta Pessoal)
**Viabilidade: ⭐⭐ (NÃO RECOMENDADO para automação)**

- **Vantagens:**
  - Não requer certificado digital
  - Interface web padrão

- **Desafios:**
  - Pode ter autenticação multi-fator (2FA)
  - Captchas podem bloquear automação
  - Menos adequado para procuração eletrônica
  - Viola termos de uso da maioria dos portais governamentais

- **Conclusão:** Não recomendado para automação

---

## 3. ARQUITETURA PROPOSTA

### 3.1. Stack Tecnológico

```
┌─────────────────────────────────────────────┐
│           Robô DET - Arquitetura            │
├─────────────────────────────────────────────┤
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │   Camada de Orquestração              │ │
│  │   - Gerenciamento de múltiplos CNPJs  │ │
│  │   - Agendamento de tarefas            │ │
│  │   - Logging e monitoramento           │ │
│  └───────────────────────────────────────┘ │
│                    ↓                        │
│  ┌───────────────────────────────────────┐ │
│  │   Camada de Navegação (Selenium)      │ │
│  │   - Acesso ao portal DET              │ │
│  │   - Navegação na Caixa Postal         │ │
│  │   - Extração de mensagens             │ │
│  └───────────────────────────────────────┘ │
│                    ↓                        │
│  ┌───────────────────────────────────────┐ │
│  │   Camada de Autenticação              │ │
│  │   - Gerenciamento de certificado A1   │ │
│  │   - Auto-seleção de certificado       │ │
│  │   - pywinauto (fallback para popup)   │ │
│  └───────────────────────────────────────┘ │
│                    ↓                        │
│  ┌───────────────────────────────────────┐ │
│  │   Camada de Dados                     │ │
│  │   - Armazenamento de mensagens        │ │
│  │   - Base de CNPJs e configurações     │ │
│  │   - Logs de execução                  │ │
│  └───────────────────────────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```

### 3.2. Componentes Principais

#### 3.2.1. Módulo de Autenticação (`auth_manager.py`)
- Gerenciamento de certificados digitais A1
- Configuração automática do registro do Windows
- Fallback com pywinauto para popup de certificado
- Gerenciamento seguro de credenciais

#### 3.2.2. Módulo de Navegação DET (`det_navigator.py`)
- Inicialização do Selenium WebDriver
- Acesso ao portal DET
- Navegação na Caixa Postal
- Seleção de CNPJ via procuração
- Extração de mensagens

#### 3.2.3. Módulo de Processamento (`message_processor.py`)
- Parser de mensagens recebidas
- Identificação de mensagens novas vs. lidas
- Classificação por tipo/urgência
- Exportação de dados

#### 3.2.4. Módulo de Orquestração (`orchestrator.py`)
- Gerenciamento de múltiplos CNPJs
- Controle de fluxo de execução
- Tratamento de erros e retry logic
- Agendamento de tarefas

---

## 4. BIBLIOTECAS PYTHON NECESSÁRIAS

### 4.1. Core - Automação Web
```python
selenium >= 4.15.0        # Automação do navegador
webdriver-manager >= 4.0  # Gerenciamento automático de drivers
```

### 4.2. Automação Windows (Certificado Digital)
```python
pywinauto >= 0.6.8        # Automação de elementos Windows
pyautogui >= 0.9.54       # Fallback para automação de teclado/mouse
pillow >= 10.0.0          # Suporte a reconhecimento de imagem
```

### 4.3. Gerenciamento de Certificados
```python
cryptography >= 41.0.0    # Manipulação de certificados .pfx
pyOpenSSL >= 23.0.0       # Interface OpenSSL para Python
```

### 4.4. Configuração e Dados
```python
python-dotenv >= 1.0.0    # Variáveis de ambiente
pydantic >= 2.5.0         # Validação de configurações
PyYAML >= 6.0             # Arquivos de configuração
```

### 4.5. Logging e Monitoramento
```python
loguru >= 0.7.0           # Logging avançado
rich >= 13.0.0            # Terminal output formatado
```

### 4.6. Agendamento (Opcional)
```python
schedule >= 1.2.0         # Agendamento de tarefas
APScheduler >= 3.10.0     # Alternativa mais robusta
```

### 4.7. Banco de Dados (Opcional)
```python
SQLAlchemy >= 2.0.0       # ORM para persistência
pandas >= 2.1.0           # Manipulação e exportação de dados
openpyxl >= 3.1.0         # Exportação para Excel
```

---

## 5. DESAFIOS TÉCNICOS E SOLUÇÕES

### 5.1. ❌ DESAFIO #1: Popup de Seleção de Certificado Digital

**Problema:**
O popup de seleção de certificado é um elemento nativo do Windows, não acessível via Selenium.

**Soluções Propostas:**

#### Solução A: Registro do Windows (PREFERENCIAL)
```
Configurar auto-seleção de certificado via Registry:

HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Google\Chrome\AutoSelectCertificateForUrls

Valor JSON:
{
  "pattern": "https://det.sit.trabalho.gov.br",
  "filter": {
    "ISSUER": {
      "CN": "AC SERASA RFB v5"
    }
  }
}
```

**Vantagens:**
- Sem interação visual necessária
- Rápido e confiável
- Funciona mesmo com navegador em headless

**Desvantagens:**
- Requer permissões de administrador
- Específico para Chrome/Edge

#### Solução B: PyWinAuto (FALLBACK)
```python
from pywinauto import Desktop

# Aguardar popup de certificado
popup = Desktop(backend="uia").window(title_re=".*Certificado.*")
popup.wait('visible', timeout=10)

# Selecionar primeiro certificado e confirmar
popup['ListBox'].select(0)
popup['OK'].click()
```

**Vantagens:**
- Não requer alteração de registro
- Funciona em qualquer navegador

**Desvantagens:**
- Requer modo visual (não headless)
- Pode ser mais lento
- Sensível a mudanças na UI do Windows

### 5.2. ❌ DESAFIO #2: Detecção de Automação

**Problema:**
Portais governamentais podem detectar e bloquear automação via Selenium.

**Soluções:**

```python
# Usar opções anti-detecção
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Usar undetected-chromedriver (biblioteca adicional)
import undetected_chromedriver as uc
driver = uc.Chrome(options=options)
```

### 5.3. ❌ DESAFIO #3: Gerenciamento de Múltiplos CNPJs

**Problema:**
Precisar alternar entre diferentes CNPJs via procuração durante a mesma sessão.

**Solução:**

```python
class DETMultiClientManager:
    def __init__(self, driver):
        self.driver = driver
        self.current_cnpj = None

    def switch_to_cnpj(self, cnpj):
        """Seleciona CNPJ via dropdown de procuração"""
        # 1. Localizar dropdown de seleção de empresa
        # 2. Selecionar CNPJ específico
        # 3. Aguardar carregamento da página
        # 4. Atualizar self.current_cnpj
        pass

    def get_messages_for_cnpj(self, cnpj):
        """Obtém mensagens de um CNPJ específico"""
        if self.current_cnpj != cnpj:
            self.switch_to_cnpj(cnpj)
        return self.scrape_mailbox()
```

### 5.4. ❌ DESAFIO #4: Segurança de Credenciais

**Problema:**
Armazenar senha do certificado .pfx de forma segura.

**Soluções:**

1. **Variáveis de Ambiente** (Básico)
```python
import os
from dotenv import load_dotenv

load_dotenv()
cert_password = os.getenv('CERT_PASSWORD')
```

2. **Keyring do Sistema** (Recomendado)
```python
import keyring

# Armazenar
keyring.set_password('det_robot', 'cert_password', 'minha_senha')

# Recuperar
password = keyring.get_password('det_robot', 'cert_password')
```

3. **Azure Key Vault / AWS Secrets Manager** (Produção)
Para ambientes corporativos com infraestrutura cloud.

### 5.5. ❌ DESAFIO #5: Timeout e Carregamento Lento

**Problema:**
Páginas governamentais podem ter carregamento lento ou intermitente.

**Solução:**

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class RobustWaiter:
    def __init__(self, driver, default_timeout=30):
        self.driver = driver
        self.wait = WebDriverWait(driver, default_timeout)

    def wait_for_element(self, by, value, timeout=None):
        """Aguarda elemento com retry logic"""
        wait_time = timeout or self.default_timeout
        return self.wait.until(
            EC.presence_of_element_located((by, value))
        )

    def wait_for_clickable(self, by, value, timeout=None):
        """Aguarda elemento clicável"""
        wait_time = timeout or self.default_timeout
        return self.wait.until(
            EC.element_to_be_clickable((by, value))
        )
```

---

## 6. PRINCIPAIS RISCOS

### 6.1. Riscos Técnicos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Mudanças na estrutura HTML do portal | Média | Alto | Usar seletores robustos (ID, data-attributes), monitoramento contínuo |
| Bloqueio por detecção de bot | Baixa | Alto | undetected-chromedriver, delays humanizados |
| Expiração de certificado digital | Alta | Crítico | Monitoramento de validade, alertas antecipados |
| Timeout em carregamentos | Média | Médio | Waits explícitos, retry logic com backoff |
| Problemas com popup de certificado | Média | Alto | Dupla estratégia: Registry + pywinauto |

### 6.2. Riscos de Segurança

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Exposição de senha do certificado | Média | Crítico | Keyring, variáveis de ambiente, nunca commitar |
| Acesso não autorizado ao sistema | Baixa | Crítico | Logs de auditoria, controle de acesso |
| Vazamento de dados de clientes | Baixa | Crítico | Criptografia de dados sensíveis, LGPD compliance |

### 6.3. Riscos Legais/Regulatórios

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Violação de termos de uso do portal | Média | Alto | Revisar termos, consultar jurídico |
| Problemas com procuração eletrônica | Baixa | Médio | Documentar procurações válidas |
| LGPD - tratamento de dados sensíveis | Média | Alto | Política de privacidade, termo de uso |

---

## 7. PLANO DE IMPLEMENTAÇÃO - ETAPAS

### 📋 FASE 1: Setup e Prova de Conceito (1-2 semanas)

**Objetivos:**
- Configurar ambiente de desenvolvimento
- Validar acesso ao portal DET com certificado
- Testar automação do popup de certificado

**Entregáveis:**
- [ ] Ambiente virtual Python configurado
- [ ] Selenium instalado e funcional
- [ ] Acesso manual ao DET com certificado
- [ ] Teste de auto-seleção de certificado (Registry OU pywinauto)
- [ ] Script POC: login automático no DET

**Código POC:**
```python
# poc_login_det.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def test_det_login():
    options = Options()
    # Configurar certificado via Registry primeiro

    driver = webdriver.Chrome(options=options)
    driver.get('https://det.sit.trabalho.gov.br/')

    # Aguardar popup de certificado (se Registry não funcionar)
    # pywinauto aqui

    time.sleep(5)
    print("Login OK" if "det.sit.trabalho.gov.br" in driver.current_url else "Falha")
    driver.quit()

if __name__ == '__main__':
    test_det_login()
```

---

### 📋 FASE 2: Módulos Core (2-3 semanas)

**Objetivos:**
- Desenvolver módulo de autenticação robusto
- Implementar navegação no DET
- Criar extração de mensagens da Caixa Postal

**Entregáveis:**
- [ ] `auth_manager.py` - Gerenciamento de certificado
- [ ] `det_navigator.py` - Navegação no portal
- [ ] `message_extractor.py` - Scraping de mensagens
- [ ] Testes unitários básicos
- [ ] Logging estruturado

**Estrutura de Arquivos:**
```
det_robot/
├── src/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── cert_manager.py
│   │   └── registry_config.py
│   ├── navigation/
│   │   ├── __init__.py
│   │   ├── det_navigator.py
│   │   └── page_objects.py
│   ├── extraction/
│   │   ├── __init__.py
│   │   └── message_extractor.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── config.py
├── tests/
├── config/
│   └── config.yaml
└── requirements.txt
```

---

### 📋 FASE 3: Multi-Cliente e Procuração (1-2 semanas)

**Objetivos:**
- Implementar troca entre CNPJs via procuração
- Criar gerenciamento de múltiplos clientes
- Desenvolver sistema de filas

**Entregáveis:**
- [ ] `multi_client_manager.py` - Gestão de múltiplos CNPJs
- [ ] Configuração de lista de clientes (YAML/JSON)
- [ ] Sistema de fila de processamento
- [ ] Tratamento de erros por cliente

**Exemplo de Configuração:**
```yaml
# config/clients.yaml
clients:
  - cnpj: "12.345.678/0001-90"
    razao_social: "Empresa A Ltda"
    active: true
    priority: high

  - cnpj: "98.765.432/0001-10"
    razao_social: "Empresa B S.A."
    active: true
    priority: normal
```

---

### 📋 FASE 4: Persistência e Relatórios (1 semana)

**Objetivos:**
- Armazenar mensagens extraídas
- Gerar relatórios consolidados
- Implementar detecção de mensagens novas

**Entregáveis:**
- [ ] Banco de dados SQLite/PostgreSQL
- [ ] Modelos de dados (SQLAlchemy)
- [ ] Exportação para Excel
- [ ] Relatório de mensagens novas
- [ ] Dashboard simples (opcional)

---

### 📋 FASE 5: Agendamento e Produção (1 semana)

**Objetivos:**
- Automatizar execução periódica
- Implementar notificações
- Preparar para ambiente de produção

**Entregáveis:**
- [ ] Agendamento automático (schedule/cron)
- [ ] Notificações por e-mail/Telegram (opcional)
- [ ] Documentação de deploy
- [ ] Monitoramento de erros
- [ ] Backup de configurações

**Opções de Deploy:**
1. **Windows Task Scheduler** (simples)
2. **Docker Container** (isolado)
3. **Servidor Linux + Cron** (robusto)

---

### 📋 FASE 6: Testes e Refinamento (1 semana)

**Objetivos:**
- Testes end-to-end
- Otimização de performance
- Documentação final

**Entregáveis:**
- [ ] Suite de testes completa
- [ ] Documentação de usuário
- [ ] Manual de troubleshooting
- [ ] Vídeo tutorial (opcional)

---

## 8. ESTIMATIVA DE ESFORÇO

**Total:** 7-11 semanas (desenvolvimento + testes)

**Breakdown:**
- Desenvolvimento: 60%
- Testes e Debug: 25%
- Documentação: 10%
- Contingência: 5%

**Recursos Necessários:**
- 1 Desenvolvedor Python (senior/pleno)
- Acesso ao portal DET com procuração válida
- Certificado digital A1 ativo
- Máquina Windows para desenvolvimento/testes

---

## 9. MÉTRICAS DE SUCESSO

### KPIs Técnicos
- ✅ Taxa de sucesso de login: > 95%
- ✅ Tempo médio de extração por CNPJ: < 2 minutos
- ✅ Taxa de detecção de mensagens novas: 100%
- ✅ Uptime do robô: > 99%

### KPIs de Negócio
- ✅ Redução de tempo manual: > 80%
- ✅ Número de CNPJs monitorados: sem limite
- ✅ Alertas de mensagens urgentes: tempo real

---

## 10. PRÓXIMOS PASSOS RECOMENDADOS

1. ✅ **Validar Procuração Eletrônica**
   - Confirmar que você possui procuração ativa no SPE para todos os CNPJs
   - Testar acesso manual ao DET de cada cliente

2. ✅ **Preparar Certificado Digital**
   - Exportar certificado A1 no formato .pfx
   - Documentar senha segura (keyring)

3. ✅ **Setup Ambiente**
   - Instalar Python 3.11+
   - Criar virtual environment
   - Instalar dependências básicas

4. ✅ **Executar POC (Fase 1)**
   - Validar login automático
   - Testar popup de certificado
   - Confirmar acesso à Caixa Postal

5. ✅ **Desenvolver em Iterações**
   - Seguir fases propostas
   - Testes contínuos com dados reais
   - Ajustar conforme necessário

---

## 11. REFERÊNCIAS

- [Manual Oficial DET](https://det.sit.trabalho.gov.br/manual/)
- [Documentação Selenium Python](https://selenium-python.readthedocs.io/)
- [PyWinAuto Documentation](https://pywinauto.readthedocs.io/)
- [Automação com Certificados Digitais - Discussão Python Brasil](https://groups.google.com/g/python-brasil/c/fNq5FxkQ5M0)
- [Selenium & Certificados - Stack Overflow](https://stackoverflow.com/questions/67929713/selenium-webdriver-to-access-e-cac-using-certificate-a1)

---

## 12. CONCLUSÃO

A automação do DET é **tecnicamente viável** e **altamente recomendada** para contadores que gerenciam múltiplos clientes.

**Principais Pontos:**
- ✅ Certificado Digital A1 é a melhor abordagem
- ✅ Dupla estratégia para popup (Registry + pywinauto)
- ✅ Arquitetura modular permite manutenção fácil
- ⚠️ Atenção especial à segurança de credenciais
- ⚠️ Monitoramento contínuo de mudanças no portal

**ROI Esperado:** Alta redução de tempo manual, minimização de erros humanos, e escalabilidade ilimitada para novos clientes.

---

**Documento preparado em:** 06/12/2025
**Versão:** 1.0
**Status:** Pronto para implementação
