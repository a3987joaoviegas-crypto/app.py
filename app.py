import streamlit as st
import requests
import random
import time

# 1. CONFIGURAÇÃO (Sem espaços no início)
st.set_page_config(page_title="MundoVivo Ultra 🌍", layout="wide")

# 2. INICIALIZAÇÃO BLINDADA DO ESTADO (Previne o AttributeError)
chaves_padrao = {
    'zoo': [], 'codigo': "", 'codigo_perm': "", 'codigo_crio': "", 'pontos': 250,
    'cor_card': "Preto", 'cor_fundo': "#0b1117", 'idioma': "pt-PT", 
    'nome_zoologo': "Explorador", 'luminosidade': 100, 'negrito': False,
    'criogenia_storage': [], 
    'resgates_ativos': ["Tigre ferido na Ásia", "Panda faminto", "Baleia encalhada"]
}

for chave, valor in chaves_padrao.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

# LÓGICA DE PRIVILÉGIOS
is_mega = st.session_state.codigo_perm == "67lucas62"
is_premium = st.session_state.codigo == "6626"
is_crio_unlocked = st.session_state.codigo_crio == "CRIO99"
is_mestre = is_premium or is_mega
LIMITE_ZOO = 80 if is_mestre else 20

# 3. DESIGN CSS (DINÂMICO)
app_bg = st.session_state.cor_fundo
lumi = st.session_state.luminosidade
peso = "bold" if st.session_state.negrito else "normal"

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; color: white; filter: brightness({lumi}%); font-weight: {peso}; }}
    
    .cartao-cidadao {{
        background: #1a1c23 !important; color: white !important;
        border-radius: 20px; padding: 15px; text-align: center; margin-bottom: 25px;
        border: 4px solid {"#ff00ff" if is_mega else "#2ecc71"};
        {"animation: galatico 3s linear infinite;" if is_mega else ""}
    }}
    @keyframes galatico {{ 0% {{ filter: hue-rotate(0deg); }} 100% {{ filter: hue-rotate(360deg); }} }}
    
    div.stButton > button {{ background-color: #2ecc71 !important; color: white !important; font-weight: bold; width: 100%; border: none; }}
    .stButton > button[kind="primary"] {{ background-color: #3498db !important; }}
    
    .campo-cidadao {{ background: rgba(255,255,255,0.1); padding: 8px; border-radius: 8px; font-size: 0.85em; text-align: left; margin-top: 5px; border-left: 4px solid gold; }}
</style>
""", unsafe_allow_html=True)

# 4. MOTOR DE DADOS
def buscar_70(q):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=70&locale=pt-PT"
        return requests.get(url, timeout=10).json().get('results', [])
    except: return []

def render_cartao(an, habitat, prefixo, i, modo_crio=False):
    random.seed(an['id'])
    bio = {"ali": random.choice(["🥩 Carnívoro", "🥗 Herbívoro", "🍕 Omnívoro"]), 
           "rep": random.choice(["🥚 Ovíparo", "🍼 Vivíparo"]),
           "con": random.choice(["✅ Seguro", "⚠️ Vulnerável", "🚨 Em Perigo"])}
    
    st.markdown(f"""
    <div class='cartao-cidadao'>
        <img src='{an.get('default_photo', {{}}).get('medium_url', '')}' style='width:100%; height:160px; object-fit:cover; border-radius:12px;'>
        <h4 style='margin:10px 0;'>{an.get('preferred_common_name', an['name']).title()}</h4>
        <div class='campo-cidadao'><b>🏠 Habitat:</b> {habitat}</div>
        <div class='campo-cidadao'><b>🍖 Dieta:</b> {bio['ali']}</div>
        <div class='campo-cidadao'><b>🐣 Reprod.:</b> {bio['rep']}</div>
    """, unsafe_allow_html=True)
    if is_mestre: st.markdown(f"<div class='campo-cidadao' style='border-color:#00ff00;'><b>🛡️ Estado:</b> {bio['con']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if not modo_crio:
        if st.button(f"Capturar", key=f"{prefixo}_{i}"):
            if len(st.session_state.zoo) < LIMITE_ZOO:
                st.session_state.zoo.append(an); st.rerun()
    else:
        if st.button(f"Descongelar", key=f"unfreeze_{i}"):
            if len(st.session_state.zoo) < LIMITE_ZOO:
                st.session_state.zoo.append(st.session_state.criogenia_storage.pop(i)); st.rerun()

# 5. SIDEBAR COM NAVEGAÇÃO COMPLETA
with st.sidebar:
    st.title("🌍 MundoVivo")
    st.write(f"🏆 {st.session_state.pontos} Pts | 🐾 {len(st.session_state.zoo)}/{LIMITE_ZOO}")
    
    nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"]
    
    if is_mega:
        st.markdown("---")
        st.subheader("💎 MEGA PREMIUM")
        nav = ["🧬 Fusão & Scanner", "🚁 Resgates", "🛰️ Radar", "🪐 Eco-Simulador", "💊 Criogenia"] + nav
    
    aba = st.radio("Navegação", nav)

# 6. LOGICA DAS ABAS
if aba == "🌍 Países":
    p = st.selectbox("Escolher País", ["Portugal", "Brasil", "Japão", "Austrália", "Angola", "EUA", "França"])
    animais = buscar_70(p)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: render_cartao(an, p, "pa", i)

elif aba == "🌲 Florestas":
    f = st.selectbox("Escolher Bioma", ["Amazónia", "Savana", "Taiga", "Selva Tropical", "Pantanal"])
    animais = buscar_70(f)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: render_cartao(an, f, "fl", i)

elif aba == "🌊 Oceanos":
    o = st.selectbox("Escolher Zona", ["Recife de Coral", "Oceano Profundo", "Ártico", "Mar Mediterrâneo"])
    animais = buscar_70(o)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: render_cartao(an, o, "oc", i)

elif aba == "🚁 Resgates" and is_mega:
    st.title("🚁 Missões de Resgate")
    for idx, res in enumerate(st.session_state.resgates_ativos):
        c1, c2 = st.columns([3, 1])
        c1.warning(f"🚨 EMERGÊNCIA: {res}")
        if c2.button("SALVAR", key=f"res_{idx}"):
            st.session_state.pontos += 150
            lista_novos = ["Koala em perigo", "Lince ferido", "Tartaruga presa", "Águia sem ninho", "Lobo perdido"]
            st.session_state.resgates_ativos[idx] = random.choice(lista_novos)
            st.rerun()

elif aba == "⭐ Coleção":
    st.header("🐾 Teu Zoo")
    if st.button("🗑️ APAGAR TODO O ZOO"):
        st.session_state.zoo = []; st.rerun()
    cols = st.columns(3)
    for i, an in enumerate(st.session_state.zoo):
        with cols[i%3]:
            render_cartao(an, "Meu Zoo", "col", i)
            if st.button(f"Eliminar", key=f"del_{i}"):
                st.session_state.zoo.pop(i); st.rerun()

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    st.session_state.nome_zoologo = st.text_input("Nome", st.session_state.nome_zoologo)
    st.session_state.codigo = st.text_input("Código Premium", type="password")
    st.session_state.codigo_perm = st.text_input("Código Mega", type="password")
    st.session_state.codigo_crio = st.text_input("Código Criogenia", type="password")
    st.session_state.cor_fundo = st.selectbox("Cor de Fundo", ["#0b1117", "#ffffff", "#001f3f", "#002b1b"])
    st.session_state.luminosidade = st.slider("Luminosidade", 50, 150, st.session_state.luminosidade)
    st.session_state.negrito = st.checkbox("Texto em Negrito", value=st.session_state.negrito)
    if st.button("Confirmar Alterações", type="primary"): st.rerun()

elif aba == "💊 Criogenia" and is_mega:
    st.title("💊 Criostase")
    if not is_crio_unlocked: st.error("Acesso Bloqueado. Requer CRIO99.")
    else: st.success("Câmara Ativa. Descongele animais aqui.")

elif aba == "🧬 Fusão & Scanner" and is_mega:
    st.title("🔬 Bio-Lab")
    st.write("Funcionalidade Premium ativa.")

elif aba == "🛰️ Radar" and is_mega:
    st.title("🛰️ Radar Global")
    st.info("A procurar espécies raras...")

elif aba == "🪐 Eco-Simulador" and is_mega:
    st.title("🪐 Simulador Interplanetário")
    st.write("Selecione um animal para testar a sobrevivência em Marte.")
