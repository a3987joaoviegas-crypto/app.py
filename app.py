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
    'luminosidade': 100, 'pontos': 250
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# 3. LÓGICA DE ESTILOS SECRETO
is_mega = st.session_state.codigo_perm == "67lucas62"
is_neon = st.session_state.codigo_neon == "6676neon7secret"
is_diamante = st.session_state.codigo_diamante == "77daimond8secret"
is_crio_auth = st.session_state.codigo_crio == "crio969"
tem_acesso = is_mega or is_neon or is_diamante or st.session_state.codigo == "6626"

# Definição de Cores Dinâmicas para Neon e Diamante
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
elif st.session_state.codigo == "6626": 
    cor_borda = "#ffd700"

# 4. DESIGN CSS (IMAGEM CONTROLADA E TEXTO AJUSTADO)
st.markdown(f"""
<style>
    .stApp {{ background-color: #0b1117; filter: brightness({st.session_state.luminosidade}%); color: white; }}
    
    .cartao-cidadao {{
        background: #1a1c23; border-radius: 15px; padding: 20px; 
        text-align: center; border: 4px solid; 
        border-image: {cor_borda if "gradient" in cor_borda else "none"} 1;
        border-color: {cor_borda if "gradient" not in cor_borda else "transparent"};
        box-shadow: {shadow}; min-height: 580px;
        display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 25px;
    }}
    
    /* TAMANHO DA IMAGEM CONTROLADO */
    .img-container img {{
        width: 100%;
        max-height: 180px; /* Impede que a imagem fique enorme */
        object-fit: cover;
        border-radius: 10px;
    }}

    .nome-comum {{ font-size: 1.5em; font-weight: bold; color: white; text-transform: uppercase; margin-top: 10px; }}
    .nome-cientifico {{ font-size: 1.1em; font-style: italic; color: #1DB954; margin-bottom: 10px; display: block; }}
    .info-bio {{ background: rgba(255,255,255,0.05); padding: 12px; border-radius: 10px; font-size: 1.05em; text-align: left; }}
    .stats-vip {{ font-size: 1.1em; color: #ffd700; border-top: 2px solid #ffd700; margin-top: 10px; padding-top: 10px; text-align: left; font-weight: bold; }}
    
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
        an['vel'] = random.randint(5, 120)
        an['vida'] = random.randint(2, 90)
        an['peso'] = random.randint(1, 4000)

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
        st.session_state.zoo.append(an); st.toast(f"{nome_comum} guardado!")

# 6. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    if tem_acesso:
        st.session_state.premium_ativo = st.toggle("🔄 MODO VIP", value=st.session_state.premium_ativo)
    
    nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    if st.session_state.premium_ativo:
        nav = ["🔬 Laboratório", "🧬 Fusão", "🚁 Missões", "📊 Estatísticas", "❄️ Criogenia", "⚙️ Definições"]
    aba = st.radio("Menu", nav)

# 7. LOGICA DAS ABAS (Conteúdo completo)
if aba == "🌍 Países":
    p = st.selectbox("País:", ["Brasil", "Portugal", "México", "Finlândia", "Rússia", "Maldivas", "Madagáscar"])
    cols = st.columns(3)
    for i, an in enumerate(buscar(p)):
        with cols[i%3]: render_cartao(an, "p")

elif aba == "🌲 Florestas":
    f = st.selectbox("Floresta:", ["Amazónia", "Selva do Congo", "Taiga", "Mata Atlântica", "Borealis", "Floresta Negra"])
    cols = st.columns(3)
    for i, an in enumerate(buscar(f)):
        with cols[i%3]: render_cartao(an, "f")

elif aba == "🌊 Oceanos":
    o = st.selectbox("Oceano:", ["Atlântico", "Pacífico", "Índico", "Antártico", "Mar Mediterrâneo", "Mar das Caraíbas"])
    cols = st.columns(3)
    for i, an in enumerate(buscar(o)):
        with cols[i%3]: render_cartao(an, "o")

elif aba == "🔬 Laboratório":
    q = st.text_input("Pesquisar Espécie:")
    if q:
        cols = st.columns(3)
        for i, an in enumerate(buscar(q)):
            with cols[i%3]: render_cartao(an, "lab", True)
    if st.session_state.zoo:
        st.divider()
        st.subheader("🦁 O Teu Zoo")
        cols_zoo = st.columns(3)
        for i, an in enumerate(st.session_state.zoo):
            with cols_zoo[i%3]: render_cartao(an, "zoo", True)

elif aba == "❄️ Criogenia":
    st.title("❄️ Unidade Criogénica")
    if not is_crio_auth: st.error("Acesso bloqueado. Insira o código da Crio.")
    else:
        if not st.session_state.zoo: st.warning("O Zoo está vazio.")
        else:
            opcoes = {f"{a.get('preferred_common_name', 'Animal')} ({a.get('id')})": a for a in st.session_state.zoo}
            escolha_nome = st.selectbox("Escolha para congelar:", list(opcoes.keys()))
            if st.button("❄️ CONGELAR AGORA"):
                animal = opcoes[escolha_nome]
                st.session_state.criogenia_storage.append(animal)
                st.session_state.zoo.remove(animal)
                st.success(f"{escolha_nome} congelado!")
                time.sleep(1); st.rerun()

elif aba == "📊 Estatísticas":
    st.title("📊 Painel VIP")
    if st.session_state.zoo:
        st.table([{"Animal": a.get('preferred_common_name'), "Vel": a.get('vel'), "Vida": a.get('vida')} for a in st.session_state.zoo])

elif aba == "🚁 Missões":
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/80/World_map_-_low_resolution.svg")
    if st.button("🚀 INICIAR RESGATE"):
        st.markdown('<audio autoplay><source src="https://www.soundjay.com/transportation/helicopter-fly-over-1.mp3"></audio>', unsafe_allow_html=True)
        st.success("Helicóptero a caminho!"); time.sleep(2); st.rerun()

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    with st.expander("🛡️ PREMIUMS", expanded=True):
        st.session_state.codigo = st.text_input("Premium (6626)", value=st.session_state.codigo, type="password")
        st.session_state.codigo_perm = st.text_input("Mega (67lucas62)", value=st.session_state.codigo_perm, type="password")
        st.session_state.codigo_crio = st.text_input("Criogenia (crio969)", value=st.session_state.codigo_crio, type="password")
        st.session_state.codigo_neon = st.text_input("Neon Secret (6676neon7secret)", value=st.session_state.codigo_neon, type="password")
        st.session_state.codigo_diamante = st.text_input("Diamante Secret (77daimond8secret)", value=st.session_state.codigo_diamante, type="password")
    
    st.session_state.luminosidade = st.slider("Brilho", 50, 150, 100)
    if st.button("Guardar Alterações"): st.rerun()
