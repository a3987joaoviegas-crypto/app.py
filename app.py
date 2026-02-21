import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo Ultra 🌍", layout="wide")

# 2. ESTADO DO SISTEMA (CORRIGIDO: Cores em Hexadecimal para evitar erro)
chaves = {
    'zoo': [], 'tanque_fusao': [], 'criogenia_storage': [],
    'codigo': "", 'codigo_perm': "", 'codigo_crio': "", 'codigo_neon': "", 'codigo_diamante': "",
    'premium_ativo': False, 'cor_card': "#1a1c23", 'cor_fundo': "#0b1117", 
    'luminosidade': 100, 'lingua': "Português", 'inicio_premium': None
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# 3. LÓGICA DE ACESSO
is_mega = st.session_state.codigo_perm == "67lucas62"
is_premium_normal = st.session_state.codigo == "6626"
tem_beneficios_premium = is_mega or is_premium_normal
is_neon = st.session_state.codigo_neon == "6676neon7secret"
is_diamante = st.session_state.codigo_diamante == "77daimond8secret"

if is_premium_normal and st.session_state.inicio_premium is None:
    st.session_state.inicio_premium = datetime.now()

# 4. ESTILOS VISUAIS DINÂMICOS
cor_borda = "#2ecc71"
linha_separadora = "border-top: 2px solid #ffd700;"
shadow = "none"

if is_mega: 
    cor_borda = "linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet)"
    linha_separadora = "height: 3px; background: linear-gradient(90deg, red, orange, yellow, green, blue, indigo, violet); border:none;"
elif is_neon: 
    cor_borda = "#00ff00"; shadow = "0 0 15px #00ff00"
elif is_diamante: 
    cor_borda = "#00d4ff"; shadow = "0 0 20px #00d4ff"
elif is_premium_normal: 
    cor_borda = "#ffd700"

st.markdown(f"""
<style>
    .stApp {{ background-color: {st.session_state.cor_fundo}; filter: brightness({st.session_state.luminosidade}%); color: white; }}
    .cartao-cidadao {{
        background: {st.session_state.cor_card}; border-radius: 15px; padding: 20px; border: 4px solid;
        border-image: {cor_borda if "gradient" in cor_borda else "none"} 1;
        border-color: {cor_borda if "gradient" not in cor_borda else "transparent"};
        box-shadow: {shadow}; min-height: 600px; display: flex; flex-direction: column; margin-bottom: 25px;
    }}
    .img-container img {{ width: 100%; max-height: 180px; object-fit: cover; border-radius: 10px; }}
    .nome-comum {{ font-size: 1.5em; font-weight: 900; text-transform: uppercase; color: white; text-align: center; display: block; margin: 10px 0; }}
    .info-item {{ font-size: 1.05em; margin: 4px 0; text-align: left; }}
    .label {{ color: #1DB954; font-weight: bold; }}
    .linha-vip {{ {linha_separadora} margin: 15px 0; }}
    .stats-vip {{ color: #ffd700; font-weight: bold; font-size: 1.1em; }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÕES
def buscar(q):
    try: return requests.get(f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=9&locale=pt-PT").json().get('results', [])
    except: return []

def render_cartao(an, key_prefix):
    nome = an.get('preferred_common_name', an.get('name', 'Espécie Identificada')).title()
    especie = an.get('name', 'N/A')
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    
    # Dados Simulados
    random.seed(an['id'])
    dieta = random.choice(["Herbívoro", "Carnívoro", "Omnívoro"])
    habitat = random.choice(["Terrestre", "Aquático", "Aéreo"])
    repro = an.get('iconic_taxon_name', 'Biológica').upper()

    st.markdown(f"""
    <div class="cartao-cidadao">
        <div style="color:gold; font-weight:bold; text-align:center;">💳 CARTÃO DE CIDADÃO</div>
        <div class="img-container"><img src="{foto}"></div>
        <span class="nome-comum">{nome}</span>
        <div class="info-item"><span class="label">🧬 ESPÉCIE:</span> {especie}</div>
        <div class="info-item"><span class="label">🌍 AMBIENTE:</span> {habitat}</div>
        <div class="info-item"><span class="label">🥩 ALIMENTAÇÃO:</span> {dieta}</div>
        <div class="info-item"><span class="label">🍼 REPRODUÇÃO:</span> {repro}</div>
    """, unsafe_allow_html=True)
    
    if st.session_state.premium_ativo and tem_beneficios_premium:
        st.markdown(f"""
        <div class="linha-vip"></div>
        <div class="stats-vip">
            📊 ESTATÍSTICAS VIP<br>
            🚀 VELOCIDADE: {random.randint(10,160)} KM/H<br>
            ⚖️ PESO: {random.randint(1,3000)} KG
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button(f"📥 CAPTURAR", key=f"btn_{key_prefix}_{an['id']}", use_container_width=True):
        limite = 80 if tem_beneficios_premium else 20
        if len(st.session_state.zoo) < limite:
            st.session_state.zoo.append(an); st.toast(f"{nome} guardado!")
        else: st.error("Zoo cheio!")

# 6. SIDEBAR
with st.sidebar:
    if st.session_state.premium_ativo and tem_beneficios_premium:
        st.markdown('<div style="background:gold; color:black; padding:10px; border-radius:10px; text-align:center; font-weight:bold;">🏆 ZOÓLOGO PROFISSIONAL</div>', unsafe_allow_html=True)
        if is_premium_normal and st.session_state.inicio_premium:
            restante = timedelta(hours=24) - (datetime.now() - st.session_state.inicio_premium)
            if restante.total_seconds() > 0:
                h, r = divmod(int(restante.total_seconds()), 3600)
                m, s = divmod(r, 60)
                st.markdown(f'<div style="background:#ff4b4b; color:white; text-align:center; padding:5px; border-radius:5px; margin:10px 0;">⏳ {h:02d}:{m:02d}:{s:02d}</div>', unsafe_allow_html=True)

    st.title("🌍 MundoVivo")
    if tem_beneficios_premium:
        st.session_state.premium_ativo = st.toggle("🔄 MODO VIP", value=st.session_state.premium_ativo)
    
    nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    if st.session_state.premium_ativo and tem_beneficios_premium:
        nav = ["🔬 Laboratório", "🧬 Fusão", "🚁 Missões", "📊 Estatísticas", "❄️ Criogenia", "⚙️ Definições"]
    aba = st.radio("Navegação", nav)

# 7. CONTEÚDO
if aba == "🌍 Países":
    p = st.selectbox("País:", ["Brasil", "Portugal", "México", "Madagáscar", "Austrália"])
    cols = st.columns(3)
    for i, an in enumerate(buscar(p)):
        with cols[i%3]: render_cartao(an, "p")

elif aba == "🌲 Florestas":
    f = st.selectbox("Floresta:", ["Amazónia", "Selva do Congo", "Mata Atlântica", "Taiga", "Floresta Negra"])
    cols = st.columns(3)
    for i, an in enumerate(buscar(f)):
        with cols[i%3]: render_cartao(an, "f")

elif aba == "🌊 Oceanos":
    o = st.selectbox("Oceano:", ["Atlântico", "Pacífico", "Índico", "Ártico", "Mar Mediterrâneo"])
    cols = st.columns(3)
    for i, an in enumerate(buscar(o)):
        with cols[i%3]: render_cartao(an, "o")

elif aba == "🔬 Laboratório":
    q = st.text_input("Procurar espécie:")
    if q:
        cols = st.columns(3)
        for i, an in enumerate(buscar(q)):
            with cols[i%3]: render_cartao(an, "lab")
    st.divider()
    st.subheader("🦁 Inventário (Zoo)")
    if st.session_state.zoo:
        cols_z = st.columns(3)
        for i, an in enumerate(st.session_state.zoo):
            with cols_z[i%3]: render_cartao(an, f"z{i}")

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    with st.expander("🎨 VISUAL"):
        st.session_state.cor_fundo = st.color_picker("Cor de Fundo", st.session_state.cor_fundo)
        st.session_state.cor_card = st.color_picker("Cor dos Cartões", st.session_state.cor_card)
        st.session_state.luminosidade = st.slider("Brilho", 50, 150, 100)

    st.markdown("### 👑 RETÂNGULO MEGA")
    with st.container():
        st.session_state.codigo_perm = st.text_input("Código Mega", value=st.session_state.codigo_perm, type="password")

    st.markdown("### ✨ CORES & PREMIUM 24H")
    with st.container():
        st.session_state.codigo_neon = st.text_input("Código Neon", value=st.session_state.codigo_neon, type="password")
        st.session_state.codigo_diamante = st.text_input("Código Diamante", value=st.session_state.codigo_diamante, type="password")
        st.session_state.codigo = st.text_input("Código Premium 24h", value=st.session_state.codigo, type="password")
        st.session_state.codigo_crio = st.text_input("Código Crio", value=st.session_state.codigo_crio, type="password")
    
    if st.button("Guardar"): st.rerun()
