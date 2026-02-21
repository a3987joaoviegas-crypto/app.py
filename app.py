import streamlit as st
import requests

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo 🌍", layout="wide")

# 2. TRADUÇÃO COMPLETA
idiomas = {
    "Português": {"paises": "Países", "florestas": "Florestas", "oceanos": "Oceanos", "lab": "Laboratório", "col": "Coleção", "def": "Definições", "luta": "Lutar", "arena": "Arena de Luta", "guardar": "Guardar", "fav": "Favoritos", "grupo": "Filtrar Grupo"},
    "English": {"paises": "Countries", "florestas": "Forests", "oceanos": "Oceans", "lab": "Laboratory", "col": "Collection", "def": "Settings", "luta": "Fight", "arena": "Fight Arena", "guardar": "Save", "fav": "Favorites", "grupo": "Filter Group"}
}

# 3. ESTADO DA APP
if 'zoo' not in st.session_state: st.session_state.zoo = []
if 'favs' not in st.session_state: st.session_state.favs = set()

for key, val in {
    'codigo': "", 'codigo_perm': "", 'cor_card': "Preto", 'cor_fundo': "Preto", 
    'idioma': "pt-PT", 'lang_label': "Português", 'nome_zoologo': "Explorador", 'luz': False
}.items():
    if key not in st.session_state: st.session_state[key] = val

T = idiomas.get(st.session_state.lang_label, idiomas["Português"])
is_mestre = st.session_state.codigo == "6626" or st.session_state.codigo_perm == "67lucas62"

# LIMITES RÍGIDOS PEDIDOS
LIMITE_ZOO = 80 if is_mestre else 20
LIMITE_FAV = 40 if is_mestre else 10 

# 4. DESIGN (CSS)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f", "Amarelo": "#f1c40f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23")
app_bg = cores_hex.get(st.session_state.cor_fundo, "#0b1117")
txt_color = "#000" if st.session_state.cor_card == "Branco" else "#fff"

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; color: {txt_color}; }}
    .cc-card {{ background: {c_bg} !important; border-radius: 20px; padding: 25px; border-left: 15px solid gold; margin-bottom: 30px; box-shadow: 8px 8px 20px rgba(0,0,0,0.4); }}
    .fav-card {{ border: 6px solid #FFD700 !important; }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÃO DE BUSCA (70 ANIMAIS)
def buscar(q, n=70):
    try:
        # Forçamos a busca por animais (taxon_id=1)
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page={n}&locale={st.session_state.idioma}"
        r = requests.get(url, timeout=10).json()
        resultados = []
        for x in r.get('results', []):
            foto = x.get('default_photo')
            img = foto.get('medium_url') if foto else "https://via.placeholder.com/600x450?text=Animal"
            resultados.append({
                'id': x['id'],
                'nome': x.get('preferred_common_name', x['name']).title(),
                'sci': x['name'],
                'foto': img
            })
        return resultados
    except:
        return []

def card(an, k, btn_txt="➕", show_fav=False):
    is_fav = an['id'] in st.session_state.favs
    fav_class = "fav-card" if is_fav else ""
    st.markdown(f"""<div class='cc-card {fav_class}'><img src='{an['foto']}' style='width:100%; border-radius:15px; height:400px; object-fit:cover;'><h2>{"⭐ " if is_fav else ""}{an['nome']}</h2><p><i>{an['sci']}</i></p></div>""", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button(btn_txt, key=f"btn_{k}", use_container_width=True):
            if "Libertar" in btn_txt:
                st.session_state.zoo = [x for x in st.session_state.zoo if x['id'] != an['id']]
                if an['id'] in st.session_state.favs: st.session_state.favs.remove(an['id'])
                st.rerun()
            elif len(st.session_state.zoo) < LIMITE_ZOO:
                if not any(x['id'] == an['id'] for x in st.session_state.zoo):
                    st.session_state.zoo.append(an); st.toast(f"{an['nome']} capturado!")
            else: st.error(f"Zoo cheio! Limite: {LIMITE_ZOO}")
    if show_fav:
        with c2:
            if st.button("⭐" if not is_fav else "🌟", key=f"fav_{k}", use_container_width=True):
                if is_fav: st.session_state.favs.remove(an['id'])
                elif len(st.session_state.favs) < LIMITE_FAV: st.session_state.favs.add(an['id'])
                st.rerun()

# 6. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    st.success(f"👤 **{st.session_state.nome_zoologo}**\n\n🐾 **Zoo:** {len(st.session_state.zoo)}/{LIMITE_ZOO}\n⭐ **Favs:** {len(st.session_state.favs)}/{LIMITE_FAV}")
    aba = st.radio("Menu", [f"🌍 {T['paises']}", f"🌲 {T['florestas']}", f"🌊 {T['oceanos']}", f"🔬 {T['lab']}", f"⭐ {T['col']}", f"⚙️ {T['def']}"])

GRUPOS = ["Todos", "Mamíferos", "Aves", "Répteis", "Anfíbios", "Peixes", "Insetos"]

# 7. INTERFACE
if f"🔬 {T['lab']}" in aba:
    st.title(T['lab'])
    txt_lab = st.text_input("Pesquisar Animal:", value="Leão")
    if txt_lab:
        res = buscar(txt_lab, 70)
        for i, a in enumerate(res): card(a, f"lab_{i}")

elif f"🌍 {T['paises']}" in aba:
    st.title(T['paises'])
    p = st.selectbox("País:", ["Portugal", "Brasil", "Angola", "Moçambique", "Japão", "Austrália", "Canadá"])
    g = st.selectbox(T['grupo'], GRUPOS)
    q = p if g == "Todos" else f"{g} {p}"
    res = buscar(q, 70)
    for i, a in enumerate(res): card(a, f"p_{i}")

elif f"🌲 {T['florestas']}" in aba:
    st.title(T['florestas'])
    f = st.selectbox("Bioma:", ["Amazónia", "Taiga", "Savana", "Pantanal"])
    g = st.selectbox(T['grupo'], GRUPOS)
    res = buscar(f"{g} {f}", 70)
    for i, a in enumerate(res): card(a, f"f_{i}")

elif f"🌊 {T['oceanos']}" in aba:
    st.title(T['oceanos'])
    o = st.selectbox("Região:", ["Oceano Atlântico", "Oceano Pacífico", "Recife de Coral", "Mar Profundo"])
    g = st.selectbox(T['grupo'], GRUPOS)
    res = buscar(f"{g} {o}", 70)
    for i, a in enumerate(res): card(a, f"o_{i}")

elif f"⭐ {T['col']}" in aba:
    st.title(T['col'])
    for i, a in enumerate(st.session_state.zoo):
        card(a, f"col_{i}", "Libertar", show_fav=True)

elif f"⚙️ {T['def']}" in aba:
    st.title(T['def'])
    st.session_state.nome_zoologo = st.text_input("Nome:", value=st.session_state.nome_zoologo)
    st.session_state.codigo = st.text_input("Código Premium:", type="password")
    st.session_state.cor_card = st.selectbox("Cor Cartão:", list(cores_hex.keys()))
    st.session_state.cor_fundo = st.selectbox("Cor Fundo:", list(cores_hex.keys()))
    if st.button(T['guardar']): st.rerun()
