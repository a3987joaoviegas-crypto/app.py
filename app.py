import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="MundoVivo", layout="wide")

# ----------------------
# ESTADO
# ----------------------
chaves = {
    'zoo': [], 'tanque_fusao': [], 'pontos_zoologo': 0,
    'animais_salvos_ids': set(), 'id_animal_atual': None,
    'internados_vet': [], 'c_24h': "", 'c_mega': "",
    'premium_ativo': False, 'cor_tema': "#0b1117", 'brilho': 100,
    'inicio_sessao_24h': None
}
for k, v in chaves.items():
    if k not in st.session_state:
        st.session_state[k] = v

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
st.markdown(f"""
<style>
.stApp {{
    background-color: {st.session_state.cor_tema};
    filter: brightness({st.session_state.brilho/100});
}}
.cartao {{
    background:#1a1c23;
    border-radius:12px;
    padding:8px;
    text-align:center;
    margin-bottom:10px;
}}
.img {{
    width:100%;
    height:120px;
    object-fit:cover;
    border-radius:10px;
}}
</style>
""", unsafe_allow_html=True)

# ----------------------
# AUDIO (só aves)
# ----------------------
def buscar_audio(animal):
    if animal.get("iconic_taxon_name") != "Aves":
        return None
    try:
        nome = animal.get("name","").replace(" ","+")
        r = requests.get(f"https://www.xeno-canto.org/api/2/recordings?query={nome}", timeout=5)
        data = r.json()
        if data["recordings"]:
            return "https:" + data["recordings"][0]["file"]
    except:
        return None
    return None

# ----------------------
# CARTÃO (ERRO CORRIGIDO AQUI)
# ----------------------
def card(an, idx):
    if not an:
        return

    nome = (an.get("preferred_common_name") or an.get("name") or "Espécie").title()
    cientifico = an.get("name","")

    foto_data = an.get("default_photo") or {}
    foto = foto_data.get("medium_url", "https://via.placeholder.com/300")

    st.markdown(f"""
    <div class="cartao">
        <img src="{foto}" class="img">
        <b>{nome}</b><br>
        <span style="font-size:0.7em;color:#aaa;">{cientifico}</span>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)

    with c1:
        if st.button("📥", key=f"z{idx}"):
            st.session_state.zoo.append(an)

    with c2:
        if st.button("🧬", key=f"f{idx}"):
            st.session_state.tanque_fusao.append(an)

    with c3:
        audio = buscar_audio(an)
        if audio and st.button("🔊", key=f"s{idx}"):
            st.audio(audio)

# ----------------------
# GRID
# ----------------------
def grid(lista):
    if not lista:
        st.write("Sem resultados")
        return

    for i in range(0,len(lista),3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(lista):
                with cols[j]:
                    card(lista[i+j], i+j)

# ----------------------
# SIDEBAR
# ----------------------
with st.sidebar:
    st.title("🌍 MundoVivo")

    premium = is_mega or is_24h_valido

    if premium:
        st.session_state.premium_ativo = st.toggle("Premium")

    if premium and st.session_state.premium_ativo:
        aba = st.radio("Menu", ["🔬 Laboratório","🐾 Zoo","⚙️ Definições"])
    else:
        aba = st.radio("Menu", ["🌲 Florestas","🌊 Oceanos","🏳️ Países","🔬 Laboratório","🐾 Zoo","⚙️ Definições"])

# ----------------------
# ABAS
# ----------------------

# FLORESTAS / OCEANOS / PAISES
if aba in ["🌲 Florestas","🌊 Oceanos","🏳️ Países"]:

    if aba=="🌲 Florestas":
        locais=["Amazónia","Savana","Taiga"]
    elif aba=="🌊 Oceanos":
        locais=["Oceano Atlântico","Oceano Pacífico","Mar Mediterrâneo"]
    else:
        locais=["Portugal","Brasil","EUA","Japão","França","Alemanha"]

    sel = st.selectbox("Local", locais)

    try:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&per_page=70", timeout=5)
        lista = r.json().get("results",[])
    except:
        lista=[]

    grid(lista)

# LAB (PESQUISA LIVRE)
elif aba=="🔬 Laboratório":

    q = st.text_input("Pesquisar animal")

    if q:
        try:
            r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={q}&per_page=70", timeout=5)
            lista = r.json().get("results",[])
        except:
            lista=[]

        grid(lista)

# ZOO
elif aba=="🐾 Zoo":
    grid(st.session_state.zoo)

# DEFINIÇÕES (AGORA FUNCIONA)
elif aba=="⚙️ Definições":

    st.subheader("Códigos")

    st.session_state.c_mega = st.text_input("Código Mega", value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input("Código 24h", value=st.session_state.c_24h)

    st.subheader("Visual")

    st.session_state.cor_tema = st.color_picker("Cor", st.session_state.cor_tema)
    st.session_state.brilho = st.slider("Brilho", 50,150, st.session_state.brilho)

    if st.button("Guardar"):
        st.rerun()
