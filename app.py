import streamlit as st
import pandas as pd
import requests
import random

# 1. CONFIGURAÇÃO BÁSICA
st.set_page_config(page_title="MundoVivo 🌍", page_icon="🌍", layout="wide")

# 2. SISTEMA DE MEMÓRIA (Persistência)
for key, val in {
    'luz': False, 'zoo': [], 'codigo': "", 'codigo_perm': "", 
    'search_query': "", 'cor_card': "Preto", 'cor_fundo': "Preto", 
    'chat_pos': "sidebar", 'nome_zoologo': "Explorador"
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Lógica de Permissões
is_perm_active = st.session_state.codigo_perm == "67lucas62"
is_mestre = st.session_state.codigo == "6626" or is_perm_active
is_ai_unlocked = st.session_state.codigo == "33236" or is_perm_active
LIMITE = 80 if is_mestre else 20

# 3. DESIGN E ESTILOS (CSS)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f", "Amarelo": "#f1c40f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23") if not st.session_state.luz else "#ffffff"
app_bg = cores_hex.get(st.session_state.cor_fundo, "#0b1117") if not st.session_state.luz else "#f0f2f6"
txt_color = "#000" if (st.session_state.luz or st.session_state.cor_card == "Branco") else "#fff"

# Borda Galáctica ou Normal
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
    .zoologo-card {{
        background: linear-gradient(135deg, #2ea043, #1a1c23);
        padding: 20px; border-radius: 15px; border: 2px solid gold; margin-bottom: 20px;
    }}
    .nome-pt {{ font-size: 1.5em; font-weight: bold; margin-bottom: 2px; }}
    .nome-sci {{ font-size: 0.9em; font-style: italic; opacity: 0.7; margin-bottom: 10px; border-bottom: 1px solid gray; }}
    @keyframes galactico {{ 0% {{ filter: hue-rotate(0deg); }} 100% {{ filter: hue-rotate(360deg); }} }}
    </style>
    """, unsafe_allow_html=True)

# 4. FUNÇÕES DO MOTOR
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
        <div class='bio-info' style='font-size: 0.8em;'>
            <b>🍴 Alimentação:</b> {alim}<br>
            <b>🏠 Ambiente:</b> {amb}<br>
            <b>🐣 Reprodução:</b> {repr}
        </div>
        {f"<div style='background:rgba(255,215,0,0.2); padding:5px; border-radius:5px; margin-top:10px; text-align:center;'>⚠️ Protegido</div>" if is_mestre else ""}
    </div>
    """, unsafe_allow_html=True)
    if st.button(f"Guardar na Reserva", key=k):
        if len(st.session_state.zoo) < LIMITE:
            st.session_state.zoo.append(an)
            st.toast(f"{an['nome']} guardado!")

# 5. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    # Cartão de Zoólogo
    st.markdown(f"""
    <div class='zoologo-card'>
        <h3 style='margin:0; color:white;'>💳 Zoólogo</h3>
        <p style='margin:0; color:#ffd700;'>{st.session_state.nome_zoologo}</p>
        <p style='margin:0; font-size:0.8em; color:white;'>Reserva: {len(st.session_state.zoo)}/{LIMITE}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if is_ai_unlocked:
        st.subheader("🤖 Assistente IA")
        if st.session_state.chat_pos == "sidebar":
            st.text_input("Dúvida Biológica:", key="ia_s")
    
    st.markdown("---")
    aba = st.radio("Menu", ["🌍 Planisfério", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"])

# 6. INTERFACE POR ABA
if aba == "🌍 Planisfério":
    st.title("🌍 Exploração Global")
    st.map(pd.DataFrame({'lat': [38.7], 'lon': [-9.1]}))
    txt = st.text_input("Pesquisar espécie:", "Lince Ibérico")
    animais = buscar_api(txt)
    cols = st.columns(3)
    for i, a in enumerate(animais):
        with cols[i%3]: desenhar_cartao(a, f"plan_{i}")

elif aba == "🌲 Florestas":
    st.title("🌲 Biomas Terrestres")
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
    st.title("🔬 Laboratório Premium")
    pesq = st.text_input("Busca Avançada (Científica):")
    res_lab = buscar_api(pesq)
    cols_lab = st.columns(3)
    for i, a in enumerate(res_lab):
        with cols_lab[i%3]: desenhar_cartao(a, f"lab_{i}")

elif aba == "⭐ Coleção":
    st.title("⭐ Minha Reserva")
    st.write(f"Utilizador: **{st.session_state.nome_zoologo}**")
    for i, a in enumerate(st.session_state.zoo):
        st.markdown(f"<div class='cc-card'><b>{a['nome']}</b> ({a['sci']})</div>", unsafe_allow_html=True)
        if st.button("Libertar Animal", key=f"lib_{i}"):
            st.session_state.zoo.pop(i)
            st.rerun()

elif aba == "⚙️ Definições":
    st.title("⚙️ Painel de Controlo")
    st.session_state.nome_zoologo = st.text_input("Nome do Zoólogo:", value=st.session_state.nome_zoologo)
    st.session_state.codigo = st.text_input("Código de Acesso:", type="password")
    st.session_state.codigo_perm = st.text_input("Código Permanente:", type="password")
    if st.button("Inserir Configurações"): st.balloons()
    
    st.markdown("---")
    st.session_state.cor_card = st.selectbox("Cor dos Cartões:", list(cores_hex.keys()))
    st.session_state.cor_fundo = st.selectbox("Cor do Fundo:", list(cores_hex.keys()))
    st.session_state.luz = st.toggle("Modo Dia (Claro)")
