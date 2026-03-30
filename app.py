import streamlit as st
import requests
import random
from datetime import datetime

st.set_page_config(page_title="MundoVivo", layout="wide")

# ----------------------
# DEBUG (importante)
# ----------------------
st.write("✅ MundoVivo carregado")

# ----------------------
# ESTADO
# ----------------------
if "zoo" not in st.session_state:
    st.session_state.zoo = []

if "premium" not in st.session_state:
    st.session_state.premium = False

# ----------------------
# FUNÇÃO SEGURA API
# ----------------------
def buscar_animais(query):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={query}&per_page=9"
        r = requests.get(url, timeout=5)

        if r.status_code != 200:
            return []

        data = r.json()
        return data.get("results", [])
    except:
        return []

# ----------------------
# CARTÃO
# ----------------------
def card(an):
    try:
        nome = (an.get("preferred_common_name") or an.get("name") or "Animal").title()
        cientifico = an.get("name", "Desconhecido")

        foto = "https://via.placeholder.com/300"
        if an.get("default_photo") and an["default_photo"].get("medium_url"):
            foto = an["default_photo"]["medium_url"]

        st.markdown(f"""
        <div style="
            background:#1a1c23;
            padding:10px;
            border-radius:15px;
            border:2px solid #2ecc71;
            text-align:center;
            color:white;">
            
            <img src="{foto}" style="width:100%;height:120px;object-fit:cover;border-radius:10px;">
            
            <h4>{nome}</h4>
            <p style="color:#aaa;font-size:12px;">{cientifico}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"🔊 {nome}", key=f"s_{nome}_{random.randint(0,99999)}"):
            st.success(f"🔊 Som de {nome} (simulado)")

    except Exception as e:
        st.error("Erro no cartão")

# ----------------------
# GRID
# ----------------------
def grid(lista):
    if not lista:
        st.warning("Sem resultados 😢")
        return

    for i in range(0, len(lista), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(lista):
                with cols[j]:
                    card(lista[i+j])

# ----------------------
# SIDEBAR
# ----------------------
with st.sidebar:
    st.title("🌍 MundoVivo")

    st.session_state.premium = st.toggle("✨ Premium", value=st.session_state.premium)

    aba = st.radio("Menu", [
        "🌲 Explorar",
        "🔬 Laboratório",
        "🐾 Meu Zoo",
        "⚙️ Definições"
    ])

# ----------------------
# EXPLORAR
# ----------------------
if aba == "🌲 Explorar":
    st.header("🌲 Explorar Animais")

    lugar = st.selectbox("Escolhe:", ["Amazónia", "Portugal", "Brasil"])

    lista = buscar_animais(lugar)
    grid(lista)

# ----------------------
# LABORATÓRIO
# ----------------------
elif aba == "🔬 Laboratório":
    st.header("🔬 Laboratório")

    if not st.session_state.premium:
        st.warning("Ativa o Premium 😎")
    else:
        txt = st.text_input("Animais (ex: leão, tigre)")

        if txt:
            nomes = [x.strip() for x in txt.split(",")][:3]

            resultados = []
            for n in nomes:
                res = buscar_animais(n)
                if res:
                    resultados.append(res[0])

            grid(resultados)

# ----------------------
# ZOO
# ----------------------
elif aba == "🐾 Meu Zoo":
    st.header("🐾 Meu Zoo")

    if st.session_state.zoo:
        grid(st.session_state.zoo)
    else:
        st.info("Sem animais ainda 🐾")

# ----------------------
# DEFINIÇÕES
# ----------------------
elif aba == "⚙️ Definições":
    st.header("⚙️ Definições")
    st.write("Configurações básicas aqui")
