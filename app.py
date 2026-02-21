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
is_mega = st.session_state.c_mega == "67lucas62" # Permanente
is_neon = st.session_state.c_neon == "6676neon7secret"
is_diamante = st.session_state.c_diamante == "77daimond8secret"

# Lógica do 6626 (Com trava de 1 semana)
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

# 4. DESIGN DOS CARTÕES COMPACTOS
cor_borda = "#2ecc71"
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
        {estilo_extra} margin-bottom: 10px; max-width: 200px;
    }}
    .label-cidadao {{ color: #ffd700; font-weight: bold; font-size: 0.6em; text-align: center; display: block; }}
    .nome-animal {{ font-size: 0.9em; margin: 5px 0 0 0; text-align: center; }}
    .cientifico-animal {{ color: #1DB954; font-style: italic; text-align: center; font-size: 0.7em; margin-bottom: 5px; }}
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
        <img src="{foto}" style="width:100%; border-radius:8px; height:100px; object-fit:cover;">
        <div class="nome-animal"><b>{nome}</b></div>
        <div class="cientifico-animal">{cientifico}</div>
    </div>
    """, unsafe_allow_html=True)
    
    limite = 80 if st.session_state.premium_ativo else 20

    if prefixo == "explorar":
        if st.session_state.premium_ativo:
            if st.button(f"🧬 Fundir", key=f"fus_{ukey}", use_container_width=True): st.toast("DNA Extraído!")
        else:
            if st.button(f"📥 Capturar", key=f"cap_{ukey}", use_container_width=True):
                if len(st.session_state.zoo) < limite:
                    st.session_state.zoo.append(an); st.toast(f"{nome} no Zoo!")
                else: st.error("Limite!")
        
        if st.session_state.c_crio == "crio99":
            if st.button(f"❄️ Criogenia", key=f"crio_{ukey}", use_container_width=True):
                st.session_state.criogenia_storage.append(an); st.success("Congelado!")

    elif prefixo == "zoo":
        if st.button(f"🗑️ Apagar", key=f"del_{ukey}", use_container_width=True):
            st.session_state.zoo.remove(an); st.rerun()

    elif prefixo == "resgate":
        if st.button(f"🌀 Resgatar", key=f"res_{ukey}", use_container_width=True):
            st.session_state.zoo.append(an); st.session_state.criogenia_storage.remove(an); st.rerun()

# 6. ABAS
if aba == "🌍 Explorar":
    st.header("🌍 Explorar")
    st.write("---")
    st.write("Estrutura da Floresta:")
    
    tipo = st.selectbox("Bioma:", ["Amazónia", "Oceano Pacífico", "Savana", "Ártico", "Recifes de Coral"])
    animais = buscar_animais(tipo)
    cols = st.columns(3) # Aumentado para 3 colunas para cartões menores
    for i, an in enumerate(animais):
        with cols[i%3]: card(an, "explorar")

elif aba == "🐾 Meu Zoo":
    st.header("🐾 Meu Zoo")
    if st.button("🔴 ELIMINAR TODO O ZOO"):
        st.session_state.zoo = []; st.rerun()
    st.write(f"Capacidade: {len(st.session_state.zoo)}/{80 if st.session_state.premium_ativo else 20}")
    cols = st.columns(3)
    for i, an in enumerate(st.session_state.zoo):
        with cols[i%3]: card(an, "zoo")

elif aba == "🔬 Lab Especial":
    st.header("🔬 Laboratório")
    

[Image of a DNA sequence model]

    st.success("Estação de análise genética pronta.")

elif aba == "🌀 Resgate":
    st.header("🌀 Resgate")
    cols = st.columns(3)
    for i, an in enumerate(st.session_state.criogenia_storage):
        with cols[i%3]: card(an, "resgate")

elif aba == "❄️ Criogenia":
    st.header("❄️ Criogenia")
    st.info("Espécies preservadas com sucesso.")

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    st.session_state.c_mega = st.text_input("Mega Permanente", value=st.session_state.c_mega, type="password")
    st.session_state.c_24h = st.text_input("Premium 24h (6626)", value=st.session_state.c_24h, type="password")
    st.session_state.c_crio = st.text_input("Criogenia (crio99)", value=st.session_state.c_crio, type="password")
    st.session_state.c_neon = st.text_input("Neon", value=st.session_state.c_neon, type="password")
    st.session_state.c_diamante = st.text_input("Diamante", value=st.session_state.c_diamante, type="password")
    if st.button("Guardar"): st.rerun()
