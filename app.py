import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

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
if is_mega:
    borda_css = "border: 5px solid; border-image: linear-gradient(var(--angle), red, orange, yellow, green, blue, indigo, violet) 1; animation: rotate_grad 3s linear infinite;"
elif is_24h_valido:
    borda_css = "border: 5px solid gold;"
else:
    borda_css = "border: 4px solid #2ecc71;"

st.markdown(f"""
<style>
@property --angle {{ syntax: '<angle>'; initial-value: 0deg; inherits: false; }}
@keyframes rotate_grad {{ to {{ --angle: 360deg; }} }}
.stApp {{ background-color: {st.session_state.cor_tema}; }}
.cartao-cidadao {{
    background-color: #1a1c23;
    border-radius: 20px;
    padding: 12px;
    {borda_css}
    margin-bottom: 15px;
    text-align: center;
    color: white;
}}
.img-an {{
    width: 100%;
    border-radius: 15px;
    height: 130px;
    object-fit: cover;
}}
</style>
""", unsafe_allow_html=True)

# ----------------------
# AUDIO (aves)
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
# CARTÃO
# ----------------------
def card(an, prefixo, idx=0, show_buttons=True):
    if not an:
        return

    nome_pt = (an.get('preferred_common_name') or an.get('name') or 'Espécie').title()
    nome_cientifico = an.get('name', "Desconhecido")

    foto = (an.get('default_photo') or {}).get('medium_url', "https://via.placeholder.com/300")

    st.markdown(f"""
    <div class="cartao-cidadao">
        <img src="{foto}" class="img-an">
        <h4>{nome_pt}</h4>
        <p style="font-size:12px;color:#aaa;">{nome_cientifico}</p>
    </div>
    """, unsafe_allow_html=True)

    if show_buttons:
        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("📥", key=f"z_{prefixo}_{idx}"):
                st.session_state.zoo.append(an)

        with c2:
            if st.button("🧬", key=f"f_{prefixo}_{idx}"):
                st.session_state.tanque_fusao.append(an)

        with c3:
            audio = buscar_audio(an)
            if audio and st.button("🔊", key=f"s_{prefixo}_{idx}"):
                st.audio(audio)

# ----------------------
# GRID
# ----------------------
def grid(lista, prefixo):
    for i in range(0, len(lista), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(lista):
                with cols[j]:
                    card(lista[i+j], prefixo, i+j)

# ----------------------
# LISTAS
# ----------------------
florestas = ["Amazônia", "Congo", "Taiga", "Temperada"]
oceanos = ["Atlântico", "Pacífico", "Índico"]
paises = ["Portugal","Brasil","EUA","França","Alemanha"] * 14  # 70

# ----------------------
# SIDEBAR
# ----------------------
with st.sidebar:
    st.title("🌍 MundoVivo")

    premium = is_mega or is_24h_valido

    if premium:
        st.session_state.premium_ativo = st.toggle("✨ PREMIUM")

    if st.session_state.premium_ativo:
        menu = ["🌀 Salvamento","🏥 Veterinário","🧬 Fusão","🔬 Laboratório"]
    else:
        menu = ["🌲 Florestas","🌊 Oceanos","🏳️ Países","🔬 Laboratório"]

    aba = st.radio("Menu", menu)

# ----------------------
# FUNÇÃO API (FIX)
# ----------------------
def buscar_animais(q):
    url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=40151&per_page=12&locale=pt-PT"
    return requests.get(url).json().get("results", [])

# ----------------------
# ABAS
# ----------------------
if aba == "🌲 Florestas":
    sel = st.selectbox("Floresta", florestas)
    grid(buscar_animais(sel), "f")

elif aba == "🌊 Oceanos":
    sel = st.selectbox("Oceano", oceanos)
    grid(buscar_animais(sel), "o")

elif aba == "🏳️ Países":
    sel = st.selectbox("País", paises)
    grid(buscar_animais(sel), "p")

elif aba == "🔬 Laboratório":
    termo = st.text_input("Pesquisar animal:")
    if termo:
        grid(buscar_animais(termo), "lab")

elif aba == "🌀 Salvamento":
    st.image(f"https://source.unsplash.com/600x200/?animal,{random.randint(1,100)}")
    lista = buscar_animais("wildlife")
    if lista:
        animal = random.choice(lista)
        card(animal, "res", 0, False)

elif aba == "🏥 Veterinário":
    st.write("Sem animais.")

elif aba == "🧬 Fusão":
    st.write("Fusão ativa.")
