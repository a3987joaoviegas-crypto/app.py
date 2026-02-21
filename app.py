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

# 3. DICIONÁRIOS
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
    .common-name {{ color: {border_color} !important; font-size: 24px; text-align: center; font-weight: bold; }}
    @keyframes gold-glow {{ 0% {{ border-color: #ffd700; }} 50% {{ border-color: #ff8c00; box-shadow: 0 0 10px #ffd700; }} 100% {{ border-color: #ffd700; }} }}
    </style>
    """, unsafe_allow_html=True)

# 5. MOTOR DE BUSCA
def buscar(q):
    url = f"https://api.inaturalist.org/v1/taxa?q={q}&per_page=30&locale={dic['code']}"
    try:
        res = requests.get(url).json()
        out = []
        for item in res.get('results', []):
            if item.get('default_photo'):
                n = (item.get('preferred_common_name') or item.get('name')).title()
                out.append({'nome': n, 'sci': item.get('name'), 'foto': item['default_photo']['medium_url'], 'esp': 'Animal', 'amb': 'Global', 'dieta': 'Omnívoro', 'rep': 'Ovíparo'})
        return out
    except: return []

def render_card(an, k, fav=False):
    st.markdown(f"""
        <div class='cc-card'>
            <img src='{an['foto']}' style='width:100%; height:200px; object-fit:cover; border-radius:8px;'>
            <div class='common-name'>{an['nome']}</div>
            <div style='text-align:center; font-style:italic; opacity:0.8;'>{an['sci']}</div>
            <hr style='border: 0.5px solid {border_color}; opacity: 0.3;'>
            <b>{dic['tax']}:</b> {an['esp']}
        </div>
    """, unsafe_allow_html=True)
    
    if not fav:
        if len(st.session_state.zoo) < LIMITE:
            if st.button(f"⭐ {dic['save']}", key=f"sv_{k}"): 
                st.session_state.zoo.append(an)
                st.rerun()
        else:
            st.error(f"Limite atingido ({LIMITE})")
    else:
        if st.button(f"🗑️ {dic['del']}", key=f"dl_{k}"): 
            st.session_state.zoo.pop(k)
            st.rerun()

# 6. INTERFACE
aba = st.sidebar.radio(dic['nav'], ["🌍 Planisfério", "🌲 " + dic['forests'], "🌊 " + dic['oceans'], "🔬 " + dic['lab'], "⭐ " + dic['favs'], "⚙️ " + dic['defs']])

if aba == "🌍 Planisfério":
    st.map(pd.DataFrame({'lat': [38.7, -15.7, 60.0], 'lon': [-9.1, -47.8, 90.0]}))
    p = st.selectbox(dic['reg'], ["Portugal", "Brasil", "Rússia", "Angola"])
    res = buscar(p)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_card(an, i)

elif "⭐" in aba:
    st.title(("💎 " if is_premium else "⭐ ") + dic['favs'])
    # Barra de Capacidade
    progresso = len(st.session_state.zoo) / LIMITE
    st.write(f"Capacidade da Reserva: {len(st.session_state.zoo)} / {LIMITE}")
    st.progress(min(progresso, 1.0))
    
    if st.button(dic['clear']): st.session_state.zoo = []; st.rerun()
    cols = st.columns(3)
    for i, an in enumerate(st.session_state.zoo):
        with cols[i%3]: render_card(an, i, fav=True)

elif "⚙️" in aba:
    st.session_state.codigo_inserido = st.text_input("Código de Desbloqueio:", type="password")
    if is_premium: st.success(f"💎 MODO PREMIUM: Limite expandido para {LIMITE} slots!")
    else: st.info(f"Modo Normal: Limite de {LIMITE} slots.")
    
    st.session_state.luz = st.toggle("Luz")
    st.session_state.lingua = st.selectbox("Língua", list(lang_map.keys()))
    if st.button("Aplicar"): st.rerun()
