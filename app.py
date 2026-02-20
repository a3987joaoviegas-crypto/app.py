import streamlit as st
import pd as pd
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# 2. DEFINIÇÕES NA SIDEBAR
st.sidebar.title("⚙️ Definições")

# Luminosidade (O botão "ovo" que desliza)
luz = st.sidebar.toggle("Luminosidade (Modo Claro)")

# Negrito
negrito = st.sidebar.toggle("Texto em Negrito")

# Cor de Fundo
cor_fundo = st.sidebar.selectbox("Cor de Fundo:", ["Preto", "Branco", "Azul", "Verde"])
cores = {"Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", "Verde": "#002b1b"}
cor_texto = "#000000" if cor_fundo == "Branco" else "#adbac7"

# Línguas
lingua = st.sidebar.selectbox("Idioma:", ["Português (Original)", "Inglês", "Espanhol", "Russo", "Finlandês", "Crioulo"])

# 3. ESTILO CSS DINÂMICO
st.markdown(f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stApp {{ background-color: {cores[cor_fundo]}; color: {cor_texto}; }}
    
    * {{ 
        font-weight: {"bold" if negrito else "normal"}; 
    }}

    .cc-card {{ 
        background: {"#f0f0f0" if cor_fundo == "Branco" else "#1c2128"}; 
        border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
        color: {cor_texto};
    }}
    .img-cc {{ width: 100%; height: 220px; object-fit: cover; border-radius: 8px; }}
    .common-name {{ color: #2ea043; font-size: 22px; font-weight: bold; margin-top: 10px; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# 4. LÓGICA BIOLÓGICA
def buscar_fauna(query, limite=12):
    url = f"https://api.inaturalist.org/v1/taxa?q={query}&taxon_id=1&locale=pt-BR"
    try:
        res = requests.get(url).json()
        out = []
        for t in res.get('results', [])[:limite]:
            if t.get('default_photo'):
                out.append({
                    'nome': (t.get('preferred_common_name') or t.get('name')).title(),
                    'sci': t.get('name'),
                    'foto': t['default_photo']['medium_url']
                })
        return out
    except: return []

# SESSÕES
if 'zoo' not in st.session_state: st.session_state.zoo = []

# MENU PRINCIPAL
st.sidebar.divider()
menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Favoritos"])

def exibir_cartao(a, key):
    st.markdown(f"""
        <div class='cc-card'>
            <img src='{a['foto']}' class='img-cc'>
            <div class='common-name'>{a['nome']}</div>
            <div style='text-align:center; font-style:italic;'>{a['sci']}</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("⭐ Guardar", key=key): st.session_state.zoo.append(a)

# --- PÁGINAS ---
if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério")
    st.map(pd.DataFrame({'lat': [39.3, -14.2], 'lon': [-8.2, -51.9]}))
    sel = st.selectbox("Escolha um País:", ["Brasil", "Portugal", "Angola", "Moçambique"])
    animais = buscar_fauna(sel, 12) # AGORA COM 12 ANIMAIS
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: exibir_cartao(an, f"map_{i}")

elif menu == "🌲 Florestas":
    st.title("🌲 Florestas")
    animais = buscar_fauna("Floresta", 12)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: exibir_cartao(an, f"flo_{i}")

elif menu == "🌊 Oceanos":
    st.title("🌊 Oceanos")
    animais = buscar_fauna("Oceano", 12)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: exibir_cartao(an, f"oce_{i}")

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório")
    txt = st.text_input("Pesquisar:")
    if txt:
        lista = buscar_fauna(txt, 12)
        cols = st.columns(3)
        for i, anim in enumerate(lista):
            with cols[i%3]: exibir_cartao(anim, f"lab_{i}")

elif menu == "⭐ Favoritos":
    st.title("🐾 Meu Zoo")
    cols = st.columns(3)
    for i, z in enumerate(st.session_state.zoo):
        with cols[i%3]: exibir_cartao(z, f"zoo_{i}")
