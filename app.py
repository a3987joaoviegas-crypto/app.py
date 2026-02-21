import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO BÁSICA
st.set_page_config(page_title="MundoVivo 🌍", page_icon="🌍", layout="wide")

# 2. DICIONÁRIO DE TRADUÇÃO COMPLETO
idiomas = {
    "Português": {"paises": "Países", "florestas": "Florestas", "oceanos": "Oceanos", "lab": "Laboratório", "col": "Coleção", "def": "Definições", "luta": "Lutar", "arena": "Arena de Luta", "guardar": "Guardar Alterações", "grupo": "Filtrar Grupo"},
    "English": {"paises": "Countries", "florestas": "Forests", "oceanos": "Oceans", "lab": "Laboratory", "col": "Collection", "def": "Settings", "luta": "Fight", "arena": "Fight Arena", "guardar": "Save Changes", "grupo": "Filter Group"},
    "Français": {"paises": "Pays", "florestas": "Forêts", "oceanos": "Océans", "lab": "Laboratoire", "col": "Collection", "def": "Paramètres", "luta": "Lutter", "arena": "Arène de Combat", "guardar": "Sauvegarder", "grupo": "Filtrer le Groupe"},
    "Español": {"paises": "Países", "florestas": "Bosques", "oceanos": "Océanos", "lab": "Laboratorio", "col": "Colección", "def": "Ajustes", "luta": "Luchar", "arena": "Arena de Lucha", "guardar": "Guardar", "grupo": "Filtrar Grupo"},
    "Deutsch": {"paises": "Länder", "florestas": "Wälder", "oceanos": "Ozeane", "lab": "Labor", "col": "Sammlung", "def": "Einstellungen", "luta": "Kämpfen", "arena": "Kampfarena", "guardar": "Speichern", "grupo": "Gruppe filtern"},
    "Russo (Русский)": {"paises": "Страны", "florestas": "Леса", "oceanos": "Океаны", "lab": "Лаборатория", "col": "Коллекция", "def": "Настройки", "luta": "Бой", "arena": "Боевая арена", "guardar": "Сохранить", "grupo": "Фильтр группы"},
    "Finlandês (Suomi)": {"paises": "Maat", "florestas": "Metsät", "oceanos": "Valtameret", "lab": "Laboratorio", "col": "Kokoelma", "def": "Asetukset", "luta": "Taistelu", "arena": "Taisteluareena", "guardar": "Tallenna", "grupo": "Suodata ryhmä"}
}

# 3. SISTEMA DE MEMÓRIA
for key, val in {
    'luz': False, 'zoo': [], 'codigo': "", 'codigo_perm': "", 'arena_ativa': False,
    'cor_card': "Preto", 'cor_fundo': "Preto", 'idioma': "pt-PT", 'lang_label': "Português", 'nome_zoologo': "Explorador"
}.items():
    if key not in st.session_state: st.session_state[key] = val

T = idiomas[st.session_state.lang_label]
is_mestre = st.session_state.codigo == "6626" or st.session_state.codigo_perm == "67lucas62"
LIMITE = 80 if is_mestre else 20

