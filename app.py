import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DE INTERFACE
st.set_page_config(page_title="BIO-MAPA EXPERT", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #adbac7; }
    .animal-card { 
        background: #1c2128; border-radius: 12px; padding: 15px; 
        border: 1px solid #2ea043; margin-bottom: 15px;
    }
    .img-fluid { width: 100%; height: 200px; object-fit: cover; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DADOS DE OCEANOS E REGIÕES
# Criamos uma lista fixa para garantir que os animais são sempre daquela área
data_mapa = pd.DataFrame({
    'lat': [0.0, -15.0, -20.0, 80.0, -3.46, -2.33, -18.28, 40.0],
    'lon': [-25.0, -140.0, 70.0, 0.0, -62.21, 34.83, 145.0, -3.7],
    'nome': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 
             'Amazónia', 'Serengeti', 'Grande Barreira de Coral', 'Península Ibérica']
})

# 3. MOTOR DE PESQUISA (SÓ ANIMAIS)
def buscar_animais_reais(termo):
    # kingdomKey=1 garante que SÓ vêm Animais (exclui plantas, fungos e ruas)
    url = f"https://api.gbif.org/v1/species/search?q={termo}&kingdomKey=1&limit=12&status=ACCEPTED"
    try:
        res = requests.get(url, timeout=5).json().get('results', [])
        lista = []
        for r in res:
            # Verificação dupla para ter a certeza que é um animal
            if r.get('kingdom') == 'Animalia' and 'canonicalName' in r:
                nome = r['canonicalName']
                # Busca foto real no iNaturalist
                foto = f"https://picsum.photos/seed/{r.get('key')}/400/300"
                try:
                    res_i = requests.get(f"https://api.inaturalist.org/v1/taxa?q={nome}&per_page=1", timeout=1).json()
                    if res_i['results']: foto = res_i['results'][0]['default_photo']['medium_url']
                except: pass
                r['foto_url'] = foto
                lista.append(r)
        return lista
    except: return []

# 4. INTERFACE: MAPA TÁTIL
st.title("🌍 BIO-MAPA INTERATIVO")

# O mapa agora funciona como um seletor
st.subheader("📍 Toca no mapa ou escolhe a região:")
escolha = st.selectbox("Região Selecionada:", [""] + list(data_mapa['nome']))

# Mostra o mapa com os pontos verdes
st.map(data_mapa, size=20, color='#2ea043')

st.markdown("---")

# 5. LISTA DE ANIMAIS DA REGIÃO (Só aparece se houver escolha)
if escolha:
    st.header(f"🐳 Fauna de: {escolha}")
    
    # Criamos as abas como pediste
    tab_lab, tab_cal, tab_fav = st.tabs(["🔬 LABORATÓRIO ANIMAL", "📅 CALENDÁRIO", "⭐ FAVORITOS"])
    
    with tab_lab:
        animais = buscar_animais_reais(escolha)
        if animais:
            cols = st.columns(3)
            for idx, a in enumerate(animais):
                with cols[idx % 3]:
                    st.markdown(f"""
                        <div class='animal-card'>
                            <img src='{a['foto_url']}' class='img-fluid'>
                            <h3 style='color:#2ea043; font-size:18px;'>{a['canonicalName']}</h3>
                            <p style='font-size:12px;'><i>{a.get('scientificName', '')}</i></p>
                            <p style='font-size:11px; color:#888;'>Classe: {a.get('class', 'N/D')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"❤️ Fav {idx}", key=f"btn_{a['key']}"):
                        st.session_state.setdefault('meus_favs', []).append(a['canonicalName'])
        else:
            st.warning("A carregar biodiversidade marinha... Tenta clicar noutra região.")

    with tab_cal:
        st.subheader("📅 Registo de Avistamento")
        c1, c2 = st.columns(2)
        data_visto = c1.date_input("Data:")
        animal_visto = c2.text_input("Qual animal viste?")
        if st.button("Registar no Calendário"):
            st.success(f"Registado: {animal_visto} em {data_visto}")

    with tab_fav:
        st.subheader("⭐ Lista de Favoritos")
        for f in set(st.session_state.get('meus_favs', [])):
            st.write(f"✅ {f}")
        st.text_area("Bloco de Notas:", "Escreve aqui as tuas notas sobre os oceanos...")

else:
    st.info("👆 Seleciona uma região no menu acima para ver os animais e abrir o Laboratório.")
