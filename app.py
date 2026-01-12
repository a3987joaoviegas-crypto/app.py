import streamlit as st
import pandas as pd
import pydeck as pdk
import requests

# 1. CONFIGURAÇÃO EXPERT
st.set_page_config(page_title="BioGlobe Ocean Edition", layout="wide")

# Estilo Dark Mode com Neons Verdes
st.markdown("""
    <style>
    .stApp { background-color: #050a0f; color: #e0e0e0; }
    .animal-card { 
        background: #101923; border-radius: 15px; padding: 20px; 
        border: 2px solid #2ea043; margin-bottom: 20px;
    }
    h1, h3 { color: #2ea043 !important; text-shadow: 0 0 10px rgba(46,160,67,0.5); }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE BUSCA (Filtro Animalia + Marinho)
def buscar_fauna(regiao):
    try:
        # Busca focada no Reino Animal (Key 1)
        url = f"https://api.gbif.org/v1/species/search?q={regiao}&kingdomKey=1&limit=12"
        res = requests.get(url, timeout=5).json()
        
        lista = []
        vistos = set()
        for r in res.get('results', []):
            nome = r.get('canonicalName')
            if nome and nome not in vistos and r.get('kingdom') == 'Animalia':
                # Imagem via iNaturalist
                img = f"https://picsum.photos/seed/{r.get('key')}/400/300"
                try:
                    res_i = requests.get(f"https://api.inaturalist.org/v1/taxa?q={nome}&per_page=1", timeout=2).json()
                    if res_i['results']: img = res_i['results'][0]['default_photo']['medium_url']
                except: pass
                
                r['foto_url'] = img
                lista.append(r)
                vistos.add(nome)
        return lista
    except: return []

# 3. BASE DE DADOS DE REGIÕES E OCEANOS
locais = pd.DataFrame({
    'nome': [
        'Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 
        'Amazónia', 'Serengeti', 'Grande Barreira de Coral', 'Península Ibérica'
    ],
    'lat': [0.0, 0.0, -20.0, 80.0, -3.46, -2.33, -18.28, 40.0],
    'lon': [-25.0, -160.0, 80.0, 0.0, -62.21, 34.83, 147.69, -3.7],
    'tipo': ['Oceano', 'Oceano', 'Oceano', 'Oceano', 'Terra', 'Terra', 'Oceano', 'Terra']
})

# 4. INTERFACE
st.title("🌍 BioGlobe: Explorador de Oceanos e Continentes")

# Seleção interativa que comanda o Globo
col_mapa, col_info = st.columns([2, 1])

with col_info:
    st.write("### 📍 Painel de Navegação")
    escolha = st.selectbox("Escolha uma região ou oceano:", [""] + list(locais['nome']))
    
    if escolha:
        regiao_sel = locais[locais['nome'] == escolha].iloc[0]
        lat_foco, lon_foco = regiao_sel['lat'], regiao_sel['lon']
        zoom_foco = 2 if regiao_sel['tipo'] == 'Oceano' else 4
    else:
        lat_foco, lon_foco, zoom_foco = 10, 0, 1

with col_mapa:
    # Configuração do Globo com Círculos Verdes
    view_state = pdk.ViewState(latitude=lat_foco, longitude=lon_foco, zoom=zoom_foco, pitch=30)
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        locais,
        get_position='[lon, lat]',
        get_color='[46, 160, 67, 200]',
        get_radius=800000,
        pickable=True,
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer], 
        initial_view_state=view_state,
        map_style='mapbox://styles/mapbox/navigation-night-v1',
        tooltip={"text": "{nome}"}
    ))

st.divider()

# 5. LISTA DE ANIMAIS (Aparece após selecionar no globo/lista)
if escolha:
    st.subheader(f"🐙 Biodiversidade em: {escolha}")
    with st.spinner("A mergulhar nas bases de dados..."):
        animais = buscar_fauna(escolha)
        
        if not animais:
            st.warning("Não encontrámos animais específicos nesta área. Tenta uma região próxima!")
        else:
            # Mostra em grelha de 3 colunas
            cols = st.columns(3)
            for idx, a in enumerate(animais):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class='animal-card'>
                        <img src='{a['foto_url']}' style='width:100%; height:180px; object-fit:cover; border-radius:10px;'>
                        <h3>{a['canonicalName']}</h3>
                        <p style='font-size:12px;'><i>{a.get('scientificName')}</i></p>
                        <hr style='border-color:#30363d'>
                        <p style='font-size:11px; color:#8b949e;'>Classe: {a.get('class', 'N/D')}</p>
                    </div>
                    """, unsafe_allow_html=True)
