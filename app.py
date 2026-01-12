import streamlit as st
import pandas as pd
import pydeck as pdk
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="BioGlobe Expert - Final", layout="wide")

# Estilo visual (Cores e Botões)
st.markdown("""
    <style>
    .stApp { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #2e7d32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZAÇÃO DE DADOS (Para não perder as notas e favoritos)
if 'favoritos' not in st.session_state: st.session_state.favoritos = []
if 'historico' not in st.session_state: st.session_state.historico = []
if 'notas_texto' not in st.session_state: st.session_state.notas_texto = ""

# 3. FUNÇÕES DE SUPORTE (Busca de dados e fotos)
def buscar_foto(nome):
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&titles={nome}&prop=pageimages&format=json&pithumbsize=500"
        res = requests.get(url, timeout=5).json()
        pages = res['query']['pages']
        for p in pages:
            return pages[p]['thumbnail']['source']
    except:
        return "https://images.unsplash.com/photo-1546182990-dffeafbe841d?q=80&w=400&auto=format&fit=crop"

def buscar_animais_regiao(termo):
    try:
        url = f"https://api.gbif.org/v1/species/search?q={termo}&limit=12"
        res = requests.get(url, timeout=5).json()
        return res.get('results', [])
    except:
        return []

# 4. MENU LATERAL
st.sidebar.title("🐾 BioGlobe Expert")
menu = st.sidebar.radio("Navegação:", ["Explorador Globo", "Pesquisa por Nome", "Meus Favoritos ❤️", "Bloco de Notas"])

# --- PÁGINA 1: GLOBO INTERATIVO ---
if menu == "Explorador Globo":
    st.title("🌍 Globo Terrestre de Biodiversidade")
    st.info("Visualiza os hotspots mundiais. Seleciona uma região abaixo para ver as espécies.")

    # Mapa interativo
    df_locais = pd.DataFrame({
        'name': ['Europa', 'África', 'América do Sul', 'Ásia', 'Oceania', 'Antártida'],
        'lat': [48.0, 7.0, -15.0, 34.0, -25.0, -75.0],
        'lon': [10.0, 21.0, -55.0, 100.0, 133.0, 0.0]
    })

    view_state = pdk.ViewState(latitude=15, longitude=0, zoom=0.8, pitch=30)
    st.pydeck_chart(pdk.Deck(
        initial_view_state=view_state,
        layers=[pdk.Layer("ScatterplotLayer", df_locais, get_position='[lon, lat]', get_color='[46, 125, 50, 180]', get_radius=700000, pickable=True)],
        tooltip={"text": "{name}"}
    ))

    regiao = st.selectbox("🗺️ Escolhe uma região para explorar:", [""] + list(df_locais['name']))
    
    if regiao:
        st.subheader(f"Espécies encontradas em: {regiao}")
        dados = buscar_animais_regiao(regiao)
        
        cols = st.columns(2) # Organiza em 2 colunas
        for i, a in enumerate(dados):
            if 'canonicalName' in a:
                nome = a['canonicalName']
                sci = a.get('scientificName', 'N/A')
                classe = a.get('class', 'Informação não disponível') # CORREÇÃO DO ERRO 'CLASS'
                
                with cols[i % 2]:
                    with st.expander(f"🐾 {nome}", expanded=True):
                        st.image(buscar_foto(nome), use_container_width=True)
                        st.write(f"**Científico:** *{sci}*")
                        st.caption(f"**Classe:** {classe}")
                        if st.button(f"Favorito: {nome}", key=f"fav_{i}"):
                            if nome not in st.session_state.favoritos:
                                st.session_state.favoritos.append(nome)
                                st.toast(f"{nome} adicionado!")

# --- PÁGINA 2: PESQUISA POR NOME ---
elif menu == "Pesquisa por Nome":
    st.title("🔍 Pesquisa Global")
    busca = st.text_input("Escreve o nome de um animal (Ex: Tigre, Orca, Falcon):")
    
    if busca:
        resultados = buscar_animais_regiao(busca)
        for r in resultados:
            if 'canonicalName' in r:
                c1, c2 = st.columns([1, 2])
                nome_r = r['canonicalName']
                c1.image(buscar_foto(nome_r))
                c2.subheader(nome_r)
                c2.write(f"**Nome Científico:** {r.get('scientificName', 'N/A')}")
                c2.write(f"**Reino:** {r.get('kingdom', 'N/A')}")
                st.divider()

# --- PÁGINA 3: FAVORITOS ---
elif menu == "Meus Favoritos ❤️":
    st.title("🐆 Minha Coleção Animal Print")
    if not st.session_state.favoritos:
        st.write("Ainda não tens favoritos. Explora o globo e clica no botão ❤️!")
    else:
        for f in st.session_state.favoritos:
            st.success(f"🌟 {f}")

# --- PÁGINA 4: NOTAS ---
elif menu == "Bloco de Notas":
    st.title("📝 Registos de Campo")
    st.session_state.notas_texto = st.text_area("Escreve as tuas notas científicas aqui:", 
                                               value=st.session_state.notas_texto, height=300)
    st.info("Dica: Estas notas ficam guardadas enquanto a página estiver aberta!")
