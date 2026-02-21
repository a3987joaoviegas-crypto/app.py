import streamlit as st
import requests
import random

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo 🌍", layout="wide")

# 2. TRADUÇÕES E CORES
idiomas = {
    "Português": {"paises": "Países", "florestas": "Florestas", "oceanos": "Oceanos", "lab": "Laboratório", "col": "Coleção", "def": "Definições", "guardar": "Guardar Alterações"},
    "English": {"paises": "Countries", "florestas": "Forests", "oceanos": "Oceans", "lab": "Laboratory", "col": "Collection", "def": "Settings", "guardar": "Save Changes"},
    "Español": {"paises": "Países", "florestas": "Bosques", "oceanos": "Océanos", "lab": "Laboratorio", "col": "Colección", "def": "Ajustes", "guardar": "Guardar"}
}

# 3. ESTADO DA APP
for key, val in {
    'zoo': [], 'favs': set(), 'codigo': "", 'codigo_perm': "",
    'cor_card': "Preto", 'cor_fundo': "Preto", 'idioma': "pt-PT", 
    'lang_label': "Português", 'nome_zoologo': "Explorador"
}.items():
    if key not in st.session_state: st.session_state[key] = val

T = idiomas.get(st.session_state.lang_label, idiomas["Português"])

# LÓGICA DE NÍVEIS E AURAS
is_premium = st.session_state.codigo == "6626"
is_mega = st.session_state.codigo_perm == "67lucas62"
is_mestre = is_premium or is_mega

LIMITE_ZOO = 80 if is_mestre else 20

# 4. DESIGN CSS (AURAS E CARTÃO COMPACTO)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f", "Cinza": "#2c3e50"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23")
app_bg = cores_hex.get(st.session_state.cor_fundo, "#0b1117")
txt_c = "#000" if st.session_state.cor_card == "Branco" else "#fff"

aura_style = ""
if is_mega:
    aura_style = "border: 4px solid transparent; border-image: linear-gradient(45deg, #ff00ff, #00ffff, #ff00ff) 1; animation: galatico 3s linear infinite;"
elif is_premium:
    aura_style = "box-shadow: 0 0 20px #ffd700; animation: pulsar 2s infinite alternate; border: 2px solid #ffd700;"

st.markdown(f"""
<style>
    @keyframes pulsar {{ from {{ box-shadow: 0 0 10px #ffd700; }} to {{ box-shadow: 0 0 25px #ffd700; }} }}
    @keyframes galatico {{ 0% {{ filter: hue-rotate(0deg); }} 100% {{ filter: hue-rotate(360deg); }} }}
    
    .stApp {{ background-color: {app_bg}; color: white; }}
    
    .cartao-cidadao {{
        background: {c_bg};
        color: {txt_c};
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        margin-bottom: 20px;
        {aura_style}
    }}
    .img-media {{
        width: 100%;
        height: 220px;
        border-radius: 8px;
        object-fit: cover;
    }}
    .dado {{
        background: rgba(255,255,255,0.1);
        padding: 6px 10px;
        border-radius: 6px;
        font-size: 0.8em;
        text-align: left;
        margin-top: 4px;
    }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÕES
def buscar_70(q):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=70&locale={st.session_state.idioma}"
        r = requests.get(url, timeout=10).json()
        return [{'id': x['id'], 'nome': x.get('preferred_common_name', x['name']).title(), 'sci': x['name'], 
                 'foto': x['default_photo']['medium_url'] if x.get('default_photo') else "https://via.placeholder.com/300"} for x in r.get('results', [])]
    except: return []

def criar_cartao(an, prefixo, i):
    random.seed(an['id'])
    bio = {"amb": random.choice(["Terrestre", "Aquático", "Aéreo"]), "ali": random.choice(["Herbívoro", "Carnívoro", "Omnívoro"]), 
           "rep": random.choice(["Ovíparo", "Vivíparo"]), "con": random.choice(["Seguro", "Vulnerável", "Ameaçado"])}
    
    st.markdown(f"""
    <div class='cartao-cidadao'>
        <img src='{an['foto']}' class='img-media'>
        <h4 style='margin:5px 0;'>{an['nome']}</h4>
        <div class='dado'>🌍 {bio['amb']} | 🍖 {bio['ali']}</div>
        <div class='dado'>🐣 {bio['rep']}</div>
    """, unsafe_allow_html=True)
    
    if is_mestre:
        st.markdown(f"<div class='dado' style='border:1px solid gold;'>🛡️ {bio['con']}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("Capturar", key=f"add_{prefixo}_{i}", use_container_width=True):
        if len(st.session_state.zoo) < LIMITE_ZOO:
            if not any(x['id'] == an['id'] for x in st.session_state.zoo):
                st.session_state.zoo.append(an); st.rerun()

# 6. INTERFACE
with st.sidebar:
    st.title("🌍 MundoVivo")
    st.info(f"👤 {st.session_state.nome_zoologo}\n🐾 Zoo: {len(st.session_state.zoo)}/{LIMITE_ZOO}")
    aba = st.radio("Menu", [T['paises'], T['florestas'], T['oceanos'], T['lab'], T['col'], T['def']])

def mostrar_grelha(termo, prefixo):
    animais = buscar_70(termo)
    for i in range(0, len(animais), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(animais):
                with cols[j]: criar_cartao(animais[i+j], prefixo, i+j)

if aba == T['paises']:
    p = st.selectbox("País", ["Portugal", "Brasil", "Japão", "Austrália", "Angola"])
    mostrar_grelha(p, "pa")
elif aba == T['florestas']:
    f = st.selectbox("Bioma", ["Amazónia", "Savana", "Taiga", "Mata Atlântica"])
    mostrar_grelha(f, "fl")
elif aba == T['oceanos']:
    o = st.selectbox("Oceano", ["Atlântico", "Pacífico", "Índico", "Mar Vermelho"])
    mostrar_grelha(o, "oc")
elif aba == T['lab']:
    q = st.text_input("Pesquisa Genética")
    if q: mostrar_grelha(q, "lb")
elif aba == T['col']:
    for i in range(0, len(st.session_state.zoo), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(st.session_state.zoo):
                with cols[j]: criar_cartao(st.session_state.zoo[i+j], "col", i+j)
elif aba == T['def']:
    st.session_state.nome_zoologo = st.text_input("Nome", st.session_state.nome_zoologo)
    st.session_state.codigo = st.text_input("Código Profissional (Dourado)", type="password")
    st.session_state.codigo_perm = st.text_input("Código Mega (Galático)", type="password")
    st.session_state.lang_label = st.selectbox("Idioma", list(idiomas.keys()))
    st.session_state.cor_card = st.selectbox("Cor do Cartão", list(cores_hex.keys()))
    st.session_state.cor_fundo = st.selectbox("Cor de Fundo", list(cores_hex.keys()))
    if st.button(T['guardar']): st.rerun()
