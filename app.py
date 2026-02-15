import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# 2. ESTILO ORIGINAL (LIMPO E DIRETO)
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    .stApp { background-color: #0b1117; color: #adbac7; }

    /* CARTÃO DE CIDADÃO (PADRÃO 220px) */
    .cc-card { 
        background: #1c2128; border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
    }
    .img-cc { width: 100%; height: 220px; object-fit: cover; border-radius: 8px; }
    .common-name { color: #2ea043; font-size: 22px; font-weight: bold; margin-top: 10px; text-align: center; }
    .sci-name { color: white; font-style: italic; font-size: 14px; text-align: center; margin-bottom: 15px; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
    
    .label-expert { color: #2ea043; font-weight: bold; font-size: 11px; margin-top: 5px; text-transform: uppercase;}
    .val-expert { color: white; font-size: 14px; margin-bottom: 6px; }
    </style>
    """, unsafe_allow_html=True)

# 3. LÓGICA BIOLÓGICA (CARACTERÍSTICAS)
def definir_biologia(nome, classe):
    n = str(nome).lower()
    dieta = "Omnívoro"
    if any(x in n for x in ['leão', 'tubarão', 'lobo', 'águia', 'orca', 'tigre', 'serpente', 'falcão']):
        dieta = "Carnívoro (Predador)"
    elif any(x in n for x in ['elefante', 'zebra', 'girafa', 'vaca', 'coelho', 'canguru', 'panda']):
        dieta = "Herbívoro (Plantas)"
    
    repro = "Vivíparo" if classe == 'Mammalia' else "Ovíparo"
    ambiente = "Marinho / Aquático" if classe in ['Actinopterygii', 'Mollusca'] or "baleia" in n else "Terrestre / Florestal"
    return dieta, repro, ambiente

def buscar_fauna(query, limite=12):
    url = f"https://api.inaturalist.org/v1/taxa?q={query}&taxon_id=1&locale=pt-BR"
    try:
        res = requests.get(url).json()
        out = []
        for t in res.get('results', [])[:limite]:
            if t.get('default_photo'):
                nome = (t.get('preferred_common_name') or t.get('name')).title()
                classe = t.get('iconic_taxon_name', 'Animal')
                d, r, amb = definir_biologia(nome, classe)
                out.append({'nome': nome, 'sci': t.get('name'), 'foto': t['default_photo']['medium_url'], 'dieta': d, 'repro': r, 'ambiente': amb})
        return out
    except: return []

# SESSÕES
if 'zoo' not in st.session_state: st.session_state.zoo = []
if 'diario' not in st.session_state: st.session_state.diario = ""

# MENU LATERAL
menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "📝 Diário", "⭐ Favoritos"])

def exibir_cartao(a, key):
    if not a: return
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
    if st.button("⭐ Guardar no Zoo", key=key):
        st.session_state.zoo.append(a)
        st.toast(f"{a['nome']} guardado!")

# --- PÁGINAS ---

if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério Bio-Interativo")
    st.map(pd.DataFrame({'lat': [39.3, -14.2, -11.2, 37.0], 'lon': [-8.2, -51.9, 17.8, -95.7]}))
    sel = st.selectbox("Ver fauna local:", ["Brasil", "Portugal", "Angola", "EUA"])
    animais = buscar_fauna(sel, 3)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i]: exibir_cartao(an, f"map_{i}")

elif menu == "🌲 Florestas":
    st.title("🌲 Fauna das Florestas")
    animais = buscar_fauna("Jaguar", 6)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: exibir_cartao(an, f"flo_{i}")

elif menu == "🌊 Oceanos":
    st.title("🌊 Fauna dos Oceanos")
    animais = buscar_fauna("Tubarão", 6)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: exibir_cartao(an, f"oce_{i}")

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório de Pesquisa")
    txt = st.text_input("🔍 Digite o nome de um animal ou grupo (ex: Felinos, Aves...):")
    if txt:
        lista = buscar_fauna(txt, 15)
        cols = st.columns(3)
        for i, anim in enumerate(lista):
            with cols[i%3]: exibir_cartao(anim, f"lab_{i}")

elif menu == "📝 Diário":
    st.title("📝 Diário de Bordo")
    st.session_state.diario = st.text_area("Notas sobre as tuas pesquisas:", value=st.session_state.diario, height=400)

elif menu == "⭐ Favoritos":
    st.title("🐾 O Meu Zoo")
    if not st.session_state.zoo:
        st.info("Ainda não guardaste animais nos favoritos.")
    else:
        cols = st.columns(3)
        for i, z in enumerate(st.session_state.zoo):
            with cols[i%3]: exibir_cartao(z, f"zoo_{i}")
