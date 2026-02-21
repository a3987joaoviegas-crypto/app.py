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
is_mestre = st.session_state.codigo == "6626" or is_perm_active
is_ai_unlocked = st.session_state.codigo == "33236" or is_perm_active
LIMITE = 80 if is_mestre else 20

# 3. CSS (Cartão de Cidadão para Todos)
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
        box-shadow: 8px 8px 20px rgba(0,0,0,0.5); margin-bottom: 20px;
        color: {txt_color} !important;
        { "animation: gold-glow 3s infinite;" if is_mestre else "" }
    }}
    .code-box {{ background: rgba(255,255,255,0.05); padding: 25px; border-radius: 15px; border: 2px dashed gray; }}
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

# 5. SIDEBAR
st.sidebar.markdown(f"# 🌍 MundoVivo")
if is_ai_unlocked:
    st.sidebar.subheader("🤖 Assistente Pessoal")
    if st.sidebar.button("⬅️ Mandar chat para a esquerda"): st.session_state.chat_pos = "left"
    chat_area = st.sidebar if st.session_state.chat_pos == "sidebar" else st
    with chat_area:
        duvida = st.text_input("Dúvida biológica:", key="chat_ia")
        if duvida: st.info(f"🤖 Assistente: Analisando características de '{duvida}'...")

st.sidebar.markdown("---")
aba = st.sidebar.radio("Navegação", ["🌍 Mundo", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"])

# 6. INTERFACE

if aba == "🌍 Mundo":
    st.title("🌍 Planisfério")
    st.map(pd.DataFrame({'lat': [20.0], 'lon': [0.0]}))
    q = st.text_input("Procurar espécie:", value=st.session_state.search_query)
    res = buscar(q if q else "Animal")
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]:
            st.markdown(f"<div class='cc-card'><img src='{an['foto']}' width='100%' style='border-radius:10px;'><h3>{an['nome']}</h3></div>", unsafe_allow_html=True)
            if st.button(f"Guardar {an['nome']}", key=f"w_{i}"):
                if len(st.session_state.zoo) < LIMITE: st.session_state.zoo.append(an)

elif aba == "🌲 Florestas":
    st.title("🌲 Regiões Florestais")
    st.map(pd.DataFrame({'lat': [-3.0, 60.0, 45.0], 'lon': [-60.0, 100.0, -5.0]}))
    st.markdown("---")
    res = buscar("Forest mammals")
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: st.markdown(f"<div class='cc-card'><h4>{an['nome']}</h4><img src='{an['foto']}' width='100%'></div>", unsafe_allow_html=True)

elif aba == "🌊 Oceanos":
    st.title("🌊 Explorador de Oceanos")
    st.map(pd.DataFrame({'lat': [0.0, -20.0, 30.0], 'lon': [-150.0, -20.0, -40.0]}))
    st.markdown("---")
    res = buscar("Ocean animals")
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: st.markdown(f"<div class='cc-card'><h4>{an['nome']}</h4><img src='{an['foto']}' width='100%'></div>", unsafe_allow_html=True)

elif aba == "🔬 Laboratório":
    st.title("🔬 Laboratório")
    t1, t2, t3 = st.tabs(["🔎 Centro de Pesquisa", "🥊 Arena de Luta", "🎲 Aleatório"])
    with t1:
        s = st.text_input("Pesquisa Científica:")
        for an in buscar(s):
            st.markdown(f"<div class='cc-card'><h3>{an['nome']}</h3><p>{an['sci']}</p></div>", unsafe_allow_html=True)
            if st.button(f"Guardar {an['nome']}", key=f"ls_{an['nome']}"): st.session_state.zoo.append(an)
    with t2:
        c1, c2 = st.columns(2)
        with c1:
            r1 = buscar(st.text_input("Lutador 1:"))
            if r1: 
                st.markdown(f"<div class='cc-card'><img src='{r1[0]['foto']}' width='100%'><h4>{r1[0]['nome']}</h4></div>", unsafe_allow_html=True)
                st.button("Escolher Lutador 1", key="l1_btn")
        with c2:
            r2 = buscar(st.text_input("Lutador 2:"))
            if r2: 
                st.markdown(f"<div class='cc-card'><img src='{r2[0]['foto']}' width='100%'><h4>{r2[0]['nome']}</h4></div>", unsafe_allow_html=True)
                st.button("Escolher Lutador 2", key="l2_btn")

elif aba == "⭐ Coleção":
    st.title("⭐ Minha Coleção")
    st.write(f"Capacidade: {len(st.session_state.zoo)} / {LIMITE}")
    for i, an in enumerate(st.session_state.zoo):
        st.markdown(f"<div class='cc-card'><h4>{an['nome']}</h4></div>", unsafe_allow_html=True)
        if st.button("Remover", key=f"r_{i}"): st.session_state.zoo.pop(i); st.rerun()

elif aba == "⚙️ Definições":
    st.title("⚙️ Definições")
    st.markdown("<div class='code-box'>", unsafe_allow_html=True)
    st.session_state.codigo = st.text_input("Inserir código premium:", type="password", value=st.session_state.codigo)
    if st.session_state.codigo != "" and st.button("❌ APAGAR PREMIUM"):
        st.session_state.codigo = ""; st.rerun()
    st.markdown("---")
    st.session_state.codigo_perm = st.text_input("Novo Código Permanente:", type="password", value=st.session_state.codigo_perm)
    if is_perm_active and st.button("❌ APAGAR PREMIUM PERMANENTE"):
        st.session_state.codigo_perm = ""; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # O BOTÃO AGORA DIZ "INSERIR"
    if st.button("Inserir"):
        st.balloons()
        st.success("Configurações Aplicadas!")
    
    st.session_state.luz = st.toggle("Modo Dia", value=st.session_state.luz)
    st.session_state.cor_card = st.selectbox("Cor do Cartão", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_card))
    st.session_state.cor_fundo = st.selectbox("Cor do Fundo", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_fundo))
