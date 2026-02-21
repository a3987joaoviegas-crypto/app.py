   import streamlit as st
import requests
import random
import time

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo Ultra 🌍", layout="wide")

# 2. ESTADO DA APP
for key, val in {
    'zoo': [], 'codigo': "", 'codigo_perm': "", 'codigo_crio': "", 'pontos': 250,
    'cor_card': "Preto", 'cor_fundo': "Preto", 'idioma': "pt-PT", 
    'lang_label': "Português", 'nome_zoologo': "Explorador",
    'luminosidade': 100, 'negrito': False, 'criogenia_storage': [],
    'resgates_ativos': ["Tigre de Bengala ferido", "Panda Gigante faminto", "Baleia Azul encalhada"]
}.items():
    if key not in st.session_state: st.session_state[key] = val

# LÓGICA DE PRIVILÉGIOS
is_mega = st.session_state.codigo_perm == "67lucas62"
is_premium = st.session_state.codigo == "6626"
is_crio_unlocked = st.session_state.codigo_crio == "CRIO99"
is_mestre = is_premium or is_mega
LIMITE_ZOO = 80 if is_mestre else 20

# 3. DESIGN CSS (INTERFACES TEMÁTICAS)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Azul": "#001f3f", "Verde": "#002b1b"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23")
app_bg = cores_hex.get(st.session_state.cor_fundo, "#0b1117")
txt_c = "#000" if st.session_state.cor_card == "Branco" else "#fff"

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; color: white; filter: brightness({st.session_state.luminosidade}%); font-weight: {"bold" if st.session_state.negrito else "normal"}; }}
    
    /* CARTÃO DE CIDADÃO */
    .cartao-cidadao {{
        background: {c_bg} !important; color: {txt_c} !important;
        border-radius: 20px; padding: 15px; text-align: center; margin-bottom: 25px;
        border: 4px solid {"#ff00ff" if is_mega else "#2ecc71"};
        {"animation: galatico 3s linear infinite;" if is_mega else ""}
    }}
    @keyframes galatico {{ 0% {{ filter: hue-rotate(0deg); }} 100% {{ filter: hue-rotate(360deg); }} }}
    
    /* LABORATÓRIO E SIMULADORES */
    .interface-premium {{
        background: linear-gradient(180deg, #001f3f, #000);
        border: 2px solid #00ffff; border-radius: 20px; padding: 25px; box-shadow: 0 0 20px rgba(0,255,255,0.3);
    }}

    /* BOTÕES */
    div.stButton > button {{ background-color: #2ecc71 !important; color: white !important; border: none !important; width: 100%; }}
    .stButton > button[kind="primary"] {{ background-color: #3498db !important; }}
    .btn-perigo > div > button {{ background-color: #e74c3c !important; }}
    
    .campo-cidadao {{ background: rgba(255,255,255,0.1); padding: 8px; border-radius: 8px; font-size: 0.85em; text-align: left; margin-top: 5px; border-left: 4px solid gold; }}
</style>
""", unsafe_allow_html=True)

# 4. MOTOR DE DADOS
def buscar_70(q):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=70&locale={st.session_state.idioma}"
        return requests.get(url, timeout=10).json().get('results', [])
    except: return []

def render_cartao(an, habitat, prefixo, i, modo_crio=False):
    random.seed(an['id'])
    bio = {"ali": random.choice(["🥩 Carnívoro", "🥗 Herbívoro", "🍕 Omnívoro"]), 
           "rep": random.choice(["🥚 Ovíparo", "🍼 Vivíparo"]),
           "con": random.choice(["✅ Seguro", "⚠️ Vulnerável", "🚨 Em Perigo"])}
    
    st.markdown(f"""
    <div class='cartao-cidadao'>
        <img src='{an.get('default_photo', {{}}).get('medium_url', '')}' style='width:100%; height:180px; object-fit:cover; border-radius:12px;'>
        <h4>{an.get('preferred_common_name', an['name']).title()}</h4>
        <div class='campo-cidadao'><b>🏠 Vive em:</b> {habitat}</div>
        <div class='campo-cidadao'><b>🍖 Dieta:</b> {bio['ali']}</div>
        <div class='campo-cidadao'><b>🐣 Reprodução:</b> {bio['rep']}</div>
    """, unsafe_allow_html=True)
    if is_mestre: st.markdown(f"<div class='campo-cidadao' style='border-color:#00ff00;'><b>🛡️ Estado:</b> {bio['con']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if not modo_crio:
        if st.button(f"Capturar", key=f"{prefixo}_{i}"):
            if len(st.session_state.zoo) < LIMITE_ZOO:
                st.session_state.zoo.append(an); st.rerun()
    else:
        if st.button(f"Descongelar", key=f"unfreeze_{i}"):
            if len(st.session_state.zoo) < LIMITE_ZOO:
                st.session_state.zoo.append(st.session_state.criogenia_storage.pop(i)); st.rerun()

# 5. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    st.write(f"🏆 {st.session_state.pontos} Pts | 🐾 {len(st.session_state.zoo)}/{LIMITE_ZOO}")
    
    nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"]
    if is_mega:
        st.markdown("---")
        st.subheader("💎 SETORES MEGA")
        nav = ["🧬 Fusão & Scanner", "🚁 Resgates", "🛰️ Radar", "🪐 Eco-Simulador", "💊 Criogenia"] + nav
    aba = st.radio("Menu de Navegação", nav)

# 6. LÓGICA DAS ABAS
if aba == "💊 Criogenia" and is_mega:
    st.title("💊 Câmara de Criostase")
    if not is_crio_unlocked:
        st.error("⚠️ ACESSO BLOQUEADO: Requer Protocolo de Segurança CRIO99.")
    else:
        st.success("✅ Protocolo Ativo. Armazenamento Infinito Disponível.")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Congelar")
            if st.session_state.zoo:
                sel = st.selectbox("Alvo", range(len(st.session_state.zoo)), format_func=lambda x: st.session_state.zoo[x]['name'])
                if st.button("❄️ Iniciar Congelamento"):
                    st.session_state.criogenia_storage.append(st.session_state.zoo.pop(sel)); st.rerun()
        with c2:
            st.subheader("Câmaras Ocupadas: {}".format(len(st.session_state.criogenia_storage)))
            for i, an in enumerate(st.session_state.criogenia_storage):
                render_cartao(an, "Gelo", "crio", i, modo_crio=True)

elif aba == "🧬 Fusão & Scanner" and is_mega:
    st.title("🔬 Centro de Bio-Pesquisa")
    st.markdown("<div class='interface-premium'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🧬 Laboratório Genético")
        if len(st.session_state.zoo) >= 2:
            a1 = st.selectbox("DNA 1", [x['name'] for x in st.session_state.zoo])
            a2 = st.selectbox("DNA 2", [x['name'] for x in st.session_state.zoo])
            if st.button("🧪 FUNDIR"):
                st.success(f"Híbrido criado: {a1[:4]}{a2[-4:].lower()}")
    with c2:
        st.subheader("📊 Bio-Scanner")
        if st.session_state.zoo:
            alvo = st.selectbox("Analisar", [x['name'] for x in st.session_state.zoo])
            st.write("🧬 Sequência: ⶫ ⶬ ⶭ ⶮ")
            st.metric("Poder Genético", f"{random.randint(100, 999)} GP")
    st.markdown("</div>", unsafe_allow_html=True)

elif aba == "🚁 Resgates" and is_mega:
    st.title("🚁 Centro de Missões")
    for idx, res in enumerate(st.session_state.resgates_ativos):
        c1, c2 = st.columns([3, 1])
        c1.warning(f"🚨 {res}")
        if c2.button("SALVAR", key=f"res_{idx}"):
            st.markdown("<h2 class='heli-anim' style='text-align:center;'>🚁 BRRRRRR...</h2>", unsafe_allow_html=True)
            time.sleep(1)
            st.session_state.pontos += 150
            st.session_state.resgates_ativos[idx] = random.choice(["Orca em perigo", "Elefante ferido", "Koala perdido"])
            st.rerun()

elif aba == "🌍 Países":
    p = st.selectbox("País", ["Portugal", "Brasil", "Japão", "Austrália", "Angola", "India", "EUA", "Canada"])
    animais = buscar_70(p)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: render_cartao(an, p, "pa", i)

elif aba == "🌲 Florestas":
    f = st.selectbox("Bioma", ["Amazónia", "Savana", "Selva Tropical", "Pantanal", "Taiga"])
    animais = buscar_70(f)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: render_cartao(an, f, "fl", i)

elif aba == "🌊 Oceanos":
    o = st.selectbox("Oceano", ["Recife de Coral", "Mar Mediterrâneo", "Oceano Profundo", "Ártico"])
    animais = buscar_70(o)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: render_cartao(an, o, "oc", i)

elif aba == "⭐ Coleção":
    st.header("🐾 Teu Zoo")
    st.markdown(f"<div class='btn-perigo'>", unsafe_allow_html=True)
    if st.button("🗑️ APAGAR TODO O ZOO"):
        st.session_state.zoo = []; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, an in enumerate(st.session_state.zoo):
        with cols[i%3]:
            render_cartao(an, "Meu Zoo", "col", i)
            st.markdown(f"<div class='btn-perigo'>", unsafe_allow_html=True)
            if st.button(f"Eliminar", key=f"del_{i}"):
                st.session_state.zoo.pop(i); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    st.session_state.nome_zoologo = st.text_input("Nome do Zoólogo", st.session_state.nome_zoologo)
    st.session_state.codigo = st.text_input("Código Premium", type="password")
    st.session_state.codigo_perm = st.text_input("Código Mega", type="password")
    st.session_state.codigo_crio = st.text_input("Código Criogenia", type="password")
    
    st.session_state.cor_fundo = st.selectbox("Cor de Fundo", ["Preto", "Branco", "Azul", "Verde"])
    st.session_state.luminosidade = st.slider("Luminosidade", 50, 150, 100)
    st.session_state.negrito = st.checkbox("Texto em Negrito")
    if st.button("Confirmar Alterações", type="primary"): st.rerun()
