import streamlit as st
import requests

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="MundoVivo 🌍", layout="wide")

# 2. TRADUÇÃO COMPLETA
idiomas = {
    "Português": {"paises": "Países", "florestas": "Florestas", "oceanos": "Oceanos", "lab": "Laboratório", "col": "Coleção", "def": "Definições", "luta": "Lutar", "arena": "Arena de Luta", "guardar": "Guardar Alterações", "grupo": "Filtrar Grupo"},
    "English": {"paises": "Countries", "florestas": "Forests", "oceanos": "Oceans", "lab": "Laboratory", "col": "Collection", "def": "Settings", "luta": "Fight", "arena": "Fight Arena", "guardar": "Save Changes", "grupo": "Filter Group"},
    "Français": {"paises": "Pays", "florestas": "Forêts", "oceanos": "Océans", "lab": "Laboratoire", "col": "Collection", "def": "Paramètres", "luta": "Lutter", "arena": "Arène de Combat", "guardar": "Sauvegarder", "grupo": "Filtrer le Groupe"},
    "Español": {"paises": "Países", "florestas": "Bosques", "oceanos": "Océanos", "lab": "Laboratorio", "col": "Colección", "def": "Ajustes", "luta": "Luchar", "arena": "Arena de Lucha", "guardar": "Guardar", "grupo": "Filtrar Grupo"},
    "Deutsch": {"paises": "Länder", "florestas": "Wälder", "oceanos": "Ozeane", "lab": "Labor", "col": "Sammlung", "def": "Einstellungen", "luta": "Kämpfen", "arena": "Kampfarena", "guardar": "Speichern", "grupo": "Gruppe filtern"},
    "Russo (Русский)": {"paises": "Страны", "florestas": "Леса", "oceanos": "Океаны", "lab": "Лаборатория", "col": "Коллекция", "def": "Настройки", "luta": "Бой", "arena": "Боевая арена", "guardar": "Сохранить", "grupo": "Фильтр группы"},
    "Finlandês (Suomi)": {"paises": "Maat", "florestas": "Metsät", "oceanos": "Valtameret", "lab": "Laboratorio", "col": "Kokoelma", "def": "Asetukset", "luta": "Taistelu", "arena": "Taisteluareena", "guardar": "Tallenna", "grupo": "Suodata ryhmä"}
}

# 3. ESTADO DA APP
for key, val in {
    'luz': False, 'zoo': [], 'codigo': "", 'codigo_perm': "", 'arena_ativa': False,
    'cor_card': "Preto", 'cor_fundo': "Preto", 'idioma': "pt-PT", 'lang_label': "Português", 'nome_zoologo': "Explorador"
}.items():
    if key not in st.session_state: st.session_state[key] = val

T = idiomas[st.session_state.lang_label]
is_mestre = st.session_state.codigo == "6626" or st.session_state.codigo_perm == "67lucas62"
LIMITE = 80 if is_mestre else 20

# 4. DESIGN
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f", "Amarelo": "#f1c40f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23") if not st.session_state.luz else "#ffffff"
app_bg = cores_hex.get(st.session_state.cor_fundo, "#0b1117") if not st.session_state.luz else "#f0f2f6"
txt_color = "#000" if (st.session_state.luz or st.session_state.cor_card == "Branco") else "#fff"

st.markdown(f"""
<style>
    .stApp {{ background-color: {app_bg}; color: {txt_color}; }}
    .cc-card {{ background: {c_bg} !important; border-radius: 20px; padding: 20px; border-left: 15px solid gold; margin-bottom: 25px; border-right: 2px solid gold; box-shadow: 5px 5px 15px rgba(0,0,0,0.3); }}
    .premium-box {{ border: 2px dashed gold; padding: 15px; border-radius: 15px; background: rgba(255,215,0,0.1); text-align: center; }}
</style>
""", unsafe_allow_html=True)

# 5. FUNÇÕES
def buscar(q, n=12):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={q}&taxon_id=1&per_page={n}&locale={st.session_state.idioma}"
        r = requests.get(url).json()
        return [{'nome': x.get('preferred_common_name', x['name']).title(), 'sci': x['name'], 'foto': x['default_photo']['medium_url'] if x.get('default_photo') else "https://via.placeholder.com/400x300?text=Sem+Foto"} for x in r['results']]
    except: return []

