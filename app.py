import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo Ultra 🌍", layout="wide")

# 2. ESTADO DO SISTEMA
chaves = {
    'zoo': [], 'criogenia_storage': [],
    'codigo': "", 'codigo_perm': "", 'codigo_crio': "", 'codigo_neon': "", 'codigo_diamante': "",
    'premium_ativo': False, 'cor_fundo_user': "#0b1117", 'cor_card_user': "#1a1c23",
    'luminosidade': 100, 'inicio_premium': None
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# 3. LÓGICA DE ACESSO
is_mega = st.session_state.codigo_perm == "67lucas62"
is_premium_normal = st.session_state.codigo == "6626"
tem_beneficios = is_mega or is_premium_normal
is_neon = st.session_state.codigo_neon == "6676neon7secret"
is_diamante = st.session_state.codigo_diamante == "77daimond8secret"

if is_premium_normal and st.session_state.inicio_premium is None:
    st.session_state.inicio_premium = datetime.now()

# Estilos de Cores Especiais
cor_borda = "#2ecc71"
linha_vip_css = "border-top: 2px solid #ffd700;"
sombra = "none"

if is_mega:
    cor_borda = "linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet)"
    linha_vip_css = "height: 3px; background: linear-gradient(90deg, red, orange, yellow, green, blue, indigo, violet); border:none;"
elif is_neon:
    cor_borda = "#00ff00"; sombra = "0 0 20px #00ff00"
elif is_diamante:
    cor_borda = "#00d4ff"; sombra = "0 0 25px #00d4ff"
elif is_premium_normal:
    cor_borda = "#ffd700"

# 4. DESIGN CSS
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
    .nome-comum {{ font-size: 1.5em; font-weight: 900; text-transform: uppercase; text-align: center; display: block; margin: 10px 0; }}
    .label {{ color: #1DB954; font-weight: bold; font-size: 0.9em; }}
    .separador-vip {{ {linha_vip_css} margin: 15px 0; }}
    .stats-txt {{ color: #ffd700; font-weight: bold; font-family: monospace; font-size: 1.1em; }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÕES
def buscar_animais(termo):
    try:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={termo}&taxon_id=1&per_page=9&locale=pt-PT")
        return r.json().get('results', [])
    except: return []

def desenhar_cartao(an, prefixo):
    nome = (an.get('preferred_common_name') or an.get('name') or 'Espécie Identificada').title()
    cientifico = an.get('name', 'N/A')
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    
    random.seed(an['id'])
    habitat = random.choice(["Terrestre", "Aquático", "Aéreo"])
    dieta = random.choice(["Herbívoro", "Carnívoro", "Omnívoro"])
    repro = an.get('iconic_taxon_name', 'Orgânica').upper()

    st.markdown(f"""
    <div class="cartao-cidadao">
        <div style="color:gold; font-weight:bold; text-align:center; font-size:0.8em;">💳 CARTÃO DE CIDADÃO</div>
        <div class="img-box"><img src="{foto}"></div>
        <span class="nome-comum">{nome}</span>
        <div class="campo"><span class="label">🧬 ESPÉCIE:</span> {cientifico}</div>
        <div class="campo"><span class="label">🌍 AMBIENTE:</span> {habitat}</div>
        <div class="campo"><span class="label">🥩 ALIMENTAÇÃO:</span> {dieta}</div>
        <div class="campo"><span class="label">🍼 REPRODUÇÃO:</span> {repro}</div>
    """, unsafe_allow_html=True)

    if st.session_state.premium_ativo and tem_beneficios:
        st.markdown(f"""<div class="separador-vip"></div>
        <div class="stats-txt">📊 DADOS VIP<br>🚀 VELOCIDADE: {random.randint(20, 180)} KM/H<br>⚖️ PESO: {random.randint(1, 4000)} KG</div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button(f"📥 CAPTURAR", key=f"btn_{prefixo}_{an['id']}", use_container_width=True):
        limite = 80 if tem_beneficios else 20
        if len(st.session_state.zoo) < limite:
            st.session_state.zoo.append(an); st.toast(f"{nome} capturado!")
        else: st.error(f"Limite de {limite} atingido!")

# 6. SIDEBAR
with st.sidebar:
    if st.session_state.premium_ativo and tem_beneficios:
        st.markdown('<div style="background:gold; color:black; padding:10px; border-radius:10px; text-align:center; font-weight:bold;">🏆 ZOÓLOGO PROFISSIONAL</div>', unsafe_allow_html=True)
        if is_premium_normal and st.session_state.inicio_premium:
            restante = timedelta(hours=24) - (datetime.now() - st.session_state.inicio_premium)
            if restante.total_seconds() > 0:
                h, r = divmod(int(restante.total_seconds()), 3600)
                m, s = divmod(r, 60)
                st.markdown(f'<div style="background:red; color:white; text-align:center; padding:5px; border-radius:5px; margin-top:5px;">⏳ {h:02d}:{m:02d}:{s:02d}</div>', unsafe_allow_html=True)

    st.title("🌍 MundoVivo")
    if tem_beneficios: st.session_state.premium_ativo = st.toggle("Mundo VIP", value=st.session_state.premium_ativo)
    
    nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    if st.session_state.premium_ativo and tem_beneficios:
        nav = ["🔬 Laboratório", "🧬 Fusão", "🚁 Missões", "📊 Estatísticas", "❄️ Criogenia", "⚙️ Definições"]
    aba = st.radio("Explorar", nav)
    st.write(f"📊 Zoo: {len(st.session_state.zoo)} / {80 if tem_beneficios else 20}")

# 7. CONTEÚDO
if aba == "🌍 Países":
    p = st.selectbox("Escolha um País:", ["Brasil", "Portugal", "Austrália", "Madagáscar"])
    cols = st.columns(3)
    for i, an in enumerate(buscar_animais(p)):
        with cols[i%3]: desenhar_cartao(an, "p")

elif aba == "🌲 Florestas":
    st.write("### Ecossistemas Terrestres")
    

[Image of the layers of a tropical rainforest]

    f = st.selectbox("Floresta:", ["Amazónia", "Selva do Congo", "Taiga"])
    cols = st.columns(3)
    for i, an in enumerate(buscar_animais(f)):
        with cols[i%3]: desenhar_cartao(an, "f")

elif aba == "🌊 Oceanos":
    st.write("### Ecossistemas Marinhos")
    
    o = st.selectbox("Oceano:", ["Pacífico", "Atlântico", "Mar Mediterrâneo"])
    cols = st.columns(3)
    for i, an in enumerate(buscar_animais(o)):
        with cols[i%3]: desenhar_cartao(an, "o")

elif aba == "🔬 Laboratório":
    q = st.text_input("Procurar Genética:")
    if q:
        cols = st.columns(3)
        for i, an in enumerate(buscar_animais(q)):
            with cols[i%3]: desenhar_cartao(an, "lab")
    st.divider()
    if st.session_state.zoo:
        st.subheader("🦁 O Teu Zoo")
        cols_z = st.columns(3)
        for i, an in enumerate(st.session_state.zoo):
            with cols_z[i%3]: desenhar_cartao(an, f"zoo_{i}")

elif aba == "❄️ Criogenia":
    if st.session_state.codigo_crio == "crio969":
        st.title("❄️ Unidade Criogénica")
        animais = {a.get('preferred_common_name', a.get('name')): a for a in st.session_state.zoo}
        if animais:
            escolha = st.selectbox("Congelar:", list(animais.keys()))
            if st.button("CONGELAR"):
                st.session_state.zoo.remove(animais[escolha])
                st.success(f"{escolha} congelado!")
                time.sleep(1); st.rerun()
    else: st.error("Código inválido.")

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    with st.expander("🎨 VISUAL"):
        st.session_state.cor_fundo_user = st.color_picker("Fundo App", st.session_state.cor_fundo_user)
        st.session_state.cor_card_user = st.color_picker("Fundo Card", st.session_state.cor_card_user)
        st.session_state.luminosidade = st.slider("Brilho", 50, 150, 100)

    st.markdown("### 👑 RETÂNGULO MEGA")
    with st.container():
        st.session_state.codigo_perm = st.text_input("Mega Código", value=st.session_state.codigo_perm, type="password")

    st.markdown("### ✨ CORES & PREMIUM 24H")
    with st.container():
        st.session_state.codigo_neon = st.text_input("Neon", value=st.session_state.codigo_neon, type="password")
        st.session_state.codigo_diamante = st.text_input("Diamante", value=st.session_state.codigo_diamante, type="password")
        st.session_state.codigo = st.text_input("Premium 24h", value=st.session_state.codigo, type="password")
        st.session_state.codigo_crio = st.text_input("Crio", value=st.session_state.codigo_crio, type="password")
    
    if st.button("Guardar"): st.rerun()
