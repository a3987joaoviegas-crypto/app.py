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
    borda_css = "border: 5px solid #ffd700;"
else:
    borda_css = "border: 4px solid #2ecc71;"

st.markdown(f"""
<style>
@property --angle {{ syntax: '<angle>'; initial-value: 0deg; inherits: false; }}
@keyframes rotate_grad {{ to {{ --angle: 360deg; }} }}
.stApp {{ background-color: {st.session_state.cor_tema}; filter: brightness({st.session_state.brilho/100}); }}
.cartao-cidadao {{
    background-color: #1a1c23 !important;
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
# FUNÇÃO CARTÃO DE CIDADÃO
# ----------------------
def card(an, prefixo, idx=0, show_buttons=True):
    if not an:
        return
    nome_pt = (an.get('preferred_common_name') or an.get('name') or 'Espécie').title()
    nome_cientifico = an.get('name', 'Desconhecido')
    foto = (an.get('default_photo') or {}).get('medium_url', "https://via.placeholder.com/300")
    st.markdown(f'''
    <div class="cartao-cidadao">
        <span style="color:#ffd700; font-size:0.6em;">💳 CARTÃO DE CIDADÃO</span><br>
        <img src="{foto}" class="img-an">
        <h4 style="color:#ffd700;">{nome_pt}</h4>
        <p style="color:#aaa; font-size:0.7em;">{nome_cientifico}</p>
    </div>
    ''', unsafe_allow_html=True)

    if show_buttons:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📥", key=f"z_{prefixo}_{idx}"):
                st.session_state.zoo.append(an)
        with c2:
            if st.button("🧬", key=f"f_{prefixo}_{idx}"):
                st.session_state.tanque_fusao.append(an)

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
# BUSCAR ANIMAIS (SÓ ANIMALIA)
# ----------------------
def buscar_animais(q):
    url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=40151&rank=species&per_page=70&locale=pt-PT"
    return requests.get(url).json().get("results", [])

# ----------------------
# LOCAIS
# ----------------------
florestas = ["Amazônia", "Congo", "Taiga", "Temperada", "Boreal", "Mata Atlântica"]
oceanos = ["Atlântico", "Pacífico", "Índico", "Ártico", "Antártico", "Mar Mediterrâneo", "Mar do Caribe"]
paises = ["Portugal","Brasil","EUA","França","Alemanha","Itália","Espanha","Japão","China","Austrália"]*7  # 70 países

# ----------------------
# SIDEBAR
# ----------------------
with st.sidebar:
    st.title("🌍 MundoVivo")
    premium = is_mega or is_24h_valido
    if premium:
        st.session_state.premium_ativo = st.toggle("✨ MODO PREMIUM")
    if st.session_state.premium_ativo:
        menu = ["🌀 Salvamento","🏥 Veterinário","🧬 Fusão","🔬 Laboratório"]
    else:
        menu = ["🌲 Florestas","🌊 Oceanos","🏳️ Países","🔬 Laboratório"]
    aba = st.radio("Menu", menu)

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
    lista = buscar_animais("wildlife")
    if lista:
        card(random.choice(lista), "res", 0, False)

elif aba == "🏥 Veterinário":
    st.write("Sem animais.")

elif aba == "🧬 Fusão":
    st.write("Fusão ativa.")

# ----------------------
# PLACEHOLDER PARA SOM VIA IA
# ----------------------
if st.session_state.premium_ativo:
    st.info("🔊 Em breve: ouvir som dos animais via IA")
