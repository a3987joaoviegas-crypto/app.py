import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# CSS ORIGINAL (ESTÁVEL E LIMPO)
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    .stApp { background-color: #0b1117; color: #adbac7; }

    /* CARTÃO DE CIDADÃO BIOLÓGICO */
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

# LÓGICA BIOLÓGICA DAS CARACTERÍSTICAS
def definir_biologia(nome, classe):
    n = str(nome).lower()
    dieta = "Omnívoro / Variada"
    if any(x in n for x in ['leão', 'tubarão', 'lobo', 'águia', 'orca', 'tigre', 'jacaré', 'serpente']):
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
                out.append({
                    'nome': nome, 
                    'sci': t.get('name'), 
                    'foto': t['default_photo']['medium_url'], 
                    'dieta': d, 
                    'repro': r, 
                    'ambiente': amb
                })
        return out
    except: return []

# ESTADOS
if 'zoo' not in st.session_state: st.session_state.zoo = []
if 'diario' not in st.session_state: st.session_state.diario = ""

# MENU LATERAL (CHAT REMOVIDO)
menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "📝 Diário", "⭐ Favoritos"])

def exibir_cartao(a, key, is_zoo=False):
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
    if not is_zoo:
        if st.button("⭐ Guardar", key=key):
            st.session_state.zoo.append(a)
    else:
        if st.button("🗑️ Eliminar", key=key):
            st.session_state.zoo.remove(a)
            st.rerun()

# --- PÁGINAS ---

if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério")
    st.map(pd.DataFrame({'lat': [-14.2, 39.3, -11.2, -18.6], 'lon': [-51.9, -8.2, 17.8, 35.5]}))
    sel = st.selectbox("Escolha um País para ver a fauna:", ["Brasil", "Portugal", "Angola", "Moçambique"])
    animais = buscar_fauna(sel, 3)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i]: exibir_cartao(an, f"map_{i}")

elif menu == "🌲 Florestas":
    st.title("🌲 Exploração de Florestas")
    animais = buscar_fauna("Floresta", 9)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: exibir_cartao(an, f"flo_{i}")

elif menu == "🌊 Oceanos":
    st.title("🌊 Exploração de Oceanos")
    animais = buscar_fauna("Oceano", 9)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i%3]: exibir_cartao(an, f"oce_{i}")

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório de Identificação")
    txt = st.text_input("🔍 Pesquisar espécie ou grupo de animais:")
    if txt:
        lista = buscar_fauna(txt, 15)
        cols = st.columns(3)
        for i, anim in enumerate(lista):
            with cols[i%3]: exibir_cartao(anim, f"lab_{i}")

elif menu == "📝 Diário":
    st.title("📝 Diário de Observações")
    st.session_state.diario = st.text_area("Notas e descobertas:", value=st.session_state.diario, height=400)

elif menu == "⭐ Favoritos":
    st.title("🐾 O Meu Zoo")
    if not st.session_state.zoo:
        st.info("O teu Zoo está vazio. Guarda alguns animais no Laboratório!")
    else:
        cols = st.columns(3)
        for i, z in enumerate(st.session_state.zoo):
            with cols[i%3]: exibir_cartao(z, f"zoo_{i}", is_zoo=True)
