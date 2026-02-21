import streamlit as st
import pandas as pd
import requests
import random

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo Ultimate", page_icon="🌍", layout="wide")

# 2. ESTADOS
for key, val in {
    'luz': False, 'negrito': False, 'cor_fundo': "Preto", 
    'cor_card': "Preto", 'lingua': "Português (Original)", 'zoo': [],
    'codigo_inserido': "", 'expedicao': None
}.items():
    if key not in st.session_state: st.session_state[key] = val

is_premium = st.session_state.codigo_inserido == "6626"
LIMITE = 80 if is_premium else 20

# 3. DICIONÁRIO
lang_map = {
    "Português (Original)": {"code": "pt-BR", "env": "AMBIENTE", "diet": "DIETA", "rep": "REPRODUÇÃO", "save": "Guardar", "del": "Apagar", "clear": "Limpar Tudo", "nav": "Navegação", "forests": "Florestas", "oceans": "Oceanos", "favs": "Coleção", "defs": "Definições", "reg": "Região", "lab": "Laboratório", "tax": "Espécie", "all": "Todos", "mam": "Mamífero", "fish": "Peixe", "rep_t": "Réptil", "bird": "Ave"},
    "Inglês": {"code": "en", "env": "ENVIRONMENT", "diet": "DIET", "rep": "REPRODUCTION", "save": "Save", "del": "Delete", "clear": "Clear All", "nav": "Navigation", "forests": "Forests", "oceans": "Oceans", "favs": "Collection", "defs": "Settings", "reg": "Region", "lab": "Laboratory", "tax": "Species", "all": "All", "mam": "Mammal", "fish": "Fish", "rep_t": "Reptile", "bird": "Bird"}
}
dic = lang_map.get(st.session_state.lingua, lang_map["Português (Original)"])
cores_hex = {"Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", "Verde": "#002b1b", "Amarelo": "#f1c40f", "Roxo": "#4b0082", "Vermelho": "#8b0000"}

