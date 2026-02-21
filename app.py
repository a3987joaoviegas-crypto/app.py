import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo Pro", page_icon="🌍", layout="wide")

# 2. ESTADOS E CONFIGURAÇÕES
if 'luz' not in st.session_state: st.session_state.luz = False
if 'negrito' not in st.session_state: st.session_state.negrito = False
if 'cor_fundo' not in st.session_state: st.session_state.cor_fundo = "Preto"
if 'cor_card' not in st.session_state: st.session_state.cor_card = "Preto"
if 'lingua' not in st.session_state: st.session_state.lingua = "Português (Original)"
if 'zoo' not in st.session_state: st.session_state.zoo = []

cores_hex = {
    "Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", 
    "Verde": "#002b1b", "Amarelo": "#f1c40f", "Roxo": "#4b0082", "Vermelho": "#8b0000"
}

# MAPA DE LÍNGUAS PARA A API E TRADUÇÃO DE TERMOS BIOLÓGICOS
lang_map = {
    "Português (Original)": {"code": "pt-BR", "env": "AMBIENTE", "diet": "DIETA", "rep": "REPRODUÇÃO", "save": "Guardar", "carn": "Carnívoro", "herb": "Herbívoro", "omni": "Omnívoro", "viv": "Vivíparo", "ovi": "Ovíparo", "terr": "Terrestre", "aqua": "Aquático"},
    "Inglês": {"code": "en", "env": "ENVIRONMENT", "diet": "DIET", "rep": "REPRODUCTION", "save": "Save", "carn": "Carnivore", "herb": "Herbivore", "omni": "Omnivore", "viv": "Viviparous", "ovi": "Oviparous", "terr": "Terrestrial", "aqua": "Aquatic"},
    "Espanhol": {"code": "es", "env": "AMBIENTE", "diet": "DIETA", "rep": "REPRODUCCIÓN", "save": "Guardar", "carn": "Carnívoro", "herb": "Herbívoro", "omni": "Omnívoro", "viv": "Vivíparo", "ovi": "Ovíparo", "terr": "Terrestre", "aqua": "Acuático"},
    "Russo": {"code": "ru", "env": "ОКРУЖАЮЩАЯ СРЕДА", "diet": "ПИТAНИЕ", "rep": "РЕПРОДУКЦИЯ", "save": "Сохранить", "carn": "Хищник", "herb": "Травоядный", "omni": "Всеядный", "viv": "Живородящие", "ovi": "Яйцекладущие", "terr": "Земной", "aqua": "Водный"},
    "Finlandês": {"code": "fi", "env": "YMPÄRISTÖ", "diet": "RUOKAVALIO", "rep": "LISÄÄNTYMINEN", "save": "Tallenna", "carn": "Lihansyöjä", "herb": "Kasvinsyöjä", "omni": "Kaikkiruokainen", "viv": "Elävänä synnyttävä", "ovi": "Muniva", "terr": "Maalla elävä", "aqua": "Vedessä elävä"},
    "Crioulo": {"code": "pt-PT", "env": "AMBIENTI", "diet": "DIETA", "rep": "REPRODUSON", "save": "Guarda", "carn": "Karnivoru", "herb": "Erbivoru", "omni": "Omnivoru", "viv": "Vivíparu", "ovi": "Ovíparu", "terr": "Terrestre", "aqua": "Akuatiku"}
}

dic = lang_map[st.session_state.lingua]

# 3. CSS DINÂMICO (CORREÇÃO DA SIDEBAR)
bg = "#f0f2f6" if st.session_state.luz else cores_hex[st.session_state.cor_fundo]
c_bg = "#ffffff" if st.session_state.luz else cores_hex[st.session_state.cor_card]
t_color = "#000000" if (st.session_state.luz or st.session_state.cor_fundo in ["Branco", "Amarelo"]) else "#ffffff"

