import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# CSS ESTILO GEMINI + GRELHA
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0b1117; color: #adbac7; }

    /* CHAT IDENTICO AO GEMINI */
    .stChatMessage { background-color: transparent !important; }
    .stChatMessage [data-testid="stChatMessageContent"] {
        background-color: #1c2128; border-radius: 20px; padding: 15px 25px; border: 1px solid #30363d;
    }
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] { display: none; }

    /* CARTÃO CHAT (PEQUENO) */
    .chat-card { background: #1c2128; border-radius: 12px; padding: 15px; border: 1px solid #30363d; margin-top: 10px; max-width: 320px; }
    .chat-img { width: 100%; height: 140px; object-fit: cover; border-radius: 8px; }
    
    /* CARTÃO LABORATÓRIO/MAPA (MÉDIO) */
    .lab-card { background: #1c2128; border-radius: 12px; padding: 15px; border-left: 5px solid #2ea043; margin-bottom: 20px; height: 380px; }
    .lab-img { width: 100%; height: 180px; object-fit: cover; border-radius: 8px; }
    .name-txt { color: #2ea043; font-weight: bold; font-size: 18px; margin-top: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA DE BUSCA MELHORADA
def buscar_fauna(query, limite=1, taxon=1):
    q = query.lower()
    if "pesado" in q: busca = "Baleia-azul"
    elif "rápido" in q: busca = "Guepardo"
    else: busca = query
    
    url = f"https://api.inaturalist.org/v1/taxa?q={busca}&taxon_id={taxon}&locale=pt-BR"
    try:
        res = requests.get(url).json()
        out = []
        for t in res['results'][:limite]:
            if t.get('default_photo'):
                out.append({
                    'nome': (t.get('preferred_common_name') or t.get('name')).title(),
                    'sci': t.get('name'),
                    'foto': t['default_photo']['medium_url'],
                    'classe': t.get('iconic_taxon_name', 'Animal')
                })
        return out
    except: return []

# SESSÕES PARA NÃO PERDER DADOS
if 'zoo' not in st.session_state: st.session_state.zoo = []
if 'chat_hist' not in st.session_state: st.session_state.chat_hist = []
if 'diario_content' not in st.session_state: st.session_state.diario_content = ""

# MENU
menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "💬 Chat IA", "📝 Diário", "⭐ Favoritos"])

def mostrar_animal(a, key, mini=True):
    card_cl = "chat-card" if mini else "lab-card"
    img_cl = "chat-img" if mini else "lab-img"
    st.markdown(f"""<div class='{card_cl}'><img src='{a['foto']}' class='{img_cl}'><div class='name-txt'>{a['nome']}</div>
    <div style='color:#8b949e; font-size:12px; font-style:italic; text-align:center;'>{a['sci']}</div>
    <div style='text-align:center; margin-top:5px;'>🏷️ {a['classe']}</div></div>""", unsafe_allow_html=True)
    if st.button("⭐ Guardar", key=key): 
        st.session_state.zoo.append(a)
        st.toast(f"{a['nome']} guardado!")

# --- PÁGINAS ---
if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério")
    st.map(pd.DataFrame({'lat': [-14.23, 39.39, -11.2, 37.09], 'lon': [-51.92, -8.22, 17.87, -95.71]}))
    sel = st.selectbox("Ver país:", ["Brasil", "Portugal", "Angola", "EUA"])
    res = buscar_fauna(sel, 3)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i]: mostrar_animal(an, f"map_{i}", False)

elif menu == "🌲 Florestas":
    st.title("🌲 Bioma: Florestas")
    res = buscar_fauna("Amazonia", 6)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: mostrar_animal(an, f"flo_{i}", False)

elif menu == "🌊 Oceanos":
    st.title("🌊 Bioma: Oceanos")
    res = buscar_fauna("Tubarao", 6)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: mostrar_animal(an, f"oce_{i}", False)

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório")
    txt = st.text_input("Pesquisar espécies (Grelha):")
    if txt:
        lista = buscar_fauna(txt, 12)
        cols = st.columns(3)
        for i, anim in enumerate(lista):
            with cols[i%3]: mostrar_animal(anim, f"lab_{i}", False)

elif menu == "💬 Chat IA":
    st.title("💬 Chat MundoVivo")
    for i, msg in enumerate(st.session_state.chat_hist):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "animal" in msg: mostrar_animal(msg["animal"], f"chat_{i}", True)

    if p := st.chat_input("Diz o nome de um animal..."):
        st.session_state.chat_hist.append({"role": "user", "content": p})
        with st.chat_message("user"): st.write(p)
        with st.chat_message("assistant"):
            dados = buscar_animal_dados = buscar_fauna(p, 1)
            if dados:
                resp = f"Aqui tens a informação sobre o **{dados[0]['nome']}**:"
                st.write(resp)
                mostrar_animal(dados[0], "chat_new", True)
                st.session_state.chat_hist.append({"role": "assistant", "content": resp, "animal": dados[0]})
            else:
                resp = "Não encontrei esse animal na base de dados."
                st.write(resp)
                st.session_state.chat_hist.append({"role": "assistant", "content": resp})

elif menu == "📝 Diário":
    st.title("📝 Diário de Bordo")
    st.session_state.diario_content = st.text_area("Escreve as tuas descobertas:", value=st.session_state.diario_content, height=400)

elif menu == "⭐ Favoritos":
    st.title("🐾 O Meu Zoo")
    cols = st.columns(3)
    for i, z in enumerate(st.session_state.zoo):
        with cols[i%3]: mostrar_animal(z, f"zoo_{i}", False)
