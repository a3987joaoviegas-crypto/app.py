import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DE INTERFACE PRO
st.set_page_config(page_title="BIO-COMMAND CENTER 2026", layout="wide", page_icon="🌍")

# Estilo Dark Mode Expert
st.markdown("""
    <style>
    .stApp { background-color: #0b1117; color: #adbac7; }
    .animal-card { 
        background: #161b22; border-radius: 12px; padding: 10px; 
        border: 1px solid #2ea043; text-align: center; height: 350px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .img-zoom { width: 100%; height: 200px; object-fit: cover; border-radius: 8px; margin-bottom: 10px; }
    h3 { font-size: 18px !important; color: #2ea043; margin-top: 5px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #1c2128; border-radius: 5px; padding: 10px 20px; color: #adbac7;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE BUSCA COM TRADUÇÃO PARA PORTUGUÊS
def buscar_animais_expert(lat, lon):
    # Usamos locale=pt-BR para forçar a tradução dos nomes
    url = f"https://api.inaturalist.org/v1/observations?lat={lat}&lng={lon}&radius=500&taxon_id=1&per_page=32&order=desc&order_by=votes&locale=pt-BR"
    
    try:
        res = requests.get(url, timeout=10).json()
        lista = []
        vistos = set()
        for obs in res.get('results', []):
            taxon = obs.get('taxon')
            if taxon:
                # Prioridade 1: Nome Comum em Português
                nome_pt = taxon.get('preferred_common_name')
                # Prioridade 2: Nome Científico (se não houver tradução)
                nome_final = nome_pt.title() if nome_pt else taxon.get('name')
                
                if nome_final not in vistos and taxon.get('default_photo'):
                    lista.append({
                        'nome': nome_final,
                        'sci': taxon.get('name'),
                        'foto': taxon['default_photo']['medium_url']
                    })
                    vistos.add(nome_final)
        return lista
    except Exception as e:
        return []

# 3. BASE DE DADOS DE HOTSPOTS (Coordenadas Reais)
locais = pd.DataFrame({
    'nome': [
        'Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 
        'Amazónia', 'Serengeti (África)', 'Grande Barreira de Coral', 'Portugal', 
        'Antártida', 'Ilhas Galápagos'
    ],
    'lat': [0.0, -15.0, -20.0, 85.0, -3.46, -2.33, -18.28, 39.5, -75.25, -0.95],
    'lon': [-25.0, -140.0, 70.0, 0.0, -62.21, 34.83, 147.69, -8.0, 0.0, -90.96]
})

# 4. INTERFACE: MAPA E COMANDOS
st.markdown("<h1 style='text-align: center; color: #2ea043;'>🌍 BIO-COMMAND CENTER v3.5</h1>", unsafe_allow_html=True)

# O Mapa ocupa a parte superior
st.subheader("📍 Mapa Global de Biodiversidade (Pontos Verdes)")
st.map(locais, size=40, color='#2ea043')

st.divider()

# Coluna de seleção para ativar a pesquisa tátil
col_sel, col_empty = st.columns([1, 2])
with col_sel:
    escolha = st.selectbox("🎯 Escolha a região para abrir o Laboratório:", [""] + list(locais['nome']))

# 5. ABAS DE CONTEÚDO (Só aparecem após a escolha)
if escolha:
    # Obtém as coordenadas da escolha para a API
    sel_data = locais[locais['nome'] == escolha].iloc[0]
    
    tab1, tab2, tab3 = st.tabs(["🔬 LABORATÓRIO ANIMAL", "📅 CALENDÁRIO", "⭐ FAVORITOS & NOTAS"])
    
    with tab1:
        st.header(f"🔎 Espécies encontradas em: {escolha}")
        with st.spinner("A traduzir nomes e a carregar imagens..."):
            animais = buscar_animais_expert(sel_data['lat'], sel_data['lon'])
            
            if animais:
                # Grelha de 4 colunas para mostrar muitos animais de uma vez
                cols = st.columns(4)
                for idx, a in enumerate(animais):
                    with cols[idx % 4]:
                        st.markdown(f"""
                        <div class='animal-card'>
                            <img src='{a['foto']}' class='img-zoom'>
                            <h3>{a['nome']}</h3>
                            <p style='font-size:12px; color:#8b949e;'><i>{a['sci']}</i></p>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"⭐ Guardar", key=f"f_{idx}"):
                            if 'favs' not in st.session_state: st.session_state.favs = []
                            st.session_state.favs.append(a['nome'])
            else:
                st.warning("Nenhum animal com foto encontrado nesta coordenada específica. Tenta outra região!")

    with tab2:
        st.header("📅 Diário de Bordo")
        c1, c2 = st.columns(2)
        with c1:
            data_v = st.date_input("Data da Observação:")
            animal_v = st.text_input("Animal visto (ex: Orca):")
        with c2:
            local_v = st.text_input("Localização exata:", value=escolha)
            if st.button("Registar Avistamento"):
                st.success(f"Registado: {animal_v} em {data_v}")

    with tab3:
        st.header("📝 Notas Científicas")
        col_f, col_n = st.columns(2)
        with col_f:
            st.subheader("⭐ Favoritos")
            for f in set(st.session_state.get('favs', [])):
                st.write(f"✅ {f}")
        with col_n:
            st.subheader("📓 Bloco de Notas")
            st.text_area("Insira aqui as suas observações sobre a fauna regional:", height=200)

else:
    st.info("💡 Para começar, selecione uma região ou oceano no menu acima do mapa.")
