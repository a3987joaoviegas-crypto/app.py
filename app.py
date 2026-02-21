import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo Ultimate", page_icon="🌍", layout="wide")

# 2. ESTADOS DE SESSÃO
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

# 4. CSS
bg = "#f0f2f6" if st.session_state.luz else cores_hex[st.session_state.cor_fundo]
c_bg = "#ffffff" if st.session_state.luz else cores_hex[st.session_state.cor_card]
t_color = "#000000" if (st.session_state.luz or st.session_state.cor_fundo in ["Branco", "Amarelo"]) else "#ffffff"

st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ min-width: 280px !important; }}
    .stApp {{ background-color: {bg}; color: {t_color}; }}
    * {{ font-weight: {"bold" if st.session_state.negrito else "normal"} !important; }}
    .cc-card {{ 
        background: {c_bg}; border-radius: 12px; padding: 20px; 
        border-left: 8px solid #2ea043; margin-bottom: 25px; color: {t_color};
    }}
    .img-cc {{ width: 100%; height: 220px; object-fit: cover; border-radius: 8px; }}
    .common-name {{ color: #2ea043; font-size: 22px; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# 5. LÓGICA
def traduzir_bio(nome, classe):
    n = str(nome).lower()
    dieta = dic['omni']
    if any(x in n for x in ['leão', 'lion', 'tubarão', 'shark', 'tiger', 'lobo']): dieta = dic['carn']
    elif any(x in n for x in ['elefante', 'elephant', 'zebra', 'giraffe']): dieta = dic['herb']
    repro = dic['viv'] if classe == 'Mammalia' else dic['ovi']
    amb = dic['aqua'] if classe in ['Actinopterygii'] or "whale" in n or "baleia" in n else dic['terr']
    return dieta, repro, amb

def buscar(query):
    url = f"https://api.inaturalist.org/v1/taxa?q={query}&taxon_id=1&per_page=70&locale={dic['code']}"
    try:
        res = requests.get(url).json()
        out = []
        for item in res.get('results', []):
            if item.get('default_photo'):
                n = (item.get('preferred_common_name') or item.get('name')).title()
                d, r, a = traduzir_bio(n, item.get('iconic_taxon_name'))
                out.append({'nome': n, 'sci': item.get('name'), 'foto': item['default_photo']['medium_url'], 'dieta': d, 'repro': r, 'ambiente': a})
        return out
    except: return []

# 6. INTERFACE
menu = st.sidebar.radio("Navegação", ["🌍 Planisfério", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Favoritos", "⚙️ Definições"])

def card(a, k):
    st.markdown(f"""<div class='cc-card'><img src='{a['foto']}' class='img-cc'><div class='common-name'>{a['nome']}</div><div style='text-align:center; font-style:italic;'>{a['sci']}</div><hr><b>{dic['env']}:</b> {a['ambiente']}<br><b>{dic['diet']}:</b> {a['dieta']}<br><b>{dic['rep']}:</b> {a['repro']}</div>""", unsafe_allow_html=True)
    if st.button(f"⭐ {dic['save']}", key=k): st.session_state.zoo.append(a)

# --- PÁGINAS ---
if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério Global")
    df_mapa = pd.DataFrame({
        'lat': [38.7, -15.7, -8.8, -18.6, 37.0, -25.2],
        'lon': [-9.1, -47.8, 13.2, 35.5, -95.7, 133.7],
        'País': ["Portugal", "Brasil", "Angola", "Moçambique", "EUA", "Austrália"]
    })
    st.map(df_mapa)
    p = st.selectbox("Selecione o local para ver os 70 animais:", df_mapa['País'])
    res = buscar(p)
    cols = st.columns(3)
    for i, anim in enumerate(res):
        with cols[i%3]: card(anim, f"p_{i}")

elif menu == "🌲 Florestas":
    st.title("🌲 Fauna das Florestas (70 Espécies)")
    res = buscar("Forest")
    cols = st.columns(3)
    for i, anim in enumerate(res):
        with cols[i%3]: card(anim, f"f_{i}")

elif menu == "🌊 Oceanos":
    st.title("🌊 Fauna dos Oceanos (70 Espécies)")
    res = buscar("Ocean")
    cols = st.columns(3)
    for i, anim in enumerate(res):
        with cols[i%3]: card(anim, f"o_{i}")

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório")
    b = st.text_input("Pesquisar:")
    if b:
        res = buscar(b)
        cols = st.columns(3)
        for i, anim in enumerate(res):
            with cols[i%3]: card(anim, f"l_{i}")

elif menu == "⚙️ Definições":
    st.title("⚙️ Definições")
    st.session_state.luz = st.toggle("Luminosidade (Ovo)", st.session_state.luz)
    st.session_state.negrito = st.toggle("Negrito", st.session_state.negrito)
    st.session_state.cor_fundo = st.selectbox("Cor de Fundo", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_fundo))
    st.session_state.cor_card = st.selectbox("Cor dos Cartões", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_card))
    st.session_state.lingua = st.selectbox("Idioma", list(lang_map.keys()), index=list(lang_map.keys()).index(st.session_state.lingua))
    if st.button("Aplicar"): st.rerun()
