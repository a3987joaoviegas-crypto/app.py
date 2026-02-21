import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. ESTADO (Memória do Zoo e Trava)
chaves = {'zoo':[], 'crio':[], 'c_24h':"", 'c_mega':"", 'ini':None, 'exp':None}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# 2. REGRAS DE ACESSO (Trava de 1 semana no 6626)
is_mega = st.session_state.c_mega == "67lucas62"
pode_6626 = True
if st.session_state.exp:
    if datetime.now() - st.session_state.exp < timedelta(weeks=1): pode_6626 = False

is_24h = (st.session_state.c_24h == "6626" and pode_6626)
if is_24h and not st.session_state.ini: st.session_state.ini = datetime.now()

# Verificação de Expiração
if st.session_state.ini and datetime.now() - st.session_state.ini > timedelta(hours=24):
    st.session_state.exp = datetime.now(); st.session_state.ini = None; st.session_state.c_24h = ""; st.rerun()

vip = is_mega or is_24h

# 3. FUNÇÃO DE BUSCA E CARD
def buscar(q):
    try:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=6&locale=pt-PT")
        return r.json().get('results', [])
    except: return []

def card(an, resgate=False):
    nome = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    cientifico = an.get('name', 'N/A')
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/150")
    
    st.markdown(f"""
    <div style="background:#1a1c23; padding:15px; border-radius:15px; border:2px solid {'#ffd700' if vip else '#2ecc71'}; margin-bottom:10px;">
        <img src="{foto}" style="width:100%; border-radius:10px;">
        <h3 style="margin:10px 0 0 0; font-size:1.1em;">{nome}</h3>
        <i style="color:#1DB954; font-size:0.9em;">{cientifico}</i>
    </div>
    """, unsafe_allow_html=True)
    
    if resgate:
        if st.button(f"🌀 Resgatar", key=f"res_{an['id']}"):
            st.session_state.zoo.append(an); st.session_state.crio.remove(an); st.rerun()
    else:
        if st.button(f"📥 Capturar", key=f"cap_{an['id']}", use_container_width=True):
            st.session_state.zoo.append(an); st.toast(f"{nome} capturado!")

# 4. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    op = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "⚙️ Definições"]
    if vip: op = ["🔬 Zoo", "🌀 Resgate", "❄️ Criogenia"] + op
    aba = st.radio("Navegação", op)

# 5. CONTEÚDO DAS ABAS
if aba == "🌲 Florestas":
    st.header("🌲 Florestas do Mundo")
    
    tipo = st.selectbox("Escolha o Bioma:", ["Amazónia", "Floresta do Congo", "Taiga Siberiana", "Mata Atlântica", "Selva Tropical"])
    animais = buscar(tipo)
    cols = st.columns(2)
    for i, an in enumerate(animais):
        with cols[i%2]: card(an)

elif aba == "🌊 Oceanos":
    st.header("🌊 Oceanos e Mares")
    
    tipo = st.selectbox("Escolha o Oceano:", ["Oceano Pacífico", "Oceano Atlântico", "Oceano Índico", "Mar Vermelho", "Abismo"])
    animais = buscar(tipo)
    cols = st.columns(2)
    for i, an in enumerate(animais):
        with cols[i%2]: card(an)

elif aba == "🔬 Zoo":
    st.header("🐾 O Teu Zoo")
    if not st.session_state.zoo: st.info("Zoo vazio.")
    cols = st.columns(2)
    for i, an in enumerate(st.session_state.zoo):
        with cols[i%2]: card(an)

elif aba == "🌀 Resgate":
    st.header("🌀 Centro de Resgate")
    if not st.session_state.crio: st.info("Nada para resgatar.")
    cols = st.columns(2)
    for i, an in enumerate(st.session_state.crio):
        with cols[i%2]: card(an, resgate=True)

elif aba == "❄️ Criogenia":
    st.header("❄️ Congelar Animal")
    if st.session_state.zoo:
        alvo = st.selectbox("Animal:", st.session_state.zoo, format_func=lambda x: x.get('preferred_common_name', x.get('name')))
        if st.button("❄️ Enviar para o Resgate"):
            st.session_state.crio.append(alvo); st.session_state.zoo.remove(alvo); st.rerun()
    else: st.warning("Não há animais no Zoo para congelar.")

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições de Acesso")
    if not pode_6626: st.error("Trava de 1 semana ativa para o código 6626.")
    st.session_state.c_mega = st.text_input("Código Mega", value=st.session_state.c_mega, type="password")
    st.session_state.c_24h = st.text_input("Código 24h", value=st.session_state.c_24h, type="password")
    if st.button("Guardar Alterações"): st.rerun()