def card(an, k, btn_txt="➕"):
    st.markdown(f"""
    <div class='cc-card'>
        <img src='{an['foto']}' style='width:100%; border-radius:15px; height:350px; object-fit:cover;'>
        <h2 style='margin-top:10px;'>{an['nome']}</h2>
        <p style='font-style:italic;'>{an['sci']}</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button(btn_txt, key=k, use_container_width=True):
        if "⚔️" in btn_txt: st.error(f"LUTANDO CONTRA: {an['nome']}!")
        elif len(st.session_state.zoo) < LIMITE: 
            st.session_state.zoo.append(an)
            st.toast(f"{an['nome']} Guardado!")

# 6. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    status = "🏆 Zoólogo Profissional" if is_mestre else "💳 Zoólogo"
    st.success(f"{status}\n\n👤 {st.session_state.nome_zoologo}\n\n🐾 {len(st.session_state.zoo)}/{LIMITE}")
    aba = st.radio("Menu", [f"🌍 {T['paises']}", f"🌲 {T['florestas']}", f"🌊 {T['oceanos']}", f"🔬 {T['lab']}", f"⭐ {T['col']}", f"⚙️ {T['def']}"])

GRUPOS = ["Todos", "Mamíferos", "Aves", "Répteis", "Anfíbios", "Peixes", "Insetos", "Aracnídeos"]

# 7. INTERFACE
if f"🔬 {T['lab']}" in aba:
    st.title(T['lab'])
    c1, c2 = st.columns([2.5, 1])
    with c1:
        if st.session_state.arena_ativa:
            st.subheader(f"🏟️ {T['arena']}")
            if st.button("⬅️ Sair da Arena"): st.session_state.arena_ativa = False; st.rerun()
            ca, cb = st.columns(2)
            for i, cx in enumerate([ca, cb]):
                with cx:
                    busca_ar = st.text_input(f"Oponente {i+1}:", key=f"ar_{i}")
                    if busca_ar:
                        res = buscar(busca_ar, 1)
                        if res: card(res[0], f"bt_ar_{i}", f"⚔️ {T['luta']}")
        else:
            txt_lab = st.text_input("Análise Livre:")
            if txt_lab:
                for i, a in enumerate(buscar(txt_lab)): card(a, f"lab_{i}")
    with c2:
        if is_mestre:
            st.markdown("<div class='premium-box'><h3>⭐ Premium Control</h3>", unsafe_allow_html=True)
            if st.button("🏟️ ENTRAR NA ARENA"): st.session_state.arena_ativa = True; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

elif f"🌍 {T['paises']}" in aba:
    st.title(T['paises'])
    p = st.selectbox("País:", ["Portugal", "Brasil", "Angola", "Moçambique", "Japão", "Austrália", "Canadá"])
    g = st.selectbox(T['grupo'], GRUPOS)
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/WorldMap.svg/800px-WorldMap.svg.png", caption="Mapa Geográfico Global", width=500)
    for i, a in enumerate(buscar(f"{g} em {p}")): card(a, f"p_{i}")

elif f"🌲 {T['florestas']}" in aba:
    st.title(T['florestas'])
    f = st.selectbox("Floresta:", ["Amazónia", "Taiga", "Savana", "Mata Atlântica"])
    g = st.selectbox(T['grupo'], GRUPOS)
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/World_map_biomes.png/800px-World_map_biomes.png", caption="Distribuição de Biomas", width=500)
    for i, a in enumerate(buscar(f"{g} na {f}")): card(a, f"f_{i}")

elif f"🌊 {T['oceanos']}" in aba:
    st.title(T['oceanos'])
    o = st.selectbox("Oceano:", ["Atlântico", "Pacífico", "Índico", "Recife de Coral", "Mar Profundo"])
    g = st.selectbox(T['grupo'], GRUPOS)
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/db/World_ocean_map.png/800px-World_ocean_map.png", caption="Mapa dos Oceanos", width=500)
    for i, a in enumerate(buscar(f"{g} no {o}")): card(a, f"o_{i}")

elif f"⚙️ {T['def']}" in aba:
    st.title(T['def'])
    st.session_state.nome_zoologo = st.text_input("Nome:", value=st.session_state.nome_zoologo)
    dic_lang = {"Português": "pt-PT", "English": "en-US", "Français": "fr", "Español": "es", "Deutsch": "de", "Russo (Русский)": "ru", "Finlandês (Suomi)": "fi"}
    escolha = st.selectbox("Idioma da App:", list(dic_lang.keys()), index=list(dic_lang.keys()).index(st.session_state.lang_label))
    st.session_state.idioma = dic_lang[escolha]
    st.session_state.lang_label = escolha
    st.session_state.codigo = st.text_input("Código Profissional:", type="password")
    st.session_state.codigo_perm = st.text_input("Código Permanente:", type="password")
    st.session_state.cor_card = st.selectbox("Cor:", list(cores_hex.keys()))
    if st.button(T['guardar']):
        st.balloons()
        st.rerun()

elif f"⭐ {T['col']}" in aba:
    st.title(T['col'])
    for i, a in enumerate(st.session_state.zoo): card(a, f"col_{i}", "Libertar")
