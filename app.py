import streamlit as st
import pandas as pd
import requests
import random

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo 🌍", page_icon="🌍", layout="wide")

# 2. ESTADOS
for key, val in {
    'luz': False, 'zoo': [], 'codigo': "", 'codigo_perm': "", 
    'search_query': "", 'cor_card': "Preto", 'cor_fundo': "Preto", 
    'chat_pos': "sidebar"
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Lógica de Permissões
is_perm_active = st.session_state.codigo_perm == "67lucas62"
is_mestre = st.session_state.codigo == "6626" or is_perm_active
is_ai_unlocked = st.session_state.codigo == "33236" or is_perm_active
LIMITE = 80 if is_mestre else 20

# 3. CSS (Estilo Cartão Biológico)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f", "Amarelo": "#f1c40f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23") if not st.session_state.luz else "#ffffff"
bg_app = cores_hex.get(st.session_state.cor_fundo, "#0b1117") if not st.session_state.luz else "#f0f2f6"
txt_color = "#000" if (st.session_state.luz or st.session_state.cor_card == "Branco") else "#fff"

border_style = "border-left: 15px solid; border-right: 5px solid;"
if is_perm_active:
    border_style += "border-image: linear-gradient(45deg, #ff00ff, #00ffff) 1; animation: galactic 3s linear infinite;"
else:
    b_color = "#ffd700" if is_mestre else "#2ea043"
    border_style += f"border-color: {b_color};"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_app}; color: {txt_color}; }}
    .cc-card {{ 
        background: {c_bg} !important; border-radius: 15px; padding: 18px; 
        {border_style}
        box-shadow: 10px 10px 25px rgba(0,0,0,0.5); margin-bottom: 20px;
        color: {txt_color} !important;
    }}
    .nome-pt {{ font-size: 1.6em; font-weight: bold; margin: 0; }}
    .nome-sci {{ font-size: 1.0em; font-style: italic; opacity: 0.7; margin-bottom: 10px; border-bottom: 1px solid rgba(128,128,128,0.3); padding-bottom: 5px; }}
    .bio-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.85em; margin-top: 10px; }}
    .bio-item {{ background: rgba(128,128,128,0.1); padding: 5px 8px; border-radius: 5px; }}
    .status-ext {{ grid-column: span 2; background: rgba(255,0,0,0.2); border: 1px solid red; text-align: center; font-weight: bold; padding: 5px; border-radius: 5px; margin-top: 5px; }}
    .label {{ font-weight: bold; font-size: 0.75em; text-transform: uppercase; opacity: 0.8; display: block; }}
    @keyframes galactic {{ 0% {{ filter: hue-rotate(0deg); }} 100% {{ filter: hue-rotate(360deg); }} }}
    </style>
    """, unsafe_allow_html=True)

# 4. LÓGICA BIOLÓGICA
def obter_bio(an):
    n, s = an['nome'].lower(), an['sci'].lower()
    # Alimentação
    if any(x in n or x in s for x in ['leão', 'tubarão', 'lobo', 'águia', 'tigre', 'orca', 'felis', 'ursus']): alim = "Carnívoro 🥩"
    elif any(x in n or x in s for x in ['elefante', 'vaca', 'girafa', 'veado', 'coelho']): alim = "Herbívoro 🌿"
    else: alim = "Omnívoro 🍎"
    # Ambiente
    if any(x in n or x in s for x in ['mar', 'peixe', 'baleia', 'golfinho', 'ocean']): amb = "Aquático 🌊"
    elif any(x in n or x in s for x in ['águia', 'pássaro', 'corvo', 'ave']): amb = "Aéreo 🦅"
    else: amb = "Terrestre 🌍"
    # Reprodução
    repr = "Ovíparo (Ovos) 🥚" if any(x in n or x in s for x in ['ave', 'peixe', 'réptil', 'pássaro']) else "Vivíparo (Gestação) 🍼"
    # Conservação (Simulação para o código 6626)
    status_list = ["Pouco Preocupante ✅", "Vulnerável ⚠️", "Em Perigo 🚨", "Criticamente em Perigo 💀"]
    cons = random.choice(status_list) if is_mestre else None
    
    return alim, amb, repr, cons

# 5. BUSCA E RENDERIZAÇÃO
def buscar(q):
    if not q: return []
    url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page=12&locale=pt-PT"
    try:
        res = requests.get(url).json()
        return [{'nome': i.get('preferred_common_name', i['name']).title(), 'sci': i['name'], 'foto': i['default_photo']['medium_url'] if i.get('default_photo') else "", 'rank': i.get('rank', 'Espécie')} for i in res['results']]
    except: return []

def render_cartao(an, key):
    alim, amb, repr, cons = obter_bio(an)
    st.markdown(f"""
    <div class='cc-card'>
        <img src='{an['foto']}' width='100%' style='border-radius:10px; height:180px; object-fit:cover; margin-bottom:10px;'>
        <div class='nome-pt'>{an['nome']}</div>
        <div class='nome-sci'>{an['sci']}</div>
        <div class='bio-grid'>
            <div class='bio-item'><span class='label'>Alimentação</span>{alim}</div>
            <div class='bio-item'><span class='label'>Ambiente</span>{amb}</div>
            <div class='bio-item'><span class='label'>Reprodução</span>{repr}</div>
            <div class='bio-item'><span class='label'>Classe</span>{an['rank'].title()}</div>
            {f"<div class='status-ext'><span class='label'>Estado de Conservação</span>{cons}</div>" if cons else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button(f"Guardar {an['nome']}", key=key):
        if len(st.session_state.zoo) < LIMITE: st.session_state.zoo.append(an)

# 6. INTERFACE PRINCIPAL
with st.sidebar:
    st.markdown("# 🌍 MundoVivo")
    if is_ai_unlocked:
        st.subheader("🤖 Assistente")
        if st.button("⬅️ Mover Chat"): st.session_state.chat_pos = "left" if st.session_state.chat_pos == "sidebar" else "sidebar"
        if st.session_state.chat_pos == "sidebar": st.text_input("Dúvida:", key="ia_side")
    aba = st.radio("Menu", ["🌍 Mundo", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"])

if aba == "🌍 Mundo":
    st.title("🌍 Planisfério")
    q = st.text_input("Procurar espécie:", value=st.session_state.search_query)
    res = buscar(q if q else "Animais")
    cols = st.columns(3)
    for i, an in enumerate(res):
        with cols[i%3]: render_cartao(an, f"w_{i}")

elif aba == "🌲 Florestas":
    st.title("🌲 Florestas")
    cols = st.columns(3)
    for i, an in enumerate(buscar("Animais da floresta")):
        with cols[i%3]: render_cartao(an, f"f_{i}")

elif aba == "🌊 Oceanos":
    st.title("🌊 Oceanos")
    cols = st.columns(3)
    for i, an in enumerate(buscar("Animais marinhos")):
        with cols[i%3]: render_cartao(an, f"o_{i}")

elif aba == "⚙️ Definições":
    st.title("⚙️ Definições")
    st.session_state.codigo = st.text_input("Código (33236 / 6626):", type="password")
    st.session_state.codigo_perm = st.text_input("Código Permanente:", type="password")
    if st.button("Inserir"): 
        st.balloons()
        if st.session_state.codigo == "6626": st.success("Modo Mestre Ativado: Conservação Desbloqueada! 🚨")
    st.session_state.luz = st.toggle("Modo Dia")
    st.session_state.cor_card = st.selectbox("Cor do Cartão", list(cores_hex.keys()))
