# 🚀 Guia de Início Rápido - Rob-DET 2.0

> **Para usuários iniciantes** - Passo a passo simplificado para começar a usar o robô em minutos!

---

## 📋 Antes de Começar

Você vai precisar de:

- [x] **Computador Windows** (Windows 10 ou 11)
- [x] **Python 3.11 ou superior** → [Baixar aqui](https://www.python.org/downloads/)
- [x] **Certificado Digital A1** (e-CNPJ ou e-CPF) instalado no Windows
- [x] **Procuração Eletrônica** ativa no SPE para os CNPJs que quer monitorar

> **💡 Dica:** Se não sabe se tem Python instalado, abra o Prompt de Comando e digite `python --version`

---

## 🎯 Instalação em 3 Passos

### **Passo 1: Baixar o Projeto**

1. Baixe o projeto como ZIP do GitHub
2. Extraia a pasta `Rob-DET-2.0` para `C:\Rob-DET-2.0`
3. Abra o **Prompt de Comando** (cmd) ou **PowerShell**
4. Navegue até a pasta:
   ```
   cd C:\Rob-DET-2.0
   ```

### **Passo 2: Executar o Instalador**

Digite no prompt:

```bash
python install.py
```

O instalador vai:
- ✅ Verificar se está tudo OK
- ✅ Instalar as bibliotecas necessárias
- ✅ Te guiar pela configuração do certificado
- ✅ Pedir os CNPJs que você quer monitorar
- ✅ Configurar horários de execução

**É só seguir as instruções na tela!** 😊

### **Passo 3: Testar o Navegador (IMPORTANTE!)**

Antes de usar o robô pela primeira vez, teste se o navegador funciona:

```bash
python robo.py
```

No menu, escolha a opção **7 - 🧪 Testar Navegador**

Isso vai:
- ✅ Verificar se Chrome ou Edge está instalado
- ✅ Abrir o navegador para você ver
- ✅ Confirmar que está tudo funcionando

> **⚠️ IMPORTANTE:** Se o navegador não abrir, execute:
> ```bash
> python scripts/diagnosticar_ambiente.py
> ```
> Este script vai tentar corrigir automaticamente os problemas!

---

## 🎮 Usando o Robô

### **Modo Simples (Interface Amigável)**

Digite:

```bash
python robo.py
```

Você verá um menu com opções:

```
╔═══════════════════════════════════════════════════════════════╗
║                    🤖 ROB-DET 2.0                             ║
║              Robô de Automação do Portal DET                 ║
╚═══════════════════════════════════════════════════════════════╝

1  🚀 Executar Robô AGORA (consulta imediata)
2  ⏰ Instalar Execução Automática (agendar)
3  📊 Ver Estatísticas e Relatórios
4  ⚙️  Configurar Certificado
5  👥 Gerenciar Clientes (adicionar/remover)
6  📧 Configurar Notificações por Email
7  🧪 Testar Navegador (diagnóstico)
8  🔍 Verificar Instalação
9  📖 Ajuda e Documentação
0  ❌ Sair

Escolha uma opção [1]:
```

**Escolha a opção 1** para executar imediatamente!

---

## ⏰ Executar Automaticamente

Para o robô executar sozinho todos os dias:

1. No menu do `python robo.py`, escolha a opção **2**
2. Confirme a instalação
3. Pronto! O robô vai executar automaticamente nos horários configurados

Para verificar se funcionou:
- Abra o **Agendador de Tarefas** do Windows
- Procure por tarefas com nome `RobDET_Exec_*`

---

## 📊 Ver Resultados

Os relatórios ficam salvos em:

```
C:\Rob-DET-2.0\relatorios\
```

Você vai encontrar:
- **Excel** (.xlsx) - Com 5 abas de informações
- **CSV** (.csv) - Para importar em outros sistemas
- **JSON** (.json) - Para programadores

---

## 🆘 Problemas Comuns

### **Problema: "Certificado não foi selecionado"**

**Solução:**
1. No menu do robô, escolha a opção **4** (Configurar Certificado)
2. Escolha a opção **2** (Configurar auto-seleção)
3. Tente executar novamente

### **Problema: "CNPJ não encontrado"**

**Solução:**
1. Acesse o portal DET manualmente: https://det.sit.trabalho.gov.br/
2. Veja se o CNPJ aparece na lista de empresas
3. Se não aparecer, você precisa de procuração eletrônica para esse CNPJ

### **Problema: "Erro ao instalar dependências"**

**Solução:**
1. Abra o Prompt de Comando **como Administrador**
2. Execute:
   ```
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

### **Problema: "Python não é reconhecido"**

**Solução:**
1. Baixe e instale o Python: https://www.python.org/downloads/
2. **IMPORTANTE:** Marque a opção "Add Python to PATH" durante a instalação
3. Reinicie o computador
4. Tente novamente

---

## 📧 Receber Notificações por Email

Para receber emails quando houver mensagens importantes:

1. No menu do robô, escolha a opção **6**
2. Siga as instruções para configurar

**Para Gmail:**
- Você precisa criar uma **Senha de App**: https://myaccount.google.com/apppasswords
- Não use sua senha normal do Gmail!

---

## 💡 Dicas Importantes

### ✅ Boas Práticas

1. **Teste primeiro manualmente** antes de agendar
2. **Execute com navegador visível** (não-headless) na primeira vez
3. **Verifique os relatórios** para confirmar que está funcionando
4. **Mantenha o Python atualizado**

### ⚠️ Atenções

1. **Não feche o Windows** nos horários agendados
2. **Mantenha o certificado válido** (renove antes de expirar)
3. **Verifique procurações** regularmente no SPE
4. **Faça backup** dos relatórios importantes

---

## 🎓 Aprendendo Mais

### **Próximos Passos:**

1. ✅ Leia o **README.md** para entender todas as funcionalidades
2. ✅ Veja o **Manual do Usuário** em `docs/MANUAL_USUARIO.md`
3. ✅ Confira o **Troubleshooting** em `docs/TROUBLESHOOTING.md`

### **Vídeos e Tutoriais:**

> 💡 Procure por tutoriais no YouTube: "Rob-DET tutorial"

---

## 📞 Precisa de Ajuda?

- 📧 **Email:** suporte@exemplo.com
- 💬 **GitHub Issues:** [Reportar Problema](https://github.com/seu-usuario/Rob-DET-2.0/issues)
- 📖 **Documentação:** Veja a pasta `docs/`

---

## ✅ Checklist de Início

Use este checklist para garantir que está tudo certo:

- [ ] Python 3.11+ instalado
- [ ] Dependências instaladas (`python install.py`)
- [ ] Certificado Digital instalado no Windows
- [ ] Auto-seleção de certificado configurada
- [ ] Clientes (CNPJs) adicionados em `config/clientes.json`
- [ ] Teste manual executado com sucesso (`python robo.py` → opção 1)
- [ ] Verificou os relatórios em `relatorios/`
- [ ] Instalou execução automática (`python robo.py` → opção 2)

---

## 🎉 Pronto!

Parabéns! Você configurou o Rob-DET 2.0 com sucesso! 🎊

O robô vai monitorar automaticamente a Caixa Postal DET dos seus clientes e gerar relatórios consolidados.

**Boa sorte! 🍀**

---

<p align="center">
  <sub>Rob-DET 2.0 - Automatizando processos trabalhistas com facilidade</sub>
</p>
