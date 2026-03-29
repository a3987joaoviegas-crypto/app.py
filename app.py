import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. ESTADO DO SISTEMA
chaves = {
    'zoo': [], 'tanque_fusao': [], 'pontos_zoologo': 0, 
    'animais_salvos_ids': set(), 'id_animal_atual': None,
    'internados_vet': [], 'c_24h': "", 'c_mega': "", 
    'premium_ativo': False, 'cor_tema': "#0b1117", 'brilho': 100,
    'inicio_sessao_24h': None
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# 2. LÓGICA DE CÓDIGOS E TEMPO
is_mega = st.session_state.c_mega == "67lucas62"
is_24h_valido = False
if st.session_state.c_24h == "6626":
    if st.session_state.inicio_sessao_24h is None:
        st.session_state.inicio_sessao_24h = datetime.now().timestamp()
    tempo_passado = datetime.now().timestamp() - st.session_state.inicio_sessao_24h
    if tempo_passado < 86400: is_24h_valido = True
    else: st.session_state.c_24h = ""

tem_acesso_vip = is_mega or is_24h_valido

# 3. CSS (BORDAS DINÂMICAS QUE NÃO AFETAM A FOTO E GRELHA)
borda_style = "border: 4px solid #2ecc71;"
if is_mega:
    # Borda arco-íris real usando border-image para não afetar o conteúdo interno
    borda_style = "border: 5px solid; border-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet) 1; animation: rb_anim 3s linear infinite;"
elif is_24h_valido:
    borda_style = "border: 5px solid #ffd700;"

st.markdown(f"""
<style>
    @keyframes rb_anim {{ 0% {{ filter: hue-rotate(0deg); }} 100% {{ filter: hue-rotate(360deg); }} }}
    .stApp {{ background-color: {st.session_state.cor_tema}; filter: brightness({st.session_state.brilho/100}); }}
    .cartao-cidadao {{
        background-color: #1a1c23 !important; 
        border-radius: 20px; 
        padding: 12px; 
        {borda_style} 
        margin-bottom: 15px; 
        text-align: center; 
        color: white;
    }}
    .img-an {{ 
        width: 100%; 
        border-radius: 15px; 
        height: 130px; 
        object-fit: cover; 
        border: 1px solid #444; 
        filter: none !important; 
    }}
</style>
""", unsafe_allow_html=True)

# 4. FUNÇÃO DO CARTÃO (3 COLUNAS E LINHAS SEPARADAS)
def card(an, prefixo, idx=0, show_buttons=True, footer_text=None, is_zoo=False):
    if not an: return
    nome_pt = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    classe = {"Mammalia": "Mamífero", "Aves": "Ave", "Reptilia": "Réptil", "Amphibia": "Anfíbio", "Actinopterygii": "Peixe"}.get(an.get('iconic_taxon_name'), "Selvagem")
    alim = random.choice(['Herbívoro', 'Carnívoro', 'Omnívoro'])
    repro = "Vivíparo" if classe == "Mamífero" else "Ovíparo"
    
    st.markdown(f'''
    <div class="cartao-cidadao">
        <span style="color:#ffd700; font-weight:bold; font-size:0.6em;">💳 CARTÃO DE CIDADÃO</span><br>
        <img src="{foto}" class="img-an">
        <h4 style="color:#ffd700; margin:8px 0; font-size:1em;">{nome_pt}</h4>
        <p style="margin:2px 0; font-size:0.8em; text-align:left; padding-left:5px;">🐾 <b>Classe:</b> {classe}</p>
        <p style="margin:2px 0; font-size:0.8em; text-align:left; padding-left:5px;">🥚 <b>Repro:</b> {repro}</p>
        <p style="margin:2px 0; font-size:0.8em; text-align:left; padding-left:5px;">🥩 <b>Alim:</b> {alim}</p>
        {f'<p style="color:#ffd700; font-weight:bold; margin-top:5px; font-size:0.8em;">{footer_text}</p>' if footer_text else ''}
    </div>
    ''', unsafe_allow_html=True)
    
    if show_buttons:
        c1, c2 = st.columns(2)
        with c1:
            if is_zoo:
                if st.button("🗑️", key=f"del_{prefixo}_{idx}", use_container_width=True):
                    st.session_state.zoo.pop(idx); st.rerun()
            else:
                if st.button("📥", key=f"in_{prefixo}_{idx}", use_container_width=True):
                    st.session_state.zoo.append(an); st.toast(f"{nome_pt} no Zoo!")
        with c2:
            if st.button("🧬", key=f"dna_{prefixo}_{idx}", use_container_width=True):
                st.session_state.tanque_fusao.append(an); st.toast("DNA Coletado!")

# 5. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    if is_24h_valido:
        restante = 86400 - (datetime.now().timestamp() - st.session_state.inicio_sessao_24h)
        st.write(f"⏳ Premium: {int(restante//3600)}h {int((restante%3600)//60)}m")
    
    if tem_acesso_vip:
        st.session_state.premium_ativo = st.toggle("✨ MODO PREMIUM", value=st.session_state.premium_ativo)
    
    menu = ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países", "🔬 Lab", "🐾 Meu Zoo", "⚙️ Defs"]
    if st.session_state.premium_ativo:
        menu = ["🌀 Salvamento", "🏥 Vet", "🧬 Fusão", "🔬 Lab", "🐾 Meu Zoo", "⚙️ Defs"]
    aba = st.radio("Navegação", menu)

# 6. GRELHA DE 3 COLUNAS
def grid(lista, prefixo):
    for i in range(0, len(lista), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(lista):
                with cols[j]: card(lista[i+j], prefixo, i+j)

# 7. LOGICA DAS ABAS
paises = sorted(["Portugal", "Brasil", "Angola", "Moçambique", "EUA", "Japão", "França", "Itália", "Alemanha", "Espanha", "China", "Canadá", "México", "Argentina", "Chile", "Egito", "Rússia", "Reino Unido", "Índia", "Austrália", "Cabo Verde", "Suíça", "Suécia", "Noruega", "Holanda", "Bélgica", "Áustria", "Grécia", "Turquia", "Tailândia", "Coreia", "Vietname", "Indonésia", "Polónia", "Ucrânia", "Irlanda", "Islândia", "Cuba", "Uruguai", "Peru", "Colômbia", "Venezuela", "Equador", "Bolívia", "Panamá", "Costa Rica", "Jamaica", "Senegal", "Nigéria", "Quénia", "África do Sul", "Israel", "EAU", "Nova Zelândia", "Dinamarca", "Finlândia"])

if aba == "🌲 Florestas":
    sel = st.selectbox("Floresta:", ["Amazónia", "Congo", "Taiga", "Bornéu", "Floresta Negra"])
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=15&locale=pt-PT")
    grid(r.json().get('results', []), "flo")

elif aba == "🌊 Oceanos":
    sel = st.selectbox("Oceano:", ["Pacífico", "Atlântico", "Índico", "Ártico", "Antártico"])
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=15&locale=pt-PT")
    grid(r.json().get('results', []), "oce")

elif aba == "🏳️ Países":
    sel = st.selectbox("País:", paises)
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=15&locale=pt-PT")
    grid(r.json().get('results', []), "pai")

elif aba == "🧬 Fusão":
    st.header("🧬 Fusão Genética")
    if len(st.session_state.tanque_fusao) < 2: st.info("Colete DNA primeiro!")
    else:
        n1 = st.selectbox("Mãe:", [a.get('name') for a in st.session_state.tanque_fusao], key="f1")
        n2 = st.selectbox("Pai:", [a.get('name') for a in st.session_state.tanque_fusao], key="f2")
        if st.button("🔬 FUNDIR"):
            st.success(f"Espécie Híbrida Criada: **{n1.split()[0]} {n2.split()[-1]}**")

elif aba == "🐾 Meu Zoo":
    grid(st.session_state.zoo, "zoo")

elif aba == "⚙️ Defs":
    st.session_state.c_mega = st.text_input("Código Mega", type="password", value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input("Código 24h", type="password", value=st.session_state.c_24h)
    if st.button("Guardar"): st.rerun()
