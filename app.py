import streamlit as st
import requests
import random
from datetime import datetime, timedelta

# 1. ESTADO DO SISTEMA
chaves = {
    'zoo': [], 'criogenia_storage': [],
    'c_24h': "", 'c_mega': "", 'c_crio': "", 
    'c_neon': "", 'c_diamante': "", 'premium_ativo': False, 
    'ini_premium': None, 'exp_trava': None
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# 2. LÓGICA DE ACESSO
is_mega = st.session_state.c_mega == "67lucas62"
is_neon = st.session_state.c_neon == "6676neon7secret"
is_diamante = st.session_state.c_diamante == "77daimond8secret"

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

vip_disponivel = is_mega or is_24h_ativo

# 3. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    if vip_disponivel:
        st.session_state.premium_ativo = st.toggle("✨ SIDE BAR PREMIUM", value=st.session_state.premium_ativo)
    
    menu = ["🌍 Explorar", "🐾 Meu Zoo", "⚙️ Definições"]
    if st.session_state.premium_ativo:
        menu = ["🔬 Lab Especial", "🌀 Resgate", "❄️ Criogenia"] + menu
    aba = st.radio("Navegação", menu)

# 4. DESIGN E CORES
cor_borda = "#2ecc71"
linha_estilo = f"border-top: 2px solid {cor_borda};"

if is_mega: 
    cor_borda = "linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet)"
    linha_estilo = "border-top: 2px solid; border-image: linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet) 1;"
elif is_24h_ativo:
    cor_borda = "#ffd700"
    linha_estilo = f"border-top: 2px solid {cor_borda};"

st.markdown(f"""
<style>
    .stApp {{ background-color: #0b1117; color: white; }}
    .cartao-cidadao {{
        background: #1a1c23; border-radius: 12px; padding: 10px; border: 3px solid;
        border-color: {cor_borda if "gradient" not in cor_borda else "transparent"};
        border-image: {cor_borda if "gradient" in cor_borda else "none"} 1;
        margin-bottom: 10px; font-size: 0.75em;
    }}
    .label-cidadao {{ color: #ffd700; font-weight: bold; font-size: 0.7em; text-align: center; display: block; }}
    .stats-vip {{ margin-top: 5px; padding-top: 5px; {linha_estilo} color: #bdc3c7; }}
    .info-base {{ margin: 2px 0; }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÕES
def card(an, prefixo):
    if not an or not isinstance(an, dict): return
    nome = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    cientifico = an.get('name', 'N/A')
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/150")
    ukey = f"{prefixo}_{an.get('id', random.randint(0,9999))}"
    
    # Dados Aleatórios para Simulação de Biologia
    classe = random.choice(["Mamífero", "Réptil", "Ave", "Peixe", "Anfíbio"])
    repro = random.choice(["Ovíparo", "Vivíparo"])
    alimen = random.choice(["Herbívoro", "Carnívoro", "Omnívoro"])
    
    html_card = f"""
    <div class="cartao-cidadao">
        <span class="label-cidadao">💳 CARTÃO DE CIDADÃO</span>
        <img src="{foto}" style="width:100%; border-radius:8px; height:85px; object-fit:cover;">
        <div style="text-align:center; font-weight:bold; margin-top:5px;">{nome}</div>
        <div style="color:#1DB954; font-style:italic; text-align:center; font-size:0.8em;">{cientifico}</div>
        <div class="info-base">🐾 <b>Classe:</b> {classe}</div>
        <div class="info-base">🥚 <b>Repro:</b> {repro}</div>
        <div class="info-base">🥩 <b>Alim:</b> {alimen}</div>
    """
    
    if st.session_state.premium_ativo:
        vel = random.randint(10, 120)
        peso = random.randint(1, 500)
        vida = random.randint(5, 80)
        html_card += f"""
        <div class="stats-vip">
            <b>⚡ Vel:</b> {vel} km/h | <b>⚖️ Peso:</b> {peso}kg<br>
            <b>⏳ Vida:</b> {vida} anos
        </div>
        """
    
    html_card += "</div>"
    st.markdown(html_card, unsafe_allow_html=True)
    
    if prefixo == "explorar":
        if st.button(f"📥 Capturar" if not st.session_state.premium_ativo else "🧬 Fundir", key=f"btn_{ukey}", use_container_width=True):
            st.session_state.zoo.append(an); st.toast(f"{nome} adicionado!")
    elif prefixo == "zoo":
        if st.button(f"🗑️ Soltar", key=f"del_{ukey}", use_container_width=True):
            st.session_state.zoo.remove(an); st.rerun()

# 6. ABAS
if aba == "🌍 Explorar":
    st.header("🌍 Biomas Mundiais")
    st.write("Conheça os ecossistemas e as suas camadas:")
    
    tipo = st.selectbox("Ambiente:", ["Amazónia", "Fossa das Marianas", "Floresta Negra", "Grande Barreira de Coral", "Savana Africana", "Oceano Ártico"])
    animais = requests.get(f"https://api.inaturalist.org/v1/taxa?q={tipo}&taxon_id=1&per_page=9&locale=pt-PT").json().get('results', [])
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: card(an, "explorar")

elif aba == "🐾 Meu Zoo":
    st.header("🐾 Meu Zoo")
    cols = st.columns(3)
    for i, an in enumerate(st.session_state.zoo):
        with cols[i%3]: card(an, "zoo")

elif aba == "🔬 Lab Especial":
    st.header("🔬 Lab de DNA")
    

[Image of a DNA sequence model]

    st.success("Sequenciador pronto para criar híbridos.")

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    st.session_state.c_mega = st.text_input("Mega", value=st.session_state.c_mega, type="password")
    st.session_state.c_24h = st.text_input("24h (6626)", value=st.session_state.c_24h, type="password")
    if st.button("Guardar"): st.rerun()
