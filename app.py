import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. ESTADO DO SISTEMA
chaves = {
    'zoo': [], 'criogenia_storage': [],
    'codigo_24h': "", 'codigo_mega': "", 'codigo_crio': "", 
    'codigo_neon': "", 'codigo_diamante': "", 'premium_ativo': False, 
    'cor_fundo_user': "#0b1117", 'cor_card_user': "#1a1c23",
    'luminosidade': 100, 'inicio_premium': None,
    'ultima_expiracao': None 
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# 2. LÓGICA DE ACESSO (TRAVA DE 1 SEMANA PARA O CÓDIGO 6626)
is_mega = st.session_state.codigo_mega == "67lucas62"
is_neon = st.session_state.codigo_neon == "6676neon7secret"
is_diamante = st.session_state.codigo_diamante == "77daimond8secret"

is_premium_normal = False
pode_ativar_normal = True
tempo_espera = None

# Verificação da trava de 1 semana (Aplica-se ao código 6626)
if st.session_state.ultima_expiracao:
    passou = datetime.now() - st.session_state.ultima_expiracao
    if passou < timedelta(weeks=1):
        pode_ativar_normal = False
        tempo_espera = timedelta(weeks=1) - passou

# Ativação do Premium Normal 24h
if st.session_state.codigo_24h == "6626":
    if pode_ativar_normal:
        is_premium_normal = True
        if st.session_state.inicio_premium is None:
            st.session_state.inicio_premium = datetime.now()
    else:
        is_premium_normal = False # Bloqueado pela trava de 1 semana

# Expiração de 24h (Quando acaba, ativa a trava)
if st.session_state.inicio_premium:
    if datetime.now() - st.session_state.inicio_premium > timedelta(hours=24):
        st.session_state.ultima_expiracao = datetime.now()
        st.session_state.inicio_premium = None
        st.session_state.codigo_24h = ""
        is_premium_normal = False
        st.rerun()

tem_beneficios = is_mega or is_premium_normal

# 3. DESIGN E ESTILOS
cor_borda = "#2ecc71"
linha_vip_css = "border-top: 2px solid #ffd700;"
sombra = "none"

if is_mega:
    cor_borda = "linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet)"
    linha_vip_css = "height: 4px; background: linear-gradient(90deg, red, orange, yellow, green, blue, indigo, violet); border:none;"
elif is_neon:
    cor_borda = "#00ff00"; sombra = "0 0 20px #00ff00"
elif is_diamante:
    cor_borda = "#00d4ff"; sombra = "0 0 25px #00d4ff"
elif is_premium_normal:
    cor_borda = "#ffd700"

st.markdown(f"""
<style>
    .stApp {{ background-color: {st.session_state.cor_fundo_user}; filter: brightness({st.session_state.luminosidade}%); color: white; }}
    .cartao-cidadao {{
        background: {st.session_state.cor_card_user}; border-radius: 15px; padding: 20px; border: 4px solid;
        border-image: {cor_borda if "gradient" in cor_borda else "none"} 1;
        border-color: {cor_borda if "gradient" not in cor_borda else "transparent"};
        box-shadow: {sombra}; min-height: 600px; display: flex; flex-direction: column; margin-bottom: 25px;
    }}
    .img-box img {{ width: 100%; max-height: 180px; object-fit: cover; border-radius: 10px; }}
    .nome-comum {{ font-size: 1.6em; font-weight: 900; text-transform: uppercase; text-align: center; color: white; margin-bottom: 0px; }}
    .nome-cientifico {{ font-size: 1.1em; font-style: italic; color: #1DB954; text-align: center; display: block; margin-bottom: 10px; }}
    .label {{ color: #1DB954; font-weight: bold; font-size: 0.9em; }}
    .campo {{ font-size: 1em; margin: 3px 0; }}
    .separador-vip {{ {linha_vip_css} margin: 15px 0; }}
    .stats-txt {{ color: #ffd700; font-weight: bold; font-family: monospace; font-size: 1.1em; }}
</style>
""", unsafe_allow_html=True)

# 4. FUNÇÕES
def buscar_animais(termo):
    try:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={termo}&taxon_id=1&per_page=9&locale=pt-PT")
        return r.json().get('results', [])
    except: return []

def desenhar_cartao(an, prefixo, modo_resgate=False):
    nome = (an.get('preferred_common_name') or an.get('name') or 'Espécie').title()
    cientifico = an.get('name', 'N/A')
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    random.seed(an['id'])
    habitat = random.choice(["Terrestre", "Aquático", "Aéreo"])
    dieta = random.choice(["Herbívoro", "Carnívoro", "Omnívoro"])
    repro = an.get('iconic_taxon_name', 'Orgânica').upper()

    st.markdown(f"""
    <div class="cartao-cidadao">
        <div style="color:gold; font-weight:bold; text-align:center; font-size:0.8em;">💳 CARTÃO DE CIDADÃO</div>
        <div class="img-box"><img src="{foto}"></div>
        <span class="nome-comum">{nome}</span>
        <span class="nome-cientifico">{cientifico}</span>
        <div class="campo"><span class="label">🌍 AMBIENTE:</span> {habitat}</div>
        <div class="campo"><span class="label">🥩 ALIMENTAÇÃO:</span> {dieta}</div>
        <div class="campo"><span class="label">🍼 REPRODUÇÃO:</span> {repro}</div>
    """, unsafe_allow_html=True)

    if st.session_state.premium_ativo and tem_beneficios:
        st.markdown(f"""<div class="separador-vip"></div>
        <div class="stats-txt">📊 ESTATÍSTICAS VIP<br>🚀 VELOCIDADE: {random.randint(50, 250)} KM/H<br>⚖️ PESO: {random.randint(1, 8000)} KG</div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if modo_resgate:
        if st.button(f"🌀 TRAZER DE VOLTA", key=f"res_{prefixo}_{an['id']}", use_container_width=True):
            st.session_state.zoo.append(an)
            st.session_state.criogenia_storage.remove(an)
            st.success(f"{nome} resgatado!")
            time.sleep(1); st.rerun()
    else:
        if st.button(f"📥 CAPTURAR", key=f"btn_{prefixo}_{an['id']}", use_container_width=True):
            limite = 80 if tem_beneficios else 20
            if len(st.session_state.zoo) < limite:
                st.session_state.zoo.append(an); st.toast(f"{nome} capturado!")
            else: st.error("Zoo cheio!")

# 5. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    if tem_beneficios:
        st.session_state.premium_ativo = st.toggle("MODO VIP", value=st.session_state.premium_ativo)
    
    nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    if st.session_state.premium_ativo and tem_beneficios:
        nav = ["🔬 Laboratório", "🧬 Fusão", "❄️ Criogenia", "🌀 Resgate", "⚙️ Definições"]
    
    aba = st.radio("Menu", nav)

# 6. ABAS
if aba == "🌀 Resgate":
    st.header("🌀 Centro de Resgate")
    if not st.session_state.criogenia_storage: st.info("Câmara vazia.")
    else:
        cols = st.columns(3)
        for i, an in enumerate(st.session_state.criogenia_storage):
            with cols[i%3]: desenhar_cartao(an, "r", modo_resgate=True)

elif aba == "❄️ Criogenia":
    st.header("❄️ Criogenia")
    if st.session_state.zoo:
        alvo = st.selectbox("Congelar:", st.session_state.zoo, format_func=lambda x: x.get('preferred_common_name', 'N/A'))
        if st.button("ENVIAR PARA RESGATE"):
            st.session_state.criogenia_storage.append(alvo)
            st.session_state.zoo.remove(alvo)
            st.success("Enviado para o Resgate!")
            time.sleep(1); st.rerun()
    else: st.warning("Zoo vazio.")

elif aba == "🌲 Florestas":
    st.header("🌲 Florestas")
    st.write("")
    f = st.selectbox("Região:", ["Amazónia", "Selva do Congo", "Taiga"])
    cols = st.columns(3)
    for i, an in enumerate(buscar_animais(f)):
        with cols[i%3]: desenhar_cartao(an, "f")

elif aba == "🌊 Oceanos":
    st.header("🌊 Oceanos")
    st.write("

[Image of the ocean zones]
")
    o = st.selectbox("Zona:", ["Pacífico", "Atlântico", "Recifes"])
    cols = st.columns(3)
    for i, an in enumerate(buscar_animais(o)):
        with cols[i%3]: desenhar_cartao(an, "o")

elif aba == "🧬 Fusão":
    st.header("🧬 Fusão")
    if len(st.session_state.zoo) >= 2:
        if st.button("🔥 EXECUTAR FUSÃO"): st.balloons(); st.success("Fusão completa!")
    else: st.warning("Zoo vazio.")

elif aba == "⚙️ Definições":
    st.header("⚙️ Painel")
    if not pode_ativar_normal:
        st.error(f"⚠️ Código 6626 bloqueado por 1 semana. Restam: {tempo_espera.days} dias e {tempo_espera.seconds//3600} horas.")

    st.session_state.codigo_mega = st.text_input("👑 Mega", value=st.session_state.codigo_mega, type="password")
    st.session_state.codigo_24h = st.text_input("🕒 Premium 24h", value=st.session_state.codigo_24h, type="password")
    st.session_state.codigo_neon = st.text_input("✨ Neon", value=st.session_state.codigo_neon, type="password")
    st.session_state.codigo_diamante = st.text_input("💎 Diamante", value=st.session_state.codigo_diamante, type="password")
    st.session_state.codigo_crio = st.text_input("❄️ Código Crio", value=st.session_state.codigo_crio, type="password")
    
    if st.button("Guardar Alterações"): st.rerun()
