# 🤖 Rob-DET 2.0 - Robô de Automação DET (Domicílio Eletrônico Trabalhista)

Robô de automação em Python para consultar mensagens do portal DET (Domicílio Eletrônico Trabalhista) de múltiplos clientes utilizando certificado digital A1 e procuração eletrônica.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Documentação](#documentação)
- [Roadmap](#roadmap)
- [Licença](#licença)

## 🎯 Visão Geral

O **Rob-DET 2.0** automatiza o processo de consulta de mensagens no portal do Domicílio Eletrônico Trabalhista (DET), permitindo que contadores e escritórios de contabilidade monitorem a Caixa Postal de múltiplos CNPJs de forma eficiente e segura.

**Portal DET:** https://det.sit.trabalho.gov.br/

## ✨ Características

- ✅ **Autenticação Automática** com Certificado Digital A1
- ✅ **Multi-Cliente**: Gerenciamento de múltiplos CNPJs via procuração eletrônica
- ✅ **Auto-seleção de Certificado**: Configuração via Registry do Windows ou pywinauto
- ✅ **Extração Inteligente**: Identifica mensagens novas e urgentes
- ✅ **Logging Completo**: Rastreamento de todas as operações
- ✅ **Exportação de Dados**: Relatórios em Excel, CSV ou banco de dados
- ✅ **Agendamento**: Execução automática via schedule/cron
- ✅ **Segurança**: Gerenciamento seguro de credenciais com keyring

## 📦 Requisitos

### Sistema Operacional
- Windows 10/11 (para certificado digital A1)
- Linux (com Wine para suporte a certificados - experimental)

### Software
- Python 3.11 ou superior
- Google Chrome ou Microsoft Edge
- Certificado Digital A1 (e-CNPJ ou e-CPF) válido
- Procuração Eletrônica ativa no SPE para os CNPJs dos clientes

### Dependências Python
Veja `requirements.txt` para lista completa.

Principais bibliotecas:
- `selenium` - Automação web
- `pywinauto` - Automação Windows
- `cryptography` - Gerenciamento de certificados
- `loguru` - Logging avançado
- `pydantic` - Validação de configurações

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/Rob-DET-2.0.git
cd Rob-DET-2.0
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o certificado digital
```bash
# Copie seu certificado .pfx para a pasta segura
mkdir -p certs
# Copie manualmente o arquivo .pfx para certs/
```

### 5. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## ⚙️ Configuração

### 1. Certificado Digital

#### Opção A: Auto-seleção via Registry (Recomendado)
Execute o script de configuração:
```bash
python scripts/setup_certificate_autoselect.py
```

#### Opção B: PyWinAuto (Fallback)
Nenhuma configuração adicional necessária - o robô detectará automaticamente.

### 2. Lista de Clientes

Edite `config/clients.yaml`:
```yaml
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

### 3. Variáveis de Ambiente

Edite `.env`:
```env
# Certificado Digital
CERT_PATH=./certs/certificado.pfx
CERT_PASSWORD=sua_senha_aqui

# Selenium
HEADLESS=false
BROWSER=chrome

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/det_robot.log

# Banco de Dados (opcional)
DATABASE_URL=sqlite:///./data/det_messages.db
```

## 📖 Uso

### Execução Manual

```bash
# Executar para todos os clientes ativos
python main.py

# Executar para um CNPJ específico
python main.py --cnpj 12.345.678/0001-90

# Modo debug (com navegador visível)
python main.py --debug

# Executar apenas mensagens novas
python main.py --only-new
```

### Agendamento Automático

#### Windows Task Scheduler
```bash
# Criar tarefa agendada (executar como administrador)
python scripts/create_scheduled_task.py
```

#### Linux Cron
```bash
# Adicionar ao crontab (executar diariamente às 9h)
0 9 * * * cd /caminho/para/Rob-DET-2.0 && /caminho/para/venv/bin/python main.py
```

### Exemplos de Saída

```
[2025-12-06 09:00:00] INFO  | Iniciando Rob-DET 2.0...
[2025-12-06 09:00:05] INFO  | Certificado digital carregado: EMPRESA EXEMPLO LTDA
[2025-12-06 09:00:10] INFO  | Login realizado com sucesso
[2025-12-06 09:00:15] INFO  | Processando CNPJ: 12.345.678/0001-90
[2025-12-06 09:00:20] INFO  | Encontradas 3 mensagens novas
[2025-12-06 09:00:25] INFO  | Mensagens exportadas para: ./data/exports/2025-12-06_mensagens.xlsx
[2025-12-06 09:00:30] INFO  | Execução concluída com sucesso!
```

## 📚 Documentação

- **[Análise Técnica Completa](ANALISE_TECNICA.md)** - Viabilidade, arquitetura e desafios
- **[Guia de Desenvolvimento](docs/DEVELOPMENT.md)** - Setup para desenvolvedores
- **[API Reference](docs/API.md)** - Documentação dos módulos
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Solução de problemas comuns
- **[FAQ](docs/FAQ.md)** - Perguntas frequentes

## 🗺️ Roadmap

### ✅ Fase 1: Setup e POC (Concluído)
- [x] Análise técnica de viabilidade
- [x] Estrutura inicial do projeto
- [x] Documentação base

### 🚧 Fase 2: Módulos Core (Em Desenvolvimento)
- [ ] Módulo de autenticação com certificado
- [ ] Navegação no portal DET
- [ ] Extração de mensagens da Caixa Postal

### 📋 Fase 3: Multi-Cliente (Planejado)
- [ ] Gerenciamento de múltiplos CNPJs
- [ ] Sistema de procuração eletrônica
- [ ] Fila de processamento

### 📋 Fase 4: Persistência e Relatórios (Planejado)
- [ ] Banco de dados SQLite
- [ ] Exportação para Excel
- [ ] Dashboard de visualização

### 📋 Fase 5: Produção (Planejado)
- [ ] Agendamento automático
- [ ] Notificações por e-mail
- [ ] Deploy em container Docker

## 🛠️ Estrutura do Projeto

```
Rob-DET-2.0/
├── src/
│   ├── auth/              # Autenticação e certificados
│   │   ├── cert_manager.py
│   │   └── registry_config.py
│   ├── navigation/        # Navegação no DET
│   │   ├── det_navigator.py
│   │   └── page_objects.py
│   ├── extraction/        # Extração de dados
│   │   └── message_extractor.py
│   └── utils/             # Utilitários
│       ├── logger.py
│       └── config.py
├── tests/                 # Testes unitários e E2E
├── config/                # Configurações
│   ├── clients.yaml
│   └── settings.yaml
├── scripts/               # Scripts auxiliares
├── logs/                  # Arquivos de log
├── data/                  # Dados e exports
├── certs/                 # Certificados digitais (gitignore)
├── main.py                # Ponto de entrada
├── requirements.txt       # Dependências
├── .env.example           # Exemplo de variáveis de ambiente
├── ANALISE_TECNICA.md     # Análise técnica detalhada
└── README.md              # Este arquivo
```

## 🔒 Segurança

- ⚠️ **NUNCA** commite certificados digitais ou senhas
- ⚠️ Use `.env` para variáveis sensíveis (já incluído no `.gitignore`)
- ⚠️ Utilize `keyring` do sistema para armazenar senhas
- ⚠️ Mantenha logs em diretório seguro
- ⚠️ Implemente rotação de logs para evitar dados sensíveis antigos

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: Minha nova feature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ⚖️ Aviso Legal

Este robô foi desenvolvido para fins de automação legítima de processos contábeis, utilizando procuração eletrônica devidamente autorizada. O uso inadequado ou não autorizado pode violar os termos de uso do portal DET e legislação aplicável.

**Responsabilidades:**
- Certifique-se de ter procuração eletrônica válida para todos os CNPJs
- Respeite os termos de uso do portal DET
- Utilize apenas para fins legítimos e autorizados
- Mantenha a segurança e confidencialidade dos dados dos clientes

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/Rob-DET-2.0/issues)
- **Documentação**: [Wiki do Projeto](https://github.com/seu-usuario/Rob-DET-2.0/wiki)
- **Email**: seu-email@exemplo.com

---

**Desenvolvido com ❤️ para a comunidade contábil brasileira**

**Versão:** 2.0.0-alpha
**Última atualização:** 06/12/2025
