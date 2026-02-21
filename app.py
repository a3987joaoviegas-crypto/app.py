import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo Ultra 🌍", layout="wide")

# 2. ESTADO DO SISTEMA
chaves_padrao = {
    'zoo': [], 'tanque_fusao': [], 'codigo': "", 'codigo_perm': "", 
    'premium_ativado_em': None, 'premium_ativo': False,
    'cor_fundo': "Preto", 'nome_zoologo': "Explorador", 'idioma': "pt-PT",
    'luminosidade': 100, 'negrito': False, 'pontos': 250,
    'resgates_ativos': ["Tigre ferido", "Panda faminto", "Baleia encalhada"]
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

# Expiração de 24h
if is_premium and st.session_state.premium_ativado_em:
    if datetime.now() > st.session_state.premium_ativado_em + timedelta(hours=24):
        st.session_state.codigo = ""
        st.session_state.premium_ativo = False

# 4. DESIGN CSS
mapa_cores = {"Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", "Verde": "#002b1b"}
app_bg = mapa_cores.get(st.session_state.cor_fundo, "#0b1117")

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; filter: brightness({st.session_state.luminosidade}%); }}
    .cartao-cidadao {{
        background: #1a1c23; color: white; border-radius: 15px; padding: 15px;
        text-align: center; border: 3px solid #2ecc71; margin-bottom: 10px;
    }}
    .lab-premium-box {{ 
        background: linear-gradient(135deg, #001f3f, #000); 
        border: 2px solid #00ffff; border-radius: 15px; padding: 20px; color: white;
    }}
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE BUSCA E INTERFACE
def buscar_animais(q):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=12&locale={st.session_state.idioma}"
        return requests.get(url, timeout=10).json().get('results', [])
    except: return []

def render_cartao_completo(an, local):
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/150")
    nome = an.get('preferred_common_name', an.get('name', 'Espécie')).title()
    
    st.markdown(f"""
    <div class="cartao-cidadao">
        <img src="{foto}" style="width:100%; border-radius:10px; height:140px; object-fit:cover;">
        <h4>{nome}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"Capturar", key=f"cap_{local}_{an['id']}"):
            st.session_state.zoo.append(an)
            st.rerun()
    with c2:
        # BOTÃO NOVO: Só aparece se o interruptor Premium estiver ON
        if st.session_state.premium_ativo and tem_acesso:
            if st.button(f"🧬 Fundir", key=f"fus_{local}_{an['id']}"):
                st.session_state.tanque_fusao.append(an)
                st.toast(f"{nome} enviado para o Tanque de Fusão!")

# 6. INTERRUPTOR PREMIUM (O OVO)
if tem_acesso:
    _, col_toggle = st.columns([5, 1])
    with col_toggle:
        st.session_state.premium_ativo = st.toggle("💎 PREMIUM", value=st.session_state.premium_ativo)

# 7. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    if st.session_state.premium_ativo and tem_acesso:
        nav = ["🔬 Lab: Fusão e Stats", "🚁 Resgates", "⚙️ Definições"]
    else:
        nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"]
    aba = st.radio("Navegação", nav)

# 8. ABAS
if aba in ["🌍 Países", "🌲 Florestas", "🌊 Oceanos"]:
    st.title(f"🔍 Explorar {aba}")
    locais = {"🌍 Países": "Portugal", "🌲 Florestas": "Amazónia", "🌊 Oceanos": "Pacífico"}
    escolha = st.selectbox("Mudar Local:", [locais[aba], "Brasil", "África", "Ártico"])
    res = buscar_animais(escolha)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_cartao_completo(an, aba)

elif aba == "🔬 Laboratório":
    st.title("🔬 Laboratório de Observação")
    if st.session_state.zoo:
        an = st.selectbox("Selecionar da Coleção:", st.session_state.zoo, format_func=lambda x: x.get('name'))
        render_cartao_completo(an, "lab_gratis")
    else: st.write("O Zoo está vazio.")

elif aba == "🔬 Lab: Fusão e Stats":
    st.title("🔬 Centro Bio-Genético Premium")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='lab-premium-box'><h3>🧬 Tanque de Fusão</h3>", unsafe_allow_html=True)
        if len(st.session_state.tanque_fusao) >= 2:
            n1 = st.selectbox("DNA 1", st.session_state.tanque_fusao, format_func=lambda x: x.get('name'), key="dna1")
            n2 = st.selectbox("DNA 2", st.session_state.tanque_fusao, format_func=lambda x: x.get('name'), key="dna2")
            if st.button("FUNDIR ESPÉCIMES"):
                nome1 = n1.get('preferred_common_name', n1['name'])
                nome2 = n2.get('preferred_common_name', n2['name'])
                st.success(f"Híbrido Estável: {nome1[:4]}{nome2[-3:].lower()}!")
        else:
            st.info(f"O Tanque tem {len(st.session_state.tanque_fusao)}/2 animais. Envia mais animais usando o botão 'Fundir' nos cartões!")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with c2:
        st.markdown("<div class='lab-premium-box'><h3>📊 Estatísticas Reais</h3>", unsafe_allow_html=True)
        st.write(f"🐾 No Zoo: {len(st.session_state.zoo)}")
        st.write(f"🧬 No Tanque: {len(st.session_state.tanque_fusao)}")
        st.write(f"🏆 Pontos: {st.session_state.pontos}")
        st.markdown("</div>", unsafe_allow_html=True)

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    st.session_state.codigo = st.text_input("Código Premium", value=st.session_state.codigo, type="password")
    st.session_state.codigo_perm = st.text_input("Código Mega", value=st.session_state.codigo_perm, type="password")
    st.session_state.cor_fundo = st.selectbox("Fundo", list(mapa_cores.keys()))
    st.session_state.luminosidade = st.slider("Brilho", 50, 150, st.session_state.luminosidade)
    if st.button("Guardar"): st.rerun()
