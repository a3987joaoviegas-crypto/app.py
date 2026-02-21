import streamlit as st
import pd
import requests

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo Ultimate", page_icon="🌍", layout="wide")

# 2. ESTADOS
for key, val in {
    'luz': False, 'negrito': False, 'cor_fundo': "Preto", 
    'cor_card': "Preto", 'lingua': "Português (Original)", 'zoo': []
}.items():
    if key not in st.session_state: st.session_state[key] = val

# 3. DICIONÁRIOS
cores_hex = {
    "Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", 
    "Verde": "#002b1b", "Amarelo": "#f1c40f", "Roxo": "#4b0082", "Vermelho": "#8b0000"
}

lang_map = {
    "Português (Original)": {"code": "pt-BR", "env": "AMBIENTE", "diet": "DIETA", "rep": "REPRODUÇÃO", "save": "Guardar", "carn": "Carnívoro", "herb": "Herbívoro", "omni": "Omnívoro", "viv": "Vivíparo", "ovi": "Ovíparo", "terr": "Terrestre", "aqua": "Aquático"},
    "Inglês": {"code": "en", "env": "ENVIRONMENT", "diet": "DIET", "rep": "REPRODUCTION", "save": "Save", "carn": "Carnivore", "herb": "Herbivore", "omni": "Omnivore", "viv": "Viviparous", "ovi": "Oviparous", "terr": "Terrestrial", "aqua": "Aquatic"},
    "Espanhol": {"code": "es", "env": "AMBIENTE", "diet": "DIETA", "rep": "REPRODUCCIÓN", "save": "Guardar", "carn": "Carnívoro", "herb": "Herbívoro", "omni": "Omnívoro", "viv": "Vivíparo", "ovi": "Ovíparo", "terr": "Terrestre", "aqua": "Acuático"},
    "Russo": {"code": "ru", "env": "ОКРУЖАЮЩАЯ СРЕДА", "diet": "ПИТAНИЕ", "rep": "РЕПРОДУКЦИЯ", "save": "Сохранить", "carn": "Хищник", "herb": "Травоядный", "omni": "Всеядный", "viv": "Живородящие", "ovi": "Яйцекладущие", "terr": "Земной", "aqua": "Водный"},
    "Finlandês": {"code": "fi", "env": "YMPÄRISTÖ", "diet": "RUOKAVALIO", "rep": "LISÄÄNTYMINEN", "save": "Tallenna", "carn": "Lihansyöjä", "herb": "Kasvinsyöjä", "omni": "Kaikkiruokainen", "viv": "Elävänä synnyttävä", "ovi": "Muniva", "terr": "Maalla elävä", "aqua": "Vedessä elävä"},
    "Crioulo": {"code": "pt-PT", "env": "AMBIENTI", "diet": "DIETA", "rep": "REPRODUSON", "save": "Guarda", "carn": "Karnivoru", "herb": "Erbivoru", "omni": "Omnivoru", "viv": "Vivíparu", "ovi": "Ovíparu", "terr": "Terrestre", "aqua": "Akuatiku"}
}
dic = lang_map[st.session_state.lingua]

# 4. CSS COM ANIMAÇÃO
bg = "#f0f2f6" if st.session_state.luz else cores_hex[st.session_state.cor_fundo]
c_bg = "#ffffff" if st.session_state.luz else cores_hex[st.session_state.cor_card]
t_color = "#000000" if (st.session_state.luz or st.session_state.cor_fundo in ["Branco", "Amarelo"]) else "#ffffff"

st.markdown(f"""
    <style>
    @keyframes move {{ from {{ background-position: 0 0; }} to {{ background-position: 100% 100%; }} }}
    .stApp {{ 
        background-color: {bg}; color: {t_color}; 
        background-image: radial-gradient(circle, rgba(255,255,255,0.07) 1px, transparent 1px);
        background-size: 60px 60px; animation: move 120s linear infinite;
    }}
    [data-testid="stSidebar"] {{ min-width: 320px !important; }}
    .cc-card {{ background: {c_bg}; border-radius: 12px; padding: 20px; border-left: 8px solid #2ea043; margin-bottom: 25px; color: {t_color}; }}
    .img-cc {{ width: 100%; height: 220px; object-fit: cover; border-radius: 8px; }}
    .common-name {{ color: #2ea043; font-size: 22px; text-align: center; margin-top: 10px; }}
    * {{ font-weight: {"bold" if st.session_state.negrito else "normal"} !important; }}
    </style>
    """, unsafe_allow_html=True)

