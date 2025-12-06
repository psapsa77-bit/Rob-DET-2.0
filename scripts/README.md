# Scripts Utilitários - Rob-DET 2.0

Scripts auxiliares para configuração e gerenciamento do robô de automação DET.

## 📋 Lista de Scripts

### 🚀 Setup e Configuração

#### `setup_environment.py`
**Script principal de configuração do ambiente.**

Executa todas as etapas necessárias para preparar o ambiente:
- Verifica versão do Python
- Instala dependências
- Cria arquivos de configuração (.env, clients.yaml)
- Lista certificados disponíveis
- Configura auto-seleção de certificado

**Uso:**
```bash
# Setup completo (recomendado)
python scripts/setup_environment.py

# Pular configuração de certificado
python scripts/setup_environment.py --skip-cert
```

**IMPORTANTE:** Execute como Administrador para configurar o registro do Windows.

---

#### `setup_auto_certificate.py`
**Configura auto-seleção de certificado digital no Chrome/Edge.**

Configura o registro do Windows para que o navegador selecione automaticamente
o certificado correto ao acessar o portal DET, eliminando o popup manual.

**Uso:**
```bash
# Modo interativo (recomendado)
python scripts/setup_auto_certificate.py

# Especificar navegador
python scripts/setup_auto_certificate.py --browser edge

# Verificar configuração atual
python scripts/setup_auto_certificate.py --verify

# Remover configuração
python scripts/setup_auto_certificate.py --remove
```

**IMPORTANTE:** Requer permissões de Administrador!

**Processo:**
1. Lista certificados digitais instalados
2. Permite selecionar o certificado correto
3. Configura registro do Windows
4. Valida configuração

---

### 🔐 Gerenciamento de Certificados

#### `list_certificates.py`
**Lista certificados digitais instalados no Windows.**

Exibe informações detalhadas sobre todos os certificados A1 disponíveis,
incluindo CNPJ/CPF, validade e status.

**Uso:**
```bash
# Listar todos os certificados
python scripts/list_certificates.py

# Buscar por CNPJ específico
python scripts/list_certificates.py --cnpj 12.345.678/0001-90

# Exportar para JSON
python scripts/list_certificates.py --export data/certificates.json

# Apenas certificados válidos
python scripts/list_certificates.py --valid-only
```

**Exemplo de saída:**
```
📋 Certificados Digitais (3 encontrados)
┌───┬────────────────────────┬──────────┬────────────────────┬──────────────┬────────┐
│ # │ Common Name            │ Tipo     │ Documento          │ Válido até   │ Status │
├───┼────────────────────────┼──────────┼────────────────────┼──────────────┼────────┤
│ 1 │ EMPRESA EXEMPLO LTDA   │ e-CNPJ   │ 12.345.678/0001-90 │ 15/06/2026   │   ✅   │
│ 2 │ JOAO SILVA             │ e-CPF    │ 123.456.789-00     │ 20/08/2025   │   ✅   │
└───┴────────────────────────┴──────────┴────────────────────┴──────────────┴────────┘
```

---

### ✅ Validação

#### `validate_config.py`
**Valida toda a configuração do ambiente.**

Verifica se o ambiente está corretamente configurado antes de executar o robô:
- Dependências Python instaladas
- Arquivos de configuração presentes
- Certificados digitais válidos
- Registro do Windows configurado
- ChromeDriver disponível
- Acesso ao portal DET (opcional)

**Uso:**
```bash
# Validação básica
python scripts/validate_config.py

# Validação completa (inclui teste de acesso ao DET)
python scripts/validate_config.py --full
```

**Exemplo de saída:**
```
📊 RESUMO DA VALIDAÇÃO
┌─────────────────────────┬────────┬──────────────────────┐
│ Verificação             │ Status │ Detalhes             │
├─────────────────────────┼────────┼──────────────────────┤
│ Pacotes Python          │   ✅   │ Todos instalados     │
│ Arquivos configuração   │   ✅   │ Todos encontrados    │
│ Diretórios              │   ✅   │ Estrutura OK         │
│ Certificados            │   ✅   │ 2 e-CNPJ válidos     │
│ Registro Windows        │   ✅   │ Configurado          │
│ ChromeDriver            │   ✅   │ Disponível           │
└─────────────────────────┴────────┴──────────────────────┘

✅ Todas as 6 verificações passaram!
🎉 Ambiente configurado corretamente!
```

