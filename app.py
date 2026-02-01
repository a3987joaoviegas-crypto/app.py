import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# ESTILOS, SEGURANÇA E CUTSCENE DE ALTA PRIORIDADE
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    .stApp { background-color: #0b1117; color: #adbac7; }
    
    /* CARTÃO DE CIDADÃO REFINADO */
    .cc-card { 
        background: #1c2128; border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
        transition: transform 0.2s;
    }
    .cc-card:hover { transform: translateY(-5px); }
    .img-cc { width: 100%; height: 220px; object-fit: cover; border-radius: 8px; }
    .common-name { color: #2ea043; font-size: 22px; font-weight: bold; margin-top: 10px; text-align: center; }
    .sci-name { color: #8b949e; font-style: italic; font-size: 14px; text-align: center; margin-bottom: 15px; }
    
    .label-expert { color: #2ea043; font-weight: bold; font-size: 12px; margin-top: 5px; text-transform: uppercase;}
    .val-expert { color: white; font-size: 15px; margin-bottom: 8px; border-bottom: 1px solid #30363d; padding-bottom: 2px;}

    /* CUTSCENE AUTOMÁTICA (ESTILO CANVA/TECNOLÓGICO) */
    .cutscene-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 99999; display: flex; flex-direction: column; align-items: center; justify-content: center;
        background: radial-gradient(circle, #062814 0%, #0b1117 100%);
        color: #2ea043; font-family: sans-serif;
        animation: fadeOutScene 2.5s forwards; pointer-events: none;
    }
    @keyframes fadeOutScene { 
        0% { opacity: 1; visibility: visible; } 
        70% { opacity: 1; } 
        100% { opacity: 0; visibility: hidden; } 
    }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA DE BIOLOGIA PRECISA
def dieta_realista(nome, classe):
    n = str(nome).lower()
    carnivoros = ['leão', 'tubarão', 'lobo', 'águia', 'orca', 'tigre', 'jacaré', 'polvo', 'serpente', 'crocodilo', 'falcão', 'lince', 'leopardo']
    if any(x in n for x in carnivoros): return "Carnívoro (Predador)"
    if classe == 'Mammalia' and any(x in n for x in ['elefante', 'zebra', 'girafa', 'vaca', 'coelho', 'canguru', 'panda']): return "Herbívoro"
    return "Omnívoro / Variada"

def buscar_fauna_v2(lat, lon, local_tipo):
    url = "https://api.inaturalist.org/v1/observations"
    # Aumentado para 100 resultados para garantir que temos "animais suficientes" após o filtro
    params = {"lat": lat, "lng": lon, "radius": 800, "taxon_id": 1, "per_page": 100, "locale": "pt-BR", "order_by": "votes"}
    
    try:
        res = requests.get(url, params=params).json()
        lista = []
        vistos = set()
        
        for obs in res.get('results', []):
            t = obs.get('taxon')
            if not t or not t.get('default_photo'): continue
            
            nome_pt = (t.get('preferred_common_name') or t.get('name')).title()
            if nome_pt in vistos: continue
            
            classe = t.get('iconic_taxon_name', 'Outros')
            
            # FILTRO DE REGIAO RIGOROSO
            if local_tipo == "marinho":
                # Só aceita peixes, moluscos, mamíferos marinhos ou répteis aquáticos
                if classe not in ['Actinopterygii', 'Mollusca', 'Amphibia'] and not any(x in nome_pt for x in ['Baleia', 'Orca', 'Tubarão', 'Foca', 'Tartaruga']):
                    continue
            elif local_tipo == "floresta":
                # Bloqueia peixes e animais puramente marinhos
                if classe in ['Actinopterygii'] or any(x in nome_pt for x in ['Tubarão', 'Polvo']):
                    continue

            lista.append({
                'nome': nome_pt, 'sci': t.get('name'),
                'foto': t['default_photo']['medium_url'],
                'ambiente': "Aquático" if local_tipo == "marinho" else "Terrestre / Húmido",
                'dieta': dieta_realista(nome_pt, classe),
                'repro': "Vivíparo" if classe == 'Mammalia' else "Ovíparo"
            })
            vistos.add(nome_pt)
            if len(lista) >= 18: break # Garante pelo menos 18 animais diferentes
        return lista
    except: return []

# BASES DE DADOS AMPLIADAS
florestas_db = pd.DataFrame({
    'nome': ['Amazónia', 'Congo', 'Selva de Bornéu', 'Taiga Siberiana', 'Floresta Negra', 'Mata Atlântica', 'Daintree Rainforest'],
    'lat': [-3.46, -0.22, 1.35, 61.52, 48.0, -23.55, -16.17],
    'lon': [-62.21, 23.61, 113.8, 105.31, 8.0, -46.63, 145.41]
})

oceanos_db = pd.DataFrame({
    'nome': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 'Mar Mediterrâneo', 'Mar do Caribe'],
    'lat': [0.0, -15.0, -20.0, 85.0, 35.0, 15.0],
    'lon': [-25.0, -140.0, 70.0, 0.0, 18.0, -75.0]
})

# LÓGICA DE NAVEGAÇÃO E CUTSCENE
if 'menu_atual' not in st.session_state: st.session_state.menu_atual = ""
if 'favs' not in st.session_state: st.session_state.favs = []

menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas do Mundo", "🌊 Oceanos e Mares", "📝 Diário", "⭐ Favoritos"])

# DISPARAR CUTSCENE NA MUDANÇA
if menu != st.session_state.menu_atual:
    st.markdown(f"""
        <div class="cutscene-overlay">
            <h1 style="font-size: 50px;">🌍 MundoVivo</h1>
            <p style="font-size: 20px;">A sintonizar com {menu}...</p>
        </div>
    """, unsafe_allow_html=True)
    st.session_state.menu_atual = menu

def exibir_animais(lista, prefixo):
    if not lista:
        st.warning("Nenhum animal encontrado para esta região específica.")
        return
    cols = st.columns(3)
    for i, a in enumerate(lista):
        with cols[i % 3]:
            st.markdown(f"""
            <div class='cc-card'>
                <img src='{a['foto']}' class='img-cc'>
                <div class='common-name'>{a['nome']}</div>
                <div class='sci-name'>{a['sci']}</div>
                <div class='label-expert'>AMBIENTE REAL</div><div class='val-expert'>🏡 {a['ambiente']}</div>
                <div class='label-expert'>ALIMENTAÇÃO</div><div class='val-expert'>🍴 {a['dieta']}</div>
                <div class='label-expert'>REPRODUÇÃO</div><div class='val-expert'>🧬 {a['repro']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"⭐ Guardar", key=f"{prefixo}_{i}"):
                if a not in st.session_state.favs: st.session_state.favs.append(a)

# INTERFACES
if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério Bio-Interativo")
    st.map(pd.concat([florestas_db, oceanos_db]))

elif menu == "🌲 Florestas do Mundo":
    st.title("🌲 Exploração de Florestas e Selvas")
    st.map(florestas_db, color='#2ea043')
    f_sel = st.selectbox("Selecione a Floresta:", [""] + list(florestas_db['nome']))
    if f_sel:
        local = florestas_db[florestas_db['nome'] == f_sel].iloc[0]
        dados = buscar_fauna_v2(local['lat'], local['lon'], "floresta")
        exibir_animais(dados, "for")

elif menu == "🌊 Oceanos e Mares":
    st.title("🌊 Abismo Marinho")
    st.map(oceanos_db, color='#0077be')
    o_sel = st.selectbox("Selecione o Oceano/Mar:", [""] + list(oceanos_db['nome']))
    if o_sel:
        local = oceanos_db[oceanos_db['nome'] == o_sel].iloc[0]
        dados = buscar_fauna_v2(local['lat'], local['lon'], "marinho")
        exibir_animais(dados, "oce")

elif menu == "📝 Diário":
    st.title("📝 Diário de Observação")
    st.text_area("Escreve aqui as tuas notas sobre a fauna...", height=400)

elif menu == "⭐ Favoritos":
    st.title("⭐ Espécies Guardadas")
    exibir_animais(st.session_state.favs, "fav")