# 5. MOTOR DE BUSCA MELHORADO
def buscar(query):
    # Dicionário de termos de busca otimizados para a API iNaturalist
    q_map = {
        "Amazónia": "Amazonia", "Mata Atlântica": "Atlantic Forest", "Taiga Siberiana": "Taiga",
        "Floresta Russa": "Russia animals", "Savana": "Savanna", "Selva Tropical": "Rainforest",
        "Oceano Atlântico": "Atlantic Ocean", "Oceano Pacífico": "Pacific Ocean", 
        "Mar Mediterrâneo": "Mediterranean Sea", "Recifes de Coral": "Coral Reef", "Abismo Marinho": "Deep Sea"
    }
    q_final = q_map.get(query, query)
    url = f"https://api.inaturalist.org/v1/taxa?q={q_final}&taxon_id=1&per_page=70&locale={dic['code']}"
    try:
        res = requests.get(url).json()
        out = []
        for item in res.get('results', []):
            if item.get('default_photo'):
                n = (item.get('preferred_common_name') or item.get('name')).title()
                cl = item.get('iconic_taxon_name', 'Animal')
                d = dic['carn'] if any(x in n.lower() for x in ['leão', 'lion', 'tubarão', 'shark', 'lobo', 'orca']) else dic['herb'] if any(x in n.lower() for x in ['zebra', 'girafa', 'elefante']) else dic['omni']
                r = dic['viv'] if cl == 'Mammalia' else dic['ovi']
                a = dic['aqua'] if cl in ['Actinopterygii', 'Mollusca'] or any(x in n.lower() for x in ['baleia', 'whale', 'peixe', 'marinho', 'ocean']) else dic['terr']
                out.append({'nome': n, 'sci': item.get('name'), 'foto': item['default_photo']['medium_url'], 'dieta': d, 'repro': r, 'ambiente': a})
        return out
    except: return []

def card(a, k):
    st.markdown(f"""<div class='cc-card'><img src='{a['foto']}' class='img-cc'><div class='common-name'>{a['nome']}</div><div style='text-align:center; font-style:italic;'>{a['sci']}</div><hr><b>{dic['env']}:</b> {a['ambiente']}<br><b>{dic['diet']}:</b> {a['dieta']}<br><b>{dic['rep']}:</b> {a['repro']}</div>""", unsafe_allow_html=True)
    if st.button(f"⭐ {dic['save']}", key=k): st.session_state.zoo.append(a)

# 6. INTERFACE
aba = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas do Mundo", "🌊 Oceanos e Mares", "🔬 Laboratório", "⭐ Favoritos", "⚙️ Definições"])

if aba == "🌲 Florestas do Mundo":
    tipo = st.sidebar.selectbox("Região:", ["Amazónia", "Mata Atlântica", "Taiga Siberiana", "Floresta Russa", "Savana", "Selva Tropical"])
    res = buscar(tipo)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: card(an, f"fl_{i}")

elif aba == "🌊 Oceanos e Mares":
    tipo_oc = st.sidebar.selectbox("Região:", ["Oceano Atlântico", "Oceano Pacífico", "Mar Mediterrâneo", "Recifes de Coral", "Abismo Marinho"])
    res = buscar(tipo_oc)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: card(an, f"oc_{i}")

elif aba == "🌍 Planisfério":
    p = st.selectbox("País:", ["Portugal", "Brasil", "Rússia", "Angola", "Austrália", "Japão"])
    res = buscar(p)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: card(an, f"pl_{i}")

elif aba == "⭐ Favoritos":
    if not st.session_state.zoo: st.write("Lista vazia.")
    else:
        cols = st.columns(3)
        for i, an in enumerate(st.session_state.zoo):
            with cols[i%3]: card(an, f"fav_{i}")

elif aba == "🔬 Laboratório":
    b = st.text_input("🔬:")
    if b:
        res = buscar(b)
        cols = st.columns(3)
        for i, an in enumerate(res):
            with cols[i%3]: card(an, f"lb_{i}")

elif aba == "⚙️ Definições":
    st.session_state.luz = st.toggle("Luz"), value=st.session_state.luz)
    st.session_state.negrito = st.toggle("Negrito", value=st.session_state.negrito)
    st.session_state.cor_fundo = st.selectbox("Fundo", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_fundo))
    st.session_state.cor_card = st.selectbox("Cartões", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_card))
    st.session_state.lingua = st.selectbox("Idioma", list(lang_map.keys()), index=list(lang_map.keys()).index(st.session_state.lingua))
    if st.button("OK"): st.rerun()
