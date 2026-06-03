#  Zana AI — Assistente de Decisões Agronômicas

Assistente agronômica inteligente que combina dados operacionais da fazenda 
com IA para responder perguntas como *"Qual talhão está em risco de seca?"* 
ou *"Qual a dose recomendada de glifosato para soja?"*.

##  Arquitetura

[Interface Web] → [FastAPI Backend] → [Agente LangGraph]
↓
┌─────────────┴──────────────┐
↓                            ↓
[GraphQL API]              [RAG - ChromaDB]
↓                            ↓
[PostgreSQL DB]          [Manuais e Bulas PDF]

##  Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Interface | HTML + CSS + JavaScript |
| Backend | FastAPI + Uvicorn |
| Agente IA | LangGraph + Groq (LLaMA 3.3) |
| API de Dados | GraphQL + Strawberry |
| Banco de Dados | PostgreSQL + SQLAlchemy |
| Busca Semântica | ChromaDB + SentenceTransformers |
| RAG | LangChain Community |

##  Estrutura do Projeto

zana_ai/
├── ai_service/          # Agente LangGraph e ferramentas
│   ├── agent.py         # Configuração do agente
│   └── tools.py         # Tools: GraphQL + RAG
├── api_graphql/         # Servidor GraphQL
│   ├── graphql_types.py # Types Strawberry
│   ├── queries.py       # Queries e lógica de negócio
│   └── server.py        # App FastAPI + GraphQL
├── backend/             # Interface web
│   ├── main.py          # Rotas FastAPI
│   └── templates/
│       └── chat.html    # Interface do chat
├── database/            # Modelos e inicialização
│   ├── models.py        # Modelos SQLAlchemy
│   └── init_db.py       # Script de população
├── rag/                 # Sistema RAG
│   ├── documentos/      # PDFs e manuais técnicos
│   ├── indexar_documentos.py
│   └── buscar_documentos.py
├── .env                 # Variáveis de ambiente (não commitado)
└── requirements.txt     # Dependências do projeto

##  Como Executar

### Pré-requisitos
- Python 3.11+
- PostgreSQL instalado e rodando
- Chave de API do Groq (gratuita em console.groq.com)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/zana-ai.git
cd zana_ai

# Crie o ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais
```

### Banco de Dados

```bash
# Crie o banco e popule com dados de exemplo
cd database
python init_db.py
```

### Indexação de Documentos

```bash
# Indexe os manuais técnicos no ChromaDB
python rag/indexar_documentos.py
```

### Execução

```bash
# Terminal 1 — API GraphQL (porta 8001)
uvicorn api_graphql.server:app --reload --port 8001

# Terminal 2 — Interface Web (porta 8000)
uvicorn backend.main:app --reload --port 8000
```

Acesse **http://localhost:8000** no navegador.

##  Exemplos de Uso

- *"Quais talhões temos na fazenda?"*
- *"Existe algum talhão em risco de seca agora?"*
- *"Qual a dose recomendada de glifosato para soja?"*
- *"Como controlar a ferrugem asiática na soja?"*
- *"Me dê detalhes do talhão 1"*

##  Próximos Passos

- [ ] Nova interface
- [ ] Autenticação de usuários
- [ ] Dashboard com gráficos de NDVI
- [ ] Integração com APIs de clima em tempo real
- [ ] App mobile
- [ ] Deploy em nuvem (Railway ou Render)

