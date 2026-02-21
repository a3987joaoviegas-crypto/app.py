import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO INICIAL
st.set_page_config(page_title="MundoVivo Ultra 🌍", layout="wide")

# 2. INICIALIZAÇÃO SEGURA DO ESTADO
chaves_padrao = {
    'zoo': [], 'codigo': "", 'codigo_perm': "", 'codigo_crio': "",
    'premium_ativado_em': None, 'premium_ativo': False,
    'cor_card': "Preto", 'cor_fundo': "Preto", 'idioma': "pt-PT", 
    'nome_zoologo': "Explorador", 'luminosidade': 100, 'negrito': False,
    'resgates_ativos': ["Tigre ferido", "Panda faminto", "Baleia encalhada"],
    'criogenia_storage': []
}

for chave, valor in chaves_padrao.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

# 3. LÓGICA DE PRIVILÉGIOS E TEMPO (24H)
is_premium = st.session_state.get('codigo') == "6626"
is_mega = st.session_state.get('codigo_perm') == "67lucas62"
tem_acesso = is_premium or is_mega

if is_premium and st.session_state.premium_ativado_em is None:
    st.session_state.premium_ativado_em = datetime.now()

tempo_restante_str = "24:00:00"
if is_premium and st.session_state.premium_ativado_em:
    expira = st.session_state.premium_ativado_em + timedelta(hours=24)
    if datetime.now() > expira:
        st.session_state.codigo = ""
        st.session_state.premium_ativado_em = None
        st.session_state.premium_ativo = False
        st.rerun()
    else:
        diff = expira - datetime.now()
        horas, rem = divmod(int(diff.total_seconds()), 3600)
        minutos, segundos = divmod(rem, 60)
        tempo_restante_str = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

# LIMITE E OCUPAÇÃO
LIMITE_ZOO = 80 if is_mega else (40 if is_premium else 20)
ocupacao_total = len(st.session_state.zoo) + len(st.session_state.criogenia_storage)

# 4. DESIGN CSS
mapa_cores = {"Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", "Verde": "#002b1b"}
app_bg = mapa_cores.get(st.session_state.cor_fundo, "#0b1117")
peso = "bold" if st.session_state.negrito else "normal"

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; filter: brightness({st.session_state.luminosidade}%); font-weight: {peso}; }}
    .lab-premium-box {{ 
        background: linear-gradient(135deg, #001f3f 0%, #000 100%); 
        border: 2px solid #00ffff; border-radius: 15px; padding: 20px; color: white;
    }}
</style>
""", unsafe_allow_html=True)

# 5. INTERRUPTOR (O OVO) NO TOPO
if tem_acesso:
    c1, c2 = st.columns([5, 1])
    with c2:
        st.session_state.premium_ativo = st.toggle("🔄 MODO PREMIUM", value=st.session_state.premium_ativo)

# 6. SIDEBAR DINÂMICA
with st.sidebar:
    st.title("🌍 MundoVivo")
    if st.session_state.premium_ativo and tem_acesso:
        st.subheader("🚀 SETOR PREMIUM")
        nav = ["🔬 Lab: Fusão e Stats", "🚁 Resgates", "💊 Criogenia", "⚙️ Definições"]
    else:
        st.subheader("🌿 SETOR NORMAL")
        nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"]
    aba = st.radio("Navegação", nav)

# 7. LOGICA DAS ABAS DUPLICADAS
if aba == "🔬 Laboratório":
    st.title("🔬 Laboratório de Observação (Grátis)")
    st.info("Este é o laboratório original. Faz as tuas análises básicas aqui.")

elif aba == "🔬 Lab: Fusão e Stats":
    st.title("🔬 Centro Bio-Genético Premium")
    

[Image of the structure of DNA double helix]

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown("<div class='lab-premium-box'>", unsafe_allow_html=True)
        st.subheader("🧬 Fusão de Genes")
        if len(st.session_state.zoo) >= 2:
            a1 = st.selectbox("DNA do Animal 1", [x.get('name', '???') for x in st.session_state.zoo], key="f1")
            a2 = st.selectbox("DNA do Animal 2", [x.get('name', '???') for x in st.session_state.zoo], key="f2")
            if st.button("FUNDIR DNA"):
                st.success(f"Híbrido criado: {a1[:4]}{a2[-3:].lower()}")
        else:
            st.warning("Captura pelo menos 2 animais para fundir genes.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_f2:
        st.markdown("<div class='lab-premium-box'>", unsafe_allow_html=True)
        st.subheader("📊 Estatísticas Reais")
        st.metric("Ocupação do Zoo (Total)", f"{ocupacao_total} / {LIMITE_ZOO}")
        st.metric("Na Criogenia", len(st.session_state.criogenia_storage))
        st.markdown("</div>", unsafe_allow_html=True)

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    if is_premium and not is_mega: st.info(f"⏳ Tempo Premium: {tempo_restante_str}")
    
    st.session_state.nome_zoologo = st.text_input("Nome", st.session_state.nome_zoologo)
    st.session_state.codigo = st.text_input("Código Premium (24h)", value=st.session_state.codigo, type="password")
    st.session_state.codigo_perm = st.text_input("Código Mega", value=st.session_state.codigo_perm, type="password")
    st.session_state.cor_fundo = st.selectbox("Cor Fundo", list(mapa_cores.keys()), index=list(mapa_cores.keys()).index(st.session_state.cor_fundo))
    st.session_state.luminosidade = st.slider("Brilho", 50, 150, st.session_state.luminosidade)
    st.session_state.negrito = st.checkbox("Negrito", value=st.session_state.negrito)
    if st.button("GUARDAR"): st.rerun()

# Lógica de Países/Florestas/Oceanos mantida conforme versões anteriores.
