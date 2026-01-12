import streamlit as st
import requests

st.title("Teste de Conexão Animal 🐾")

# Botão de Teste
if st.button("Carregar Animal de Teste"):
    try:
        # Tenta buscar o Leão na base de dados mundial
        res = requests.get("https://api.gbif.org/v1/species/search?q=Panthera%20leo&limit=1")
        dados = res.json()['results'][0]
        
        st.success("Conectado à Base de Dados Mundial!")
        st.write(f"**Nome Comum:** {dados['canonicalName']}")
        st.write(f"**Nome Científico:** {dados['scientificName']}")
        st.write(f"**Classe:** {dados['class']}")
        
        # Tenta buscar a foto na Wikipedia
        foto_res = requests.get("https://en.wikipedia.org/w/api.php?action=query&titles=Panthera%20leo&prop=pageimages&format=json&pithumbsize=400")
        pages = foto_res.json()['query']['pages']
        for p in pages:
            st.image(pages[p]['thumbnail']['source'])
            
    except Exception as e:
        st.error(f"Erro ao carregar: {e}")
