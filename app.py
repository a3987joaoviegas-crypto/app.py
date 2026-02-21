import streamlit as st
import pandas as pd
import requests
import random
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo 🌍", page_icon="🌍", layout="wide")

# 2. ESTADOS
for key, val in {
    'luz': False, 'zoo': [], 'codigo': "", 'codigo_perm': "", 'search_query': "", 
    'cor_card': "Preto", 'cor_fundo': "Preto", 'chat_pos': "sidebar", 'data_login': datetime.now().day
}.items():
    if key not in st.session_state: st.session_state[key] = val

# Lógica de Expiração (67lucas62 é permanente)
is_perm_active = st.session_state.codigo_perm == "67lucas62"
if st.session_state.data_login != datetime.now().day and not is_perm_active:
    st.session_state.codigo = ""
    st.session_state.data_login = datetime.now().day

is_mestre = st.session_state.codigo == "6626" or is_perm_active
is_ai_unlocked = st.session_state.codigo == "33236" or is_perm_active
LIMITE = 80 if is_mestre else 20

# 3. CSS (Estilo Cartão de Cidadão)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f", "Amarelo": "#f1c40f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23") if not st.session_state.luz else "#ffffff"
bg_app = cores_hex.get(st.session_state.cor_fundo, "#0b1117") if not st.session_state.luz else "#f0f2f6"
txt_color = "#000" if (st.session_state.luz or st.session_state.cor_card == "Branco") else "#fff"
border_color = "#b9f2ff" if is_perm_active else ("#ffd700" if is_mestre else "#2ea043")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_app}; color: {txt_color}; }}
    .cc-card {{ 
        background: {c_bg} !important; border-radius: 15px; padding: 20px; 
        border-left: 15px solid {border_color}; border-right: 5px solid {border_color};
        box-shadow: 10px 10px 25px rgba(0,0,0,0.6); margin-bottom: 20px;
        color: {txt_color} !important;
        { "animation: gold-glow 3s infinite;" if is_mestre else "" }
    }}
    .code-box {{ background: rgba(255,255,255,0.05); padding: 25px; border-radius: 15px; border: 2px dashed {border_color}; margin: 15px 0; }}
    @keyframes gold-glow {{ 0% {{ box-shadow: 0 0 5px #ffd700; }} 50% {{ box-shadow: 0 0 20px {border_color}; }} 100% {{ box-shadow: 0 0 5px #ffd700; }} }}
    </style>
    """, unsafe_allow_html=True)

# 4. MOTOR DE BUSCA
def buscar(q):
    if not q: return []
    url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=12"
    try:
        res = requests.get(url).json()
        return [{'nome': i.get('preferred_common_name', i['name']).title(), 'sci': i['name'], 'foto': i['default_photo']['medium_url'] if i.get('default_photo') else "", 'score': i.get('observations_count', 1)} for i in res['results']]
    except: return []

# 5. SIDEBAR E CHAT
st.sidebar.markdown(f"# 🌍 MundoVivo")
if is_ai_unlocked:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 Assistente Pessoal")
    if st.sidebar.button("⬅️ Mandar chat para a esquerda"): st.session_state.chat_pos = "left"
    
    chat_area = st.sidebar if st.session_state.chat_pos == "sidebar" else st
    with chat_area:
        duvida = st.text_input("Dúvida biológica:", key="chat_ia")
        if duvida:
            st.session_state.search_query = duvida
            st.info(f"🤖 A pesquisar cartão para: {duvida}")

st.sidebar.markdown("---")
aba = st.sidebar.radio("Navegação", ["🌍 Mundo", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"])

# 6. INTERFACE PRINCIPAL
if aba == "🔬 Laboratório":
    st.title("🔬 Centro de Pesquisa e Arena")

