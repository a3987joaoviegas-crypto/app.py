import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# ESTILOS, SEGURANÇA E CUTSCENE REFORÇADA
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
    .img-cc { width: 100%; height: 200px; object-fit: cover; border-radius: 8px; }
    .common-name { color: #2ea043; font-size: 20px; font-weight: bold; margin-top: 10px; text-align: center; }
    .sci-name { color: white; font-style: italic; font-size: 14px; text-align: center; margin-bottom: 15px; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
    .label-expert { color: #2ea043; font-weight: bold; font-size: 12px; margin-top: 5px;}
    .val-expert { color: white; font-size: 14px; margin-bottom: 8px; }

    /* FIX: CUTSCENE QUE APARECE SEMPRE */
    .cutscene-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 99999; display: flex; align-items: center; justify-content: center;
        background: #0b1117; color: #2ea043;
        animation: fadeAway 2.2s forwards; pointer-events: none;
    }
    @keyframes fadeAway { 
        0% { opacity: 1; visibility: visible; } 
        85% { opacity: 1; } 
        100% { opacity: 0; visibility: hidden; } 
    }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA DE DADOS (BIOLOGIA E FILTRAGEM)
def consultar_dieta_real(nome):
    n = str(nome).lower()
    if any(x in n for x in ['leão', 'tubarão', 'lobo', 'águia', 'falcão', 'orca', 'serpente', 'tigre', 'jacaré', 'polvo', 'coruja', 'sapo', 'cobra', 'lince', 'crocodilo']):
        return "Carnívoro (Predador)"
    if any(x in n for x in ['elefante', 'veado', 'vaca', 'zebra', 'girafa', 'coelho', 'cavalo', 'ovelha', 'cabra', 'hipopótamo', 'rinoceronte', 'canguru', 'panda', 'tartaruga', 'gazela']):
        return "Herbívoro (Plantas/Frutos)"
    return "Omnívoro / Dieta Variada"

def buscar_fauna(termo, lat=None, lon=None, local_tipo="geral"):
    url = "https://api.inaturalist.org/v1/observations"
    params = {"taxon_id": 1, "per_page": 45, "locale": "pt-BR", "order_by": "votes"}
    if lat and lon: params.update({"lat": lat, "lng": lon, "radius": 700})
    else: params.update({"q": termo})
    
    try:
        res = requests.get(url, params=params).json()
        lista = []
        vistos = set() # FIX: EVITAR REPETIDOS
        
        for obs in res.get('results', []):
            t = obs.get('taxon')
            if not t or not t.get('default_photo'): continue
            
            nome_pt = (t.get('preferred_common_name') or t.get('name')).title()
            if nome_pt in vistos: continue
            
            classe = t.get('iconic_taxon_name', 'Outros')
            
            # FIX: FILTRO DE BIOMA (NADA DE ANIMAIS "NADA A VER")
            if local_tipo == "marinho":
                if classe not in ['Actinopterygii', 'Mollusca', 'Amphibia', 'Reptilia'] and 'Baleia' not in nome_pt and 'Orca' not in nome_pt and 'Tubarão' not in nome_pt:
                    continue
            elif local_tipo == "floresta":
                if classe in ['Actinopterygii']: continue

            lista.append({
                'nome': nome_pt, 'sci': t.get('name'),
                'foto': t['default_photo']['medium_url'],
                'classe': classe,
                'ambiente': "Marinho" if local_tipo == "marinho" else "Terrestre",
                'dieta': consultar_dieta_real(nome_pt),
                'repro': "Vivíparo" if classe == 'Mammalia' else "Ovíparo"
            })
            vistos.add(nome_pt)
        return lista[:12]
    except: return []

# BASES DE DATA
paises_db = pd.DataFrame({
    'nome': ['Brasil', 'Portugal', 'México', 'Rússia', 'Angola', 'Estados Unidos', 'Canadá', 'Gronelândia', 'Inglaterra', 'Finlândia', 'Maldivas', 'Saara'],
    'lat': [-14.23, 39.39, 23.63, 61.52, -11.20, 37.09, 56.13, 71.70, 52.35, 61.92, 3.20, 23.41],
    'lon': [-51.92, -8.22, -102.55, 105.31, 17.87, -95.71, -106.34, -42.60, -1.17, 25.74, 73.22, 25.66]
})

florestas_db = pd.DataFrame({
    'nome': ['Amazónia', 'Congo', 'Bornéu', 'Taiga Siberiana', 'Floresta Negra', 'Daintree', 'Tongass', 'Mata Atlântica'],
    'lat': [-3.46, -0.22, 1.35, 61.52, 48.0, -16.17, 57.17, -23.55],
    'lon': [-62.21, 23.61, 113.8, 105.31, 8.0, 145.41, -134.58, -46.63]
})

oceanos_db = pd.DataFrame({
    'nome': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 'Mar Mediterrâneo', 'Mar do Caribe'],
    'lat': [0.0, -15.0, -20.0, 85.0, 35.0, 15.0],
    'lon': [-25.0, -140.0, 70.0, 0.0, 18.0, -75.0]
})

# SESSÃO E NAVEGAÇÃO
if 'favs' not in st.session_state: st.session_state.favs = []
if 'last_menu' not in st.session_state: st.session_state.last_menu = ""

menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas e Selvas", "🌊 Oceanos e Mares", "🔬 Laboratório", "📝 Diário", "⭐ Favoritos"])

# FIX: GATILHO DA CUTSCENE
if menu != st.session_state.last_menu:
    st.markdown(f"<div class='cutscene-overlay'><h1>🚀 A explorar {menu}...</h1></div>", unsafe_allow_html=True)
    st.session_state.last_menu = menu

def desenhar_cartao(a, i, key_prefix):
    st.markdown(f"""
    <div class='cc-card'>
        <img src='{a['foto']}' class='img-cc'>
        <div class='common-name'>{a['nome']}</div>
        <div class='sci-name'>{a['sci']}</div>
        <div class='label-expert'>AMBIENTE NATURAL</div><div class='val-expert'>🏡 {a['ambiente']}</div>
        <div class='label-expert'>ALIMENTAÇÃO REAL</div><div class='val-expert'>🍴 {a['dieta']}</div>
        <div class='label-expert'>REPRODUÇÃO</div><div class='val-expert'>🧬 {a['repro']}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button(f"⭐ Guardar", key=f"{key_prefix}_{i}"):
        if a not in st.session_state.favs: st.session_state.favs.append(a)

# INTERFACES
if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério")
    st.map(paises_db, color='#2ea043')
    sel_p = st.selectbox("Escolha um País:", [""] + list(paises_db['nome']))
    if sel_p:
        dados = buscar_fauna("", *paises_db[paises_db['nome']==sel_p][['lat','lon']].values[0])
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]: desenhar_cartao(a, i, "pla")

elif menu == "🌲 Florestas e Selvas":
    st.title("🌲 Florestas e Selvas")
    st.map(florestas_db, color='#1e5631')
    f_sel = st.selectbox("Selecione:", [""] + list(florestas_db['nome']))
    if f_sel:
        dados = buscar_fauna("", *florestas_db[florestas_db['nome']==f_sel][['lat','lon']].values[0], "floresta")
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]: desenhar_cartao(a, i, "for")

elif menu == "🌊 Oceanos e Mares":
    st.title("🌊 Oceanos e Mares")
    st.map(oceanos_db, color='#0077be')
    o_sel = st.selectbox("Selecione:", [""] + list(oceanos_db['nome']))
    if o_sel:
        dados = buscar_fauna("", *oceanos_db[oceanos_db['nome']==o_sel][['lat','lon']].values[0], "marinho")
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]: desenhar_cartao(a, i, "oce")

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório")
    p = st.text_input("Animal:")
    if p:
        dados = buscar_fauna(p)
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]: desenhar_cartao(a, i, "lab")

elif menu == "📝 Diário":
    st.title("📝 Diário")
    st.text_area("Notas:", height=400)

elif menu == "⭐ Favoritos":
    st.title("⭐ Favoritos")
    cols = st.columns(3)
    for i, a in enumerate(st.session_state.favs):
        with cols[i%3]: desenhar_cartao(a, i, "fav")
