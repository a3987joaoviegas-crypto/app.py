import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo Ultimate", page_icon="🌍", layout="wide")

# 2. ESTADOS
for key, val in {
    'luz': False, 'negrito': False, 'cor_fundo': "Preto", 
    'cor_card': "Preto", 'lingua': "Português (Original)", 'zoo': [],
    'codigo_inserido': ""
}.items():
    if key not in st.session_state: st.session_state[key] = val

# Verificação Premium
is_premium = st.session_state.codigo_inserido == "6626"

# 3. DICIONÁRIOS
lang_map = {
    "Português (Original)": {"code": "pt-BR", "env": "AMBIENTE", "diet": "DIETA", "rep": "REPRODUÇÃO", "save": "Guardar", "del": "Apagar", "clear": "Limpar Tudo", "nav": "Navegação", "forests": "Florestas do Mundo", "oceans": "Oceanos e Mares", "favs": "Coleção", "defs": "Definições", "reg": "Região", "lab": "Laboratório", "carn": "Carnívoro", "herb": "Herbívoro", "omni": "Omnívoro", "viv": "Vivíparo", "ovi": "Ovíparo", "terr": "Terrestre", "aqua": "Aquático", "tax": "Espécie", "all": "Todos", "mam": "Mamífero", "fish": "Peixe", "rep_t": "Réptil", "bird": "Ave"},
    "Inglês": {"code": "en", "env": "ENVIRONMENT", "diet": "DIET", "rep": "REPRODUCTION", "save": "Save", "del": "Delete", "clear": "Clear All", "nav": "Navigation", "forests": "World Forests", "oceans": "Oceans and Seas", "favs": "Collection", "defs": "Settings", "reg": "Region", "lab": "Laboratory", "carn": "Carnivore", "herb": "Herbivore", "omni": "Omnivore", "viv": "Viviparous", "ovi": "Oviparous", "terr": "Terrestrial", "aqua": "Aquatic", "tax": "Species", "all": "All", "mam": "Mammal", "fish": "Fish", "rep_t": "Reptile", "bird": "Bird"},
    "Russo": {"code": "ru", "env": "ОКРУЖАЮЩАЯ СРЕДА", "diet": "ПИТАНИЕ", "rep": "РЕПРОДУКЦИЯ", "save": "Сохранить", "del": "Удалить", "clear": "Очистить все", "nav": "Навигация", "forests": "Леса мира", "oceans": "Океаны и моря", "favs": "Избранное", "defs": "Настройки", "reg": "Область", "lab": "Лаборатория", "carn": "Хищник", "herb": "Травоядный", "omni": "Всеядный", "viv": "Живородящие", "ovi": "Яйцекладущие", "terr": "Земной", "aqua": "Водный", "tax": "Вид", "all": "Все", "mam": "Млекопитающее", "fish": "Рыба", "rep_t": "Рептилия", "bird": "Птица"}
}
dic = lang_map.get(st.session_state.lingua, lang_map["Português (Original)"])
cores_hex = {"Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", "Verde": "#002b1b", "Amarelo": "#f1c40f", "Roxo": "#4b0082", "Vermelho": "#8b0000"}

# 4. CSS (CARTÃO DE CIDADÃO + PREMIUM)
bg = "#e0e2e6" if st.session_state.luz else cores_hex[st.session_state.cor_fundo]
c_bg = "#ffffff" if st.session_state.luz else cores_hex[st.session_state.cor_card]
txt = "#000000" if (st.session_state.luz or st.session_state.cor_card in ["Branco", "Amarelo"]) else "#ffffff"
border_color = "#ffd700" if is_premium else "#2ea043"

st.markdown(f"""
    <style>
    @keyframes move {{ from {{ background-position: 0 0; }} to {{ background-position: 100% 100%; }} }}
    @keyframes gold-glow {{ 0% {{ border-color: #ffd700; }} 50% {{ border-color: #ff8c00; box-shadow: 0 0 15px #ffd700; }} 100% {{ border-color: #ffd700; }} }}
    .stApp {{ background-color: {bg}; background-image: radial-gradient(circle, rgba(0,0,0,0.05) 1px, transparent 1px); background-size: 60px 60px; animation: move 120s linear infinite; color: {txt}; }}
    
    .cc-card {{ 
        background-color: {c_bg} !important; 
        border-radius: 12px; 
        padding: 20px; 
        border-left: 12px solid {border_color}; 
        margin-bottom: 25px; 
        box-shadow: 0px 5px 15px rgba(0,0,0,0.3);
        color: {txt} !important;
        { "animation: gold-glow 3s infinite; border: 2px solid #ffd700; border-left: 12px solid #ffd700;" if is_premium else "" }
    }}
    .common-name {{ color: {border_color} !important; font-size: 24px; text-align: center; font-weight: bold; margin-top: 10px; }}
    .sci-name {{ text-align: center; font-style: italic; opacity: 0.8; color: {txt}; }}
    .separator {{ border: 1px solid {border_color}; margin: 15px 0; opacity: 0.4; }}
    .premium-badge {{ color: #ffd700; font-weight: bold; text-align: center; font-size: 0.9em; margin-bottom: 5px; }}
    .code-box {{ background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; border: 1px dashed {border_color}; }}
    * {{ font-weight: {"bold" if st.session_state.negrito else "normal"} !important; }}
    </style>
    """, unsafe_allow_html=True)

