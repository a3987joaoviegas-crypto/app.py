import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo Ultra 🌍", layout="wide")

# 2. ESTADO DO SISTEMA (Cores fixas em Hexadecimal para evitar o erro de Traceback)
chaves = {
    'zoo': [], 'criogenia_storage': [],
    'codigo': "", 'codigo_perm': "", 'codigo_crio': "", 'codigo_neon': "", 'codigo_diamante': "",
    'premium_ativo': False, 'cor_fundo_user': "#0b1117", 'cor_card_user': "#1a1c23",
    'luminosidade': 100, 'inicio_premium': None
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# 3. LÓGICA DE ACESSO E CORES ESPECIAIS
is_mega = st.session_state.codigo_perm == "67lucas62"
is_premium_normal = st.session_state.codigo == "6626"
tem_beneficios = is_mega or is_premium_normal

is_neon = st.session_state.codigo_neon == "6676neon7secret"
is_diamante = st.session_state.codigo_diamante == "77daimond8secret"

# Definição visual das bordas e separadores
cor_borda = "#2ecc71"
linha_vip_css = "border-top: 2px solid #ffd700;"
sombra = "none"

if is_mega:
    cor_borda = "linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet)"
    linha_vip_css = "height: 3px; background: linear-gradient(90deg, red, orange, yellow, green, blue, indigo, violet); border:none;"
elif is_neon:
    cor_borda = "#00ff00"
    sombra = "0 0 20px #00ff00"
elif is_diamante:
    cor_borda = "#00d4ff"
    sombra = "0 0 25px #00d4ff"
elif is_premium_normal:
    cor_borda = "#ffd700"

# 4. CSS DO CARTÃO DE CIDADÃO
st.markdown(f"""
<style>
    .stApp {{ background-color: {st.session_state.cor_fundo_user}; filter: brightness({st.session_state.luminosidade}%); color: white; }}
    
    .cartao-cidadao {{
        background: {st.session_state.cor_card_user}; border-radius: 15px; padding: 20px; border: 4px solid;
        border-image: {cor_borda if "gradient" in cor_borda else "none"} 1;
        border-color: {cor_borda if "gradient" not in cor_borda else "transparent"};
        box-shadow: {sombra}; min-height: 620px; display: flex; flex-direction: column; margin-bottom: 25px;
    }}
    
    .img-box img {{ width: 100%; max-height: 180px; object-fit: cover; border-radius: 10px; }}
    .header-card {{ color: gold; font-size: 0.9em; font-weight: bold; text-align: center; margin-bottom: 10px; opacity: 0.8; }}
    .nome-comum {{ font-size: 1.5em; font-weight: 900; text-transform: uppercase; text-align: center; display: block; margin: 10px 0; color: white; }}
    .campo {{ font-size: 1em; margin: 3px 0; }}
    .label {{ color: #1DB954; font-weight: bold; font-size: 0.9em; }}
    .separador-vip {{ {linha_vip_css} margin: 15px 0; }}
    .stats-txt {{ color: #ffd700; font-weight: bold; font-family: monospace; font-size: 1.1em; }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÕES DE BUSCA E RENDERIZAÇÃO
def buscar_animais(termo):
    try:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={termo}&taxon_id=1&per_page=9&locale=pt-PT")
        return r.json().get('results', [])
    except: return []

def desenhar_cartao(an, prefixo):
    nome = an.get('preferred_common_name', an.get('name', 'Espécie Desconhecida')).title()
    cientifico = an.get('name', 'N/A')
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    classe = an.get('iconic_taxon_name', 'Orgânica').upper()
    
    # Dados aleatórios fixos pelo ID
    random.seed(an['id'])
    habitat = random.choice(["Terrestre", "Aquático", "Aéreo", "Subterrâneo"])
    dieta = random.choice(["Herbívoro", "Carnívoro", "Insetívoro", "Omnívoro"])

    st.markdown(f"""
    <div class="cartao-cidadao">
        <div class="header-card">ID-VIVO: {an['id']} | EMISSÃO: 2026</div>
        <div class="img-box"><img src="{foto}"></div>
        <span class="nome-comum">{nome}</span>
        <div class="campo"><span class="label">🧬 ESPÉCIE:</span> {cientifico}</div>
        <div class="campo"><span class="label">🌍 AMBIENTE:</span> {habitat}</div>
        <div class="campo"><span class="label">🥩 ALIMENTAÇÃO:</span> {dieta}</div>
        <div class="campo"><span class="label">🍼 REPRODUÇÃO:</span> {classe}</div>
    """, unsafe_allow_html=True)

    if st.session_state.premium_ativo and tem_beneficios:
        st.markdown(f"""
        <div class="separador-vip"></div>
        <div class="stats-txt">
            📊 DADOS PREMIUM<br>
            🚀 VELOCIDADE: {random.randint(20, 180)} KM/H<br>
            ⚖️ PESO: {random.randint(1, 4000)} KG
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button(f"📥 CAPTURAR", key=f"btn_{prefixo}_{an['id']}", use_container_width=True):
        limite = 80 if tem_beneficios else 20
        if len(st.session_state.zoo) < limite:
            st.session_state.zoo.append(an)
            st.toast(f"{nome} adicionado ao Zoo!")
        else: st.error(f"Zoo lotado! Máximo: {limite}")

# 6. SIDEBAR COM TEMPORIZADOR
with st.sidebar:
    if st.session_state.premium_ativo and tem_beneficios:
        st.markdown('<div style="background:gold; color:black; padding:10px; border-radius:10px; text-align:center; font-weight:bold;">🏆 ZOÓLOGO PROFISSIONAL</div>', unsafe_allow_html=True)
        if is_premium_normal:
            if st.session_state.inicio_premium is None: st.session_state.inicio_premium = datetime.now()
            restante = timedelta(hours=24) - (datetime.now() - st.session_state.inicio_premium)
            if restante.total_seconds() > 0:
                h, r = divmod(int(restante.total_seconds()), 3600)
                m, s = divmod(r, 60)
                st.markdown(f'<div style="background:red; color:white; text-align:center; padding:5px; border-radius:5px; margin-top:5px;">⌛ EXPIRA EM: {h:02d}:{m:02d}:{s:02d}</div>', unsafe_allow_html=True)

    st.title("🌍 MundoVivo")
    if tem_beneficios:
        st.session_state.premium_ativo = st.toggle("🔄 ATIVAR MODO VIP", value=st.session_state.premium_ativo)
    
    opcoes_nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    if st.session_state.premium_ativo and tem_beneficios:
        opcoes_nav = ["🔬 Laboratório", "🧬 Fusão", "🚁 Missões", "📊 Estatísticas", "❄️ Criogenia", "⚙️ Definições"]
    
    aba = st.radio("Explorar", opcoes_nav)
    st.write(f"📊 Zoo: {len(st.session_state.zoo)} / {80 if tem_beneficios else 20}")

# 7. LOGICA DAS ABAS
if aba == "🌍 Países":
    escolha = st.selectbox("País:", ["Brasil", "Portugal", "Madagáscar", "Austrália", "Japão"])
    cols = st.columns(3)
    for i, an in enumerate(buscar_animais(escolha)):
        with cols[i%3]: desenhar_cartao(an, "p")

elif aba == "🌲 Florestas":
    

[Image of the layers of a tropical rainforest]

    escolha = st.selectbox("Ecossistema:", ["Amazónia", "Selva do Congo", "Mata Atlântica", "Taiga Siberiana"])
    cols = st.columns(3)
    for i, an in enumerate(buscar_animais(escolha)):
        with cols[i%3]: desenhar_cartao(an, "f")

elif aba == "🌊 Oceanos":
    
    escolha = st.selectbox("Zona Marinha:", ["Oceano Pacífico", "Oceano Atlântico", "Mar Mediterrâneo", "Grande Barreira de Coral"])
    cols = st.columns(3)
    for i, an in enumerate(buscar_animais(escolha)):
        with cols[i%3]: desenhar_cartao(an, "o")

elif aba == "🔬 Laboratório":
    q = st.text_input("Pesquisa Genética:")
    if q:
        cols = st.columns(3)
        for i, an in enumerate(buscar_animais(q)):
            with cols[i%3]: desenhar_cartao(an, "lab")
    st.divider()
    st.subheader("🦁 O Teu Zoo (Grátis & VIP)")
    if st.session_state.zoo:
        cols_z = st.columns(3)
        for i, an in enumerate(st.session_state.zoo):
            with cols_z[i%3]: desenhar_cartao(an, f"zoo_{i}")

elif aba == "❄️ Criogenia":
    if st.session_state.codigo_crio != "crio969": st.error("Acesso negado à Criogenia.")
    else:
        st.title("❄️ Unidade Criogénica")
        nomes_zoo = {a.get('preferred_common_name', a.get('name')): a for a in st.session_state.zoo}
        if nomes_zoo:
            alvo = st.selectbox("Animal para congelar:", list(nomes_zoo.keys()))
            if st.button("❄️ EXECUTAR CONGELAMENTO"):
                st.session_state.zoo.remove(nomes_zoo[alvo])
                st.success(f"{alvo} foi criopreservado.")
                time.sleep(1); st.rerun()

elif aba == "⚙️ Definições":
    st.header("⚙️ Painel de Controlo")
    
    with st.expander("🎨 PERSONALIZAÇÃO VISUAL"):
        st.session_state.cor_fundo_user = st.color_picker("Fundo do App", st.session_state.cor_fundo_user)
        st.session_state.cor_card_user = st.color_picker("Fundo dos Cartões", st.session_state.cor_card_user)
        st.session_state.luminosidade = st.slider("Brilho Global", 50, 150, 100)

    # RETÂNGULO 1: MEGA PREMIUM
    st.markdown("### 👑 RETÂNGULO MEGA")
    with st.container():
        st.session_state.codigo_perm = st.text_input("Acesso Mega (67lucas62)", value=st.session_state.codigo_perm, type="password")
        st.write("---")

    # RETÂNGULO 2: CORES E PREMIUM TEMPORÁRIO
    st.markdown("### ✨ CORES & ACESSOS ESPECIAIS")
    with st.container():
        st.session_state.codigo_neon = st.text_input("Código Neon", value=st.session_state.codigo_neon, type="password")
        st.session_state.codigo_diamante = st.text_input("Código Diamante", value=st.session_state.codigo_diamante, type="password")
        st.session_state.codigo = st.text_input("Código Premium 24h (6626)", value=st.session_state.codigo, type="password")
        st.session_state.codigo_crio = st.text_input("Código Criogenia (crio969)", value=st.session_state.codigo_crio, type="password")

    if st.button("Aplicar Alterações"): st.rerun()
