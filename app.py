import streamlit as st
import requests
import random
from datetime import datetime, timedelta

# 1. ESTADO DO SISTEMA
if 'zoo' not in st.session_state: st.session_state.zoo = []
if 'nomes_zoo' not in st.session_state: st.session_state.nomes_zoo = {}
if 'c_24h' not in st.session_state: st.session_state.c_24h = ""
if 'c_mega' not in st.session_state: st.session_state.c_mega = ""
if 'premium_ativo' not in st.session_state: st.session_state.premium_ativo = False
if 'ini_premium' not in st.session_state: st.session_state.ini_premium = None
if 'exp_trava' not in st.session_state: st.session_state.exp_trava = None
if 'cor_tema' not in st.session_state: st.session_state.cor_tema = "#0b1117"
if 'negrito' not in st.session_state: st.session_state.negrito = False
if 'lingua' not in st.session_state: st.session_state.lingua = "Português"
if 'brilho' not in st.session_state: st.session_state.brilho = 100

# 2. LÓGICA DE ACESSO
is_mega = st.session_state.c_mega == "67lucas62"
is_24h_ativo = st.session_state.c_24h == "6626"
tem_acesso_vip = is_mega or is_24h_ativo

# 3. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    if tem_acesso_vip:
        st.session_state.premium_ativo = st.toggle("✨ SIDE BAR PREMIUM", value=st.session_state.premium_ativo)
    else:
        st.session_state.premium_ativo = False

    menu = ["🌍 Explorar", "🔬 Lab Especial", "🐾 Meu Zoo", "⚙️ Definições"]
    if st.session_state.premium_ativo:
        menu = ["🌀 Resgate", "❄️ Criogenia"] + menu
    aba = st.radio("Navegação", menu)

# 4. DESIGN CSS (PONTAS CURVAS E APARÊNCIA)
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
        margin-bottom: 25px; min-height: 540px;
    }}
    .img-vertical {{ width: 100%; border-radius: 20px; height: 280px; object-fit: cover; }}
    .linha-sep {{ border-top: 2px solid {cor_borda if "gradient" not in cor_borda else "#ff00ff"}; margin: 12px 0; }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÃO DO CARTÃO
def card(an, prefixo, idx=0):
    if not an: return
    nome = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    cientifico = an.get('name', 'N/A')
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/250x400")
    ukey = f"{prefixo}_{an.get('id', random.randint(1000,9999))}_{idx}"
    
    amb = "Aquático" if any(x in st.session_state.get('bioma_sel', '') for x in ['Oceano', 'Mar', 'Fossa', 'Coral']) else "Terrestre"
    nome_exibicao = st.session_state.nomes_zoo.get(ukey, nome)
    
    html = f"""
    <div class="cartao-cidadao">
        <span style="color:#ffd700; font-weight:bold; font-size:0.65em; display:block; text-align:center;">💳 CARTÃO DE CIDADÃO</span>
        <img src="{foto}" class="img-vertical">
        <div style="text-align:center; font-weight:bold; margin-top:15px; font-size:1.3em; color:#ffd700;">{nome_exibicao}</div>
        <div style="color:#1DB954; font-style:italic; text-align:center; margin-bottom:12px; font-size:0.9em;">({cientifico})</div>
        <div>🐾 <b>Classe:</b> {random.choice(["Mamífero", "Ave", "Peixe", "Réptil"])}</div>
        <div>🥚 <b>Repro:</b> {random.choice(["Ovíparo", "Vivíparo"])}</div>
        <div>🥩 <b>Alim:</b> {random.choice(["Herbívoro", "Carnívoro"])}</div>
        <div>🌲 <b>Amb:</b> {amb}</div>
    """
    if st.session_state.premium_ativo:
        html += f'<div class="linha-sep"></div><div style="color:#bdc3c7;"><b>⚡ Vel:</b> {random.randint(10,150)}km/h | <b>⚖️ Peso:</b> {random.randint(1,800)}kg<br><b>⏳ Vida:</b> {random.randint(2,100)} anos</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
    
    if prefixo == "explorar":
        if st.button("📥 Capturar", key=f"cap_{ukey}", use_container_width=True):
            st.session_state.zoo.append(an); st.toast("Capturado!")
    elif prefixo == "zoo":
        nn = st.text_input("Apelido:", key=f"in_{ukey}")
        if nn: st.session_state.nomes_zoo[ukey] = nn; st.rerun()
        if st.button("🗑️ Soltar", key=f"del_{ukey}", use_container_width=True):
            st.session_state.zoo.pop(idx); st.rerun()

# 6. ABAS
if aba == "🌍 Explorar":
    st.header("🌍 Planisfério de Exploração")
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/World_map_-_low_resolution.svg/1000px-World_map_-_low_resolution.svg.png")
    
    bioma = st.selectbox("Escolha a Região:", [
        "Floresta Amazónica", "Floresta do Congo", "Floresta Negra", "Taiga Siberiana", "Mata Atlântica",
        "Oceano Pacífico", "Oceano Atlântico", "Oceano Índico", "Oceano Ártico", "Fossa das Marianas", "Grande Barreira de Coral"
    ])
    st.session_state.bioma_sel = bioma
    
    try:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={bioma}&taxon_id=1&per_page=70&locale=pt-PT")
        animais = r.json().get('results', [])
    except: animais = []
    
    for i in range(0, len(animais), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(animais):
                with cols[j]: card(animais[i+j], "explorar", i+j)

elif aba == "🐾 Meu Zoo":
    st.header("🐾 Meu Zoo")
    for i in range(0, len(st.session_state.zoo), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(st.session_state.zoo):
                with cols[j]: card(st.session_state.zoo[i+j], "zoo", i+j)

elif aba == "🔬 Lab Especial":
    st.header("🔬 Laboratório")
    st.success("Sequenciador disponível.")

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    t1, t2 = st.tabs(["🔑 Acesso", "🎨 Aparência"])
    with t1:
        st.session_state.c_mega = st.text_input("Código Mega", value=st.session_state.c_mega, type="password")
        st.session_state.c_24h = st.text_input("Código 24h", value=st.session_state.c_24h, type="password")
    with t2:
        st.session_state.cor_tema = st.color_picker("Cor de Fundo", st.session_state.cor_tema)
        st.session_state.negrito = st.checkbox("Negrito", st.session_state.negrito)
        st.session_state.brilho = st.slider("Brilho", 50, 150, st.session_state.brilho)
    if st.button("Guardar"): st.rerun()
