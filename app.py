import streamlit as st
import pandas as pd
import requests
import random

# 1. CONFIGURAÇÃO BÁSICA
st.set_page_config(page_title="MundoVivo 🌍", page_icon="🌍", layout="wide")

# 2. SISTEMA DE MEMÓRIA (Persistência)
if 'luz' not in st.session_state: st.session_state.luz = False
if 'zoo' not in st.session_state: st.session_state.zoo = []
if 'codigo' not in st.session_state: st.session_state.codigo = ""
if 'codigo_perm' not in st.session_state: st.session_state.codigo_perm = ""
if 'cor_card' not in st.session_state: st.session_state.cor_card = "Preto"
if 'cor_fundo' not in st.session_state: st.session_state.cor_fundo = "Preto"
if 'chat_pos' not in st.session_state: st.session_state.chat_pos = "sidebar"

# Lógica de Permissões
is_perm_active = st.session_state.codigo_perm == "67lucas62"
is_mestre = st.session_state.codigo == "6626" or is_perm_active
is_ai_unlocked = st.session_state.codigo == "33236" or is_perm_active
LIMITE = 80 if is_mestre else 20

# 3. DESIGN E CORES
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f", "Amarelo": "#f1c40f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23") if not st.session_state.luz else "#ffffff"
app_bg = cores_hex.get(st.session_state.cor_fundo, "#0b1117") if not st.session_state.luz else "#f0f2f6"
txt_color = "#000" if (st.session_state.luz or st.session_state.cor_card == "Branco") else "#fff"

if is_perm_active:
    border_css = "border-left: 15px solid; border-right: 5px solid; border-image: linear-gradient(45deg, #ff00ff, #00ffff) 1; animation: galactico 3s linear infinite;"
else:
    b_col = "#ffd700" if is_mestre else "#2ea043"
    border_css = f"border-left: 15px solid {b_col}; border-right: 5px solid {b_col};"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {app_bg}; color: {txt_color}; }}
    .cc-card {{ 
        background: {c_bg} !important; border-radius: 15px; padding: 20px; 
        {border_css}
        box-shadow: 8px 8px 20px rgba(0,0,0,0.5); margin-bottom: 20px;
        color: {txt_color} !important;
    }}
    .nome-pt {{ font-size: 1.5em; font-weight: bold; margin-bottom: 2px; }}
    .nome-sci {{ font-size: 0.9em; font-style: italic; opacity: 0.7; margin-bottom: 10px; border-bottom: 1px solid gray; }}
    .bio-info {{ font-size: 0.8em; margin-top: 5px; }}
    .status-cons {{ background: rgba(255,215,0,0.2); padding: 5px; border-radius: 5px; font-weight: bold; margin-top: 10px; text-align: center; border: 1px solid gold; }}
    @keyframes galactico {{ 0% {{ filter: hue-rotate(0deg); }} 100% {{ filter: hue-rotate(360deg); }} }}
    </style>
    """, unsafe_allow_html=True)

# 4. MOTOR DE DADOS
def buscar_api(termo):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={termo}&taxon_id=1&per_page=9&locale=pt-PT"
        r = requests.get(url).json()
        return [{'nome': i.get('preferred_common_name', i['name']).title(), 'sci': i['name'], 'foto': i['default_photo']['medium_url'] if i.get('default_photo') else "", 'id': i['id']} for i in r['results']]
    except: return []

def obter_bio(nome):
    if any(x in nome.lower() for x in ['tubarão', 'leão', 'lobo', 'tigre', 'águia', 'orca']):
        return "Carnívoro 🥩", "Predador 🏹", "Vivíparo 🍼"
    return "Herbívoro/Ominívoro 🌿", "Variável 🌍", "Ovíparo/Vivíparo 🥚"

def desenhar_cartao(an, k):
    alim, amb, repr = obter_bio(an['nome'])
    st.markdown(f"""
    <div class='cc-card'>
        <img src='{an['foto']}' width='100%' style='border-radius:10px; height:180px; object-fit:cover;'>
        <div class='nome-pt'>{an['nome']}</div>
        <div class='nome-sci'>{an['sci']}</div>
        <div class='bio-info'>
            <b>🍴 Alimentação:</b> {alim}<br>
            <b>🏠 Ambiente:</b> {amb}<br>
            <b>🐣 Reprodução:</b> {repr}
        </div>
        {f"<div class='status-cons'>⚠️ Estado: Protegido (Mestre)</div>" if is_mestre else ""}
    </div>
    """, unsafe_allow_html=True)
    if st.button(f"Guardar na Reserva", key=k):
        if len(st.session_state.zoo) < LIMITE:
            st.session_state.zoo.append(an)
            st.success(f"{an['nome']} guardado!")

# 5. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    if is_ai_unlocked:
        st.subheader("🤖 Assistente IA")
        if st.button("Trocar Lado do Chat"):
            st.session_state.chat_pos = "left" if st.session_state.chat_pos == "sidebar" else "sidebar"
        if st.session_state.chat_pos == "sidebar":
            st.text_input("Pergunta à IA:", key="ia_s")
    
    st.markdown("---")
    aba = st.radio("Explorar", ["🌍 Planisfério", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"])

# 6. ABAS
if aba == "🌍 Planisfério":
    st.title("🌍 Mapa Global")
    st.map(pd.DataFrame({'lat': [38.7], 'lon': [-9.1]}))
    txt = st.text_input("Pesquisar espécie:", "Lince Ibérico")
    for i, a in enumerate(buscar_api(txt)):
        desenhar_cartao(a, f"map_{i}")

elif aba == "🌲 Florestas":
    st.title("🌲 Biomas de Floresta")
    st.map(pd.DataFrame({'lat': [-3.0, 45.0], 'lon': [-60.0, -5.0]}))
    cols = st.columns(3)
    for i, a in enumerate(buscar_api("Mamíferos da floresta")):
        with cols[i%3]: desenhar_cartao(a, f"florest_{i}")

elif aba == "🌊 Oceanos":
    st.title("🌊 Abismo Marinho")
    st.map(pd.DataFrame({'lat': [20.0, -10.0], 'lon': [-40.0, -140.0]}))
    cols = st.columns(3)
    for i, a in enumerate(buscar_api("Peixes e baleias")):
        with cols[i%3]: desenhar_cartao(a, f"ocean_{i}")

elif aba == "🔬 Laboratório":
    st.title("🔬 Laboratório de Pesquisa")
    pesq = st.text_input("Termo científico ou espécie:")
    res_lab = buscar_api(pesq)
    cols_lab = st.columns(3)
    for i, a in enumerate(res_lab):
        with cols_lab[i%3]:
            desenhar_cartao(a, f"lab_premium_{i}")

elif aba == "⭐ Coleção":
    st.title("⭐ Minha Reserva")
    for i, a in enumerate(st.session_state.zoo):
        st.markdown(f"<div class='cc-card'><b>{a['nome']}</b></div>", unsafe_allow_html=True)
        if st.button("Libertar", key=f"lib_{i}"):
            st.session_state.zoo.pop(i)
            st.rerun()

elif aba == "⚙️ Definições":
    st.title("⚙️ Definições")
    st.session_state.codigo = st.text_input("Código de Acesso:", type="password")
    st.session_state.codigo_perm = st.text_input("Código Permanente:", type="password")
    if st.button("Inserir"): st.balloons()
    st.session_state.cor_card = st.selectbox("Cor dos Cartões:", list(cores_hex.keys()))
    st.session_state.cor_fundo = st.selectbox("Cor do Ecrã:", list(cores_hex.keys()))
    st.session_state.luz = st.toggle("Modo Dia")
