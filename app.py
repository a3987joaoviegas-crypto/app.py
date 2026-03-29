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

# 3. CSS DINÂMICO (CORREÇÃO: APENAS A BORDA MUDA DE COR)
borda_css = "border: 4px solid #2ecc71;" # Padrão Verde
if is_mega:
    borda_css = """
        border: 4px solid;
        border-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet) 1;
        animation: rainbow_border 3s linear infinite;
    """
elif is_24h_valido:
    borda_css = "border: 4px solid #ffd700;" # Dourado Fixo

st.markdown(f"""
<style>
    @keyframes rainbow_border {{
        0% {{ filter: hue-rotate(0deg); }}
        100% {{ filter: hue-rotate(360deg); }}
    }}
    .stApp {{ background-color: {st.session_state.cor_tema}; filter: brightness({st.session_state.brilho/100}); }}
    .cartao-cidadao {{
        background-color: #1a1c23 !important; 
        border-radius: 25px; 
        padding: 15px; 
        {borda_css}
        margin-bottom: 20px; 
        text-align: center; 
        color: white; 
        opacity: 1 !important;
    }}
    .img-an {{ width: 100%; border-radius: 20px; height: 180px; object-fit: cover; border: 1px solid #444; filter: none !important; }}
    @keyframes helicopter_ride {{ 0% {{ transform: translateX(-200px); }} 100% {{ transform: translateX(110vw); }} }}
    .heli-anim {{ position: fixed; top: 30%; font-size: 80px; z-index: 9999; animation: helicopter_ride 3s linear forwards; }}
</style>
""", unsafe_allow_html=True)

# 4. FUNÇÕES AUXILIARES
def traduzir_classe(taxon_name):
    trad = {"Mammalia": "Mamífero", "Aves": "Ave", "Reptilia": "Réptil", "Amphibia": "Anfíbio", "Actinopterygii": "Peixe", "Arachnida": "Aracnídeo", "Insecta": "Inseto", "Mollusca": "Molusco"}
    return trad.get(taxon_name, "Espécie Selvagem")

def card(an, prefixo, idx=0, show_buttons=True, footer_text=None, is_zoo=False):
    if not an: return
    nome = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    classe = traduzir_classe(an.get('iconic_taxon_name'))
    alim = random.choice(['Herbívoro', 'Carnívoro', 'Omnívoro'])
    
    st.markdown(f"""<div class="cartao-cidadao">
        <span style="color:#ffd700; font-weight:bold; font-size:0.7em;">💳 CARTÃO DE CIDADÃO</span><br>
        <img src="{foto}" class="img-an">
        <h3 style="color:#ffd700; margin:10px 0;">{nome}</h3>
        <p style="margin:2px 0;">🐾 <b>Classe:</b> {classe} | 🥚 <b>Repro:</b> {"Vivíparo" if classe=="Mamífero" else "Ovíparo"}</p>
        <p style="margin:2px 0;">🥩 <b>Alimentação:</b> {alim}</p>
        {f'<p style="color:#ffd700; font-weight:bold; margin-top:5px;">{footer_text}</p>' if footer_text else ''}
    </div>""", unsafe_allow_html=True)
    
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
                st.session_state.tanque_fusao.append(an); st.toast("DNA Coletado!")

