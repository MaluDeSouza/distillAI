import streamlit as st
import requests
import time

# Configuração da página e variáveis globais
st.set_page_config(page_title="Knowledge Distiller", page_icon="🧠", layout="wide")
API_BASE_URL = "http://localhost:8000/v1"

# Controle de estado para navegação e dados da sessão
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "agent_id" not in st.session_state:
    st.session_state.agent_id = None
if "agent_info" not in st.session_state:
    st.session_state.agent_info = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- NAVEGAÇÃO LATERAL ---
with st.sidebar:
    st.title("🗺️ Navegação")
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "Home"
    if st.button("⚙️ Criar Agente", use_container_width=True):
        st.session_state.page = "Criar Agente"
    if st.button("💬 Testar Chat", use_container_width=True):
        st.session_state.page = "Chat"

# --- PÁGINA 1: HOME ---
if st.session_state.page == "Home":
    # 1. Hero Section Centralizada
    st.markdown("""
        <div style="text-align: center; padding-top: 2rem; padding-bottom: 2rem;">
            <h1 style="font-size: 3.5rem; margin-bottom: 0px;">🧠 Knowledge Distiller</h1>
            <h3 style="font-weight: 400; color: #a1a1aa;">Transforme o caos do suporte em agentes hiper-inteligentes.</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Botão centralizado usando colunas para controlar a largura
    col_vazia1, col_botao, col_vazia2 = st.columns([1, 1.5, 1])
    with col_botao:
        if st.button("🚀 Iniciar Destilação do Conhecimento", type="primary", use_container_width=True):
            st.session_state.page = "Criar Agente"
            st.rerun()

    st.divider()

    # 2. Grid de Funcionalidades (Cards visuais)
    st.markdown("<h4 style='text-align: center; margin-bottom: 2rem;'>O que a plataforma faz por você?</h4>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        #### 📂 1. Ingestão de Dados
        Faça upload de múltiplos históricos brutos de atendimento. O sistema processa e limpa os arquivos `.txt` automaticamente, sem você precisar estruturar os dados.
        """)
        
        st.warning("""
        #### ⚡ 3. RAG Automático em Segundos
        Todo o conhecimento é vetorizado (Embeddings) e armazenado no banco. O agente ganha uma memória exclusiva e à prova de alucinações.
        """)

    with col2:
        st.success("""
        #### ✨ 2. Otimização de Prompt por IA
        Não sabe como escrever o System Prompt perfeito? Nossa engine refina seu rascunho e cria regras de comportamento de alta performance na hora.
        """)
        
        st.error("""
        #### 💬 4. Teste em Tempo Real
        Valide a destilação no mesmo instante com um chat interativo. Veja exatamente quais trechos do RAG a IA usou para formular cada resposta.
        """)
