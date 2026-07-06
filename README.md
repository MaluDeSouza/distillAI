# 🧪 DistillAI

Plataforma inteligente para destilação de históricos de suporte e geração autônoma de agentes Nível 1 com lógica de transição humana (*handoff*).

![Demonstração do Fluxo](img/gif.gif)

---

## 🚀 O Problema que Resolvemos
Empresas gastam tempo excessivo com suporte repetitivo, enquanto criar FAQs estruturados manualmente é ineficiente. O **DistillAI** automatiza esse processo: ele lê históricos de chats brutos e desestruturados, extrai regras operacionais, mapeia restrições críticas do negócio e gera agentes de atendimento dinâmicos e resilientes.

## 🏗️ Funcionalidades em Desenvolvimento (Core Business)
* **Knowledge Distiller Engine:** Ingestão de arquivos de log que converte conversas informais em esquemas estritos de árvores de decisão usando Pydantic.
![Otimização de Prompt](img/escolha_persona_2.png)

* **Contextual Agent Factory:** Geração dinâmica de agentes de atendimento (via Agno Framework) que executam passos sequenciais antes do transbordo técnico.
![Guardrails do Agente](img/painel_do_agente_3_2.png)

* **Payload Handoff Mechanism:** Geração automática de resumos de contexto para operadores humanos, detalhando tudo o que a IA tentou antes de transferir o atendimento.

## 🔌 Documentação da API
O ecossistema é suportado por uma API robusta, documentada automaticamente para facilitar integrações futuras.
![Swagger da API](img/swagger.png)

## 🛠️ Stack Tecnológico
* Python 3.11+
* FastAPI
* Agno Framework
* Google Gemini API
* PostgreSQL (`pgvector`)

---

## 💻 Como Configurar o Ambiente Local

1. **Clone o repositório:**
```bash
git clone [https://github.com/SEU_USUARIO/distillAI.git](https://github.com/SEU_USUARIO/distillAI.git)
cd distillAI
```

2. **Inicie o servidor:**
```bash
uvicorn src.main:app --reload