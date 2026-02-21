import streamlit as st
import pandas as pd
import requests
import random

# 1. CONFIGURAÇÃO BÁSICA
st.set_page_config(page_title="MundoVivo 🌍", page_icon="🌍", layout="wide")

# 2. SISTEMA DE MEMÓRIA
for key, val in {
    'luz': False, 'zoo': [], 'codigo': "", 'codigo_perm': "", 
    'cor_card': "Preto", 'cor_fundo': "Preto", 'idioma': "pt-PT", 'nome_zoologo': "Explorador", 'lang_label': "Português"
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Lógica de Permissões
is_perm_active = st.session_state.codigo_perm == "67lucas62"
is_mestre = st.session_state.codigo == "6626" or is_perm_active
LIMITE = 80 if is_mestre else 20
titulo_zoologo = "🏆 Zoólogo Profissional" if is_mestre else "💳 Zoólogo"

# 3. DESIGN (CSS)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f", "Amarelo": "#f1c40f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23") if not st.session_state.luz else "#ffffff"
app_bg = cores_hex.get(st.session_state.cor_fundo, "#0b1117") if not st.session_state.luz else "#f0f2f6"
txt_color = "#000" if (st.session_state.luz or st.session_state.cor_card == "Branco") else "#fff"

border_css = "border-left: 15px solid; border-right: 5px solid;"
if is_perm_active:
    border_css += "border-image: linear-gradient(45deg, #ff00ff, #00ffff) 1; animation: galactico 3s linear infinite;"
else:
    b_col = "#ffd700" if is_mestre else "#2ea043"
    border_css += f"border-color: {b_col};"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {app_bg}; color: {txt_color}; }}
    .cc-card {{ background: {c_bg} !important; border-radius: 15px; padding: 18px; {border_css} box-shadow: 8px 8px 20px rgba(0,0,0,0.5); margin-bottom: 20px; color: {txt_color} !important; }}
    .sidebar-card {{ background: #2ea043; padding: 15px; border-radius: 10px; border: 2px solid gold; color: white; }}
    .premium-luta-box {{ background: rgba(255, 215, 0, 0.05); border: 2px dashed gold; padding: 15px; border-radius: 15px; }}
    </style>
    """, unsafe_allow_html=True)

# 4. FUNÇÕES
def buscar_api(termo, qtd=9):
    try:
        lang = st.session_state.idioma
        url = f"https://api.inaturalist.org/v1/taxa?q={termo}&taxon_id=1&per_page={qtd}&locale={lang}"
        r = requests.get(url).json()
        return [{'nome': i.get('preferred_common_name', i['name']).title(), 'sci': i['name'], 'foto': i['default_photo']['medium_url'] if i.get('default_photo') else "", 'id': i['id']} for i in r['results']]
    except: return []

def render_cartao(an, k, tipo="zoo"):
    label_btn = "⚔️ LUTAR" if tipo == "luta" else "➕ Guardar Animal"
    st.markdown(f"<div class='cc-card'><img src='{an['foto']}' width='100%' style='border-radius:10px; height:180px; object-fit:cover;'><div style='font-size:1.3em; font-weight:bold;'>{an['nome']}</div><div style='font-style:italic; opacity:0.7;'>{an['sci']}</div></div>", unsafe_allow_html=True)
    if st.button(label_btn, key=k, use_container_width=True):
        if tipo == "zoo":
            if len(st.session_state.zoo) < LIMITE:
                st.session_state.zoo.append(an); st.toast(f"{an['nome']} guardado!")
        else: st.error(f"COMBATE CONTRA {an['nome']}!")

# 5. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    st.markdown(f"<div class='sidebar-card'><h4>{titulo_zoologo}</h4><b>{st.session_state.nome_zoologo}</b><br><small>Reserva: {len(st.session_state.zoo)}/{LIMITE}</small></div>", unsafe_allow_html=True)
    st.markdown("---")
    aba = st.radio("Menu", ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Coleção", "⚙️ Definições"])

GRUPOS = ["Todos", "Mamíferos", "Aves", "Répteis", "Anfíbios", "Peixes", "Aracnídeos", "Insetos"]

# 6. INTERFACE
if aba == "🔬 Laboratório":
    st.title("🔬 Laboratório Central")
    col_pesquisa, col_luta = st.columns([1.8, 1])
    with col_pesquisa:
        st.subheader("🔍 Análise Livre")
        termo_lab = st.text_input("Introduza nome para estudo:")
        if termo_lab:
            res = buscar_api(termo_lab)
            c1, c2 = st.columns(2)
            for i, a in enumerate(res):
                with (c1 if i % 2 == 0 else c2): render_cartao(a, f"lab_{i}")
    with col_luta:
        st.markdown("<div class='premium-luta-box'>", unsafe_allow_html=True)
        st.subheader("🥊 Lutas Premium")
        if is_mestre:
            op_txt = st.text_input("Oponente (1vs1):", key="search_fight")
            if op_txt:
                inimigo = buscar_api(op_txt, qtd=1)
                if inimigo: render_cartao(inimigo[0], "btn_luta", tipo="luta")
        else: st.error("Acesso bloqueado.")
        st.markdown("</div>", unsafe_allow_html=True)

elif aba == "🌲 Florestas":
    st.title("🌲 Biomas")
    col1, col2 = st.columns(2)
    with col1: tipo = st.selectbox("Escolha a Floresta:", ["Amazónia", "Taiga", "Savana", "Mata Atlântica"])
    with col2: grupo = st.selectbox("Filtrar Grupo:", GRUPOS, key="f_grupo")
    busca = f"Animais da {tipo}" if grupo == "Todos" else f"Animais {grupo} da {tipo}"
    cols = st.columns(3)
    for i, a in enumerate(buscar_api(busca)):
        with cols[i%3]: render_cartao(a, f"f_{i}")

elif aba == "🌊 Oceanos":
    st.title("🌊 Oceanos")
    col1, col2 = st.columns(2)
    with col1: oceano = st.selectbox("Escolha:", ["Oceano Atlântico", "Oceano Pacífico", "Recifes de Coral", "Mar Profundo"])
    with col2: grupo = st.selectbox("Filtrar Grupo:", GRUPOS, key="o_grupo")
    busca = f"Animais do {oceano}" if grupo == "Todos" else f"Animais {grupo} do {oceano}"
    cols = st.columns(3)
    for i, a in enumerate(buscar_api(busca)):
        with cols[i%3]: render_cartao(a, f"o_{i}")

elif aba == "🌍 Países":
    st.title("🌍 Países")
    col1, col2 = st.columns(2)
    with col1: pais = st.selectbox("Selecione:", ["Portugal", "Brasil", "Angola", "Moçambique", "Japão", "Austrália"])
    with col2: grupo = st.selectbox("Filtrar Grupo:", GRUPOS, key="p_grupo")
    busca = f"Animais de {pais}" if grupo == "Todos" else f"Animais {grupo} de {pais}"
    cols = st.columns(3)
    for i, a in enumerate(buscar_api(busca)):
        with cols[i%3]: render_cartao(a, f"p_{i}")

elif aba == "⭐ Coleção":
    st.title("⭐ Minha Reserva")
    for i, a in enumerate(st.session_state.zoo):
        st.markdown(f"<div class='cc-card'><b>{a['nome']}</b></div>", unsafe_allow_html=True)
        if st.button("Libertar", key=f"lib_{i}"): st.session_state.zoo.pop(i); st.rerun()

elif aba == "⚙️ Definições":
    st.title("⚙️ Definições e Idioma")
    st.session_state.nome_zoologo = st.text_input("Nome:", value=st.session_state.nome_zoologo)
    
    # Seletor de Idiomas aqui
    idiomas_dict = {
        "Português": "pt-PT", "English": "en-US", "Français": "fr", 
        "Español": "es", "Deutsch": "de", "Russo (Русский)": "ru", "Finlandês (Suomi)": "fi"
    }
    escolha_lang = st.selectbox("🌐 Idioma das Pesquisas:", list(idiomas_dict.keys()), index=list(idiomas_dict.keys()).index(st.session_state.lang_label))
    st.session_state.idioma = idiomas_dict[escolha_lang]
    st.session_state.lang_label = escolha_lang
    
    st.markdown("---")
    st.session_state.codigo = st.text_input("Código:", type="password")
    st.session_state.codigo_perm = st.text_input("Código Permanente:", type="password")
    st.session_state.cor_card = st.selectbox("Cor Cartão:", list(cores_hex.keys()))
    st.session_state.luz = st.toggle("Modo Dia")
