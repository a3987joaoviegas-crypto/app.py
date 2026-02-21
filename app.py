import streamlit as st
import pd
import requests
import random

# 1. CONFIGURAÇÃO BÁSICA
st.set_page_config(page_title="MundoVivo 🌍", page_icon="🌍", layout="wide")

# 2. SISTEMA DE MEMÓRIA
for key, val in {
    'luz': False, 'zoo': [], 'codigo': "", 'codigo_perm': "", 
    'cor_card': "Preto", 'cor_fundo': "Preto", 'chat_pos': "sidebar", 'nome_zoologo': "Explorador"
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Lógica de Permissões
is_perm_active = st.session_state.codigo_perm == "67lucas62"
is_mestre = st.session_state.codigo == "6626" or is_perm_active
is_ai_unlocked = st.session_state.codigo == "33236" or is_perm_active
LIMITE = 80 if is_mestre else 20

# Título do Cartão Dinâmico
titulo_zoologo = "🏆 Zoólogo Profissional" if is_mestre else "💳 Zoólogo"

# 3. DESIGN (CSS)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f", "Amarelo": "#f1c40f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23") if not st.session_state.luz else "#ffffff"
app_bg = cores_hex.get(st.session_state.cor_fundo, "#0b1117") if not st.session_state.luz else "#f0f2f6"
txt_color = "#000" if (st.session_state.luz or st.session_state.cor_card == "Branco") else "#fff"

border_css = "border-left: 15px solid; border-right: 5px solid;"
if is_perm_active:
    border_css += "border-image: linear-gradient(45deg, #ff00ff, #00ffff) 1; animation: galactico 3s linear infinite;"
else:
    b_col = "#ffd700" if is_mestre else "#2ea043"
    border_css += f"border-color: {b_col};"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {app_bg}; color: {txt_color}; }}
    .cc-card {{ background: {c_bg} !important; border-radius: 15px; padding: 18px; {border_css} box-shadow: 8px 8px 20px rgba(0,0,0,0.5); margin-bottom: 20px; color: {txt_color} !important; }}
    .sidebar-card {{ background: #2ea043; padding: 15px; border-radius: 10px; border: 2px solid gold; color: white; }}
    @keyframes galactico {{ 0% {{ filter: hue-rotate(0deg); }} 100% {{ filter: hue-rotate(360deg); }} }}
    </style>
    """, unsafe_allow_html=True)

# 4. FUNÇÕES
def buscar_api(termo, qtd=9):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={termo}&taxon_id=1&per_page={qtd}&locale=pt-PT"
        r = requests.get(url).json()
        return [{'nome': i.get('preferred_common_name', i['name']).title(), 'sci': i['name'], 'foto': i['default_photo']['medium_url'] if i.get('default_photo') else "", 'id': i['id']} for i in r['results']]
    except: return []

def obter_bio(nome):
    n = nome.lower()
    if any(x in n for x in ['tubarão', 'leão', 'lobo', 'tigre', 'águia', 'orca']):
        return "Carnívoro 🥩", "Predador 🏹", "Vivíparo 🍼"
    return "Herbívoro/Ominívoro 🌿", "Variável 🌍", "Ovíparo/Vivíparo 🥚"

def render_cartao(an, k):
    alim, amb, repr = obter_bio(an['nome'])
    st.markdown(f"""
    <div class='cc-card'>
        <img src='{an['foto']}' width='100%' style='border-radius:10px; height:180px; object-fit:cover;'>
        <div style='font-size:1.4em; font-weight:bold;'>{an['nome']}</div>
        <div style='font-style:italic; opacity:0.7;'>{an['sci']}</div>
        <div style='font-size: 0.8em; margin-top: 5px;'>
            <b>🍴 Alimentação:</b> {alim}<br>
            <b>🏠 Ambiente:</b> {amb}<br>
            <b>🐣 Reprodução:</b> {repr}
        </div>
        {f"<div style='background:rgba(255,215,0,0.2); padding:5px; border-radius:5px; margin-top:10px; text-align:center; font-weight:bold;'>ESTADO: PROTEGIDO 🚨</div>" if is_mestre else ""}
    </div>
    """, unsafe_allow_html=True)
    if st.button(f"Guardar Animal", key=k):
        if len(st.session_state.zoo) < LIMITE:
            st.session_state.zoo.append(an)
            st.toast(f"{an['nome']} guardado!")

# 5. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    # Cartão de Zoólogo Dinâmico
    st.markdown(f"""
    <div class='sidebar-card'>
        <h4 style='margin:0;'>{titulo_zoologo}</h4>
        <p style='margin:0; font-weight:bold;'>{st.session_state.nome_zoologo}</p>
        <small>Espaço: {len(st.session_state.zoo)}/{LIMITE}</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    aba = st.radio("Navegação", ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "🥊 Luta Especial", "⭐ Coleção", "⚙️ Definições"])

# 6. INTERFACE
if aba == "🥊 Luta Especial":
    st.title("🥊 Arena de Luta Especial")
    categoria = st.selectbox("Escolha a Classe de Combate:", ["Vertebrados", "Invertebrados", "Mamíferos", "Répteis", "Aves"])
    inimigos = buscar_api(categoria, qtd=3)
    cols = st.columns(3)
    for i, a in enumerate(inimigos):
        with cols[i]: render_cartao(a, f"fight_{i}")
    st.markdown(f"<p style='text-align:center; font-weight:bold; margin-top:20px;'>(Ex: {categoria})</p>", unsafe_allow_html=True)

elif aba == "🔬 Laboratório":
    st.title("🔬 Laboratório de Pesquisa")
    pesq = st.text_input("Análise Biológica (Pesquisa Livre):")
    if pesq:
        cols = st.columns(3)
        for i, a in enumerate(buscar_api(pesq)):
            with cols[i%3]: render_cartao(a, f"l_{i}")

elif aba == "🌲 Florestas":
    st.title("🌲 Biomas Florestais")
    tipo = st.selectbox("Escolha a Floresta:", ["Amazónia", "Taiga", "Savana", "Mata Atlântica"])
    cols = st.columns(3)
    for i, a in enumerate(buscar_api(f"Animais da {tipo}")):
        with cols[i%3]: render_cartao(a, f"f_{i}")

elif aba == "🌊 Oceanos":
    st.title("🌊 Oceanos")
    oceano = st.selectbox("Região Marinha:", ["Oceano Atlântico", "Oceano Pacífico", "Recifes de Coral"])
    cols = st.columns(3)
    for i, a in enumerate(buscar_api(f"Animais do {oceano}")):
        with cols[i%3]: render_cartao(a, f"o_{i}")

elif aba == "🌍 Países":
    st.title("🌍 Países")
    pais = st.selectbox("Selecione o País:", ["Portugal", "Brasil", "Angola", "Moçambique"])
    cols = st.columns(3)
    for i, a in enumerate(buscar_api(f"Animais de {pais}")):
        with cols[i%3]: render_cartao(a, f"p_{i}")

elif aba == "⭐ Coleção":
    st.title("⭐ Reserva do Zoologo")
    for i, a in enumerate(st.session_state.zoo):
        st.markdown(f"<div class='cc-card'><b>{a['nome']}</b></div>", unsafe_allow_html=True)
        if st.button("Libertar", key=f"lib_{i}"):
            st.session_state.zoo.pop(i); st.rerun()

elif aba == "⚙️ Definições":
    st.title("⚙️ Definições")
    st.session_state.nome_zoologo = st.text_input("Seu Nome:", value=st.session_state.nome_zoologo)
    st.session_state.codigo = st.text_input("Código de Acesso:", type="password")
    st.session_state.codigo_perm = st.text_input("Código Permanente:", type="password")
    st.session_state.cor_card = st.selectbox("Cor Cartão:", list(cores_hex.keys()))
    st.session_state.luz = st.toggle("Modo Dia")