---

## 🔄 Fluxo de Uso Recomendado

### 1️⃣ Primeira Vez (Setup Inicial)

```bash
# 1. Executar setup completo (como Administrador)
python scripts/setup_environment.py

# 2. Editar arquivos de configuração
# - .env (certificado, navegador, etc.)
# - config/clients.yaml (CNPJs dos clientes)

# 3. Validar configuração
python scripts/validate_config.py --full

# 4. Testar robô
python main.py --debug
```

### 2️⃣ Adicionar/Modificar Certificado

```bash
# Listar certificados disponíveis
python scripts/list_certificates.py

# Configurar novo certificado (como Administrador)
python scripts/setup_auto_certificate.py

# Validar
python scripts/validate_config.py
```

### 3️⃣ Verificar Configuração Atual

```bash
# Verificar registro do Windows
python scripts/setup_auto_certificate.py --verify

# Validação completa
python scripts/validate_config.py --full
```

---

## ⚠️ Avisos Importantes

### Permissões de Administrador

Os seguintes scripts **REQUEREM** execução como Administrador:
- `setup_environment.py` (para configurar registro)
- `setup_auto_certificate.py`

**Como executar como Administrador:**

**PowerShell:**
```powershell
# Clique direito no PowerShell > "Executar como Administrador"
cd C:\caminho\para\Rob-DET-2.0
python scripts/setup_auto_certificate.py
```

**CMD:**
```cmd
# Clique direito no CMD > "Executar como Administrador"
cd C:\caminho\para\Rob-DET-2.0
python scripts\setup_auto_certificate.py
```

### Configuração do Registro

A configuração de auto-seleção de certificado modifica o registro do Windows em:
- `HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Google\Chrome\AutoSelectCertificateForUrls`
- `HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Edge\AutoSelectCertificateForUrls`

**Para remover a configuração:**
```bash
python scripts/setup_auto_certificate.py --remove
```

---

## 🆘 Solução de Problemas

### Problema: "Nenhum certificado encontrado"

**Solução:**
1. Verifique se o certificado A1 está instalado no Windows
2. Certifique-se de que o certificado tem chave privada
3. Execute: `certmgr.msc` e verifique em "Pessoal > Certificados"

### Problema: "Permissão negada ao configurar registro"

**Solução:**
1. Execute o PowerShell/CMD como Administrador
2. Navegue até a pasta do projeto
3. Execute o script novamente

### Problema: "Certificado não é selecionado automaticamente"

**Solução:**
1. **Feche COMPLETAMENTE o navegador** (verifique no Gerenciador de Tarefas)
2. Abra o navegador novamente
3. Acesse o portal DET
4. Se ainda não funcionar:
   ```bash
   # Verificar configuração
   python scripts/setup_auto_certificate.py --verify

   # Reconfigurar
   python scripts/setup_auto_certificate.py
   ```

### Problema: "ChromeDriver não encontrado"

**Solução:**
```bash
# O webdriver-manager faz download automático
# Se falhar, tente:
pip install --upgrade webdriver-manager

# Ou execute:
python scripts/validate_config.py
```

---

## 📚 Documentação Relacionada

- **[README.md](../README.md)** - Documentação principal do projeto
- **[ANALISE_TECNICA.md](../ANALISE_TECNICA.md)** - Análise técnica completa
- **[.env.example](../.env.example)** - Exemplo de variáveis de ambiente
- **[config/clients.yaml.example](../config/clients.yaml.example)** - Exemplo de configuração de clientes

---

## 🔧 Desenvolvimento

### Adicionar Novo Script

1. Criar arquivo em `scripts/`
2. Adicionar shebang: `#!/usr/bin/env python3`
3. Adicionar docstring descritiva
4. Implementar argparse para parâmetros CLI
5. Usar `rich` para output formatado
6. Documentar neste README
7. Tornar executável (Linux/Mac): `chmod +x scripts/nome.py`

### Convenções

- **Naming**: `snake_case.py`
- **Output**: Usar `rich` (Console, Table, Panel)
- **Errors**: Retornar exit code (0 = sucesso, 1 = erro, 130 = interrompido)
- **Logging**: Usar `loguru` ou `rich.console`
- **Path**: Usar `pathlib.Path` (não strings)

---

**Versão:** 2.0.0
**Última atualização:** 06/12/2025
