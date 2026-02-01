import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# ESTILOS, SEGURANÇA E CUTSCENE DINÂMICA
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

    .cutscene-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 99999; display: flex; flex-direction: column; align-items: center; justify-content: center;
        background: radial-gradient(circle, #062814 0%, #0b1117 100%);
        color: #2ea043; text-align: center;
        animation: fadeOutScene 2.5s forwards; pointer-events: none;
    }
    @keyframes fadeOutScene { 0% { opacity: 1; } 85% { opacity: 1; } 100% { opacity: 0; visibility: hidden; } }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA DE DADOS
def dieta_realista(nome):
    n = str(nome).lower()
    if any(x in n for x in ['leão', 'tubarão', 'lobo', 'águia', 'orca', 'tigre', 'jacaré', 'serpente']): return "Carnívoro"
    if any(x in n for x in ['elefante', 'zebra', 'girafa', 'vaca', 'coelho', 'canguru']): return "Herbívoro"
    return "Omnívoro"

def buscar_fauna(lat, lon, local_tipo="geral"):
    url = "https://api.inaturalist.org/v1/observations"
    params = {"lat": lat, "lng": lon, "radius": 800, "taxon_id": 1, "per_page": 60, "locale": "pt-BR"}
    try:
        res = requests.get(url, params=params).json()
        lista = []
        vistos = set()
        for obs in res.get('results', []):
            t = obs.get('taxon')
            if not t or not t.get('default_photo'): continue
            nome_pt = (t.get('preferred_common_name') or t.get('name')).title()
            if nome_pt in vistos: continue
            classe = t.get('iconic_taxon_name', '')
            if local_tipo == "marinho" and classe not in ['Actinopterygii', 'Mollusca'] and 'Baleia' not in nome_pt: continue
            lista.append({'nome': nome_pt, 'sci': t.get('name'), 'foto': t['default_photo']['medium_url'], 'dieta': dieta_realista(nome_pt)})
            vistos.add(nome_pt)
        return lista[:15]
    except: return []

# SESSÃO PARA FAVORITOS
if 'meus_favs' not in st.session_state: st.session_state.meus_favs = []

# BASES DE DADOS EXPANDIDAS
paises_db = pd.DataFrame({
    'nome': ['Brasil', 'Portugal', 'México', 'Rússia', 'Angola', 'Estados Unidos', 'Canadá', 'Gronelândia', 'Inglaterra', 'Finlândia', 'Maldivas', 'Saara'],
    'lat': [-14.23, 39.39, 23.63, 61.52, -11.20, 37.09, 56.13, 71.70, 52.35, 61.92, 3.20, 23.41],
    'lon': [-51.92, -8.22, -102.55, 105.31, 17.87, -95.71, -106.34, -42.60, -1.17, 25.74, 73.22, 25.66]
})

florestas_db = pd.DataFrame({
    'nome': ['Amazónia', 'Congo', 'Selva de Bornéu', 'Taiga Siberiana', 'Floresta Negra', 'Mata Atlântica', 'Daintree Rainforest', 'Tongass'],
    'lat': [-3.46, -0.22, 1.35, 61.52, 48.0, -23.55, -16.17, 57.17],
    'lon': [-62.21, 23.61, 113.8, 105.31, 8.0, -46.63, 145.41, -134.58]
})

oceanos_db = pd.DataFrame({
    'nome': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 'Mar Mediterrâneo', 'Mar do Caribe', 'Mar Vermelho'],
    'lat': [0.0, -15.0, -20.0, 85.0, 35.0, 15.0, 20.0],
    'lon': [-25.0, -140.0, 70.0, 0.0, 18.0, -75.0, 38.0]
})

menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "📝 Diário", "⭐ Favoritos"])

def mostrar_animais(dados, prefixo):
    cols = st.columns(3)
    for i, a in enumerate(dados):
        with cols[i%3]:
            st.markdown(f"""
            <div class='cc-card'>
                <img src='{a['foto']}' class='img-cc'>
                <div class='common-name'>{a['nome']}</div>
                <div class='sci-name'>{a['sci']}</div>
                <div class='label-expert'>DIETA</div><div class='val-expert'>{a['dieta']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"⭐ Guardar", key=f"{prefixo}_{i}"):
                if a not in st.session_state.meus_favs: st.session_state.meus_favs.append(a)

if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério Bio-Interativo")
    st.map(paises_db)
    sel = st.selectbox("Escolha o País:", [""] + list(paises_db['nome']))
    if sel:
        st.markdown(f'<div class="cutscene-overlay"><h1>🌍 A viajar para...</h1><h2>{sel}</h2></div>', unsafe_allow_html=True)
        loc = paises_db[paises_db['nome'] == sel].iloc[0]
        mostrar_animais(buscar_fauna(loc['lat'], loc['lon']), "pla")

elif menu == "🌲 Florestas":
    st.title("🌲 Selvas e Florestas do Mundo")
    st.map(florestas_db, color='#2ea043')
    f_sel = st.selectbox("Escolha a Selva:", [""] + list(florestas_db['nome']))
    if f_sel:
        st.markdown(f'<div class="cutscene-overlay"><h1>🌲 A entrar na selva...</h1><h2>{f_sel}</h2></div>', unsafe_allow_html=True)
        loc = florestas_db[florestas_db['nome'] == f_sel].iloc[0]
        mostrar_animais(buscar_fauna(loc['lat'], loc['lon'], "floresta"), "for")

elif menu == "🌊 Oceanos":
    st.title("🌊 Mares e Oceanos do Planeta")
    st.map(oceanos_db, color='#0077be')
    o_sel = st.selectbox("Escolha o Mar/Oceano:", [""] + list(oceanos_db['nome']))
    if o_sel:
        st.markdown(f'<div class="cutscene-overlay"><h1>🌊 A entrar no oceano...</h1><h2>{o_sel}</h2></div>', unsafe_allow_html=True)
        loc = oceanos_db[oceanos_db['nome'] == o_sel].iloc[0]
        mostrar_animais(buscar_fauna(loc['lat'], loc['lon'], "marinho"), "oce")

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório de Pesquisas")
    p = st.text_input("Pesquisar Espécie:")
    if p:
        res = requests.get(f"https://api.inaturalist.org/v1/observations?q={p}&per_page=12&locale=pt-BR").json()
        dados_lab = []
        for obs in res.get('results', []):
            t = obs.get('taxon')
            if t and t.get('default_photo'):
                dados_lab.append({'nome': t.get('preferred_common_name', t['name']).title(), 'sci': t['name'], 'foto': t['default_photo']['medium_url'], 'dieta': "Pesquisa Lab"})
        mostrar_animais(dados_lab, "lab")

elif menu == "📝 Diário":
    st.title("📝 Diário")
    st.text_area("Notas de Observação:", height=400)

elif menu == "⭐ Favoritos":
    st.title("⭐ Espécies Favoritas")
    if not st.session_state.meus_favs:
        st.info("Ainda não guardaste nenhum animal.")
    else:
        mostrar_animais(st.session_state.meus_favs, "fav_page")
