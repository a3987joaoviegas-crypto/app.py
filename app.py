import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO INICIAL
st.set_page_config(page_title="MundoVivo Ultra 🌍", layout="wide")

# 2. INICIALIZAÇÃO BLINDADA DO ESTADO
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

# 3. LÓGICA DO TEMPO (24 HORAS)
is_premium = st.session_state.codigo == "6626"
is_mega = st.session_state.codigo_perm == "67lucas62"
tem_acesso = is_premium or is_mega

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

# 4. DESIGN CSS DINÂMICO
mapa_cores = {"Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", "Verde": "#002b1b"}
app_bg = mapa_cores.get(st.session_state.cor_fundo, "#0b1117")
card_bg = mapa_cores.get(st.session_state.cor_card, "#1a1c23")
txt_c = "black" if st.session_state.cor_fundo == "Branco" else "white"
peso = "bold" if st.session_state.negrito else "normal"

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; color: {txt_c}; filter: brightness({st.session_state.luminosidade}%); font-weight: {peso}; }}
    .cartao-cidadao {{
        background: {card_bg} !important; color: white; border-radius: 20px; 
        padding: 15px; text-align: center; border: 4px solid #2ecc71;
    }}
    .lab-pesquisa {{
        background: linear-gradient(135deg, #001f3f, #000);
        border: 2px solid #00ffff; border-radius: 15px; padding: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# 5. TOPO: INTERRUPTOR PREMIUM (O OVO)
if tem_acesso:
    c1, c2 = st.columns([5, 1])
    with c2:
        st.session_state.premium_ativo = st.toggle("💎 MODO PREMIUM", value=st.session_state.premium_ativo)

# 6. SIDEBAR DINÂMICA (SUBSTITUIÇÃO TOTAL)
with st.sidebar:
    st.title("🌍 MundoVivo")
    if st.session_state.premium_ativo and tem_acesso:
        st.subheader("🚀 MENU PREMIUM")
        nav = ["🔬 Lab de Pesquisa", "🚁 Resgates", "💊 Criogenia", "⚙️ Definições"]
    else:
        st.subheader("🌿 MENU NORMAL")
        nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "⭐ Coleção", "⚙️ Definições"]
    aba = st.radio("Navegação", nav)

# 7. CONTEÚDO DAS ABAS
if aba == "⚙️ Definições":
    st.header("⚙️ Painel de Controlo")
    
    if is_premium and not is_mega:
        st.info(f"⏳ Tempo Premium: **{tempo_restante_str}** restantes.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔑 Acessos")
        st.session_state.codigo = st.text_input("Código Premium (24h)", value=st.session_state.codigo)
        st.session_state.codigo_perm = st.text_input("Código Mega (Infinito)", value=st.session_state.codigo_perm)
        st.session_state.codigo_crio = st.text_input("Código Criogenia", value=st.session_state.codigo_crio)
        
        st.subheader("🎨 Estilo")
        st.session_state.cor_fundo = st.selectbox("Cor do Fundo", list(mapa_cores.keys()), index=list(mapa_cores.keys()).index(st.session_state.cor_fundo))
        st.session_state.cor_card = st.selectbox("Cor dos Cartões", list(mapa_cores.keys()), index=list(mapa_cores.keys()).index(st.session_state.cor_card))
        st.session_state.negrito = st.checkbox("Texto em Negrito", value=st.session_state.negrito)

    with col2:
        st.subheader("⚙️ Preferências")
        st.session_state.nome_zoologo = st.text_input("Nome do Zoólogo", st.session_state.nome_zoologo)
        st.session_state.idioma = st.selectbox("Idioma do Sistema", ["pt-PT", "pt-BR", "en-US", "es-ES"])
        st.session_state.luminosidade = st.slider("Luminosidade (%)", 50, 150, st.session_state.luminosidade)

    if st.button("💾 GUARDAR TODAS AS ALTERAÇÕES", type="primary"):
        st.rerun()

elif aba == "🔬 Lab de Pesquisa":
    st.markdown("<div class='lab-pesquisa'>", unsafe_allow_html=True)
    st.title("🔬 Laboratório de Bio-Genética")
    st.write(f"Bem-vindo, {st.session_state.nome_zoologo}. O laboratório está operacional.")
    st.markdown("</div>", unsafe_allow_html=True)

elif aba == "🌍 Países":
    st.title("🌍 Explorar Países")
    st.write(f"Procurando animais em idioma: {st.session_state.idioma}")
    # Aqui viria a função buscar_70 e render_cartao...

elif aba == "⭐ Coleção":
    st.header("🐾 Teu Zoo")
    # Lógica da coleção aqui...
