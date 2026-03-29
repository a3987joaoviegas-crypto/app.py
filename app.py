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

# 3. CSS FIXO (BORDA ARCO-ÍRIS SEM AFETAR A IMAGEM)
borda_style = "border: 4px solid #2ecc71;"
if is_mega:
    borda_style = "border: 5px solid; border-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet) 1;"
elif is_24h_valido:
    borda_style = "border: 5px solid #ffd700;"

st.markdown(f"""
<style>
    .stApp {{ background-color: {st.session_state.cor_tema}; filter: brightness({st.session_state.brilho/100}); }}
    .cartao-cidadao {{
        background-color: #1a1c23 !important; 
        border-radius: 20px; 
        padding: 15px; 
        {borda_style}
        margin-bottom: 20px; 
        text-align: center; 
        color: white;
    }}
    .img-an {{ width: 100%; border-radius: 15px; height: 180px; object-fit: cover; border: 1px solid #444; }}
</style>
""", unsafe_allow_html=True)

# 4. FUNÇÃO DO CARTÃO
def card(an, prefixo, idx=0, show_buttons=True, footer_text=None, is_zoo=False):
    if not an: return
    nome_pt = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    classe = {"Mammalia": "Mamífero", "Aves": "Ave", "Reptilia": "Réptil"}.get(an.get('iconic_taxon_name'), "Selvagem")
    
    st.markdown(f'''
    <div class="cartao-cidadao">
        <p style="color:#ffd700; font-weight:bold; font-size:0.7em; margin:0;">💳 CARTÃO DE CIDADÃO</p>
        <img src="{foto}" class="img-an">
        <h3 style="color:#ffd700; margin:10px 0;">{nome_pt}</h3>
        <p style="margin:2px 0;">🐾 {classe} | 🥩 Omnívoro</p>
        {f'<p style="color:#ffd700; font-weight:bold;">{footer_text}</p>' if footer_text else ''}
    </div>
    ''', unsafe_allow_html=True)
    
    if show_buttons:
        c1, c2 = st.columns(2)
        with c1:
            if is_zoo:
                if st.button("🗑️ Excluir", key=f"del_{prefixo}_{idx}"):
                    st.session_state.zoo.pop(idx); st.rerun()
            else:
                if st.button("📥 Zoo", key=f"in_{prefixo}_{idx}"):
                    st.session_state.zoo.append(an); st.toast("No Zoo!")
        with c2:
            if st.button("🧬 DNA", key=f"dna_{prefixo}_{idx}"):
                st.session_state.tanque_fusao.append(an); st.toast("DNA coletado!")

# 5. SIDEBAR
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

# 6. LISTAS E ABAS
florestas = ["Amazónia", "Congo", "Taiga", "Daintree", "Floresta Negra", "Mata Atlântica", "Bornéu", "Monteverde", "Tongass", "Bialowieza"]
oceanos = ["Oceano Pacífico", "Oceano Atlântico", "Oceano Índico", "Oceano Ártico", "Oceano Antártico", "Mar Mediterrâneo", "Mar Vermelho", "Mar das Caraíbas", "Mar de Coral", "Mar Morto"]
paises = ["Portugal", "Brasil", "Angola", "Moçambique", "Espanha", "França", "Itália", "Alemanha", "EUA", "Japão", "China", "Índia", "Austrália", "Canadá", "México", "Argentina", "Chile", "Egito", "África do Sul", "Rússia", "Reino Unido", "Coreia do Sul", "Tailândia", "Grécia", "Turquia", "Noruega", "Suécia", "Holanda", "Suíça", "Israel", "Arábia Saudita", "Vietname", "Indonésia", "Filipinas", "Colômbia", "Peru", "Polónia", "Ucrânia", "Bélgica", "Áustria", "Irlanda", "Islândia", "Cuba", "Uruguai", "Marrocos", "Nigéria", "Quénia", "Nova Zelândia", "Dinamarca", "Finlândia", "Singapura", "Malásia", "Equador", "Venezuela", "Paraguai", "Bolívia", "Panamá", "Costa Rica", "Honduras", "Guatemala", "Jamaica", "Senegal", "Gana", "Irão", "Iraque", "EAU", "Cabo Verde", "Paquistão", "Bangladesh", "Mali"]

if aba == "🌲 Florestas":
    sel = st.selectbox("Escolha uma Floresta:", florestas)
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=12&locale=pt-PT")
    for i, an in enumerate(r.json().get('results', [])): card(an, "floresta", i)

elif aba == "🌊 Oceanos":
    sel = st.selectbox("Escolha um Oceano:", oceanos)
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=12&locale=pt-PT")
    for i, an in enumerate(r.json().get('results', [])): card(an, "ocean", i)

elif aba == "🏳️ Países":
    sel = st.selectbox("Escolha um País:", sorted(paises))
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=12&locale=pt-PT")
    for i, an in enumerate(r.json().get('results', [])): card(an, "pais", i)

elif aba == "🧬 Tanque de Fusão":
    if len(st.session_state.tanque_fusao) < 2: st.info("Use o botão DNA!")
    else:
        n1 = st.selectbox("Animal 1:", [a.get('name') for a in st.session_state.tanque_fusao], key="f1")
        n2 = st.selectbox("Animal 2:", [a.get('name') for a in st.session_state.tanque_fusao], key="f2")
        if st.button("🔬 FUNDIR"):
            st.success(f"Nova Espécie: {n1.split()[0]} {n2.split()[-1]}")

elif aba == "🐾 Meu Zoo":
    for i, an in enumerate(st.session_state.zoo): card(an, "zoo", i, is_zoo=True)

elif aba == "⚙️ Definições":
    st.session_state.c_mega = st.text_input("Código Mega", type="password", value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input("Código 24h", type="password", value=st.session_state.c_24h)
    if st.button("Guardar"): st.rerun()
