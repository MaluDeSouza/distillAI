📐 Documento de Arquitetura: DistillAI
1. Visão Geral do Sistema
O DistillAI é uma plataforma voltada para a criação automatizada de agentes de suporte Nível 1. O sistema ingere históricos brutos de conversas (WhatsApp/Chats) e, através de LLMs, destila esses dados em regras estruturadas, gerando um agente calibrado com árvores de decisão e um mecanismo resiliente de transição para operadores humanos (handoff).

2. Stack Tecnológico
Backend Framework: FastAPI (Assíncrono, alta performance).

Orquestração de IA: Agno Framework (para gerenciamento de múltiplos agentes e ferramentas).

Modelos de Linguagem: Google Gemini (Gemini Pro para destilação e Flash para o runtime de atendimento).

Banco de Dados: PostgreSQL + pgvector (persistência de configurações dos bots e busca semântica de contextos).

Ambiente e Dependências: Python 3.11+, Virtualenv, Pydantic v2 (validação estrita de schemas).

3. Estrutura de Diretórios Proposta
Plaintext
distillAI/
├── .gitignore
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py                 # Ponto de entrada do FastAPI
│   ├── core/                   # Configurações globais, segurança, conexão com banco
│   │   ├── config.py
│   │   └── database.py
│   ├── services/               # Lógica de negócio e engenharia de IA
│   │   ├── distiller_service.py # IA Engenheira (Lê logs -> cospe JSON)
│   │   └── agent_service.py     # Orquestração do Agente Dinâmico via Agno
│   ├── schemas/                # Modelos Pydantic (Validação de entrada/saída)
│   │   ├── distiller.py
│   │   └── agent.py
│   └── routes/                 # Endpoints da API (FastAPI)
│       ├── distiller_routes.py
│       └── agent_routes.py
└── tests/                      # Testes automatizados