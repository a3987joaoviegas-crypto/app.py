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
for k,v in chaves.items():
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
# FUNÇÃO CARTÃO DE CIDADÃO COMPLETO
# ----------------------
def card(an, prefixo, idx=0, show_buttons=True, footer_text=None, is_zoo=False):
    if not an: return
    nome_pt = (an.get('preferred_common_name') or an.get('name','Espécie')).title()
    nome_cient = an.get('name','Desconhecido')
    foto = (an.get('default_photo') or {}).get('medium_url',"https://via.placeholder.com/300")
    classe = {"Mammalia":"Mamífero","Aves":"Ave","Reptilia":"Réptil","Amphibia":"Anfíbio","Actinopterygii":"Peixe"}.get(an.get('iconic_taxon_name'),"Selvagem")
    alim = random.choice(['Herbívoro','Carnívoro','Omnívoro'])
    repro = "Vivíparo" if classe=="Mamífero" else "Ovíparo"
    st.markdown(f'''
    <div class="cartao-cidadao">
        <span style="color:#ffd700; font-weight:bold; font-size:0.6em;">💳 CARTÃO DE CIDADÃO</span><br>
        <img src="{foto}" class="img-an">
        <h4 style="color:#ffd700; margin:5px 0 0 0;">{nome_pt}</h4>
        <p style="margin:2px 0; font-size:0.8em; font-style:italic;">{nome_cient}</p>
        <p style="margin:2px 0; font-size:0.8em;">🐾 <b>Classe:</b> {classe}</p>
        <p style="margin:2px 0; font-size:0.8em;">🥚 <b>Reprodução:</b> {repro}</p>
        <p style="margin:2px 0; font-size:0.8em;">🥩 <b>Alimentação:</b> {alim}</p>
        {f'<p style="color:#ffd700
