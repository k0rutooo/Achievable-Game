import streamlit as st
import pandas as pd
from streamlit_agraph import agraph, Config
from utils.data import charger_donnees_user
from utils.domains import est_domaine_principal, trier_domaines
from utils.arbre_compétence import generer_arbre_dynamique
from utils.security import securite_page
#📂
user = st.session_state.username
df_total = charger_donnees_user(user)
securite_page()
df_arbre = df_total[df_total['Parent'] != 'META'].copy()

# ------------------------------------------------------------------------------------
#   TEST ARBRE FINAL
# ------------------------------------------------------------------------------------

from config import DATA_DOMAINE_DIR, DATA_ASSET_DIR

path_dossier_domaine = DATA_DOMAINE_DIR
chemin_domaines = path_dossier_domaine / "domaine.csv"

df_domaines = pd.read_csv(chemin_domaines)
#nodes,edges = generer_arbre_dynamique(df_domaines)

# ------------------------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="Arbre de Compétences")

# ------------------------------------------------------------------------------------
#   INTERFACE STREAMLIT
# ------------------------------------------------------------------------------------

@st.dialog("À savoir sur l'arbre de Compétences", width="medium")
def info_arbre():
    st.space("small")
    with st.container(border=True):
        st.markdown('''Dans l'arbre vous pouvez visualiser tout vos domaines, 
                    en cliquant les noeuds de domaine vous vous rendrez dans leur bureau respectif, 
                    ou alors, en cliquant sur un 
                    :blue-background[Composant]
                    ou un 
                    :blue-background[Hub], 
                    les liens vers leurs parents et enfant direct seront en surbrillance''')
        st.image(DATA_ASSET_DIR / "arbre_hres_01.png")

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.big-body-font {
    font-size:16px !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🌳 Arbre de Compétences")
st.space("small")

st.markdown('''<p class="big-body-font">
            Ici vous pouvez cliquer sur vos domaines pour vous rendre dans le bureau de ce dernier, 
            où alors cliquer sur un Hub
            ou un Composant
            pour voir à qui ils sont reliés
            </p>''', unsafe_allow_html=True)

c1,c2 = st.columns([6,1], gap="large")

st.space("small")

with c1:
    if df_arbre is not None:
        nodes,edges = generer_arbre_dynamique(df_arbre)


config = Config(
    width='stretch', 
    height=500,
    edges={"selectionWidth":2.5},

    # === LA LOGIQUE DE CHEMIN LISIBLE ===
    hierarchical=True,               # Active l'alignement strict des nœuds
    levelSeparation=200,
    nodeSpacing=110,
    #treeSpacing=1000,
    direction='LR',                  # 'UD' (De haut en bas) ou 'LR' (De gauche à droite)
    sortMethod='directed',           # Aligne les nœuds selon le sens des flèches (Parent -> Enfant)
    parentCentralization=True,

    # On coupe la physique de répulsion aléatoire : l'arbre se range au millimètre
    physics=False,
    solver="hierarchicalRepulsion",
    minVelocity=1,
    maxVelocity=50,
    timeStep=0.50
)

# Affichage
with c1:
    with st.container(border=True):
        node_id_clique = agraph(nodes=nodes, edges=edges, config=config)

st.caption(f"L'arbre peut avoir des problèmes de génération quand on lui ajoute des domaines, dans ce cas là il faut rerun l'application (avec la touche R sur pc ou dans les options de la page")
if node_id_clique:

    if est_domaine_principal(df_arbre, node_id_clique):
        
        st.session_state.domaine_actif = node_id_clique
        
        st.switch_page("bureaux.py")
    else:
        st.sidebar.info("Ceci est une compétence finale, ou un hub.")
with c2:

    if st.button("Information Supplémentaire sur l'arbre"):
        info_arbre()
