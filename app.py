import streamlit as st
import requests
import random
from datetime import datetime, timedelta

# 1. ESTADO DO SISTEMA
chaves = {
    'zoo': [], 'crio_storage': [], 'tanque_fusao': [], 'nomes_zoo': {},
    'c_24h': "", 'c_mega': "", 'premium_ativo': False,
    'cor_tema': "#0b1117", 'negrito': False, 'brilho': 100
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

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

    menu = ["🌲 Florestas", "🌊 Oceanos", "🔬 Lab Especial", "🐾 Meu Zoo", "⚙️ Definições"]
    if st.session_state.premium_ativo:
        menu = ["🌀 Salvamento", "❄️ Criogenia", "🧬 Tanque de Fusão"] + menu
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
        margin-bottom: 25px; min-height: 540px;
    }}
    .img-vertical {{ width: 100%; border-radius: 20px; height: 280px; object-fit: cover; }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÃO DO CARTÃO
def card(an, prefixo, idx=0):
    if not an: return
    nome = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/250x400")
    ukey = f"{prefixo}_{an.get('id', random.randint(100,999))}_{idx}"
    
    st.markdown(f"""<div class="cartao-cidadao">
        <span style="color:#ffd700; font-weight:bold; font-size:0.65em; display:block; text-align:center;">💳 CARTÃO DE CIDADÃO</span>
        <img src="{foto}" class="img-vertical">
        <div style="text-align:center; font-weight:bold; margin-top:15px; font-size:1.3em; color:#ffd700;">{st.session_state.nomes_zoo.get(ukey, nome)}</div>
        <div style="font-size:0.9em; margin-top:10px;">🐾 <b>Ambiente:</b> {"Aquático" if aba == "🌊 Oceanos" else "Terrestre"}</div>
    </div>""", unsafe_allow_html=True)
    
    if prefixo in ["explorar", "lab"]:
        if st.button("📥 Capturar", key=f"cap_{ukey}", use_container_width=True):
            st.session_state.zoo.append(an); st.toast("Capturado!")
    elif prefixo == "zoo":
        if st.session_state.premium_ativo:
            if st.button("🧬 Enviar para Fusão", key=f"dna_{ukey}", use_container_width=True):
                st.session_state.tanque_fusao.append(an)
                st.session_state.zoo.pop(idx)
                st.toast("Enviado para o Tanque de Fusão!"); st.rerun()
        if st.button("🗑️ Soltar", key=f"del_{ukey}", use_container_width=True):
            st.session_state.zoo.pop(idx); st.rerun()

# 6. LOGICA DE BUSCA
def busca_animais(termo):
    try:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={termo}&taxon_id=1&per_page=70&locale=pt-PT")
        animais = r.json().get('results', [])
        for i in range(0, len(animais), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(animais):
                    with cols[j]: card(animais[i+j], "lab", i+j)
    except: pass

# 7. ABAS
if aba == "🌲 Florestas":
    st.header("🌲 Florestas")
    sel = st.selectbox("Escolha:", ["Amazónia", "Congo", "Taiga"])
    busca_animais(sel)

elif aba == "🌊 Oceanos":
    st.header("🌊 Oceanos")
    sel = st.selectbox("Escolha:", ["Oceano Pacífico", "Oceano Atlântico", "Recife de Coral"])
    busca_animais(sel)

elif aba == "🔬 Lab Especial":
    st.header("🔬 Pesquisa de Espécies")
    nome_busca = st.text_input("🔍 Pesquisar Animal:")
    if nome_busca: busca_animais(nome_busca)

elif aba == "🧬 Tanque de Fusão":
    st.header("🧬 Tanque de Fusão Premium")
    if len(st.session_state.tanque_fusao) < 2:
        st.info("Envia pelo menos 2 animais do teu Zoo usando o símbolo 🧬 para começar a fusão.")
    else:
        st.write("Selecione os espécimes para fundir:")
        a1 = st.selectbox("Espécime A:", [a.get('name') for a in st.session_state.tanque_fusao], index=0)
        a2 = st.selectbox("Espécime B:", [a.get('name') for a in st.session_state.tanque_fusao], index=1)
        if st.button("💥 INICIAR FUSÃO"):
            st.balloons()
            st.success(f"NOVA ESPÉCIE CRIADA: {a1[:4]}{a2[2:]} híbrido!")

elif aba == "🌀 Salvamento":
    st.header("🌀 Centro de Salvamento")
    st.button("💉 Curar Animal Ferido")

elif aba == "❄️ Criogenia":
    st.header("❄️ Câmara Criogénica")
    st.button("❄️ Congelar Animal")

elif aba == "🐾 Meu Zoo":
    st.header("🐾 Meu Zoo")
    for i in range(0, len(st.session_state.zoo), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(st.session_state.zoo):
                with cols[j]: card(st.session_state.zoo[i+j], "zoo", i+j)

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    st.session_state.c_mega = st.text_input("Código Mega", type="password")
    st.session_state.c_24h = st.text_input("Código 24h", type="password")
    st.session_state.cor_tema = st.color_picker("Tema", st.session_state.cor_tema)
    if st.button("Guardar"): st.rerun()
