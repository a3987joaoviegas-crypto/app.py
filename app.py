import streamlit as st
import requests
import random

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo 🌍", layout="wide")

# 2. SISTEMA DE IDIOMAS
idiomas = {
    "Português": {"paises": "🌍 Países", "florestas": "🌲 Florestas/Habitats", "oceanos": "🌊 Oceanos/Mares", "lab": "🔬 Laboratório", "col": "⭐ Coleção", "def": "⚙️ Definições", "guardar": "Confirmar Alterações"},
    "English": {"paises": "🌍 Countries", "florestas": "🌲 Habitats", "oceanos": "🌊 Oceans", "lab": "🔬 Laboratory", "col": "⭐ Collection", "def": "⚙️ Settings", "guardar": "Save Changes"}
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

# 4. DESIGN CSS (BORDAS E AURAS)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f", "Castanho": "#3e2723"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23")
app_bg = cores_hex.get(st.session_state.cor_fundo, "#0b1117")
txt_c = "#000" if st.session_state.cor_card == "Branco" else "#fff"

if is_mega:
    borda_style = "border: 5px solid transparent; border-image: linear-gradient(45deg, #ff00ff, #00ffff, #ff00ff, #00ffff) 1; animation: galatico 3s linear infinite;"
elif is_premium:
    borda_style = "border: 4px solid #ffd700; box-shadow: 0 0 20px #ffd700; animation: pulsar 1.5s infinite alternate;"
else:
    borda_style = "border: 4px solid #2ecc71;"

st.markdown(f"""
<style>
    @keyframes pulsar {{ from {{ box-shadow: 0 0 10px #ffd700; }} to {{ box-shadow: 0 0 25px #ffd700; }} }}
    @keyframes galatico {{ 0% {{ filter: hue-rotate(0deg); }} 100% {{ filter: hue-rotate(360deg); }} }}
    .stApp {{ background-color: {app_bg}; color: white; }}
    .cartao-cidadao {{
        background: {c_bg} !important;
        color: {txt_c} !important;
        border-radius: 20px;
        padding: 15px;
        text-align: center;
        margin-bottom: 25px;
        {borda_style}
    }}
    .img-container {{ width: 100%; height: 220px; border-radius: 12px; overflow: hidden; margin-bottom: 12px; }}
    .img-animal {{ width: 100%; height: 100%; object-fit: cover; }}
    .campo-cidadao {{
        background: rgba(255,255,255,0.1);
        padding: 8px;
        border-radius: 8px;
        font-size: 0.85em;
        text-align: left;
        margin-top: 5px;
        border-left: 4px solid gold;
    }}
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE BUSCA (GARANTE 70 RESULTADOS)
def buscar_70(q):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=70&locale={st.session_state.idioma}"
        r = requests.get(url, timeout=10).json()
        results = r.get('results', [])
        return [{'id': x['id'], 'nome': x.get('preferred_common_name', x['name']).title(), 'sci': x['name'], 
                 'foto': x['default_photo']['medium_url'] if x.get('default_photo') else "https://via.placeholder.com/400x300"} for x in results]
    except: return []

def render_cartao(an, prefixo, i, habitat):
    random.seed(an['id'])
    bio = {
        "ali": random.choice(["🥩 Carnívoro", "🥗 Herbívoro", "🍕 Omnívoro"]),
        "rep": random.choice(["🥚 Ovíparo", "🍼 Vivíparo"]),
        "con": random.choice(["✅ Seguro", "⚠️ Vulnerável", "🚨 Em Perigo"])
    }
    
    st.markdown(f"""
    <div class='cartao-cidadao'>
        <div class='img-container'><img src='{an['foto']}' class='img-animal'></div>
        <h4 style='margin:0;'>{an['nome']}</h4>
        <div class='campo-cidadao'><b>🏠 Vive em:</b> {habitat}</div>
        <div class='campo-cidadao'><b>🍖 Dieta:</b> {bio['ali']}</div>
        <div class='campo-cidadao'><b>🐣 Reprodução:</b> {bio['rep']}</div>
    """, unsafe_allow_html=True)
    
    if is_mestre:
        st.markdown(f"<div class='campo-cidadao' style='border-color: #00ff00;'><b>🛡️ Estado:</b> {bio['con']}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button(f"Capturar", key=f"btn_{prefixo}_{i}", use_container_width=True):
        if len(st.session_state.zoo) < LIMITE_ZOO:
            if not any(x['id'] == an['id'] for x in st.session_state.zoo):
                st.session_state.zoo.append(an); st.rerun()

# 6. INTERFACE
with st.sidebar:
    st.title("🌍 MundoVivo")
    st.info(f"👤 {st.session_state.nome_zoologo}\n🐾 Zoo: {len(st.session_state.zoo)}/{LIMITE_ZOO}")
    aba = st.radio("Explorar Mundo", [T['paises'], T['florestas'], T['oceanos'], T['lab'], T['col'], T['def']])

def grid_3(termo, prefixo, habitat_nome):
    animais = buscar_70(termo)
    if animais:
        for i in range(0, len(animais), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(animais):
                    with cols[j]: render_cartao(animais[i+j], prefixo, i+j, habitat_nome)
    else: st.warning("A procurar mais espécies...")

# ABAS COM BUSCA AMPLIADA
if aba == T['paises']:
    p = st.selectbox("País", ["Portugal", "Brasil", "Japão", "Austrália", "Angola", "India", "Madagascar", "Canada", "EUA", "Egito"])
    grid_3(p, "pa", f"Região de {p}")

elif aba == T['florestas']:
    h = {"Amazónia": "Amazon Forest", "Savana": "Savanna", "Deserto": "Desert", "Selva Tropical": "Rainforest", "Montanhas": "Mountains", "Pantanal": "Pantanal"}
    f_sel = st.selectbox("Habitat", list(h.keys()))
    grid_3(h[f_sel], "fl", f_sel)

elif aba == T['oceanos']:
    m = {"Recife de Coral": "Coral Reef", "Oceano Profundo": "Deep Sea", "Mar Mediterrâneo": "Mediterranean Sea", "Ártico": "Arctic Ocean", "Oceano Pacífico": "Pacific Ocean"}
    o_sel = st.selectbox("Mares e Oceanos", list(m.keys()))
    grid_3(m[o_sel], "oc", o_sel)

elif aba == T['lab']:
    q = st.text_input("Pesquisa por Nome")
    if q: grid_3(q, "lb", "Habitat Desconhecido")

elif aba == T['col']:
    st.header("Teu Zoo")
    for i in range(0, len(st.session_state.zoo), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(st.session_state.zoo):
                with cols[j]: render_cartao(st.session_state.zoo[i+j], "col", i+j, "Meu Zoo")

elif aba == T['def']:
    st.header("⚙️ Definições")
    st.session_state.nome_zoologo = st.text_input("Nome", st.session_state.nome_zoologo)
    st.session_state.codigo = st.text_input("Código Premium", type="password")
    st.session_state.codigo_perm = st.text_input("Código Mega", type="password")
    st.session_state.cor_card = st.selectbox("Cor do Cartão", list(cores_hex.keys()))
    if st.button("Guardar"): st.rerun()
