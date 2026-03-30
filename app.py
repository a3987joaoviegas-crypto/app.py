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
            if st.button("🔊", key=f"s_{prefixo}_{idx}"):
                # Placeholder de som funcional
                st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3")

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
        return r.json().get("results", [])
    except:
        return []

# ----------------------
# SIDEBAR COM PREMIUM CORRIGIDO
# ----------------------
with st.sidebar:
    st.title("🌍 MundoVivo")

    # Verifica premium real
    premium_real = is_mega or is_24h_valido
    if premium_real:
        st.session_state.premium_ativo = st.toggle("✨ MODO PREMIUM", value=st.session_state.premium_ativo)

    # Menu
    if premium_real and st.session_state.premium_ativo:
        menu = ["🌀 Salvamento", "🏥 Veterinário", "🧬 Tanque de Fusão", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    else:
        menu = ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]

    aba = st.radio("Navegação", menu)

# ----------------------
# ABAS
# ----------------------
if aba == "🌲 Florestas":
    lista_loc = ["Amazónia", "Congo", "Taiga", "Mata Atlântica"]
    sel = st.selectbox("Florestas:", lista_loc)
    lista = safe_api(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=70&locale=pt-PT")
    grid(lista, "exp")

elif aba == "🌊 Oceanos":
    oceanos = ["Oceano Pacífico", "Oceano Atlântico", "Oceano Índico", "Oceano Ártico", "Oceano Antártico",
               "Mar Mediterrâneo", "Mar do Caribe", "Mar da China"]
    sel = st.selectbox("Oceanos e Mares:", oceanos)
    lista = safe_api(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=70&locale=pt-PT")
    grid(lista, "exp")

elif aba == "🏳️ Países":
    paises = [
        "Afeganistão","África do Sul","Albânia","Alemanha","Andorra","Angola","Antígua e Barbuda","Arábia Saudita","Argélia","Argentina",
        "Arménia","Austrália","Áustria","Azerbaijão","Bahamas","Bangladesh","Barbados","Barein","Bélgica","Belize",
        "Benim","Bielorrússia","Bolívia","Bósnia e Herzegovina","Botsuana","Brasil","Brunei","Bulgária","Burkina Faso","Burúndi",
        "Butão","Cabo Verde","Camarões","Camboja","Canadá","Catar","Cazaquistão","Chade","Chile","China",
        "Chipre","Colômbia","Comores","Coreia do Norte","Coreia do Sul","Costa do Marfim","Costa Rica","Croácia","Cuba","Dinamarca",
        "Djibuti","Dominica","Egito","El Salvador","Emirados Árabes Unidos","Equador","Eritreia","Eslováquia","Eslovénia","Espanha",
        "Estónia","Estados Unidos","Eswatini","Etiópia","Fiji","Filipinas","Finlândia","França","Gabão","Gâmbia",
        "Gana","Geórgia","Grécia","Granada","Guatemala","Guiné","Guiné-Bissau","Guiné Equatorial","Haiti","Honduras"
    ]
    sel = st.selectbox("País:", paises)
    lista = safe_api(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=70&locale=pt-PT")
    grid(lista, "exp")

elif aba == "🔬 Laboratório":
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

elif aba == "🐾 Meu Zoo":
    grid(st.session_state.zoo, "zoo")

elif aba == "🌀 Salvamento" and premium_real and st.session_state.premium_ativo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/World_map_-_low_resolution.svg/1000px-World_map_-_low_resolution.svg.png")
    if not st.session_state.id_animal_atual:
        r = safe_api(f"https://api.inaturalist.org/v1/taxa?q=Africa&taxon_id=1&per_page=1&locale=pt-PT")
        if r: st.session_state.id_animal_atual = r[0]
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
