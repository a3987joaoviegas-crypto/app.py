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
    background-color: #1a1c23 !important; border-radius: 20px; padding: 12px; 
    {borda_css} margin-bottom: 15px; text-align: center; color: white;
}}
.img-an {{ width: 100%; border-radius: 15px; height: 130px; object-fit: cover; border: 1px solid #444; filter: none !important; }}
@keyframes heli {{ 0% {{ transform: translateX(-200px); }} 100% {{ transform: translateX(110vw); }} }}
.heli-anim {{ position: fixed; top: 30%; font-size: 80px; z-index: 9999; animation: heli 3s linear forwards; }}
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
# CARTÃO
# ----------------------
def card(an, prefixo, idx=0, show_buttons=True, footer_text=None, is_zoo=False):
    if not an:
        return

    nome_pt = (an.get('preferred_common_name') or an.get('name') or 'Espécie').title()
    nome_cientifico = an.get('name', "Desconhecido")

    foto_data = an.get('default_photo') or {}
    foto = foto_data.get('medium_url', "https://via.placeholder.com/300")

    classe = {
        "Mammalia": "Mamífero",
        "Aves": "Ave",
        "Reptilia": "Réptil",
        "Amphibia": "Anfíbio",
        "Actinopterygii": "Peixe"
    }.get(an.get('iconic_taxon_name'), "Selvagem")

    alim = random.choice(['Herbívoro', 'Carnívoro', 'Omnívoro'])
    repro = "Vivíparo" if classe == "Mamífero" else "Ovíparo"

    st.markdown(f'''
    <div class="cartao-cidadao">
        <span style="color:#ffd700; font-weight:bold; font-size:0.6em;">💳 CARTÃO DE CIDADÃO</span><br>
        <img src="{foto}" class="img-an">
        <h4 style="color:#ffd700; margin:8px 0; font-size:1em;">{nome_pt}</h4>
        <p style="color:#aaa; font-size:0.7em;">{nome_cientifico}</p>
        <p style="margin:2px 0; font-size:0.8em; text-align:left;">🐾 <b>Classe:</b> {classe}</p>
        <p style="margin:2px 0; font-size:0.8em; text-align:left;">🥚 <b>Repro:</b> {repro}</p>
        <p style="margin:2px 0; font-size:0.8em; text-align:left;">🥩 <b>Alimentação:</b> {alim}</p>
        {f'<p style="color:#ffd700; font-weight:bold;">{footer_text}</p>' if footer_text else ''}
    </div>
    ''', unsafe_allow_html=True)

    if show_buttons:
        c1, c2, c3, c4 = st.columns([1,1,1,1])

        with c1:
            if is_zoo:
                if st.button("🗑️", key=f"d_{prefixo}_{idx}"):
                    st.session_state.zoo.pop(idx)
                    st.rerun()
            else:
                if st.button("📥", key=f"z_{prefixo}_{idx}"):
                    st.session_state.zoo.append(an)
                    st.toast("No Zoo!")

        with c2:
            if st.button("🧬", key=f"f_{prefixo}_{idx}"):
                st.session_state.tanque_fusao.append(an)
                st.toast("DNA Coletado!")

        with c3:
            audio_url = buscar_audio(an)
            if audio_url and st.button("🔊", key=f"s_{prefixo}_{idx}"):
                st.audio(audio_url)

        with c4:
            st.button("👁️", key=f"eye_{prefixo}_{idx}")  # Botão do olho

# ----------------------
# GRID
# ----------------------
def grid(lista, prefixo=""):
    for i in range(0,len(lista),3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(lista):
                with cols[j]:
                    card(lista[i+j], f"{prefixo}_{i+j}")

# ----------------------
# LISTAS EXEMPLO
# ----------------------
florestas = ["Amazônia", "Congo", "Taiga", "Temperada", "Manguezal"]
oceanos = ["Atlântico", "Pacífico", "Índico", "Ártico", "Antártico"]
paises = ["Portugal","Brasil","EUA","França","Alemanha","Japão","China","Índia","México","Canadá"] * 7  # 70 países

# ----------------------
# SIDEBAR
# ----------------------
with st.sidebar:
    st.title("🌍 MundoVivo")

    premium = is_mega or is_24h_valido

    if premium:
        st.session_state.premium_ativo = st.toggle("✨ MODO PREMIUM", value=st.session_state.premium_ativo)

    if st.session_state.premium_ativo:
        menu = ["🌀 Salvamento", "🏥 Veterinário", "🧬 Tanque de Fusão", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    else:
        menu = ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]

    aba = st.radio("Navegação", menu)

# ----------------------
# ABAS
# ----------------------
if aba == "🌲 Florestas":
    sel = st.selectbox("Localização:", florestas)
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=12&locale=pt-PT")
    grid(r.json().get('results', []), "exp")

elif aba == "🌊 Oceanos":
    sel = st.selectbox("Localização:", oceanos)
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=12&locale=pt-PT")
    grid(r.json().get('results', []), "exp")

elif aba == "🏳️ Países":
    sel = st.selectbox("País:", paises)
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=12&locale=pt-PT")
    grid(r.json().get('results', []), "exp")

elif aba == "🌀 Salvamento":
    st.image(f"https://source.unsplash.com/600x200/?animal,{random.randint(1,100)}")
    if not st.session_state.id_animal_atual:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q=Animal&taxon_id=1&per_page=1&locale=pt-PT")
        if r.json()['results']: st.session_state.id_animal_atual = r.json()['results'][0]
    if st.session_state.id_animal_atual:
        card(st.session_state.id_animal_atual, "res", 0, show_buttons=False)
        if st.button("🚁 ENVIAR HELICÓPTERO"):
            st.markdown('<div class="heli-anim">🚁</div>', unsafe_allow_html=True)
            time.sleep(3)
            st.session_state.internados_vet.append({'animal': st.session_state.id_animal_atual, 'data_alta': (datetime.now() + timedelta(hours=24)).timestamp()})
            st.session_state.id_animal_atual = None
            st.rerun()

elif aba == "🏥 Veterinário":
    st.header("🏥 Hospital")
    if not st.session_state.internados_vet: st.info("Sem animais feridos.")
    for i, item in enumerate(st.session_state.internados_vet):
        falta = item['data_alta'] - datetime.now().timestamp()
        txt = f"⏳ {int(falta//3600)}h" if falta > 0 else "✅ ALTA"
        card(item['animal'], "vet", i, show_buttons=False, footer_text=txt)
        if falta <= 0 and st.button("🏁 Zoo", key=f"mv_{i}"):
            st.session_state.zoo.append(item['animal'])
            st.session_state.internados_vet.pop(i)
            st.rerun()

elif aba == "🧬 Tanque de Fusão":
    if len(st.session_state.tanque_fusao) < 2: st.info("Colete DNA!")
    else:
        n1 = st.selectbox("Mãe:", [a.get('name') for a in st.session_state.tanque_fusao], key="f1")
        n2 = st.selectbox("Pai:", [a.get('name') for a in st.session_state.tanque_fusao], key="f2")
        if st.button("🔬 FUNDIR"):
            st.success(f"Nova Espécie: **{n1.split()[0]} {n2.split()[-1]}**")

elif aba == "🐾 Meu Zoo":
    grid(st.session_state.zoo, "zoo")

elif aba == "🔬 Laboratório":
    termo = st.text_input("Pesquisar animal livremente:")
    if termo:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={termo}&per_page=12&locale=pt-PT")
        results = r.json().get('results', [])
        if results:
            grid(results, "lab")
        else:
            st.info("Nenhum resultado encontrado.")

elif aba == "⚙️ Definições":
    st.session_state.c_mega = st.text_input("Código Mega", type="password", value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input("Código 24h", type="password", value=st.session_state.c_24h)
    if st.button("Guardar"): st.rerun()
