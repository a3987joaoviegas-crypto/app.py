import streamlit as st
import pandas as pd
import pydeck as pdk
import requests # Para ligar à base de dados mundial

st.set_page_config(page_title="BioGlobe Open Source", layout="wide")

# INICIALIZAÇÃO DOS FAVORITOS E NOTAS
if 'favoritos' not in st.session_state:
    st.session_state.favoritos = []
if 'historico' not in st.session_state:
    st.session_state.historico = []

st.sidebar.title("🐾 BioGlobe Expert")
menu = st.sidebar.radio("Navegador:", ["Globo & Regiões", "Pesquisa por Classe", "Favoritos 🐆", "Bloco de Notas"])

# --- FUNÇÃO PARA BUSCAR DADOS REAIS (GBIF) ---
def buscar_dados_cientificos(query):
    # Esta base de dados é pública e não pede chave!
    url = f"https://api.gbif.org/v1/species/search?q={query}&limit=5"
    response = requests.get(url)
    return response.json()['results'] if response.status_code == 200 else []

# --- PÁGINA 1: GLOBO ---
if menu == "Globo & Regiões":
    st.title("🌍 Explorador Global (Dados Abertos)")
    st.write("Clica nos pontos para ver exemplos de fauna local.")
    
    view_state = pdk.ViewState(latitude=38.7, longitude=-9.1, zoom=1)
    # Criamos pontos clicáveis
    df = pd.DataFrame({
        'name': ['Europa', 'África', 'América do Sul', 'Ásia'],
        'lat': [48.0, 7.0, -15.0, 34.0], 'lon': [10.0, 21.0, -55.0, 100.0]
    })
    
    st.pydeck_chart(pdk.Deck(
        initial_view_state=view_state,
        layers=[pdk.Layer("ScatterplotLayer", df, get_position='[lon, lat]', get_radius=500000, get_color='[0, 255, 128]', pickable=True)],
        tooltip={"text": "{name}"}
    ))
    
    regiao = st.text_input("Escreve o nome de um País ou Continente:")
    if regiao:
        animais = buscar_dados_cientificos(regiao)
        for a in animais:
            st.write(f"✅ **{a.get('canonicalName', 'N/A')}** ({a.get('scientificName', '')}) - Classe: {a.get('class', 'N/A')}")

# --- PÁGINA 2: PESQUISA POR CLASSE ---
elif menu == "Pesquisa por Classe":
    st.title("🔍 Pesquisador de Nomes Científicos")
    classe_escolhida = st.selectbox("Escolhe a Classe:", ["Mammalia", "Aves", "Reptilia", "Amphibia", "Insecta"])
    
    if st.button("Listar Espécies"):
        dados = buscar_dados_cientificos(classe_escolhida)
        st.session_state.historico.append(f"Pesquisa: {classe_escolhida}")
        for d in dados:
            with st.container():
                col1, col2 = st.columns([3, 1])
                col1.write(f"**{d.get('canonicalName')}**")
                col1.caption(f"Nome Científico: {d.get('scientificName')}")
                if col2.button("❤️", key=d.get('key')):
                    st.session_state.favoritos.append(d.get('canonicalName'))
                    st.toast(f"{d.get('canonicalName')} nos favoritos!")

# --- PÁGINA 3: FAVORITOS ---
elif menu == "Favoritos 🐆":
    st.title("🐆 Os Meus Favoritos")
    for f in set(st.session_state.favoritos):
        st.subheader(f"❤️ {f}")

# --- PÁGINA 4: NOTAS ---
elif menu == "Bloco de Notas":
    st.title("📝 Notas de Campo")
    st.text_area("Escreve as tuas descobertas:", height=300)
    st.write("---")
    st.write("📜 Histórico Recente:", st.session_state.historico)
