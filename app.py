import streamlit as st
import requests
import random
import time

# 1. CONFIGURAÇÃO E ÁUDIO
st.set_page_config(page_title="MundoVivo 🌍", layout="wide")

# 2. ESTADO DA APP
for key, val in {
    'zoo': [], 'codigo': "", 'codigo_perm': "", 'pontos': 0,
    'cor_card': "Preto", 'cor_fundo': "Preto", 'idioma': "pt-PT", 
    'lang_label': "Português", 'nome_zoologo': "Explorador",
    'resgates_ativos': ["Tigre ferido na Ásia", "Panda sem comida na China", "Águia presa em fios", "Baleia perdida", "Lince em perigo"]
}.items():
    if key not in st.session_state: st.session_state[key] = val

is_mega = st.session_state.codigo_perm == "67lucas62"
is_mestre = (st.session_state.codigo == "6626") or is_mega
LIMITE_ZOO = 80 if is_mestre else 20

# 3. DESIGN CSS (LABORATÓRIO E BOTÕES)
st.markdown(f"""
<style>
    .stApp {{ background-color: #0b1117; color: white; }}
    
    /* Botão Capturar/Resgatar Verde */
    div.stButton > button:first-child {{
        background-color: #2ecc71 !important; color: white !important; border: none; font-weight: bold;
    }}
    
    /* Botão Confirmar/Guardar Azul */
    .stButton > button[kind="primary"] {{
        background-color: #3498db !important; color: white !important;
    }}

    /* Botão Eliminar Vermelho */
    .btn-eliminar {{ background-color: #e74c3c !important; color: white !important; border-radius: 5px; }}

    /* Fundo Laboratório de Pesquisa */
    .lab-fundo {{
        background-color: #000;
        background-image: radial-gradient(circle, #001f3f 0%, #000 70%);
        border: 2px solid #00ffff; border-radius: 20px; padding: 30px;
        box-shadow: 0 0 30px rgba(0,255,255,0.2);
    }}

    /* Animação Helicóptero */
    @keyframes heli-move {{
        0% {{ left: 0%; top: 50%; transform: rotate(0deg); }}
        50% {{ left: 50%; top: 20%; transform: rotate(10deg); }}
        100% {{ left: 100%; top: 50%; transform: rotate(0deg); }}
    }}
    .helicoptero {{
        position: relative; font-size: 40px; animation: heli-move 3s linear;
    }}
</style>
""", unsafe_allow_html=True)

# 4. FUNÇÕES DE SUPORTE
def buscar_70(q):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=70&locale={st.session_state.idioma}"
        return requests.get(url, timeout=10).json().get('results', [])
    except: return []

def animacao_resgate():
    placeholder = st.empty()
    # Som de helicóptero simulado (via HTML/JS se necessário, ou apenas visual)
    for i in range(3):
        placeholder.markdown(f"""
        <div style='text-align:center; background: url("https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg") center; background-size: contain; height: 300px; position: relative;'>
            <div class='helicoptero'>🚁 BRRRRRRRRR...</div>
            <h3 style='margin-top:200px; color: gold;'>A voar para a região do animal...</h3>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1)
    placeholder.empty()

# 5. PAGINA PREMIUM
if is_mega and st.sidebar.toggle("💎 ACEDER AO PREMIUM", value=True):
    st.markdown(f"<div style='text-align:center;'><h1>💎 MUNDOVIVO PREMIUM</h1><p><b>Zoólogo:</b> {st.session_state.nome_zoologo} | 🏆 {st.session_state.pontos} Pontos</p></div>", unsafe_allow_html=True)
    
    aba_p = st.selectbox("Setor de Operação", ["🔬 Laboratório de Pesquisa Genética", "📊 Bio-Análise Avançada", "🚁 Missões de Resgate"])

    if aba_p == "🔬 Laboratório de Pesquisa Genética":
        st.markdown("<div class='lab-fundo'>", unsafe_allow_html=True)
        st.subheader("🧬 Estação de Sequenciamento")
        if len(st.session_state.zoo) >= 2:
            c1, c2 = st.columns(2)
            a1 = c1.selectbox("Animal A", [x['preferred_common_name'] for x in st.session_state.zoo])
            a2 = c2.selectbox("Animal B", [x['preferred_common_name'] for x in st.session_state.zoo])
            if st.button("MISTURAR GENES", type="primary"):
                st.success(f"Mistura completa: {a1[:4]}{a2[-4:].lower()} híbrido!")
        st.markdown("</div>", unsafe_allow_html=True)

    elif aba_p == "📊 Bio-Análise Avançada":
        st.markdown("<div class='lab-fundo'>", unsafe_allow_html=True)
        st.subheader("🖥️ Consola de Estatísticas")
        if st.session_state.zoo:
            alvo = st.selectbox("Escolher para Scanner", [x['preferred_common_name'] for x in st.session_state.zoo])
            st.write(f"🧬 **Símbolo de Genes:** ⶫ ⶬ ⶭ (Sequência Encontrada)")
            st.metric("Esperança de Vida", f"{random.randint(10, 100)} anos")
        st.markdown("</div>", unsafe_allow_html=True)

    elif aba_p == "🚁 Missões de Resgate":
        st.subheader("Planisfério de Operações")
        for idx, res in enumerate(st.session_state.resgates_ativos):
            c1, c2 = st.columns([4, 1])
            c1.info(f"📍 {res}")
            if c2.button("Resgatar", key=f"res_{idx}"):
                animacao_resgate()
                st.session_state.pontos += 100
                novos_animais = ["Elefante no gelo", "Koala no fogo", "Gato perdido no mar", "Lobo ferido", "Pássaro sem ninho"]
                st.session_state.resgates_ativos[idx] = random.choice(novos_animais)
                st.rerun()

# 6. PAGINA NORMAL
else:
    with st.sidebar:
        st.title("🌍 MundoVivo")
        aba = st.radio("Navegação", ["Países", "Habitats", "Coleção", "Definições"])

    if aba == "Países":
        p = st.selectbox("Escolher País", ["Portugal", "Brasil", "Japão"])
        animais = buscar_70(p)
        cols = st.columns(3)
        for i, an in enumerate(animais):
            with cols[i%3]:
                st.image(an.get('default_photo', {}).get('medium_url', ''), use_container_width=True)
                st.write(an.get('preferred_common_name', an['name']))
                if st.button(f"Capturar", key=f"cap_{i}"):
                    st.session_state.zoo.append(an)
                    st.toast("Capturado!")

    elif aba == "Coleção":
        st.header("⭐ O Teu Zoo")
        if st.button("🗑️ APAGAR TODO O ZOO", type="secondary"):
            st.session_state.zoo = []
            st.rerun()
            
        cols = st.columns(3)
        for i, an in enumerate(st.session_state.zoo):
            with cols[i%3]:
                st.write(an.get('preferred_common_name', an['name']))
                if st.button(f"Eliminar {i}", key=f"del_{i}"):
                    st.session_state.zoo.pop(i)
                    st.rerun()

    elif aba == "Definições":
        st.session_state.nome_zoologo = st.text_input("Nome", st.session_state.nome_zoologo)
        st.session_state.codigo_perm = st.text_input("Código Mega", type="password")
        if st.button("Confirmar Alterações", type="primary"): st.rerun()
