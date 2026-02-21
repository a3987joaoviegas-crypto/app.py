import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO BÁSICA
st.set_page_config(page_title="MundoVivo 🌍", page_icon="🌍", layout="wide")

# 2. SISTEMA DE MEMÓRIA E TRADUÇÃO
idiomas = {
    "Português": {"paises": "Países", "florestas": "Florestas", "oceanos": "Oceanos", "lab": "Laboratório", "col": "Coleção", "def": "Definições", "luta": "Lutar", "arena": "Arena de Luta"},
    "English": {"paises": "Countries", "florestas": "Forests", "oceanos": "Oceans", "lab": "Laboratory", "col": "Collection", "def": "Settings", "luta": "Fight", "arena": "Fight Arena"},
    "Français": {"paises": "Pays", "florestas": "Forêts", "oceanos": "Océans", "lab": "Laboratoire", "col": "Collection", "def": "Paramètres", "luta": "Lutter", "arena": "Arène de Combat"},
    "Español": {"paises": "Países", "florestas": "Bosques", "oceanos": "Océanos", "lab": "Laboratorio", "col": "Colección", "def": "Ajustes", "luta": "Luchar", "arena": "Arena de Lucha"},
    "Deutsch": {"paises": "Länder", "florestas": "Wälder", "oceanos": "Ozeane", "lab": "Labor", "col": "Sammlung", "def": "Einstellungen", "luta": "Kämpfen", "arena": "Kampfarena"},
    "Russo (Русский)": {"paises": "Страны", "florestas": "Леса", "oceanos": "Океаны", "lab": "Лаборатория", "col": "Коллекция", "def": "Настройки", "luta": "Бой", "arena": "Боевая арена"},
    "Finlandês (Suomi)": {"paises": "Maat", "florestas": "Metsät", "oceanos": "Valtameret", "lab": "Laboratorio", "col": "Kokoelma", "def": "Asetukset", "luta": "Taistelu", "arena": "Taisteluareena"}
}

for key, val in {
    'luz': False, 'zoo': [], 'codigo': "", 'codigo_perm': "", 'arena_ativa': False,
    'cor_card': "Preto", 'cor_fundo': "Preto", 'idioma': "pt-PT", 'lang_label': "Português", 'nome_zoologo': "Explorador"
}.items():
    if key not in st.session_state: st.session_state[key] = val

T = idiomas[st.session_state.lang_label]
is_mestre = st.session_state.codigo == "6626" or st.session_state.codigo_perm == "67lucas62"
LIMITE = 80 if is_mestre else 20

