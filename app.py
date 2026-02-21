import streamlit as st
import requests
import random
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo Ultra 🌍", layout="wide")

# 2. ESTADO DO SISTEMA
chaves_padrao = {
    'zoo': [], 'tanque_fusao': [], 'criogenia_storage': [],
    'codigo': "", 'codigo_perm': "", 'premium_ativo': False, 
    'cor_card': "Preto", 'cor_fundo': "Preto", 'luminosidade': 100, 
    'pontos': 250
}

for chave, valor in chaves_padrao.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

# 3. LÓGICA DE ACESSO E BORDAS
is_premium_normal = st.session_state.codigo == "6626"
is_mega = st.session_state.codigo_perm == "67lucas62"
tem_acesso = is_premium_normal or is_mega

# Definição visual da borda baseada no código
if is_mega:
    estilo_borda = "border: 5px solid; border-image: linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet) 1;"
elif is_premium_normal:
    estilo_borda = "border: 4px solid #ffd700;" # Dourado
else:
    estilo_borda = "border: 4px solid #2ecc71;" # Verde Normal

# 4. DESIGN CSS E ANIMAÇÕES
mapa_cores = {"Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", "Verde": "#002b1b", "Cinza": "#262730"}
app_bg = mapa_cores.get(st.session_state.cor_fundo, "#0b1117")
card_bg = mapa_cores.get(st.session_state.cor_card, "#1a1c23")

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; filter: brightness({st.session_state.luminosidade}%); color: white; }}
    
    /* CARTÃO VERTICAL */
    .cartao-cidadao {{
        background: {card_bg}; color: white; border-radius: 15px; padding: 15px; 
        text-align: center; {estilo_borda} min-height: 520px;
        display: flex; flex-direction: column; justify-content: space-between;
        margin-bottom: 20px;
    }}
    .img-container img {{ width: 100%; border-radius: 10px; height: 220px; object-fit: cover; }}
    
    /* ANIMAÇÃO DE RAIOS BRILHANTES (MODO PREMIUM) */
    @keyframes rays {{
        0% {{ box-shadow: 0 0 20px rgba(255, 215, 0, 0.2), 0 0 40px rgba(255, 215, 0, 0.1) inset; }}
        50% {{ box-shadow: 0 0 50px rgba(255, 215, 0, 0.6), 0 0 80px rgba(255, 215, 0, 0.3) inset; }}
        100% {{ box-shadow: 0 0 20px rgba(255, 215, 0, 0.2), 0 0 40px rgba(255, 215, 0, 0.1) inset; }}
    }}

    .premium-panel {{
        background: radial-gradient(circle, rgba(255,215,0,0.15) 0%, rgba(0,0,0,0) 70%);
        padding: 20px; border-radius: 20px; text-align: center;
        animation: rays 3s infinite; border: 1px solid rgba(255, 215, 0, 0.3);
        margin-bottom: 20px;
    }}
    
    .diamond {{ font-size: 50px; text-shadow: 0 0 20px #fff; }}
    .premium-text {{ color: #ffd700; font-weight: bold; font-size: 1.2em; text-transform: uppercase; letter-spacing: 2px; }}
    
    .info-bio {{ background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; font-size: 0.85em; text-align: left; margin: 10px 0; border-left: 3px solid #2ecc71; }}
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE BUSCA
def buscar_natureza(query):
    if not query: return []
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={query}&taxon_id=1&per_page=12&locale=pt-PT"
        return requests.get(url, timeout=10).json().get('results', [])
    except: return []

def render_cartao(an, key_prefix):
    nome = an.get('preferred_common_name', an.get('name', 'Espécie')).title()
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/200")
    classe = an.get('iconic_taxon_name', 'Desconhecido')
    
    st.markdown(f"""
    <div class="cartao-cidadao">
        <div class="img-container"><img src="{foto}"></div>
        <h4 style="margin: 10px 0; min-height: 50px;">{nome}</h4>
        <div class="info-bio">
            <b>🧬 Classe:</b> {classe}<br>
            <b>🏠 Habitat:</b> Nativo<br>
            <b>🍼 Reprodução:</b> Biológica<br>
            <b>🍖 Alimentação:</b> Dieta Natural
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.premium_ativo and tem_acesso:
        st.markdown('<div style="color:#ffd700; font-weight:bold; font-size:0.75em;">🛡️ STATUS: MONITORIZADO</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Capturar", key=f"cap_{key_prefix}_{an['id']}"):
            st.session_state.zoo.append(an)
            st.toast(f"{nome} guardado!")
    with c2:
        if st.session_state.premium_ativo and tem_acesso:
            if st.button("🧬 DNA", key=f"dna_{key_prefix}_{an['id']}"):
                st.session_state.tanque_fusao.append(an)
                st.toast("Sequência de DNA obtida!")

# 6. SIDEBAR COM ANIMAÇÃO PREMIUM
with st.sidebar:
    st.title("🌍 MundoVivo")
    
    if tem_acesso:
        st.session_state.premium_ativo = st.toggle("🔄 ATIVAR MODO VIP", value=st.session_state.premium_ativo)
        
        if st.session_state.premium_ativo:
            # Painel com Raios, Diamante e Texto
            st.markdown("""
                <div class="premium-panel">
                    <div class="diamond">💎</div>
                    <div class="premium-text">TORNOU-SE PREMIUM</div>
                </div>
            """, unsafe_allow_html=True)
            nav = ["🔬 Laboratório", "🧬 Fusão", "🚁 Missões", "⚙️ Definições"]
        else:
            nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    else:
        nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    
    aba = st.radio("Navegação", nav)

# 7. LÓGICA DE ABAS
if aba in ["🌍 Países", "🌲 Florestas", "🌊 Oceanos"]:
    if aba == "🌍 Países":
        escolha = st.selectbox("Explorar País:", ["Portugal", "Brasil", "Angola", "Japão", "Austrália"])
    elif aba == "🌲 Florestas":
        escolha = st.selectbox("Explorar Bioma:", ["Amazónia", "Selva do Congo", "Taiga", "Mata Atlântica"])
    else:
        escolha = st.selectbox("Explorar Mar:", ["Oceano Atlântico", "Oceano Pacífico", "Mar Vermelho", "Mar Mediterrâneo"])
    
    res = buscar_natureza(escolha)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_cartao(an, aba)

elif aba == "🔬 Laboratório":
    st.title("🔬 Centro de Análise")
    query = st.text_input("🔍 Pesquisa Global:", placeholder="Ex: Pantera, Orca...")
    if query:
        res = buscar_natureza(query)
        cols = st.columns(3)
        for i, an in enumerate(res):
            with cols[i%3]: render_cartao(an, "pesq")
    st.divider()
    if st.session_state.zoo:
        st.subheader("🦁 Espécimes Capturados")
        cols_zoo = st.columns(3)
        for i, an in enumerate(st.session_state.zoo):
            with cols_zoo[i%3]: render_cartao(an, "zoo_lab")

elif aba == "🧬 Fusão":
    st.title("🧬 Engenharia Genética")
    if len(st.session_state.tanque_fusao) >= 2:
        a1 = st.selectbox("Matriz A", st.session_state.tanque_fusao, format_func=lambda x: x.get('preferred_common_name', x['name']))
        a2 = st.selectbox("Matriz B", st.session_state.tanque_fusao, format_func=lambda x: x.get('preferred_common_name', x['name']))
        if st.button("FUNDIR"):
            h = f"{a1['name'][:4]}{a2['name'][-3:]}".upper()
            st.success(f"HÍBRIDO CRIADO: {h}")
            st.balloons()
    else: st.warning("Necessita de 2 amostras de DNA.")

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições de Sistema")
    st.session_state.codigo = st.text_input("Código Premium", value=st.session_state.codigo, type="password")
    st.session_state.codigo_perm = st.text_input("Código Mega", value=st.session_state.codigo_perm, type="password")
    st.session_state.cor_fundo = st.selectbox("Fundo", list(mapa_cores.keys()), index=list(mapa_cores.keys()).index(st.session_state.cor_fundo))
    st.session_state.luminosidade = st.slider("Brilho", 50, 150, st.session_state.luminosidade)
    if st.button("Guardar Alterações"): st.rerun()
