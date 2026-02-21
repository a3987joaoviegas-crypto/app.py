import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

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
    "Português (Original)": {"code": "pt-BR", "env": "AMBIENTE", "diet": "DIETA", "rep": "REPRODUÇÃO", "save": "Guardar", "del": "Apagar", "clear": "Limpar Tudo", "carn": "Carnívoro", "herb": "Herbívoro", "omni": "Omnívoro", "viv": "Vivíparo", "ovi": "Ovíparo", "terr": "Terrestre", "aqua": "Aquático"},
    "Inglês": {"code": "en", "env": "ENVIRONMENT", "diet": "DIET", "rep": "REPRODUCTION", "save": "Save", "del": "Delete", "clear": "Clear All", "carn": "Carnivore", "herb": "Herbivore", "omni": "Omnivore", "viv": "Viviparous", "ovi": "Oviparous", "terr": "Terrestrial", "aqua": "Aquatic"},
    "Crioulo": {"code": "pt-PT", "env": "AMBIENTI", "diet": "DIETA", "rep": "REPRODUSON", "save": "Guarda", "del": "Paga", "clear": "Limpia Tudo", "carn": "Karnivoru", "herb": "Erbivoru", "omni": "Omnivoru", "viv": "Vivíparu", "ovi": "Ovíparu", "terr": "Terrestre", "aqua": "Akuatiku"}
}
dic = lang_map.get(st.session_state.lingua, lang_map["Português (Original)"])

# 4. CSS COM ANIMAÇÃO E CARTÃO DE CIDADÃO
bg = "#e0e2e6" if st.session_state.luz else cores_hex[st.session_state.cor_fundo]
c_bg = "#ffffff" if st.session_state.luz else cores_hex[st.session_state.cor_card]
main_text = "#000000" if (st.session_state.luz or st.session_state.cor_fundo in ["Branco", "Amarelo"]) else "#ffffff"
card_text = "#000000" if (st.session_state.luz or st.session_state.cor_card in ["Branco", "Amarelo"]) else "#ffffff"

st.markdown(f"""
    <style>
    @keyframes move {{ from {{ background-position: 0 0; }} to {{ background-position: 100% 100%; }} }}
    .stApp {{ 
        background-color: {bg}; color: {main_text}; 
        background-image: radial-gradient(circle, rgba(0,0,0,0.05) 1px, transparent 1px);
        background-size: 60px 60px; animation: move 120s linear infinite;
    }}
    .cc-card {{ 
        background: {c_bg}; border-radius: 12px; padding: 20px; 
        border-left: 10px solid #2ea043; margin-bottom: 25px; 
        color: {card_text} !important; box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    }}
    .cc-card b, .cc-card div {{ color: {card_text} !important; }}
    .img-cc {{ width: 100%; height: 220px; object-fit: cover; border-radius: 8px; }}
    .common-name {{ color: #2ea043 !important; font-size: 22px; text-align: center; font-weight: bold; margin-bottom: 0px; }}
    .sci-name {{ text-align: center; font-style: italic; font-size: 0.9em; opacity: 0.8; margin-bottom: 10px; }}
    * {{ font-weight: {"bold" if st.session_state.negrito else "normal"} !important; }}
    </style>
    """, unsafe_allow_html=True)

