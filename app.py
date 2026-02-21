import streamlit as st
import requests
import random

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo 🌍", layout="wide")

# 2. ESTADO DA APP
if 'zoo' not in st.session_state: st.session_state.zoo = []
if 'favs' not in st.session_state: st.session_state.favs = set()

for key, val in {
    'codigo': "", 'cor_card': "Preto", 'cor_fundo': "Preto", 
    'idioma': "pt-PT", 'nome_zoologo': "Explorador"
}.items():
    if key not in st.session_state: st.session_state[key] = val

is_mestre = st.session_state.codigo == "6626"
LIMITE_ZOO = 80 if is_mestre else 20
LIMITE_FAV = 40 if is_mestre else 10 

# 3. DESIGN CSS (IMAGENS MÉDIAS - O EQUILÍBRIO DE ANTES)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23")
app_bg = cores_hex.get(st.session_state.cor_fundo, "#0b1117")
txt_c = "#000" if st.session_state.cor_card == "Branco" else "#fff"

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; color: white; }}
    .cartao-cidadao {{
        background: {c_bg};
        color: {txt_c};
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 2px solid rgba(255,215,0,0.4);
        margin-bottom: 25px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
        transition: 0.3s;
    }}
    .cartao-cidadao:hover {{ transform: scale(1.02); border-color: gold; }}
    /* O TAMANHO QUE PEDISTE */
    .img-media {{
        width: 100%;
        height: 250px;
        border-radius: 10px;
        object-fit: cover;
        margin-bottom: 12px;
    }}
    .info-grid {{
        display: grid;
        grid-template-columns: 1fr;
        gap: 5px;
        margin-top: 10px;
    }}
    .dado {{
        background: rgba(255,255,255,0.1);
        padding: 8px;
        border-radius: 6px;
        font-size: 0.85em;
        text-align: left;
    }}
    .premium-tag {{
        background: linear-gradient(90deg, #ffd700, #ff8c00);
        color: black;
        padding: 8px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 0.85em;
        margin-top: 5px;
    }}
</style>
""", unsafe_allow_html=True)

# 4. LÓGICA DE DADOS
def get_biometria(id_an):
    random.seed(id_an)
    return {
        "amb": random.choice(["Terrestre", "Aquático", "Aéreo", "Anfíbio"]),
        "ali": random.choice(["Herbívoro", "Carnívoro", "Omnívoro"]),
        "rep": random.choice(["Ovíparo", "Vivíparo", "Ovovivíparo"]),
        "con": random.choice(["Seguro", "Vulnerável", "Em Perigo", "Crítico"])
    }

def buscar_70(q):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=70&locale=pt-PT"
        r = requests.get(url, timeout=10).json()
        return [{
            'id': x['id'],
            'nome': x.get('preferred_common_name', x['name']).title(),
            'sci': x['name'],
            'foto': x['default_photo']['medium_url'] if x.get('default_photo') else "https://via.placeholder.com/300x250"
        } for x in r.get('results', [])]
    except: return []

# 5. RENDERIZADOR
def criar_cartao(an, prefixo, i):
    bio = get_biometria(an['id'])
    is_fav = an['id'] in st.session_state.favs
    
    st.markdown(f"""
    <div class='cartao-cidadao'>
        <img src='{an['foto']}' class='img-media'>
        <h3 style='margin:0;'>{an['nome']}</h3>
        <p style='font-style:italic; font-size:0.8em; opacity:0.7;'>{an['sci']}</p>
        <div class='info-grid'>
            <div class='dado'>🌍 <b>Ambiente:</b> {bio['amb']}</div>
            <div class='dado'>🍖 <b>Alimentação:</b> {bio['ali']}</div>
            <div class='dado'>🐣 <b>Reprodução:</b> {bio['rep']}</div>
    """, unsafe_allow_html=True)
    
    if is_mestre:
        st.markdown(f"<div class='premium-tag'>🛡️ Conservação: {bio['con']}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='dado' style='color:#ff4b4b;'>🔒 Conservação: Bloqueado</div>", unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    if c1.button("➕", key=f"add_{prefixo}_{i}", use_container_width=True):
        if len(st.session_state.zoo) < LIMITE_ZOO:
            if not any(x['id'] == an['id'] for x in st.session_state.zoo):
                st.session_state.zoo.append(an)
                st.rerun()
    if c2.button("⭐" if not is_fav else "🌟", key=f"fav_{prefixo}_{i}", use_container_width=True):
        if is_fav: st.session_state.favs.remove(an['id'])
        elif len(st.session_state.favs) < LIMITE_FAV: st.session_state.favs.add(an['id'])
        st.rerun()

# 6. INTERFACE
with st.sidebar:
    st.title("🌍 MundoVivo")
    st.success(f"👤 {st.session_state.nome_zoologo}\n\n🐾 {len(st.session_state.zoo)}/{LIMITE_ZOO}\n⭐ {len(st.session_state.favs)}/{LIMITE_FAV}")
    aba = st.radio("Menu", ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"])

def grelha_4(termo, prefixo):
    animais = buscar_70(termo)
    for i in range(0, len(animais), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(animais):
                with cols[j]:
                    criar_cartao(animais[i+j], prefixo, i+j)

# ABAS
if "Países" in aba:
    p = st.selectbox("País", ["Portugal", "Brasil", "Angola", "Japão", "Austrália"])
    grelha_4(p, "pa")
elif "Florestas" in aba:
    f = st.selectbox("Bioma", ["Rainforest", "Savanna", "Desert"])
    grelha_4(f, "fl")
elif "Oceanos" in aba:
    o = st.selectbox("Oceano", ["Coral Reef", "Atlantic Ocean", "Deep Sea"])
    grelha_4(o, "oc")
elif "Laboratório" in aba:
    q = st.text_input("Procurar espécie", "Lince")
    if q: grelha_4(q, "lb")
elif "Coleção" in aba:
    st.header("Teu Zoo")
    for i in range(0, len(st.session_state.zoo), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(st.session_state.zoo):
                with cols[j]: criar_cartao(st.session_state.zoo[i+j], "col", i+j)
elif "Definições" in aba:
    st.session_state.nome_zoologo = st.text_input("Nome", st.session_state.nome_zoologo)
    st.session_state.codigo = st.text_input("Código Premium", type="password")
    st.session_state.cor_card = st.selectbox("Cor Cartão", ["Preto", "Branco", "Verde", "Azul"])
    if st.button("Guardar"): st.rerun()
