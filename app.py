import streamlit as st
import requests
import random
import time

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo Ultra 🌍", layout="wide")

# 2. ESTADO DO SISTEMA
chaves_padrao = {
    'zoo': [], 'tanque_fusao': [], 'criogenia_storage': [],
    'codigo': "", 'codigo_perm': "", 'codigo_crio': "",
    'premium_ativo': False, 'cor_card': "Preto", 'cor_fundo': "Preto", 
    'luminosidade': 100, 'pontos': 250, 'missoes_concluidas': 0
}

for chave, valor in chaves_padrao.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

# 3. LÓGICA DE ACESSO E ESTILOS
is_premium_normal = st.session_state.codigo == "6626"
is_mega = st.session_state.codigo_perm == "67lucas62"
is_crio_auth = st.session_state.codigo_crio == "crio969"
tem_acesso = is_premium_normal or is_mega

# Definição das Bordas e Linhas Separadoras do Cartão
if is_mega:
    estilo_borda = "border: 5px solid; border-image: linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet) 1;"
    linha_separadora = "background: linear-gradient(90deg, red, orange, yellow, green, blue, indigo, violet); height: 4px; border-radius: 2px; margin: 12px 0;"
elif is_premium_normal:
    estilo_borda = "border: 4px solid #ffd700;"
    linha_separadora = "background: #ffd700; height: 2px; margin: 12px 0;"
else:
    estilo_borda = "border: 4px solid #2ecc71;"
    linha_separadora = "background: #2ecc71; height: 1px; margin: 12px 0;"

