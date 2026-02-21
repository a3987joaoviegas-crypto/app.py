import streamlit as st
import pandas as pd
import requests
import random

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo 🌍", page_icon="🌍", layout="wide")

# 2. ESTADOS
for key, val in {
    'luz': False, 'zoo': [], 'codigo': "", 'codigo_perm': "", 
    'search_query': "", 'cor_card': "Preto", 'cor_fundo': "Preto", 
    'chat_pos': "sidebar"
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Lógica de Permissões
is_perm_active = st.session_state.codigo_perm == "67lucas62"
is_mestre = st.session_state.codigo == "6626"
is_ai_unlocked = st.session_state.codigo == "33236" or is_perm_active
LIMITE = 80 if (is_mestre or is_perm_active) else 20

# 3. CSS (ESTILO CARTÃO ORIGINAL)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f", "Amarelo": "#f1c40f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23") if not st.session_state.luz else "#ffffff"
bg_app = cores_hex.get(st.session_state.cor_fundo, "#0b1117") if not st.session_state.luz else "#f0f2f6"
txt_color = "#000" if (st.session_state.luz or st.session_state.cor_card == "Branco") else "#fff"

if is_perm_active:
    border_style = """
        border-left: 15px solid; border-right: 15px solid;
        border-image: linear-gradient(45deg, #ff00ff, #00ffff, #ff00ff, #00ffff) 1;
        animation: galactic 3s linear infinite;
    """
else:
    b_color = "#ffd700" if is_mestre else "#2ea043"
    border_style = f"border-left: 15px solid {b_color}; border-right: 5px solid {b_color};"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_app}; color: {txt_color}; }}
    .cc-card {{ 
        background: {c_bg} !important; border-radius: 15px; padding: 20px; 
        {border_style}
        box-shadow: 10px 10px 25px rgba(0,0,0,0.5); margin-bottom: 20px;
        color: {txt_color} !important;
    }}
    .nome-pt {{ font-size: 1.6em; font-weight: bold; margin: 0; color: {txt_color}; }}
    .nome-sci {{ font-size: 1.0em; font-style: italic; opacity: 0.7; margin-bottom: 10px; color: {txt_color}; }}
    @keyframes galactic {{
        0% {{ filter: hue-rotate(0deg); }}
        100% {{ filter: hue-rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)

# 4. MOTOR DE BUSCA
def buscar(q):
    if not q: return []
    url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=12&locale=pt-PT"
    try:
        res = requests.get(url).json()
        return [{'nome': i.get('preferred_common_name', i['name']).title(), 'sci': i['name'], 'foto': i['default_photo']['medium_url'] if i.get('default_photo') else ""} for i in res['results']]
    except: return []

# 5. SIDEBAR
with st.sidebar:
    st.markdown("# 🌍 MundoVivo")
    st.markdown("---")
    
    if is_ai_unlocked:
        st.subheader("🤖 Assistente (33236)")
        if st.button("⬅️ Mover Chat"):
            st.session_state.chat_pos = "left" if st.session_state.chat_pos == "sidebar" else "sidebar"
        if st.session_state.chat_pos == "sidebar":
            st.text_input("Dúvida biológica:", key="ia_side")
    
    aba = st.radio("Navegação", ["🌍 Mundo", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"])

# 6. INTERFACE
if aba == "🌍 Mundo":
    st.title("🌍 Planisfério")
    st.map(pd.DataFrame({'lat': [39.5], 'lon': [-8.0]}))
    q = st.text_input("Procurar espécie:", value=st.session_state.search_query)
    res = buscar(q if q else "Animais")
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]:
            st.markdown(f"""
            <div class='cc-card'>
                <img src='{an['foto']}' width='100%' style='border-radius:10px; margin-bottom:10px;'>
                <div class='nome-pt'>{an['nome']}</div>
                <div class='nome-sci'>{an['sci']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Guardar {an['nome']}", key=f"w_{i}"):
                if len(st.session_state.zoo) < LIMITE: st.session_state.zoo.append(an)

elif aba == "🌲 Florestas":
    st.title("🌲 Florestas")
    st.map(pd.DataFrame({'lat': [40.0, -3.0], 'lon': [-8.0, -60.0]}))
    cols = st.columns(3)
    for i, an in enumerate(buscar("Animais da floresta")):
        with cols[i%3]:
            st.markdown(f"<div class='cc-card'><img src='{an['foto']}' width='100%'><div class='nome-pt'>{an['nome']}</div><div class='nome-sci'>{an['sci']}</div></div>", unsafe_allow_html=True)

elif aba == "🌊 Oceanos":
    st.title("🌊 Oceanos")
    st.map(pd.DataFrame({'lat': [20.0, -10.0], 'lon': [-40.0, -140.0]}))
    cols = st.columns(3)
    for i, an in enumerate(buscar("Animais marinhos")):
        with cols[i%3]:
            st.markdown(f"<div class='cc-card'><img src='{an['foto']}' width='100%'><div class='nome-pt'>{an['nome']}</div><div class='nome-sci'>{an['sci']}</div></div>", unsafe_allow_html=True)

elif aba == "🔬 Laboratório":
    st.title("🔬 Laboratório")
    t1, t2 = st.tabs(["🔎 Pesquisa", "🥊 Arena"])
    with t1:
        s = st.text_input("Pesquisar:")
        for an in buscar(s):
            st.markdown(f"<div class='cc-card'><div class='nome-pt'>{an['nome']}</div><div class='nome-sci'>{an['sci']}</div></div>", unsafe_allow_html=True)

elif aba == "⚙️ Definições":
    st.title("⚙️ Definições")
    st.markdown("<div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px;'>", unsafe_allow_html=True)
    st.session_state.codigo = st.text_input("Código IA (33236) ou Mestre (6626):", type="password")
    st.session_state.codigo_perm = st.text_input("Código Supremo (67lucas62):", type="password")
    
    if (is_perm_active) and st.button("❌ APAGAR SUPREMO PERMANENTE"):
        st.session_state.codigo_perm = ""
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("Inserir"):
        st.balloons()
        st.success("Configurações Aplicadas!")
    
    st.session_state.luz = st.toggle("Modo Dia")
    st.session_state.cor_card = st.selectbox("Cor do Cartão", list(cores_hex.keys()))
    st.session_state.cor_fundo = st.selectbox("Cor do Fundo", list(cores_hex.keys()))
