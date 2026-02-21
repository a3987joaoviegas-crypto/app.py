import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo Ultra 🌍", layout="wide")

# 2. ESTADO DO SISTEMA
chaves = {
    'zoo': [], 'tanque_fusao': [], 'criogenia_storage': [],
    'codigo': "", 'codigo_perm': "", 'codigo_crio': "", 'codigo_neon': "", 'codigo_diamante': "",
    'premium_ativo': False, 'cor_card': "Cinza Escuro", 'cor_fundo': "Preto", 
    'luminosidade': 100, 'lingua': "Português", 'inicio_premium': None
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# 3. LÓGICA DE ACESSO (SEPARADA DE CORES)
is_mega = st.session_state.codigo_perm == "67lucas62"
is_premium_normal = st.session_state.codigo == "6626"
tem_beneficios_premium = is_mega or is_premium_normal  # Apenas estes dão abas extras e limite 80

# Lógica de Cores (Independente)
is_neon = st.session_state.codigo_neon == "6676neon7secret"
is_diamante = st.session_state.codigo_diamante == "77daimond8secret"

# Temporizador Premium 24h
if is_premium_normal and st.session_state.inicio_premium is None:
    st.session_state.inicio_premium = datetime.now()
elif not is_premium_normal:
    st.session_state.inicio_premium = None

# 4. ESTILOS VISUAIS DINÂMICOS
mapa_cores = {"Preto": "#0b1117", "Cinza Escuro": "#1a1c23", "Azul Noite": "#001f3f", "Verde Floresta": "#002b1b", "Branco": "#ffffff"}
app_bg = mapa_cores.get(st.session_state.cor_fundo, "#0b1117")
card_bg = mapa_cores.get(st.session_state.cor_card, "#1a1c23")

# Prioridade de cor: Mega > Neon > Diamante > Premium > Padrão
cor_borda = "#2ecc71"
shadow = "none"
if is_mega: 
    cor_borda = "linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet)"
elif is_neon: 
    cor_borda = "#00ff00"; shadow = "0 0 15px #00ff00, 0 0 30px #ff00ff"
elif is_diamante: 
    cor_borda = "#00d4ff"; shadow = "0 0 20px #00d4ff"
elif is_premium_normal: 
    cor_borda = "#ffd700"

limite_zoo = 80 if tem_beneficios_premium else 20

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; filter: brightness({st.session_state.luminosidade}%); color: white; }}
    .cartao-cidadao {{
        background: {card_bg}; border-radius: 15px; padding: 20px; text-align: center; border: 4px solid; 
        border-image: {cor_borda if "gradient" in cor_borda else "none"} 1;
        border-color: {cor_borda if "gradient" not in cor_borda else "transparent"};
        box-shadow: {shadow}; min-height: 550px; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 25px;
    }}
    .img-container img {{ width: 100%; max-height: 180px; object-fit: cover; border-radius: 10px; }}
    .nome-comum {{ font-size: 1.5em; font-weight: bold; text-transform: uppercase; margin-top: 10px; }}
    .nome-cientifico {{ font-size: 1.1em; font-style: italic; color: #1DB954; margin-bottom: 10px; display: block; }}
    .info-bio {{ background: rgba(255,255,255,0.05); padding: 12px; border-radius: 10px; font-size: 1.05em; text-align: left; }}
    .status-vip-label {{ background: gold; color: black; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 10px; }}
    .timer-premium {{ background: #ff4b4b; color: white; padding: 5px; border-radius: 5px; font-family: monospace; font-size: 1.2em; text-align: center; margin-bottom: 15px; }}
    
    [data-testid="stSidebar"] {{
        border-right: 5px solid;
        border-image: {cor_borda if "gradient" in cor_borda else "none"} 1;
        border-color: {cor_borda if "gradient" not in cor_borda else "transparent"};
    }}
</style>
""", unsafe_allow_html=True)

# 5. RENDERIZAÇÃO E BUSCA
def buscar(q):
    try: return requests.get(f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=12&locale=pt-PT").json().get('results', [])
    except: return []

def render_cartao(an, key_prefix, mostrar_stats=False):
    nome = an.get('preferred_common_name', an.get('name', 'Espécie Identificada'))
    cientifico = an.get('name', 'N/A')
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    
    st.markdown(f"""
    <div class="cartao-cidadao">
        <div class="img-container"><img src="{foto}"></div>
        <div><span class="nome-comum">{nome.title()}</span><br><span class="nome-cientifico">({cientifico})</span></div>
        <div class="info-bio"><b>🧬 CLASSE:</b> {an.get('iconic_taxon_name', 'Bio').upper()}<br><b>🏠 HABITAT:</b> NATURAL</div>
    """, unsafe_allow_html=True)
    if mostrar_stats and st.session_state.premium_ativo:
        st.markdown(f"""<div style="color:gold; font-weight:bold; border-top:1px solid gold; margin-top:10px; padding-top:10px; text-align:left;">🚀 VELOCIDADE: {random.randint(5,130)} KM/H<br>⏳ VIDA: {random.randint(1,100)} ANOS</div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("📥 CAPTURAR", key=f"btn_{key_prefix}_{an['id']}", use_container_width=True):
        if len(st.session_state.zoo) < limite_zoo:
            st.session_state.zoo.append(an); st.toast(f"{nome} guardado!")
        else:
            st.error(f"Limite do Zoo atingido ({limite_zoo})!")

# 6. SIDEBAR
with st.sidebar:
    # Só mostra o título se tiver benefícios de abas/limites ativos
    if st.session_state.premium_ativo and tem_beneficios_premium:
        st.markdown('<div class="status-vip-label">🏆 ZOÓLOGO PROFISSIONAL</div>', unsafe_allow_html=True)
        if is_premium_normal and st.session_state.inicio_premium:
            restante = timedelta(hours=24) - (datetime.now() - st.session_state.inicio_premium)
            if restante.total_seconds() > 0:
                h, r = divmod(int(restante.total_seconds()), 3600)
                m, s = divmod(r, 60)
                st.markdown(f'<div class="timer-premium">⏳ {h:02d}:{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
            else: st.session_state.codigo = ""
    
    st.title("🌍 MundoVivo")
    # Toggle só aparece se tiver algum código de benefícios (Mega ou 24h)
    if tem_beneficios_premium:
        st.session_state.premium_ativo = st.toggle("🔄 MODO VIP", value=st.session_state.premium_ativo)
    
    nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    if st.session_state.premium_ativo and tem_beneficios_premium:
        nav = ["🔬 Laboratório", "🧬 Fusão", "🚁 Missões", "📊 Estatísticas", "❄️ Criogenia", "⚙️ Definições"]
    
    aba = st.radio("Menu", nav)
    st.write(f"📊 Zoo: {len(st.session_state.zoo)} / {limite_zoo}")

# 7. LOGICA DE ABAS (Simplificada para o exemplo)
if aba == "🌍 Países":
    p = st.selectbox("País:", ["Brasil", "Portugal", "México", "Rússia"])
    cols = st.columns(3)
    for i, an in enumerate(buscar(p)):
        with cols[i%3]: render_cartao(an, "p")

elif aba == "🔬 Laboratório":
    q = st.text_input("Pesquisar:")
    if q:
        cols = st.columns(3)
        for i, an in enumerate(buscar(q)):
            with cols[i%3]: render_cartao(an, "lab", True)
    st.divider()
    if st.session_state.zoo:
        st.subheader("🦁 O Teu Zoo")
        cols_z = st.columns(3)
        for i, an in enumerate(st.session_state.zoo):
            with cols_z[i%3]: render_cartao(an, f"z{i}", True)

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    
    with st.expander("🎨 VISUAL E IDIOMA", expanded=False):
        st.session_state.cor_fundo = st.selectbox("Cor de Fundo", list(mapa_cores.keys()))
        st.session_state.cor_card = st.selectbox("Cor dos Cartões", list(mapa_cores.keys()))
        st.session_state.luminosidade = st.slider("Brilho", 50, 150, 100)

    # RETÂNGULO 1: SÓ MEGA
    st.markdown("### 👑 RETÂNGULO MEGA")
    with st.container():
        st.session_state.codigo_perm = st.text_input("Código Mega", value=st.session_state.codigo_perm, type="password")
    
    # RETÂNGULO 2: CORES E PREMIUM 24H
    st.markdown("### ✨ CORES & PREMIUM 24H")
    with st.container():
        st.session_state.codigo_neon = st.text_input("Código Neon", value=st.session_state.codigo_neon, type="password")
        st.session_state.codigo_diamante = st.text_input("Código Diamante", value=st.session_state.codigo_diamante, type="password")
        st.session_state.codigo = st.text_input("Código Premium 24h", value=st.session_state.codigo, type="password")
        st.session_state.codigo_crio = st.text_input("Código Criogenia", value=st.session_state.codigo_crio, type="password")

    if st.button("Guardar Alterações"): st.rerun()
