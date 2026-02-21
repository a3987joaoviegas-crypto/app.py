import streamlit as st
import pandas as pd
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
    "Português (Original)": {"code": "pt-BR", "env": "AMBIENTE", "diet": "DIETA", "rep": "REPRODUÇÃO", "save": "Guardar", "del": "Apagar", "clear": "Limpar Tudo", "carn": "Carnívoro", "herb": "Herbívoro", "omni": "Omnívoro", "viv": "Vivíparo", "ovi": "Ovíparo", "terr": "Terrestre", "aqua": "Aquático"},
    "Inglês": {"code": "en", "env": "ENVIRONMENT", "diet": "DIET", "rep": "REPRODUCTION", "save": "Save", "del": "Delete", "clear": "Clear All", "carn": "Carnivore", "herb": "Herbivore", "omni": "Omnivore", "viv": "Viviparous", "ovi": "Oviparous", "terr": "Terrestrial", "aqua": "Aquatic"},
    "Crioulo": {"code": "pt-PT", "env": "AMBIENTI", "diet": "DIETA", "rep": "REPRODUSON", "save": "Guarda", "del": "Paga", "clear": "Limpia Tudo", "carn": "Karnivoru", "herb": "Erbivoru", "omni": "Omnivoru", "viv": "Vivíparu", "ovi": "Ovíparu", "terr": "Terrestre", "aqua": "Akuatiku"}
}
# (Outros idiomas mantidos internamente)
dic = lang_map.get(st.session_state.lingua, lang_map["Português (Original)"])

# 4. CSS DINÂMICO
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
        border-left: 8px solid #2ea043; margin-bottom: 25px; 
        color: {card_text} !important; 
    }}
    .img-cc {{ width: 100%; height: 220px; object-fit: cover; border-radius: 8px; }}
    .common-name {{ color: #2ea043 !important; font-size: 22px; text-align: center; font-weight: bold; }}
    * {{ font-weight: {"bold" if st.session_state.negrito else "normal"} !important; }}
    </style>
    """, unsafe_allow_html=True)

# 5. MOTOR DE BUSCA
def buscar(query):
    q_map = {"Amazónia": "Amazonia", "Mata Atlântica": "Atlantic Forest", "Taiga Siberiana": "Taiga", "Floresta Russa": "Russia fauna", "Savana": "Savanna", "Abismo Marinho": "Bathyal zone"}
    q_final = q_map.get(query, query)
    url = f"https://api.inaturalist.org/v1/taxa?q={q_final}&taxon_id=1&per_page=70&locale={dic['code']}"
    try:
        res = requests.get(url).json()
        out = []
        for item in res.get('results', []):
            if item.get('default_photo'):
                n = (item.get('preferred_common_name') or item.get('name')).title()
                cl = item.get('iconic_taxon_name', 'Animal')
                d, r, a = dic['omni'], (dic['viv'] if cl == 'Mammalia' else dic['ovi']), dic['terr']
                if cl in ['Actinopterygii'] or "marinho" in query.lower(): a = dic['aqua']
                out.append({'nome': n, 'sci': item.get('name'), 'foto': item['default_photo']['medium_url'], 'dieta': d, 'repro': r, 'ambiente': a})
        return out
    except: return []

# 6. INTERFACE
aba = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas do Mundo", "🌊 Oceanos e Mares", "🔬 Laboratório", "⭐ Favoritos", "⚙️ Definições"])

if aba == "⭐ Favoritos":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.title("⭐ " + dic['save'] + "s")
    with col_t2: 
        if st.button(dic['clear']): 
            st.session_state.zoo = []
            st.rerun()
    
    if not st.session_state.zoo: st.write("Lista vazia.")
    else:
        cols = st.columns(3)
        for i, an in enumerate(st.session_state.zoo):
            with cols[i%3]:
                st.markdown(f"<div class='cc-card'><img src='{an['foto']}' class='img-cc'><div class='common-name'>{an['nome']}</div><hr><b>{dic['env']}:</b> {an['ambiente']}<br><b>{dic['diet']}:</b> {an['dieta']}</div>", unsafe_allow_html=True)
                if st.button(f"🗑️ {dic['del']}", key=f"del_{i}"):
                    st.session_state.zoo.pop(i)
                    st.rerun()

elif aba == "🌲 Florestas do Mundo":
    tipo = st.sidebar.selectbox("Região:", ["Amazónia", "Mata Atlântica", "Taiga Siberiana", "Floresta Russa", "Savana", "Selva Tropical"])
    res = buscar(tipo)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]:
            st.markdown(f"<div class='cc-card'><img src='{an['foto']}' class='img-cc'><div class='common-name'>{an['nome']}</div><hr><b>{dic['env']}:</b> {an['ambiente']}</div>", unsafe_allow_html=True)
            if st.button(f"⭐ {dic['save']}", key=f"sv_{i}"): st.session_state.zoo.append(an)

elif aba == "🌊 Oceanos e Mares":
    tipo_oc = st.sidebar.selectbox("Região:", ["Oceano Atlântico", "Oceano Pacífico", "Mar Mediterrâneo", "Recifes de Coral", "Abismo Marinho"])
    res = buscar(tipo_oc)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]:
            st.markdown(f"<div class='cc-card'><img src='{an['foto']}' class='img-cc'><div class='common-name'>{an['nome']}</div><hr><b>{dic['env']}:</b> {an['ambiente']}</div>", unsafe_allow_html=True)
            if st.button(f"⭐ {dic['save']}", key=f"oc_{i}"): st.session_state.zoo.append(an)

elif aba == "🌍 Planisfério":
    p = st.selectbox("País:", ["Portugal", "Brasil", "Rússia", "Angola", "Austrália"])
    res = buscar(p)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]:
            st.markdown(f"<div class='cc-card'><img src='{an['foto']}' class='img-cc'><div class='common-name'>{an['nome']}</div></div>", unsafe_allow_html=True)
            if st.button(f"⭐ {dic['save']}", key=f"pl_{i}"): st.session_state.zoo.append(an)

elif aba == "🔬 Laboratório":
    b = st.text_input("🔬:")
    if b:
        res = buscar(b)
        cols = st.columns(3)
        for i, an in enumerate(res):
            with cols[i%3]:
                st.markdown(f"<div class='cc-card'><img src='{an['foto']}' class='img-cc'><div class='common-name'>{an['nome']}</div></div>", unsafe_allow_html=True)
                if st.button(f"⭐ {dic['save']}", key=f"lb_{i}"): st.session_state.zoo.append(an)

elif aba == "⚙️ Definições":
    st.session_state.luz = st.toggle("Luminosidade", value=st.session_state.luz)
    st.session_state.negrito = st.toggle("Negrito", value=st.session_state.negrito)
    st.session_state.cor_fundo = st.selectbox("Fundo", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_fundo))
    st.session_state.cor_card = st.selectbox("Cartões", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_card))
    st.session_state.lingua = st.selectbox("Idioma", list(lang_map.keys()), index=list(lang_map.keys()).index(st.session_state.lingua))
    if st.button("OK"): st.rerun()
