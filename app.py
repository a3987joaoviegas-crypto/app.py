import streamlit as st
import requests
import random
from datetime import datetime, timedelta

# ----------------------
# ESTADO
# ----------------------
chaves = {
    'zoo': [], 'tanque_fusao': [], 'pontos_zoologo': 0,
    'animais_salvos_ids': set(), 'id_animal_atual': None,
    'internados_vet': [], 'c_24h': '', 'c_mega': '',
    'premium_ativo': False, 'cor_tema': '#0b1117', 'brilho': 100,
    'inicio_sessao_24h': None
}
for k, v in chaves.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ----------------------
# PREMIUM
# ----------------------
is_mega = st.session_state.c_mega == '67lucas62'
is_24h_valido = False
if st.session_state.c_24h == '6626':
    if st.session_state.inicio_sessao_24h is None:
        st.session_state.inicio_sessao_24h = datetime.now().timestamp()
    if (datetime.now().timestamp() - st.session_state.inicio_sessao_24h) < 86400:
        is_24h_valido = True

# ----------------------
# CSS
# ----------------------
if is_mega:
    borda_css = "border:5px solid; border-image: linear-gradient(var(--angle),red,orange,yellow,green,blue,indigo,violet) 1; animation:rotate_grad 3s linear infinite;"
elif is_24h_valido:
    borda_css = "border:5px solid #ffd700;"
else:
    borda_css = "border:4px solid #2ecc71;"

st.markdown(f"""
<style>
@property --angle {{ syntax: '<angle>'; initial-value: 0deg; inherits: false; }}
@keyframes rotate_grad {{ to {{ --angle:360deg; }} }}
.stApp {{ background-color:{st.session_state.cor_tema}; filter:brightness({st.session_state.brilho/100}); }}
.cartao-cidadao {{
    background-color:#1a1c23 !important;
    border-radius:20px;
    padding:12px;
    {borda_css}
    margin-bottom:15px;
    text-align:center;
    color:white;
}}
.img-an {{
    width:100%;
    border-radius:15px;
    height:130px;
    object-fit:cover;
}}
</style>
""", unsafe_allow_html=True)

# ----------------------
# FUNÇÃO CARTÃO DE CIDADÃO
# ----------------------
def card(an):
    if not an or an.get('iconic_taxon_name') == 'Plantae':
        return
    nome_pt = (an.get('preferred_common_name') or an.get('name','Espécie')).title()
    nome_cient = an.get('name','Desconhecido')
    foto = (an.get('default_photo') or {}).get('medium_url','https://via.placeholder.com/300')
    classe = {"Mammalia":"Mamífero","Aves":"Ave","Reptilia":"Réptil","Amphibia":"Anfíbio","Actinopterygii":"Peixe"}.get(an.get('iconic_taxon_name'),"Selvagem")
    alim = random.choice(['Herbívoro','Carnívoro','Omnívoro'])
    repro = "Vivíparo" if classe=="Mamífero" else "Ovíparo"
    st.markdown(f'''
    <div class="cartao-cidadao">
        <img src="{foto}" class="img-an">
        <h4 style="color:#ffd700; margin:5px 0 0 0;">{nome_pt}</h4>
        <p style="margin:2px 0; font-size:0.8em; font-style:italic;">{nome_cient}</p>
        <p style="margin:2px 0; font-size:0.8em;">🐾 <b>Classe:</b> {classe}</p>
        <p style="margin:2px 0; font-size:0.8em;">🥚 <b>Reprodução:</b> {repro}</p>
        <p style="margin:2px 0; font-size:0.8em;">🥩 <b>Alimentação:</b> {alim}</p>
    </div>
    ''', unsafe_allow_html=True)

