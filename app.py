import streamlit as st
import requests
import random
from datetime import datetime, timedelta

# ----------------------
# ESTADO
# ----------------------
chaves = {
    'zoo': [], 'tanque_fusao': [],
    'c_24h': "", 'c_mega': "",
    'premium_ativo': False,
    'inicio_sessao_24h': None,
    'laboratorio_animais': []
}
for k, v in chaves.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ----------------------
# FUNÇÃO SEGURA API
# ----------------------
def buscar_animais(url):
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        return data.get('results', [])
    except:
        return []

# ----------------------
# PREMIUM
# ----------------------
is_mega = st.session_state.c_mega == "67lucas62"

is_24h_valido = False
if st.session_state.c_24h == "6626":
    if st.session_state.inicio_sessao_24h is None:
        st.session_state.inicio_sessao_24h = datetime.now().timestamp()
    if (datetime.now().timestamp() - st.session_state.inicio_sessao_24h) < 86400:
        is_24h_valido = True

# ----------------------
# CSS
# ----------------------
st.markdown("""
<style>
.cartao {
    background:#1a1c23;
    padding:10px;
    border-radius:15px;
    border:2px solid #2ecc71;
    text-align:center;
    color:white;
}
.img {
    width:100%;
    height:120px;
    object-fit:cover;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------
# CARTÃO
# ----------------------
def card(an):
    if not an:
        return

    nome = (an.get('preferred_common_name') or an.get('name') or "Animal").title()
    cientifico = an.get('name', "Desconhecido")

    foto = "https://via.placeholder.com/300"
    if an.get('default_photo') and an['default_photo'].get('medium_url'):
        foto = an['default_photo']['medium_url']

    classe = an.get('iconic_taxon_name', "Animal")

    st.markdown(f"""
    <div class="cartao">
        <img src="{foto}" class="img">
        <h4>{nome}</h4>
        <p style="color:#aaa;font-size:12px;">{cientifico}</p>
        <p>🐾 {classe}</p>
    </div>
    """, unsafe_allow_html=True)

    # botão som (seguro)
    if st.button(f"🔊 {nome}", key=f"s_{an.get('id', nome)}"):
        st.info(f"IA encontrou som de {nome} 🔊")

# ----------------------
# GRID
# ----------------------
def grid(lista):
    for i in range(0, len(lista), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(lista):
                with cols[j]:
                    card(lista[i + j])

# ----------------------
# SIDEBAR
# ----------------------
with st.sidebar:
    st.title("🌍 MundoVivo")

    if is_mega or is_24h_valido:
        st.session_state.premium_ativo = st.toggle("✨ Premium")

    menu = ["🌲 Florestas", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    if st.session_state.premium_ativo:
        menu += ["🧬 Fusão"]

    aba = st.radio("Menu", menu)

# ----------------------
# ABAS
# ----------------------

# FLORESTA
if aba == "🌲 Florestas":
    sel = st.selectbox("Local:", ["Amazónia", "Portugal", "Brasil"])
    lista = buscar_animais(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=9")
    
    if lista:
        grid(lista)
    else:
        st.warning("Sem animais 😢")

# LABORATÓRIO
elif aba == "🔬 Laboratório":
    if not st.session_state.premium_ativo:
        st.warning("Ativa o premium 😎")
    else:
        txt = st.text_input("Animais (ex: leão, tigre)")

        if txt:
            nomes = [x.strip() for x in txt.split(",")][:3]
            lista = []

            for n in nomes:
                res = buscar_animais(f"https://api.inaturalist.org/v1/taxa?q={n}&per_page=1")
                if res:
                    lista.append(res[0])

            if lista:
                grid(lista)
            else:
                st.warning("Nada encontrado")

# ZOO
elif aba == "🐾 Meu Zoo":
    if st.session_state.zoo:
        grid(st.session_state.zoo)
    else:
        st.info("Zoo vazio 🐾")

# FUSÃO
elif aba == "🧬 Fusão":
    if len(st.session_state.tanque_fusao) < 2:
        st.info("Precisas de 2 animais 🧬")
    else:
        if st.button("Fundir"):
            st.success("Novo animal criado! 🧬")

# DEFINIÇÕES
elif aba == "⚙️ Definições":
    st.session_state.c_mega = st.text_input("Código Mega", value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input("Código 24h", value=st.session_state.c_24h)
