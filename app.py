import streamlit as st
import requests
import random
import time

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo Ultra 🌍", layout="wide")

# 2. ESTADO DO SISTEMA
chaves = {
    'zoo': [], 'tanque_fusao': [], 'criogenia_storage': [],
    'codigo': "", 'codigo_perm': "", 'codigo_crio': "", 'codigo_neon': "", 'codigo_diamante': "",
    'premium_ativo': False, 'cor_card': "Preto", 'cor_fundo': "Preto", 
    'luminosidade': 100, 'pontos': 250, 'lingua': "Português"
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# 3. LÓGICA DE ACESSO E ESTILOS
is_mega = st.session_state.codigo_perm == "67lucas62"
is_neon = st.session_state.codigo_neon == "6676neon7secret"
is_diamante = st.session_state.codigo_diamante == "77daimond8secret"
is_crio_auth = st.session_state.codigo_crio == "crio969"
is_premium_normal = st.session_state.codigo == "6626"
tem_acesso = is_mega or is_premium_normal or is_neon or is_diamante

# Mapeamento de Cores e Fundos
mapa_cores = {
    "Preto": "#0b1117", "Cinza Escuro": "#1a1c23", "Azul Noite": "#001f3f", 
    "Verde Floresta": "#002b1b", "Branco": "#ffffff", "Ciano": "#008b8b"
}
app_bg = mapa_cores.get(st.session_state.cor_fundo, "#0b1117")
card_bg = mapa_cores.get(st.session_state.cor_card, "#1a1c23")

# Definição de Cores Dinâmicas para Bordas
cor_borda = "#2ecc71"
shadow = "none"
if is_mega: 
    cor_borda = "linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet)"
elif is_neon: 
    cor_borda = "#00ff00"
    shadow = "0 0 15px #00ff00, 0 0 30px #ff00ff"
elif is_diamante: 
    cor_borda = "#00d4ff"
    shadow = "0 0 20px #00d4ff"
elif is_premium_normal: 
    cor_borda = "#ffd700"

limite_zoo = 80 if tem_acesso else 20

# 4. DESIGN CSS
st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; filter: brightness({st.session_state.luminosidade}%); color: white; }}
    
    .cartao-cidadao {{
        background: {card_bg}; border-radius: 15px; padding: 20px; 
        text-align: center; border: 4px solid; 
        border-image: {cor_borda if "gradient" in cor_borda else "none"} 1;
        border-color: {cor_borda if "gradient" not in cor_borda else "transparent"};
        box-shadow: {shadow}; min-height: 580px;
        display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 25px;
    }}
    
    .img-container img {{ width: 100%; max-height: 180px; object-fit: cover; border-radius: 10px; }}
    .nome-comum {{ font-size: 1.5em; font-weight: bold; color: inherit; text-transform: uppercase; margin-top: 10px; }}
    .nome-cientifico {{ font-size: 1.1em; font-style: italic; color: #1DB954; margin-bottom: 10px; display: block; }}
    .info-bio {{ background: rgba(255,255,255,0.05); padding: 12px; border-radius: 10px; font-size: 1.05em; text-align: left; }}
    .stats-vip {{ font-size: 1.1em; color: #ffd700; border-top: 2px solid #ffd700; margin-top: 10px; padding-top: 10px; text-align: left; font-weight: bold; }}
    
    .status-vip-label {{ background: gold; color: black; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px; }}

    [data-testid="stSidebar"] {{
        border-right: 5px solid;
        border-image: {cor_borda if "gradient" in cor_borda else "none"} 1;
        border-color: {cor_borda if "gradient" not in cor_borda else "transparent"};
        box-shadow: {shadow};
    }}
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE BUSCA
def buscar(q):
    try: return requests.get(f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=9&locale=pt-PT").json().get('results', [])
    except: return []

def render_cartao(an, key_prefix, mostrar_stats=False):
    nome_comum = an.get('preferred_common_name', 'Desconhecido').title()
    nome_cientifico = an.get('name', 'N/A')
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    
    if 'vel' not in an:
        an['vel'] = random.randint(5, 120); an['vida'] = random.randint(2, 90); an['peso'] = random.randint(1, 4000)

    st.markdown(f"""
    <div class="cartao-cidadao">
        <div class="img-container"><img src="{foto}"></div>
        <div>
            <span class="nome-comum">{nome_comum}</span>
            <span class="nome-cientifico">({nome_cientifico})</span>
        </div>
        <div class="info-bio">
            <b>🧬 CLASSE:</b> {an.get('iconic_taxon_name', 'Bio').upper()}<br>
            <b>🏠 HABITAT:</b> NATURAL<br>
            <b>🍼 REPRODUÇÃO:</b> BIOLÓGICA
        </div>
    """, unsafe_allow_html=True)
    
    if mostrar_stats and st.session_state.premium_ativo:
        st.markdown(f"""<div class="stats-vip">🚀 VELOCIDADE: {an['vel']} KM/H<br>⏳ VIDA: {an['vida']} ANOS<br>⚖️ PESO: {an['peso']} KG</div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button(f"📥 CAPTURAR", key=f"btn_{key_prefix}_{an['id']}", use_container_width=True):
        if len(st.session_state.zoo) < limite_zoo:
            st.session_state.zoo.append(an); st.toast(f"{nome_comum} capturado!")
        else:
            st.error(f"Zoo cheio! ({limite_zoo} máx)")

# 6. SIDEBAR
with st.sidebar:
    if st.session_state.premium_ativo and tem_acesso:
        st.markdown('<div class="status-vip-label">🏆 ZOÓLOGO PROFISSIONAL</div>', unsafe_allow_html=True)
    st.title("🌍 MundoVivo")
    if tem_acesso:
        st.session_state.premium_ativo = st.toggle("🔄 MODO VIP", value=st.session_state.premium_ativo)
    
    nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    if st.session_state.premium_ativo:
        nav = ["🔬 Laboratório", "🧬 Fusão", "🚁 Missões", "📊 Estatísticas", "❄️ Criogenia", "⚙️ Definições"]
    aba = st.radio("Menu", nav)
    st.write(f"📊 Zoo: {len(st.session_state.zoo)} / {limite_zoo}")

# 7. LOGICA DAS ABAS
if aba == "🌍 Países":
    p = st.selectbox("País:", ["Brasil", "Portugal", "México", "Finlândia", "Rússia", "Maldivas", "Madagáscar"])
    cols = st.columns(3); res = buscar(p)
    for i, an in enumerate(res):
        with cols[i%3]: render_cartao(an, "p")

elif aba == "🔬 Laboratório":
    q = st.text_input("Pesquisar Espécie:")
    if q:
        cols = st.columns(3); res = buscar(q)
        for i, an in enumerate(res):
            with cols[i%3]: render_cartao(an, "lab", True)
    
    st.divider()
    st.subheader("🦁 O Teu Zoo")
    if st.session_state.zoo:
        cols_zoo = st.columns(3)
        for i, an in enumerate(st.session_state.zoo):
            with cols_zoo[i%3]: render_cartao(an, "zoo", True)

elif aba == "❄️ Criogenia":
    st.title("❄️ Unidade Criogénica")
    if not is_crio_auth: st.error("Acesso bloqueado.")
    else:
        opcoes = {f"{a.get('preferred_common_name', 'Animal')}": a for a in st.session_state.zoo}
        if opcoes:
            escolha = st.selectbox("Selecionar para Congelar:", list(opcoes.keys()))
            if st.button("❄️ CONGELAR"):
                st.session_state.criogenia_storage.append(opcoes[escolha])
                st.session_state.zoo.remove(opcoes[escolha]); st.rerun()

elif aba == "⚙️ Definições":
    st.header("⚙️ Configurações Gerais")
    
    # --- BLOCO 1: DEFINIÇÕES ORIGINAIS ---
    with st.expander("🎨 VISUAL E IDIOMA", expanded=True):
        st.session_state.lingua = st.selectbox("Língua", ["Português", "English", "Español"], index=0)
        st.session_state.cor_fundo = st.selectbox("Cor de Fundo", list(mapa_cores.keys()))
        st.session_state.cor_card = st.selectbox("Cor dos Cartões", list(mapa_cores.keys()), index=1)
        st.session_state.luminosidade = st.slider("Brilho (Luminosidade)", 50, 150, 100)
    
    # --- BLOCO 2: MEGA & ESPECIAIS ---
    with st.container():
        st.markdown("### 💎 MEGA & CORES ESPECIAIS")
        st.session_state.codigo_perm = st.text_input("Código Mega", value=st.session_state.codigo_perm, type="password")
        st.session_state.codigo_neon = st.text_input("Código Neon Secret", value=st.session_state.codigo_neon, type="password")
        st.session_state.codigo_diamante = st.text_input("Código Diamante Secret", value=st.session_state.codigo_diamante, type="password")
        st.markdown("---")

    # --- BLOCO 3: PREMIUM & CRIOGENIA ---
    with st.container():
        st.markdown("### ⏳ PREMIUM & CRIOGENIA")
        st.session_state.codigo = st.text_input("Código Premium 24h", value=st.session_state.codigo, type="password")
        st.session_state.codigo_crio = st.text_input("Código Crio", value=st.session_state.codigo_crio, type="password")

    if st.button("Guardar Configurações"): st.rerun()

# Outras abas (Fusão, Missões, etc) permanecem as mesmas.
