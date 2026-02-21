import streamlit as st
import pandas as pd
import requests
import random

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo 🌍", page_icon="🌍", layout="wide")

# 2. ESTADOS
for key, val in {
    'luz': False, 'zoo': [], 'codigo': "", 'search_query': "", 
    'cor_card': "Preto", 'cor_fundo': "Preto", 'chat_pos': "sidebar"
}.items():
    if key not in st.session_state: st.session_state[key] = val

is_mestre = st.session_state.codigo == "6626"
is_ai_unlocked = st.session_state.codigo == "33236"
LIMITE = 80 if is_mestre else 20

# 3. CSS (Efeitos Dinâmicos)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f", "Amarelo": "#f1c40f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23") if not st.session_state.luz else "#ffffff"
bg_app = cores_hex.get(st.session_state.cor_fundo, "#0b1117") if not st.session_state.luz else "#f0f2f6"
txt_color = "#000" if (st.session_state.luz or st.session_state.cor_card == "Branco") else "#fff"
border_color = "#ffd700" if is_mestre else "#2ea043"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_app}; color: {txt_color}; }}
    .cc-card {{ 
        background: {c_bg} !important; border-radius: 12px; padding: 15px; 
        border-left: 10px solid {border_color}; margin-bottom: 15px;
        color: {txt_color} !important;
        { "animation: gold-glow 3s infinite; border: 2px solid #ffd700;" if is_mestre else "" }
    }}
    .code-box {{ background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; border: 2px dashed gray; margin: 15px 0; }}
    @keyframes gold-glow {{ 0% {{ border-color: #ffd700; }} 50% {{ border-color: #ff8c00; box-shadow: 0 0 15px #ffd700; }} 100% {{ border-color: #ffd700; }} }}
    </style>
    """, unsafe_allow_html=True)

# 4. MOTOR DE BUSCA
def buscar(q):
    if not q: return []
    url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=12"
    try:
        res = requests.get(url).json()
        return [{'nome': i.get('preferred_common_name', i['name']).title(), 'sci': i['name'], 'foto': i['default_photo']['medium_url'], 'score': i.get('observations_count', 1)} for i in res['results'] if i.get('default_photo')]
    except: return []

# 5. SIDEBAR E ASSISTENTE PESSOAL (PREMIUM 33236)
st.sidebar.markdown(f"# 🌍 MundoVivo")

if is_ai_unlocked:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 Assistente Pessoal")
    if st.sidebar.button("⬅️ Mandar chat para a esquerda"):
        st.session_state.chat_pos = "left"
    
    chat_container = st.sidebar.container() if st.session_state.chat_pos == "sidebar" else st.container()
    
    with chat_container:
        duvida = st.text_input("Pergunta à IA (procura por características):", key="ai_chat")
        if duvida:
            st.session_state.search_query = duvida
            if "rápido" in duvida.lower(): st.info("🤖 O animal mais rápido é o Falcão-peregrino.")
            elif "bico" in duvida.lower(): st.info("🤖 O Tucano tem o bico mais marcante.")
            else: st.info(f"🤖 A procurar animais parecidos com: '{duvida}'.")

st.sidebar.markdown("---")
aba = st.sidebar.radio("Navegação", ["🌍 Mundo", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"])

# 6. INTERFACE PRINCIPAL (TUDO DISPONÍVEL)

if aba == "🌍 Mundo": 
    st.map(pd.DataFrame({'lat': [20.0], 'lon': [0.0]}))
    q = st.text_input("Procurar espécie:", value=st.session_state.search_query)
    res = buscar(q if q else "Animal")
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]:
            st.markdown(f"<div class='cc-card'><img src='{an['foto']}' style='width:100%; height:180px; object-fit:cover; border-radius:10px;'><h3>{an['nome']}</h3></div>", unsafe_allow_html=True)
            if st.button(f"Guardar {an['nome']}", key=f"sv_{i}"):
                if len(st.session_state.zoo) < LIMITE: st.session_state.zoo.append(an)
                else: st.error("Reserva cheia! Precisas do Código Mestre para 80 slots.")

elif aba == "🌲 Florestas":
    st.map(pd.DataFrame({'lat': [-3.4, 63.7], 'lon': [-62.2, 95.8]}))
    res = buscar("Forest")
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: st.markdown(f"<div class='cc-card'><img src='{an['foto']}' style='width:100%; border-radius:10px;'><h4>{an['nome']}</h4></div>", unsafe_allow_html=True)

elif aba == "🌊 Oceanos":
    st.map(pd.DataFrame({'lat': [-8.7, 14.5], 'lon': [-145.0, -30.0]}))
    res = buscar("Ocean")
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: st.markdown(f"<div class='cc-card'><img src='{an['foto']}' style='width:100%; border-radius:10px;'><h4>{an['nome']}</h4></div>", unsafe_allow_html=True)

elif aba == "🔬 Laboratório":
    st.title("🔬 Laboratório")
    c1, c2 = st.columns(2)
    p1 = c1.text_input("Animal 1:", "Leão")
    p2 = c2.text_input("Animal 2:", "Tigre")
    if st.button("🔥 LUTAR"):
        r1, r2 = buscar(p1), buscar(p2)
        if r1 and r2:
            venc = r1[0]['nome'] if r1[0]['score'] > r2[0]['score'] else r2[0]['nome']
            st.success(f"🏆 Vencedor: {venc}!")

elif aba == "⭐ Coleção":
    st.title("⭐ Minha Coleção")
    if is_mestre: st.markdown("<div style='color:#ffd700; font-weight:bold; border:1px solid; padding:5px; text-align:center;'>🏆 CERTIFICADO DE MESTRE ZOÓLOGO ATIVO</div>", unsafe_allow_html=True)
    st.write(f"Capacidade: {len(st.session_state.zoo)} / {LIMITE}")
    cols = st.columns(3)
    for i, an in enumerate(st.session_state.zoo):
        with cols[i%3]:
            st.markdown(f"<div class='cc-card'><img src='{an['foto']}' style='width:100%; border-radius:10px;'><h4>{an['nome']}</h4></div>", unsafe_allow_html=True)
            if st.button("Remover", key=f"rm_{i}"): st.session_state.zoo.pop(i); st.rerun()

elif aba == "⚙️ Definições":
    st.title("⚙️ Definições")
    st.markdown("<div class='code-box'>", unsafe_allow_html=True)
    st.session_state.codigo = st.text_input("inserir codigo premium 6626 ou 33236", type="password", value=st.session_state.codigo)
    if (is_mestre or is_ai_unlocked) and st.button("❌ APAGAR PREMIUM"):
        st.session_state.codigo = ""
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.session_state.luz = st.toggle("Modo Dia", value=st.session_state.luz)
    st.session_state.cor_card = st.selectbox("Cor do Cartão", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_card))
    st.session_state.cor_fundo = st.selectbox("Cor do Fundo", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_fundo))
