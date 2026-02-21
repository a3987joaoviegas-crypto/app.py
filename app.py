import streamlit as st
import requests
import random

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo 🌍", layout="wide")

# 2. SISTEMA DE IDIOMAS
idiomas = {
    "Português": {"paises": "🌍 Países", "florestas": "🌲 Habitats", "oceanos": "🌊 Oceanos", "lab": "🔬 Pesquisa", "col": "⭐ Coleção", "def": "⚙️ Definições", "mega": "💎 PREMIUM", "guardar": "Confirmar Alterações"},
    "English": {"paises": "🌍 Countries", "florestas": "🌲 Habitats", "oceanos": "🌊 Oceans", "lab": "🔬 Research", "col": "⭐ Collection", "def": "Settings", "mega": "💎 PREMIUM", "guardar": "Save"}
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
    borda_style = "border: 5px solid transparent; border-image: linear-gradient(45deg, #ff00ff, #00ffff, #ff00ff, #00ffff) 1; animation: galatico_borda 3s linear infinite;"
elif is_premium:
    borda_style = "border: 4px solid #ffd700; box-shadow: 0 0 20px #ffd700; animation: pulsar 1.5s infinite alternate;"
else:
    borda_style = "border: 4px solid #2ecc71;"

st.markdown(f"""
<style>
    @keyframes pulsar {{ from {{ box-shadow: 0 0 10px #ffd700; }} to {{ box-shadow: 0 0 25px #ffd700; }} }}
    @keyframes galatico_borda {{ 0% {{ border-image-source: linear-gradient(45deg, #ff00ff, #00ffff); }} 50% {{ border-image-source: linear-gradient(180deg, #00ffff, #ff00ff); }} 100% {{ border-image-source: linear-gradient(45deg, #ff00ff, #00ffff); }} }}
    .stApp {{ background-color: {app_bg}; color: white; }}
    .cartao-cidadao {{ background: {c_bg} !important; color: {txt_c} !important; border-radius: 20px; padding: 15px; text-align: center; margin-bottom: 25px; {borda_style} }}
    .img-animal {{ width: 100%; height: 220px; border-radius: 12px; object-fit: cover; filter: none !important; }}
    .campo-cidadao {{ background: rgba(255,255,255,0.1); padding: 8px; border-radius: 8px; font-size: 0.85em; text-align: left; margin-top: 5px; border-left: 4px solid gold; }}
    .mega-box {{ background: linear-gradient(135deg, rgba(44,0,62,0.8), rgba(0,0,0,0.9)); border: 2px solid #00ffff; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 0 15px rgba(0,255,255,0.2); }}
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE DADOS
def buscar_70(q):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=70&locale={st.session_state.idioma}"
        r = requests.get(url, timeout=10).json()
        return [{'id': x['id'], 'nome': x.get('preferred_common_name', x['name']).title(), 'sci': x['name'], 
                 'foto': x['default_photo']['medium_url'] if x.get('default_photo') else "https://via.placeholder.com/400x300"} for x in r.get('results', [])]
    except: return []

def render_cartao(an, prefixo, i, habitat):
    random.seed(an['id'])
    bio = {"ali": random.choice(["🥩 Carnívoro", "🥗 Herbívoro", "🍕 Omnívoro"]), "rep": random.choice(["🥚 Ovíparo", "🍼 Vivíparo"]), "con": random.choice(["✅ Seguro", "⚠️ Vulnerável", "🚨 Em Perigo"])}
    st.markdown(f"<div class='cartao-cidadao'><img src='{an['foto']}' class='img-animal'><h4 style='margin:10px 0;'>{an['nome']}</h4><div class='campo-cidadao'><b>🏠 Vive em:</b> {habitat}</div><div class='campo-cidadao'><b>🍖 Dieta:</b> {bio['ali']}</div><div class='campo-cidadao'><b>🐣 Reprodução:</b> {bio['rep']}</div>", unsafe_allow_html=True)
    if is_mestre: st.markdown(f"<div class='campo-cidadao' style='border-color: #00ff00;'><b>🛡️ Estado:</b> {bio['con']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button(f"Capturar", key=f"btn_{prefixo}_{i}", use_container_width=True):
        if len(st.session_state.zoo) < LIMITE_ZOO:
            if not any(x['id'] == an['id'] for x in st.session_state.zoo): st.session_state.zoo.append(an); st.rerun()

# 6. INTERFACE
menu_opcoes = [T['paises'], T['florestas'], T['oceanos'], T['lab'], T['col'], T['def']]
if is_mega: menu_opcoes.insert(0, T['mega'])

with st.sidebar:
    st.title("🌍 MundoVivo")
    st.info(f"👤 {st.session_state.nome_zoologo} | 🐾 {len(st.session_state.zoo)}/{LIMITE_ZOO}")
    aba = st.radio("Menu", menu_opcoes)

# LOGICA DE ABAS MEGA PREMIUM
if is_mega and aba == T['mega']:
    st.title("💎 Centro de Comando MEGA")
    
    # 🧬 LABORATÓRIO GENÉTICO
    st.markdown("<div class='mega-box'><h2>🧬 Laboratório Genético</h2>", unsafe_allow_html=True)
    if len(st.session_state.zoo) >= 2:
        c1, c2 = st.columns(2)
        a1 = c1.selectbox("Animal Base", [x['nome'] for x in st.session_state.zoo], index=0)
        a2 = c2.selectbox("Doador de DNA", [x['nome'] for x in st.session_state.zoo], index=1)
        if st.button("🧪 Realizar Fusão Genética", use_container_width=True):
            novo_nome = a1[:len(a1)//2] + a2[len(a2)//2:].lower()
            st.success(f"Sucesso! Criaste o Híbrido: **{novo_nome}**")
            st.info(f"Características herdadas: Habitat de {a1} e Dieta de {a2}")
    else: st.warning("Captura pelo menos 2 animais no teu Zoo para usar o Laboratório.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 📊 ESTATÍSTICAS E MISSÕES
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<div class='mega-box'><h3>📊 Bio-Análise</h3>", unsafe_allow_html=True)
        if st.session_state.zoo:
            alvo = st.selectbox("Escolher para Análise", [x['nome'] for x in st.session_state.zoo])
            random.seed(alvo)
            st.metric("Longevidade Esperada", f"{random.randint(10, 120)} anos")
            st.progress(random.random(), text=f"Nível de Inteligência: {random.randint(10, 100)} IQ")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_b:
        st.markdown("<div class='mega-box'><h3>🚁 Centro de Resgate</h3>", unsafe_allow_html=True)
        st.write("📡 **Radar:** Animal ferido detetado na Amazónia!")
        if st.button("🚀 Enviar Helicóptero"): 
            st.balloons()
            st.toast("Animal resgatado com sucesso!")
        st.markdown("</div>", unsafe_allow_html=True)

# ABAS NORMAIS
elif aba == T['paises']:
    p = st.selectbox("País", ["Portugal", "Brasil", "Japão", "Austrália", "Angola", "India", "USA"])
    animais = buscar_70(p); cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i % 3]: render_cartao(an, "pa", i, p)

elif aba == T['florestas']:
    h = {"Amazónia": "Amazon Forest", "Savana": "Savanna", "Deserto": "Desert", "Pantanal": "Pantanal"}
    f_sel = st.selectbox("Habitats", list(h.keys()))
    animais = buscar_70(h[f_sel]); cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i % 3]: render_cartao(an, "fl", i, f_sel)

elif aba == T['oceanos']:
    m = {"Recife de Coral": "Coral Reef", "Oceano Profundo": "Deep Sea", "Mar Mediterrâneo": "Mediterranean Sea"}
    o_sel = st.selectbox("Mares", list(m.keys()))
    animais = buscar_70(m[o_sel]); cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i % 3]: render_cartao(an, "oc", i, o_sel)

elif aba == T['lab']:
    q = st.text_input("Pesquisa Genética Livre")
    if q:
        animais = buscar_70(q); cols = st.columns(3)
        for i, an in enumerate(animais):
            with cols[i % 3]: render_cartao(an, "lb", i, "Habitat Desconhecido")

elif aba == T['col']:
    st.header("Teu Zoo")
    cols = st.columns(3)
    for i, an in enumerate(st.session_state.zoo):
        with cols[i % 3]: render_cartao(an, "col", i, "Zoo")

elif aba == T['def']:
    st.header("⚙️ Definições")
    st.session_state.nome_zoologo = st.text_input("Nome", st.session_state.nome_zoologo)
    st.session_state.codigo = st.text_input("Código Premium (6626)", type="password")
    st.session_state.codigo_perm = st.text_input("Código Mega (67lucas62)", type="password")
    st.session_state.lang_label = st.selectbox("Idioma", list(idiomas.keys()))
    st.session_state.cor_card = st.selectbox("Cor do Cartão", list(cores_hex.keys()))
    st.session_state.cor_fundo = st.selectbox("Cor de Fundo", list(cores_hex.keys()))
    if st.button(T['guardar']): st.rerun()
