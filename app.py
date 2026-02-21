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

# 4. DESIGN CSS (TEXTO AUMENTADO)
mapa_cores = {"Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", "Verde": "#002b1b", "Cinza": "#262730"}
app_bg = mapa_cores.get(st.session_state.cor_fundo, "#0b1117")
card_bg = mapa_cores.get(st.session_state.cor_card, "#1a1c23")

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; filter: brightness({st.session_state.luminosidade}%); color: white; }}
    
    .cartao-cidadao {{
        background: {card_bg}; color: white; border-radius: 20px; padding: 25px; 
        text-align: center; {estilo_borda} 
        min-height: 750px; 
        display: flex; flex-direction: column; justify-content: space-between; 
        margin-bottom: 30px;
    }}
    
    .nome-comum {{ font-size: 2.2em; font-weight: 900; margin-bottom: 2px; color: #ffffff; text-transform: uppercase; }}
    .nome-cientifico {{ font-size: 1.4em; font-style: italic; color: #1DB954; margin-bottom: 15px; display: block; letter-spacing: 1px; }}
    
    .img-box img {{ width: 100%; height: 210px; object-fit: cover; border-radius: 15px; }}
    
    .info-bio {{ background: rgba(255,255,255,0.08); padding: 20px; border-radius: 12px; font-size: 1.2em; text-align: left; line-height: 1.5; }}
    .stats-vip {{ font-size: 1.25em; text-align: left; color: #ffd700; font-family: 'Arial Black', Gadget, sans-serif; background: rgba(0,0,0,0.4); padding: 15px; border-radius: 8px; border-left: 5px solid #ffd700; }}
    
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
    
    # Botões maiores com ícones
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"📥 CAPTURAR {nome_comum.upper()}", key=f"c_{key_prefix}_{an['id']}", use_container_width=True):
            st.session_state.zoo.append(an); st.toast(f"{nome_comum} guardado!")
    with c2:
        if st.session_state.premium_ativo and tem_acesso:
            if st.button("🧬 EXTRAIR DNA", key=f"d_{key_prefix}_{an['id']}", use_container_width=True):
                st.session_state.tanque_fusao.append(an); st.toast("DNA Sequenciado!")

# ... (Manter o restante das lógicas de Sidebar, Países, Florestas, Oceanos e Definições conforme o código anterior)

# [Abaixo está a parte final da lógica de navegação]
with st.sidebar:
    st.title("🌍 MundoVivo")
    if tem_acesso:
        st.session_state.premium_ativo = st.toggle("🔄 ATIVAR MODO VIP", value=st.session_state.premium_ativo)
    
    nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    if st.session_state.premium_ativo and tem_acesso:
        nav = ["🔬 Laboratório", "🧬 Fusão", "🚁 Missões", "📊 Estatísticas", "❄️ Criogenia", "⚙️ Definições"]
    aba = st.radio("Navegação", nav)

# Lógica das abas segue a mesma estrutura, chamando render_cartao com mostrar_stats=True no laboratório.
