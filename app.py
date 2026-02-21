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

if is_mega:
    estilo_borda = "border: 6px solid; border-image: linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet) 1;"
    linha_separadora = "background: linear-gradient(90deg, red, orange, yellow, green, blue, indigo, violet); height: 5px; border-radius: 5px; margin: 15px 0;"
elif is_premium_normal:
    estilo_borda = "border: 5px solid #ffd700;"
    linha_separadora = "background: #ffd700; height: 3px; margin: 15px 0;"
else:
    estilo_borda = "border: 5px solid #2ecc71;"
    linha_separadora = "background: #2ecc71; height: 2px; margin: 15px 0;"

# 4. DESIGN CSS (TEXTO GIGANTE E IMAGEM ORIGINAL)
mapa_cores = {"Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", "Verde": "#002b1b", "Cinza": "#262730"}
app_bg = mapa_cores.get(st.session_state.cor_fundo, "#0b1117")
card_bg = mapa_cores.get(st.session_state.cor_card, "#1a1c23")

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; filter: brightness({st.session_state.luminosidade}%); color: white; }}
    
    .cartao-cidadao {{
        background: {card_bg}; color: white; border-radius: 20px; padding: 25px; 
        text-align: center; {estilo_borda} min-height: 750px;
        display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 30px;
    }}
    
    .nome-comum {{ font-size: 2.2em; font-weight: 900; color: #ffffff; text-transform: uppercase; }}
    .nome-cientifico {{ font-size: 1.4em; font-style: italic; color: #1DB954; margin-bottom: 15px; display: block; }}
    
    .img-box img {{ width: 100%; height: 210px; object-fit: cover; border-radius: 15px; }}
    
    .info-bio {{ background: rgba(255,255,255,0.08); padding: 20px; border-radius: 12px; font-size: 1.2em; text-align: left; line-height: 1.5; }}
    .stats-vip {{ font-size: 1.25em; text-align: left; color: #ffd700; font-family: 'Arial Black', sans-serif; background: rgba(0,0,0,0.4); padding: 15px; border-radius: 8px; border-left: 5px solid #ffd700; }}
    
    @keyframes fly {{ from {{ transform: translateX(-150%); }} to {{ transform: translateX(250%); }} }}
    .helicoptero {{ font-size: 90px; position: fixed; top: 25%; z-index: 9999; animation: fly 4s linear forwards; }}
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE BUSCA
def buscar(q):
    try: return requests.get(f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=12&locale=pt-PT").json().get('results', [])
    except: return []

def render_cartao(an, key_prefix, mostrar_stats=False):
    nome_comum = an.get('preferred_common_name', 'Desconhecido').title()
    nome_cientifico = an.get('name', 'N/A')
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    
    if 'vel' not in an:
        an['vel'] = random.randint(5, 120)
        an['vida'] = random.randint(2, 90)
        an['peso'] = random.randint(2, 5000) if an.get('iconic_taxon_name') == 'Mammalia' else random.randint(1, 80)

    st.markdown(f"""
    <div class="cartao-cidadao">
        <div class="img-box"><img src="{foto}"></div>
        <div>
            <span class="nome-comum">{nome_comum}</span>
            <span class="nome-cientifico">({nome_cientifico})</span>
        </div>
        <div class="info-bio">
            <b>🧬 CLASSE:</b> {an.get('iconic_taxon_name', 'Taxon').upper()}<br>
            <b>🏠 HABITAT:</b> ECOSSISTEMA NATURAL<br>
            <b>🍼 REPRODUÇÃO:</b> BIOLÓGICA
        </div>
    """, unsafe_allow_html=True)
    
    if mostrar_stats and st.session_state.premium_ativo:
        st.markdown(f'<div style="{linha_separadora}"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="stats-vip">
            <b>📊 BIOMETRIA VIP:</b><br>
            🚀 VELOCIDADE: {an['vel']} KM/H<br>
            ⏳ LONGEVIDADE: {an['vida']} ANOS<br>
            ⚖️ PESO MÉDIO: {an['peso']} KG
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"📥 CAPTURAR", key=f"c_{key_prefix}_{an['id']}", use_container_width=True):
            st.session_state.zoo.append(an); st.toast(f"{nome_comum} guardado!")
    with c2:
        if st.session_state.premium_ativo and tem_acesso:
            if st.button("🧬 DNA", key=f"d_{key_prefix}_{an['id']}", use_container_width=True):
                st.session_state.tanque_fusao.append(an); st.toast("DNA extraído!")

# 6. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    if tem_acesso:
        st.session_state.premium_ativo = st.toggle("🔄 MODO VIP", value=st.session_state.premium_ativo)
    
    nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    if st.session_state.premium_ativo and tem_acesso:
        nav = ["🔬 Laboratório", "🧬 Fusão", "🚁 Missões", "📊 Estatísticas", "❄️ Criogenia", "⚙️ Definições"]
    aba = st.radio("Navegação", nav)

# 7. CONTEÚDO DAS ABAS
if aba == "🌍 Países":
    p = st.selectbox("Escolha o País:", ["Brasil", "Portugal", "México", "Finlândia", "Rússia", "Maldivas", "Madagáscar"])
    res = buscar(p)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_cartao(an, "pais")

elif aba == "🌲 Florestas":
    f = st.selectbox("Escolha a Floresta/Selva:", ["Amazónia", "Selva do Congo", "Floresta Negra", "Taiga Siberiana", "Daintree Rainforest", "Selva Lacandona", "Mata Atlântica", "Borealis"])
    res = buscar(f)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_cartao(an, "flor")

elif aba == "🌊 Oceanos":
    o = st.selectbox("Escolha o Oceano:", ["Oceano Atlântico", "Oceano Pacífico", "Oceano Índico", "Oceano Ártico", "Oceano Antártico", "Mar Mediterrâneo", "Mar Vermelho", "Mar das Caraíbas"])
    res = buscar(o)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_cartao(an, "oce")

elif aba == "🔬 Laboratório":
    query = st.text_input("🔍 Pesquisar Espécie:")
    res = buscar(query) if query else []
    if res:
        cols = st.columns(3)
        for i, an in enumerate(res):
            with cols[i%3]: render_cartao(an, "lab", mostrar_stats=True)
    if st.session_state.zoo:
        st.divider()
        st.subheader("🦁 O Teu Zoo")
        cols_zoo = st.columns(3)
        for i, an in enumerate(st.session_state.zoo):
            with cols_zoo[i%3]: render_cartao(an, "zoo", mostrar_stats=True)

elif aba == "❄️ Criogenia":
    if not is_crio_auth: st.error("Insira o código 'crio969' nas Definições.")
    else:
        st.success("SISTEMA ONLINE")
        an_crio = st.selectbox("Animal:", st.session_state.zoo, format_func=lambda x: x.get('name', 'N/A'))
        if st.button("❄️ CONGELAR"):
            st.session_state.criogenia_storage.append(an_crio)
            st.session_state.zoo.remove(an_crio); st.rerun()

elif aba == "🚁 Missões":
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/80/World_map_-_low_resolution.svg")
    if st.button("🚀 INICIAR RESGATE"):
        st.markdown('<audio autoplay><source src="https://www.soundjay.com/transportation/helicopter-fly-over-1.mp3"></audio>', unsafe_allow_html=True)
        st.markdown('<div class="helicoptero">🚁</div>', unsafe_allow_html=True)
        time.sleep(4); st.session_state.pontos += 100; st.rerun()

elif aba == "📊 Estatísticas":
    st.table([{"Animal": a.get('name'), "Vel": f"{a.get('vel')}km/h", "Peso": f"{a.get('peso')}kg"} for a in st.session_state.zoo])

elif aba == "⚙️ Definições":
    st.session_state.codigo = st.text_input("Premium (6626)", value=st.session_state.codigo, type="password")
    st.session_state.codigo_perm = st.text_input("Mega (67lucas62)", value=st.session_state.codigo_perm, type="password")
    st.session_state.codigo_crio = st.text_input("Crio (crio969)", value=st.session_state.codigo_crio, type="password")
    st.session_state.cor_fundo = st.selectbox("Fundo", list(mapa_cores.keys()))
    st.session_state.luminosidade = st.slider("Brilho", 50, 150, 100)
    if st.button("Guardar"): st.rerun()