# 4. DESIGN CSS
mapa_cores = {"Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", "Verde": "#002b1b", "Cinza": "#262730"}
app_bg = mapa_cores.get(st.session_state.cor_fundo, "#0b1117")
card_bg = mapa_cores.get(st.session_state.cor_card, "#1a1c23")

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; filter: brightness({st.session_state.luminosidade}%); color: white; }}
    .cartao-cidadao {{
        background: {card_bg}; color: white; border-radius: 15px; padding: 15px; 
        text-align: center; {estilo_borda} min-height: 560px;
        display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 20px;
    }}
    .info-bio {{ background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; font-size: 0.85em; text-align: left; }}
    .stats-vip {{ font-size: 0.85em; text-align: left; color: #ffd700; font-family: monospace; }}
    @keyframes fly {{ from {{ transform: translateX(-150%); }} to {{ transform: translateX(250%); }} }}
    .helicoptero {{ font-size: 80px; position: fixed; top: 20%; z-index: 9999; animation: fly 4s linear forwards; }}
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE BUSCA
def buscar(q):
    try: return requests.get(f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=12&locale=pt-PT").json().get('results', [])
    except: return []

def render_cartao(an, key_prefix, mostrar_stats=False):
    nome = an.get('preferred_common_name', an.get('name', 'Espécie')).title()
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/200")
    
    if 'vel' not in an:
        an['vel'] = random.randint(5, 120)
        an['vida'] = random.randint(2, 85)
        an['peso'] = random.randint(1, 4500) if an.get('iconic_taxon_name') == 'Mammalia' else random.randint(1, 60)

    st.markdown(f"""
    <div class="cartao-cidadao">
        <img src="{foto}" style="width:100%; height:210px; object-fit:cover; border-radius:10px;">
        <h4 style="margin:10px 0;">{nome}</h4>
        <div class="info-bio">
            <b>🧬 Classe:</b> {an.get('iconic_taxon_name', 'Bio')}<br>
            <b>🏠 Habitat:</b> Selvagem<br>
            <b>🍼 Reprodução:</b> Biológica
        </div>
    """, unsafe_allow_html=True)
    
    if mostrar_stats and st.session_state.premium_ativo:
        st.markdown(f'<div style="{linha_separadora}"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="stats-vip">
            ⚡ Velocidade: {an['vel']} km/h<br>
            ⏳ Tempo de Vida: {an['vida']} anos<br>
            ⚖️ Peso: {an['peso']} kg
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Capturar", key=f"c_{key_prefix}_{an['id']}"):
            st.session_state.zoo.append(an); st.toast(f"{nome} guardado!")
    with c2:
        if st.session_state.premium_ativo and tem_acesso:
            if st.button("🧬 DNA", key=f"d_{key_prefix}_{an['id']}"):
                st.session_state.tanque_fusao.append(an); st.toast("DNA extraído!")

# 6. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    if tem_acesso:
        st.session_state.premium_ativo = st.toggle("🔄 MODO VIP", value=st.session_state.premium_ativo)
    
    if st.session_state.premium_ativo and tem_acesso:
        nav = ["🔬 Laboratório", "🧬 Fusão", "🚁 Missões", "📊 Estatísticas", "❄️ Criogenia", "⚙️ Definições"]
    else:
        nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    
    aba = st.radio("Navegação", nav)

# 7. LOGICA DE ABAS
if aba == "🌍 Países":
    p = st.selectbox("País:", ["Brasil", "Portugal", "México", "Finlândia", "Rússia", "Maldivas", "Madagáscar"])
    res = buscar(p)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_cartao(an, "pais")

elif aba == "🌲 Florestas":
    f = st.selectbox("Floresta/Selva:", ["Amazónia", "Selva do Congo", "Floresta Negra", "Taiga Siberiana", "Daintree Rainforest", "Selva Lacandona", "Mata Atlântica", "Borealis"])
    res = buscar(f)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_cartao(an, "flor")

elif aba == "🌊 Oceanos":
    o = st.selectbox("Oceano/Mar:", ["Oceano Atlântico", "Oceano Pacífico", "Oceano Índico", "Oceano Ártico", "Oceano Antártico", "Mar Mediterrâneo", "Mar Vermelho", "Mar das Caraíbas"])
    res = buscar(o)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_cartao(an, "oce")

elif aba == "🔬 Laboratório":
    st.title("🔬 Centro de Pesquisa")
    query = st.text_input("🔍 Pesquisa Global (Ex: Tigre):")
    res = buscar(query) if query else []
    if res:
        cols = st.columns(3)
        for i, an in enumerate(res):
            with cols[i%3]: render_cartao(an, "lab", mostrar_stats=True)
    st.divider()
    if st.session_state.zoo:
        st.subheader("🦁 O Teu Zoo")
        cols_zoo = st.columns(3)
        for i, an in enumerate(st.session_state.zoo):
            with cols_zoo[i%3]: render_cartao(an, "zoo", mostrar_stats=True)

elif aba == "❄️ Criogenia":
    st.title("❄️ Unidade Criogénica")
    if not is_crio_auth:
        st.error("ACESSO NEGADO. Insira o código da Crio nas Definições.")
    else:
        st.success("SISTEMA DE CRIOSTASE ONLINE")
        if st.session_state.zoo:
            an_crio = st.selectbox("Animal para Congelar:", st.session_state.zoo, format_func=lambda x: x.get('name'))
            if st.button("❄️ INICIAR CONGELAMENTO"):
                st.session_state.criogenia_storage.append(an_crio)
                st.session_state.zoo.remove(an_crio); st.rerun()
        if st.session_state.criogenia_storage:
            st.divider()
            st.subheader("🧊 Animais Congelados")
            for a in st.session_state.criogenia_storage:
                st.info(f"Em suspensão: {a.get('name')}")

elif aba == "📊 Estatísticas":
    st.title("📊 Painel VIP")
    if st.session_state.zoo:
        st.table([{"Espécie": a.get('name'), "Velocidade": f"{a.get('vel')} km/h", "Peso": f"{a.get('peso')} kg", "Longevidade": f"{a.get('vida')} anos"} for a in st.session_state.zoo])

elif aba == "🚁 Missões":
    st.title("🚁 Resgate")
    if st.button("🚀 INICIAR OPERAÇÃO"):
        st.markdown('<audio autoplay><source src="https://www.soundjay.com/transportation/helicopter-fly-over-1.mp3"></audio>', unsafe_allow_html=True)
        st.markdown('<div class="helicoptero">🚁</div>', unsafe_allow_html=True)
        time.sleep(4); st.session_state.pontos += 100; st.rerun()

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    st.session_state.codigo = st.text_input("Código Premium", value=st.session_state.codigo, type="password")
    st.session_state.codigo_perm = st.text_input("Código Mega", value=st.session_state.codigo_perm, type="password")
    st.session_state.codigo_crio = st.text_input("Código Crio (crio969)", value=st.session_state.codigo_crio, type="password")
    st.session_state.cor_fundo = st.selectbox("Fundo", list(mapa_cores.keys()))
    st.session_state.luminosidade = st.slider("Brilho", 50, 150, 100)
    if st.button("Guardar"): st.rerun()
