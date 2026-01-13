import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="BIO-COMMAND", layout="wide")

# Estilo para os Cartões de Cidadão (Visual, não Python)
st.markdown("""
    <style>
    .stApp { background-color: #0b1117; color: #adbac7; }
    .cc-card { 
        background: #1c2128; border-radius: 10px; padding: 15px; 
        border-left: 5px solid #2ea043; margin-bottom: 20px;
    }
    .img-cc { width: 100%; height: 160px; object-fit: cover; border-radius: 5px; }
    .info-label { color: #2ea043; font-weight: bold; font-size: 13px; }
    </style>
    """, unsafe_allow_html=True)

# 2. LÓGICA DE REPRODUÇÃO
def get_reproducao(classe):
    c = str(classe).lower()
    if 'mammalia' in c: return "Vivíparo"
    if any(x in c for x in ['aves', 'reptilia', 'amphibia']): return "Ovíparo"
    return "Ovíparo/Variável"

# 3. MOTOR DE BUSCA (50 ANIMAIS + TRADUÇÃO)
def buscar_laboratorio(termo, lat=None, lon=None):
    url = "https://api.inaturalist.org/v1/observations"
    params = {"taxon_id": 1, "per_page": 50, "locale": "pt-BR", "order": "desc", "order_by": "votes"}
    if lat and lon:
        params.update({"lat": lat, "lng": lon, "radius": 600})
    else:
        params.update({"q": termo})
    
    try:
        res = requests.get(url, params=params, timeout=10).json()
        lista = []
        vistos = set()
        for obs in res.get('results', []):
            t = obs.get('taxon')
            if t and t.get('default_photo'):
                nome = t.get('preferred_common_name') or t.get('name')
                if nome not in vistos:
                    lista.append({
                        'nome': nome.title(),
                        'sci': t.get('name'),
                        'foto': t['default_photo']['medium_url'],
                        'classe': t.get('iconic_taxon_name', 'Desconhecida'),
                        'repro': get_reproducao(t.get('iconic_taxon_name', ''))
                    })
                    vistos.add(nome)
        return lista
    except: return []

# 4. BASE DE DADOS (Com Yucatán e Rússia)
locais = pd.DataFrame({
    'lat': [0.0, -15.0, -20.0, 85.0, -3.46, -2.33, -25.27, 39.5, 18.84, 61.52],
    'lon': [-25.0, -140.0, 70.0, 0.0, -62.21, 34.83, 133.77, -8.0, -89.11, 105.31],
    'nome': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 
             'Amazónia', 'Serengeti', 'Austrália', 'Portugal', 'Península de Yucatán', 'Rússia']
})

# 5. INTERFACE
st.title("🌍 BIO-COMMAND CENTER")

# Mapa Nativo (Aparece sempre)
st.map(locais, color='#2ea043')

# Navegador do Laboratório (Global ou por Região)
st.markdown("---")
c1, c2 = st.columns([1, 1])
escolha_mapa = c1.selectbox("🎯 Escolha a região do mapa:", [""] + list(locais['nome']))
busca_manual = c2.text_input("🔬 Pesquisa Manual no Laboratório (Ex: Cobra, Leão):")

query = busca_manual if busca_manual else escolha_mapa

if query:
    tab1, tab2, tab3 = st.tabs(["🔬 LABORATÓRIO ANIMAL", "📅 CALENDÁRIO", "📝 NOTAS & FAVORITOS"])
    
    with tab1:
        st.subheader(f"🗂️ Cartões de Cidadão: {query}")
        
        # Define se busca por coordenadas ou texto
        if busca_manual:
            dados = buscar_laboratorio(busca_manual)
        else:
            sel = locais[locais['nome'] == escolha_mapa].iloc[0]
            dados = buscar_laboratorio("", sel['lat'], sel['lon'])
            
        if dados:
            cols = st.columns(3)
            for i, a in enumerate(dados):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class='cc-card'>
                        <img src='{a['foto']}' class='img-cc'>
                        <h3>{a['nome']}</h3>
                        <p><span class='info-label'>CIENTÍFICO:</span> <br><i>{a['sci']}</i></p>
                        <p><span class='info-label'>REPRODUÇÃO:</span> <br>{a['repro']}</p>
                        <p><span class='info-label'>CLASSE:</span> <br>{a['classe']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"⭐ Fav", key=f"f_{i}"):
                        st.session_state.setdefault('favs', []).append(a['nome'])
        else:
            st.warning("Nenhum animal encontrado.")

    with tab2:
        st.header("📅 Calendário")
        st.date_input("Data:")
        st.text_input("O que viste?")
        st.button("Registar")

    with tab3:
        st.header("📝 Notas")
        st.text_area("Escreve aqui...")
        for f in set(st.session_state.get('favs', [])):
            st.success(f"Favorito: {f}")
