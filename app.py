import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo Ultra 🌍", layout="wide")

# 2. INICIALIZAÇÃO DO ESTADO
if 'zoo' not in st.session_state:
    st.session_state.update({
        'zoo': [], 'codigo': "", 'codigo_perm': "", 'codigo_crio': "",
        'premium_ativado_em': None, 'premium_ativo': False,
        'cor_fundo': "Preto", 'luminosidade': 100,
        'resgates_ativos': ["Tigre ferido", "Panda faminto", "Baleia encalhada"]
    })

# LÓGICA DE TEMPO E EXPIRAÇÃO (24 HORAS)
if st.session_state.codigo == "6626" and st.session_state.premium_ativado_em is None:
    st.session_state.premium_ativado_em = datetime.now()

tempo_restante = ""
if st.session_state.premium_ativado_em:
    expira = st.session_state.premium_ativado_em + timedelta(hours=24)
    agora = datetime.now()
    if agora > expira:
        st.session_state.codigo = ""
        st.session_state.premium_ativado_em = None
        st.session_state.premium_ativo = False
        st.warning("O teu acesso Premium de 24h expirou!")
    else:
        diff = expira - agora
        horas, rem = divmod(diff.seconds, 3600)
        minutos, segundos = divmod(rem, 60)
        tempo_restante = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

# PRIVILÉGIOS
is_mega = st.session_state.codigo_perm == "67lucas62"
is_premium = st.session_state.codigo == "6626"
tem_acesso = is_premium or is_mega

# 3. INTERRUPTOR DE SUBSTITUIÇÃO NO TOPO
if tem_acesso:
    c1, c2 = st.columns([5, 1])
    with c2:
        st.session_state.premium_ativo = st.toggle("🔄 ALTERAR SIDEBAR", value=st.session_state.premium_ativo)

# 4. SIDEBAR DINÂMICA (SUBSTITUIÇÃO TOTAL)
with st.sidebar:
    st.title("🌍 MundoVivo")
    
    if st.session_state.premium_ativo and tem_acesso:
        st.subheader("💎 MENU PREMIUM")
        nav = ["🔬 Lab de Pesquisa", "🚁 Resgates", "💊 Criogenia", "⚙️ Definições"]
    else:
        st.subheader("🌿 MENU NORMAL")
        nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "⭐ Coleção", "⚙️ Definições"]
    
    aba = st.radio("Navegação", nav)

# 5. CONTEÚDO DAS ABAS
if aba == "⚙️ Definições":
    st.header("⚙️ Definições & Segurança")
    
    # Temporizador Visível
    if is_premium and not is_mega:
        st.info(f"⏳ Tempo Premium Restante: **{tempo_restante}**")
    elif is_mega:
        st.success("💎 Acesso Mega Vitalício Ativo")

    st.session_state.codigo = st.text_input("Código Premium (24h)", value=st.session_state.codigo, type="password")
    st.session_state.codigo_perm = st.text_input("Código Mega (Permanente)", value=st.session_state.codigo_perm, type="password")
    
    st.session_state.cor_fundo = st.selectbox("Cor Fundo", ["Preto", "Branco", "Azul", "Verde"])
    if st.button("GUARDAR ALTERAÇÕES", type="primary"):
        st.rerun()

elif aba == "🚁 Resgates":
    st.title("🚁 Missões de Resgate")
    for idx, res in enumerate(st.session_state.resgates_ativos):
        c1, c2 = st.columns([3, 1])
        c1.warning(f"🚨 EMERGÊNCIA: {res}")
        if c2.button("SALVAR", key=f"res_{idx}"):
            st.session_state.resgates_ativos[idx] = random.choice(["Lince preso", "Orca ferida", "Águia em perigo"])
            st.rerun()

elif aba == "🌍 Países":
    st.title("🌍 Explorar Países")
    st.write("Conteúdo normal aqui...")

# Lógica CSS e Funções de procura seriam mantidas como nas versões anteriores...
