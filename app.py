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
borda_css = "border: 4px solid #2ecc71;" if not (is_mega or is_24h_valido) else (
    "border: 5px solid #ffd700;" if is_24h_valido else
    "border: 5px solid; border-image: linear-gradient(var(--angle), red, orange, yellow, green, blue, indigo, violet) 1; animation: rotate_grad 3s linear infinite;"
)
st.markdown(f"""
<style>
@property --angle {{ syntax: '<angle>'; initial-value: 0deg; inherits: false; }}
@keyframes rotate_grad {{ to {{ --angle: 360deg; }} }}
.stApp {{ background-color: {st.session_state.cor_tema}; filter: brightness({st.session_state.brilho/100}); }}
.cartao-cidadao {{
    background-color: #1a1c23 !important;
    border-radius: 15px;
    padding: 8px;
    {borda_css}
    text-align: center;
    color: white;
    max-width: 250px;
    margin: auto;
}}
.img-an {{
    width: 100%;
    height: 120px;
    object-fit: cover;
    border-radius: 10px;
    border: 1px solid #444;
}}
@keyframes heli {{ 0% {{ transform: translateX(-200px); }} 100% {{ transform: translateX(110vw); }} }}
.heli-anim {{ position: fixed; top: 30%; font-size: 80px; z-index: 9999; animation: heli 3s linear forwards; }}
</style>
""", unsafe_allow_html=True)

# ----------------------
# FUNÇÃO DE BUSCA DE ÁUDIO (APENAS AVES)
# ----------------------
def buscar_audio(animal):
    if animal.get("iconic_taxon_name") != "Aves":
        return None
    nome_cientifico = animal.get("name")
    if not nome_cientifico: return None
    query = nome_cientifico.replace(" ", "+")
    try:
        r = requests.get(f"https://www.xeno-canto.org/api/2/recordings?query={query}", timeout=5)
        if r.status_code != 200: return None
        results = r.json().get("recordings", [])
        if results:
            file_url = "https:" + results[0].get("file")
            return file_url
    except:
        return None
    return None

# ----------------------
# FUNÇÃO DE CARTÃO
# ----------------------
def card(an, prefixo, idx=0, show_buttons=True, footer_text=None, is_zoo=False):
    if not an: return
    nome_pt = (an.get('preferred_common_name') or an.get('name') or 'Espécie').title()
    nome_cientifico = an.get('name', "Desconhecido")
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    classe = {"Mammalia": "Mamífero", "Aves": "Ave", "Reptilia": "Réptil",
              "Amphibia": "Anfíbio", "Actinopterygii": "Peixe"}.get(an.get('iconic_taxon_name'), "Selvagem")
    alim = random.choice(['Herbívoro', 'Carnívoro', 'Omnívoro'])
    repro = "Vivíparo" if classe == "Mamífero" else "Ovíparo"

    st.markdown(f'''
    <div class="cartao-cidadao">
        <span style="color:#ffd700; font-weight:bold; font-size:0.6em;">💳 CARTÃO DE CIDADÃO</span><br>
        <img src="{foto}" class="img-an">
        <h4 style="color:#ffd700; margin:4px 0;">{nome_pt}</h4>
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
            if an.get("iconic_taxon_name") == "Aves":
                audio_url = buscar_audio(an)
                if audio_url and st.button("🔊", key=f"s_{prefixo}_{idx}"):
                    st.audio(audio_url, format="audio/mp3")

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
# API SEGURA
# ----------------------
def safe_api(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return []
        results = r.json().get("results", [])
        if not results:
            results = [{"name": f"AnimalFake{i}", "preferred_common_name": f"Espécie{i}",
                        "iconic_taxon_name": random.choice(["Mammalia","Aves","Reptilia","Amphibia","Actinopterygii"]),
                        "default_photo": {"medium_url":"https://via.placeholder.com/300"}} for i in range(5)]
        return results
    except:
        return []

# ----------------------
# SIDEBAR
# ----------------------
with st.sidebar:
    st.title("🌍 MundoVivo")
    premium_real = is_mega or is_24h_valido
    if premium_real:
        st.session_state.premium_ativo = st.toggle("✨ MODO PREMIUM", value=st.session_state.premium_ativo)
    if premium_real and st.session_state.premium_ativo:
        menu = ["🌀 Salvamento", "🏥 Veterinário", "🧬 Tanque de Fusão", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    else:
        menu = ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    aba = st.radio("Navegação", menu)

# ----------------------
# ABAS
# ----------------------
# Florestas, Oceanos, Países
if aba in ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países"]:
    if aba == "🌲 Florestas":
        lista_loc = ["Amazônia", "Savana Africana", "Floresta Temperada", "Deserto", "Taiga", "Manguezal"]
    elif aba == "🌊 Oceanos":
        lista_loc = ["Oceano Pacífico", "Oceano Atlântico", "Oceano Índico", "Mar Mediterrâneo",
                     "Mar do Norte", "Mar Báltico", "Mar da China Meridional"]
    else:
        lista_loc = ["Portugal","Brasil","EUA","China","Japão","Índia","França","Alemanha","Itália","México",
                     "Rússia","Canadá","Argentina","Egito","África do Sul","Marrocos","Turquia","Irã","Arábia Saudita",
                     "Coreia do Sul","Indonésia","Malásia","Tailândia","Filipinas","Vietnã","Nova Zelândia","Austrália",
                     "Colômbia","Peru","Chile","Venezuela","Bolívia","Equador","Paraguai","Uruguai","Cuba","Haiti",
                     "Jamaica","Costa Rica","Panamá","Nicarágua","Honduras","El Salvador","Guatemala","Belize",
                     "Islândia","Noruega","Suécia","Finlândia","Dinamarca","Polônia","Ucrânia","Bélgica","Holanda",
                     "Suíça","Áustria","Hungria","Romênia","Bulgária","Grécia","Portugal","Eslováquia","República Tcheca",
                     "Lituânia","Letônia","Estônia","Chipre","Malta","Luxemburgo"]
    sel = st.selectbox("Localização:", lista_loc)
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=70&locale=pt-PT")
    grid(r.json().get('results', []), "exp")

# Laboratório grátis
elif aba == "🔬 Laboratório":
    st.header("🔬 Laboratório")
    if st.session_state.premium_ativo:
        st.info("Laboratório disponível para todos, mesmo no grátis!")
    # Buscar 70 animais aleatórios
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?taxon_id=1&per_page=70&locale=pt-PT")
    grid(r.json().get("results", []), "lab")

# Aqui podes adicionar Salvamento, Veterinário, Tanque de Fusão, Meu Zoo, Definições mantendo layout do cartão
