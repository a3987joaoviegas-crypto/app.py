import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="BIO-MAPA EXPERT", layout="wide")

# Estilo para os Cards de Animais
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #adbac7; }
    .animal-card { 
        background: #1c2128; border-radius: 15px; padding: 20px; 
        border: 2px solid #2ea043; margin-bottom: 20px; text-align: center;
    }
    .img-fluid { width: 100%; height: 200px; object-fit: cover; border-radius: 10px; }
    h1, h2, h3 { color: #2ea043 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DADOS DE REGIÕES (Interatividade)
locais = pd.DataFrame({
    'nome': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 'Amazónia', 'Serengeti', 'Austrália', 'Portugal'],
    'lat': [0.0, -15.0, -20.0, 85.0, -3.46, -2.33, -25.27, 39.5],
    'lon': [-25.0, -140.0, 70.0, 0.0, -62.21, 34.83, 133.77, -8.0]
})

# 3. FUNÇÃO DE BUSCA POR NOMES COMUNS (iNaturalist)
def buscar_animais_regiao(termo):
    # Procuramos apenas no reino animal (taxon_id=1) e pedimos nomes comuns
    url = f"https://api.inaturalist.org/v1/observations?q={termo}&taxon_id=1&per_page=9&order=desc&order_by=created_at"
    try:
        res = requests.get(url, timeout=5).json()
        lista = []
        vistos = set()
        for obs in res.get('results', []):
            taxon = obs.get('taxon')
            if taxon:
                nome_comum = taxon.get('preferred_common_name')
                nome_sci = taxon.get('name')
                
                # Só adiciona se tiver nome comum e não for repetido
                if nome_comum and nome_comum not in vistos:
                    foto = taxon.get('default_photo', {}).get('medium_url')
                    if foto:
                        lista.append({
                            'comum': nome_comum,
                            'cientifico': nome_sci,
                            'foto': foto
                        })
                        vistos.add(nome_comum)
        return lista
    except:
        return []

# 4. INTERFACE PRINCIPAL
st.title("🌍 BIO-CENTRO DE COMANDO")

# O Mapa aparece primeiro
st.subheader("📍 Mapa Interativo de Hotspots")
st.map(locais, size=25, color='#2ea043')

# A Interatividade: O seletor que ativa as abas
st.markdown("### 🔍 Seleciona uma região para ativar o Laboratório")
escolha = st.selectbox("Clica aqui para escolher a região que tocaste no mapa:", [""] + list(locais['nome']))

st.divider()

# 5. AS ABAS SÓ APARECEM SE HOUVER UMA ESCOLHA
if escolha:
    aba1, aba2, aba3 = st.tabs(["🔬 LABORATÓRIO ANIMAL", "📅 CALENDÁRIO", "📝 NOTAS & FAVORITOS"])
    
    with aba1:
        st.header(f"🐾 Espécies Registadas em: {escolha}")
        with st.spinner("A carregar nomes comuns e fotos..."):
            animais = buscar_animais_regiao(escolha)
            
            if animais:
                cols = st.columns(3)
                for idx, a in enumerate(animais):
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div class='animal-card'>
                            <img src='{a['foto']}' class='img-fluid'>
                            <h3 style='margin-top:10px;'>{a['comum'].title()}</h3>
                            <p style='font-style:italic; font-size:13px;'>{a['cientifico']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"❤️ Favoritar {a['comum']}", key=f"fav_{idx}"):
                            if 'meus_favoritos' not in st.session_state:
                                st.session_state.meus_favoritos = []
                            st.session_state.meus_favoritos.append(a['comum'])
            else:
                st.warning("A tentar ligar aos satélites... Tenta selecionar a região novamente.")

    with aba2:
        st.header("📅 Diário de Bordo")
        c1, c2 = st.columns(2)
        data = c1.date_input("Data do avistamento:")
        animal_input = c2.text_input("Qual animal viste (ex: Orca)?")
        if st.button("Guardar no Calendário"):
            st.success(f"Avistamento de {animal_input} guardado para {data}!")

    with aba3:
        st.header("📝 Teu Bloco Científico")
        col_fav, col_note = st.columns(2)
        with col_fav:
            st.subheader("⭐ Favoritos")
            favs = st.session_state.get('meus_favoritos', [])
            for f in set(favs):
                st.write(f"✅ {f}")
        with col_note:
            st.subheader("📓 Notas")
            st.text_area("Escreve aqui as tuas observações:", height=200)

else:
    st.info("💡 Escolha uma região no menu acima para abrir o mapa e ver os animais.")
