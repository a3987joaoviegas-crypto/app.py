import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", layout="wide")

# Estilo visual (Mantido)
st.markdown("""
    <style>
    .stApp { background-color: #0b1117; color: #adbac7; }
    .cc-card { 
        background: #1c2128; border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
    }
    .img-cc { width: 100%; height: 200px; object-fit: cover; border-radius: 8px; }
    .label-expert { color: #2ea043; font-weight: bold; font-size: 14px; margin-bottom: 2px; }
    .val-expert { color: white; font-size: 16px; margin-bottom: 10px; }
    h1, h2, h3 { color: #2ea043 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ALIMENTAÇÃO REAL ---
def definir_dieta(classe, nome):
    n = str(nome).lower()
    # Carnívoros e especialistas em carne
    if any(x in n for x in ['leão', 'tigre', 'lobo', 'orca', 'tubarão', 'jacaré', 'crocodilo']): return "Carnívoro"
    if any(x in n for x in ['águia', 'falcão', 'coruja', 'gavião', 'abutre']): return "Carnívoro (Rapina)"
    if any(x in n for x in ['garça', 'pinguim', 'pelicano', 'lontra', 'foca']): return "Piscívoro (Peixes)"
    
    # Herbívoros e especialistas em plantas
    if any(x in n for x in ['elefante', 'girafa', 'zebra', 'vaca', 'ovelha', 'veado', 'coelho']): return "Herbívoro"
    if any(x in n for x in ['panda', 'coala']): return "Herbívoro Estrito"
    if any(x in n for x in ['arara', 'papagaio', 'tucano']): return "Frugívoro (Frutos/Sementes)"
    
    # Insetívoros
    if any(x in n for x in ['sapinho', 'rã', 'camaleão', 'lagartixa', 'andorinha', 'morcego']): return "Insetívoro"
    if any(x in n for x in ['papa-formigas', 'tatu']): return "Insetívoro Especialista"
    
    # Omnívoros reais
    if any(x in n for x in ['porco', 'javali', 'urso', 'macaco', 'chimpanzé', 'rato', 'corvo', 'gaivota']): return "Omnívoro"
    
    # Decisão por classe se não houver nome específico
    c = str(classe).lower()
    if 'reptilia' in c: return "Carnívoro / Insetívoro"
    if 'amphibia' in c: return "Insetívoro"
    return "Omnívoro"

# 2. LÓGICA DE REPRODUÇÃO (Mantida)
def definir_repro(classe):
    c = str(classe).lower()
    if 'mammalia' in c: return "Vivíparo"
    if any(x in c for x in ['aves', 'reptilia', 'amphibia']): return "Ovíparo"
    return "Ovíparo / Variável"

# 3. MOTOR DE BUSCA
def buscar_fauna(termo, lat=None, lon=None):
    url = "https://api.inaturalist.org/v1/observations"
    params = {"taxon_id": 1, "per_page": 50, "locale": "pt-BR", "order": "desc", "order_by": "votes"}
    if lat and lon:
        params.update({"lat": lat, "lng": lon, "radius": 600})
    else:
        params.update({"q": termo})
    try:
        res = requests.get(url, params=params, timeout=10).json()
        lista = []
        vistos = set()
        for obs in res.get('results', []):
            t = obs.get('taxon')
            if t and t.get('default_photo'):
                nome = t.get('preferred_common_name') or t.get('name')
                if nome not in vistos:
                    lista.append({
                        'nome': nome.title(),
                        'sci': t.get('name'),
                        'foto': t['default_photo']['medium
