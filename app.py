import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO ESTILO GEMINI (Limpo e Moderno)
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

st.markdown("""
    <style>
    /* RESET E CORES GERAIS */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stDeployButton {display:none;}
    .stApp { background-color: #0b1117; color: #adbac7; }

    /* MENSAGENS ESTILO GEMINI (Sem ícones de robô) */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding-top: 0px !important;
    }
    [data-testid="stChatMessageContent"] {
        background-color: #1c2128;
        border-radius: 18px;
        padding: 15px 20px;
        border: 1px solid #30363d;
        color: #adbac7;
    }
    /* Estilo para a mensagem do utilizador ficar mais distinta se quiseres */
    
    /* CARTÃO COMPACTO (Aparece abaixo do texto) */
    .cc-mini-card { 
        background: #1c2128; border-radius: 12px; padding: 15px; 
        border: 1px solid #30363d; border-left: 5px solid #2ea043;
        margin-top: 10px; max-width: 450px; /* Largura controlada para não ser gigante */
    }
    .img-mini { width: 100%; height: 180px; object-fit: cover; border-radius: 8px; }
    .name-mini { color: #2ea043; font-size: 18px; font-weight: bold; margin-top: 8px; }
    .sci-mini { color: #8b949e; font-style: italic; font-size: 12px; margin-bottom: 10px; }
    .grid-expert { display: flex; gap: 15px; font-size: 13px; color: white; }
    .label-mini { color: #2ea043; font-weight: bold; font-size: 10px; text-transform: uppercase; }

    /* GRELHA DO LABORATÓRIO (Original) */
    .lab-card { 
        background: #1c2128; border-radius: 10px; padding: 15px; 
        margin-bottom: 20px; border: 1px solid #30363d;
    }
    .img-lab { width: 100%; height: 150px; object-fit: cover; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA DE BUSCA
def buscar_fauna(query, limite=1):
    q = query.lower()
    # Respostas diretas para perguntas comuns
    if "pesado" in q: busca = "Baleia-azul"
    elif "rápido" in q or "veloz" in q: busca = "Guepardo"
    else: busca = query

    url = f"https://api.inaturalist.org/v1/taxa?q={busca}&taxon_id=1&locale=pt-BR"
    try:
        res = requests.get(url).json()
        if res['results']:
            results = []
            for t in res['results'][:limite]:
                if t.get('default_photo'):
                    nome = (t.get('preferred_common_name') or t.get('name')).title()
                    results.append({
                        'nome': nome, 'sci': t.get('name'), 
                        'foto': t['default_photo']['medium_url'],
                        'dieta': "Herbívoro" if any(x in nome.lower() for x in ['elefante', 'zebra', 'girafa']) else "Carnívoro",
                        'repro': "Vivíparo" if t.get('iconic_taxon_name') == "Mammalia" else "Ovíparo",
                        'ambiente': "Aquático" if "baleia" in nome.lower() else "Terrestre"
                    })
            return results
    except: return []
    return []

# ESTADOS
if 'zoo' not in st.session_state: st.session_state.zoo = []
if 'chat_hist' not in st.session_state: st.session_state.chat_hist = []

# SIDEBAR
menu = st.sidebar.radio("Explorar:", ["🌍 Planisfério", "🔬 Laboratório", "💬 Chat IA", "📝 Diário", "⭐ Favoritos"])

def render_cartao_compacto(dados, key, mini=True):
    if not dados: return
    classe_card = "cc-mini-card" if mini else "lab-card"
    classe_img = "img-mini" if mini else "img-lab"
    
    st.markdown(f"""
        <div class='{classe_card}'>
            <img src='{dados['foto']}' class='{classe_img}'>
            <div class='name-mini'>{dados['nome']}</div>
            <div class='sci-mini'>{dados['sci']}</div>
            <div class='grid-expert'>
                <div><div class='label-mini'>DIETA</div>{dados['dieta']}</div>
                <div><div class='label-mini'>REPRO</div>{dados['repro']}</div>
                <div><div class='label-mini'>CASA</div>{dados['ambiente']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("⭐ Guardar", key=key):
        st.session_state.zoo.append(dados)

# --- PÁGINAS ---

if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério")
    st.map(pd.DataFrame({'lat': [-14.23, 39.39], 'lon': [-51.92, -8.22]}))

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório")
    busca = st.text_input("Pesquisa por espécies ou grupos:")
    if busca:
        animais = buscar_fauna(busca, 12)
        cols = st.columns(3)
        for i, a in enumerate(animais):
            with cols[i%3]: render_cartao_compacto(a, f"lab_{i}", mini=False)

elif menu == "💬 Chat IA":
    st.title("💬 Chat MundoVivo")
    
    # Exibir histórico estilo Gemini
    for i, msg in enumerate(st.session_state.chat_hist):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "data" in msg:
                render_cartao_compacto(msg["data"], f"chat_save_{i}")

    if prompt := st.chat_input("Ex: Qual o animal mais pesado?"):
        # Utilizador
        st.session_state.chat_hist.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        # Resposta IA (Sempre em baixo da imagem)
        with st.chat_message("assistant"):
            dados = buscar_fauna(prompt, 1)
            if dados:
                resp = f"O animal que procuras é o **{dados[0]['nome']}**. Aqui estão os dados dele:"
                st.write(resp)
                render_cartao_compacto(dados[0], "chat_new")
                st.session_state.chat_hist.append({"role": "assistant", "content": resp, "data": dados[0]})
            else:
                resp = "Ainda não tenho dados sobre essa espécie específica."
                st.write(resp)
                st.session_state.chat_hist.append({"role": "assistant", "content": resp})

elif menu == "📝 Diário":
    st.title("📝 Diário")
    st.text_area("Notas:", height=300)

elif menu == "⭐ Favoritos":
    st.title("🐾 Meu Zoo")
    if st.session_state.zoo:
        cols = st.columns(3)
        for i, z in enumerate(st.session_state.zoo):
            with cols[i%3]: render_cartao_compacto(z, f"zoo_{i}", mini=False)
