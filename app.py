import streamlit as st
import requests
import random
import time
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

# 2. LÓGICA DE ACESSO E CÓDIGOS
is_mega = st.session_state.c_mega == "67lucas62"
is_neon = st.session_state.c_neon == "6676neon7secret"
is_diamante = st.session_state.c_diamante == "77daimond8secret"

# Trava do 6626 (1 semana após uso)
pode_6626 = True
if st.session_state.exp_trava:
    if datetime.now() - st.session_state.exp_trava < timedelta(weeks=1): 
        pode_6626 = False

is_24h = (st.session_state.c_24h == "6626" and pode_6626)
vip_global = is_mega or is_24h

# 3. SIDEBAR COM INTERRUPTOR
with st.sidebar:
    st.title("🌍 MundoVivo")
    
    # Interruptor aparece apenas se tiver direito ao VIP
    if vip_global:
        st.session_state.premium_ativo = st.toggle("✨ SIDE BAR PREMIUM", value=st.session_state.premium_ativo)
    
    # Menu Dinâmico
    if st.session_state.premium_ativo and vip_global:
        menu = ["🔬 Lab Especial", "🌀 Resgate", "❄️ Criogenia", "🐾 Meu Zoo", "🌍 Explorar", "⚙️ Definições"]
    else:
        menu = ["🌍 Explorar", "🐾 Meu Zoo", "⚙️ Definições"]
    
    aba = st.radio("Navegação", menu)

# 4. DESIGN (NEON / DIAMANTE / MEGA)
cor_borda = "#2ecc71"
if is_neon: cor_borda = "#00ff00"
if is_diamante: cor_borda = "#00d4ff"
if is_mega: cor_borda = "linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet)"

st.markdown(f"""
<style>
    .stApp {{ background-color: #0b1117; color: white; }}
    .cartao {{
        background: #1a1c23; border-radius: 15px; padding: 15px; border: 4px solid;
        border-image: {cor_borda if "gradient" in cor_borda else "none"} 1;
        border-color: {cor_borda if "gradient" not in cor_borda else "transparent"};
        margin-bottom: 15px;
    }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÕES
def buscar_animais(q):
    try:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=6&locale=pt-PT")
        return r.json().get('results', [])
    except: return []

def card(an, modo="explorar"):
    nome = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    cientifico = an.get('name', 'N/A')
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/150")
    
    st.markdown(f"""
    <div class="cartao">
        <img src="{foto}" style="width:100%; border-radius:10px; height:160px; object-fit:cover;">
        <h3 style="margin:10px 0 0 0;">{nome}</h3>
        <i style="color:#1DB954;">{cientifico}</i>
    </div>
    """, unsafe_allow_html=True)
    
    limite = 80 if st.session_state.premium_ativo else 20

    if modo == "explorar":
        # Lógica de Botões Inferiores
        if st.session_state.premium_ativo:
            if st.button(f"🧬 Fundir Genes", key=f"fus_{an['id']}"):
                st.toast("ADN extraído para o Laboratório!")
        else:
            if st.button(f"📥 Capturar", key=f"cap_{an['id']}", use_container_width=True):
                if len(st.session_state.zoo) < limite:
                    st.session_state.zoo.append(an)
                    st.toast(f"{nome} enviado para o Zoo!")
                else: st.error("Zoo cheio (Limite 20)!")
        
        # Botão Criogenia (Bloqueado por crio99)
        if st.session_state.c_crio == "crio99":
            if st.button(f"❄️ Enviar para Criogenia", key=f"crio_btn_{an['id']}"):
                st.session_state.criogenia_storage.append(an)
                st.success("Animal congelado!")
        else:
            st.button("🔒 Criogenia Bloqueada", key=f"lock_{an['id']}", disabled=True, help="Usa o código crio99 nas definições")

    elif modo == "zoo":
        if st.button(f"🗑️ Apagar Animal", key=f"del_{an['id']}", use_container_width=True):
            st.session_state.zoo.remove(an)
            st.rerun()

    elif modo == "resgate":
        if st.button(f"🌀 Resgatar", key=f"res_{an['id']}", use_container_width=True):
            st.session_state.zoo.append(an)
            st.session_state.criogenia_storage.remove(an)
            st.rerun()

# 6. ABAS
if aba == "🌍 Explorar":
    st.header("🌍 Explorar Biomas")
    
    tipo = st.selectbox("Escolha onde procurar:", ["Amazónia", "Oceano Pacífico", "Savana Africana", "Florestas Boreais"])
    cols = st.columns(2)
    for i, an in enumerate(buscar_animais(tipo)):
        with cols[i%2]: card(an, "explorar")

elif aba == "🐾 Meu Zoo":
    st.header("🐾 Meu Zoo")
    if st.button("🔴 ELIMINAR TODO O ZOO", use_container_width=True):
        st.session_state.zoo = []
        st.rerun()
    
    st.write(f"Capacidade ocupada: {len(st.session_state.zoo)}/{80 if st.session_state.premium_ativo else 20}")
    cols = st.columns(2)
    for i, an in enumerate(st.session_state.zoo):
        with cols[i%2]: card(an, "zoo")

elif aba == "🌀 Resgate":
    st.header("🌀 Unidade de Resgate")
    if not st.session_state.criogenia_storage: st.info("Câmara de criogenia vazia.")
    for an in st.session_state.criogenia_storage: card(an, "resgate")

elif aba == "❄️ Criogenia":
    st.header("❄️ Criogenia Desbloqueada")
    st.write("Usa o menu 'Explorar' para mandar animais para aqui.")

elif aba == "🔬 Lab Especial":
    st.header("🔬 Laboratório Premium")
    st.success("Acesso autorizado. Mistura de genes ativada.")
    

[Image of a DNA sequence model]


elif aba == "⚙️ Definições":
    st.header("⚙️ Configurações")
    st.session_state.c_mega = st.text_input("Código Mega", value=st.session_state.c_mega, type="password")
    st.session_state.c_24h = st.text_input("Código 24h (6626)", value=st.session_state.c_24h, type="password")
    st.session_state.c_crio = st.text_input("Código Criogenia (crio99)", value=st.session_state.c_crio, type="password")
    st.session_state.c_neon = st.text_input("Código Neon", value=st.session_state.c_neon, type="password")
    st.session_state.c_diamante = st.text_input("Código Diamante", value=st.session_state.c_diamante, type="password")
    if st.button("Guardar Alterações"): st.rerun()
