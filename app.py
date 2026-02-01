import streamlit as st
import pandas as pd
import requests
import time

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# ESTILOS CANVA-STYLE E ANIMAÇÕES
st.markdown("""
    <style>
    .stApp { background-color: #0b1117; color: #adbac7; }
    .cc-card { 
        background: #1c2128; border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
        transition: transform 0.3s;
    }
    .cc-card:hover { transform: scale(1.02); }
    .img-cc { width: 100%; height: 200px; object-fit: cover; border-radius: 8px; }
    .label-expert { color: #2ea043; font-weight: bold; font-size: 14px; }
    .val-expert { color: white; font-size: 16px; margin-bottom: 10px; }
    
    /* ANIMAÇÃO FLORESTA (CANVA STYLE) */
    @keyframes forestFade {
        0% { background: #0b1117; }
        50% { background: #062814; }
        100% { background: #0b1117; }
    }
    .cutscene-forest { animation: forestFade 2s ease-in-out; }

    /* ANIMAÇÃO BOLHAS (CANVA STYLE) */
    @keyframes bubbles {
        0% { transform: translateY(100vh); opacity: 0; }
        50% { opacity: 0.5; }
        100% { transform: translateY(-100vh); opacity: 0; }
    }
    .bubble {
        position: fixed; bottom: -10px; background: rgba(255,255,255,0.3);
        border-radius: 50%; animation: bubbles 3s infinite; pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA DE AMBIENTE
def definir_ambiente(classe, nome):
    n, c = str(nome).lower(), str(classe).lower()
    if any(x in n for x in ['tubarão', 'peixe', 'orca', 'baleia', 'polvo', 'raia', 'coral']): return "Marinho / Oceânico"
    if any(x in n for x in ['sapo', 'rã', 'jacaré', 'crocodilo', 'hipopótamo', 'garça']): return "Ambiente Húmido"
    if any(x in n for x in ['camelo', 'escorpião', 'serpente']): return "Árido / Desértico"
    return "Terrestre / Florestal"

# MOTOR DE BUSCA
def buscar_fauna(termo, lat=None, lon=None):
    url = "https://api.inaturalist.org/v1/observations"
    params = {"taxon_id": 1, "per_page": 70, "locale": "pt-BR", "order": "desc", "order_by": "votes"}
    if lat and lon: params.update({"lat": lat, "lng": lon, "radius": 600})
    else: params.update({"q": termo})
    try:
        res = requests.get(url, params=params).json()
        lista = []
        for obs in res.get('results', []):
            t = obs.get('taxon')
            if t and t.get('default_photo'):
                nome = t.get('preferred_common_name') or t.get('name')
                lista.append({
                    'nome': nome.title(), 'sci': t.get('name'),
                    'foto': t['default_photo']['medium_url'],
                    'classe': t.get('iconic_taxon_name', 'Outros'),
                    'repro': "Vivíparo" if 'mammalia' in t.get('iconic_taxon_name','').lower() else "Ovíparo",
                    'dieta': "Especializada", # Simplificado para manter performance
                    'ambiente': definir_ambiente(t.get('iconic_taxon_name', ''), nome)
                })
        return lista
    except: return []

# BASES DE DATA MAPAS
florestas_db = pd.DataFrame({
    'nome': ['Amazónia', 'Congo', 'Taiga', 'Tongass', 'Daintree', 'Bornéu', 'Floresta Negra'],
    'lat': [-3.46, -0.22, 61.52, 57.17, -16.17, 1.35, 48.0],
    'lon': [-62.21, 23.61, 105.31, -134.58, 145.41, 113.8, 8.0]
})

oceanos_db = pd.DataFrame({
    'nome': ['Atlântico', 'Pacífico', 'Índico', 'Ártico'],
    'lat': [0.0, -15.0, -20.0, 85.0], 'lon': [-25.0, -140.0, 70.0, 0.0]
})

if 'meus_favs_objetos' not in st.session_state: st.session_state.meus_favs_objetos = []

# SIDEBAR
st.sidebar.title("🌲 MundoVivo")
menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas do Mundo", "🌊 Oceanos", "⭐ Favoritos"])

def desenhar_cartao(a, i):
    st.markdown(f"""
    <div class='cc-card'>
        <img src='{a['foto']}' class='img-cc'>
        <h3>{a['nome']}</h3>
        <p class='label-expert'>AMBIENTE</p><p class='val-expert'>{a['ambiente']}</p>
        <p class='label-expert'>REPRODUÇÃO</p><p class='val-expert'>{a['repro']}</p>
    </div>
    """, unsafe_allow_html=True)

# INTERFACES
if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério Bio-Interativo")
    st.map(pd.concat([florestas_db, oceanos_db]))

elif menu == "🌲 Florestas do Mundo":
    st.title("🌲 Exploração Florestal")
    st.map(florestas_db, color='#2ea043')
    f_sel = st.selectbox("Selecione a Floresta:", [""] + list(florestas_db['nome']))
    if f_sel:
        # CUTSCENE AUTOMÁTICA (CSS)
        st.markdown("<div class='cutscene-forest' style='height:10px;'></div>", unsafe_allow_html=True)
        sel = florestas_db[florestas_db['nome'] == f_sel].iloc[0]
        dados = buscar_fauna("", sel['lat'], sel['lon'])
        cols = st.columns(3)
        for i, a in enumerate(dados[:12]):
            with cols[i%3]:
                desenhar_cartao(a, i)
                if st.button(f"⭐ Guardar {i}", key=f"f{i}"): st.session_state.meus_favs_objetos.append(a)

elif menu == "🌊 Oceanos":
    st.title("🌊 Abismo Marinho")
    st.map(oceanos_db, color='#0077be')
    o_sel = st.selectbox("Selecione o Oceano:", [""] + list(oceanos_db['nome']))
    if o_sel:
        # CUTSCENE BOLHAS (CSS)
        for _ in range(10): st.markdown("<div class='bubble' style='left:{}%; width:{}px; height:{}px; animation-delay:{}s;'></div>".format(pd.np.random.randint(0,100), 20, 20, pd.np.random.randint(0,3)), unsafe_allow_html=True)
        sel = oceanos_db[oceanos_db['nome'] == o_sel].iloc[0]
        dados = buscar_fauna("", sel['lat'], sel['lon'])
        cols = st.columns(3)
        for i, a in enumerate(dados[:12]):
            with cols[i%3]:
                desenhar_cartao(a, i)
                if st.button(f"⭐ Guardar {i}", key=f"o{i}"): st.session_state.meus_favs_objetos.append(a)

elif menu == "⭐ Favoritos":
    st.title("⭐ Coleção Privada")
    if st.button("🗑️ Limpar Tudo"): st.session_state.meus_favs_objetos = []; st.rerun()
    cols = st.columns(3)
    for i, a in enumerate(st.session_state.meus_favs_objetos):
        with cols[i%3]:
            desenhar_cartao(a, i)
            if st.button(f"❌ Remover", key=f"del{i}"):
                st.session_state.meus_favs_objetos.remove(a)
                st.rerun()
