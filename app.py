import streamlit as st
import requests

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo 🌍", layout="wide")

# 2. TRADUÇÃO COMPLETA
idiomas = {
    "Português": {"paises": "Países", "florestas": "Florestas", "oceanos": "Oceanos", "lab": "Laboratório", "col": "Coleção", "def": "Definições", "luta": "Lutar", "arena": "Arena de Luta", "guardar": "Guardar Alterações", "fav": "Favoritos", "grupo": "Filtrar Grupo"},
    "English": {"paises": "Countries", "florestas": "Forests", "oceanos": "Oceans", "lab": "Laboratory", "col": "Collection", "def": "Settings", "luta": "Fight", "arena": "Fight Arena", "guardar": "Save Changes", "fav": "Favorites", "grupo": "Filter Group"},
    "Français": {"paises": "Pays", "florestas": "Forêts", "oceanos": "Océans", "lab": "Laboratoire", "col": "Collection", "def": "Paramètres", "luta": "Lutter", "arena": "Arène de Combat", "guardar": "Sauvegarder", "fav": "Favoris", "grupo": "Filtrer le Groupe"},
    "Español": {"paises": "Países", "florestas": "Bosques", "oceanos": "Océanos", "lab": "Laboratorio", "col": "Colección", "def": "Ajustes", "luta": "Luchar", "arena": "Arena de Lucha", "guardar": "Guardar", "fav": "Favoritos", "grupo": "Filtrar Grupo"},
    "Deutsch": {"paises": "Länder", "florestas": "Wälder", "oceanos": "Ozeane", "lab": "Labor", "col": "Sammlung", "def": "Einstellungen", "luta": "Kämpfen", "arena": "Kampfarena", "guardar": "Speichern", "fav": "Favoriten", "grupo": "Gruppe filtern"},
    "Russo (Русский)": {"paises": "Страны", "florestas": "Леса", "oceanos": "Океаны", "lab": "Лаборатория", "col": "Коллекция", "def": "Настройки", "luta": "Бой", "arena": "Боевая арена", "guardar": "Сохранить", "fav": "Избранное", "grupo": "Фильтр группы"},
    "Finlandês (Suomi)": {"paises": "Maat", "florestas": "Metsät", "oceanos": "Valtameret", "lab": "Laboratorio", "col": "Kokoelma", "def": "Asetukset", "luta": "Taistelu", "arena": "Taisteluareena", "guardar": "Tallenna", "fav": "Suosikit", "grupo": "Suodata ryhmä"}
}

# 3. ESTADO DA APP
if 'zoo' not in st.session_state: st.session_state.zoo = []
if 'favs' not in st.session_state: st.session_state.favs = set()

for key, val in {
    'luz': False, 'codigo': "", 'codigo_perm': "", 'arena_ativa': False,
    'cor_card': "Preto", 'cor_fundo': "Preto", 'idioma': "pt-PT", 'lang_label': "Português", 'nome_zoologo': "Explorador"
}.items():
    if key not in st.session_state: st.session_state[key] = val

T = idiomas[st.session_state.lang_label]
is_mestre = st.session_state.codigo == "6626" or st.session_state.codigo_perm == "67lucas62"

# --- LIMITES DO ZOO ---
LIMITE_ZOO = 80 if is_mestre else 20
LIMITE_FAV = 40 if is_mestre else 10 

