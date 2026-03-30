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
    if k not in st.session_state: st.session_state[k] = v

# ----------------------
# CÓDIGOS PREMIUM
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
    background-color: #1a1c23 !important; border-radius: 20px; padding: 12px; 
    {borda_css} margin-bottom: 15px; text-align: center; color: white;
}}
.img-an {{ width: 100%; border-radius: 15px; height: 130px; object-fit: cover; border: 1px solid #444; filter: none !important; }}
@keyframes heli {{ 0% {{ transform: translateX(-200px); }} 100% {{ transform: translateX(110vw); }} }}
.heli-anim {{ position: fixed; top: 30%; font-size: 80px; z-index: 9999; animation: heli 3s linear forwards; }}
</style>
""", unsafe_allow_html=True)

# ----------------------
# FUNÇÃO DE CARTÃO (com novidades)
# ----------------------
def card(an, prefixo, idx=0, show_buttons=True, footer_text=None, is_zoo=False):
    if not an: return
    nome_pt = (an.get('preferred_common_name') or an.get('name') or 'Espécie').title()
    nome_cientifico = an.get('name', "Desconhecido")

    foto = "https://via.placeholder.com/300"
    if an.get('default_photo') and an['default_photo'].get('medium_url'):
        foto = an['default_photo']['medium_url']

    classe = {"Mammalia": "Mamífero", "Aves": "Ave", "Reptilia": "Réptil",
              "Amphibia": "Anfíbio", "Actinopterygii": "Peixe"}.get(an.get('iconic_taxon_name'), "Selvagem")
    alim = random.choice(['Herbívoro', 'Carnívoro', 'Omnívoro'])
    repro = "Vivíparo" if classe == "Mamífero" else "Ovíparo"

    st.markdown(f'''
    <div class="cartao-cidadao">
        <span style="color:#ffd700; font-weight:bold; font-size:0.6em;">💳 CARTÃO DE CIDADÃO</span><br>
        <img src="{foto}" class="img-an">
        <h4 style="color:#ffd700; margin:8px 0; font-size:1em;">{nome_pt}</h4>
        <p style="color:#aaa; font-size:0.7em;">{nome_cientifico}</p>
        <p style="margin:2px 0; font-size:0.8em; text-align:left; padding-left:5px;">🐾 <b>Classe:</b> {classe}</p>
        <p style="margin:2px 0; font-size:0.8em; text-align:left; padding-left:5px;">🥚 <b>Repro:</b> {repro}</p>
        <p style="margin:2px 0; font-size:0.8em; text-align:left; padding-left:5px;">🥩 <b>Alimentação:</b> {alim}</p>
        {f'<p style="color:#ffd700; font-weight:bold; margin-top:5px; font-size:0.8em;">{footer_text}</p>' if footer_text else ''}
    </div>
    ''', unsafe_allow_html=True)

    if show_buttons:
        c1, c2, c3 = st.columns(3)
        with c1:
            if is_zoo:
                if st.button("🗑️", key=f"d_{prefixo}_{idx}"):
                    st.session_state.zoo.pop(idx); st.rerun()
            else:
                if st.button("📥", key=f"z_{prefixo}_{idx}"):
                    st.session_state.zoo.append(an); st.toast("No Zoo!")
        with c2:
            if st.button("🧬", key=f"f_{prefixo}_{idx}"):
                st.session_state.tanque_fusao.append(an); st.toast("DNA Coletado!")
        with c3:
            if st.button("🔊", key=f"s_{prefixo}_{idx}"):
                st.info(f"🔊 IA encontrou som de {nome_pt}")

# ----------------------
# SIDEBAR
# ----------------------
with st.sidebar:
    st.title("🌍 MundoVivo")
    if is_24h_valido or is_mega:
        st.session_state.premium_ativo = st.toggle("✨ MODO PREMIUM", value=st.session_state.premium_ativo)

    menu = ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    if st.session_state.premium_ativo:
        menu = ["🌀 Salvamento", "🏥 Veterinário", "🧬 Tanque de Fusão", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    aba = st.radio("Navegação", menu)

# ----------------------
# FUNÇÃO GRID
# ----------------------
def grid(lista, prefixo):
    for i in range(0, len(lista), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(lista):
                with cols[j]: card(lista[i+j], prefixo, i+j)

# ----------------------
# FUNÇÃO DE API SEGURA
# ----------------------
def safe_api(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return []
        return r.json().get("results", [])
    except:
        return []

# ----------------------
# ABAS
# ----------------------
if aba in ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países"]:
    lista_loc = ["Amazónia", "Oceano Pacífico", "Portugal", "Brasil"] + [f"País{i}" for i in range(5,71)]
    sel = st.selectbox("Localização:", lista_loc)
    lista = safe_api(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=70&locale=pt-PT")
    grid(lista, "exp")

elif aba == "🔬 Laboratório":
    if st.session_state.premium_ativo:
        st.header("🔬 Laboratório MundoVivo")
        animais_input = st.text_input("Digite nomes de animais (até 3, separados por vírgula):")
        if animais_input:
            nomes = [x.strip() for x in animais_input.split(",")][:3]
            lista = []
            for n in nomes:
                res = safe_api(f"https://api.inaturalist.org/v1/taxa?q={n}&per_page=1&locale=pt-PT")
                if res:
                    lista.append(res[0])
            grid(lista, "lab")
    else:
        st.info("Ativa o premium para acessar o laboratório 🧪")

elif aba == "🐾 Meu Zoo":
    grid(st.session_state.zoo, "zoo")

elif aba == "⚙️ Definições":
    st.session_state.c_mega = st.text_input("Código Mega", type="password", value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input("Código 24h", type="password", value=st.session_state.c_24h)
    if st.button("Guardar"): st.rerun()
