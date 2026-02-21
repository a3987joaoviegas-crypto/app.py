import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. ESTADO DO SISTEMA
chaves = {
    'zoo': [], 'criogenia_storage': [], 'fusao_temp': [],
    'codigo': "", 'codigo_perm': "", 'codigo_crio': "", 
    'codigo_neon': "", 'codigo_diamante': "", 'premium_ativo': False, 
    'cor_fundo_user': "#0b1117", 'cor_card_user': "#1a1c23",
    'luminosidade': 100, 'inicio_premium': None
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# 2. LÓGICA DE ACESSO
is_mega = st.session_state.codigo_perm == "67lucas62"
is_premium_normal = st.session_state.codigo == "6626"
tem_beneficios = is_mega or is_premium_normal
is_neon = st.session_state.codigo_neon == "6676neon7secret"
is_diamante = st.session_state.codigo_diamante == "77daimond8secret"

# 3. ESTILOS VISUAIS
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

def desenhar_cartao(an, prefixo, op_resgate=False):
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
        <div class="stats-txt">📊 ESTATÍSTICAS VIP<br>🚀 VELOCIDADE: {random.randint(20, 200)} KM/H<br>⚖️ PESO: {random.randint(1, 6000)} KG</div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if not op_resgate:
        if st.button(f"📥 CAPTURAR", key=f"btn_{prefixo}_{an['id']}", use_container_width=True):
            limite = 80 if tem_beneficios else 20
            if len(st.session_state.zoo) < limite:
                st.session_state.zoo.append(an); st.toast(f"{nome} capturado!")
            else: st.error("Zoo cheio!")
    else:
        if st.button(f"🌀 RESGATAR", key=f"res_{prefixo}_{an['id']}", use_container_width=True):
            st.session_state.zoo.append(an)
            st.session_state.criogenia_storage.remove(an)
            st.success("Animal resgatado!")
            time.sleep(1); st.rerun()

# 5. SIDEBAR
with st.sidebar:
    if is_premium_normal and st.session_state.inicio_premium:
        restante = timedelta(hours=24) - (datetime.now() - st.session_state.inicio_premium)
        if restante.total_seconds() > 0:
            h, r = divmod(int(restante.total_seconds()), 3600)
            m, s = divmod(r, 60)
            st.markdown(f'<div style="background:red; color:white; padding:10px; border-radius:10px; text-align:center;">⌛ {h:02d}:{m:02d}:{s:02d}</div>', unsafe_allow_html=True)

    st.title("🌍 MundoVivo")
    if tem_beneficios: st.session_state.premium_ativo = st.toggle("MODO VIP", value=st.session_state.premium_ativo)
    
    nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    if st.session_state.premium_ativo and tem_beneficios:
        nav = ["🔬 Laboratório", "🧬 Fusão", "📊 Estatísticas", "❄️ Criogenia", "⚙️ Definições"]
    aba = st.radio("Menu", nav)

# 6. CONTEÚDO DAS ABAS
if aba == "🌲 Florestas":
    st.header("🌲 Ecossistemas de Floresta")
    
    f = st.selectbox("Região:", ["Amazónia", "Selva do Congo", "Taiga Siberiana"])
    cols = st.columns(3)
    for i, an in enumerate(buscar_animais(f)):
        with cols[i%3]: desenhar_cartao(an, "f")

elif aba == "🌊 Oceanos":
    st.header("🌊 Ecossistemas Oceânicos")
    
    o = st.selectbox("Zona:", ["Oceano Pacífico", "Recifes de Coral", "Abismo"])
    cols = st.columns(3)
    for i, an in enumerate(buscar_animais(o)):
        with cols[i%3]: desenhar_cartao(an, "o")

elif aba == "🧬 Fusão":
    st.header("🧬 Câmara de Fusão Genética")
    if len(st.session_state.zoo) < 2: st.warning("Precisas de 2 animais no Zoo.")
    else:
        c1, c2 = st.columns(2)
        a1 = c1.selectbox("Animal 1", st.session_state.zoo, format_func=lambda x: x.get('preferred_common_name', 'N/A'), key="f1")
        a2 = c2.selectbox("Animal 2", st.session_state.zoo, format_func=lambda x: x.get('preferred_common_name', 'N/A'), key="f2")
        if st.button("🔥 INICIAR FUSÃO"):
            with st.spinner("Misturando ADN..."):
                time.sleep(2)
                novo_nome = a1.get('preferred_common_name','')[0:4] + a2.get('preferred_common_name','')[2:]
                st.balloons()
                st.success(f"Nova espécie criada: {novo_nome.upper()}!")

elif aba == "❄️ Criogenia":
    st.header("❄️ Criogenia & Resgate")
    if st.session_state.codigo_crio == "crio969":
        aba_crio = st.tabs(["Congelar", "Unidade de Resgate"])
        with aba_crio[0]:
            if st.session_state.zoo:
                alvo = st.selectbox("Animal para congelar:", st.session_state.zoo, format_func=lambda x: x.get('preferred_common_name', 'N/A'))
                if st.button("❄️ CONGELAR"):
                    st.session_state.criogenia_storage.append(alvo)
                    st.session_state.zoo.remove(alvo)
                    st.rerun()
        with aba_crio[1]:
            if not st.session_state.criogenia_storage: st.info("Câmara vazia.")
            else:
                cols = st.columns(3)
                for i, an in enumerate(st.session_state.criogenia_storage):
                    with cols[i%3]: desenhar_cartao(an, "res", op_resgate=True)
    else: st.error("Acesso Negado.")

elif aba == "⚙️ Definições":
    st.header("⚙️ Painel")
    with st.expander("🎨 VISUAL"):
        st.session_state.cor_fundo_user = st.color_picker("Fundo", st.session_state.cor_fundo_user)
        st.session_state.cor_card_user = st.color_picker("Cards", st.session_state.cor_card_user)
    
    st.markdown("### 👑 ACESSOS")
    c1, c2 = st.columns(2)
    with c1: st.session_state.codigo_perm = st.text_input("Mega Código", type="password")
    with c2: st.session_state.codigo = st.text_input("Premium 24h", type="password")
    
    st.markdown("### ✨ CORES & CRIO")
    c3, c4, c5 = st.columns(3)
    with c3: st.session_state.codigo_neon = st.text_input("Neon", type="password")
    with c4: st.session_state.codigo_diamante = st.text_input("Diamante", type="password")
    with c5: st.session_state.codigo_crio = st.text_input("Crio", type="password")
    
    if st.button("Guardar"): st.rerun()