# --- PÁGINA 2: CRIAR AGENTE ---
elif st.session_state.page == "Criar Agente":
    st.title("Upload e Criação de Agente")
    st.markdown("Arraste até 50 arquivos `.txt` com logs ou regras de negócio.")
    
    # Inicializa variáveis de estado se não existirem
    if "optimized_prompt" not in st.session_state:
        st.session_state.optimized_prompt = None
    if "prompt_choice" not in st.session_state:
        st.session_state.prompt_choice = "Original"

    nome = st.text_input("Nome do Agente", placeholder="Ex: Agente de suporte tecnico")
    comportamento = st.text_area("Rascunho de Comportamento", placeholder="Ex: Você é o agente de suporte...")
    
    # Botão para chamar a rota de otimização
    if st.button("✨ Melhorar Prompt com IA"):
        if comportamento.strip() == "":
            st.warning("Escreva um rascunho primeiro para a IA poder melhorar!")
        else:
            with st.spinner("Otimizando prompt..."):
                try:
                    res = requests.post(
                        f"{API_BASE_URL}/agents/optimize", 
                        json={"draft_behavior": comportamento}
                    )
                    if res.status_code == 200:
                        st.session_state.optimized_prompt = res.json().get("optimized_prompt")
                        st.session_state.prompt_choice = "Otimizado" # Muda o rádio pro otimizado
                    else:
                        st.error("Erro ao otimizar o prompt.")
                except Exception as e:
                    st.error(f"Erro de conexão: {e}")

    # Se a IA já gerou um prompt, mostra a comparação e deixa o usuário escolher
    prompt_final_para_envio = comportamento # Padrão
    
    if st.session_state.optimized_prompt:
        st.divider()
        st.subheader("Escolha a versão do Comportamento:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Seu Rascunho:**\n\n" + comportamento)
        with col2:
            st.success("**Prompt Otimizado (Recomendado):**\n\n" + st.session_state.optimized_prompt)
            
        st.session_state.prompt_choice = st.radio(
            "Qual versão você deseja usar para o agente?",
            ["Original", "Otimizado"],
            index=1 if st.session_state.prompt_choice == "Otimizado" else 0
        )
        
        # Define qual prompt vai para o backend
        if st.session_state.prompt_choice == "Otimizado":
            prompt_final_para_envio = st.session_state.optimized_prompt

    st.divider()
    uploaded_files = st.file_uploader("Arquivos de Conhecimento (.txt)", type=["txt"], accept_multiple_files=True)
    
    # Botão final de criação
    if st.button("Criar Agente", type="primary"):
        if not nome or not prompt_final_para_envio or not uploaded_files:
            st.error("Preencha o nome, o comportamento e anexe pelo menos um arquivo.")
        else:
            log_container = st.empty()
            progress_bar = st.progress(0)
            
            with log_container.container():
                st.write("⏳ Iniciando processamento...")
                
                files_payload = [("files", (file.name, file.getvalue(), "text/plain")) for file in uploaded_files]
                data_payload = {
                    "nome": nome,
                    "tipo": "Flash",
                    "comportamento": prompt_final_para_envio, # Manda a versão escolhida
                    "status_agente": "production"
                }

                st.write(f"✔ Lendo {len(uploaded_files)} arquivo(s)...")
                progress_bar.progress(30)
                
                try:
                    response = requests.post(f"{API_BASE_URL}/agents", data=data_payload, files=files_payload)
                    progress_bar.progress(80)
                    
                    if response.status_code == 201:
                        result = response.json()
                        st.write("✔ Agente criado e conhecimento vetorizado...")
                        progress_bar.progress(100)
                        st.success("Agente criado com sucesso!")
                        
                        st.session_state.agent_id = result.get("agent_id")
                        st.session_state.agent_info = {
                            "nome": nome,
                            "prompt_otimizado": prompt_final_para_envio,
                            "docs": len(uploaded_files),
                            "chunks": result.get("knowledge_processed", {}).get("chunks_saved", "N/A") if result.get("knowledge_processed") else "N/A",
                            "status": "Em Produção"
                        }
                        time.sleep(1.5)
                        # Limpa o state para a próxima criação
                        st.session_state.optimized_prompt = None
                        st.session_state.page = "Dashboard"
                        st.rerun()
                    else:
                        st.error(f"Erro no backend: {response.text}")
                except Exception as e:
                    st.error(f"Falha na conexão com a API: {str(e)}")

# --- PÁGINA 2.5: DASHBOARD DO AGENTE ---
elif st.session_state.page == "Dashboard":
    st.title("Painel do Agente")
    info = st.session_state.agent_info
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Status", info.get("status", "Desconhecido"))
    col2.metric("Documentos Ingeridos", info.get("docs", 0))
    col3.metric("Chunks Gerados", info.get("chunks", 0))
    
    st.subheader("Prompt Otimizado (System)")
    st.info(info.get("prompt_otimizado", "Nenhum prompt disponível."))
    
    if st.button("Ir para o Chat 💬"):
        st.session_state.page = "Chat"
        st.rerun()

# --- PÁGINA 3: CHAT INTERATIVO ---
elif st.session_state.page == "Chat":
    st.title("Chatbot (Runtime)")
    
    if not st.session_state.agent_id:
        st.warning("Nenhum agente criado nesta sessão. Vá em 'Criar Agente' primeiro.")
        st.stop()
        
    st.caption(f"Conversando com o Agente ID: {st.session_state.agent_id}")

    # Renderiza o histórico da tela
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
           
            

    # Input de nova mensagem
    user_input = st.chat_input("Digite sua dúvida (ex: 'Minha internet caiu')...")
    
    if user_input:
        # Exibe a mensagem do usuário imediatamente
        with st.chat_message("user"):
            st.markdown(user_input)
        
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Prepara a chamada para o runtime
        history_payload = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in st.session_state.chat_history[:-1]
        ]

        payload = {
            "agent_id": st.session_state.agent_id,
            "message": user_input,
            "history": history_payload 
        }
        
        with st.chat_message("assistant"):
            with st.spinner("Consultando base de conhecimento..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/chat/interact", json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        reply = data.get("reply", "Resposta vazia do modelo.")
                        st.markdown(reply)
                                                        
                        # Salva no histórico
                        st.session_state.chat_history.append({
                            "role": "assistant", 
                            "content": reply,
                        })
                    else:
                        st.error(f"Erro na API: {response.status_code}")
                except Exception as e:
                    st.error(f"Erro de comunicação: {str(e)}")