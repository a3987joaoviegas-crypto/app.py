import streamlit as st
import requests

# 1. ESTADO DO SISTEMA
if 'zoo' not in st.session_state:
    st.session_state.update({
        'zoo': [], 'tanque_fusao': [], 'premium_ativo': False,
        'nome_zoologo': "Explorador", 'codigo_perm': "67lucas62", 'codigo': "6626"
    })

# 2. LÓGICA DE ACESSO
tem_acesso = (st.session_state.codigo == "6626" or st.session_state.codigo_perm == "67lucas62")

# 3. DESIGN CSS
st.markdown(f"""
<style>
    .cartao-cidadao {{
        background-color: #1a1c23;
        padding: 15px;
        border-radius: 15px;
        border: 2px solid #34495e;
        color: white;
        margin-bottom: 10px;
    }}
    .info-box {{
        background: rgba(255,255,255,0.05);
        padding: 10px;
        border-radius: 8px;
        font-size: 0.85em;
        margin-top: 10px;
        text-align: left;
        line-height: 1.4;
    }}
    .selo-premium {{
        background: linear-gradient(45deg, #ffd700, #ffa500);
        color: black;
        padding: 3px 8px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 0.75em;
        display: block;
        margin-top: 8px;
        text-align: center;
    }}
</style>
""", unsafe_allow_html=True)

# 4. FUNÇÃO DE EXIBIÇÃO
def exibir_animal(an):
    nome = an.get('preferred_common_name', an.get('name', 'Espécie')).title()
    foto = an.get('default_photo', {}).get('medium_url', "")
    classe = an.get('iconic_taxon_name', 'Mamífero')
    
    st.markdown(f"""
    <div class="cartao-cidadao">
        <img src="{foto}" width="100%" style="border-radius: 10px; border: 1px solid #444;">
        <h3 style="margin: 10px 0; color: #2ecc71;">{nome}</h3>
        <div class="info-box">
            <b>🧬 Classe:</b> {classe}<br>
            <b>🌍 Habitat:</b> Selvagem / Natural<br>
            <b>🍼 Reprodução:</b> Nativa da Espécie<br>
            <b>🍖 Alimentação:</b> Dieta Natural
    """, unsafe_allow_html=True)

    # APENAS CONSERVAÇÃO É PREMIUM
    if st.session_state.premium_ativo:
        st.markdown(f'<div class="selo-premium">🛡️ STATUS: PROTEGIDO (IUCN)</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
        </div>
        <div style="margin-top:8px; opacity:0.5; font-size:0.7em;">ID: {an['id']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"📥 CAPTURAR {nome}", key=f"cap_{an['id']}"):
        st.session_state.zoo.append(an)
        st.toast(f"{nome} adicionado ao Zoo!")

# 5. INTERFACE PRINCIPAL
st.title("MundoVivo: Enciclopédia 🌍")

if tem_acesso:
    st.session_state.premium_ativo = st.toggle("🔓 Ver Status de Conservação", value=st.session_state.premium_ativo)

busca = st.text_input("Pesquisar espécie:", "Lince")

if busca:
    url = f"https://api.inaturalist.org/v1/taxa?q={busca}&taxon_id=1&per_page=3"
    try:
        dados = requests.get(url).json().get('results', [])
        cols = st.columns(3)
        for i, animal in enumerate(dados):
            with cols[i]:
                exibir_animal(animal)
    except:
        st.error("Erro ao carregar dados da natureza.")

# 6. RODAPÉ (DEFINIÇÕES)
with st.expander("⚙️ Painel do Zoólogo"):
    st.session_state.codigo = st.text_input("Código de Acesso:", value=st.session_state.codigo, type="password")
