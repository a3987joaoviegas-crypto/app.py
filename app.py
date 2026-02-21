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

# 4. DESIGN CSS (CARTÃO DE CIDADÃO + CORES)
mapa_cores = {
    "Preto": "#0b1117", 
    "Branco": "#ffffff", 
    "Azul": "#001f3f", 
    "Verde": "#002b1b", 
    "Cinza": "#262730"
}
app_bg = mapa_cores.get(st.session_state.cor_fundo, "#0b1117")
card_bg = mapa_cores.get(st.session_state.cor_card, "#1a1c23")
peso_fonte = "bold" if st.session_state.negrito else "normal"
cor_texto = "white" if st.session_state.cor_fundo != "Branco" else "black"

st.markdown(f"""
<style>
    .stApp {{ 
        background-color: {app_bg}; 
        filter: brightness({st.session_state.luminosidade}%); 
        font-weight: {peso_fonte};
        color: {cor_texto};
    }}
    .cartao-cidadao {{
        background: {card_bg}; 
        color: white; 
        border-radius: 20px; 
        padding: 15px; 
        text-align: center; 
        border: 4px solid #2ecc71; 
        margin-bottom: 10px;
    }}
    .lab-box {{ 
        background: linear-gradient(135deg, #001f3f, #000); 
        border: 2px solid #00ffff; 
        border-radius: 15px; 
        padding: 20px; 
        color: white;
        margin-bottom: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÕES DE BUSCA E RENDERIZAÇÃO
def buscar_70(q):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=9&locale={st.session_state.idioma}"
        return requests.get(url, timeout=10).json().get('results', [])
    except: return []

def render_cartao(an, local):
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/150")
    nome = an.get('preferred_common_name', an.get('name', 'Espécie')).title()
    st.markdown(f'<div class="cartao-cidadao"><img src="{foto}" style="width:100%; border-radius:12px; height:150px; object-fit:cover;"><h4>{nome}</h4></div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"Capturar", key=f"cap_{local}_{an['id']}"):
            st.session_state.zoo.append(an)
            st.toast(f"{nome} guardado no Zoo!")
    with c2:
        if st.session_state.premium_ativo and tem_acesso:
            if st.button(f"🧬 Fusão", key=f"fus_{local}_{an['id']}"):
                st.session_state.tanque_fusao.append(an)
                st.toast(f"{nome} enviado para o Tanque!")

# 6. INTERRUPTOR PREMIUM
if tem_acesso:
    _, col_t = st.columns([5, 1])
    with col_t:
        st.session_state.premium_ativo = st.toggle("🔄 MODO PREMIUM", value=st.session_state.premium_ativo)

# 7. SIDEBAR DINÂMICA
with st.sidebar:
    st.title("🌍 MundoVivo")
    if st.session_state.premium_ativo and tem_acesso:
        nav = ["🧬 Fusão de Genes", "📊 Estatísticas", "🚁 Resgates", "💊 Criogenia", "⚙️ Definições"]
    else:
        nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"]
    aba = st.radio("Navegação", nav)

# 8. LÓGICA DAS ABAS
if aba in ["🌍 Países", "🌲 Florestas", "🌊 Oceanos"]:
    st.title(f"🔍 {aba}")
    locais = {
        "🌍 Países": ["Portugal", "Brasil", "Angola", "Japão", "Espanha"],
        "🌲 Florestas": ["Amazónia", "Selva do Congo", "Taiga Siberiana"],
        "🌊 Oceanos": ["Oceano Atlântico", "Oceano Índico", "Mar Vermelho"]
    }
    escolha = st.selectbox("Escolher Localização:", locais[aba])
    animais = buscar_70(escolha)
    if animais:
        cols = st.columns(3)
        for i, an in enumerate(animais):
            with cols[i%3]: render_cartao(an, aba)

elif aba == "🧬 Fusão de Genes":
    st.title("🧬 Tanque de Fusão de DNA")
    st.markdown("<div class='lab-box'>", unsafe_allow_html=True)
    if len(st.session_state.tanque_fusao) >= 2:
        a1 = st.selectbox("DNA do Espécime 1", st.session_state.tanque_fusao, format_func=lambda x: x.get('name'), key="dna1")
        a2 = st.selectbox("DNA do Espécime 2", st.session_state.tanque_fusao, format_func=lambda x: x.get('name'), key="dna2")
        if st.button("EXECUTAR FUSÃO"):
            h = f"{a1.get('name')[:4].upper()}-{a2.get('name')[-3:].upper()}"
            st.success(f"NOVA ESPÉCIE HÍBRIDA: {h}")
            st.balloons()
    else: st.warning("O tanque precisa de pelo menos 2 animais. Usa o botão 🧬 nos cartões!")
    st.markdown("</div>", unsafe_allow_html=True)

elif aba == "📊 Estatísticas":
    st.title("📊 Painel de Estatísticas")
    st.markdown("<div class='lab-box'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.metric("Animais no Zoo", len(st.session_state.zoo))
    col1.metric("No Tanque de Fusão", len(st.session_state.tanque_fusao))
    col2.metric("Em Criostase", len(st.session_state.criogenia_storage))
    col2.metric("Pontos Atuais", st.session_state.pontos)
    st.markdown("</div>", unsafe_allow_html=True)

elif aba == "🚁 Resgates":
    st.title("🚁 Missões de Resgate")
    for idx, missao in enumerate(st.session_state.resgates_ativos):
        c1, c2 = st.columns([4, 1])
        c1.warning(f"🚨 MISSÃO ATIVA: {missao}")
        if c2.button("Resgatar", key=f"res_{idx}"):
            st.session_state.pontos += 50
            st.session_state.resgates_ativos[idx] = random.choice(["Lince preso", "Águia ferida", "Golfinho em rede"])
            st.rerun()

elif aba == "💊 Criogenia":
    st.title("💊 Unidade de Criostase")
    if st.session_state.zoo:
        an_crio = st.selectbox("Selecionar para congelar:", st.session_state.zoo, format_func=lambda x: x.get('name'))
        if st.button("Ativar Criostase"):
            st.session_state.criogenia_storage.append(an_crio)
            st.session_state.zoo.remove(an_crio)
            st.rerun()
    st.write(f"❄️ Total de animais em suspensão: {len(st.session_state.criogenia_storage)}")
    if st.session_state.criogenia_storage:
        if st.button("Descongelar Todos"):
            st.session_state.zoo.extend(st.session_state.criogenia_storage)
            st.session_state.criogenia_storage = []
            st.rerun()

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições de Sistema")
    if is_premium: st.info(f"⏳ Tempo Restante (24h): {tempo_restante_str}")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.session_state.nome_zoologo = st.text_input("Nome do Zoólogo", st.session_state.nome_zoologo)
        st.session_state.codigo = st.text_input("Código Premium (24h)", value=st.session_state.codigo, type="password")
        st.session_state.codigo_perm = st.text_input("Código Mega (Permanente)", value=st.session_state.codigo_perm, type="password")
        st.session_state.negrito = st.checkbox("Texto em Negrito", value=st.session_state.negrito)
    
    with col_d2:
        st.session_state.cor_fundo = st.selectbox("Cor do Fundo", list(mapa_cores.keys()), index=list(mapa_cores.keys()).index(st.session_state.cor_fundo))
        st.session_state.cor_card = st.selectbox("Cor do Cartão", list(mapa_cores.keys()), index=list(mapa_cores.keys()).index(st.session_state.cor_card))
        st.session_state.luminosidade = st.slider("Brilho da Interface", 50, 150, st.session_state.luminosidade)
    
    if st.button("Guardar Alterações"): st.rerun()

elif aba == "🔬 Laboratório":
    st.title("🔬 Laboratório Original")
    st.info("Laboratório básico para observação de espécimes capturados.")
    if st.session_state.zoo:
        an_lab = st.selectbox("Analisar Espécime:", st.session_state.zoo, format_func=lambda x: x.get('name'))
        render_cartao(an_lab, "lab_base")
    else: st.write("O Zoo está vazio.")