st.markdown(f"""
    <style>
    /* Impedir que a sidebar desapareça totalmente ou mude de largura bruscamente */
    [data-testid="stSidebar"] {{ min-width: 250px; max-width: 300px; }}
    
    .stApp {{ background-color: {bg}; color: {t_color}; }}
    * {{ font-weight: {"bold" if st.session_state.negrito else "normal"} !important; }}
    
    .cc-card {{ 
        background: {c_bg}; border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
        color: {t_color}; box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }}
    .img-cc {{ width: 100%; height: 220px; object-fit: cover; border-radius: 8px; }}
    .common-name {{ color: #2ea043; font-size: 22px; font-weight: bold; margin-top: 10px; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# 4. LÓGICA DE TRADUÇÃO BIOLÓGICA
def traduzir_bio(nome, classe):
    n = str(nome).lower()
    # Dieta
    dieta = dic['omni']
    if any(x in n for x in ['leão', 'lion', 'tubarão', 'shark', 'tiger', 'tigre']): dieta = dic['carn']
    elif any(x in n for x in ['elefante', 'elephant', 'zebra', 'giraffe', 'girafa']): dieta = dic['herb']
    
    # Reprodução
    repro = dic['viv'] if classe == 'Mammalia' else dic['ovi']
    
    # Ambiente
    amb = dic['aqua'] if classe in ['Actinopterygii', 'Mollusca'] or "whale" in n or "baleia" in n else dic['terr']
    
    return dieta, repro, amb

def buscar_ia(query):
    # O parâmetro locale= faz a API devolver o nome comum na língua certa
    url = f"https://api.inaturalist.org/v1/taxa?q={query}&taxon_id=1&per_page=70&locale={dic['code']}"
    try:
        res = requests.get(url).json()
        out = []
        for item in res.get('results', []):
            if item.get('default_photo'):
                n_comum = (item.get('preferred_common_name') or item.get('name')).title()
                cl = item.get('iconic_taxon_name', 'Animal')
                d, r, a = traduzir_bio(n_comum, cl)
                out.append({'nome': n_comum, 'sci': item.get('name'), 'foto': item['default_photo']['medium_url'], 'dieta': d, 'repro': r, 'ambiente': a})
        return out
    except: return []

# 5. NAVEGAÇÃO
menu = st.sidebar.radio("Menu:", ["🌍 Planisfério", "🔬 Laboratório", "⭐ Favoritos", "⚙️ Definições"])

def exibir(a, k):
    st.markdown(f"""
        <div class='cc-card'>
            <img src='{a['foto']}' class='img-cc'>
            <div class='common-name'>{a['nome']}</div>
            <div style='text-align:center; font-style:italic; font-size: 0.9em;'>{a['sci']}</div>
            <hr style='border: 0.1px solid gray; opacity: 0.2;'>
            <b>{dic['env']}:</b> {a['ambiente']}<br>
            <b>{dic['diet']}:</b> {a['dieta']}<br>
            <b>{dic['rep']}:</b> {a['repro']}
        </div>
    """, unsafe_allow_html=True)
    if st.button(f"⭐ {dic['save']}", key=k): st.session_state.zoo.append(a)

if menu == "⚙️ Definições":
    st.title("⚙️ Definições")
    st.session_state.luz = st.toggle("Luminosidade (Ovo)", value=st.session_state.luz)
    st.session_state.negrito = st.toggle("Negrito", value=st.session_state.negrito)
    st.session_state.cor_fundo = st.selectbox("Fundo:", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_fundo))
    st.session_state.cor_card = st.selectbox("Cartões:", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_card))
    st.session_state.lingua = st.selectbox("Língua:", list(lang_map.keys()), index=list(lang_map.keys()).index(st.session_state.lingua))
    if st.button("Aplicar"): st.rerun()

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório")
    busca = st.text_input("Pesquisar 70 espécies:")
    if busca:
        res = buscar_ia(busca)
        cols = st.columns(3)
        for i, anim in enumerate(res):
            with cols[i%3]: exibir(anim, f"lab_{i}")
# (Outras páginas seguem a mesma lógica)
