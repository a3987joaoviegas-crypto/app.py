import streamlit as st
import requests

# 1. Configuração inicial
st.set_page_config(page_title="Bio-Expert", layout="wide")

# 2. Função de Imagem Melhorada (Wiki + iNaturalist)
def buscar_foto(nome_cientifico, gbif_id):
    try:
        # Tenta iNaturalist primeiro
        res = requests.get(f"https://api.inaturalist.org/v1/taxa?q={nome_cientifico}&per_page=1", timeout=2).json()
        if res['results'] and res['results'][0].get('default_photo'):
            return res['results'][0]['default_photo']['medium_url']
        
        # Se falhar, tenta Wikipedia
        url_wiki = f"https://en.wikipedia.org/w/api.php?action=query&titles={nome_cientifico}&prop=pageimages&format=json&pithumbsize=500"
        res_wiki = requests.get(url_wiki, timeout=2).json()
        pages = res_wiki['query']['pages']
        for p in pages:
            if 'thumbnail' in pages[p]:
                return pages[p]['thumbnail']['source']
    except:
        pass
    # Se não encontrar nada, usa uma imagem padrão baseada no ID para não repetir
    return f"https://picsum.photos/seed/{gbif_id}/400/300"

# 3. Interface de Pesquisa
st.title("🐾 Pesquisa de Animais")
busca = st.text_input("Escreve o nome do animal:")

if busca:
    # Fazemos apenas UMA chamada à API
    url_gbif = f"https://api.gbif.org/v1/species/search?q={busca}&kingdomKey=1&limit=10"
    dados = requests.get(url_gbif).json().get('results', [])
    
    # Criamos as colunas para exibição limpa
    for item in dados:
        if 'canonicalName' in item:
            nome = item['canonicalName']
            sci_name = item.get('scientificName', 'N/A')
            gbif_id = item.get('key', 0)
            
            # Container único para cada animal (evita repetições)
            with st.container():
                col1, col2 = st.columns([1, 2])
                
                # Busca a foto específica para este ID
                foto_url = buscar_foto(nome, gbif_id)
                
                col1.image(foto_url, use_container_width=True)
                col2.subheader(f"🐾 {nome}")
                col2.write(f"**Nome Científico:** *{sci_name}*")
                col2.write(f"**Classe:** {item.get('class', 'N/D')}")
                st.divider()