# ----------------------
# GRELHA
# ----------------------
def grid(lista):
    for i in range(0,len(lista),3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(lista):
                with cols[j]:
                    card(lista[i+j])

# ----------------------
# FUNÇÃO BUSCAR ANIMAIS
# ----------------------
def get_animais(query):
    r = requests.get(f'https://api.inaturalist.org/v1/taxa?q={query}&taxon_id=1&per_page=70&locale=pt-PT')
    results = [a for a in r.json().get('results',[]) if a.get('iconic_taxon_name') != 'Plantae']
    return results[:70]

# ----------------------
# SIDEBAR
# ----------------------
with st.sidebar:
    st.title('🌍 MundoVivo')
    menu = ['🌲 Florestas','🌊 Oceanos','🏳️ Países','🔬 Laboratório','🐾 Meu Zoo','⚙️ Definições']
    premium_checkbox = False
    if is_mega or is_24h_valido:
        premium_checkbox = st.checkbox('✨ Premium', value=st.session_state.premium_ativo)
        st.session_state.premium_ativo = premium_checkbox
        if premium_checkbox:
            menu = ['🌀 Salvamento','🏥 Veterinário','🧬 Tanque de Fusão','🔬 Laboratório','🐾 Meu Zoo','⚙️ Definições']
    aba = st.radio('Navegação', menu)

# ----------------------
# ABAS
# ----------------------
if aba == '🌲 Florestas':
    florestas = ['Amazónia','Congo','Taiga','Savana']
    sel = st.selectbox('Escolha a floresta:', florestas)
    grid(get_animais(sel))

elif aba == '🌊 Oceanos':
    oceanos = ['Oceano Pacífico','Atlântico','Índico','Ártico','Antártico']
    sel = st.selectbox('Escolha o oceano:', oceanos)
    grid(get_animais(sel))

elif aba == '🏳️ Países':
    paises = [
        'Portugal','Espanha','França','Alemanha','Itália','Reino Unido','Bélgica','Países Baixos','Suíça','Áustria',
        'Polónia','República Checa','Hungria','Eslováquia','Roménia','Bulgária','Grécia','Dinamarca','Noruega','Suécia',
        'Finlândia','Islândia','Irlanda','Luxemburgo','Malta','Chipre','Estónia','Letónia','Lituânia','Ucrânia',
        'Bielorrússia','Rússia','Sérvia','Croácia','Bósnia','Eslovénia','Macedónia','Albânia','Montenegro','Kosovo',
        'Turquia','Arménia','Geórgia','Azerbaijão','Cazaquistão','Uzbequistão','Quirguistão','Tadjiquistão','Turquemenistão',
        'Afeganistão','Irão','Iraque','Síria','Líbano','Israel','Jordânia','Egipto','Líbia','Tunísia','Argélia','Marrocos',
        'Sudão','Etiópia','Somália','Quénia','Uganda','Tanzânia','Moçambique','Angola','Zâmbia','Zimbabwe','Botswana','Namíbia'
    ]
    sel = st.selectbox('Escolha o país:', paises)
    grid(get_animais(sel))

elif aba == '🔬 Laboratório':
    query = st.text_input('Pesquisar animal (qualquer nome):')
    if query:
        grid(get_animais(query))
    else:
        st.info('Digite um nome para pesquisar.')

elif aba == '🐾 Meu Zoo':
    grid(st.session_state.zoo)

elif aba == '🌀 Salvamento' and st.session_state.premium_ativo:
    animais = [a for a in get_animais("animal") if a.get('id') not in st.session_state.animais_salvos_ids]
    for an in animais:
        card(an)
        if st.button(f"Salvar {an.get('preferred_common_name','Animal')}", key=f"salvar_{an.get('id')}"):
            st.session_state.zoo.append(an)
            st.session_state.animais_salvos_ids.add(an.get('id'))
            st.success(f"{an.get('preferred_common_name','Animal')} salvo!")

elif aba == '🏥 Veterinário' and st.session_state.premium_ativo:
    for an in st.session_state.internados_vet:
        st.markdown(f"{an.get('preferred_common_name','Animal')} - Alta em 24h")
    if st.button("Internar novo animal"):
        if st.session_state.zoo:
            an = random.choice(st.session_state.zoo)
            st.session_state.internados_vet.append(an)
            st.success(f"{an.get('preferred_common_name','Animal')} internado.")

elif aba == '🧬 Tanque de Fusão' and st.session_state.premium_ativo:
    grid(get_animais("animal"))

elif aba == '⚙️ Definições':
    st.session_state.c_mega = st.text_input('Código Mega', type='password', value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input('Código 24h', type='password', value=st.session_state.c_24h)
    if st.button('Guardar'):
        st.success('Definições guardadas com sucesso!')
