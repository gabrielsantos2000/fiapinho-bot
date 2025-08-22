# 🤖 Fiapinho Bot

<div align="center">

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.6.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**Um bot Discord inteligente para estudantes da FIAP** 🎓

*Automatização a sincronização de eventos do calendário acadêmico para manter comunidade sempre atualizada!*

</div>

---

## 📋 Índice

- [🎯 Sobre o Projeto](#-sobre-o-projeto)
- [✨ Funcionalidades](#-funcionalidades)
- [🚀 Instalação e Configuração](#-instalação-e-configuração)
- [📖 Como Usar](#-como-usar)
- [🛠️ Comandos Disponíveis](#️-comandos-disponíveis)
- [🏗️ Arquitetura](#️-arquitetura)
- [🤝 Contribuindo](#-contribuindo)
- [📝 Licença](#-licença)
- [📞 Suporte](#-suporte)

---

## 🎯 Sobre o Projeto

O **Fiapinho Bot** é um bot Discord desenvolvido especificamente para estudantes da FIAP, projetado para automatizar e facilitar o acesso a informações acadêmicas importantes. O bot sincroniza automaticamente eventos do calendário FIAP e envia notificações em tempo real para servidores Discord.

### 🎨 Características Principais

- **🔄 Sincronização Automática**: Monitora e sincroniza eventos do calendário FIAP automaticamente
- **📅 Notificações em Tempo Real**: Alertas instantâneos sobre novos eventos acadêmicos
- **🎯 Interface Amigável**: Comandos intuitivos com embeds visuais elegantes
- **⚙️ Modular e Extensível**: Arquitetura baseada em Cogs para fácil manutenção
- **🛡️ Robusto e Confiável**: Sistema de retry e tratamento de erros abrangente

---

## ✨ Funcionalidades

### 📚 Gestão de Eventos Acadêmicos
- ✅ Sincronização automática com o calendário FIAP
- ✅ Detecção inteligente de novos eventos
- ✅ Notificações com informações detalhadas (data, horário, links)
- ✅ Suporte a diferentes tipos de eventos (aulas, provas, palestras)

### 🎛️ Comandos Administrativos
- ✅ Sincronização manual do calendário
- ✅ Status do sistema em tempo real  
- ✅ Gerenciamento de Cogs (carregar/recarregar/descarregar)
- ✅ Informações detalhadas do bot

### 🔧 Utilitários
- ✅ Comando de ping para verificar latência
- ✅ Informações sobre uptime do bot
- ✅ Sistema de help customizado e interativo

---

## 🚀 Instalação e Configuração

### 📋 Pré-requisitos

- **Python 3.11+** instalado no sistema
- **Discord Bot Token** (criado no [Discord Developer Portal](https://discord.com/developers/applications))
- **Credenciais FIAP** válidas
- **Git** para controle de versão

### ⚡ Instalação Rápida

#### Opção 1: Setup Automático (Recomendado)

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/fiapinho-bot.git
   cd fiapinho-bot
   ```

2. **Execute o script de setup**
   ```bash
   python setup.py
   ```

3. **Configure suas credenciais**
   Edite o arquivo `.env` gerado com suas configurações.

4. **Execute o bot**
   ```bash
   python main.py
   ```

#### Opção 2: Setup Manual

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/fiapinho-bot.git
   cd fiapinho-bot
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   ```
   
   Edite o arquivo `.env` com suas configurações:
   ```env
   # Discord Bot Configuration
   DISCORD_BOT_TOKEN=seu_token_aqui
   DISCORD_MONITORING_CHANNEL_ID=id_do_canal_monitoria
   DISCORD_CALENDAR_CHANNEL_ID=id_do_canal_calendario
   
   # FIAP Credentials  
   FIAP_USERNAME=seu_usuario_fiap
   FIAP_PASSWORD=sua_senha_fiap
   FIAP_LOGIN_URL=https://on.fiap.com.br/index.php
   FIAP_API_BASE=https://on.fiap.com.br/lib/ajax/service.php
   
   # Bot Configuration
   BOT_PREFIX=!
   
   # Webhook Configuration
   WEBHOOK_INTERVAL_HOURS=60
   MAX_LOGIN_RETRIES=3
   
   # Logging
   LOG_LEVEL=INFO
   LOG_FILE=logs/bot.log
   ```

4. **Execute o bot**
   ```bash
   python main.py
   ```

### 🔐 Configuração de Permissões do Discord

O bot precisa das seguintes permissões no seu servidor Discord:

- ✅ **Ler Mensagens** - Para processar comandos
- ✅ **Enviar Mensagens** - Para responder comandos e notificações
- ✅ **Usar Emojis Externos** - Para embeds mais ricos
- ✅ **Anexar Arquivos** - Para enviar imagens em notificações
- ✅ **Incorporar Links** - Para criar embeds
- ✅ **Ler Histórico de Mensagens** - Para funcionalidades avançadas

---

## 📖 Como Usar

### 🎮 Comandos Básicos

Após adicionar o bot ao seu servidor Discord, você pode começar a usar os comandos. Por padrão, o prefixo é `!`.

```
!help              # Mostra todos os comandos disponíveis
!ping               # Verifica a latência do bot
!status             # Exibe o status do sistema
!info               # Informações sobre o bot
```

### 🔧 Comandos Administrativos

> **⚠️ Importante**: Comandos administrativos requerem permissões especiais

```
!fiap sync_calendar    # Força sincronização manual do calendário
!reload <cog_name>     # Recarrega um cog específico (owner only)
!cogs                  # Lista todos os cogs carregados (owner only)
```

### 📅 Funcionalidades Automáticas

O bot executa automaticamente as seguintes tarefas:

- **Sincronização Periódica**: A cada 24 horas (configurável)
- **Detecção de Novos Eventos**: Compara com eventos já conhecidos
- **Notificações Automáticas**: Envia alertas para o canal configurado

---

## 🛠️ Comandos Disponíveis

### 📂 Comandos Principais

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `help` | Exibe lista de comandos ou ajuda específica | `!help` ou `!help ping` |
| `ping` | Verifica latência do bot | `!ping` |
| `status` | Mostra status completo do sistema | `!status` |
| `info` | Informações detalhadas do bot | `!info` |
| `uptime` | Tempo de atividade do bot | `!uptime` |
| `version` | Versão atual do bot | `!version` |

### 📚 Comandos FIAP

| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `fiap` | Menu principal dos comandos FIAP | Todos |
| `fiap sync_calendar` | Força sincronização manual | Admin |
| `fiap events_monthly` | Exibe eventos do mês | Admin |

### ⚙️ Comandos Administrativos

| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `reload <cog>` | Recarrega um cog específico | Owner |
| `load <cog>` | Carrega um cog | Owner |
| `unload <cog>` | Descarrega um cog | Owner |
| `cogs` | Lista cogs carregados | Owner |

---

## 🏗️ Arquitetura

### 📁 Estrutura do Projeto

```
fiapinho-bot/
├── 📁 app/                          # Código principal da aplicação
│   ├── 📁 cogs/                     # Módulos de comandos (Cogs)
│   │   ├── fiap.py                  # Comandos relacionados à FIAP
│   │   └── utility.py               # Comandos utilitários
│   ├── 📁 enum/                     # Enumerações e constantes
│   │   ├── colors.py                # Cores para embeds
│   │   └── discord/roles.py         # Definições de roles
│   ├── 📁 utils/                    # Utilitários e helpers
│   │   ├── format_datetime.py       # Formatação de datas
│   │   └── discord/notifications.py # Sistema de notificações
│   └── 📁 webhooks/                 # Sistema de webhooks e sync
│       ├── webhook.py               # Gerenciador de webhooks
│       ├── 📁 core/                 # Núcleo do sistema
│       │   ├── base.py              # Classe base para webhooks
│       │   └── fiap_auth.py         # Autenticação FIAP
│       └── 📁 sync_calendar/        # Sincronização de calendário
│           ├── app.py               # Lógica principal de sync
│           └── evens_api.py         # Interface com API FIAP
├── 📁 src/images/                   # Imagens e assets
├── 📁 logs/                         # Logs do sistema
├── main.py                          # Ponto de entrada do bot
├── requirements.txt                 # Dependências Python
├── .env.example                     # Exemplo de configuração
└── README.md                        # Este arquivo
```

### 🔧 Tecnologias Utilizadas

- **[discord.py](https://discordpy.readthedocs.io/)** `2.6.0` - Framework para Discord bots
- **[aiohttp](https://docs.aiohttp.org/)** `3.12.15` - Cliente HTTP assíncrono
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** `1.1.1` - Gerenciamento de variáveis de ambiente
- **[validators](https://python-validators.github.io/validators/)** `0.34.0` - Validação de dados

### 🎯 Padrões de Design

- **Cogs Pattern**: Organização modular de comandos
- **Webhook Pattern**: Sistema de notificações assíncronas
- **Factory Pattern**: Criação de embeds e notificações
- **Observer Pattern**: Monitoramento de eventos FIAP

---

## 🤝 Contribuindo

Adoramos contribuições! Seja você um estudante da FIAP ou um desenvolvedor interessado em ajudar, sua contribuição é bem-vinda.

### 🚦 Primeiros Passos

1. **🍴 Fork o repositório**
2. **📥 Clone seu fork**
   ```bash
   git clone https://github.com/seu-usuario/fiapinho-bot.git
   cd fiapinho-bot
   ```
3. **🔧 Configure o ambiente de desenvolvimento**
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Configure suas variáveis de ambiente
   ```

### 🌟 Processo de Contribuição

#### 1. 📝 Crie ou Encontre uma Issue

- **Novos recursos**: Abra uma issue descrevendo a funcionalidade
- **Bugs**: Descreva o problema detalhadamente
- **Melhorias**: Explique o que pode ser otimizado

#### 2. 🌿 Criação de Branch

Use o padrão de nomenclatura baseado na issue:

```bash
# Para features
git checkout -b feature/issue-123-add-new-command

# Para correções
git checkout -b fix/issue-456-calendar-sync-error

# Para melhorias
git checkout -b improvement/issue-789-optimize-api-calls

# Para documentação
git checkout -b docs/issue-101-update-readme
```

#### 3. 💻 Desenvolvimento

- **📏 Siga o estilo de código Python** (PEP 8)
- **🧪 Teste suas alterações** localmente
- **📝 Documente funções e classes** importantes
- **🔍 Use type hints** sempre que possível

#### 4. 📤 Commit Guidelines

Usamos o padrão **Conventional Commits**:

```bash
# Formato
<type>[optional scope]: <description>

# Exemplos
feat: add monthly events display command
fix(calendar): resolve sync timing issue
docs: update installation instructions
style: format code according to PEP 8
refactor(webhooks): simplify error handling
test: add unit tests for utility functions
chore: update dependencies to latest versions
```

**Tipos de commit:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação de código
- `refactor`: Refatoração de código
- `test`: Testes
- `chore`: Tarefas de manutenção

#### 5. 🚀 Pull Request

1. **📋 Use o template de PR** (será criado automaticamente)
2. **✅ Descreva suas alterações** claramente
3. **🔗 Referencie a issue** usando `Fixes #123`
4. **🧪 Confirme que os testes passam**
5. **📸 Adicione screenshots** se aplicável

### 📋 Checklist do Contributor

- [ ] Fork do repositório feito
- [ ] Branch criada com nome apropriado
- [ ] Código segue as convenções do projeto
- [ ] Documentação atualizada se necessário
- [ ] Testes passando localmente
- [ ] Commits seguem o padrão estabelecido
- [ ] Pull Request criado com descrição clara

### 🐛 Reportando Bugs

Ao reportar bugs, inclua:

- **🖥️ Sistema operacional** e versão do Python
- **📝 Passos para reproduzir** o problema
- **📋 Comportamento esperado** vs **atual**
- **📊 Logs relevantes** (sem informações sensíveis)
- **📸 Screenshots** se aplicável

### 💡 Sugerindo Funcionalidades

Para sugerir novas funcionalidades:

- **🎯 Descreva o problema** que a funcionalidade resolve
- **📖 Explique a solução** proposta
- **🔍 Considere alternativas** que foram pensadas
- **📈 Avalie o impacto** nos usuários existentes

### 🏷️ Labels das Issues

- `bug` - Algo não está funcionando
- `enhancement` - Nova funcionalidade ou melhoria
- `good first issue` - Boa para iniciantes
- `help wanted` - Ajuda extra é bem-vinda
- `documentation` - Melhorias na documentação
- `question` - Dúvida ou discussão

---

## 🛡️ Testes

### 🔍 Teste Manual

1. **Configure um servidor Discord de teste**
2. **Use credenciais FIAP**
3. **Teste todos os comandos** básicos
4. **Verifique logs** para erros

---

## 📊 Roadmap

### 🎯 Versão Atual (v0.1.0)
- ✅ Sistema básico de comandos
- ✅ Sincronização de calendário FIAP
- ✅ Notificações de eventos
- ✅ Sistema de webhooks

### 🚀 Próximas Versões

**v0.2.0** - Melhorias na UX
- [ ] Comandos de configuração por servidor
- [ ] Sistema de preferências de usuário

**v0.3.0** - Recursos Avançados
- [ ] Integração com outros sistemas FIAP
- [ ] Lembretes personalizáveis

**v1.0.0** - Estável
- [ ] Documentação completa da API
- [ ] Deploy automatizado

---

## 🔒 Segurança

### 🛡️ Boas Práticas

- **🔐 Nunca commite** credenciais ou tokens
- **🔒 Use variáveis de ambiente** para informações sensíveis
- **🧹 Mantenha dependências** atualizadas
- **📋 Revise PRs** cuidadosamente

### 🚨 Reportando Vulnerabilidades

Encontrou uma vulnerabilidade de segurança? 

📧 **Envie uma mensagem para os responsáveis no discord**

**Não** abra issues públicas para vulnerabilidades de segurança.

---

## 📝 Licença

Este projeto está licenciado sob a **Licença MIT** - veja o arquivo [LICENSE](LICENSE) para detalhes.

```
MIT License

Copyright (c) 2024 Fiapinho Bot Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Suporte

### 💬 Canais de Comunicação

- **📋 Issues do GitHub**: Para bugs e sugestões de recursos
- **💬 Discord**: Servidor da comunidade

### 📚 Recursos Úteis

- **🔗 Discord.py Docs**: https://discordpy.readthedocs.io/
- **🎓 FIAP**: https://www.fiap.com.br/
- **🐍 Python Docs**: https://docs.python.org/3/

### ❓ FAQ

**Q: O bot não está respondendo aos comandos**
A: Verifique se o bot tem as permissões necessárias e se o prefix está correto.

**Q: A sincronização de calendário não está funcionando**
A: Confirme suas credenciais FIAP e verifique os logs para mensagens de erro.

**Q: Como posso contribuir se sou iniciante?**
A: Procure issues com a label `good first issue` e não hesite em pedir ajuda!

---

<div align="center">

### 🌟 Desenvolvido com ❤️ para a comunidade FIAP

**Se este projeto foi útil para você, considere dar uma ⭐ no repositório!**

[⬆️ Voltar ao topo](#-fiapinho-bot)

</div>
