import streamlit as st
import requests
import json

# Emojis para os participantes
EMOJI_USER = "🤓"
EMOJI_BOT = "🤖"


# Função de streaming da resposta
def perguntar_ollama_stream(prompt, modelo):
    """Envia uma pergunta para o modelo Qwen3 via API Ollama e retorna a resposta em tempo real.
    Args:
        prompt (str): A pergunta a ser enviada ao modelo.
        modelo (str): O nome do modelo a ser utilizado.
    Returns:
        str: A resposta completa do modelo.
    """

    # URL da API do Ollama
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": True,
        "num_predict": 200,
        "stop": ["Usuário:", "User:", "\n\n", "</s>"],
    }

    # Envia a requisição POST para a API
    resposta = requests.post(url, json=payload, stream=True)
    resposta.raise_for_status()

    # Processa a resposta em tempo real
    resposta_completa = ""
    for linha in resposta.iter_lines():
        if linha:
            parte = json.loads(linha.decode("utf-8"))
            if parte.get("done"):
                break
            if "response" in parte:
                novo_texto = parte["response"]
                yield novo_texto
                resposta_completa += novo_texto
    return resposta_completa


# Configurações da página
st.set_page_config(page_title="🤖 Chatbot Qwen3", layout="wide")

# --- Configurações da barra lateral ---
with st.sidebar:
    st.markdown("## 🤖 MathBot App")
    st.markdown("Este é um chatbot LLM baseado em:")
    st.markdown("- Streamlit\n- Ollama\n- Modelos Qwen3 customizados")

    modelo_escolhido = st.selectbox(
        "📦 Escolha o modelo:", ["qwen3-think", "qwen3-math4"]
    )
    st.markdown("---")

# Inicializar histórico de mensagens
if "historico" not in st.session_state:
    st.session_state.historico = []

# --- INTERFACE PRINCIPAL ---

st.markdown(
    "<style>"
    ".user-msg {text-align: right; background-color: #e6f2ff; padding: 10px; border-radius: 10px; margin: 8px;}"
    ".bot-msg {text-align: left; background-color: #f9f9f9; padding: 10px; border-radius: 10px; margin: 8px;}"
    "</style>",
    unsafe_allow_html=True,
)

# Exibir mensagens anteriores
for msg in st.session_state.historico:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='user-msg'>{EMOJI_USER} {msg['content']}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div class='bot-msg'>{EMOJI_BOT} {msg['content']}</div>",
            unsafe_allow_html=True,
        )

# Entrada do usuário
prompt = st.chat_input("Digite sua pergunta...")

if prompt:
    # Armazenar e mostrar a pergunta do usuário
    st.session_state.historico.append({"role": "user", "content": prompt})
    st.markdown(
        f"<div class='user-msg'>{EMOJI_USER} {prompt}</div>", unsafe_allow_html=True
    )

    resposta = ""
    with st.empty():
        caixa_resposta = ""
        for parte in perguntar_ollama_stream(prompt, modelo_escolhido):
            resposta += parte
            caixa_resposta = f"<div class='bot-msg'>{EMOJI_BOT} {resposta}</div>"
            st.markdown(caixa_resposta, unsafe_allow_html=True)

    # Armazenar a resposta do bot no histórico
    st.session_state.historico.append({"role": "assistant", "content": resposta})
