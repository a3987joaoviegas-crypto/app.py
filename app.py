python
import random
import time
from datetime import datetime
from urllib.parse import quote

import requests
import streamlit as st

# ============================================================
# MUNDOVIVO
# App de animais - versão sem Premium e sem sons
# ============================================================

st.set_page_config(
    page_title="MundoVivo",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# CSS
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #071b13 0%, #0b2b20 45%, #102e25 100%);
    }

    [data-testid="stSidebar"] {
        background: #071812;
    }

    .hero {
        padding: 24px;
        border-radius: 24px;
        background: linear-gradient(135deg, #123c2c, #0a251c);
        border: 1px solid rgba(255,255,255,.10);
        margin-bottom: 20px;
    }

    .hero h1 {
        margin: 0;
        color: #ffffff;
        font-size: 42px;
    }

    .hero p {
        color: #b8d8ca;
        font-size: 17px;
        margin-top: 8px;
    }

    .animal-card {
        padding: 18px;
        border-radius: 22px;
        background: rgba(17, 47, 37, .92);
        border: 1px solid rgba(255,255,255,.09);
        margin-bottom: 18px;
        box-shadow: 0 8px 25px rgba(0,0,0,.20);
    }

    .animal-card h3 {
        color: white;
        margin: 4px 0;
    }

    .scientific {
        color: #9bc7b4;
        font-style: italic;
        margin-bottom: 8px;
    }

    .tag {
        display: inline-block;
        padding: 5px 9px;
        margin: 3px;
        border-radius: 999px;
        background: #164b38;
        color: #d9f5e8;
        font-size: 13px;
    }

    .danger {
        padding: 10px;
        border-radius: 12px;
        background: rgba(180, 35, 35, .25);
        border: 1px solid rgba(255, 80, 80, .35);
        color: #ffd0d0;
        margin-top: 10px;
    }

    .safe {
        padding: 10px;
        border-radius: 12px;
        background: rgba(30, 130, 80, .20);
        border: 1px solid rgba(80, 220, 140, .25);
        color: #d2ffe4;
        margin-top: 10px;
    }

    .stat {
        padding: 15px;
        border-radius: 18px;
        background: #0d3023;
        border: 1px solid rgba(255,255,255,.08);
        text-align: center;
    }

    .small-muted {
        color: #91b6a6;
        font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Constantes
# -----------------------------
API = "https://api.inaturalist.org/v1"

COUNTRIES = [
    "Portugal", "Espanha", "França", "Itália", "Alemanha", "Reino Unido",
    "Irlanda", "Islândia", "Noruega", "Suécia", "Finlândia", "Dinamarca",
    "Países Baixos", "Bélgica", "Suíça", "Áustria", "Polónia", "Chéquia",
    "Hungria", "Roménia", "Bulgária", "Grécia", "Croácia", "Sérvia",
    "Eslovénia", "Eslováquia", "Ucrânia", "Turquia", "Marrocos", "Argélia",
    "Tunísia", "Egito", "África do Sul", "Quénia", "Tanzânia", "Etiópia",
    "Nigéria", "Gana", "Senegal", "Camarões", "Brasil", "Argentina",
    "Chile", "Peru", "Colômbia", "Venezuela", "Equador", "Bolívia",
    "Paraguai", "Uruguai", "México", "Estados Unidos", "Canadá",
    "Costa Rica", "Panamá", "Cuba", "Jamaica", "China", "Japão",
    "Coreia do Sul", "Índia", "Nepal", "Tailândia", "Vietname",
    "Indonésia", "Filipinas", "Austrália", "Nova Zelândia", "Fiji",
    "Papua-Nova Guiné"
]

FORESTS = {
    "Amazónia": (-15.0, -75.0, 5.0, -50.0),
    "Floresta do Congo": (-5.0, 10.0, 5.0, 30.0),
    "Mata Atlântica": (-30.0, -55.0, 5.0, -35.0),
    "Floresta Boreal": (45.0, -140.0, 70.0, 170.0),
    "Floresta Temperada Europeia": (40.0, -10.0, 60.0, 35.0),
    "Florestas do Sudeste Asiático": (-10.0, 90.0, 25.0, 145.0),
    "Florestas da América Central": (5.0, -95.0, 25.0, -75.0),
}

OCEANS = {
    "Atlântico": (-60.0, -70.0, 70.0, 20.0),
    "Pacífico": (-60.0, 120.0, 70.0, -70.0),
    "Índico": (-60.0, 20.0, 30.0, 150.0),
    "Ártico": (60.0, -180.0, 90.0, 180.0),
    "Antártico": (-90.0, -180.0, -55.0, 180.0),
}

COMMON_NAMES = {
    "Panthera leo": "Leão",
    "Panthera tigris": "Tigre",
    "Panthera pardus": "Leopardo",
    "Panthera onca": "Onça-pintada",
    "Acinonyx jubatus": "Chita",
    "Elephas maximus": "Elefante-asiático",
    "Loxodonta africana": "Elefante-africano",
    "Giraffa camelopardalis": "Girafa",
    "Gorilla gorilla": "Gorila",
    "Pongo pygmaeus": "Orangotango-de-bornéu",
    "Ursus arctos": "Urso-pardo",
    "Ursus maritimus": "Urso-polar",
    "Vulpes vulpes": "Raposa-vermelha",
    "Canis lupus": "Lobo",
    "Canis lupus familiaris": "Cão",
    "Felis catus": "Gato",
    "Lynx lynx": "Lince-euroasiático",
    "Cervus elaphus": "Veado-vermelho",
    "Equus quagga": "Zebra-das-planícies",
    "Equus ferus caballus": "Cavalo",
    "Hippopotamus amphibius": "Hipopótamo",
    "Crocodylus niloticus": "Crocodilo-do-Nilo",
    "Python regius": "Píton-real",
    "Naja naja": "Cobra-de-óculos",
    "Chelonia mydas": "Tartaruga-verde",
    "Dermochelys coriacea": "Tartaruga-de-couro",
    "Delphinus delphis": "Golfinho-comum",
    "Tursiops truncatus": "Golfinho-roaz",
    "Orcinus orca": "Orca",
    "Balaenoptera musculus": "Baleia-azul",
    "Carcharodon carcharias": "Tubarão-branco",
    "Sphyrna mokarran": "Tubarão-martelo-gigante",
    "Aptenodytes forsteri": "Pinguim-imperador",
    "Spheniscus demersus": "Pinguim-africano",
    "Struthio camelus": "Avestruz",
    "Bubo bubo": "Bufo-real",
    "Falco peregrinus": "Falcão-peregrino",
    "Aquila chrysaetos": "Águia-real",
    "Ara macao": "Arara-vermelha",
    "Psittacus erithacus": "Papagaio-cinzento",
    "Pavo cristatus": "Pavão",
    "Apis mellifera": "Abelha-do-mel",
    "Danaus plexippus": "Borboleta-monarca",
    "Octopus vulgaris": "Polvo-comum",
    "Hippocampus hippocampus": "Cavalo-marinho-de-focinho-curto",
}

# -----------------------------
# Estado
# -----------------------------
defaults = {
    "page": "🏠 Início",
    "favorites": [],
    "rescued": [],
    "veterinary": {},
    "quiz_score": 0,
    "quiz_total": 0,
    "achievements": set(),
    "last_animals": [],
    "search_results": [],
    "fusion_result": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        if isinstance(value, list):
            st.session_state[key] = []
        elif isinstance(value, dict):
            st.session_state[key] = {}
        elif isinstance(value, set):
            st.session_state[key] = set()
        else:
            st.session_state[key] = value

# -----------------------------
# HTTP seguro
# -----------------------------
@st.cache_data(ttl=900, show_spinner=False)
def api_get(endpoint, params=None):
    try:
        response = requests.get(
            f"{API}/{endpoint}",
            params=params or {},
            timeout=15,
            headers={"User-Agent": "MundoVivo/1.0"},
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


# -----------------------------
# Helpers
# -----------------------------
def safe_photo(taxon):
    photo = taxon.get("default_photo")
    if isinstance(photo, dict):
        return (
            photo.get("medium_url")
            or photo.get("large_url")
            or photo.get("square_url")
            or photo.get("url")
        )
    return None


def animal_name(taxon):
    scientific = taxon.get("name", "")
    if scientific in COMMON_NAMES:
        return COMMON_NAMES[scientific]

    common = (
        taxon.get("preferred_common_name")
        or taxon.get("common_name")
        or ""
    )

    if common:
        return common

    return scientific.replace("_", " ").title() or "Animal sem nome"


def class_name(taxon):
    iconic = taxon.get("iconic_taxon_name") or ""
    mapping = {
        "Mammalia": "Mamífero",
        "Aves": "Ave",
        "Reptilia": "Réptil",
        "Amphibia": "Anfíbio",
        "Actinopterygii": "Peixe",
        "Mollusca": "Molusco",
        "Insecta": "Inseto",
        "Arachnida": "Aracnídeo",
        "Crustacea": "Crustáceo",
        "Animalia": "Animal",
    }
    return mapping.get(iconic, iconic or "Animal")


def get_conservation(taxon):
    status = taxon.get("conservation_status")
    if isinstance(status, dict):
        return (
            status.get("status_name")
            or status.get("name")
            or status.get("status")
            or ""
        )

    statuses = taxon.get("conservation_statuses")
    if isinstance(statuses, list) and statuses:
        first = statuses[0]
        if isinstance(first, dict):
            return first.get("status_name") or first.get("name") or ""

    return ""


def is_plant(taxon):
    return (taxon.get("iconic_taxon_name") or "").lower() == "plantae"


def is_animal(taxon):
    return (taxon.get("iconic_taxon_name") or "").lower() == "animalia" or (
        taxon.get("iconic_taxon_name") or ""
    ) in {
        "Mammalia",
        "Aves",
        "Reptilia",
        "Amphibia",
        "Actinopterygii",
        "Mollusca",
        "Insecta",
        "Arachnida",
        "Crustacea",
    }


def normalize_taxa(items, limit=70):
    output = []
    seen = set()

    for item in items or []:
        if not isinstance(item, dict):
            continue

        taxon = item.get("taxon", item)
        if not isinstance(taxon, dict):
            continue

        if is_plant(taxon):
            continue

        if not is_animal(taxon):
            continue

        tid = taxon.get("id")
        name = animal_name(taxon)

        if not tid or not name or tid in seen:
            continue

        seen.add(tid)
        output.append(taxon)

        if len(output) >= limit:
            break

    return output


@st.cache_data(ttl=1800, show_spinner=False)
def search_animals(text, limit=70):
    data = api_get(
        "taxa",
        {
            "q": text,
            "rank": "species",
            "iconic_taxa": "Animalia",
            "per_page": min(limit, 100),
            "locale": "pt-PT",
        },
    )
    if not data:
        return []
    return normalize_taxa(data.get("results", []), limit)


@st.cache_data(ttl=1800, show_spinner=False)
def observations_bbox(bbox, limit=70):
    data = api_get(
        "observations",
        {
            "taxon_id": 1,
            "verifiable": "true",
            "quality_grade": "research",
            "bbox": ",".join(str(x) for x in bbox),
            "per_page": min(limit, 100),
            "order": "desc",
            "order_by": "observed_on",
        },
    )

    if not data:
        return []

    taxa = []
    seen = set()

    for obs in data.get("results", []):
        taxon = obs.get("taxon")
        if not isinstance(taxon, dict):
            continue
        if is_plant(taxon) or not is_animal(taxon):
            continue
        tid = taxon.get("id")
        if tid and tid not in seen:
            seen.add(tid)
            taxa.append(taxon)
        if len(taxa) >= limit:
            break

    return taxa


@st.cache_data(ttl=1800, show_spinner=False)
def country_place_id(country):
    data = api_get(
        "places/autocomplete",
        {
            "q": country,
            "per_page": 10,
            "locale": "pt-PT",
        },
    )
    if not data:
        return None

    results = data.get("results", [])
    for item in results:
        if item.get("display_name", "").lower() == country.lower():
            return item.get("id")

    for item in results:
        if item.get("id"):
            return item.get("id")

    return None


@st.cache_data(ttl=1800, show_spinner=False)
def country_animals(country, limit=70):
    place_id = country_place_id(country)

    if place_id:
        data = api_get(
            "observations",
            {
                "taxon_id": 1,
                "place_id": place_id,
                "verifiable": "true",
                "quality_grade": "research",
                "per_page": 100,
                "order": "desc",
                "order_by": "observed_on",
            },
        )

        if data:
            return normalize_taxa(data.get("results", []), limit)

    return search_animals(country, limit)


def add_favorite(taxon):
    tid = taxon.get("id")
    if not tid:
        return

    if not any(x.get("id") == tid for x in st.session_state.favorites):
        st.session_state.favorites.append(taxon)
        st.session_state.achievements.add("Primeiro favorito")


def remove_favorite(tid):
    st.session_state.favorites = [
        x for x in st.session_state.favorites if x.get("id") != tid
    ]


def add_rescue(taxon):
    tid = taxon.get("id")
    if not tid:
        return

    if not any(x.get("id") == tid for x in st.session_state.rescued):
        st.session_state.rescued.append(taxon)
        st.session_state.achievements.add("Primeiro resgate")


def open_vet(taxon):
    tid = taxon.get("id")
    if tid:
        st.session_state.veterinary[str(tid)] = time.time()


def get_habitat(taxon):
    """
    Obtém uma descrição de habitat baseada na classe do animal.
    """
    cls = class_name(taxon)

    habitats = {
        "Mamífero": "Florestas, savanas, montanhas, desertos, campos ou ambientes urbanos, conforme a espécie.",
        "Ave": "Florestas, zonas húmidas, montanhas, praias, campos ou ambientes urbanos, conforme a espécie.",
        "Réptil": "Florestas, desertos, savanas, rios, zonas costeiras ou outros habitats quentes, conforme a espécie.",
        "Anfíbio": "Zonas húmidas, rios, lagos, charcos, florestas e outros locais com disponibilidade de água.",
        "Peixe": "Rios, lagos, estuários, recifes, zonas costeiras ou mar aberto, conforme a espécie.",
        "Molusco": "Ambientes marinhos, água doce ou habitats terrestres húmidos, conforme a espécie.",
        "Inseto": "Florestas, campos, jardins, zonas húmidas, desertos e outros ambientes terrestres.",
        "Aracnídeo": "Solo, vegetação, cavernas, florestas, desertos e outros habitats terrestres.",
        "Crustáceo": "Oceanos, rios, lagos, estuários e zonas costeiras, conforme a espécie.",
    }

    return habitats.get(
        cls,
        "O habitat varia conforme a espécie e a sua distribuição geográfica."
    )


def get_diet(taxon):
    cls = class_name(taxon)

    diets = {
        "Mamífero": "Herbívoro, carnívoro ou omnívoro, conforme a espécie.",
        "Ave": "Sementes, frutos, néctar, insetos, peixe ou outros animais, conforme a espécie.",
        "Réptil": "Carnívoro, herbívoro ou omnívoro, conforme a espécie.",
        "Anfíbio": "Principalmente insetos e outros pequenos invertebrados.",
        "Peixe": "Algas, plantas aquáticas, plâncton, pequenos animais ou outros peixes, conforme a espécie.",
        "Molusco": "Algas, plantas, plâncton, detritos ou outros animais, conforme a espécie.",
        "Inseto": "Néctar, folhas, sementes, frutos, madeira ou outros pequenos organismos, conforme a espécie.",
        "Aracnídeo": "Principalmente insetos e outros pequenos animais.",
        "Crustáceo": "Algas, detritos, plâncton ou pequenos animais, conforme a espécie.",
    }

    return diets.get(cls, "A alimentação varia conforme a espécie.")


def get_reproduction(taxon):
    cls = class_name(taxon)

    reproduction = {
        "Mamífero": "Na maioria das espécies, reprodução sexuada e nascimento de crias vivas.",
        "Ave": "Reprodução sexuada e postura de ovos.",
        "Réptil": "Reprodução sexuada; muitas espécies põem ovos.",
        "Anfíbio": "Reprodução sexuada; muitas espécies põem ovos na água ou em locais húmidos.",
        "Peixe": "Reprodução sexuada, podendo ocorrer fecundação externa ou interna.",
        "Molusco": "Reprodução sexuada, com estratégias diferentes conforme a espécie.",
        "Inseto": "Reprodução sexuada e desenvolvimento através de ovos.",
        "Aracnídeo": "Reprodução sexuada e produção de ovos.",
        "Crustáceo": "Reprodução sexuada e produção de ovos.",
    }

    return reproduction.get(
        cls,
        "A reprodução varia conforme a espécie."
    )


def get_distribution(taxon):
    """
    Usa os dados disponíveis na API para apresentar uma indicação
    da distribuição conhecida.
    """
    preferred = taxon.get("preferred_common_name") or ""
    wikipedia = taxon.get("wikipedia_url") or ""

    if wikipedia:
        return "Distribuição geográfica disponível nas fontes científicas associadas à espécie."

    if preferred:
        return "A distribuição geográfica depende da espécie e das populações conhecidas."

    return "Distribuição geográfica não especificada pela API."


def get_fun_fact(taxon):
    """
    Pequenos factos educativos baseados na classe.
    """
    cls = class_name(taxon)

    facts = {
        "Mamífero": "Os mamíferos distinguem-se, entre outras características, pela presença de glândulas mamárias.",
        "Ave": "As aves possuem penas e um sistema respiratório altamente especializado.",
        "Réptil": "Os répteis possuem adaptações que lhes permitem viver sobretudo em ambientes terrestres.",
        "Anfíbio": "Muitos anfíbios passam parte do seu ciclo de vida na água e parte em terra.",
        "Peixe": "Os peixes apresentam uma enorme diversidade de formas, tamanhos e habitats.",
        "Molusco": "Os moluscos incluem grupos muito diferentes, como polvos, lulas, caracóis e mexilhões.",
        "Inseto": "Os insetos constituem um dos grupos de animais mais diversos do planeta.",
        "Aracnídeo": "Aranhas, escorpiões, ácaros e carraças pertencem ao grupo dos aracnídeos.",
        "Crustáceo": "Os crustáceos incluem animais como caranguejos, camarões, lagostas e krill.",
    }

    return facts.get(
        cls,
        "Cada espécie possui adaptações únicas ao seu ambiente."
    )


def show_animal_card(taxon, compact=False, key_prefix="animal"):
    name = animal_name(taxon)
    scientific = taxon.get("name", "Nome científico indisponível")
    photo = safe_photo(taxon)
    cls = class_name(taxon)
    conservation = get_conservation(taxon)

    if compact:
        st.markdown('<div class="animal-card">', unsafe_allow_html=True)
        if photo:
            st.image(photo, use_container_width=True)

        st.markdown(f"### {name}")
        st.markdown(
            f'<div class="scientific">{scientific}</div>',
            unsafe_allow_html=True,
        )

        st.caption(f"Classe: {cls}")

        if st.button(
            "❤️ Guardar",
            key=f"{key_prefix}_fav_{taxon.get('id')}"
        ):
            add_favorite(taxon)
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ========================================================
    # CARTÃO DE CIDADÃO COMPLETO
    # ========================================================

    st.markdown('<div class="animal-card">', unsafe_allow_html=True)

    if photo:
        st.image(photo, use_container_width=True)
    else:
        st.info("📷 A API não forneceu fotografia para este animal.")

    st.markdown(
        f"## 🪪 CARTÃO DE CIDADÃO DO ANIMAL",
        unsafe_allow_html=True,
    )

    st.markdown(f"### 🐾 {name}")

    st.markdown(
        f'<div class="scientific">{scientific}</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # Identificação
    st.markdown("### 🆔 Identificação")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Nome comum:** {name}")
        st.write(f"**Nome científico:** *{scientific}*")
        st.write(f"**Classe:** {cls}")

    with col2:
        st.write("**Reino:** Animalia")
        st.write(f"**ID científico:** {taxon.get('id', 'Não disponível')}")
        st.write(
            f"**Estado de conservação:** "
            f"{conservation if conservation else 'Não disponível'}"
        )

    st.divider()

    # Características
    st.markdown("### 🔬 Características")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"🍖 **Alimentação:** {get_diet(taxon)}")
        st.write(f"🥚 **Reprodução:** {get_reproduction(taxon)}")

    with col2:
        st.write(f"🌍 **Habitat:** {get_habitat(taxon)}")
        st.write(f"🗺️ **Distribuição:** {get_distribution(taxon)}")

    st.divider()

    # Facto interessante
    st.markdown("### 💡 Sabias que...")

    st.info(get_fun_fact(taxon))

    # Estado de conservação
    if conservation:
        conservation_lower = conservation.lower()

        dangerous_statuses = {
            "cr",
            "en",
            "vu",
            "critically endangered",
            "endangered",
            "vulnerable",
            "criticamente em perigo",
            "em perigo",
            "vulnerável",
        }

        if conservation_lower in dangerous_statuses:
            st.markdown(
                f'''
                <div class="danger">
                    ⚠️ <b>Animal com preocupação de conservação:</b>
                    {conservation}
                </div>
                ''',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'''
                <div class="safe">
                    🛡️ <b>Estado de conservação:</b>
                    {conservation}
                </div>
                ''',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '''
            <div class="safe">
                🛡️ <b>Estado de conservação:</b>
                Informação não disponível.
            </div>
            ''',
            unsafe_allow_html=True,
        )

    st.divider()

    # Botões
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button(
            "❤️ Adicionar ao Zoo",
            key=f"{key_prefix}_fav_{taxon.get('id')}",
            use_container_width=True,
        ):
            add_favorite(taxon)
            st.success("Adicionado ao teu Zoo!")

    with c2:
        if st.button(
            "🚑 Resgatar",
            key=f"{key_prefix}_rescue_{taxon.get('id')}",
            use_container_width=True,
        ):
            add_rescue(taxon)
            st.success("Animal resgatado!")

    with c3:
        if st.button(
            "🩺 Veterinário",
            key=f"{key_prefix}_vet_{taxon.get('id')}",
            use_container_width=True,
        ):
            open_vet(taxon)
            st.success("Animal encaminhado para o veterinário.")

    st.markdown("</div>", unsafe_allow_html=True)


def show_results(results, title="Animais", limit=None):
    if not results:
        st.warning("Não encontrei animais para esta seleção.")
        return

    st.subheader(f"{title} — {len(results)} encontrados")

    data = results if limit is None else results[:limit]

    for index in range(0, len(data), 3):
        cols = st.columns(3)

        for col, taxon in zip(cols, data[index:index + 3]):
            with col:
                show_animal_card(
                    taxon,
                    compact=True,
                    key_prefix=f"grid_{taxon.get('id')}",
                )


# -----------------------------
# Barra lateral
# -----------------------------
with st.sidebar:
    st.markdown("# 🌍 MundoVivo")
    st.caption("O teu mundo de animais")

    pages = [
        "🏠 Início",
        "❤️ Meu Zoo",
        "🌳 Florestas",
        "🌊 Oceanos",
        "🌍 Países",
        "🔬 Laboratório",
        "📸 Visão IA",
        "🚑 Salvamento",
        "🩺 Veterinário",
        "🧬 Tanque de Fusão",
        "🧠 Quiz",
        "🏆 Conquistas",
        "📊 Estatísticas",
        "⚙️ Definições",
    ]

    selected = st.radio(
        "Navegação",
        pages,
        index=pages.index(st.session_state.page)
        if st.session_state.page in pages
        else 0,
    )

    st.session_state.page = selected

    st.divider()

    st.metric("❤️ No teu Zoo", len(st.session_state.favorites))
    st.metric("🚑 Resgatados", len(st.session_state.rescued))
    st.metric("🏆 Conquistas", len(st.session_state.achievements))


# -----------------------------
# Cabeçalho
# -----------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🌍 MundoVivo</h1>
        <p>Explora animais, habitats, países e oceanos. Descobre, guarda e cuida da tua coleção.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# INÍCIO
# ============================================================
if st.session_state.page == "🏠 Início":
    st.subheader("✨ Bem-vindo ao MundoVivo")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("❤️ Meu Zoo", len(st.session_state.favorites))

    with c2:
        st.metric("🚑 Resgates", len(st.session_state.rescued))

    with c3:
        st.metric("🏆 Conquistas", len(st.session_state.achievements))

    with c4:
        st.metric("🩺 Veterinário", len(st.session_state.veterinary))

    st.divider()

    st.subheader("🔎 Explorar rapidamente")

    quick = st.text_input(
        "Procura um animal",
        placeholder="Ex.: leão, golfinho, águia, panda...",
    )

    if quick:
        results = search_animals(quick, 12)
        show_results(results, f"Resultados para «{quick}»", 12)
    else:
        st.info(
            "Escolhe uma secção no menu lateral ou pesquisa diretamente um animal."
        )

    if st.session_state.favorites:
        st.divider()
        st.subheader("❤️ Os teus últimos animais")
        show_results(
            st.session_state.favorites[-6:][::-1],
            "Meu Zoo",
            6,
        )


# ============================================================
# MEU ZOO
# ============================================================
elif st.session_state.page == "❤️ Meu Zoo":
    st.subheader("❤️ Meu Zoo / Favoritos")

    if not st.session_state.favorites:
        st.info(
            "Ainda não tens animais no teu Zoo. Vai a Países, Florestas, "
            "Oceanos ou Laboratório e carrega em «Adicionar ao Zoo»."
        )
    else:
        st.write(
            f"Tens **{len(st.session_state.favorites)} animais** guardados."
        )

        for taxon in st.session_state.favorites:
            tid = taxon.get("id")
            name = animal_name(taxon)
            photo = safe_photo(taxon)

            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 2, 1])

                with col1:
                    if photo:
                        st.image(photo, use_container_width=True)

                with col2:
                    st.markdown(f"### {name}")
                    st.markdown(
                        f"*{taxon.get('name', 'Nome científico indisponível')}*"
                    )
                    st.write(class_name(taxon))

                with col3:
                    if st.button(
                        "🗑️ Remover",
                        key=f"remove_fav_{tid}",
                        use_container_width=True,
                    ):
                        remove_favorite(tid)
                        st.rerun()


# ============================================================
# FLORESTAS
# ============================================================
elif st.session_state.page == "🌳 Florestas":
    st.subheader("🌳 Florestas")

    forest = st.selectbox(
        "Escolhe uma floresta",
        list(FORESTS.keys()),
    )

    if st.button("🔎 Explorar floresta", type="primary"):
        with st.spinner("A procurar animais desta região..."):
            results = observations_bbox(FORESTS[forest], 70)

        st.session_state.last_animals = results
        show_results(results, forest, 70)

    elif st.session_state.last_animals:
        show_results(st.session_state.last_animals, forest, 70)
    else:
        st.info(
            "Escolhe uma floresta e carrega em «Explorar floresta»."
        )


# ============================================================
# OCEANOS
# ============================================================
elif st.session_state.page == "🌊 Oceanos":
    st.subheader("🌊 Oceanos")

    ocean = st.selectbox(
        "Escolhe um oceano",
        list(OCEANS.keys()),
    )

    if st.button("🌊 Explorar oceano", type="primary"):
        with st.spinner("A procurar animais marinhos..."):
            results = observations_bbox(OCEANS[ocean], 70)

        results = [
            x for x in results
            if not is_plant(x)
        ]

        st.session_state.last_animals = results
        show_results(results, ocean, 70)

    elif st.session_state.last_animals:
        show_results(st.session_state.last_animals, ocean, 70)
    else:
        st.info(
            "Escolhe um oceano e começa a exploração."
        )


# ============================================================
# PAÍSES
# ============================================================
elif st.session_state.page == "🌍 Países":
    st.subheader("🌍 Animais por país")

    country = st.selectbox(
        "Escolhe um país",
        COUNTRIES,
        index=COUNTRIES.index("Portugal"),
    )

    st.caption(f"{len(COUNTRIES)} países disponíveis.")

    if st.button("🦁 Explorar país", type="primary"):
        with st.spinner(
            f"A procurar animais em {country}..."
        ):
            results = country_animals(country, 70)

        st.session_state.last_animals = results

        if not results:
            st.warning(
                "A API não encontrou observações suficientes para este país."
            )
        else:
            show_results(
                results,
                f"Animais de {country}",
                70,
            )

    elif st.session_state.last_animals:
        show_results(
            st.session_state.last_animals,
            f"Animais de {country}",
            70,
        )


# ============================================================
# LABORATÓRIO
# ============================================================
elif st.session_state.page == "🔬 Laboratório":
    st.subheader("🔬 Laboratório")

    query = st.text_input(
        "Pesquisa livre",
        placeholder="Ex.: leão, tubarão, pinguim, raposa...",
    )

    limit = st.slider(
        "Número de resultados",
        6,
        70,
        20,
    )

    if query:
        with st.spinner(
            "A pesquisar no catálogo animal..."
        ):
            results = search_animals(query, limit)

        results = [
            x for x in results
            if not is_plant(x)
        ]

        show_results(
            results,
            f"Laboratório: {query}",
            limit,
        )
    else:
        st.info(
            "Escreve o nome de um animal para começar."
        )


# ============================================================
# VISÃO IA
# ============================================================
elif st.session_state.page == "📸 Visão IA":
    st.subheader("📸 Visão IA")

    st.write(
        "Tira uma fotografia para tentares encontrar animais semelhantes "
        "no catálogo do MundoVivo."
    )

    photo = st.camera_input(
        "📸 Tirar fotografia"
    )

    if photo:
        st.image(
            photo,
            caption="Fotografia recebida",
            use_container_width=True,
        )

        st.warning(
            "A identificação automática por fotografia precisa de um serviço "
            "de visão animal configurado. Para não inventar um animal, esta "
            "versão não apresenta um resultado falso."
        )

        manual = st.text_input(
            "Se quiseres confirmar manualmente, escreve o nome do animal"
        )

        if manual:
            results = search_animals(manual, 6)

            show_results(
                results,
                f"Possíveis resultados: {manual}",
                6,
            )


# ============================================================
# SALVAMENTO
# ============================================================
elif st.session_state.page == "🚑 Salvamento":
    st.subheader("🚑 Centro de Salvamento")

    if st.session_state.last_animals:
        candidate = random.choice(
            st.session_state.last_animals
        )
    else:
        candidate = None

    if candidate:
        st.markdown(
            "### 🐾 Animal disponível para resgate"
        )

        show_animal_card(
            candidate,
            compact=False,
            key_prefix="rescue_page",
        )
    else:
        st.info(
            "Primeiro explora uma floresta, oceano, país ou usa o laboratório. "
            "Depois volta aqui para resgatar um animal."
        )

    if st.session_state.rescued:
        st.divider()
        st.subheader("❤️ Animais resgatados")

        show_results(
            st.session_state.rescued,
            "Resgatados",
            20,
        )


# ============================================================
# VETERINÁRIO
# ============================================================
elif st.session_state.page == "🩺 Veterinário":
    st.subheader("🩺 Veterinário")

    if not st.session_state.veterinary:
        st.info(
            "Ainda não tens animais internados."
        )
    else:
        for tid, start in list(
            st.session_state.veterinary.items()
        ):
            taxon = next(
                (
                    x
                    for x in (
                        st.session_state.favorites
                        + st.session_state.rescued
                    )
                    if str(x.get("id")) == str(tid)
                ),
                None,
            )

            if taxon is None:
                continue

            elapsed = int(
                time.time() - start
            )

            remaining = max(
                0,
                86400 - elapsed
            )

            hours = remaining // 3600
            minutes = (remaining % 3600) // 60

            with st.container(border=True):
                st.markdown(
                    f"### 🐾 {animal_name(taxon)}"
                )

                if remaining > 0:
                    st.info(
                        f"🩺 Em recuperação. Tempo restante: "
                        f"**{hours}h {minutes}min**."
                    )
                else:
                    st.success(
                        "✅ Alta disponível!"
                    )

                    if st.button(
                        "🏠 Dar alta",
                        key=f"discharge_{tid}",
                    ):
                        del st.session_state.veterinary[tid]
                        st.rerun()


# ============================================================
# TANQUE DE FUSÃO
# ============================================================
elif st.session_state.page == "🧬 Tanque de Fusão":
    st.subheader("🧬 Tanque de Fusão")

    if len(st.session_state.favorites) < 2:
        st.info(
            "Precisas de pelo menos 2 animais no teu Zoo "
            "para usar o Tanque de Fusão."
        )
    else:
        names = [
            animal_name(x)
            for x in st.session_state.favorites
        ]

        a = st.selectbox(
            "Primeiro animal",
            names,
            key="fusion_a",
        )

        b = st.selectbox(
            "Segundo animal",
            names,
            index=1 if len(names) > 1 else 0,
            key="fusion_b",
        )

        if st.button(
            "🧬 Criar fusão",
            type="primary",
        ):
            if a == b:
                st.error(
                    "Escolhe dois animais diferentes."
                )
            else:
                first = next(
                    x
                    for x in st.session_state.favorites
                    if animal_name(x) == a
                )

                second = next(
                    x
                    for x in st.session_state.favorites
                    if animal_name(x) == b
                )

                st.session_state.fusion_result = {
                    "name": f"{a} + {b}",
                    "a": first,
                    "b": second,
                }

        fusion = st.session_state.fusion_result

        if fusion:
            st.divider()

            st.markdown(
                f"## 🧬 {fusion['name']}"
            )

            c1, c2 = st.columns(2)

            with c1:
                photo = safe_photo(
                    fusion["a"]
                )

                if photo:
                    st.image(
                        photo,
                        use_container_width=True,
                    )

                st.write(
                    animal_name(fusion["a"])
                )

            with c2:
                photo = safe_photo(
                    fusion["b"]
                )

                if photo:
                    st.image(
                        photo,
                        use_container_width=True,
                    )

                st.write(
                    animal_name(fusion["b"])
                )

            st.success(
                "Fusão criada! Esta criatura é uma combinação virtual "
                "dos dois animais escolhidos."
            )


# ============================================================
# QUIZ
# ============================================================
elif st.session_state.page == "🧠 Quiz":
    st.subheader("🧠 Quiz do MundoVivo")

    pool = (
        st.session_state.favorites
        or st.session_state.last_animals
    )

    if len(pool) < 4:
        st.info(
            "Guarda pelo menos 4 animais no Zoo "
            "ou explora uma região primeiro."
        )
    else:
        question = random.choice(pool)

        correct = animal_name(question)

        options = [correct]

        others = [
            animal_name(x)
            for x in pool
            if animal_name(x) != correct
        ]

        random.shuffle(others)

        options.extend(
            others[:3]
        )

        random.shuffle(options)

        st.markdown(
            "### Que animal é este?"
        )

        photo = safe_photo(question)

        if photo:
            st.image(
                photo,
                width=450,
            )
        else:
            st.info(
                "Esta espécie não tem fotografia disponível."
            )

        answer = st.radio(
            "Escolhe uma resposta:",
            options,
            key=(
                f"quiz_{question.get('id')}_"
                f"{st.session_state.quiz_total}"
            ),
        )

        if st.button(
            "✅ Responder"
        ):
            st.session_state.quiz_total += 1

            if answer == correct:
                st.session_state.quiz_score += 1

                st.session_state.achievements.add(
                    "Primeiro acerto"
                )

                st.success(
                    "🎉 Correto!"
                )
            else:
                st.error(
                    f"❌ Não. Era **{correct}**."
                )

        st.metric(
            "Pontuação",
            f"{st.session_state.quiz_score}/"
            f"{st.session_state.quiz_total}",
        )


# ============================================================
# CONQUISTAS
# ============================================================
elif st.session_state.page == "🏆 Conquistas":
    st.subheader("🏆 Conquistas")

    achievements = [
        (
            "Primeiro favorito",
            "❤️ Guardaste o primeiro animal."
        ),
        (
            "Primeiro resgate",
            "🚑 Fizeste o primeiro resgate."
        ),
        (
            "Primeiro acerto",
            "🧠 Acertaste a primeira pergunta do quiz."
        ),
    ]

    if len(st.session_state.favorites) >= 10:
        st.session_state.achievements.add(
            "Colecionador"
        )

    if len(st.session_state.favorites) >= 25:
        st.session_state.achievements.add(
            "Grande Colecionador"
        )

    if len(st.session_state.favorites) >= 50:
        st.session_state.achievements.add(
            "Mestre do Zoo"
        )

    achievements.extend([
        (
            "Colecionador",
            "❤️ Tens 10 animais."
        ),
        (
            "Grande Colecionador",
            "❤️ Tens 25 animais."
        ),
        (
            "Mestre do Zoo",
            "❤️ Tens 50 animais."
        ),
    ])

    for name, description in achievements:
        if name in st.session_state.achievements:
            st.success(
                f"🏆 **{name}** — {description}"
            )
        else:
            st.write(
                f"🔒 **{name}** — {description}"
            )


# ============================================================
# ESTATÍSTICAS
# ============================================================
elif st.session_state.page == "📊 Estatísticas":
    st.subheader(
        "📊 Estatísticas do teu MundoVivo"
    )

    total = len(
        st.session_state.favorites
    )

    rescued = len(
        st.session_state.rescued
    )

    classes = {}

    for taxon in st.session_state.favorites:
        cls = class_name(taxon)

        classes[cls] = (
            classes.get(cls, 0) + 1
        )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            '<div class="stat">❤️<br><b>Zoo</b><br>'
            f'{total}</div>',
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            '<div class="stat">🚑<br><b>Resgates</b><br>'
            f'{rescued}</div>',
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            '<div class="stat">🏆<br><b>Conquistas</b><br>'
            f'{len(st.session_state.achievements)}</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    if classes:
        st.subheader(
            "🐾 Animais por classe"
        )

        for cls, amount in sorted(
            classes.items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            st.write(
                f"**{cls}:** {amount}"
            )

            st.progress(
                min(
                    amount / max(total, 1),
                    1.0,
                )
            )
    else:
        st.info(
            "Adiciona animais ao teu Zoo "
            "para veres estatísticas."
        )


# ============================================================
# DEFINIÇÕES
# ============================================================
elif st.session_state.page == "⚙️ Definições":
    st.subheader(
        "⚙️ Definições"
    )

    st.write(
        "### 🧹 Dados locais da aplicação"
    )

    if st.button(
        "🗑️ Limpar Meu Zoo"
    ):
        st.session_state.favorites = []

        st.success(
            "Meu Zoo limpo."
        )

    if st.button(
        "🗑️ Limpar resgates"
    ):
        st.session_state.rescued = []

        st.success(
            "Resgates limpos."
        )

    if st.button(
        "🔄 Repor conquistas"
    ):
        st.session_state.achievements = set()
        st.session_state.quiz_score = 0
        st.session_state.quiz_total = 0

        st.success(
            "Conquistas e pontuação repostas."
        )

    st.divider()

    st.markdown(
        "### ℹ️ Sobre"
    )

    st.write(
        "MundoVivo é uma aplicação educativa de exploração animal. "
        "Os dados e fotografias apresentados dependem da disponibilidade "
        "da API do iNaturalist."
    )

    st.caption(
        "Versão: MundoVivo 2.0 — sem Premium e sem sons."
    )

