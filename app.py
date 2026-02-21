import streamlit as st
import pandas as pd
import requests
import random

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo 🌍", page_icon="🌍", layout="wide")

# 2. ESTADOS
for key, val in {
    'luz': False, 'zoo': [], 'codigo': "", 'codigo_perm': "", 
    'search_query': "", 'cor_card': "Preto", 'cor_fundo': "Preto", 
    'chat_pos': "sidebar"
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Lógica de Permissões
is_perm_active = st.session_state.codigo_perm == "67lucas62"
is_mestre = st.session_state.codigo == "6626" or is_perm_active
is_ai_unlocked = st.session_state.codigo == "33236" or is_perm_active
LIMITE = 80 if is_mestre else 20

# 3. CSS (Bordas Galácticas para o código 67lucas62)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f", "Amarelo": "#f1c40f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23") if not st.session_state.luz else "#ffffff"
bg_app = cores_hex.get(st.session_state.cor_fundo, "#0b1117") if not st.session_state.luz else "#f0f2f6"
txt_color = "#000" if (st.session_state.luz or st.session_state.cor_card == "Branco") else "#fff"

# Definição da Borda
if is_perm_active:
    # Efeito Galáctico (Animado)
    border_style = """
        border-left: 15px solid;
        border-right: 15px solid;
        border-image: linear-gradient(45deg, #ff00ff, #00ffff, #ff00ff, #00ffff) 1;
        animation: galactic 4s linear infinite;
    """
else:
    b_color = "#ffd700" if is_mestre else "#2ea043"
    border_style = f"border-left: 15px solid {b_color}; border-right: 5px solid {b_color};"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_app}; color: {txt_color}; }}
    
    .cc-card {{ 
        background: {c_bg} !important; 
        border-radius: 15px; 
        padding: 20px; 
        {border_style}
        box-shadow: 10px 10px 30px rgba(0,0,0,0.7); 
        margin-bottom: 20px;
        color: {txt_color} !important;
    }}
    
    @keyframes galactic {{
        0% {{ filter: hue-rotate(0deg); box-shadow: 0 0 10px #ff00ff; }}
        50% {{ box-shadow: 0 0 30px #00ffff; }}
        100% {{ filter: hue-rotate(360deg); box-shadow: 0 0 10px #ff00ff; }}
    }}
    
    .code-box {{ background: rgba(255,255,255,0.05); padding: 25px; border-radius: 15px; border: 2px dashed #444; }}
    </style>
    """, unsafe_allow_html=True)

# 4. MOTOR DE BUSCA
def buscar(q):
    if not q: return []
    url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=12"
    try:
        res = requests.get(url).json()
        return [{'nome': i.get('preferred_common_name', i['name']).title(), 'sci': i['name'], 'foto': i['default_photo']['medium_url'] if i.get('default_photo') else "", 'score': i.get('observations_count', 1)} for i in res['results']]
    except: return []

# 5. SIDEBAR (Sempre visível)
with st.sidebar:
    st.markdown(f"# 🌍 MundoVivo")
    st.markdown("---")
    
    if is_ai_unlocked:
        st.subheader("🤖 Assistente Supremo")
        if st.button("⬅️ Mover Chat"): 
            st.session_state.chat_pos = "left" if st.session_state.chat_pos == "sidebar" else "sidebar"
        
        if st.session_state.chat_pos == "sidebar":
            duvida = st.text_input("Dúvida Galáctica:", key="ia_side")
            if duvida: st.info(f"🌌 A analisar: {duvida}")
    
    aba = st.sidebar.radio("Navegação", ["🌍 Mundo", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"])

# 6. INTERFACE PRINCIPAL
if st.session_state.chat_pos == "left" and is_ai_unlocked:
    st.text_input("Dúvida Galáctica (Centro):", key="ia_center")

if aba == "🌍 Mundo":
    st.title("🌍 Planisfério")
    st.map(pd.DataFrame({'lat': [20.0], 'lon': [0.0]}))
    q = st.text_input("Procurar:", value=st.session_state.search_query)
    res = buscar(q if q else "Animal")
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]:
            st.markdown(f"<div class='cc-card'><img src='{an['foto']}' width='100%' style='border-radius:10px;'><h3>{an['nome']}</h3></div>", unsafe_allow_html=True)
            if st.button(f"Guardar {an['nome']}", key=f"w_{i}"):
                if len(st.session_state.zoo) < LIMITE: st.session_state.zoo.append(an)

elif aba == "🌲 Florestas":
    st.title("🌲 Regiões Florestais")
    st.map(pd.DataFrame({'lat': [-3.0, 60.0], 'lon': [-60.0, 100.0]}))
    res = buscar("Forest mammals")
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: st.markdown(f"<div class='cc-card'><h4>{an['nome']}</h4><img src='{an['foto']}' width='100%'></div>", unsafe_allow_html=True)

elif aba == "🌊 Oceanos":
    st.title("🌊 Explorador de Oceanos")
    st.map(pd.DataFrame({'lat': [0.0, -20.0], 'lon': [-150.0, -20.0]}))
    res = buscar("Ocean animals")
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: st.markdown(f"<div class='cc-card'><h4>{an['nome']}</h4><img src='{an['foto']}' width='100%'></div>", unsafe_allow_html=True)

elif aba == "🔬 Laboratório":
    st.title("🔬 Laboratório Supremo")
    t1, t2, t3 = st.tabs(["🔎 Centro Original", "🥊 Arena", "🎲 Aleatório"])
    with t1:
        s = st.text_input("Pesquisa Científica:")
        for an in buscar(s):
            st.markdown(f"<div class='cc-card'><h3>{an['nome']}</h3></div>", unsafe_allow_html=True)
            if st.button(f"Guardar {an['nome']}", key=f"lab_{an['nome']}"): st.session_state.zoo.append(an)

elif aba == "⚙️ Definições":
    st.title("⚙️ Definições")
    st.markdown("<div class='code-box'>", unsafe_allow_html=True)
    st.session_state.codigo = st.text_input("Código Premium:", type="password", value=st.session_state.codigo)
    st.session_state.codigo_perm = st.text_input("Código Supremo (Permanente):", type="password", value=st.session_state.codigo_perm)
    
    if is_perm_active and st.button("❌ APAGAR SUPREMO"):
        st.session_state.codigo_perm = ""
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("Inserir"):
        st.balloons()
        st.success("Efeito Galáctico Ativado!")
    
    st.session_state.luz = st.toggle("Modo Dia", value=st.session_state.luz)
    st.session_state.cor_card = st.selectbox("Cor do Cartão", list(cores_hex.keys()))
    st.session_state.cor_fundo = st.selectbox("Cor do Fundo", list(cores_hex.keys()))
