import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo 70", page_icon="🌍", layout="wide")

# 2. DEFINIÇÕES NA SIDEBAR
st.sidebar.title("⚙️ Definições")

# Luminosidade e Negrito (Estilo "Ovo" / Toggle)
luz = st.sidebar.toggle("Luminosidade (Modo Claro)")
negrito = st.sidebar.toggle("Texto em Negrito")

# Cor de Fundo
cor_fundo = st.sidebar.selectbox("Cor de Fundo:", ["Preto", "Branco", "Azul", "Verde"])
cores = {"Preto": "#0b1117", "Branco": "#ffffff", "Azul": "#001f3f", "Verde": "#002b1b"}
cor_card = "#f2f2f2" if cor_fundo == "Branco" else "#1c2128"
cor_texto = "#000000" if cor_fundo == "Branco" else "#adbac7"

# Idiomas (Sidebar dentro da Sidebar)
with st.sidebar.expander("🌐 Idioma"):
    lingua = st.selectbox("Escolha a língua:", 
                         ["Português (Original)", "Inglês", "Espanhol", "Russo", "Finlandês", "Crioulo"])

# 3. ESTILO CSS DINÂMICO
st.markdown(f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stApp {{ background-color: {cores[cor_fundo]}; color: {cor_texto}; }}
    
    /* Aplicação do Negrito Global */
    * {{ 
        font-weight: {"bold" if negrito else "normal"} !important; 
    }}

    .cc-card {{ 
        background: {cor_card}; 
        border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
        color: {cor_texto};
        min-height: 480px;
    }}
    .img-cc {{ width: 100%; height: 220px; object-fit: cover; border-radius: 8px; }}
    .common-name {{ color: #2ea043; font-size: 20px; font-weight: bold; margin-top: 10px; text-align: center; }}
    .sci-name {{ color: {cor_texto}; font-style: italic; font-size: 13px; text-align: center; margin-bottom: 10px; opacity: 0.8; }}
    
    .label-expert {{ color: #2ea043; font-weight: bold; font-size: 10px; text-transform: uppercase; margin-top: 8px;}}
    .val-expert {{ color: {cor_texto}; font-size: 14px; margin-bottom: 4px; }}
    </style>
    """, unsafe_allow_html=True)

# 4. LÓGICA BIOLÓGICA
def definir_biologia(nome, classe):
    n = str(nome).lower()
    dieta = "Omnívoro"
    if any(x in n for x in ['leão', 'tubarão', 'lobo', 'águia', 'orca', 'tigre', 'cobra', 'falcão']):
        dieta = "Carnívoro"
    elif any(x in n for x in ['elefante', 'zebra', 'girafa', 'vaca', 'coelho', 'cervo', 'gazela']):
        dieta = "Herbívoro"
    
    repro = "Vivíparo" if classe == 'Mammalia' else "Ovíparo"
    ambiente = "Marinho / Aquático" if classe in ['Actinopterygii', 'Mollusca'] or "baleia" in n else "Terrestre"
    return dieta, repro, ambiente

def buscar_fauna(query, limite=70): # LIMITE EXPANDIDO PARA 70
    url = f"https://api.inaturalist.org/v1/taxa?q={query}&taxon_id=1&per_page={limite}&locale=pt-BR"
    try:
        res = requests.get(url).json()
        out = []
        for t in res.get('results', []):
            if t.get('default_photo'):
                nome = (t.get('preferred_common_name') or t.get('name')).title()
                classe = t.get('iconic_taxon_name', 'Animal')
                d, r, amb = definir_biologia(nome, classe)
                out.append({'nome': nome, 'sci': t.get('name'), 'foto': t['default_photo']['medium_url'], 'dieta': d, 'repro': r, 'ambiente': amb})
        return out
    except: return []

# SESSÕES
if 'zoo' not in st.session_state: st.session_state.zoo = []

# MENU PRINCIPAL
st.sidebar.divider()
menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Favoritos"])

def exibir_cartao(a, key):
    st.markdown(f"""
        <div class='cc-card'>
            <img src='{a['foto']}' class='img-cc'>
            <div class='common-name'>{a['nome']}</div>
            <div class='sci-name'>{a['sci']}</div>
            <div class='label-expert'>AMBIENTE</div><div class='val-expert'>🏡 {a['ambiente']}</div>
            <div class='label-expert'>DIETA</div><div class='val-expert'>🍴 {a['dieta']}</div>
            <div class='label-expert'>REPRODUÇÃO</div><div class='val-expert'>🧬 {a['repro']}</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("⭐ Guardar", key=key): 
        st.session_state.zoo.append(a)
        st.toast(f"{a['nome']} guardado!")

# --- PÁGINAS ---
if menu == "🌍 Planisfério":
    st.title("🌍 Exploração Mundial (Até 70 espécies)")
    st.map(pd.DataFrame({'lat': [38.7, -15.7, -8.8, 37.0], 'lon': [-9.1, -47.8, 13.2, -95.7]}))
    sel = st.selectbox("Escolha um País:", ["Brasil", "Portugal", "Angola", "Moçambique", "EUA", "Austrália"])
    animais = buscar_fauna(sel, 70)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: exibir_cartao(an, f"map_{i}")

elif menu == "🌲 Florestas":
    st.title("🌲 Fauna de Florestas e Selvas")
    animais = buscar_fauna("Mammalia", 70) # Busca ampla por mamíferos de floresta
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: exibir_cartao(an, f"flo_{i}")

elif menu == "🌊 Oceanos":
    st.title("🌊 Fauna Marinha e Oceânica")
    animais = buscar_fauna("Fish", 70)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: exibir_cartao(an, f"oce_{i}")

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório de Identificação Massiva")
    txt = st.text_input("🔍 Pesquisar espécie (Ex: Ursos, Felinos, Aves...):")
    if txt:
        lista = buscar_fauna(txt, 70)
        st.write(f"Encontrados {len(lista)} resultados.")
        cols = st.columns(3)
        for i, anim in enumerate(lista):
            with cols[i%3]: exibir_cartao(anim, f"lab_{i}")

elif menu == "⭐ Favoritos":
    st.title("🐾 O Meu Zoo Pessoal")
    if not st.session_state.zoo:
        st.write("Ainda não guardaste nenhum animal.")
    else:
        cols = st.columns(3)
        for i, z in enumerate(st.session_state.zoo):
            with cols[i%3]: exibir_cartao(z, f"zoo_{i}")
