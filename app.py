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

# LÓGICA DE FILTRAGEM BIOLÓGICA REALISTA
def buscar_fauna_filtrada(lat, lon, bioma_tipo):
    url = "https://api.inaturalist.org/v1/observations"
    params = {"lat": lat, "lng": lon, "radius": 800, "taxon_id": 1, "per_page": 80, "locale": "pt-BR"}
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
            
            # REGRAS DE BIOMA RIGOROSAS
            if bioma_tipo == "marinho":
                # Apenas peixes, moluscos e cetáceos/répteis marinhos
                if classe not in ['Actinopterygii', 'Mollusca'] and not any(x in nome_pt for x in ['Baleia', 'Tubarão', 'Orca', 'Tartaruga Marinha']):
                    continue
            elif bioma_tipo == "floresta":
                # Bloqueia peixes em terra firme
                if classe in ['Actinopterygii'] or any(x in nome_pt for x in ['Tubarão', 'Polvo']):
                    continue

            lista.append({'nome': nome_pt, 'sci': t.get('name'), 'foto': t['default_photo']['medium_url']})
            vistos.add(nome_pt)
        return lista[:15]
    except: return []

# BASES DE DADOS
paises_db = pd.DataFrame({'nome': ['Brasil', 'Portugal', 'México', 'Rússia', 'Angola', 'Estados Unidos', 'Canadá', 'Gronelândia', 'Inglaterra', 'Finlândia', 'Maldivas', 'Saara'], 'lat': [-14.23, 39.39, 23.63, 61.52, -11.20, 37.09, 56.13, 71.70, 52.35, 61.92, 3.20, 23.41], 'lon': [-51.92, -8.22, -102.55, 105.31, 17.87, -95.71, -106.34, -42.60, -1.17, 25.74, 73.22, 25.66]})
florestas_db = pd.DataFrame({'nome': ['Amazónia', 'Congo', 'Selva de Bornéu', 'Taiga Siberiana', 'Mata Atlântica', 'Daintree Rainforest'], 'lat': [-3.46, -0.22, 1.35, 61.52, -23.55, -16.17], 'lon': [-62.21, 23.61, 113.8, 105.31, -46.63, 145.41]})
oceanos_db = pd.DataFrame({'nome': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 'Mar Mediterrâneo', 'Mar do Caribe'], 'lat': [0.0, -15.0, -20.0, 85.0, 35.0, 15.0], 'lon': [-25.0, -140.0, 70.0, 0.0, 18.0, -75.0]})

# SESSÃO
if 'favs' not in st.session_state: st.session_state.favs = []

menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "⭐ Favoritos"])

def exibir(dados, prefixo):
    cols = st.columns(3)
    for i, a in enumerate(dados):
        with cols[i%3]:
            st.markdown(f"<div class='cc-card'><img src='{a['foto']}' class='img-cc'><div class='common-name'>{a['nome']}</div><div class='sci-name'>{a['sci']}</div></div>", unsafe_allow_html=True)
            if st.button("⭐ Guardar", key=f"{prefixo}_{i}"): st.session_state.favs.append(a)

if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério")
    st.map(paises_db)
    sel = st.selectbox("Escolha a Região:", [""] + list(paises_db['nome']))
    if sel:
        st.markdown(f'<div class="cutscene-overlay"><h1>🌍 A viajar para...</h1><h2>{sel}</h2></div>', unsafe_allow_html=True)
        loc = paises_db[paises_db['nome'] == sel].iloc[0]
        exibir(buscar_fauna_filtrada(loc['lat'], loc['lon'], "geral"), "pla")

elif menu == "🌲 Florestas":
    st.title("🌲 Florestas e Selvas")
    f_sel = st.selectbox("Escolha a Selva:", [""] + list(florestas_db['nome']))
    if f_sel:
        st.markdown(f'<div class="cutscene-overlay"><h1>🌲 A entrar na selva...</h1><h2>{f_sel}</h2></div>', unsafe_allow_html=True)
        loc = florestas_db[florestas_db['nome'] == f_sel].iloc[0]
        exibir(buscar_fauna_filtrada(loc['lat'], loc['lon'], "floresta"), "for")

elif menu == "🌊 Oceanos":
    st.title("🌊 Oceanos e Mares")
    o_sel = st.selectbox("Escolha o Mar:", [""] + list(oceanos_db['nome']))
    if o_sel:
        st.markdown(f'<div class="cutscene-overlay"><h1>🌊 A mergulhar no...</h1><h2>{o_sel}</h2></div>', unsafe_allow_html=True)
        loc = oceanos_db[oceanos_db['nome'] == o_sel].iloc[0]
        exibir(buscar_fauna_filtrada(loc['lat'], loc['lon'], "marinho"), "oce")

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório")
    p = st.text_input("Pesquisar:")
    if p: exibir(buscar_fauna_filtrada(None, None, "geral"), "lab")

elif menu == "⭐ Favoritos":
    st.title("⭐ Favoritos")
    exibir(st.session_state.favs, "fav")
