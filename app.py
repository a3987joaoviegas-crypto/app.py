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
    'premium_ativo': False, 'cor_card': "Preto", 'cor_fundo': "Preto", 
    'luminosidade': 100, 'pontos': 250, 'missoes_concluidas': 0
}

for chave, valor in chaves_padrao.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

# 3. LÓGICA DE ACESSO E BORDAS
is_premium_normal = st.session_state.codigo == "6626"
is_mega = st.session_state.codigo_perm == "67lucas62"
tem_acesso = is_premium_normal or is_mega

if is_mega:
    estilo_borda = "border: 5px solid; border-image: linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet) 1;"
elif is_premium_normal:
    estilo_borda = "border: 4px solid #ffd700;"
else:
    estilo_borda = "border: 4px solid #2ecc71;"

# 4. DESIGN CSS
mapa_cores = {"Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", "Verde": "#002b1b", "Cinza": "#262730"}
app_bg = mapa_cores.get(st.session_state.cor_fundo, "#0b1117")
card_bg = mapa_cores.get(st.session_state.cor_card, "#1a1c23")

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; filter: brightness({st.session_state.luminosidade}%); color: white; }}
    .cartao-cidadao {{
        background: {card_bg}; color: white; border-radius: 15px; padding: 15px; 
        text-align: center; {estilo_borda} min-height: 580px;
        display: flex; flex-direction: column; justify-content: space-between;
        margin-bottom: 20px;
    }}
    @keyframes fly {{
        from {{ transform: translateX(-150%) translateY(0px); }}
        to {{ transform: translateX(250%) translateY(0px); }}
    }}
    .helicoptero {{ font-size: 80px; position: fixed; top: 20%; left: 0; z-index: 9999; animation: fly 4s linear forwards; pointer-events: none; }}
    .premium-panel {{
        background: radial-gradient(circle, rgba(255,215,0,0.15) 0%, rgba(0,0,0,0) 70%);
        padding: 20px; border-radius: 20px; text-align: center; border: 1px solid rgba(255, 215, 0, 0.3); margin-bottom: 20px;
    }}
    .diamond {{ font-size: 50px; text-shadow: 0 0 20px #fff; }}
    .info-bio {{ background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; font-size: 0.8em; text-align: left; margin: 8px 0; border-left: 3px solid #2ecc71; }}
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE BUSCA
def buscar(q):
    try: return requests.get(f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=9&locale=pt-PT").json().get('results', [])
    except: return []

def render_cartao(an, key_prefix):
    nome = an.get('preferred_common_name', an.get('name', 'Espécie')).title()
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/200")
    
    # Gerar dados se não existirem
    if 'vel' not in an:
        an['vel'] = random.randint(10, 120) if an.get('iconic_taxon_name') == 'Mammalia' else random.randint(1, 40)
        an['vida'] = random.randint(5, 80)
        an['peso'] = random.randint(1, 500)

    st.markdown(f"""
    <div class="cartao-cidadao">
        <img src="{foto}" style="width:100%; height:200px; object-fit:cover; border-radius:10px;">
        <h4 style="margin:10px 0;">{nome}</h4>
        <div class="info-bio">
            <b>🧬 Velocidade:</b> {an['vel']} km/h<br>
            <b>⏳ Expectativa:</b> {an['vida']} anos<br>
            <b>⚖️ Peso Médio:</b> {an['peso']} kg<br>
            <b>🍼 Reprodução:</b> Biológica
        </div>
    </div>""", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Capturar", key=f"c_{key_prefix}_{an['id']}"):
            st.session_state.zoo.append(an); st.toast(f"{nome} capturado!")
    with c2:
        if st.session_state.premium_ativo and tem_acesso:
            if st.button("🧬 DNA", key=f"d_{key_prefix}_{an['id']}"):
                st.session_state.tanque_fusao.append(an); st.toast("DNA extraído!")

# 6. SIDEBAR DINÂMICA
with st.sidebar:
    st.title("🌍 MundoVivo")
    if tem_acesso:
        st.session_state.premium_ativo = st.toggle("🔄 MODO VIP", value=st.session_state.premium_ativo)
        if st.session_state.premium_ativo:
            st.markdown('<div class="premium-panel"><div class="diamond">💎</div><div style="color:#ffd700; font-weight:bold;">TORNOU-SE PREMIUM</div></div>', unsafe_allow_html=True)
            nav = ["🔬 Laboratório", "🧬 Fusão", "🚁 Missões", "📊 Estatísticas", "⚙️ Definições"]
        else:
            nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    else:
        nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    aba = st.radio("Navegação", nav)

# 7. LOGICA DE ABAS
if aba in ["🌍 Países", "🌲 Florestas", "🌊 Oceanos"]:
    escolha = st.selectbox("Explorar:", ["Portugal", "Brasil", "Amazónia", "Oceano Atlântico", "Japão"])
    res = buscar(escolha)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_cartao(an, aba)

elif aba == "🔬 Laboratório":
    st.title("🔬 Centro de Pesquisa")
    query = st.text_input("🔍 Pesquisa Global:")
    if query:
        res = buscar(query); cols = st.columns(3)
        for i, an in enumerate(res):
            with cols[i%3]: render_cartao(an, "lab")
    st.divider()
    if st.session_state.zoo:
        st.subheader("🦁 Inventário")
        cols_zoo = st.columns(3)
        for i, an in enumerate(st.session_state.zoo):
            with cols_zoo[i%3]: render_cartao(an, "zoo")

elif aba == "🧬 Fusão":
    st.title("🧬 Engenharia de Híbridos")
    if len(st.session_state.tanque_fusao) >= 2:
        a1 = st.selectbox("Matriz A", st.session_state.tanque_fusao, format_func=lambda x: x.get('name'))
        a2 = st.selectbox("Matriz B", st.session_state.tanque_fusao, format_func=lambda x: x.get('name'))
        if st.button("FUNDIR"):
            h = f"{a1['name'][:4]}{a2['name'][-3:]}".upper()
            st.success(f"HÍBRIDO CRIADO: {h}"); st.balloons()
    else: st.warning("Necessita de 2 amostras de DNA.")

elif aba == "🚁 Missões":
    st.title("🚁 Unidade de Resgate")
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/80/World_map_-_low_resolution.svg")
    if st.button("🚀 INICIAR RESGATE"):
        st.markdown('<audio autoplay><source src="https://www.soundjay.com/transportation/helicopter-fly-over-1.mp3"></audio>', unsafe_allow_html=True)
        st.markdown('<div class="helicoptero">🚁</div>', unsafe_allow_html=True)
        time.sleep(4); st.session_state.pontos += 100; st.session_state.missoes_concluidas += 1; st.rerun()

elif aba == "📊 Estatísticas": # ESTA ABA SÓ APARECE NO MODO PREMIUM
    st.title("📊 Estatísticas Biológicas VIP")
    if st.session_state.zoo:
        v_media = sum(a.get('vel', 0) for a in st.session_state.zoo) / len(st.session_state.zoo)
        t_medio = sum(a.get('vida', 0) for a in st.session_state.zoo) / len(st.session_state.zoo)
        c1, c2 = st.columns(2)
        c1.metric("Velocidade Média do Zoo", f"{v_media:.1f} km/h")
        c2.metric("Longevidade Média do Zoo", f"{t_medio:.1f} anos")
        st.write("---")
        st.subheader("📋 Registro Detalhado")
        st.table([{"Animal": a.get('name'), "Velocidade": f"{a.get('vel')} km/h", "Vida": f"{a.get('vida')} anos", "Peso": f"{a.get('peso')} kg"} for a in st.session_state.zoo])
    else: st.info("Zoo vazio.")

elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    st.session_state.codigo = st.text_input("Código Premium", value=st.session_state.codigo, type="password")
    st.session_state.codigo_perm = st.text_input("Código Mega", value=st.session_state.codigo_perm, type="password")
    st.session_state.cor_fundo = st.selectbox("Fundo", list(mapa_cores.keys()), index=list(mapa_cores.keys()).index(st.session_state.cor_fundo))
    st.session_state.luminosidade = st.slider("Brilho", 50, 150, st.session_state.luminosidade)
    if st.button("Guardar"): st.rerun()
