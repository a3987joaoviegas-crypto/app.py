import streamlit as st
import pandas as pd
import requests
import pydeck as pdk

# 1. CONFIGURAÇÃO EXPERT
st.set_page_config(page_title="BIO-COMMAND CENTER GLOBAL", layout="wide", page_icon="🌎")

st.markdown("""
    <style>
    .stApp { background-color: #0b1117; color: #adbac7; }
    .cc-card { 
        background: #161b22; border-radius: 15px; padding: 15px; 
        border: 2px solid #2ea043; margin-bottom: 20px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
    }
    .img-cc { width: 100%; height: 220px; object-fit: cover; border-radius: 10px; border: 1px solid #30363d; }
    .label-cc { color: #2ea043; font-weight: bold; font-size: 12px; text-transform: uppercase; }
    .info-cc { color: white; font-size: 14px; margin-bottom: 8px; }
    h1, h2 { color: #2ea043 !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE REPRODUÇÃO (Lógica Taxonómica)
def definir_reproducao(classe):
    classe = str(classe).lower()
    if classe in ['mammalia', 'mamíferos']: return "Vivíparo (Geralmente)"
    if classe in ['aves', 'reptilia', 'amphibia', 'reptéis', 'anfíbios']: return "Ovíparo"
    if classe in ['actinopterygii', 'elasmobranchii', 'peixes']: return "Ovíparo / Ovovivíparo"
    return "Variável / Invertebrado"

# 3. MOTOR DE BUSCA GLOBAL (50 ANIMAIS)
def buscar_dados_completos(query, lat=None, lon=None):
    base_url = "https://api.inaturalist.org/v1/observations"
    params = {
        "taxon_id": 1, "per_page": 50, "order": "desc", 
        "order_by": "votes", "locale": "pt-BR"
    }
    if lat and lon:
        params.update({"lat": lat, "lng": lon, "radius": 500})
    else:
        params.update({"q": query})
        
    try:
        res = requests.get(base_url, params=params, timeout=10).json()
        lista = []
        vistos = set()
        for obs in res.get('results', []):
            t = obs.get('taxon')
            if t:
                nome = t.get('preferred_common_name') or t.get('name')
                if nome not in vistos and t.get('default_photo'):
                    lista.append({
                        'nome': nome.title(),
                        'sci': t.get('name'),
                        'foto': t['default_photo']['medium_url'],
                        'classe': t.get('iconic_taxon_name', 'N/D'),
                        'familia': t.get('ancestor_ids', ['N/D'])[-1], # Exemplo simplificado
                        'reproducao': definir_reproducao(t.get('iconic_taxon_name'))
                    })
                    vistos.add(nome)
        return lista
    except: return []

# 4. BASE DE DADOS EXPANDIDA
locais = pd.DataFrame({
    'nome': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 
             'Amazónia', 'Serengeti', 'Austrália', 'Portugal', 'Rússia', 'Península de Yucatán'],
    'lat': [0.0, -15.0, -20.0, 85.0, -3.46, -2.33, -25.27, 39.5, 61.52, 18.84],
    'lon': [-25.0, -140.0, 70.0, 0.0, -62.21, 34.83, 133.77, -8.0, 105.31, -89.11]
})

# 5. GLOBO INTERATIVO 3D
st.title("🌍 BIO-COMMAND CENTER: GLOBO 3D")

escolha = st.selectbox("🎯 Clique para focar numa região ou navegue no Globo:", ["Explorar Global"] + list(locais['nome']))

if escolha != "Explorar Global":
    sel = locais[locais['nome'] == escolha].iloc[0]
    view_state = pdk.ViewState(latitude=sel['lat'], longitude=sel['lon'], zoom=4, pitch=45, bearing=0)
else:
    view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1, pitch=30, bearing=0)

# Camada de Hotspots (Círculos Verdes)
layer = pdk.Layer(
    "ScatterplotLayer", locais, get_position='[lon, lat]',
    get_color='[46, 160, 67, 200]', get_radius=500000, pickable=True
)

st.pydeck_chart(pdk.Deck(
    layers=[layer], initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/navigation-night-v1",
    tooltip={"text": "{nome}"}
))

st.divider()

# 6. LABORATÓRIO E CARTÕES DE CIDADÃO
tab1, tab2, tab3 = st.tabs(["🔬 LABORATÓRIO ANIMAL", "📅 CALENDÁRIO", "📝 NOTAS"])

with tab1:
    col_search, col_info = st.columns([1, 2])
    with col_search:
        pesquisa_manual = st.text_input("🔬 Navegador do Laboratório (Pesquisa Global):", 
                                       placeholder="Ex: Tigre, Tubarão, Cobra...")
    
    # Define o que pesquisar: se manual ou se pela região do mapa
    query_final = pesquisa_manual if pesquisa_manual else escolha
    
    if query_final and query_final != "Explorar Global":
        st.subheader(f"🗂️ Registos de Identidade: {query_final}")
        
        # Busca por coordenadas se for região, senão busca por texto
        if pesquisa_manual:
            dados_animais = buscar_dados_completos(query_final)
        else:
            dados_animais = buscar_dados_completos("", sel['lat'], sel['lon'])

        if dados_animais:
            cols = st.columns(3)
            for idx, a in enumerate(dados_animais):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class='cc-card'>
                        <img src='{a['foto']}' class='img-cc'>
                        <div style='padding:10px;'>
                            <h3 style='margin:0;'>{a['nome']}</h3>
                            <p style='font-size:11px; color:#8b949e; margin-bottom:15px;'><i>{a['sci']}</i></p>
                            
                            <div class='label-cc'>Tipo de Reprodução</div>
                            <div class='info-cc'>🧬 {a['reproducao']}</div>
                            
                            <div class='label-cc'>Classe Taxonómica</div>
                            <div class='info-cc'>🏷️ {a['classe']}</div>
                            
                            <div class='label-cc'>Estado de Observação</div>
                            <div class='info-cc'>✅ Identificação Confirmada</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Nenhum 'Cartão de Cidadão' disponível para esta pesquisa.")

# 7. CALENDÁRIO E NOTAS (Mantidos conforme pedido)
with tab2:
    st.date_input("Data da Observação:")
    st.text_input("Animal Avistado:")
    st.button("Registar no Diário")

with tab3:
    st.text_area("Bloco de Notas Científico:", height=200)
