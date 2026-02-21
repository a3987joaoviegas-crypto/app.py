import streamlit as st
import requests
import random
from datetime import datetime, timedelta

# 1. ESTADO DO SISTEMA
chaves = {
    'zoo': [], 'criogenia_storage': [], 'nomes_zoo': {},
    'c_24h': "", 'c_mega': "", 'c_crio': "", 
    'premium_ativo': False, 'ini_premium': None, 'exp_trava': None
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# 2. LÓGICA DE ACESSO
is_mega = st.session_state.c_mega == "67lucas62"
pode_6626 = True
if st.session_state.exp_trava:
    if datetime.now() - st.session_state.exp_trava < timedelta(weeks=1):
        pode_6626 = False

is_24h_ativo = False
if st.session_state.c_24h == "6626" and pode_6626:
    is_24h_ativo = True
    if st.session_state.ini_premium is None:
        st.session_state.ini_premium = datetime.now()

if st.session_state.ini_premium:
    if datetime.now() - st.session_state.ini_premium > timedelta(hours=24):
        st.session_state.exp_trava = datetime.now()
        st.session_state.ini_premium = None
        st.session_state.c_24h = ""
        st.rerun()

tem_acesso_vip = is_mega or is_24h_ativo

# 3. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    escolha_premium = st.toggle("✨ SIDE BAR PREMIUM", value=st.session_state.premium_ativo)
    
    if escolha_premium and not tem_acesso_vip:
        st.error("🔒 Requer Código Premium")
        st.session_state.premium_ativo = False
    else:
        st.session_state.premium_ativo = escolha_premium

    menu = ["🌍 Explorar", "🐾 Meu Zoo", "⚙️ Definições"]
    if st.session_state.premium_ativo:
        menu = ["🔬 Laboratório Especial", "🌀 Resgate", "❄️ Criogenia"] + menu
    aba = st.radio("Navegação", menu)

# 4. DESIGN (IMAGENS VERTICAIS E GRELHA)
cor_borda = "#2ecc71"
cor_linha = "#2ecc71"

if is_mega: 
    cor_borda = "linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet)"
    cor_linha = "#ff00ff" 
elif is_24h_ativo:
    cor_borda = "#ffd700"
    cor_linha = "#ffd700"

st.markdown(f"""
<style>
    .stApp {{ background-color: #0b1117; color: white; }}
    .cartao-cidadao {{
        background: #1a1c23; border-radius: 10px; padding: 10px; border: 3px solid;
        border-color: {cor_borda if "gradient" not in cor_borda else "transparent"};
        border-image: {cor_borda if "gradient" in cor_borda else "none"} 1;
        margin-bottom: 15px; font-size: 0.75em;
        min-height: 440px;
    }}
    .img-vertical {{
        width: 100%; border-radius: 5px; height: 180px; 
        object-fit: cover; margin-top: 5px; border-bottom: 1px solid #333;
    }}
    .label-cidadao {{ color: #ffd700; font-weight: bold; font-size: 0.65em; text-align: center; display: block; }}
    .linha-sep {{ border-top: 2px solid {cor_linha}; margin: 8px 0; opacity: 0.8; }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÕES
def card(an, prefixo, idx=0):
    if not an: return
    animal_id = str(an.get('id', random.randint(1000, 9999)))
    nome_comum = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    cientifico = an.get('name', 'N/A')
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/150x200")
    ukey = f"{prefixo}_{animal_id}_{idx}"
    
    # Simulação de Bio
    classe = random.choice(["Mamífero", "Réptil", "Ave", "Peixe", "Anfíbio"])
    repro = random.choice(["Ovíparo", "Vivíparo"])
    alimen = random.choice(["Herbívoro", "Carnívoro", "Omnívoro"])
    ambiente = random.choice(["Terrestre", "Aquático", "Arborícola"])
    
    nome_exibicao = st.session_state.nomes_zoo.get(ukey, nome_comum)
    
    card_html = f"""
    <div class="cartao-cidadao">
        <span class="label-cidadao">💳 CARTÃO DE CIDADÃO</span>
        <img src="{foto}" class="img-vertical">
        <div style="text-align:center; font-weight:bold; margin-top:8px; font-size:1.1em; color:#ffd700;">{nome_exibicao}</div>
        <div style="color:#1DB954; font-style:italic; text-align:center; margin-bottom:8px; font-size:0.85em;">({cientifico})</div>
        <div>🐾 <b>Classe:</b> {classe}</div>
        <div>🥚 <b>Repro:</b> {repro}</div>
        <div>🥩 <b>Alim:</b> {alimen}</div>
        <div>🌲 <b>Amb:</b> {ambiente}</div>
    """
    
    if st.session_state.premium_ativo:
        vel, peso, vida = random.randint(10,130), random.randint(1,600), random.randint(4,95)
        card_html += f"""
        <div class="linha-sep"></div>
        <div style="color:#bdc3c7;">
            <b>⚡ Vel:</b> {vel}km/h | <b>⚖️ Peso:</b> {peso}kg<br><b>⏳ Vida:</b> {vida} anos
        </div>
        """
    card_html += "</div>"
    st.markdown(card_html, unsafe_allow_html=True)
    
    if prefixo == "explorar":
        if st.button("📥 Capturar", key=f"cap_{ukey}", use_container_width=True):
            st.session_state.zoo.append(an); st.toast(f"{nome_comum} capturado!")
    elif prefixo == "zoo":
        novo_nome = st.text_input("Apelido:", value=st.session_state.nomes_zoo.get(ukey, ""), key=f"input_{ukey}")
        if novo_nome: st.session_state.nomes_zoo[ukey] = novo_nome
        if st.button("🗑️ Soltar", key=f"del_{ukey}", use_container_width=True):
            st.session_state.zoo.pop(idx); st.session_state.nomes_zoo.pop(ukey, None); st.rerun()

# 6. ABAS
if aba == "🌍 Explorar":
    st.header("🌍 Explorar Biomas")
    tipo = st.selectbox("Região:", ["Amazónia", "Fossa das Marianas", "Floresta Negra", "Grande Barreira de Coral", "Savana Africana", "Ártico", "Oceano Índico"])
    
    try:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={tipo}&taxon_id=1&per_page=70&locale=pt-PT")
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
    st.success("Sequenciador VIP Ativo.")

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    st.session_state.c_mega = st.text_input("Mega", value=st.session_state.c_mega, type="password")
    st.session_state.c_24h = st.text_input("24h (6626)", value=st.session_state.c_24h, type="password")
    if st.button("Guardar"): st.rerun()