# 5. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    if is_24h_valido:
        res = 86400 - (datetime.now().timestamp() - st.session_state.inicio_sessao_24h)
        st.write(f"⏳ Premium: {int(res//3600)}h {int((res%3600)//60)}m")
    
    st.markdown(f"""<div style="background:#1a1c23; padding:10px; border-radius:15px; border:2px solid #ffd700; text-align:center;">
        <b>{st.session_state.pontos_zoologo} PTS</b><br><small>Recruta</small></div>""", unsafe_allow_html=True)
    
    if tem_acesso_vip:
        st.session_state.premium_ativo = st.toggle("✨ MODO PREMIUM", value=st.session_state.premium_ativo)
    
    menu = ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    if st.session_state.premium_ativo:
        menu = ["🌀 Salvamento", "🏥 Veterinário", "🧬 Tanque de Fusão", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    aba = st.radio("Navegação", menu)

# 6. LISTAS
florestas = ["Amazónia", "Congo", "Taiga", "Daintree", "Floresta Negra", "Mata Atlântica", "Bornéu", "Monteverde", "Tongass", "Bialowieza"]
oceanos = ["Oceano Pacífico", "Oceano Atlântico", "Oceano Índico", "Oceano Ártico", "Oceano Antártico", "Mar Mediterrâneo", "Mar Vermelho", "Mar das Caraíbas", "Mar de Coral", "Mar Morto"]
paises = ["Portugal", "Brasil", "Angola", "Moçambique", "Espanha", "França", "Itália", "Alemanha", "EUA", "Japão", "China", "Índia", "Austrália", "Canadá", "México", "Argentina", "Chile", "Egito", "África do Sul", "Rússia", "Reino Unido", "Coreia do Sul", "Tailândia", "Grécia", "Turquia", "Noruega", "Suécia", "Holanda", "Suíça", "Israel", "Arábia Saudita", "Vietname", "Indonésia", "Filipinas", "Colômbia", "Peru", "Polónia", "Ucrânia", "Bélgica", "Áustria", "Irlanda", "Islândia", "Cuba", "Uruguai", "Marrocos", "Nigéria", "Quénia", "Nova Zelândia", "Dinamarca", "Finlândia", "Singapura", "Malásia", "Equador", "Venezuela", "Paraguai", "Bolívia", "Panamá", "Costa Rica", "Honduras", "Guatemala", "Jamaica", "Senegal", "Gana", "Irão", "Iraque", "EAU", "Cabo Verde", "Paquistão", "Bangladesh", "Mali"]

# 7. ABAS
if aba in ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países"]:
    lista = florestas if aba == "🌲 Florestas" else oceanos if aba == "🌊 Oceanos" else sorted(paises)
    sel = st.selectbox("Escolha Localização:", lista)
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=70&locale=pt-PT")
    ans = r.json().get('results', [])
    for i in range(0, len(ans), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(ans):
                with cols[j]: card(ans[i+j], "exp", i+j)

elif aba == "🌀 Salvamento":
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/World_map_-_low_resolution.svg/1000px-World_map_-_low_resolution.svg.png")
    if not st.session_state.id_animal_atual:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={random.choice(['Africa','Amazon'])}&taxon_id=1&per_page=1&locale=pt-PT")
        if r.json()['results']: st.session_state.id_animal_atual = r.json()['results'][0]
    if st.session_state.id_animal_atual:
        card(st.session_state.id_animal_atual, "res", 0, show_buttons=False)
        if st.button("🚁 ENVIAR HELICÓPTERO"):
            st.markdown('<div class="heli-anim">🚁</div>', unsafe_allow_html=True)
            time.sleep(3)
            st.session_state.pontos_zoologo += 50
            st.session_state.internados_vet.append({'animal': st.session_state.id_animal_atual, 'data_alta': (datetime.now() + timedelta(hours=24)).timestamp()})
            st.session_state.id_animal_atual = None; st.rerun()

elif aba == "🏥 Veterinário":
    st.header("🏥 Hospital Veterinário")
    if not st.session_state.internados_vet: st.info("Vazio.")
    for i, item in enumerate(st.session_state.internados_vet):
        falta = item['data_alta'] - datetime.now().timestamp()
        txt = f"⏳ {int(falta//3600)}h {int((falta%3600)//60)}m" if falta > 0 else "✅ PRONTO!"
        card(item['animal'], "vet", i, show_buttons=False, footer_text=txt)
        if falta <= 0:
            if st.button("🏁 Mover para Zoo", key=f"mv_{i}"):
                st.session_state.zoo.append(item['animal']); st.session_state.internados_vet.pop(i); st.rerun()

elif aba == "🧬 Tanque de Fusão":
    st.header("🧬 Fusão Científica")
    if len(st.session_state.tanque_fusao) < 2: st.info("Use o botão DNA nos animais primeiro!")
    else:
        ani1 = st.selectbox("Mãe:", [a.get('preferred_common_name', a.get('name')) for a in st.session_state.tanque_fusao], key="f1")
        ani2 = st.selectbox("Pai:", [a.get('preferred_common_name', a.get('name')) for a in st.session_state.tanque_fusao], key="f2")
        if st.button("🔬 FUNDIR"):
            n1 = next(a['name'] for a in st.session_state.tanque_fusao if (a.get('preferred_common_name') or a.get('name')) == ani1)
            n2 = next(a['name'] for a in st.session_state.tanque_fusao if (a.get('preferred_common_name') or a.get('name')) == ani2)
            st.success(f"Nova Espécie Criada: **{n1.split()[0]} {n2.split()[-1]}**")

elif aba == "🐾 Meu Zoo":
    for i in range(0, len(st.session_state.zoo), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(st.session_state.zoo):
                with cols[j]: card(st.session_state.zoo[i+j], "zoo", i+j, is_zoo=True)

elif aba == "⚙️ Definições":
    st.session_state.c_mega = st.text_input("Código Mega", type="password", value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input("Código 24h", type="password", value=st.session_state.c_24h)
    st.session_state.brilho = st.slider("Brilho", 50, 150, st.session_state.brilho)
    if st.button("Guardar"): st.rerun()