# 4. DESIGN (CSS)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f", "Amarelo": "#f1c40f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23") if not st.session_state.luz else "#ffffff"
app_bg = cores_hex.get(st.session_state.cor_fundo, "#0b1117") if not st.session_state.luz else "#f0f2f6"
txt_color = "#000" if (st.session_state.luz or st.session_state.cor_card == "Branco") else "#fff"

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; color: {txt_color}; }}
    .cc-card {{ background: {c_bg} !important; border-radius: 20px; padding: 25px; border-left: 15px solid gold; margin-bottom: 30px; border-right: 2px solid gold; box-shadow: 8px 8px 20px rgba(0,0,0,0.4); }}
    .fav-card {{ border: 6px solid #FFD700 !important; box-shadow: 0px 0px 30px #FFD700 !important; }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÕES DE BUSCA (Ajustado para 70)
def buscar(q, n=70):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page={n}&locale={st.session_state.idioma}"
        r = requests.get(url).json()
        return [{'id': x['id'], 'nome': x.get('preferred_common_name', x['name']).title(), 'sci': x['name'], 'foto': x['default_photo']['medium_url'] if x.get('default_photo') else "https://via.placeholder.com/600x450?text=Sem+Foto"} for x in r['results']]
    except: return []

def card(an, k, btn_txt="➕", show_fav=False):
    is_fav = an['id'] in st.session_state.favs
    fav_class = "fav-card" if is_fav else ""
    
    st.markdown(f"""
    <div class='cc-card {fav_class}'>
        <img src='{an['foto']}' style='width:100%; border-radius:15px; height:450px; object-fit:cover;'>
        <h1 style='margin-top:15px; font-size: 2.5em;'>{"⭐ " if is_fav else ""}{an['nome']}</h1>
        <p style='font-style:italic; font-size: 1.3em; opacity: 0.8;'>{an['sci']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(btn_txt, key=f"btn_{k}", use_container_width=True):
            if "Libertar" in btn_txt:
                st.session_state.zoo = [x for x in st.session_state.zoo if x['id'] != an['id']]
                if an['id'] in st.session_state.favs: st.session_state.favs.remove(an['id'])
                st.rerun()
            elif len(st.session_state.zoo) < LIMITE_ZOO:
                if not any(x['id'] == an['id'] for x in st.session_state.zoo):
                    st.session_state.zoo.append(an)
                    st.toast(f"{an['nome']} capturado!")
            else: st.error(f"Zoo cheio! ({LIMITE_ZOO})")
    
    if show_fav:
        with col_b:
            if st.button("⭐ Fav" if not is_fav else "🌟 Remover", key=f"fav_{k}", use_container_width=True):
                if is_fav: st.session_state.favs.remove(an['id'])
                elif len(st.session_state.favs) < LIMITE_FAV: st.session_state.favs.add(an['id'])
                else: st.error(f"Limite Fav: {LIMITE_FAV}")
                st.rerun()

# 6. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    status = "🏆 Mestre" if is_mestre else "💳 Zoólogo"
    st.success(f"👤 **{st.session_state.nome_zoologo}**\n\n🐾 **Zoo:** {len(st.session_state.zoo)}/{LIMITE_ZOO}\n⭐ **Favs:** {len(st.session_state.favs)}/{LIMITE_FAV}")
    aba = st.radio("Menu", [f"🌍 {T['paises']}", f"🌲 {T['florestas']}", f"🌊 {T['oceanos']}", f"🔬 {T['lab']}", f"⭐ {T['col']}", f"⚙️ {T['def']}"])

# 7. INTERFACE (70 Resultados)
if f"🔬 {T['lab']}" in aba:
    st.title(T['lab'])
    txt_lab = st.text_input("Procurar (70 animais):")
    if txt_lab:
        for i, a in enumerate(buscar(txt_lab, 70)): card(a, f"lab_{i}")

elif f"🌍 {T['paises']}" in aba:
    st.title(T['paises'])
    p = st.selectbox("País:", ["Portugal", "Brasil", "Angola", "Moçambique", "Japão", "Austrália"])
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/WorldMap.svg/1000px-WorldMap.svg.png")
    for i, a in enumerate(buscar(f"Animais de {p}", 70)): card(a, f"p_{i}")

elif f"🌲 {T['florestas']}" in aba:
    st.title(T['florestas'])
    f = st.selectbox("Bioma:", ["Amazónia", "Taiga", "Savana"])
    
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/World_map_biomes.png/1000px-World_map_biomes.png")
    for i, a in enumerate(buscar(f"Animais na {f}", 70)): card(a, f"f_{i}")

elif f"🌊 {T['oceanos']}" in aba:
    st.title(T['oceanos'])
    o = st.selectbox("Oceano:", ["Atlântico", "Pacífico", "Índico"])
    

[Image of world map showing ocean basins]

    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/db/World_ocean_map.png/1000px-World_ocean_map.png")
    for i, a in enumerate(buscar(f"Animais no {o}", 70)): card(a, f"o_{i}")

elif f"⭐ {T['col']}" in aba:
    st.title(T['col'])
    zoo_ordenado = sorted(st.session_state.zoo, key=lambda x: x['id'] in st.session_state.favs, reverse=True)
    for i, a in enumerate(zoo_ordenado): card(a, f"col_{i}", "Libertar Animal", show_fav=True)

elif f"⚙️ {T['def']}" in aba:
    st.title(T['def'])
    st.session_state.nome_zoologo = st.text_input("Nome:", value=st.session_state.nome_zoologo)
    st.session_state.codigo = st.text_input("Código Premium:", type="password")
    if st.button(T['guardar']): st.balloons(); st.rerun()
