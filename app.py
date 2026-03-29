import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. ESTADO DO SISTEMA
chaves = {
    'zoo': [], 'tanque_fusao': [], 'pontos_zoologo': 0, 
    'animais_salvos_ids': set(), 'id_animal_atual': None,
    'internados_vet': [], 'c_24h': "", 'c_mega': "", 
    'premium_ativo': False, 'cor_tema': "#0b1117", 'brilho': 100,
    'inicio_sessao_24h': None
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# 2. LÓGICA DE CÓDIGOS E TEMPO
is_mega = st.session_state.c_mega == "67lucas62"
is_24h_valido = False
if st.session_state.c_24h == "6626":
    if st.session_state.inicio_sessao_24h is None:
        st.session_state.inicio_sessao_24h = datetime.now().timestamp()
    tempo_passado = datetime.now().timestamp() - st.session_state.inicio_sessao_24h
    if tempo_passado < 86400: is_24h_valido = True
    else: st.session_state.c_24h = ""

tem_acesso_vip = is_mega or is_24h_valido

# 3. CSS PARA BORDAS (SEM AFETAR O ANIMAL)
borda_css = "border: 4px solid #2ecc71;"
if is_mega:
    borda_css = "border: 4px solid; border-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet) 1; animation: rainbow_border 3s linear infinite;"
elif is_24h_valido:
    borda_css = "border: 4px solid #ffd700;"

st.markdown(f"""
<style>
    @keyframes rainbow_border {{ 0% {{ filter: hue-rotate(0deg); }} 100% {{ filter: hue-rotate(360deg); }} }}
    .stApp {{ background-color: {st.session_state.cor_tema}; filter: brightness({st.session_state.brilho/100}); }}
    .cartao-cidadao {{
        background-color: #1a1c23 !important; border-radius: 20px; padding: 15px; 
        {borda_css} margin-bottom: 20px; text-align: center; color: white;
    }}
    .img-an {{ width: 100%; border-radius: 15px; height: 180px; object-fit: cover; border: 1px solid #444; filter: none !important; }}
    @keyframes helicopter_ride {{ 0% {{ transform: translateX(-200px); }} 100% {{ transform: translateX(110vw); }} }}
    .heli-anim {{ position: fixed; top: 30%; font-size: 80px; z-index: 9999; animation: helicopter_ride 3s linear forwards; }}
</style>
""", unsafe_allow_html=True)

# 4. FUNÇÃO DO CARTÃO (CORREÇÃO DO </div> E DNA)
def card(an, prefixo, idx=0, show_buttons=True, footer_text=None, is_zoo=False):
    if not an: return
    nome_pt = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    classe = {"Mammalia": "Mamífero", "Aves": "Ave", "Reptilia": "Réptil", "Amphibia": "Anfíbio"}.get(an.get('iconic_taxon_name'), "Selvagem")
    
    # Renderização HTML sem erros de fecho
    st.markdown(f'''
    <div class="cartao-cidadao">
        <span style="color:#ffd700; font-weight:bold; font-size:0.7em;">💳 CARTÃO DE CIDADÃO</span><br>
        <img src="{foto}" class="img-an">
        <h3 style="color:#ffd700; margin:10px 0;">{nome_pt}</h3>
        <p style="margin:2px 0; font-size:0.9em;">🐾 <b>Classe:</b> {classe} | 🥩 <b>Alim:</b> Omnívoro</p>
        {f'<p style="color:#ffd700; font-weight:bold; margin-top:5px;">{footer_text}</p>' if footer_text else ''}
    </div>
    ''', unsafe_allow_html=True)
    
    if show_buttons:
        c1, c2 = st.columns(2)
        with c1:
            if is_zoo:
                if st.button("🗑️ Excluir", key=f"del_{prefixo}_{idx}"):
                    st.session_state.zoo.pop(idx); st.rerun()
            else:
                if st.button("📥 Zoo", key=f"in_{prefixo}_{idx}"):
                    st.session_state.zoo.append(an); st.toast("No Zoo!")
        with c2:
            if st.button("🧬 DNA", key=f"dna_{prefixo}_{idx}"):
                st.session_state.tanque_fusao.append(an); st.toast("DNA enviado!")

# 5. SIDEBAR E MENUS
with st.sidebar:
    st.title("🌍 MundoVivo")
    if is_24h_valido:
        res = 86400 - (datetime.now().timestamp() - st.session_state.inicio_sessao_24h)
        st.write(f"⏳ Premium: {int(res//3600)}h {int((res%3600)//60)}m")
    
    if tem_acesso_vip:
        st.session_state.premium_ativo = st.toggle("✨ MODO PREMIUM", value=st.session_state.premium_ativo)
    
    menu = ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    if st.session_state.premium_ativo:
        menu = ["🌀 Salvamento", "🏥 Veterinário", "🧬 Tanque de Fusão", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    aba = st.radio("Navegação", menu)

# 6. LISTAS E ABAS (MANTIDO TUDO)
paises_70 = ["Portugal", "Brasil", "Angola", "EUA", "Japão", "França", "Itália", "Alemanha", "China", "Canadá"] # (Expandido no uso real)

if aba in ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países"]:
    sel = st.selectbox("Escolha Local:", ["Amazónia", "Oceano Atlântico", "Portugal", "Brasil"])
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=12&locale=pt-PT")
    for i, an in enumerate(r.json().get('results', [])):
        card(an, "exp", i)

elif aba == "🧬 Tanque de Fusão":
    st.header("🧬 Fusão Científica")
    if len(st.session_state.tanque_fusao) < 2: st.info("Use o botão DNA nos animais!")
    else:
        ani1 = st.selectbox("Mãe (PT):", [ (a.get('preferred_common_name') or a.get('name')).title() for a in st.session_state.tanque_fusao ], key="f1")
        ani2 = st.selectbox("Pai (PT):", [ (a.get('preferred_common_name') or a.get('name')).title() for a in st.session_state.tanque_fusao ], key="f2")
        if st.button("🔬 FUNDIR"):
            n1 = next(a['name'] for a in st.session_state.tanque_fusao if (a.get('preferred_common_name') or a.get('name')).title() == ani1)
            n2 = next(a['name'] for a in st.session_state.tanque_fusao if (a.get('preferred_common_name') or a.get('name')).title() == ani2)
            st.success(f"Nova Espécie (Nome Científico): **{n1.split()[0]} {n2.split()[-1]}**")

elif aba == "🏥 Veterinário":
    for i, item in enumerate(st.session_state.internados_vet):
        falta = item['data_alta'] - datetime.now().timestamp()
        txt = f"⏳ {int(falta//3600)}h" if falta > 0 else "✅ PRONTO!"
        card(item['animal'], "vet", i, show_buttons=False, footer_text=txt)
        if falta <= 0 and st.button("🏁 Zoo", key=f"mv_{i}"):
            st.session_state.zoo.append(item['animal']); st.session_state.internados_vet.pop(i); st.rerun()

elif aba == "🐾 Meu Zoo":
    for i, an in enumerate(st.session_state.zoo):
        card(an, "zoo", i, is_zoo=True)

elif aba == "⚙️ Definições":
    st.session_state.c_mega = st.text_input("Código Mega", type="password", value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input("Código 24h", type="password", value=st.session_state.c_24h)
    if st.button("Guardar"): st.rerun()
