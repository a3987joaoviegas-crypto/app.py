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

# 3. DICIONÁRIO DE LÍNGUAS
lang_map = {
    "Português (Original)": {"code": "pt-BR", "env": "AMBIENTE", "diet": "DIETA", "rep": "REPRODUÇÃO", "save": "Guardar", "del": "Apagar", "clear": "Limpar Tudo", "nav": "Navegação", "forests": "Florestas do Mundo", "oceans": "Oceanos e Mares", "favs": "Favoritos", "defs": "Definições", "reg": "Região", "lab": "Laboratório", "carn": "Carnívoro", "herb": "Herbívoro", "omni": "Omnívoro", "viv": "Vivíparo", "ovi": "Ovíparo", "terr": "Terrestre", "aqua": "Aquático"},
    "Inglês": {"code": "en", "env": "ENVIRONMENT", "diet": "DIET", "rep": "REPRODUCTION", "save": "Save", "del": "Delete", "clear": "Clear All", "nav": "Navigation", "forests": "World Forests", "oceans": "Oceans and Seas", "favs": "Favorites", "defs": "Settings", "reg": "Region", "lab": "Laboratory", "carn": "Carnivore", "herb": "Herbivore", "omni": "Omnivore", "viv": "Viviparous", "ovi": "Oviparous", "terr": "Terrestrial", "aqua": "Aquatic"},
    "Russo": {"code": "ru", "env": "ОКРУЖАЮЩАЯ СРЕДА", "diet": "ПИТАНИЕ", "rep": "РЕПРОДУКЦИЯ", "save": "Сохранить", "del": "Удалить", "clear": "Очистить все", "nav": "Навигация", "forests": "Леса мира", "oceans": "Океаны и моря", "favs": "Избранное", "defs": "Настройки", "reg": "Область", "lab": "Лаборатория", "carn": "Хищник", "herb": "Травоядный", "omni": "Всеядный", "viv": "Живородящие", "ovi": "Яйцекладущие", "terr": "Земной", "aqua": "Водный"},
    "Crioulo": {"code": "pt-PT", "env": "AMBIENTI", "diet": "DIETA", "rep": "REPRODUSON", "save": "Guarda", "del": "Paga", "clear": "Limpia Tudo", "nav": "Navegason", "forests": "Floresta di Mundu", "oceans": "Osianu ku Mar", "favs": "Favoritus", "defs": "Definisons", "reg": "Rejion", "lab": "Laboratoriu", "carn": "Karnivoru", "herb": "Erbivoru", "omni": "Omnivoru", "viv": "Vivíparu", "ovi": "Ovíparu", "terr": "Terrestre", "aqua": "Akuatiku"}
}
dic = lang_map.get(st.session_state.lingua, lang_map["Português (Original)"])
cores_hex = {"Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", "Verde": "#002b1b", "Amarelo": "#f1c40f", "Roxo": "#4b0082", "Vermelho": "#8b0000"}

# 4. CSS
bg = "#e0e2e6" if st.session_state.luz else cores_hex[st.session_state.cor_fundo]
c_bg = "#ffffff" if st.session_state.luz else cores_hex[st.session_state.cor_card]
txt = "#000000" if (st.session_state.luz or st.session_state.cor_card in ["Branco", "Amarelo"]) else "#ffffff"

st.markdown(f"""
    <style>
    @keyframes move {{ from {{ background-position: 0 0; }} to {{ background-position: 100% 100%; }} }}
    .stApp {{ background-color: {bg}; background-image: radial-gradient(circle, rgba(0,0,0,0.05) 1px, transparent 1px); background-size: 60px 60px; animation: move 120s linear infinite; color: {txt}; }}
    .cc-card {{ background: {c_bg}; border-radius: 12px; padding: 20px; border-left: 12px solid #2ea043; margin-bottom: 25px; color: {txt} !important; box-shadow: 0px 5px 15px rgba(0,0,0,0.3); }}
    .common-name {{ color: #2ea043 !important; font-size: 24px; text-align: center; font-weight: bold; }}
    .sci-name {{ text-align: center; font-style: italic; opacity: 0.8; margin-bottom: 10px; }}
    .separator {{ border: 1px solid #2ea043; margin: 15px 0; opacity: 0.4; }}
    * {{ font-weight: {"bold" if st.session_state.negrito else "normal"} !important; }}
    </style>
    """, unsafe_allow_html=True)