# 4. CSS
bg = "#e0e2e6" if st.session_state.luz else cores_hex[st.session_state.cor_fundo]
c_bg = "#ffffff" if st.session_state.luz else cores_hex[st.session_state.cor_card]
txt = "#000000" if (st.session_state.luz or st.session_state.cor_card in ["Branco", "Amarelo"]) else "#ffffff"
border_color = "#ffd700" if is_premium else "#2ea043"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    .cc-card {{ 
        background-color: {c_bg} !important; border-radius: 12px; padding: 20px; 
        border-left: 12px solid {border_color}; margin-bottom: 25px; 
        { "animation: gold-glow 3s infinite; border: 2px solid #ffd700;" if is_premium else "" }
    }}
    .common-name {{ color: {border_color} !important; font-size: 22px; font-weight: bold; text-align: center; }}
    @keyframes gold-glow {{ 0% {{ border-color: #ffd700; }} 50% {{ border-color: #ff8c00; box-shadow: 0 0 15px #ffd700; }} 100% {{ border-color: #ffd700; }} }}
    </style>
    """, unsafe_allow_html=True)

# 5. BUSCA (FILTRANDO PLANTAS - taxon_id=1 é animais no iNaturalist)
def buscar(q, taxon_key="all"):
    taxons = {"all": 1, "mam": 40151, "fish": 47178, "rep_t": 26036, "bird": 3}
    tid = taxons.get(taxon_key, 1)
    url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id={tid}&per_page=30&locale={dic['code']}"
    try:
        res = requests.get(url).json()
        out = []
        for item in res.get('results', []):
            if item.get('default_photo') and item.get('iconic_taxon_name') != 'Plantae':
                n = (item.get('preferred_common_name') or item.get('name')).title()
                cl = item.get('iconic_taxon_name', 'Animal')
                esp = dic['mam'] if cl == 'Mammalia' else dic['fish'] if cl in ['Actinopterygii', 'Elasmobranchii'] else dic['rep_t'] if cl == 'Reptilia' else dic['bird'] if cl == 'Aves' else dic['all']
                out.append({'nome': n, 'sci': item.get('name'), 'foto': item['default_photo']['medium_url'], 'esp': esp, 'amb': 'Natural', 'dieta': 'Variada', 'rep': 'Ovíparo/Vivíparo'})
        return out
    except: return []

def render_card(an, k, fav=False):
    st.markdown(f"""
        <div class='cc-card'>
            <img src='{an['foto']}' style='width:100%; height:200px; object-fit:cover; border-radius:8px;'>
            <div class='common-name'>{an['nome']}</div>
            <div style='text-align:center; font-style:italic; opacity:0.7; font-size: 0.9em;'>{an['sci']}</div>
            <hr style='opacity:0.2;'>
            <b>{dic['tax']}:</b> {an['esp']}
        </div>
    """, unsafe_allow_html=True)
    if not fav:
        if len(st.session_state.zoo) < LIMITE:
            if st.button(f"⭐ {dic['save']}", key=f"sv_{k}"): 
                st.session_state.zoo.append(an); st.rerun()
        else: st.warning("Limite atingido!")
    else:
        if st.button(f"🗑️ {dic['del']}", key=f"dl_{k}"): st.session_state.zoo.pop(k); st.rerun()

# 6. INTERFACE
aba = st.sidebar.radio(dic['nav'], ["🌍 Planisfério", "🌲 " + dic['forests'], "🌊 " + dic['oceans'], "🔬 " + dic['lab'], "⭐ " + dic['favs'], "⚙️ " + dic['defs']])

# Seletor global de espécies
if any(x in aba for x in ["Planisfério", "🌲", "🌊"]):
    especie_sel = st.selectbox(dic['tax'], [dic['all'], dic['mam'], dic['fish'], dic['rep_t'], dic['bird']])
    esp_key = "all"
    if especie_sel == dic['mam']: esp_key = "mam"
    elif especie_sel == dic['fish']: esp_key = "fish"
    elif especie_sel == dic['rep_t']: esp_key = "rep_t"
    elif especie_sel == dic['bird']: esp_key = "bird"

if aba == "🌍 Planisfério":
    st.map(pd.DataFrame({'lat': [38.7, -15.7, 60.0], 'lon': [-9.1, -47.8, 90.0]}))
    p = st.selectbox(dic['reg'], ["Portugal", "Brasil", "Rússia", "Angola"])
    res = buscar(p, esp_key)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_card(an, i)

elif "🌲" in aba:
    st.map(pd.DataFrame({'lat': [-3.4, 63.7, -23.5], 'lon': [-62.2, 95.8, -46.6]}))
    op = st.selectbox(dic['reg'], ["Amazonia", "Taiga", "Atlantic Forest"])
    res = buscar(op, esp_key)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_card(an, i)

elif "🌊" in aba:
    st.map(pd.DataFrame({'lat': [-8.7, 14.5, -18.2], 'lon': [-145.0, -30.0, 147.4]}))
    op = st.selectbox(dic['reg'], ["Pacific Ocean", "Atlantic Ocean", "Coral Reef"])
    res = buscar(op, esp_key)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_card(an, i)

elif "🔬" in aba:
    st.title(dic['lab'])
    b = st.text_input("Pesquisar:")
    if b:
        res = buscar(b)
        cols = st.columns(3)
        for i, an in enumerate(res):
            with cols[i%3]: render_card(an, i)

elif "⭐" in aba:
    st.title(("💎 " if is_premium else "⭐ ") + dic['favs'])
    st.write(f"Capacidade: {len(st.session_state.zoo)} / {LIMITE}")
    st.progress(min(len(st.session_state.zoo)/LIMITE, 1.0))
    if st.button(dic['clear']): st.session_state.zoo = []; st.rerun()
    cols = st.columns(3)
    for i, an in enumerate(st.session_state.zoo):
        with cols[i%3]: render_card(an, i, fav=True)

elif "⚙️" in aba:
    st.subheader("Configurações Premium")
    if not is_premium:
        st.session_state.codigo_inserido = st.text_input("Inserir Código:", type="password")
    else:
        st.success("💎 MODO PREMIUM ATIVADO")
        if st.button("❌ APAGAR PREMIUM (REMOVER CÓDIGO)"):
            st.session_state.codigo_inserido = ""
            st.rerun()
    
    st.session_state.luz = st.toggle("Modo Claro")
    st.session_state.lingua = st.selectbox("Idioma", list(lang_map.keys()))
    if st.button("Aplicar"): st.rerun()
