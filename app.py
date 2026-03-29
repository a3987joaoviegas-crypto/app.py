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

# 2. LÓGICA DE CÓDIGOS
is_mega = st.session_state.c_mega == "67lucas62"
is_24h_valido = False
if st.session_state.c_24h == "6626":
    if st.session_state.inicio_sessao_24h is None:
        st.session_state.inicio_sessao_24h = datetime.now().timestamp()
    if (datetime.now().timestamp() - st.session_state.inicio_sessao_24h) < 86400:
        is_24h_valido = True

# 3. CSS (BORDAS DINÂMICAS - IMAGEM PROTEGIDA)
borda_style = "border: 4px solid #2ecc71;"
if is_mega:
    borda_style = "border: 5px solid; border-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet) 1; animation: rainbow_anim 3s linear infinite;"
elif is_24h_valido:
    borda_style = "border: 5px solid #ffd700;"

st.markdown(f"""
<style>
    @keyframes rainbow_anim {{ 0% {{ filter: hue-rotate(0deg); }} 100% {{ filter: hue-rotate(360deg); }} }}
    .stApp {{ background-color: {st.session_state.cor_tema}; filter: brightness({st.session_state.brilho/100}); }}
    .cartao-cidadao {{
        background-color: #1a1c23 !important; border-radius: 20px; padding: 12px; 
        {borda_style} margin-bottom: 15px; text-align: center; color: white;
    }}
    .img-an {{ width: 100%; border-radius: 15px; height: 140px; object-fit: cover; border: 1px solid #444; filter: none !important; }}
    @keyframes helicopter_ride {{ 0% {{ transform: translateX(-200px); }} 100% {{ transform: translateX(110vw); }} }}
    .heli-anim {{ position: fixed; top: 30%; font-size: 80px; z-index: 9999; animation: helicopter_ride 3s linear forwards; }}
</style>
""", unsafe_allow_html=True)

# 4. FUNÇÃO DO CARTÃO (3 COLUNAS)
def card(an, prefixo, idx=0, show_buttons=True, footer_text=None, is_zoo=False):
    if not an: return
    nome_pt = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    classe = {"Mammalia": "Mamífero", "Aves": "Ave", "Reptilia": "Réptil", "Amphibia": "Anfíbio", "Actinopterygii": "Peixe"}.get(an.get('iconic_taxon_name'), "Selvagem")
    
    st.markdown(f'''<div class="cartao-cidadao">
        <p style="color:#ffd700; font-weight:bold; font-size:0.6em; margin:0;">💳 CARTÃO DE CIDADÃO</p>
        <img src="{foto}" class="img-an">
        <h4 style="color:#ffd700; margin:8px 0; font-size:1em;">{nome_pt}</h4>
        <p style="margin:2px 0; font-size:0.8em;">🐾 {classe} | 🥩 Omnívoro</p>
        {f'<p style="color:#ffd700; font-size:0.8em; font-weight:bold;">{footer_text}</p>' if footer_text else ''}
    </div>''', unsafe_allow_html=True)
    
    if show_buttons:
        c1, c2 = st.columns(2)
        with c1:
            if is_zoo:
                if st.button("🗑️", key=f"del_{prefixo}_{idx}", help="Excluir"):
                    st.session_state.zoo.pop(idx); st.rerun()
            else:
                if st.button("📥", key=f"in_{prefixo}_{idx}", help="Zoo"):
                    st.session_state.zoo.append(an); st.toast(f"{nome_pt} no Zoo!")
        with c2:
            if st.button("🧬", key=f"dna_{prefixo}_{idx}", help="DNA"):
                st.session_state.tanque_fusao.append(an); st.toast("DNA coletado!")

# 5. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    if is_24h_valido:
        res = 86400 - (datetime.now().timestamp() - st.session_state.inicio_sessao_24h)
        st.caption(f"⏳ Premium: {int(res//3600)}h {int((res%3600)//60)}m")
    
    if is_mega or is_24h_valido:
        st.session_state.premium_ativo = st.toggle("✨ MODO PREMIUM", value=st.session_state.premium_ativo)
    
    menu = ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    if st.session_state.premium_ativo:
        menu = ["🌀 Salvamento", "🏥 Veterinário", "🧬 Tanque de Fusão", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    aba = st.radio("Navegação", menu)

# 6. LISTAS
florestas = ["Amazónia", "Congo", "Taiga", "Daintree", "Floresta Negra", "Mata Atlântica", "Bornéu", "Monteverde", "Tongass", "Bialowieza"]
oceanos = ["Oceano Pacífico", "Oceano Atlântico", "Oceano Índico", "Oceano Ártico", "Oceano Antártico", "Mar Mediterrâneo", "Mar Vermelho", "Mar das Caraíbas", "Mar de Coral", "Mar Morto"]
paises = sorted(["Portugal", "Brasil", "Angola", "Moçambique", "EUA", "Japão", "França", "Itália", "Alemanha", "China", "Espanha", "Canadá", "México", "Argentina", "Chile", "Egito", "Rússia", "Reino Unido", "Austrália", "Índia"]) # + restante dos 70

# 7. LOGICA DE EXIBIÇÃO EM GRELHA (3 COLUNAS)
def render_grid(results, prefix):
    for i in range(0, len(results), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(results):
                with cols[j]: card(results[i+j], prefix, i+j)

# 8. ABAS
if aba == "🌲 Florestas":
    sel = st.selectbox("Escolha uma Floresta:", florestas)
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=21&locale=pt-PT")
    render_grid(r.json().get('results', []), "floresta")

elif aba == "🌊 Oceanos":
    sel = st.selectbox("Escolha um Oceano:", oceanos)
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=21&locale=pt-PT")
    render_grid(r.json().get('results', []), "ocean")

elif aba == "🏳️ Países":
    sel = st.selectbox("Escolha um País:", paises)
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=21&locale=pt-PT")
    render_grid(r.json().get('results', []), "pais")

elif aba == "🧬 Tanque de Fusão":
    st.header("🧬 Tanque de Fusão")
    if len(st.session_state.tanque_fusao) < 2: st.info("Colete DNA!")
    else:
        n1 = st.selectbox("Mãe:", [a.get('name') for a in st.session_state.tanque_fusao], key="f1")
        n2 = st.selectbox("Pai:", [a.get('name') for a in st.session_state.tanque_fusao], key="f2")
        if st.button("🔬 FUNDIR"):
            st.success(f"Espécie Criada: {n1.split()[0]} {n2.split()[-1]}")

elif aba == "🐾 Meu Zoo":
    render_grid(st.session_state.zoo, "zoo")

elif aba == "⚙️ Definições":
    st.session_state.c_mega = st.text_input("Código Mega", type="password", value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input("Código 24h", type="password", value=st.session_state.c_24h)
    if st.button("Guardar"): st.rerun()
