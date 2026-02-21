import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo Ultra 🌍", layout="wide")

# 2. ESTADO DO SISTEMA
chaves_padrao = {
    'zoo': [], 'tanque_fusao': [], 'criogenia_storage': [],
    'codigo': "", 'codigo_perm': "", 'codigo_crio': "",
    'premium_ativado_em': None, 'premium_ativo': False,
    'cor_card': "Preto", 'cor_fundo': "Preto", 'idioma': "pt-PT",
    'nome_zoologo': "Explorador", 'luminosidade': 100, 'negrito': False, 'pontos': 250,
    'resgates_ativos': ["Tigre ferido na Ásia", "Panda faminto na China", "Baleia encalhada em Portugal"]
}

for chave, valor in chaves_padrao.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

# 3. LÓGICA PREMIUM
is_premium = st.session_state.codigo == "6626"
is_mega = st.session_state.codigo_perm == "67lucas62"
tem_acesso = is_premium or is_mega

if is_premium and st.session_state.premium_ativado_em is None:
    st.session_state.premium_ativado_em = datetime.now()

# 4. DESIGN CSS AVANÇADO (ANIMAÇÕES)
mapa_cores = {"Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", "Verde": "#002b1b", "Cinza": "#262730"}
app_bg = mapa_cores.get(st.session_state.cor_fundo, "#0b1117")
card_bg = mapa_cores.get(st.session_state.cor_card, "#1a1c23")

# Definição da Borda Baseada no Nível
if is_mega and st.session_state.premium_ativo:
    border_style = "border: 5px solid; border-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet) 1; animation: rainbow 3s linear infinite;"
elif is_premium and st.session_state.premium_ativo:
    border_style = "border: 4px solid #ffd700; animation: pulse-gold 2s infinite;"
else:
    border_style = "border: 4px solid #2ecc71;"

st.markdown(f"""
<style>
    @keyframes pulse-gold {{
        0% {{ box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.7); border-color: #ffd700; }}
        70% {{ box-shadow: 0 0 0 15px rgba(255, 215, 0, 0); border-color: #fff3a0; }}
        100% {{ box-shadow: 0 0 0 0 rgba(255, 215, 0, 0); border-color: #ffd700; }}
    }}
    @keyframes rainbow {{
        0% {{ filter: hue-rotate(0deg); }}
        100% {{ filter: hue-rotate(360deg); }}
    }}
    .stApp {{ background-color: {app_bg}; filter: brightness({st.session_state.luminosidade}%); }}
    .cartao-cidadao {{
        background: {card_bg}; color: white; border-radius: 15px; padding: 15px; 
        text-align: center; {border_style} margin-bottom: 10px;
    }}
    .lab-box {{ 
        background: linear-gradient(135deg, #001f3f, #000); 
        border: 2px solid #00ffff; border-radius: 15px; padding: 20px; color: white;
    }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÕES
def buscar_70(q):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=9&locale={st.session_state.idioma}"
        return requests.get(url, timeout=10).json().get('results', [])
    except: return []

def render_cartao(an, local):
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/150")
    nome = an.get('preferred_common_name', an.get('name', 'Espécie')).title()
    st.markdown(f"""
    <div class="cartao-cidadao">
        <img src="{foto}" style="width:100%; border-radius:10px; height:150px; object-fit:cover;">
        <h3 style="margin:10px 0;">{nome}</h3>
        <p style="font-size:0.8em; color:#aaa;">ID: {an['id']} | {st.session_state.nome_zoologo}</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"📥 Capturar", key=f"cap_{local}_{an['id']}"):
            st.session_state.zoo.append(an)
            st.toast(f"{nome} capturado!")
    with c2:
        if st.session_state.premium_ativo and tem_acesso:
            if st.button(f"🧬 DNA", key=f"fus_{local}_{an['id']}"):
                st.session_state.tanque_fusao.append(an)
                st.toast(f"DNA de {nome} extraído!")

