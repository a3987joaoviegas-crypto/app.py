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

# 3. DESIGN CSS (GRELHA DE 3 COLUNAS)
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
        padding: 20px;
        text-align: center;
        border: 2px solid rgba(255,215,0,0.4);
        margin-bottom: 30px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
    }}
    .img-media {{
        width: 100%;
        height: 300px;
        border-radius: 10px;
        object-fit: cover;
        margin-bottom: 15px;
    }}
    .info-grid {{
        display: grid;
        grid-template-columns: 1fr;
        gap: 8px;
        margin-top: 10px;
    }}
    .dado {{
        background: rgba(255,255,255,0.1);
        padding: 10px;
        border-radius: 8px;
        font-size: 0.9em;
        text-align: left;
    }}
    .premium-tag {{
        background: linear-gradient(90deg, #ffd700, #ff8c00);
        color: black;
        padding: 10px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 0.9em;
        margin-top: 8px;
    }}
</style>
""", unsafe_allow_html=True)

# 4. LÓGICA DE DADOS
def get_biometria(id_an):
    random.seed(id_an)
    return {
        "amb": random.choice(["Terrestre", "Aquático", "Aéreo", "Anfíbio"]),
        "ali": random.choice(["Herbívoro", "Carnívoro", "Omnívoro", "Insetívoro"]),
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
            'foto': x['default_photo']['medium_url'] if x.get('default_photo') else "https://via.placeholder.com/400x300"
        } for x in r.get('results', [])]
    except: return []

# 5. RENDERIZADOR
def criar_cartao(an, prefixo, i):
    bio = get_biometria(an['id'])
    is_fav = an['id'] in st.session_state.favs
    
    st.markdown(f"""
    <div class='cartao-cidadao'>
        <img src='{an['foto']}' class='img-media'>
        <h2 style='margin:0;'>{an['nome']}</h2>
        <p style='font-style:italic; font-size:0.9em; opacity:0.7;'>{an['sci']}</p>
        <div class='info-grid'>
            <div class='dado'>🌍 <b>Ambiente:</b> {bio['amb']}</div>
            <div class='dado'>🍖 <b>Alimentação:</b> {bio['ali']}</div>
            <div class='dado'>🐣 <b>Reprodução:</b> {bio['rep']}</div>
    """, unsafe_allow_html=True)
    
    if is_mestre:
        st.markdown(f"<div class='premium-tag'>🛡️ Conservação: {bio['con']}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='dado' style='color:#ff4b4b; text-align:center;'>🔒 Conservação: Bloqueado (Mestre)</div>", unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    if c1.button("Capturar", key=f"add_{prefixo}_{i}", use_container_width=True):
        if len(st.session_state.zoo) < LIMITE_ZOO:
            if not any(x['id'] == an['id'] for x in st.session_state.zoo):
                st.session_state.zoo.append(an); st.rerun()
    if c2.button("⭐" if not is_fav else "🌟", key=f"fav_{prefixo}_{i}", use_container_width=True):
        if is_fav: st.session_state.favs.remove(an['id'])
        elif len(st.session_state.favs) < LIMITE_FAV: st.session_state.favs.add(an['id'])
        st.rerun()

# 6. FUNÇÃO GRELHA 3 COLUNAS
def grelha_3(termo, prefixo):
    animais = buscar_70(termo)
    if animais:
        for i in range(0, len(animais), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(animais):
                    with cols[j]:
                        criar_cartao(animais[i + j], prefixo, i + j)
    else:
        st.warning("Nenhum animal encontrado nesta região.")

# 7. INTERFACE E LISTAS COMPLETAS
with st.sidebar:
    st.title("🌍 MundoVivo")
    st.info(f"👤 {st.session_state.nome_zoologo}\n🐾 Zoo: {len(st.session_state.zoo)}/{LIMITE_ZOO}\n⭐ Favs: {len(st.session_state.favs)}/{LIMITE_FAV}")
    aba = st.radio("Explorar", ["🌍 Países", "🌲 Florestas & Biomas", "🌊 Oceanos & Mares", "🔬 Lab", "⭐ Coleção", "⚙️ Definições"])

if "Países" in aba:
    p = st.selectbox("Escolha o País:", ["Portugal", "Brasil", "Angola", "Moçambique", "Cabo Verde", "Guiné-Bissau", "Timor-Leste", "Japão", "Austrália", "Canadá", "Índia", "Egito", "Madagáscar"])
    grelha_3(p, "pa")

elif "Florestas" in aba:
    f = st.selectbox("Escolha o Bioma:", ["Amazónia", "Floresta Tropical", "Savana Africana", "Taiga Siberiana", "Pantanal", "Deserto do Saara", "Mata Atlântica", "Tundra"])
    grelha_3(f, "fl")

elif "Oceanos" in aba:
    o = st.selectbox("Escolha o Mar/Oceano:", ["Oceano Atlântico", "Oceano Pacífico", "Oceano Índico", "Mar Mediterrâneo", "Mar Vermelho", "Recife de Coral", "Mar Profundo (Abissal)", "Oceano Ártico"])
    grelha_3(o, "oc")

elif "Lab" in aba:
    q = st.text_input("Pesquisa Genética:", "Panthera leo")
    if q: grelha_3(q, "lb")

elif "Coleção" in aba:
    st.header("Teu Zoo Particular")
    if st.session_state.zoo:
        for i in range(0, len(st.session_state.zoo), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(st.session_state.zoo):
                    with cols[j]: criar_cartao(st.session_state.zoo[i+j], "col", i+j)
    else: st.write("O teu Zoo está vazio. Explora o mundo para capturar animais!")

elif "Definições" in aba:
    st.session_state.nome_zoologo = st.text_input("Nome:", st.session_state.nome_zoologo)
    st.session_state.codigo = st.text_input("Código Mestre:", type="password")
    st.session_state.cor_card = st.selectbox("Cor Cartão:", ["Preto", "Branco", "Verde", "Azul"])
    if st.button("Guardar"): st.rerun()
