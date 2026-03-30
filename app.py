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
                if st.button("🔊", key=f"s_{prefixo}_{idx}"):
                    audio_url = buscar_audio(an)
                    if audio_url:
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
        if not results:  # fallback: criar 5 animais fake
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
if aba in ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países"]:
    if aba == "🌲 Florestas":
        lista_loc = ["Amazônia", "Savana Africana", "Floresta Temperada", "Deserto"]
    elif aba == "🌊 Oceanos":
        lista_loc = ["Oceano Pacífico", "Oceano Atlântico", "Oceano Índico", "Mar Mediterrâneo"]
    else:  # Países
        lista_loc = ["Portugal", "Brasil", "EUA", "China", "Japão", "Índia", "França", "Alemanha", "Itália", "México",
                     "Canadá", "Austrália", "Argentina", "Rússia", "Noruega", "Suécia", "Finlândia", "Egito",
                     "África do Sul", "Marrocos", "Nigéria", "Quênia", "Turquia", "Grécia", "Holanda", "Bélgica",
                     "Polônia", "Suíça", "Áustria", "Hungria", "Irlanda", "Nova Zelândia", "Chile", "Peru", "Colômbia",
                     "Venezuela", "Cuba", "Coreia do Sul", "Coreia do Norte", "Tailândia", "Indonésia", "Malásia",
                     "Filipinas", "Singapura", "Paquistão", "Bangladesh", "Sri Lanka", "Nepal", "Butão", "Mianmar",
                     "Laos", "Camboja", "Vietnam", "Uzbequistão", "Cazaquistão", "Quirguistão", "Tajiquistão",
                     "Afeganistão", "Irã", "Iraque", "Síria", "Líbano", "Israel", "Jordânia", "Emirados Árabes",
                     "Arábia Saudita", "Omã", "Iémen", "Kuwait", "Bahrein", "Qatar"]
    sel = st.selectbox("Localização:", lista_loc)
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=70")
    grid(r.json().get('results', []), "exp")

elif aba == "🔬 Laboratório":
    st.header("🔬 Laboratório de Animais")
    lista_loc = ["Amazônia", "Savana Africana", "Floresta Temperada", "Deserto", "Oceano Pacífico", "Oceano Atlântico", "Oceano Índico"]
    sel = st.selectbox("Escolha a pesquisa:", lista_loc)
    query = sel.replace(" ", "%20")
    url_api = f"https://api.inaturalist.org/v1/taxa?q={query}&taxon_id=1&per_page=70"
    animais = safe_api(url_api)
    grid(animais, "lab")

elif aba == "🐾 Meu Zoo":
    grid(st.session_state.zoo, "zoo")

elif aba == "🌀 Salvamento" and premium_real and st.session_state.premium_ativo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/World_map_-_low_resolution.svg/1000px-World_map_-_low_resolution.svg.png")
    if not st.session_state.id_animal_atual:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q=Africa&taxon_id=1&per_page=1")
        if r.json()['results']: st.session_state.id_animal_atual = r.json()['results'][0]
    if st.session_state.id_animal_atual:
        card(st.session_state.id_animal_atual, "res", 0, show_buttons=False)
        if st.button("🚁 ENVIAR HELICÓPTERO"):
            st.markdown('<div class="heli-anim">🚁</div>', unsafe_allow_html=True)
            time.sleep(3)
            st.session_state.internados_vet.append({'animal': st.session_state.id_animal_atual, 'data_alta': (datetime.now() + timedelta(hours=24)).timestamp()})
            st.session_state.id_animal_atual = None; st.rerun()

elif aba == "🏥 Veterinário" and premium_real and st.session_state.premium_ativo:
    st.header("🏥 Hospital")
    if not st.session_state.internados_vet: st.info("Sem animais feridos.")
    for i, item in enumerate(st.session_state.internados_vet):
        falta = item['data_alta'] - datetime.now().timestamp()
        txt = f"⏳ {int(falta//3600)}h" if falta > 0 else "✅ ALTA"
        card(item['animal'], "vet", i, show_buttons=False, footer_text=txt)
        if falta <= 0 and st.button("🏁 Zoo", key=f"mv_{i}"):
            st.session_state.zoo.append(item['animal']); st.session_state.internados_vet.pop(i); st.rerun()

elif aba == "🧬 Tanque de Fusão" and premium_real and st.session_state.premium_ativo:
    if len(st.session_state.tanque_fusao) < 2: st.info("Colete DNA!")
    else:
        n1 = st.selectbox("Mãe:", [a.get('name') for a in st.session_state.tanque_fusao], key="f1")
        n2 = st.selectbox("Pai:", [a.get('name') for a in st.session_state.tanque_fusao], key="f2")
        if st.button("🔬 FUNDIR"):
            st.success(f"Nova Espécie: **{n1.split()[0]} {n2.split()[-1]}**")

elif aba == "⚙️ Definições":
    st.session_state.c_mega = st.text_input("Código Mega", type="password", value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input("Código 24h", type="password", value=st.session_state.c_24h)
    if st.button("Guardar"): st.rerun()