# 5. MOTOR DE BUSCA
def buscar(query):
    q_map = {"Amazónia": "Amazonia", "Mata Atlântica": "Atlantic Forest", "Taiga Siberiana": "Taiga", "Floresta Russa": "Russia fauna", "Abismo Marinho": "Bathyal zone"}
    q_final = q_map.get(query, query)
    url = f"https://api.inaturalist.org/v1/taxa?q={q_final}&taxon_id=1&per_page=70&locale={dic['code']}"
    try:
        res = requests.get(url).json()
        out = []
        for item in res.get('results', []):
            if item.get('default_photo'):
                n = (item.get('preferred_common_name') or item.get('name')).title()
                sci = item.get('name')
                cl = item.get('iconic_taxon_name', 'Animal')
                # Lógica biológica básica
                d = dic['carn'] if any(x in n.lower() for x in ['leão', 'lion', 'tubarão', 'shark', 'lobo', 'orca']) else dic['herb'] if any(x in n.lower() for x in ['zebra', 'girafa', 'elefante']) else dic['omni']
                r = dic['viv'] if cl == 'Mammalia' else dic['ovi']
                a = dic['aqua'] if cl in ['Actinopterygii', 'Mollusca'] or any(x in n.lower() for x in ['baleia', 'whale', 'peixe', 'marinho', 'ocean']) else dic['terr']
                out.append({'nome': n, 'sci': sci, 'foto': item['default_photo']['medium_url'], 'dieta': d, 'repro': r, 'ambiente': a})
        return out
    except: return []

def render_card(an, key_id, mode="search"):
    st.markdown(f"""
        <div class='cc-card'>
            <img src='{an['foto']}' class='img-cc'>
            <div class='common-name'>{an['nome']}</div>
            <div class='sci-name'>{an['sci']}</div>
            <hr style='opacity:0.2;'>
            <b>{dic['env']}:</b> {an['ambiente']}<br>
            <b>{dic['diet']}:</b> {an['dieta']}<br>
            <b>{dic['rep']}:</b> {an['repro']}
        </div>
    """, unsafe_allow_html=True)
    if mode == "search":
        if st.button(f"⭐ {dic['save']}", key=f"btn_{key_id}"):
            st.session_state.zoo.append(an)
    else:
        if st.button(f"🗑️ {dic['del']}", key=f"del_{key_id}"):
            st.session_state.zoo.pop(key_id)
            st.rerun()

# 6. INTERFACE
aba = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas do Mundo", "🌊 Oceanos e Mares", "🔬 Laboratório", "⭐ Favoritos", "⚙️ Definições"])

if aba == "⭐ Favoritos":
    col1, col2 = st.columns([3,1])
    col1.title("⭐ " + dic['save'] + "s")
    if col2.button(dic['clear']):
        st.session_state.zoo = []
        st.rerun()
    if not st.session_state.zoo: st.write("Vazio.")
    else:
        cols = st.columns(3)
        for i, an in enumerate(st.session_state.zoo):
            with cols[i%3]: render_card(an, i, mode="fav")

elif aba == "🌲 Florestas do Mundo":
    tipo = st.sidebar.selectbox("Região:", ["Amazónia", "Mata Atlântica", "Taiga Siberiana", "Floresta Russa", "Savana", "Selva Tropical"])
    res = buscar(tipo)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_card(an, f"fl_{i}")

elif aba == "🌊 Oceanos e Mares":
    tipo_oc = st.sidebar.selectbox("Região:", ["Oceano Atlântico", "Oceano Pacífico", "Mar Mediterrâneo", "Recifes de Coral", "Abismo Marinho"])
    res = buscar(tipo_oc)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_card(an, f"oc_{i}")

elif aba == "🌍 Planisfério":
    p = st.selectbox("País:", ["Portugal", "Brasil", "Rússia", "Angola", "Austrália"])
    res = buscar(p)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_card(an, f"pl_{i}")

elif aba == "🔬 Laboratório":
    b = st.text_input("🔬:")
    if b:
        res = buscar(b)
        cols = st.columns(3)
        for i, an in enumerate(res):
            with cols[i%3]: render_card(an, f"lb_{i}")

elif aba == "⚙️ Definições":
    st.session_state.luz = st.toggle("Luminosidade", value=st.session_state.luz)
    st.session_state.negrito = st.toggle("Negrito", value=st.session_state.negrito)
    st.session_state.cor_fundo = st.selectbox("Fundo", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_fundo))
    st.session_state.cor_card = st.selectbox("Cartões", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_card))
    st.session_state.lingua = st.selectbox("Idioma", list(lang_map.keys()), index=list(lang_map.keys()).index(st.session_state.lingua))
    if st.button("OK"): st.rerun()
