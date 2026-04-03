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
def card(an, prefixo, idx=0, show_buttons=True, footer_text=None, is_zoo=False):
    if not an: return
    nome_pt = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    foto = (an.get('default_photo') or {}).get('medium_url', "https://via.placeholder.com/300")
    st.markdown(f'''
    <div class="cartao-cidadao">
        <span style="color:#ffd700; font-size:0.6em;">💳 CARTÃO DE CIDADÃO</span><br>
        <img src="{foto}" class="img-an">
        <h4 style="color:#ffd700;">{nome_pt}</h4>
    </div>
    ''', unsafe_allow_html=True)

    if show_buttons:
        c1, c2 = st.columns(2)
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
# BUSCAR ANIMAIS
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
    if is_24h_valido:
        res = 86400 - (datetime.now().timestamp() - st.session_state.inicio_sessao_24h)
        st.write(f"⏳ Premium: {int(res//3600)}h {int((res%3600)//60)}m")
    if is_mega or is_24h_valido:
        st.session_state.premium_ativo = st.toggle("✨ MODO PREMIUM", value=st.session_state.premium_ativo)

    menu = ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    if st.session_state.premium_ativo:
        menu = ["🌀 Salvamento", "🏥 Veterinário", "🧬 Tanque de Fusão", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    aba = st.radio("Navegação", menu)

# ----------------------
# ABAS
# ----------------------
if aba in ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países"]:
    lista_loc = florestas if aba=="🌲 Florestas" else oceanos if aba=="🌊 Oceanos" else paises
    sel = st.selectbox("Localização:", lista_loc)
    r = buscar_animais(sel)
    grid(r, "exp")

elif aba == "🌀 Salvamento":
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/World_map_-_low_resolution.svg/1000px-World_map_-_low_resolution.svg.png")
    if not st.session_state.id_animal_atual:
        r = buscar_animais("Africa")
        if r: st.session_state.id_animal_atual = r[0]
    if st.session_state.id_animal_atual:
        card(st.session_state.id_animal_atual, "res", 0, show_buttons=False)
        if st.button("🚁 ENVIAR HELICÓPTERO"):
            st.markdown('<div style="font-size:80px;">🚁</div>', unsafe_allow_html=True)
            time.sleep(3)
            st.session_state.internados_vet.append({'animal': st.session_state.id_animal_atual, 'data_alta': (datetime.now() + timedelta(hours=24)).timestamp()})
            st.session_state.id_animal_atual = None
            st.rerun()

elif aba == "🏥 Veterinário":
    st.header("🏥 Hospital")
    if not st.session_state.internados_vet:
        st.info("Sem animais feridos.")
    for i, item in enumerate(st.session_state.internados_vet):
        falta = item['data_alta'] - datetime.now().timestamp()
        txt = f"⏳ {int(falta//3600)}h" if falta>0 else "✅ ALTA"
        card(item['animal'], "vet", i, show_buttons=False, footer_text=txt)
        if falta<=0 and st.button("🏁 Zoo", key=f"mv_{i}"):
            st.session_state.zoo.append(item['animal'])
            st.session_state.internados_vet.pop(i)
            st.rerun()

elif aba == "🧬 Tanque de Fusão":
    if len(st.session_state.tanque_fusao)<2:
        st.info("Colete DNA!")
    else:
        n1 = st.selectbox("Mãe:", [a.get('name') for a in st.session_state.tanque_fusao], key="f1")
        n2 = st.selectbox("Pai:", [a.get('name') for a in st.session_state.tanque_fusao], key="f2")
        if st.button("🔬 FUNDIR"):
            st.success(f"Nova Espécie: **{n1.split()[0]} {n2.split()[-1]}**")

elif aba == "🐾 Meu Zoo":
    grid(st.session_state.zoo, "zoo")

elif aba == "⚙️ Definições":
    st.session_state.c_mega = st.text_input("Código Mega", type="password", value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input("Código 24h", type="password", value=st.session_state.c_24h)
    if st.button("Guardar"):
        st.rerun()
