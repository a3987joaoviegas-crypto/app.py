import streamlit as st
import requests
import random
import time

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

# 3. LÓGICA DE ACESSO
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
        text-align: center; {estilo_borda} min-height: 500px;
        display: flex; flex-direction: column; justify-content: space-between;
        margin-bottom: 20px;
    }}
    .info-bio {{ background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; font-size: 0.85em; text-align: left; margin: 8px 0; border-left: 3px solid #2ecc71; }}
    .premium-stats {{ background: rgba(255, 215, 0, 0.1); border: 1px solid #ffd700; padding: 10px; border-radius: 8px; font-size: 0.8em; margin-top: 5px; color: #ffd700; }}
    @keyframes fly {{ from {{ transform: translateX(-150%); }} to {{ transform: translateX(250%); }} }}
    .helicoptero {{ font-size: 80px; position: fixed; top: 20%; z-index: 9999; animation: fly 4s linear forwards; }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÕES
def render_cartao(an, key_prefix, mostrar_premium=False):
    nome = an.get('preferred_common_name', an.get('name', 'Espécie')).title()
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/200")
    
    # Gerar dados ocultos (apenas calculados uma vez)
    if 'vel' not in an:
        an['vel'] = random.randint(5, 110)
        an['vida'] = random.randint(2, 70)
        an['peso'] = random.randint(10, 4000) if an.get('iconic_taxon_name') == 'Mammalia' else random.uniform(0.1, 50)

    st.markdown(f"""
    <div class="cartao-cidadao">
        <img src="{foto}" style="width:100%; height:200px; object-fit:cover; border-radius:10px;">
        <h4 style="margin:10px 0;">{nome}</h4>
        <div class="info-bio">
            <b>🧬 Classe:</b> {an.get('iconic_taxon_name', 'Bio')}<br>
            <b>🏠 Habitat:</b> Selvagem<br>
            <b>🍼 Reprodução:</b> Biológica
        </div>
    """, unsafe_allow_html=True)
    
    # EXCLUSIVO LAB PREMIUM
    if mostrar_premium:
        st.markdown(f"""
        <div class="premium-stats">
            📊 <b>BIOMETRIA VIP:</b><br>
            • Velocidade: {an['vel']} km/h<br>
            • Expectativa: {an['vida']} anos<br>
            • Peso: {an['peso']:.1f} kg
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Capturar", key=f"c_{key_prefix}_{an['id']}"):
            st.session_state.zoo.append(an); st.toast(f"{nome} no Zoo!")
    with c2:
        if st.session_state.premium_ativo and tem_acesso:
            if st.button("🧬 DNA", key=f"d_{key_prefix}_{an['id']}"):
                st.session_state.tanque_fusao.append(an); st.toast("DNA extraído!")

# 6. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    if tem_acesso:
        st.session_state.premium_ativo = st.toggle("🔄 MODO VIP", value=st.session_state.premium_ativo)
        if st.session_state.premium_ativo:
            nav = ["🔬 Laboratório Premium", "🧬 Fusão", "🚁 Missões", "📊 Estatísticas", "⚙️ Definições"]
        else: nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    else: nav = ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⚙️ Definições"]
    aba = st.radio("Navegação", nav)

# 7. LÓGICA DE ABAS
def buscar(q):
    try: return requests.get(f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=9&locale=pt-PT").json().get('results', [])
    except: return []

if aba in ["🌍 Países", "🌲 Florestas", "🌊 Oceanos"]:
    escolha = st.selectbox("Explorar:", ["Portugal", "Brasil", "Amazónia", "Oceano Pacífico"])
    res = buscar(escolha)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_cartao(an, aba)

elif "Laboratório" in aba:
    st.title(f"🔬 {aba}")
    query = st.text_input("🔍 Pesquisa Global:")
    if query:
        res = buscar(query); cols = st.columns(3)
        for i, an in enumerate(res):
            with cols[i%3]: render_cartao(an, "lab", mostrar_premium=st.session_state.premium_ativo)
    st.divider()
    if st.session_state.zoo:
        st.subheader("🦁 O Teu Inventário")
        cols_zoo = st.columns(3)
        for i, an in enumerate(st.session_state.zoo):
            with cols_zoo[i%3]: render_cartao(an, "zoo", mostrar_premium=st.session_state.premium_ativo)

elif aba == "🧬 Fusão":
    st.title("🧬 Engenharia de Híbridos")
    if len(st.session_state.tanque_fusao) >= 2:
        a1 = st.selectbox("Matriz A", st.session_state.tanque_fusao, format_func=lambda x: x.get('name'))
        a2 = st.selectbox("Matriz B", st.session_state.tanque_fusao, format_func=lambda x: x.get('name'))
        if st.button("FUNDIR"):
            st.success(f"HÍBRIDO: {a1['name'][:4].upper()}{a2['name'][-3:].upper()}"); st.balloons()
    else: st.warning("Necessita de 2 amostras de DNA.")

elif aba == "🚁 Missões":
    st.title("🚁 Resgate")
    if st.button("🚀 ENVIAR HELICÓPTERO"):
        st.markdown('<audio autoplay><source src="https://www.soundjay.com/transportation/helicopter-fly-over-1.mp3"></audio>', unsafe_allow_html=True)
        st.markdown('<div class="helicoptero">🚁</div>', unsafe_allow_html=True)
        time.sleep(4); st.session_state.pontos += 100; st.session_state.missoes_concluidas += 1; st.rerun()

elif aba == "📊 Estatísticas":
    st.title("📊 BIOMETRIA GERAL (VIP)")
    if st.session_state.zoo:
        v_media = sum(a.get('vel', 0) for a in st.session_state.zoo) / len(st.session_state.zoo)
        p_total = sum(a.get('peso', 0) for a in st.session_state.zoo)
        st.metric("Velocidade Média do Zoo", f"{v_media:.1f} km/h")
        st.metric("Peso Total Estimado", f"{p_total:.1f} kg")
        st.table([{"Animal": a.get('name'), "Velocidade": f"{a.get('vel')} km/h", "Peso": f"{a.get('peso'):.1f} kg"} for a in st.session_state.zoo])
    else: st.info("Sem dados.")

elif aba == "⚙️ Definições":
    st.session_state.codigo = st.text_input("Premium", value=st.session_state.codigo, type="password")
    st.session_state.codigo_perm = st.text_input("Mega", value=st.session_state.codigo_perm, type="password")
    st.session_state.cor_fundo = st.selectbox("Fundo", list(mapa_cores.keys()), index=0)
    st.session_state.luminosidade = st.slider("Brilho", 50, 150, 100)
    if st.button("Guardar"): st.rerun()
