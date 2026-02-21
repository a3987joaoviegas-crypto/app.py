import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo Ultra 🌍", layout="wide")

# 2. INICIALIZAÇÃO SEGURA (Evita AttributeError)
chaves_padrao = {
    'zoo': [], 'codigo': "", 'codigo_perm': "", 'codigo_crio': "",
    'premium_ativado_em': None, 'premium_ativo': False,
    'cor_fundo': "Preto", 'luminosidade': 100, 'negrito': False,
    'resgates_ativos': ["Tigre ferido", "Panda faminto", "Baleia encalhada"],
    'criogenia_storage': []
}

for chave, valor in chaves_padrao.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

# 3. LÓGICA DO TEMPO (24 HORAS)
is_premium = st.session_state.codigo == "6626"
is_mega = st.session_state.codigo_perm == "67lucas62"
tem_acesso = is_premium or is_mega

# Se ativou o premium agora, grava a hora
if is_premium and st.session_state.premium_ativado_em is None:
    st.session_state.premium_ativado_em = datetime.now()

tempo_restante_str = "24:00:00"
if is_premium and st.session_state.premium_ativado_em:
    expira = st.session_state.premium_ativado_em + timedelta(hours=24)
    agora = datetime.now()
    if agora > expira:
        st.session_state.codigo = ""
        st.session_state.premium_ativado_em = None
        st.session_state.premium_ativo = False
        st.rerun()
    else:
        diff = expira - agora
        horas, rem = divmod(int(diff.total_seconds()), 3600)
        minutos, segundos = divmod(rem, 60)
        tempo_restante_str = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

# 4. INTERRUPTOR DE SUBSTITUIÇÃO (O OVO)
if tem_acesso:
    col_t1, col_t2 = st.columns([5, 1])
    with col_t2:
        # Só aparece se tiver um dos códigos
        st.session_state.premium_ativo = st.toggle("💎 MODO PREMIUM", value=st.session_state.premium_ativo)

# 5. SIDEBAR DINÂMICA
with st.sidebar:
    st.title("🌍 MundoVivo")
    
    # Se o interruptor estiver ligado, a sidebar MUDA TOTALMENTE
    if st.session_state.premium_ativo and tem_acesso:
        st.subheader("🚀 MENU PREMIUM")
        nav = ["🔬 Lab de Pesquisa", "🚁 Resgates", "💊 Criogenia", "⚙️ Definições"]
    else:
        st.subheader("🌿 MENU NORMAL")
        nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "⭐ Coleção", "⚙️ Definições"]
    
    aba = st.radio("Navegação", nav)

# 6. CONTEÚDO DAS ABAS
if aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    
    if is_premium and not is_mega:
        st.info(f"⏳ O teu acesso Premium expira em: **{tempo_restante_str}**")
    
    st.session_state.codigo = st.text_input("Código Premium (24h)", value=st.session_state.codigo)
    st.session_state.codigo_perm = st.text_input("Código Mega (Infinito)", value=st.session_state.codigo_perm)
    st.session_state.cor_fundo = st.selectbox("Cor Fundo", ["Preto", "Branco", "Azul", "Verde"])
    
    if st.button("GUARDAR E ATUALIZAR"):
        st.rerun()

elif aba == "🔬 Lab de Pesquisa":
    st.title("🔬 Laboratório de Bio-Genética")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #001f3f, #000); border: 2px solid #00ffff; padding: 20px; border-radius: 15px;'>
        <h3 style='color: #00ffff;'>Central de Pesquisa Ativa</h3>
        <p>Aqui podes fundir genes e analisar o teu Zoo.</p>
    </div>
    """, unsafe_allow_html=True)

elif aba == "🌍 Países":
    st.title("🌍 Explorar o Mundo")
    st.write("Escolhe um país para encontrar animais!")

# Outras abas seguiriam a mesma lógica...
