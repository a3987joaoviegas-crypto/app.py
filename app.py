import streamlit as st
import requests

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo 🌍", layout="wide")

# 2. ESTADO DA APP
if 'zoo' not in st.session_state: st.session_state.zoo = []
if 'favs' not in st.session_state: st.session_state.favs = set()

for key, val in {
    'codigo': "", 'cor_card': "Preto", 'cor_fundo': "Preto", 
    'idioma': "pt-PT", 'lang_label': "Português", 'nome_zoologo': "Explorador"
}.items():
    if key not in st.session_state: st.session_state[key] = val

is_mestre = st.session_state.codigo == "6626"
LIMITE_ZOO = 80 if is_mestre else 20
LIMITE_FAV = 40 if is_mestre else 10 

# 3. DESIGN (GRELHA E IMAGENS 120PX)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23")
app_bg = cores_hex.get(st.session_state.cor_fundo, "#0b1117")

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; color: white; }}
    /* Contentor da Grelha */
    .animal-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 20px;
        padding: 10px;
    }}
    /* Cartão Pequeno */
    .animal-card {{
        background: {c_bg};
        border-radius: 12px;
        padding: 10px;
        text-align: center;
        border: 1px solid #444;
        transition: 0.3s;
    }}
    .animal-card:hover {{ transform: translateY(-5px); border-color: gold; }}
    /* Imagem Fixa em 120px */
    .animal-img {{
        width: 120px;
        height: 120px;
        border-radius: 10px;
        object-fit: cover;
        margin-bottom: 8px;
    }}
    .fav-tag {{ color: gold; font-weight: bold; font-size: 0.8em; }}
</style>
""", unsafe_allow_html=True)

# 4. FUNÇÃO DE BUSCA MELHORADA
def buscar(q, n=70):
    try:
        # Aumentamos o "rank" para garantir que apareçam espécies conhecidas
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page={n}&locale={st.session_state.idioma}"
        r = requests.get(url, timeout=10).json()
        return [{
            'id': x['id'],
            'nome': x.get('preferred_common_name', x['name']).title(),
            'sci': x['name'],
            'foto': x['default_photo']['square_url'] if x.get('default_photo') else "https://via.placeholder.com/120?text=Animal"
        } for x in r.get('results', [])]
    except:
        return []

def exibir_grelha(lista_animais, prefixo):
    st.markdown("<div class='animal-grid'>", unsafe_allow_html=True)
    cols = st.columns(4) # Cria colunas para os botões do Streamlit
    for i, an in enumerate(lista_animais):
        with cols[i % 4]:
            is_fav = an['id'] in st.session_state.favs
            fav_border = "border: 2px solid gold;" if is_fav else ""
            
            st.markdown(f"""
            <div class='animal-card' style='{fav_border}'>
                <img src='{an['foto']}' class='animal-img'>
                <div style='font-size: 0.9em; font-weight: bold;'>{an['nome']}</div>
                {"<div class='fav-tag'>⭐ FAVORITO</div>" if is_fav else ""}
            </div>
            """, unsafe_allow_html=True)
            
            # Botões de ação por baixo da imagem
            c1, c2 = st.columns(2)
            if c1.button("➕", key=f"add_{prefixo}_{i}"):
                if len(st.session_state.zoo) < LIMITE_ZOO:
                    if not any(x['id'] == an['id'] for x in st.session_state.zoo):
                        st.session_state.zoo.append(an)
                        st.rerun()
                else: st.error("Cheio!")
            
            if c2.button("⭐", key=f"fav_{prefixo}_{i}"):
                if is_fav: st.session_state.favs.remove(an['id'])
                elif len(st.session_state.favs) < LIMITE_FAV: st.session_state.favs.add(an['id'])
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# 5. INTERFACE (MENU)
with st.sidebar:
    st.title("🌍 MundoVivo")
    st.info(f"👤 {st.session_state.nome_zoologo}\n\n🐾 Zoo: {len(st.session_state.zoo)}/{LIMITE_ZOO}\n⭐ Favs: {len(st.session_state.favs)}/{LIMITE_FAV}")
    aba = st.sidebar.radio("Menu", ["🌍 Países", "🌲 Florestas", "🌊 Oceanos", "🔬 Lab", "⭐ Coleção", "⚙️ Definições"])

# 6. ABAS
if "Países" in aba:
    p = st.selectbox("País", ["Portugal", "Brasil", "Angola", "Moçambique", "Japão"])
    exibir_grelha(buscar(p, 70), "pais")

elif "Florestas" in aba:
    f = st.selectbox("Floresta/Bioma", ["Amazon", "Savanna", "Taiga", "Rainforest"])
    exibir_grelha(buscar(f, 70), "flor")

elif "Oceanos" in aba:
    o = st.selectbox("Oceano/Mar", ["Atlantic Ocean", "Pacific Ocean", "Coral Reef", "Deep Sea"])
    exibir_grelha(buscar(o, 70), "oce")

elif "Lab" in aba:
    q = st.text_input("Pesquisa rápida", "Lince")
    if q: exibir_grelha(buscar(q, 70), "lab")

elif "Coleção" in aba:
    st.title("Sua Coleção")
    if st.button("Libertar Todos"): st.session_state.zoo = []; st.session_state.favs = set(); st.rerun()
    exibir_grelha(st.session_state.zoo, "col")

elif "Definições" in aba:
    st.session_state.nome_zoologo = st.text_input("Nome", st.session_state.nome_zoologo)
    st.session_state.codigo = st.text_input("Código Premium", type="password")
    st.session_state.cor_card = st.selectbox("Cor Cartão", list(cores_hex.keys()))
    if st.button("Guardar"): st.rerun()
