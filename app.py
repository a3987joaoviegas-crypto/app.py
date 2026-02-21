import streamlit as st
import requests
import random

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo 🌍", layout="wide")

# 2. IDIOMAS E TEMAS
idiomas = {
    "Português": {"paises": "🌍 Países", "florestas": "🌲 Florestas", "oceanos": "🌊 Oceanos", "lab": "🔬 Laboratório", "col": "⭐ Coleção", "def": "⚙️ Definições", "guardar": "Confirmar Alterações"},
    "English": {"paises": "🌍 Countries", "florestas": "🌲 Forests", "oceanos": "🌊 Oceans", "lab": "🔬 Laboratory", "col": "⭐ Collection", "def": "⚙️ Settings", "guardar": "Save Changes"}
}

# 3. ESTADO DA APP
for key, val in {
    'zoo': [], 'favs': set(), 'codigo': "", 'codigo_perm': "",
    'cor_card': "Preto", 'cor_fundo': "Preto", 'idioma': "pt-PT", 
    'lang_label': "Português", 'nome_zoologo': "Explorador"
}.items():
    if key not in st.session_state: st.session_state[key] = val

T = idiomas.get(st.session_state.lang_label, idiomas["Português"])

# LÓGICA DE NÍVEIS
is_premium = st.session_state.codigo == "6626"
is_mega = st.session_state.codigo_perm == "67lucas62"
is_mestre = is_premium or is_mega
LIMITE_ZOO = 80 if is_mestre else 20

# 4. DESIGN CSS (BORDAS E CORES ORIGINAIS)
cores_hex = {
    "Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", 
    "Azul": "#001f3f", "Castanho": "#3e2723", "Cinza": "#263238"
}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23")
app_bg = cores_hex.get(st.session_state.cor_fundo, "#0b1117")
txt_c = "#000" if st.session_state.cor_card == "Branco" else "#fff"

# Estilo das Bordas
if is_mega:
    borda_style = "border: 5px solid transparent; border-image: linear-gradient(45deg, #ff00ff, #00ffff, #ff00ff, #00ffff) 1; animation: galatico 3s linear infinite;"
elif is_premium:
    borda_style = "border: 4px solid #ffd700; box-shadow: 0 0 20px #ffd700; animation: pulsar 1.5s infinite alternate;"
else:
    borda_style = "border: 4px solid #2ecc71;" # Verde Grátis