# 3. DESIGN (CSS)
cores_hex = {"Preto": "#1a1c23", "Branco": "#ffffff", "Verde": "#002b1b", "Azul": "#001f3f", "Amarelo": "#f1c40f"}
c_bg = cores_hex.get(st.session_state.cor_card, "#1a1c23") if not st.session_state.luz else "#ffffff"
app_bg = cores_hex.get(st.session_state.cor_fundo, "#0b1117") if not st.session_state.luz else "#f0f2f6"
txt_color = "#000" if (st.session_state.luz or st.session_state.cor_card == "Branco") else "#fff"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {app_bg}; color: {txt_color}; }}
    .cc-card {{ background: {c_bg} !important; border-radius: 15px; padding: 18px; border-left: 15px solid gold; margin-bottom: 20px; color: {txt_color} !important; }}
    .premium-side {{ background: rgba(255, 215, 0, 0.1); border-left: 3px solid gold; padding: 15px; border-radius: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# 4. FUNÇÕES
def buscar_api(termo, qtd=9):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={termo}&taxon_id=1&per_page={qtd}&locale={st.session_state.idioma}"
        r = requests.get(url).json()
        return [{'nome': i.get('preferred_common_name', i['name']).title(), 'sci': i['name'], 'foto': i['default_photo']['medium_url'] if i.get('default_photo') else "", 'id': i['id']} for i in r['results']]
    except: return []

def render_cartao(an, k, l_btn="➕"):
    st.markdown(f"<div class='cc-card'><img src='{an['foto']}' width='100%' style='border-radius:10px; height:180px; object-fit:cover;'><div style='font-size:1.2em; font-weight:bold;'>{an['nome']}</div><div style='font-style:italic; opacity:0.7;'>{an['sci']}</div></div>", unsafe_allow_html=True)
    if st.button(l_btn, key=k, use_container_width=True):
        if "Lutar" in l_btn or "Fight" in l_btn: st.error("Iniciando Combate!")
        elif len(st.session_state.zoo) < LIMITE: st.session_state.zoo.append(an); st.toast("Guardado!")

# 5. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    tit_zoo = "🏆 Zoólogo Profissional" if is_mestre else "💳 Zoólogo"
    st.markdown(f"<div style='background:#2ea043; padding:10px; border-radius:10px; color:white;'><b>{tit_zoo}</b><br>{st.session_state.nome_zoologo}</div>", unsafe_allow_html=True)
    st.markdown("---")
    aba = st.radio("Menu", [f"🌍 {T['paises']}", f"🌲 {T['florestas']}", f"🌊 {T['oceanos']}", f"🔬 {T['lab']}", f"⭐ {T['col']}", f"⚙️ {T['def']}"])

# 6. INTERFACE
GRUPOS = ["Todos", "Mamíferos", "Aves", "Répteis", "Anfíbios", "Peixes"]

if f"🔬 {T['lab']}" in aba:
    st.title(f"🔬 {T['lab']}")
    col_pesq, col_prem = st.columns([2, 1])
    
    with col_pesq:
        if st.session_state.arena_ativa:
            st.subheader(T['arena'])
            if st.button("⬅️ Sair da Arena"): st.session_state.arena_ativa = False; st.rerun()
            c1, c2 = st.columns(2)
            for i, c in enumerate([c1, c2]):
                with c:
                    t = st.text_input(f"Oponente {i+1}:", key=f"op_{i}")
                    if t:
                        res = buscar_api(t, 1)
                        if res: render_cartao(res[0], f"bt_l_{i}", l_btn=T['luta'])
        else:
            term = st.text_input("Pesquisa Livre:")
            if term:
                res = buscar_api(term)
                cols = st.columns(2)
                for i, a in enumerate(res):
                    with cols[i%2]: render_cartao(a, f"lab_{i}")

    with col_prem:
        if is_mestre:
            st.markdown("<div class='premium-side'>", unsafe_allow_html=True)
            st.subheader("⭐ Premium")
            if st.button("🏟️ Entrar na Arena"): st.session_state.arena_ativa = True; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

elif f"⚙️ {T['def']}" in aba:
    st.title(T['def'])
    st.session_state.nome_zoologo = st.text_input("Nome:", value=st.session_state.nome_zoologo)
    
    idiomas_dict = {"Português": "pt-PT", "English": "en-US", "Français": "fr", "Español": "es", "Deutsch": "de", "Russo (Русский)": "ru", "Finlandês (Suomi)": "fi"}
    escolha = st.selectbox("🌐 Idioma:", list(idiomas_dict.keys()), index=list(idiomas_dict.keys()).index(st.session_state.lang_label))
    st.session_state.idioma = idiomas_dict[escolha]
    st.session_state.lang_label = escolha

    st.session_state.codigo = st.text_input("Código:", type="password")
    st.session_state.codigo_perm = st.text_input("Código Perm:", type="password")
    st.session_state.cor_card = st.selectbox("Cor:", list(cores_hex.keys()))
    st.session_state.luz = st.toggle("Modo Dia")
    
    if st.button("💾 Guardar Alterações"):
        st.balloons()
        st.rerun()

elif f"🌍 {T['paises']}" in aba:
    p = st.selectbox("País:", ["Portugal", "Brasil", "Angola", "Moçambique", "Japão"])
    g = st.selectbox("Grupo:", GRUPOS)
    for i, a in enumerate(buscar_api(f"Animais {g} de {p}")):
        render_cartao(a, f"p_{i}")

elif f"🌲 {T['florestas']}" in aba:
    f = st.selectbox("Floresta:", ["Amazónia", "Taiga", "Savana"])
    g = st.selectbox("Grupo:", GRUPOS)
    for i, a in enumerate(buscar_api(f"Animais {g} da {f}")):
        render_cartao(a, f"f_{i}")

elif f"🌊 {T['oceanos']}" in aba:
    o = st.selectbox("Oceano:", ["Atlântico", "Pacífico", "Recife"])
    g = st.selectbox("Grupo:", GRUPOS)
    for i, a in enumerate(buscar_api(f"Animais {g} do {o}")):
        render_cartao(a, f"o_{i}")

elif f"⭐ {T['col']}" in aba:
    for i, a in enumerate(st.session_state.zoo):
        st.write(f"⭐ {a['nome']}")
        if st.button("Libertar", key=f"lib_{i}"): st.session_state.zoo.pop(i); st.rerun()
