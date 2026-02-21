import streamlit as st
import pandas as pd
import requests
import random

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo Ultimate Pro", page_icon="🧬", layout="wide")

# 2. ESTADOS
for key, val in {
    'luz': False, 'zoo': [], 'codigo': "", 'search_query': "Wildlife", 'cor_card': "Preto"
}.items():
    if key not in st.session_state: st.session_state[key] = val

is_mestre = st.session_state.codigo == "6626"
is_ai_unlocked = st.session_state.codigo == "33236"
is_premium = is_mestre or is_ai_unlocked
LIMITE = 80 if is_premium else 20

# 3. CSS (Borda lateral AI, Estilo Mestre e Efeitos de Luta)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23") if not st.session_state.luz else "#ffffff"
txt_color = "#000" if st.session_state.luz else "#fff"
border_color = "#ffd700" if is_mestre else "#2ea043"

st.markdown(f"""
    <style>
    @keyframes battle-shake {{ 0% {{ transform: translate(1px, 1px) rotate(0deg); }} 10% {{ transform: translate(-1px, -2px) rotate(-1deg); }} 100% {{ transform: translate(1px, 1px) rotate(0deg); }} }}
    .stApp {{ background-color: {"#f0f2f6" if st.session_state.luz else "#0b1117"}; color: {txt_color}; }}
    .cc-card {{ 
        background: {c_bg} !important; border-radius: 15px; padding: 20px; 
        border-left: 12px solid {border_color}; margin-bottom: 20px;
        color: {txt_color} !important;
        { "animation: gold-glow 3s infinite;" if is_mestre else "" }
    }}
    .battle-card {{ border: 3px solid #ff4b4b; animation: battle-shake 0.5s infinite; }}
    .winner-glow {{ box-shadow: 0 0 30px #ffd700; border: 4px solid #ffd700 !important; }}
    </style>
    """, unsafe_allow_html=True)

# 4. FUNÇÃO DE BUSCA
def buscar(q):
    url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=10&locale=pt-PT"
    try:
        res = requests.get(url).json()
        return [{'nome': i.get('preferred_common_name', i['name']).title(), 'sci': i['name'], 'foto': i['default_photo']['medium_url'], 'score': i.get('observations_count', 1)} for i in res['results'] if i.get('default_photo')]
    except: return []

# 5. ASSISTENTE IA (BARRA LATERAL)
st.sidebar.title("🎮 Painel")
st.session_state.codigo = st.sidebar.text_input("Código:", type="password")

if is_ai_unlocked:
    st.sidebar.info("🤖 **Bio-Assistente IA**")
    if st.sidebar.button("🌍 REGIÃO ALEATÓRIA"):
        st.session_state.search_query = random.choice(["Amazonia", "Sahara", "Arctic", "Serengeti"])
    duvida = st.sidebar.text_input("Pergunta à IA:")
    if duvida:
        if "rápido" in duvida.lower(): st.sidebar.write("⚡ Falcão-peregrino!")
        else: st.sidebar.write("🔍 Analisando...")

# 6. INTERFACE
aba = st.sidebar.radio("Menu", ["🌍 Mundo", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"])

if aba == "🔬 Laboratório":
    st.title("⚔️ Arena de Duelos & Laboratório")
    
    tab1, tab2 = st.tabs(["🔎 Busca Avançada", "🥊 Luta de Animais"])
    
    with tab1:
        search_lab = st.text_input("Pesquisa Genética:")
        if search_lab:
            res = buscar(search_lab)
            cols = st.columns(3)
            for i, an in enumerate(res):
                with cols[i%3]:
                    st.markdown(f"<div class='cc-card'><img src='{an['foto']}' style='width:100%; border-radius:10px;'><h4>{an['nome']}</h4></div>", unsafe_allow_html=True)
                    if st.button(f"Guardar {an['nome']}", key=f"lab_{i}"):
                        if len(st.session_state.zoo) < LIMITE: st.session_state.zoo.append(an)
    
    with tab2:
        st.subheader("Preparem-se para o combate!")
        c1, c2 = st.columns(2)
        p1 = c1.text_input("Desafiante 1:", "Leão")
        p2 = c2.text_input("Desafiante 2:", "Tigre")
        
        if st.button("🔥 INICIAR LUTA"):
            res1, res2 = buscar(p1), buscar(p2)
            if res1 and res2:
                a1, a2 = res1[0], res2[0]
                s1, s2 = a1['score'], a2['score'] # Usa número de observações como 'poder'
                
                col1, col2 = st.columns(2)
                with col1:
                    win_class = "winner-glow" if s1 > s2 else ""
                    st.markdown(f"<div class='cc-card battle-card {win_class}'><img src='{a1['foto']}' style='width:100%;'><h3>{a1['nome']}</h3><p>Poder: {s1}</p></div>", unsafe_allow_html=True)
                with col2:
                    win_class = "winner-glow" if s2 > s1 else ""
                    st.markdown(f"<div class='cc-card battle-card {win_class}'><img src='{a2['foto']}' style='width:100%;'><h3>{a2['nome']}</h3><p>Poder: {s2}</p></div>", unsafe_allow_html=True)
                
                if s1 > s2: st.success(f"🏆 VENCEDOR: {a1['nome']}!")
                elif s2 > s1: st.success(f"🏆 VENCEDOR: {a2['nome']}!")
                else: st.warning("Empate Biológico!")

elif aba == "🌍 Mundo":
    st.map(pd.DataFrame({'lat': [20.0], 'lon': [0.0]}))
    q = st.text_input("Procurar:", value=st.session_state.search_query)
    res = buscar(q)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]:
            st.markdown(f"<div class='cc-card'><img src='{an['foto']}' style='width:100%; height:180px; object-fit:cover; border-radius:10px;'><h3>{an['nome']}</h3></div>", unsafe_allow_html=True)
            if st.button(f"Guardar {an['nome']}", key=f"m_{i}"):
                if len(st.session_state.zoo) < LIMITE: st.session_state.zoo.append(an)

elif aba == "⭐ Coleção":
    if is_mestre: st.markdown("<div class='mestre-badge'>🏆 MESTRE ZOÓLOGO</div>", unsafe_allow_html=True)
    st.write(f"Capacidade: {len(st.session_state.zoo)} / {LIMITE}")
    cols = st.columns(3)
    for i, an in enumerate(st.session_state.zoo):
        with cols[i%3]:
            st.markdown(f"<div class='cc-card'><img src='{an['foto']}' style='width:100%; border-radius:10px;'><h4>{an['nome']}</h4></div>", unsafe_allow_html=True)
            if st.button("Remover", key=f"del_{i}"): st.session_state.zoo.pop(i); st.rerun()

elif aba == "⚙️ Definições":
    st.session_state.luz = st.toggle("Modo Claro")
    if is_premium and st.button("❌ APAGAR PREMIUM"):
        st.session_state.codigo = ""; st.rerun()
