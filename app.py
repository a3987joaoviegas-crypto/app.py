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

# 3. LÓGICA PREMIUM & TEMPO
is_premium = st.session_state.codigo == "6626"
is_mega = st.session_state.codigo_perm == "67lucas62"
tem_acesso = is_premium or is_mega

if is_premium and st.session_state.premium_ativado_em is None:
    st.session_state.premium_ativado_em = datetime.now()

tempo_restante_str = "24:00:00"
if is_premium and st.session_state.premium_ativado_em:
    expira = st.session_state.premium_ativado_em + timedelta(hours=24)
    if datetime.now() > expira:
        st.session_state.codigo = ""
        st.session_state.premium_ativo = False
    else:
        diff = expira - datetime.now()
        horas, rem = divmod(int(diff.total_seconds()), 3600)
        minutos, segundos = divmod(rem, 60)
        tempo_restante_str = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

# 4. DESIGN CSS
mapa_cores = {"Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", "Verde": "#002b1b"}
app_bg = mapa_cores.get(st.session_state.cor_fundo, "#0b1117")
card_bg = mapa_cores.get(st.session_state.cor_card, "#1a1c23")
peso = "bold" if st.session_state.negrito else "normal"

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; filter: brightness({st.session_state.luminosidade}%); font-weight: {peso}; }}
    .cartao-cidadao {{
        background: {card_bg}; color: white; border-radius: 20px; padding: 15px; 
        text-align: center; border: 4px solid #2ecc71; margin-bottom: 15px;
    }}
    .lab-box {{ background: linear-gradient(135deg, #001f3f, #000); border: 2px solid #00ffff; border-radius: 15px; padding: 20px; color: white; }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÕES DE BUSCA E RENDERIZAÇÃO
def buscar_70(q):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=12&locale={st.session_state.idioma}"
        return requests.get(url, timeout=10).json().get('results', [])
    except: return []

def render_cartao(an, local):
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/150")
    nome = an.get('preferred_common_name', an.get('name', 'Espécie')).title()
    
    st.markdown(f"""
    <div class="cartao-cidadao">
        <img src="{foto}" style="width:100%; border-radius:12px; height:150px; object-fit:cover;">
        <h4 style="margin:10px 0;">{nome}</h4>
        <div style="font-size:0.8em; opacity:0.8;">🧬 ID: {an.get('id', '???')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"Capturar", key=f"cap_{local}_{an['id']}"):
            st.session_state.zoo.append(an)
            st.toast(f"{nome} capturado!")
    with c2:
        if st.session_state.premium_ativo and tem_acesso:
            if st.button(f"🧬 Fusão", key=f"fus_{local}_{an['id']}"):
                st.session_state.tanque_fusao.append(an)
                st.toast("Enviado para o Tanque de Fusão!")

# 6. INTERRUPTOR PREMIUM (O OVO)
if tem_acesso:
    _, col_t = st.columns([5, 1])
    with col_t:
        st.session_state.premium_ativo = st.toggle("🔄 MODO PREMIUM", value=st.session_state.premium_ativo)

# 7. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    if st.session_state.premium_ativo and tem_acesso:
        nav = ["🔬 Lab Especializado", "🚁 Resgates", "💊 Criogenia", "⚙️ Definições"]
    else:
        nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"]
    aba = st.radio("Navegação", nav)

# 8. ABAS
if aba in ["🌍 Países", "🌲 Florestas", "🌊 Oceanos"]:
    st.title(f"🔍 {aba}")
    locais = {
        "🌍 Países": ["Portugal", "Brasil", "Angola", "Japão", "Espanha"],
        "🌲 Florestas": ["Amazónia", "Selva Congo", "Floresta Boreal"],
        "🌊 Oceanos": ["Mar Vermelho", "Oceano Índico", "Abismo das Marianas"]
    }
    escolha = st.selectbox("Escolher Local:", locais[aba])
    animais = buscar_70(escolha)
    if animais:
        cols = st.columns(3)
        for i, an in enumerate(animais):
            with cols[i%3]: render_cartao(an, aba)

elif aba == "🔬 Lab Especializado":
    st.title("🔬 Centro Bio-Genético (Premium)")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='lab-box'><h3>🧬 Tanque de Fusão</h3>", unsafe_allow_html=True)
        if len(st.session_state.tanque_fusao) >= 2:
            a1 = st.selectbox("DNA 1", st.session_state.tanque_fusao, format_func=lambda x: x.get('name'), key="t1")
            a2 = st.selectbox("DNA 2", st.session_state.tanque_fusao, format_func=lambda x: x.get('name'), key="t2")
            if st.button("FUNDIR"):
                st.success(f"Híbrido Estável: {a1.get('name')[:4]}{a2.get('name')[-3:]}")
                st.balloons()
        else: st.info(f"O tanque tem {len(st.session_state.tanque_fusao)}/2 animais. Manda animais para aqui usando o botão '🧬 Fusão' nos cartões!")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='lab-box'><h3>📊 Estatísticas</h3>", unsafe_allow_html=True)
        st.write(f"🐾 No Zoo: {len(st.session_state.zoo)}")
        st.write(f"❄️ Na Criogenia: {len(st.session_state.criogenia_storage)}")
        st.write(f"🧬 No Tanque: {len(st.session_state.tanque_fusao)}")
        st.markdown("</div>", unsafe_allow_html=True)

elif aba == "🚁 Resgates":
    st.title("🚁 Centro de Resgate")
    for idx, missao in enumerate(st.session_state.resgates_ativos):
        c1, c2 = st.columns([4, 1])
        c1.warning(f"🚨 MISSÃO: {missao}")
        if c2.button("Resgatar", key=f"res_{idx}"):
            st.session_state.pontos += 50
            st.session_state.resgates_ativos[idx] = random.choice(["Lince ferido", "Águia presa", "Golfinho em rede"])
            st.rerun()

elif aba == "💊 Criogenia":
    st.title("💊 Criostase")
    if st.session_state.zoo:
        an_crio = st.selectbox("Selecionar para Congelar:", st.session_state.zoo, format_func=lambda x: x.get('name'))
        if st.button("Mandar para Criogenia"):
            st.session_state.criogenia_storage.append(an_crio)
            st.session_state.zoo.remove(an_crio)
            st.rerun()
    st.write(f"❄️ Total em Criogenia: {len(st.session_state.criogenia_storage)}")

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    if is_premium: st.info(f"⏳ Tempo Premium: {tempo_restante_str}")
    st.session_state.codigo = st.text_input("Código Premium", value=st.session_state.codigo)
    st.session_state.codigo_perm = st.text_input("Código Mega", value=st.session_state.codigo_perm)
    st.session_state.cor_card = st.selectbox("Cor Cartão", list(mapa_cores.keys()))
    st.session_state.luminosidade = st.slider("Brilho", 50, 150, st.session_state.luminosidade)
    if st.button("Guardar"): st.rerun()
