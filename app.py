import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# ----------------------
# 1. ESTADO DO SISTEMA
# ----------------------
chaves = {
    'zoo': [], 'tanque_fusao': [], 'pontos_zoologo': 0,
    'animais_salvos_ids': set(), 'id_animal_atual': None,
    'internados_vet': [], 'c_24h': "", 'c_mega': "",
    'premium_ativo': False, 'cor_tema': "#0b1117", 'brilho': 100,
    'inicio_sessao_24h': None, 'quiz_score': 0,
    'laboratorio_animais': []
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# ----------------------
# 2. LÓGICA DE CÓDIGOS
# ----------------------
is_mega = st.session_state.c_mega == "67lucas62"
is_24h_valido = False
if st.session_state.c_24h == "6626":
    if st.session_state.inicio_sessao_24h is None:
        st.session_state.inicio_sessao_24h = datetime.now().timestamp()
    if (datetime.now().timestamp() - st.session_state.inicio_sessao_24h) < 86400:
        is_24h_valido = True

# ----------------------
# 3. CSS BLINDADO
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
    .img-an {{ width: 100%; border-radius: 15px; height: 200px; object-fit: cover; border: 1px solid #444; filter: none !important; }}
    .multi-cartao {{ display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }}
</style>
""", unsafe_allow_html=True)

# ----------------------
# 4. FUNÇÃO DO CARTÃO
# ----------------------
def card_merlin(an, show_sound=True):
    if not an: return
    nome_pt = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    classe = {"Mammalia": "Mamífero", "Aves": "Ave", "Reptilia": "Réptil",
              "Amphibia": "Anfíbio", "Actinopterygii": "Peixe"}.get(an.get('iconic_taxon_name'), "Selvagem")
    alim = random.choice(['Herbívoro', 'Carnívoro', 'Omnívoro'])
    repro = "Vivíparo" if classe == "Mamífero" else "Ovíparo"
    
    st.markdown(f'''
    <div class="cartao-cidadao">
        <h2 style="color:#ffd700; margin:5px 0;">{nome_pt}</h2>
        <img src="{foto}" class="img-an">
        <p>🐾 <b>Classe:</b> {classe}</p>
        <p>🥚 <b>Repro:</b> {repro}</p>
        <p>🥩 <b>Alimentação:</b> {alim}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    if show_sound:
        if st.button(f"🔊 Ouvir {nome_pt}", key=f"snd_{nome_pt}"):
            # Aqui simulamos IA buscando som online
            st.info(f"IA encontrou sons de {nome_pt} na internet! 🔊")
            # st.audio('URL_DO_SOM') -> Aqui você colocaria a URL real obtida pela IA

# ----------------------
# 5. SIDEBAR
# ----------------------
with st.sidebar:
    st.title("🌍 MundoVivo")
    if is_24h_valido:
        res = 86400 - (datetime.now().timestamp() - st.session_state.inicio_sessao_24h)
        st.write(f"⏳ Premium: {int(res//3600)}h {int((res%3600)//60)}m")
    
    if is_mega or is_24h_valido:
        st.session_state.premium_ativo = st.toggle("✨ MODO PREMIUM", value=st.session_state.premium_ativo)
    
    menu = ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições", "🎯 Quiz"]
    if st.session_state.premium_ativo:
        menu += ["🌀 Salvamento", "🏥 Veterinário", "🧬 Tanque de Fusão"]
    aba = st.radio("Navegação", menu)

# ----------------------
# 6. LOGICA DE GRELHA
# ----------------------
def grid(lista, prefixo):
    for i in range(0, len(lista), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(lista):
                with cols[j]: card_merlin(lista[i+j], show_sound=False)

# ----------------------
# 7. ABAS
# ----------------------
# Florestas, Oceanos, Países
if aba in ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países"]:
    lista_loc = ["Amazónia", "Oceano Pacífico", "Portugal", "Brasil"]
    sel = st.selectbox("Localização:", lista_loc)
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=12&locale=pt-PT")
    grid(r.json().get('results', []), "exp")

# Laboratório (Premium)
elif aba == "🔬 Laboratório" and st.session_state.premium_ativo:
    st.header("🔬 Laboratório MundoVivo")
    animais_input = st.text_input("Digite nomes de animais (separados por vírgula):")
    if animais_input:
        nomes = [x.strip() for x in animais_input.split(",")][:3]  # máximo 3 animais
        st.session_state.laboratorio_animais = []
        for n in nomes:
            r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={n}&per_page=1&locale=pt-PT")
            if r.json()['results']:
                st.session_state.laboratorio_animais.append(r.json()['results'][0])
    if st.session_state.laboratorio_animais:
        st.markdown('<div class="multi-cartao">', unsafe_allow_html=True)
        for an in st.session_state.laboratorio_animais:
            card_merlin(an, show_sound=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Quiz
elif aba == "🎯 Quiz":
    st.header("🎯 Quiz: Qual é este animal?")
    if "quiz_animal" not in st.session_state or st.button("Novo Quiz"):
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q=Africa&taxon_id=1&per_page=1&locale=pt-PT")
        if r.json()['results']:
            st.session_state.quiz_animal = r.json()['results'][0]
    an = st.session_state.quiz_animal
    if an:
        st.image(an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300"))
        options = [an.get('preferred_common_name') or an.get('name')]
        fake_names = ["Leopardo", "Girafa", "Tigre", "Elefante", "Crocodilo"]
        while len(options) < 3:
            fake = random.choice(fake_names)
            if fake not in options: options.append(fake)
        random.shuffle(options)
        choice = st.radio("Escolha o nome correto:", options)
        if st.button("Verificar"):
            if choice == (an.get('preferred_common_name') or an.get('name')):
                st.success("✅ Correto! +1 ponto")
                st.session_state.quiz_score += 1
            else:
                st.error("❌ Errado!")
            st.write(f"Pontuação: {st.session_state.quiz_score}")

# Meu Zoo
elif aba == "🐾 Meu Zoo":
    grid(st.session_state.zoo, "zoo")

# Tanque de Fusão
elif aba == "🧬 Tanque de Fusão" and st.session_state.premium_ativo:
    if len(st.session_state.tanque_fusao) < 2: st.info("Colete DNA!")
    else:
        n1 = st.selectbox("Mãe:", [a.get('name') for a in st.session_state.tanque_fusao], key="f1")
        n2 = st.selectbox("Pai:", [a.get('name') for a in st.session_state.tanque_fusao], key="f2")
        if st.button("🔬 FUNDIR"):
            st.success(f"Nova Espécie: **{n1.split()[0]} {n2.split()[-1]}**")

# Salvamento
elif aba == "🌀 Salvamento" and st.session_state.premium_ativo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/World_map_-_low_resolution.svg/1000px-World_map_-_low_resolution.svg.png")
    if not st.session_state.id_animal_atual:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q=Africa&taxon_id=1&per_page=1&locale=pt-PT")
        if r.json()['results']: st.session_state.id_animal_atual = r.json()['results'][0]
    if st.session_state.id_animal_atual:
        card_merlin(st.session_state.id_animal_atual, show_sound=False)
        if st.button("🚁 ENVIAR HELICÓPTERO"):
            st.markdown('<div class="heli-anim">🚁</div>', unsafe_allow_html=True)
            time.sleep(3)
            st.session_state.internados_vet.append({'animal': st.session_state.id_animal_atual, 'data_alta': (datetime.now() + timedelta(hours=24)).timestamp()})
            st.session_state.id_animal_atual = None; st.rerun()

# Veterinário
elif aba == "🏥 Veterinário" and st.session_state.premium_ativo:
    st.header("🏥 Hospital")
    if not st.session_state.internados_vet: st.info("Sem animais feridos.")
    for i, item in enumerate(st.session_state.internados_vet):
        falta = item['data_alta'] - datetime.now().timestamp()
        txt = f"⏳ {int(falta//3600)}h" if falta > 0 else "✅ ALTA"
        card_merlin(item['animal'], show_sound=False)
        if falta <= 0 and st.button("🏁 Zoo", key=f"mv_{i}"):
            st.session_state.zoo.append(item['animal']); st.session_state.internados_vet.pop(i); st.rerun()

# Definições
elif aba == "⚙️ Definições":
    st.session_state.c_mega = st.text_input("Código Mega", type="password", value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input("Código 24h", type="password", value=st.session_state.c_24h)
    if st.button("Guardar"): st.rerun()
