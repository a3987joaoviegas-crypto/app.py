import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. ESTADO INICIAL
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
    else:
        st.session_state.premium_ativo = False
    
    menu = ["🌍 Explorar", "🐾 Meu Zoo", "⚙️ Definições"]
    if st.session_state.premium_ativo:
        menu = ["🔬 Lab Especial", "🌀 Resgate", "❄️ Criogenia"] + menu
    aba = st.radio("Navegação", menu)

# 4. DESIGN DOS CARTÕES COMPACTOS
cor_borda = "#2ecc71" # Verde padrão (Grátis)
estilo_extra = f"border-color: {cor_borda};"

if is_mega: 
    estilo_extra = "border-image: linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet) 1;"
elif is_diamante: estilo_extra = "border-color: #00d4ff; box-shadow: 0 0 10px #00d4ff;"
elif is_neon: estilo_extra = "border-color: #00ff00; box-shadow: 0 0 10px #00ff00;"
elif is_24h_ativo: estilo_extra = "border-color: #ffd700; box-shadow: 0 0 8px #ffd700;"

st.markdown(f"""
<style>
    .stApp {{ background-color: #0b1117; color: white; }}
    .cartao-cidadao {{
        background: #1a1c23; border-radius: 12px; padding: 10px; border: 3px solid;
        {estilo_extra} margin-bottom: 10px;
    }}
    .label-cidadao {{ color: #ffd700; font-weight: bold; font-size: 0.6em; text-align: center; display: block; }}
    .nome-animal {{ font-size: 0.85em; margin: 5px 0 0 0; text-align: center; font-weight: bold; }}
    .cientifico-animal {{ color: #1DB954; font-style: italic; text-align: center; font-size: 0.65em; margin-bottom: 5px; }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÕES
def buscar_animais(q):
    try:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=12&locale=pt-PT")
        return r.json().get('results', [])
    except: return []

def card(an, prefixo):
    nome = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    cientifico = an.get('name', 'N/A')
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/150")
    ukey = f"{prefixo}_{an['id']}_{random.randint(0,9999)}"
    
    st.markdown(f"""
    <div class="cartao-cidadao">
        <span class="label-cidadao">💳 C. CIDADÃO</span>
        <img src="{foto}" style="width:100%; border-radius:8px; height:90px; object-fit:cover;">
        <div class="nome-animal">{nome}</div>
        <div class="cientifico-animal">{cientifico}</div>
    </div>
    """, unsafe_allow_html=True)
    
    limite = 80 if st.session_state.premium_ativo else 20

    if prefixo == "explorar":
        if st.session_state.premium_ativo:
            if st.button(f"🧬 Fundir Genes", key=f"fus_{ukey}", use_container_width=True): 
                st.toast("🧬 Genes extraídos para o Lab!")
        else:
            if st.button(f"📥 Capturar", key=f"cap_{ukey}", use_container_width=True):
                if len(st.session_state.zoo) < limite:
                    st.session_state.zoo.append(an); st.toast(f"📥 {nome} guardado no Zoo!")
                else: st.error("❌ Zoo Cheio!")
        
        if st.session_state.c_crio == "crio99":
            if st.button(f"❄️ Criogenia", key=f"crio_{ukey}", use_container_width=True):
                st.session_state.criogenia_storage.append(an); st.success("❄️ Congelado!")

    elif prefixo == "zoo":
        if st.button(f"🗑️ Apagar Animal", key=f"del_{ukey}", use_container_width=True):
            st.session_state.zoo.remove(an); st.rerun()

    elif prefixo == "resgate":
        if st.button(f"🌀 Resgatar", key=f"res_{ukey}", use_container_width=True):
            st.session_state.zoo.append(an); st.session_state.criogenia_storage.remove(an); st.rerun()

# 6. ABAS
if aba == "🌍 Explorar":
    st.header("🌍 Explorar Biomas")
    # Biomas de Florestas e Oceanos integrados aqui
    tipo = st.selectbox("Escolha onde explorar:", [
        "Amazónia", "Floresta do Congo", "Taiga Siberiana", "Floresta Negra",
        "Oceano Atlântico", "Oceano Pacífico", "Mar Mediterrâneo", "Fossa das Marianas",
        "Recifes de Coral", "Ártico", "Savana Africana"
    ])
    animais = buscar_animais(tipo)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: card(an, "explorar")

elif aba == "🐾 Meu Zoo":
    st.header("🐾 Meu Zoo")
    if st.button("🔴 ELIMINAR TODO O ZOO", use_container_width=True):
        st.session_state.zoo = []; st.rerun()
    st.write(f"Capacidade: {len(st.session_state.zoo)}/{80 if st.session_state.premium_ativo else 20}")
    cols = st.columns(3)
    for i, an in enumerate(st.session_state.zoo):
        with cols[i%3]: card(an, "zoo")

elif aba == "🔬 Lab Especial":
    st.header("🔬 Laboratório Premium")
    st.success("Estação de análise de DNA e Fusão de Genes pronta.")

elif aba == "🌀 Resgate":
    st.header("🌀 Unidade de Resgate")
    if not st.session_state.criogenia_storage: st.info("Câmara vazia.")
    cols = st.columns(3)
    for i, an in enumerate(st.session_state.criogenia_storage):
        with cols[i%3]: card(an, "resgate")

elif aba == "❄️ Criogenia":
    st.header("❄️ Criogenia")
    st.info("Utiliza o código crio99 para enviar animais para aqui.")

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    st.session_state.c_mega = st.text_input("Código Mega (Arco-íris)", value=st.session_state.c_mega, type="password")
    st.session_state.c_24h = st.text_input("Código 24h (6626)", value=st.session_state.c_24h, type="password")
    st.session_state.c_crio = st.text_input("Código Crio (crio99)", value=st.session_state.c_crio, type="password")
    st.session_state.c_neon = st.text_input("Código Neon", value=st.session_state.c_neon, type="password")
    st.session_state.c_diamante = st.text_input("Código Diamante", value=st.session_state.c_diamante, type="password")
    if st.button("Guardar Alterações"): st.rerun()