# 5. MOTOR DE BUSCA
def buscar(q):
    url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=70&locale={dic['code']}"
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
                out.append({'nome': n, 'sci': item.get('name'), 'foto': item['default_photo']['medium_url'], 'dieta': d, 'rep': r, 'amb': a})
        return out
    except: return []

def render_card(an, k, fav=False):
    st.markdown(f"""
        <div class='cc-card'>
            <img src='{an['foto']}' style='width:100%; height:220px; object-fit:cover; border-radius:8px;'>
            <div class='common-name'>{an['nome']}</div>
            <div class='sci-name'>{an['sci']}</div>
            <div class='separator'></div>
            <b>{dic['env']}:</b> {an['amb']}<br>
            <b>{dic['diet']}:</b> {an['dieta']}<br>
            <b>{dic['rep']}:</b> {an['rep']}
        </div>
    """, unsafe_allow_html=True)
    if not fav:
        if st.button(f"⭐ {dic['save']}", key=f"sv_{k}"): st.session_state.zoo.append(an)
    else:
        if st.button(f"🗑️ {dic['del']}", key=f"dl_{k}"): 
            st.session_state.zoo.pop(k); st.rerun()

# 6. INTERFACE
aba = st.sidebar.radio(dic['nav'], ["🌍 Planisfério", "🌲 " + dic['forests'], "🌊 " + dic['oceans'], "🔬 " + dic['lab'], "⭐ " + dic['favs'], "⚙️ " + dic['defs']])

if aba == "🌍 Planisfério":
    st.map(pd.DataFrame({'lat': [38.7, -15.7, 60.0, -22.9], 'lon': [-9.1, -47.8, 90.0, -43.2]}))
    p = st.selectbox(dic['reg'], ["Portugal", "Brasil", "Rússia", "Angola"])
    res = buscar(p)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_card(an, i)

elif "🌲" in aba:
    # Planisfério das Florestas (Amazónia, Mata Atlântica, Taiga, Floresta Russa, Savana)
    st.map(pd.DataFrame({'lat': [-3.4, -23.5, 63.7, 60.0, -13.1], 'lon': [-62.2, -46.6, 95.8, 40.0, 27.8]}))
    op = st.selectbox(dic['reg'], ["Amazonia", "Atlantic Forest", "Taiga", "Russian Forest", "Savanna"])
    res = buscar(op)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_card(an, i)

elif "🌊" in aba:
    # Planisfério dos Mares e Oceanos (Pacífico, Atlântico, Coral, Abismo)
    st.map(pd.DataFrame({'lat': [-8.7, 14.5, -18.2, 0.0], 'lon': [-145.0, -30.0, 147.4, 10.0]}))
    op = st.selectbox(dic['reg'], ["Pacific Ocean", "Atlantic Ocean", "Coral Reef", "Deep Sea"])
    res = buscar(op)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_card(an, i)

elif "🔬" in aba:
    st.title(dic['lab'])
    b = st.text_input("🔍:")
    if b:
        res = buscar(b)
        cols = st.columns(3)
        for i, an in enumerate(res):
            with cols[i%3]: render_card(an, i)

elif "⭐" in aba:
    st.title(dic['favs'])
    if st.button(dic['clear']): st.session_state.zoo = []; st.rerun()
    cols = st.columns(3)
    for i, an in enumerate(st.session_state.zoo):
        with cols[i%3]: render_card(an, i, fav=True)

elif "⚙️" in aba:
    st.session_state.luz = st.toggle("Luminosidade", value=st.session_state.luz)
    st.session_state.negrito = st.toggle("Negrito", value=st.session_state.negrito)
    st.session_state.cor_card = st.selectbox("Cartão", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_card))
    st.session_state.lingua = st.selectbox("Idioma", list(lang_map.keys()), index=list(lang_map.keys()).index(st.session_state.lingua))
    if st.button("OK"): st.rerun()