# 4. DESIGN (CSS)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f", "Amarelo": "#f1c40f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23") if not st.session_state.luz else "#ffffff"
app_bg = cores_hex.get(st.session_state.cor_fundo, "#0b1117") if not st.session_state.luz else "#f0f2f6"
txt_color = "#000" if (st.session_state.luz or st.session_state.cor_card == "Branco") else "#fff"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {app_bg}; color: {txt_color}; }}
    .cc-card {{ background: {c_bg} !important; border-radius: 15px; padding: 20px; border-left: 15px solid gold; box-shadow: 10px 10px 20px rgba(0,0,0,0.5); margin-bottom: 25px; }}
    .premium-side {{ background: rgba(255, 215, 0, 0.1); border: 2px dashed gold; padding: 15px; border-radius: 15px; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# 5. FUNÇÕES
def buscar_api(termo, qtd=12):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={termo}&taxon_id=1&per_page={qtd}&locale={st.session_state.idioma}"
        r = requests.get(url).json()
        return [{'nome': i.get('preferred_common_name', i['name']).title(), 'sci': i['name'], 'foto': i['default_photo']['medium_url'] if i.get('default_photo') else "", 'id': i['id']} for i in r['results']]
    except: return []

def render_cartao(an, k, l_btn="➕"):
    st.markdown(f"""
    <div class='cc-card'>
        <img src='{an['foto']}' style='width:100%; border-radius:10px; height:280px; object-fit:cover;'>
        <h2 style='margin-bottom:0;'>{an['nome']}</h2>
        <p style='font-style:italic; opacity:0.8;'>{an['sci']}</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button(l_btn, key=k, use_container_width=True):
        if T['luta'] in l_btn or "⚔️" in l_btn: st.error(f"COMBATE: {an['nome']}!")
        elif len(st.session_state.zoo) < LIMITE:
            st.session_state.zoo.append(an)
            st.toast(f"{an['nome']} Guardado!")

# 6. SIDEBAR PRINCIPAL
with st.sidebar:
    st.title("🌍 MundoVivo")
    tit_zoo = "🏆 Zoólogo Profissional" if is_mestre else "💳 Zoólogo"
    st.markdown(f"<div style='background:#2ea043; padding:15px; border-radius:12px; color:white; border:2px solid gold;'><b>{tit_zoo}</b><br>{st.session_state.nome_zoologo}<br><small>{len(st.session_state.zoo)}/{LIMITE}</small></div>", unsafe_allow_html=True)
    st.markdown("---")
    aba = st.radio("Menu", [f"🌍 {T['paises']}", f"🌲 {T['florestas']}", f"🌊 {T['oceanos']}", f"🔬 {T['lab']}", f"⭐ {T['col']}", f"⚙️ {T['def']}"])

GRUPOS = ["Todos", "Mamíferos", "Aves", "Répteis", "Anfíbios", "Peixes", "Aracnídeos", "Insetos"]

# 7. INTERFACE
if f"🔬 {T['lab']}" in aba:
    st.title(f"🔬 {T['lab']}")
    col_pesq, col_prem = st.columns([2.2, 1])
    
    with col_pesq:
        if st.session_state.arena_ativa:
            st.subheader(f"🏟️ {T['arena']}")
            if st.button("⬅️ Sair da Arena"): st.session_state.arena_ativa = False; st.rerun()
            c1, c2 = st.columns(2)
            for i, c in enumerate([c1, c2]):
                with c:
                    txt = st.text_input(f"Oponente {i+1}:", key=f"fight_in_{i}")
                    if txt:
                        res = buscar_api(txt, 1)
                        if res: render_cartao(res[0], f"arena_btn_{i}", l_btn=f"⚔️ {T['luta']}")
        else:
            term = st.text_input("Pesquisa Biológica:")
            if term:
                res = buscar_api(term)
                for i, a in enumerate(res): render_cartao(a, f"lab_card_{i}")

    with col_prem:
        if is_mestre:
            st.markdown("<div class='premium-side'>", unsafe_allow_html=True)
            st.subheader("⭐ Premium Area")
            if st.button("🏟️ ENTRAR NA ARENA"): st.session_state.arena_ativa = True; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

elif f"🌍 {T['paises']}" in aba:
    st.title(T['paises'])
    p = st.selectbox("Escolha o País:", ["Portugal", "Brasil", "Angola", "Moçambique", "Japão", "Austrália"])
    g = st.selectbox(T['grupo'], GRUPOS, key="g_p")
    for i, a in enumerate(buscar_api(f"Animais {g} de {p}")): render_cartao(a, f"p_c_{i}")

elif f"🌲 {T['florestas']}" in aba:
    st.title(T['florestas'])
    f = st.selectbox("Bioma:", ["Amazónia", "Taiga", "Savana", "Mata Atlântica"])
    g = st.selectbox(T['grupo'], GRUPOS, key="g_f")
    for i, a in enumerate(buscar_api(f"Animais {g} da {f}")): render_cartao(a, f"f_c_{i}")

elif f"🌊 {T['oceanos']}" in aba:
    st.title(T['oceanos'])
    o = st.selectbox("Região Marinha:", ["Oceano Atlântico", "Recife de Coral", "Mar Profundo"])
    g = st.selectbox(T['grupo'], GRUPOS, key="g_o")
    for i, a in enumerate(buscar_api(f"Animais {g} do {o}")): render_cartao(a, f"o_c_{i}")

elif f"⚙️ {T['def']}" in aba:
    st.title(T['def'])
    st.session_state.nome_zoologo = st.text_input("Nome do Zoólogo:", value=st.session_state.nome_zoologo)
    
    idiomas_dict = {"Português": "pt-PT", "English": "en-US", "Français": "fr", "Español": "es", "Deutsch": "de", "Russo (Русский)": "ru", "Finlandês (Suomi)": "fi"}
    escolha = st.selectbox("🌐 Idioma Principal:", list(idiomas_dict.keys()), index=list(idiomas_dict.keys()).index(st.session_state.lang_label))
    st.session_state.idioma = idiomas_dict[escolha]
    st.session_state.lang_label = escolha

    st.markdown("---")
    st.session_state.codigo = st.text_input("Código Premium:", type="password")
    st.session_state.codigo_perm = st.text_input("Código Permanente:", type="password")
    st.session_state.cor_card = st.selectbox("Cor dos Cartões:", list(cores_hex.keys()))
    st.session_state.luz = st.toggle("Modo Dia")
    
    if st.button(f"💾 {T['guardar']}"):
        st.balloons()
        st.rerun()

elif f"⭐ {T['col']}" in aba:
    st.title(T['col'])
    for i, a in enumerate(st.session_state.zoo):
        st.markdown(f"<div class='cc-card'><h2>{a['nome']}</h2></div>", unsafe_allow_html=True)
        if st.button(f"Libertar", key=f"rel_{i}"): st.session_state.zoo.pop(i); st.rerun()
