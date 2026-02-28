import streamlit as st
import requests
import random
from datetime import datetime, timedelta

# 1. ESTADO DO SISTEMA
chaves = {
    'zoo': [], 'favoritos': [], 'crio_storage': [], 'tanque_fusao': [], 'nomes_zoo': {},
    'c_24h': "", 'c_mega': "", 'premium_ativo': False,
    'cor_tema': "#0b1117", 'negrito': False, 'brilho': 100
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# 2. LÓGICA DE ACESSO
is_mega = st.session_state.c_mega == "67lucas62"
is_24h_ativo = st.session_state.c_24h == "6626"
tem_acesso_vip = is_mega or is_24h_ativo

# 3. SIDEBAR (FILTRADA POR PREMIUM)
with st.sidebar:
    st.title("🌍 MundoVivo")
    if tem_acesso_vip:
        st.session_state.premium_ativo = st.toggle("✨ MODO PREMIUM", value=st.session_state.premium_ativo)
    
    if st.session_state.premium_ativo:
        menu = ["🧬 Tanque de Fusão", "🌀 Salvamento", "❄️ Criogenia", "🔬 Laboratório", "🐾 Meu Zoo", "⭐ Favoritos", "⚙️ Definições"]
    else:
        menu = ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países", "🔬 Laboratório", "🐾 Meu Zoo", "⭐ Favoritos", "⚙️ Definições"]
    
    aba = st.radio("Navegação", menu)

# 4. DESIGN CSS
cor_borda = "#2ecc71"
if is_mega: cor_borda = "linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet)"
elif is_24h_ativo: cor_borda = "#ffd700"

st.markdown(f"""
<style>
    .stApp {{ background-color: {st.session_state.cor_tema}; color: white; filter: brightness({st.session_state.brilho/100}); font-weight: {'bold' if st.session_state.negrito else 'normal'}; }}
    .cartao-cidadao {{
        background: #1a1c23; border-radius: 25px; padding: 15px; border: 4px solid;
        border-color: {cor_borda if "gradient" not in cor_borda else "transparent"};
        border-image: {cor_borda if "gradient" in cor_borda else "none"} 1;
        margin-bottom: 25px; min-height: 580px;
    }}
    .img-vertical {{ width: 100%; border-radius: 20px; height: 280px; object-fit: cover; }}
    .linha-sep {{ border-top: 2px solid #444; margin: 10px 0; }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÃO DO CARTÃO COMPLETO
def card(an, prefixo, idx=0):
    if not an: return
    id_an = an.get('id', random.randint(100,999))
    nome = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/250x400")
    ukey = f"{prefixo}_{id_an}_{idx}"
    
    # Dados biológicos estáveis
    classe = random.choice(["Mamífero", "Ave", "Peixe", "Réptil", "Anfíbio"])
    repro = "Ovíparo" if classe in ["Ave", "Peixe", "Réptil"] else "Vivíparo"
    alim = random.choice(["Herbívoro", "Carnívoro", "Omnívoro"])
    amb = "Aquático" if "Oceano" in aba or "Mar" in aba else "Terrestre"

    html = f"""
    <div class="cartao-cidadao">
        <span style="color:#ffd700; font-weight:bold; font-size:0.65em; display:block; text-align:center;">💳 CARTÃO DE CIDADÃO</span>
        <img src="{foto}" class="img-vertical">
        <div style="text-align:center; font-weight:bold; margin-top:15px; font-size:1.3em; color:#ffd700;">{st.session_state.nomes_zoo.get(ukey, nome)}</div>
        <div class="linha-sep"></div>
        <div style="font-size:0.9em;">🐾 <b>Classe:</b> {classe}</div>
        <div style="font-size:0.9em;">🥚 <b>Reprodução:</b> {repro}</div>
        <div style="font-size:0.9em;">🥩 <b>Alimentação:</b> {alim}</div>
        <div style="font-size:0.9em;">🌲 <b>Ambiente:</b> {amb}</div>
    """
    if st.session_state.premium_ativo:
        html += f"""<div class="linha-sep"></div>
        <div style="color:#bdc3c7; font-size:0.85em;">
            ⚡ <b>Velocidade:</b> {random.randint(10,180)} km/h<br>
            ⚖️ <b>Peso:</b> {random.randint(1,2000)} kg<br>
            ⏳ <b>Expectativa Vida:</b> {random.randint(5,120)} anos
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📥 Zoo", key=f"cap_{ukey}"): st.session_state.zoo.append(an); st.toast("No Zoo!")
    with c2:
        if st.button("⭐ Fav", key=f"fav_{ukey}"): st.session_state.favoritos.append(an); st.toast("Favorito!")
    
    if st.session_state.premium_ativo and prefixo == "zoo":
        if st.button("🧬 Fusão", key=f"fus_{ukey}", use_container_width=True):
            st.session_state.tanque_fusao.append(an); st.session_state.zoo.pop(idx); st.rerun()

# 6. LÓGICA DE API
def carregar_70(termo):
    try:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={termo}&taxon_id=1&per_page=70&locale=pt-PT")
        animais = r.json().get('results', [])
        for i in range(0, len(animais), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(animais):
                    with cols[j]: card(animais[i+j], "explorar", i+j)
    except: st.error("Erro ao carregar animais.")

# 7. ABAS
if aba == "🌲 Florestas":
    sel = st.selectbox("Escolha a Floresta:", ["Amazónia", "Congo", "Floresta Negra"])
    carregar_70(sel)
elif aba == "🌊 Oceanos":
    sel = st.selectbox("Escolha o Oceano:", ["Oceano Pacífico", "Oceano Índico", "Mar Mediterrâneo"])
    carregar_70(sel)
elif aba == "🏳️ Países":
    sel = st.selectbox("Escolha o País:", ["Portugal", "Brasil", "Austrália", "Japão", "Canadá"])
    carregar_70(sel)
elif aba == "🔬 Laboratório":
    st.header("🔬 Laboratório de Pesquisa")
    busca = st.text_input("🔍 Pesquisar animal para analisar:")
    if busca: carregar_70(busca)
elif aba == "🐾 Meu Zoo":
    for i in range(0, len(st.session_state.zoo), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(st.session_state.zoo):
                with cols[j]: card(st.session_state.zoo[i+j], "zoo", i+j)
elif aba == "⭐ Favoritos":
    st.header("⭐ Meus Favoritos")
    for i in range(0, len(st.session_state.favoritos), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(st.session_state.favoritos):
                with cols[j]: card(st.session_state.favoritos[i+j], "fav", i+j)
elif aba == "🧬 Tanque de Fusão":
    st.header("🧬 Tanque de Fusão")
    st.write(f"Espécimes no tanque: {len(st.session_state.tanque_fusao)}")
    if st.button("💥 FUNDIR TUDO"): st.balloons(); st.success("Híbrido criado!")
elif aba == "⚙️ Definições":
    st.session_state.c_mega = st.text_input("Código Mega", type="password", value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input("Código 24h", type="password", value=st.session_state.c_24h)
    st.session_state.brilho = st.slider("Luminosidade", 50, 150, st.session_state.brilho)
    if st.button("Guardar"): st.rerun()