# 5. MOTOR DE BUSCA
def buscar(q, taxon_key="all"):
    taxons = {"all": 1, "mam": 40151, "fish": 47178, "rep_t": 26036, "bird": 3}
    tid = taxons.get(taxon_key, 1)
    url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id={tid}&per_page=70&locale={dic['code']}"
    try:
        res = requests.get(url).json()
        out = []
        for item in res.get('results', []):
            if item.get('default_photo'):
                n = (item.get('preferred_common_name') or item.get('name')).title()
                cl = item.get('iconic_taxon_name', 'Animal')
                esp = dic['mam'] if cl == 'Mammalia' else dic['fish'] if cl in ['Actinopterygii', 'Elasmobranchii'] else dic['rep_t'] if cl == 'Reptilia' else dic['bird'] if cl == 'Aves' else dic['all']
                out.append({'nome': n, 'sci': item.get('name'), 'foto': item['default_photo']['medium_url'], 'dieta': dic['omni'], 'rep': dic['ovi'], 'amb': dic['terr'], 'esp': esp})
        return out
    except: return []

def render_card(an, k, fav=False):
    p_tag = f"<div class='premium-badge'>💎 PREMIUM</div>" if is_premium else ""
    st.markdown(f"""
        <div class='cc-card'>
            {p_tag}
            <img src='{an['foto']}' style='width:100%; height:220px; object-fit:cover; border-radius:8px;'>
            <div class='common-name'>{an['nome']}</div>
            <div class='sci-name'>{an['sci']}</div>
            <div class='separator'></div>
            <div style='line-height: 1.6;'>
                <b>{dic['tax']}:</b> {an['esp']}<br>
                <b>{dic['env']}:</b> {an['amb']}<br>
                <b>{dic['diet']}:</b> {an['dieta']}<br>
                <b>{dic['rep']}:</b> {an['rep']}
            </div>
        </div>
    """, unsafe_allow_html=True)
    if not fav:
        if st.button(f"⭐ {dic['save']}", key=f"sv_{k}"): st.session_state.zoo.append(an)
    else:
        if st.button(f"🗑️ {dic['del']}", key=f"dl_{k}"): 
            st.session_state.zoo.pop(k); st.rerun()

# 6. INTERFACE
aba = st.sidebar.radio(dic['nav'], ["🌍 Planisfério", "🌲 " + dic['forests'], "🌊 " + dic['oceans'], "🔬 " + dic['lab'], "⭐ " + dic['favs'], "⚙️ " + dic['defs']])

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
    st.map(pd.DataFrame({'lat': [-3.4, 60.0, -23.5], 'lon': [-62.2, 40.0, -46.6]}))
    op = st.selectbox(dic['reg'], ["Amazonia", "Russian Forest", "Atlantic Forest", "Taiga"])
    res = buscar(op, esp_key)
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_card(an, i)

elif "🌊" in aba:
    st.map(pd.DataFrame({'lat': [-8.7, 14.5, -18.2], 'lon': [-145.0, -30.0, 147.4]}))
    op = st.selectbox(dic['reg'], ["Pacific Ocean", "Atlantic Ocean", "Coral Reef", "Deep Sea"])
    res = buscar(op, esp_key)
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
    st.title(("💎 " if is_premium else "⭐ ") + dic['favs'])
    if is_premium:
        c1, c2 = st.columns(2)
        c1.metric("🐾 Total", len(st.session_state.zoo))
        mams = len([x for x in st.session_state.zoo if x['esp'] == dic['mam']])
        c2.metric("🦁 " + dic['mam'] + "s", mams)
    
    if st.button(dic['clear']): st.session_state.zoo = []; st.rerun()
    cols = st.columns(3)
    for i, an in enumerate(st.session_state.zoo):
        with cols[i%3]: render_card(an, i, fav=True)

elif "⚙️" in aba:
    st.markdown("<div class='code-box'>", unsafe_allow_html=True)
    st.session_state.codigo_inserido = st.text_input("Inserir Código Premium:", type="password", help="Insere 6626 para desbloquear")
    if is_premium: st.success("💎 MODO PREMIUM ATIVADO")
    st.markdown("</div><br>", unsafe_allow_html=True)
    
    st.session_state.luz = st.toggle("Luminosidade", value=st.session_state.luz)
    st.session_state.negrito = st.toggle("Negrito", value=st.session_state.negrito)
    st.session_state.cor_card = st.selectbox("Cor dos Cartões", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_card))
    st.session_state.lingua = st.selectbox("Idioma", list(lang_map.keys()), index=list(lang_map.keys()).index(st.session_state.lingua))
    if st.button("Aplicar Alterações"): st.rerun()