# 6. INTERRUPTOR PREMIUM
if tem_acesso:
    _, col_t = st.columns([5, 1])
    with col_t:
        st.session_state.premium_ativo = st.toggle("💎 MODO PREMIUM", value=st.session_state.premium_ativo)

# 7. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    st.write(f"🏆 Pontos: **{st.session_state.pontos}**")
    if st.session_state.premium_ativo and tem_acesso:
        nav = ["🧬 Fusão de Genes", "📊 Estatísticas", "🚁 Resgates", "💊 Criogenia", "⚙️ Definições"]
    else:
        nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"]
    aba = st.radio("Navegação", nav)

# 8. LOGICA DAS ABAS
if aba in ["🌍 Países", "🌲 Florestas", "🌊 Oceanos"]:
    st.title(f"🔍 Explorar {aba}")
    locais = {"🌍 Países": ["Portugal", "Brasil", "Angola"], "🌲 Florestas": ["Amazónia", "Congo"], "🌊 Oceanos": ["Atlântico", "Pacífico"]}
    escolha = st.selectbox("Local:", locais[aba])
    animais = buscar_70(escolha)
    if animais:
        cols = st.columns(3)
        for i, an in enumerate(animais):
            with cols[i%3]: render_cartao(an, aba)

elif aba == "🧬 Fusão de Genes":
    st.title("🧬 Tanque de Fusão")
    

[Image of the structure of DNA double helix]

    st.markdown("<div class='lab-box'>", unsafe_allow_html=True)
    if len(st.session_state.tanque_fusao) >= 2:
        a1 = st.selectbox("DNA 1", st.session_state.tanque_fusao, format_func=lambda x: x.get('name'), key="dna1")
        a2 = st.selectbox("DNA 2", st.session_state.tanque_fusao, format_func=lambda x: x.get('name'), key="dna2")
        if st.button("REALIZAR FUSÃO"):
            h = f"{a1.get('name')[:4].upper()}-{a2.get('name')[-3:].upper()}"
            st.success(f"Híbrido Estável: {h}")
            st.balloons()
    else: st.warning("Extrai DNA de pelo menos 2 animais primeiro!")
    st.markdown("</div>", unsafe_allow_html=True)

elif aba == "📊 Estatísticas":
    st.title("📊 Painel de Status")
    st.markdown("<div class='lab-box'>", unsafe_allow_html=True)
    st.metric("Zoo", len(st.session_state.zoo))
    st.metric("Tanque Fusão", len(st.session_state.tanque_fusao))
    st.metric("Criostase", len(st.session_state.criogenia_storage))
    st.markdown("</div>", unsafe_allow_html=True)

elif aba == "🚁 Resgates":
    st.title("🚁 Missões")
    for idx, missao in enumerate(st.session_state.resgates_ativos):
        c1, c2 = st.columns([4, 1])
        c1.warning(f"🚨 {missao}")
        if c2.button("Resgatar", key=f"res_{idx}"):
            st.session_state.pontos += 50
            st.session_state.resgates_ativos[idx] = "Missão Concluída! Próxima em breve..."
            st.rerun()

elif aba == "💊 Criogenia":
    st.title("💊 Criostase")
    if st.session_state.zoo:
        an = st.selectbox("Congelar:", st.session_state.zoo, format_func=lambda x: x.get('name'))
        if st.button("Ativar"):
            st.session_state.criogenia_storage.append(an)
            st.session_state.zoo.remove(an)
            st.rerun()

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.nome_zoologo = st.text_input("Nome", st.session_state.nome_zoologo)
        st.session_state.codigo = st.text_input("Código Premium", value=st.session_state.codigo, type="password")
        st.session_state.codigo_perm = st.text_input("Código Mega", value=st.session_state.codigo_perm, type="password")
    with c2:
        st.session_state.cor_fundo = st.selectbox("Fundo", list(mapa_cores.keys()))
        st.session_state.cor_card = st.selectbox("Cartão", list(mapa_cores.keys()))
        st.session_state.negrito = st.checkbox("Negrito", value=st.session_state.negrito)
    if st.button("Guardar"): st.rerun()
