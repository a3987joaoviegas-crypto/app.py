import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA (Podes mudar o nome aqui)
st.set_page_config(page_title="BIO-COMMAND PLANISFÉRIO", layout="wide")

# Estilo visual dos Cartões
st.markdown("""
    <style>
    .stApp { background-color: #0b1117; color: #adbac7; }
    .cc-card { 
        background: #1c2128; border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
    }
    .img-cc { width: 100%; height: 200px; object-fit: cover; border-radius: 8px; }
    .label-expert { color: #2ea043; font-weight: bold; font-size: 14px; margin-bottom: 2px; }
    .val-expert { color: white; font-size: 16px; margin-bottom: 10px; }
    h1, h2, h3 { color: #2ea043 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ALIMENTAÇÃO DINÂMICA ---
def definir_dieta(classe, nome):
    n = str(nome).lower()
    # Carnívoros estritos
    if any(x in n for x in ['leão', 'tubarão', 'lobo', 'águia', 'falcão', 'orca', 'serpente', 'tigre', 'jacaré']): 
        return "Carnívoro"
    # Herbívoros estritos
    if any(x in n for x in ['elefante', 'veado', 'vaca', 'zebra', 'girafa', 'coelho', 'cavalo', 'ovelha']): 
        return "Herbívoro"
    # Casos específicos de Omnívoros (como o Porco, Ursos, Humanos, etc)
    if any(x in n for x in ['porco', 'javali', 'urso', 'macaco', 'chimpanzé', 'rato', 'galinha']): 
        return "Omnívoro"
    
    # Se não estiver na lista acima, decide pela classe biológica
    c = str(classe).lower()
    if 'mammalia' in c: return "Omnívoro" # Maioria dos mamíferos não listados
    if 'aves' in c: return "Omnívoro"
    if 'reptilia' in c: return "Carnívoro"
    return "Omnívoro"

# 2. LÓGICA DE REPRODUÇÃO
def definir_repro(classe):
    c = str(classe).lower()
    if 'mammalia' in c: return "Vivíparo"
    if any(x in c for x in ['aves', 'reptilia', 'amphibia']): return "Ovíparo"
    return "Ovíparo / Variável"

# 3. MOTOR DE BUSCA (50 ESPÉCIES)
def buscar_fauna(termo, lat=None, lon=None):
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
                        'classe': t.get('iconic_taxon_name', 'Não Classificado'),
                        'repro': definir_repro(t.get('iconic_taxon_name', '')),
                        'dieta': definir_dieta(t.get('iconic_taxon_name', ''), nome)
                    })
                    vistos.add(nome)
        return lista
    except: return []

# 4. BASE DE DADOS
locais = pd.DataFrame({
    'nome': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 
             'Amazónia', 'Serengeti', 'Austrália', 'Portugal', 'Península de Yucatán', 'Rússia'],
    'lat': [0.0, -15.0, -20.0, 85.0, -3.46, -2.33, -25.27, 39.5, 18.84, 61.52],
    'lon': [-25.0, -140.0, 70.0, 0.0, -62.21, 34.83, 133.77, -8.0, -89.11, 105.31]
})

# 5. BARRA LATERAL (NAVEGADOR)
st.sidebar.title("📑 Navegador")
menu = st.sidebar.radio("Ir para:", ["🌍 Planisfério e Animais", "🔬 Laboratório Global", "📅 Calendário", "⭐ Favoritos"])

# 6. INTERFACE PRINCIPAL
if menu == "🌍 Planisfério e Animais":
    st.title("🌍 PLANISFÉRIO BIO-INTERATIVO")
    st.map(locais, color='#2ea043', size=40)
    st.markdown("---")
    escolha_regiao = st.selectbox("📍 Selecionar Região para ver Animais:", [""] + list(locais['nome']))
    
    if escolha_regiao:
        st.subheader(f"🗂️ Animais mais comuns da região: {escolha_regiao}")
        sel = locais[locais['nome'] == escolha_regiao].iloc[0]
        animais_data = buscar_fauna("", sel['lat'], sel['lon'])
        
        if animais_data:
            cols = st.columns(3)
            for i, animal in enumerate(animais_data):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class='cc-card'>
                        <img src='{animal['foto']}' class='img-cc'>
                        <h3>{animal['nome']}</h3>
                        <div class='label-expert'>NOME CIENTÍFICO</div>
                        <div class='val-expert'><i>{animal['sci']}</i></div>
                        <div class='label-expert'>MÉTODO REPRODUTIVO</div>
                        <div class='val-expert'>🧬 {animal['repro']}</div>
                        <div class='label-expert'>ALIMENTAÇÃO</div>
                        <div class='val-expert'>🍴 {animal['dieta']}</div>
                        <div class='label-expert'>CLASSE BIOLÓGICA</div>
                        <div class='val-expert'>🏷️ {animal['classe']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"⭐ Guardar {i}", key=f"btn_{i}"):
                        st.session_state.setdefault('meus_favs', []).append(animal['nome'])

elif menu == "🔬 Laboratório Global":
    st.title("🔬 Laboratório de Pesquisa Livre")
    pesquisa = st.text_input("Pesquisar qualquer animal no mundo:")
    if pesquisa:
        dados = buscar_fauna(pesquisa)
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i % 3]:
                st.image(a['foto'], use_container_width=True)
                st.write(f"**{a['nome']}**")

elif menu == "📅 Calendário":
    st.title("📅 Diário de Observação")
    st.date_input("Data:")
    st.text_input("Animal observado:")
    st.button("Registar")

elif menu == "⭐ Favoritos":
    st.title("⭐ Os Meus Favoritos")
    if 'meus_favs' in st.session_state:
        for f in set(st.session_state.meus_favs):
            st.success(f)
