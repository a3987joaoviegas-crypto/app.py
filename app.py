import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo Pro", page_icon="🌍", layout="wide")

# 2. INICIALIZAÇÃO DE ESTADOS (Para as definições funcionarem entre páginas)
if 'luz' not in st.session_state: st.session_state.luz = False
if 'negrito' not in st.session_state: st.session_state.negrito = False
if 'cor_fundo' not in st.session_state: st.session_state.cor_fundo = "Preto"
if 'cor_card_user' not in st.session_state: st.session_state.cor_card_user = "Preto"
if 'lingua' not in st.session_state: st.session_state.lingua = "Português (Original)"
if 'zoo' not in st.session_state: st.session_state.zoo = []

# Dicionário de Cores
cores_hex = {
    "Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", 
    "Verde": "#002b1b", "Amarelo": "#f1c40f", "Roxo": "#4b0082", "Vermelho": "#8b0000"
}

# Dicionário de Traduções Simples para a Interface
trans = {
    "Português (Original)": {"env": "AMBIENTE", "diet": "DIETA", "rep": "REPRODUÇÃO", "search": "Pesquisar", "save": "Guardar"},
    "Inglês": {"env": "ENVIRONMENT", "diet": "DIET", "rep": "REPRODUCTION", "search": "Search", "save": "Save"},
    "Espanhol": {"env": "AMBIENTE", "diet": "DIETA", "rep": "REPRODUCCIÓN", "search": "Buscar", "save": "Guardar"},
    "Russo": {"env": "ОКРУЖАЮЩАЯ СРЕДА", "diet": "ПИТАНИЕ", "rep": "REPRODUCTION", "search": "поиск", "save": "сохранить"},
    "Finlandês": {"env": "YMPÄRISTÖ", "diet": "RUOKAVALIO", "rep": "LISÄÄNTYMINEN", "search": "Etsi", "save": "Tallenna"},
    "Crioulo": {"env": "AMBIENTI", "diet": "DIETA", "rep": "REPRODUSON", "search": "Buska", "save": "Guarda"}
}
t = trans[st.session_state.lingua]

# 3. LÓGICA DE ESTILO DINÂMICO
bg_color = "#f0f2f6" if st.session_state.luz else cores_hex[st.session_state.cor_fundo]
card_bg = "#ffffff" if st.session_state.luz else cores_hex[st.session_state.cor_card_user]
text_color = "#000000" if (st.session_state.luz or st.session_state.cor_fundo in ["Branco", "Amarelo"]) else "#ffffff"

st.markdown(f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    * {{ font-weight: {"bold" if st.session_state.negrito else "normal"} !important; }}
    
    .cc-card {{ 
        background: {card_bg}; 
        border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
        color: {text_color};
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }}
    .img-cc {{ width: 100%; height: 220px; object-fit: cover; border-radius: 8px; }}
    .common-name {{ color: #2ea043; font-size: 22px; font-weight: bold; margin-top: 10px; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# 4. FUNÇÕES
def definir_biologia(nome, classe):
    n = str(nome).lower()
    dieta = "Omnívoro"
    if any(x in n for x in ['leão', 'tubarão', 'lobo', 'tigre']): dieta = "Carnívoro"
    elif any(x in n for x in ['elefante', 'zebra', 'girafa']): dieta = "Herbívoro"
    repro = "Vivíparo" if classe == 'Mammalia' else "Ovíparo"
    ambiente = "Marinho" if "baleia" in n or classe in ['Actinopterygii'] else "Terrestre"
    return dieta, repro, ambiente

def buscar_fauna(query, limite=70):
    url = f"https://api.inaturalist.org/v1/taxa?q={query}&taxon_id=1&per_page={limite}&locale=pt-BR"
    try:
        res = requests.get(url).json()
        out = []
        for t_item in res.get('results', []):
            if t_item.get('default_photo'):
                nome = (t_item.get('preferred_common_name') or t_item.get('name')).title()
                cl = t_item.get('iconic_taxon_name', 'Animal')
                d, r, amb = definir_biologia(nome, cl)
                out.append({'nome': nome, 'sci': t_item.get('name'), 'foto': t_item['default_photo']['medium_url'], 'dieta': d, 'repro': r, 'ambiente': amb})
        return out
    except: return []

# 5. MENU LATERAL
menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Favoritos", "⚙️ Definições"])

def exibir_cartao(a, key):
    st.markdown(f"""
        <div class='cc-card'>
            <img src='{a['foto']}' class='img-cc'>
            <div class='common-name'>{a['nome']}</div>
            <div style='text-align:center; opacity: 0.8;'>{a['sci']}</div>
            <hr style='border: 0.5px solid #30363d;'>
            <b>{t['env']}:</b> 🏡 {a['ambiente']}<br>
            <b>{t['diet']}:</b> 🍴 {a['dieta']}<br>
            <b>{t['rep']}:</b> 🧬 {a['repro']}
        </div>
    """, unsafe_allow_html=True)
    if st.button(f"⭐ {t['save']}", key=key): st.session_state.zoo.append(a)

# --- PÁGINAS ---

if menu == "⚙️ Definições":
    st.title("⚙️ Configurações do Sistema")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Visual")
        st.session_state.luz = st.toggle("Luminosidade (Modo Claro)", value=st.session_state.luz)
        st.session_state.negrito = st.toggle("Texto em Negrito", value=st.session_state.negrito)
        st.session_state.cor_fundo = st.selectbox("Cor de Fundo:", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_fundo))
        st.session_state.cor_card_user = st.selectbox("Cor dos Cartões:", list(cores_hex.keys()), index=list(cores_hex.keys()).index(st.session_state.cor_card_user))

    with col2:
        st.subheader("Regional")
        st.session_state.lingua = st.selectbox("Idioma do Sistema:", ["Português (Original)", "Inglês", "Espanhol", "Russo", "Finlandês", "Crioulo"], index=["Português (Original)", "Inglês", "Espanhol", "Russo", "Finlandês", "Crioulo"].index(st.session_state.lingua))
    
    if st.button("Aplicar e Recarregar"): st.rerun()

elif menu == "🌍 Planisfério":
    st.title("🌍 Planisfério")
    st.map(pd.DataFrame({'lat': [38.7, -15.7], 'lon': [-9.1, -47.8]}))
    sel = st.selectbox("País:", ["Brasil", "Portugal", "Angola"])
    animais = buscar_fauna(sel, 70)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: exibir_cartao(an, f"map_{i}")

elif menu == "🔬 Laboratório":
    st.title(f"🔬 {t['search']}")
    txt = st.text_input(f"{t['search']} 70 espécies:")
    if txt:
        lista = buscar_fauna(txt, 70)
        cols = st.columns(3)
        for i, anim in enumerate(lista):
            with cols[i%3]: exibir_cartao(anim, f"lab_{i}")

# (As outras abas seguem a mesma lógica de 70 animais e exibir_cartao)