st.markdown(f"""
<style>
    @keyframes pulsar {{ from {{ box-shadow: 0 0 10px #ffd700; }} to {{ box-shadow: 0 0 25px #ffd700; }} }}
    @keyframes galatico {{ 0% {{ filter: hue-rotate(0deg); }} 100% {{ filter: hue-rotate(360deg); }} }}
    
    .stApp {{ background-color: {app_bg}; color: white; }}
    
    .cartao-cidadao {{
        background: {c_bg} !important;
        color: {txt_c} !important;
        border-radius: 20px;
        padding: 18px;
        text-align: center;
        margin-bottom: 30px;
        {borda_style}
        transition: transform 0.3s;
    }}
    .cartao-cidadao:hover {{ transform: scale(1.02); }}
    
    .img-container {{
        width: 100%;
        height: 250px;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 15px;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    .img-animal {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        filter: none !important; /* Garante as cores originais */
    }}
    .campo-cidadao {{
        background: rgba(255,255,255,0.12);
        padding: 10px;
        border-radius: 8px;
        font-size: 0.85em;
        text-align: left;
        margin-top: 6px;
        border-left: 5px solid gold;
    }}
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE BUSCA (70 ANIMAIS)
def buscar_70(q):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=70&locale={st.session_state.idioma}"
        r = requests.get(url, timeout=10).json()
        return [{'id': x['id'], 'nome': x.get('preferred_common_name', x['name']).title(), 'sci': x['name'], 
                 'foto': x['default_photo']['medium_url'] if x.get('default_photo') else "https://via.placeholder.com/400x300"} for x in r.get('results', [])]
    except: return []

def render_cartao(an, prefixo, i):
    random.seed(an['id'])
    bio = {
        "amb": random.choice(["🏔️ Terrestre", "🌊 Aquático", "☁️ Aéreo", "🌿 Anfíbio"]),
        "ali": random.choice(["🥩 Carnívoro", "🥗 Herbívoro", "🍕 Omnívoro", "🐜 Insetívoro"]),
        "rep": random.choice(["🥚 Ovíparo", "🍼 Vivíparo"]),
        "con": random.choice(["✅ Seguro", "⚠️ Vulnerável", "🚨 Em Perigo", "💀 Crítico"])
    }
    
    st.markdown(f"""
    <div class='cartao-cidadao'>
        <div class='img-container'>
            <img src='{an['foto']}' class='img-animal'>
        </div>
        <h3 style='margin:0;'>{an['nome']}</h3>
        <p style='font-style:italic; font-size:0.85em; opacity:0.8;'>{an['sci']}</p>
        <div class='campo-cidadao'><b>🌎 Ambiente:</b> {bio['amb']}</div>
        <div class='campo-cidadao'><b>🍖 Alimentação:</b> {bio['ali']}</div>
        <div class='campo-cidadao'><b>🐣 Reprodução:</b> {bio['rep']}</div>
    """, unsafe_allow_html=True)
    
    if is_mestre:
        st.markdown(f"<div class='campo-cidadao' style='border-color: #00ff00;'><b>🛡️ Conservação:</b> {bio['con']}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='campo-cidadao' style='border-color: red; opacity: 0.5;'><b>🛡️ Conservação:</b> 🔒 Bloqueado</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button(f"Capturar {an['nome']}", key=f"btn_{prefixo}_{i}", use_container_width=True):
        if len(st.session_state.zoo) < LIMITE_ZOO:
            if not any(x['id'] == an['id'] for x in st.session_state.zoo):
                st.session_state.zoo.append(an); st.toast(f"Capturado: {an['nome']}")
                st.rerun()
        else: st.error("Zoo Cheio!")

# 6. INTERFACE
with st.sidebar:
    st.title("🌍 MundoVivo")
    st.info(f"👤 {st.session_state.nome_zoologo}\n🐾 Zoo: {len(st.session_state.zoo)}/{LIMITE_ZOO}")
    aba = st.radio("Menu Principal", [T['paises'], T['florestas'], T['oceanos'], T['lab'], T['col'], T['def']])

def grid_3(termo, prefixo):
    animais = buscar_70(termo)
    for i in range(0, len(animais), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(animais):
                with cols[j]: render_cartao(animais[i+j], prefixo, i+j)

# LOGICA DE ABAS
if aba == T['paises']:
    p = st.selectbox("País", ["Portugal", "Brasil", "Japão", "Austrália", "Angola", "Moçambique", "Canadá"])
    grid_3(p, "pa")
elif aba == T['florestas']:
    f = st.selectbox("Bioma", ["Amazónia", "Savana", "Taiga Siberiana", "Pantanal", "Floresta Negra"])
    grid_3(f, "fl")
elif aba == T['oceanos']:
    o = st.selectbox("Oceano/Mar", ["Atlântico", "Pacífico", "Índico", "Recife de Coral", "Mar Vermelho"])
    grid_3(o, "oc")
elif aba == T['lab']:
    q = st.text_input("Inserir ADN Animal")
    if q: grid_3(q, "lb")
elif aba == T['col']:
    st.header("Teu Zoo")
    for i in range(0, len(st.session_state.zoo), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(st.session_state.zoo):
                with cols[j]: render_cartao(st.session_state.zoo[i+j], "col", i+j)
elif aba == T['def']:
    st.header("⚙️ Definições")
    st.session_state.nome_zoologo = st.text_input("Nome do Zoólogo", st.session_state.nome_zoologo)
    st.session_state.codigo = st.text_input("Código Premium (Dourado)", type="password")
    st.session_state.codigo_perm = st.text_input("Código Mega (Galático)", type="password")
    st.session_state.lang_label = st.selectbox("Idioma", list(idiomas.keys()))
    st.session_state.cor_card = st.selectbox("Cor do Cartão", list(cores_hex.keys()))
    st.session_state.cor_fundo = st.selectbox("Cor de Fundo", list(cores_hex.keys()))
    if st.button(T['guardar']): st.rerun()
