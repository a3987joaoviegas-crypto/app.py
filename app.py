import streamlit as st
import requests
import random

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo 🌍", layout="wide")

# 2. ESTADO DA APP
for key, val in {
    'zoo': [], 'codigo': "", 'codigo_perm': "", 'pontos': 0,
    'cor_card': "Preto", 'cor_fundo': "Preto", 'idioma': "pt-PT", 
    'lang_label': "Português", 'nome_zoologo': "Explorador"
}.items():
    if key not in st.session_state: st.session_state[key] = val

# LÓGICA DE NÍVEIS
is_mega = st.session_state.codigo_perm == "67lucas62"
is_mestre = (st.session_state.codigo == "6626") or is_mega
LIMITE_ZOO = 80 if is_mestre else 20

# 3. DESIGN CSS AVANÇADO
app_bg = "#0b1117" if st.session_state.cor_fundo == "Preto" else "#ffffff"

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; color: white; }}
    
    /* Borda Galática para o Mega */
    .cartao-cidadao {{
        background: #1a1c23; border-radius: 15px; padding: 15px; text-align: center;
        border: 4px solid transparent; border-image: linear-gradient(45deg, #ff00ff, #00ffff) 1;
        animation: galatico_borda 3s linear infinite;
    }}
    @keyframes galatico_borda {{ 0% {{ filter: hue-rotate(0deg); }} 100% {{ filter: hue-rotate(360deg); }} }}

    /* Layout Premium */
    .premium-header {{
        background: linear-gradient(90deg, #2c003e, #000000);
        padding: 30px; border-radius: 20px; border: 1px solid #00ffff; text-align: center; margin-bottom: 20px;
    }}
    .lab-container {{
        background-image: url('https://www.transparenttextures.com/patterns/carbon-fibre.png');
        background-color: #0d1117; border: 2px solid #30363d; border-radius: 15px; padding: 25px;
    }}
    .stat-card {{
        background: rgba(0, 255, 255, 0.05); border-left: 5px solid #00ffff;
        padding: 10px; margin: 5px 0; border-radius: 5px;
    }}
    .ponto-badge {{
        background: gold; color: black; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# 4. FUNÇÕES
def buscar_70(q):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=70&locale={st.session_state.idioma}"
        return requests.get(url, timeout=10).json().get('results', [])
    except: return []

def render_cartao(an, habitat):
    st.markdown(f"""
    <div class='cartao-cidadao'>
        <img src='{an.get('default_photo', {{}}).get('medium_url', '')}' style='width:100%; height:180px; object-fit:cover; border-radius:10px;'>
        <h4 style='margin:10px 0;'>{an.get('preferred_common_name', an['name']).title()}</h4>
        <div style='font-size:0.8em; text-align:left; background:rgba(255,255,255,0.1); padding:5px; border-radius:5px;'>
            🏠 <b>Habitat:</b> {habitat}<br>
            🧬 <b>DNA:</b> {an['id']}
        </div>
    </div>
    """, unsafe_allow_html=True)

# 5. PÁGINA PREMIUM MEGA
if is_mega and st.sidebar.toggle("💎 ACEDER AO PREMIUM", value=True):
    st.markdown(f"""
    <div class='premium-header'>
        <h1>💎 BEM-VINDO AO MUNDOVIVO PREMIUM</h1>
        <p>Aqui tens acesso às ferramentas mais avançadas de biologia molecular e conservação.</p>
        <span class='ponto-badge'>🏆 {st.session_state.pontos} PONTOS DE ZOÓLOGO</span>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar interna do Premium
    with st.sidebar:
        st.markdown("---")
        st.subheader("📍 Navegação Premium")
        menu_p = st.selectbox("Escolha o Setor", ["🧬 Laboratório Genético", "📊 Scanner de Bio-Análise", "🚁 Centro de Resgate Global"])

    if menu_p == "🧬 Laboratório Genético":
        st.subheader("🧬 Estação de Fusão de Genes")
        if len(st.session_state.zoo) >= 2:
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                p1 = st.selectbox("Espécie A", [x['preferred_common_name'] for x in st.session_state.zoo], key="p1")
            with col2:
                st.markdown("<h1 style='text-align:center;'>+</h1>", unsafe_allow_html=True)
            with col3:
                p2 = st.selectbox("Espécie B", [x['preferred_common_name'] for x in st.session_state.zoo], key="p2")
            
            if st.button("🧪 MISTURAR GENES NO REATOR", use_container_width=True):
                hibrido = p1[:len(p1)//2] + p2[len(p2)//2:].lower()
                st.balloons()
                st.markdown(f"<div class='lab-container' style='text-align:center;'><h2>NOVA ESPÉCIE DETETADA: {hibrido}</h2></div>", unsafe_allow_html=True)
        else:
            st.info("Precisas de pelo menos 2 animais no teu Zoo para realizar fusões.")

    elif menu_p == "📊 Scanner de Bio-Análise":
        st.subheader("🔬 Scanner de Bio-Análise Completa")
        if st.session_state.zoo:
            escolha = st.selectbox("Inserir Animal no Scanner", [x['preferred_common_name'] for x in st.session_state.zoo])
            random.seed(escolha)
            
            c1, c2 = st.columns([1, 2])
            with c1:
                # Simular imagem de laboratório
                st.markdown("🖼️ **Imagem do Scanner Ativa**")
                st.write("🔍 A analisar estrutura óssea...")
                st.write("🔍 A analisar ritmo cardíaco...")
            with c2:
                st.markdown(f"<div class='stat-card'>🧬 <b>Simbolo de Genes:</b> Ativo (Match {random.randint(90,99)}%)</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='stat-card'>⏱️ <b>Esperança de Vida:</b> {random.randint(5, 150)} anos</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='stat-card'>⚡ <b>Velocidade:</b> {random.randint(10, 110)} km/h</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='stat-card'>🧠 <b>QI Animal:</b> {random.randint(10, 90)} pts</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='stat-card'>🍖 <b>Consumo Diário:</b> {random.uniform(0.5, 50.0):.1f} kg</div>", unsafe_allow_html=True)
        else:
            st.write("Zoo vazio. Sem dados para analisar.")

    elif menu_p == "🚁 Centro de Resgate Global":
        st.subheader("🚁 Missões de Emergência")
        st.write("Estes animais precisam de ajuda imediata! Resgata-os para ganhar Pontos de Zoólogo.")
        
        # Gerar lista de resgate (simulação)
        resgates = ["Panda Ferido", "Tartaruga em Rede", "Águia com Asa Partida", "Leão em Armadilha", "Pinguim em Maré Negra"]
        for r in resgates:
            col_r1, col_r2 = st.columns([3, 1])
            with col_r1:
                st.warning(f"🚨 ALERTA: {r}")
            with col_r2:
                if st.button(f"Resgatar", key=r):
                    st.session_state.pontos += 50
                    st.toast(f"Resgataste o {r}! +50 pontos")
                    st.rerun()

# 6. INTERFACE NORMAL (ZOO E BUSCA)
else:
    with st.sidebar:
        st.title("🌍 MundoVivo")
        st.write(f"Zoólogo: **{st.session_state.nome_zoologo}**")
        aba = st.radio("Navegação", ["Países", "Habitats", "Oceano", "Laboratório", "Coleção", "Definições"])

    if aba == "Países":
        pais = st.selectbox("Escolher País", ["Portugal", "Brasil", "Japão", "Austrália"])
        animais = buscar_70(pais)
        cols = st.columns(3)
        for i, an in enumerate(animais):
            with cols[i%3]: 
                render_cartao(an, pais)
                if st.button(f"Capturar", key=f"cap_{i}"):
                    if len(st.session_state.zoo) < LIMITE_ZOO:
                        st.session_state.zoo.append(an)
                        st.rerun()

    elif aba == "Coleção":
        st.header("🐾 O Teu Zoo")
        cols = st.columns(3)
        for i, an in enumerate(st.session_state.zoo):
            with cols[i%3]: render_cartao(an, "Meu Zoo")

    elif aba == "Definições":
        st.session_state.nome_zoologo = st.text_input("Nome", st.session_state.nome_zoologo)
        st.session_state.codigo_perm = st.text_input("Código Mega", type="password")
        if st.button("Guardar"): st.rerun()
