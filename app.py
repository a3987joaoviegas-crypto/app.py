import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# ESTILOS E CUTSCENE REFORÇADA
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    .stApp { background-color: #0b1117; color: #adbac7; }
    
    .cc-card { 
        background: #1c2128; border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
    }
    .img-cc { width: 100%; height: 220px; object-fit: cover; border-radius: 8px; }
    .common-name { color: #2ea043; font-size: 22px; font-weight: bold; margin-top: 10px; text-align: center; }
    .sci-name { color: #8b949e; font-style: italic; font-size: 14px; text-align: center; margin-bottom: 15px; }
    
    .label-expert { color: #2ea043; font-weight: bold; font-size: 12px; margin-top: 5px; text-transform: uppercase;}
    .val-expert { color: white; font-size: 15px; margin-bottom: 8px; border-bottom: 1px solid #30363d; padding-bottom: 2px;}

    /* CUTSCENE ANIMADA */
    .cutscene-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 99999; display: flex; flex-direction: column; align-items: center; justify-content: center;
        background: radial-gradient(circle, #062814 0%, #0b1117 100%);
        color: #2ea043; text-align: center;
        animation: fadeOutScene 2.5s forwards; pointer-events: none;
    }
    @keyframes fadeOutScene { 
        0% { opacity: 1; visibility: visible; } 
        80% { opacity: 1; } 
        100% { opacity: 0; visibility: hidden; } 
    }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA DE BIOLOGIA
def dieta_realista(nome, classe):
    n = str(nome).lower()
    carnivoros = ['leão', 'tubarão', 'lobo', 'águia', 'orca', 'tigre', 'jacaré', 'polvo', 'serpente', 'crocodilo']
    if any(x in n for x in carnivoros): return "Carnívoro (Predador)"
    return "Omnívoro / Variada"

def buscar_fauna(lat, lon, local_tipo):
    url = "https://api.inaturalist.org/v1/observations"
    params = {"lat": lat, "lng": lon, "radius": 800, "taxon_id": 1, "per_page": 50, "locale": "pt-BR", "order_by": "votes"}
    try:
        res = requests.get(url, params=params).json()
        lista = []
        vistos = set()
        for obs in res.get('results', []):
            t = obs.get('taxon')
            if not t or not t.get('default_photo'): continue
            nome_pt = (t.get('preferred_common_name') or t.get('name')).title()
            if nome_pt in vistos: continue
            classe = t.get('iconic_taxon_name', 'Outros')
            if local_tipo == "marinho" and classe not in ['Actinopterygii', 'Mollusca'] and 'Baleia' not in nome_pt: continue
            if local_tipo == "floresta" and classe == 'Actinopterygii': continue
            lista.append({'nome': nome_pt, 'sci': t.get('name'), 'foto': t['default_photo']['medium_url'], 'ambiente': local_tipo, 'dieta': dieta_realista(nome_pt, classe), 'repro': "Vivíparo" if classe == 'Mammalia' else "Ovíparo"})
            vistos.add(nome_pt)
        return lista[:15]
    except: return []

# BASES DE DADOS
florestas_db = pd.DataFrame({
    'nome': ['Amazónia', 'Congo', 'Selva de Bornéu', 'Taiga Siberiana', 'Floresta Negra', 'Mata Atlântica'],
    'lat': [-3.46, -0.22, 1.35, 61.52, 48.0, -23.55], 'lon': [-62.21, 23.61, 113.8, 105.31, 8.0, -46.63]
})
oceanos_db = pd.DataFrame({
    'nome': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 'Mar Mediterrâneo'],
    'lat': [0.0, -15.0, -20.0, 85.0, 35.0], 'lon': [-25.0, -140.0, 70.0, 0.0, 18.0]
})

# CONTROLO DE SESSÃO PARA CUTSCENE
if 'trigger_cutscene' not in st.session_state: st.session_state.trigger_cutscene = None

menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas do Mundo", "🌊 Oceanos e Mares", "📝 Diário", "⭐ Favoritos"])

# INTERFACE
if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério")
    st.map(pd.concat([florestas_db, oceanos_db]))

elif menu == "🌲 Florestas do Mundo":
    st.title("🌲 Florestas e Selvas")
    f_sel = st.selectbox("Escolha a Floresta:", [""] + list(florestas_db['nome']))
    if f_sel:
        st.markdown(f'<div class="cutscene-overlay"><h1>🌲 A entrar na selva...</h1><h2>{f_sel}</h2></div>', unsafe_allow_html=True)
        local = florestas_db[florestas_db['nome'] == f_sel].iloc[0]
        dados = buscar_fauna(local['lat'], local['lon'], "floresta")
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]:
                st.markdown(f"<div class='cc-card'><img src='{a['foto']}' class='img-cc'><div class='common-name'>{a['nome']}</div><div class='sci-name'>{a['sci']}</div><div class='label-expert'>DIETA</div><div class='val-expert'>{a['dieta']}</div></div>", unsafe_allow_html=True)

elif menu == "🌊 Oceanos e Mares":
    st.title("🌊 Oceanos e Mares")
    o_sel = st.selectbox("Escolha o Oceano/Mar:", [""] + list(oceanos_db['nome']))
    if o_sel:
        st.markdown(f'<div class="cutscene-overlay"><h1>🌊 A entrar no oceano...</h1><h2>{o_sel}</h2></div>', unsafe_allow_html=True)
        local = oceanos_db[oceanos_db['nome'] == o_sel].iloc[0]
        dados = buscar_fauna(local['lat'], local['lon'], "marinho")
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]:
                st.markdown(f"<div class='cc-card'><img src='{a['foto']}' class='img-cc'><div class='common-name'>{a['nome']}</div><div class='sci-name'>{a['sci']}</div><div class='label-expert'>DIETA</div><div class='val-expert'>{a['dieta']}</div></div>", unsafe_allow_html=True)
