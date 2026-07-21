import streamlit as st
import pandas as pd
import os
from utils.data import charger_donnees_user
from utils.progression import appliquer_atrophie, get_global_level
from utils.clan_func import joueur_in_clan, role_in_clan

# ------------------------------------------------------------------------------------
#   1. CONFIGURATION DE L'ÉTAT
# ------------------------------------------------------------------------------------

if "username" not in st.session_state:
    st.session_state.username = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------------------------------------------------------------------------
#   2. FONCTIONS DE GESTION DES UTILISATEURS
# ------------------------------------------------------------------------------------

def gerer_inscription(new_u, new_p):
    if not new_u or not new_p:
        st.error("Veuillez remplir tous les champs.")
        return
    
    file = "users.csv"
    # Charger ou créer le fichier des utilisateurs
    if os.path.exists(file):
        df = pd.read_csv(file)
    else:
        df = pd.DataFrame(columns=['user', 'pw'])

    # Vérifier si le pseudo existe déjà
    if new_u in df['user'].values:
        st.error("Ce pseudo est déjà utilisé par un autre héros.")
    else:
        # Ajouter le nouvel utilisateur
        new_row = pd.DataFrame([{'user': new_u, 'pw': new_p}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(file, index=False)
        
        # CRUCIAL : Créer le fichier de données du joueur immédiatement
        # pour éviter les erreurs au premier login
        charger_donnees_user(new_u) 
        
        st.success("Compte créé avec succès ! Tu peux maintenant te connecter.")

# ------------------------------------------------------------------------------------
#   3. DÉFINITION DE LA PAGE DE LOGIN (UTILS?)
# ------------------------------------------------------------------------------------

def login_page():
    st.space("medium")
    st.markdown("<h1 style='text-align: center; text-shadow: 0 0 50px #FFFFFF,0 0 100px #FFFFFF;font-size: 100px;font-weight: black;'>ACHIEVABLE GAME</h1>", unsafe_allow_html=True)
    st.space("medium")
    
    colonne_1,colonne_2,colonne_3 = st.columns([1,4,1])
    with colonne_2:
        tab_login, tab_sign_up = st.tabs(["🔒 Connexion", "📝 Créer un compte"])


        with tab_login:
            with st.container(border=True):
                u = st.text_input("Pseudo", key="login_user")
                p = st.text_input("Mot de passe", type="password", key="login_pw")
                if st.button("Entrer dans l'aventure"):
                    if os.path.exists("users.csv"):
                        df = pd.read_csv("users.csv")
                        user_match = df[(df['user'] == u) & (df['pw'].astype(str) == p)]
                        if not user_match.empty:
                            st.session_state.logged_in = True
                            st.session_state.username = u 
                            st.rerun()
                    st.error("Identifiants incorrects ou compte inexistant.")

        with tab_sign_up:
            with st.container(border=True):
                new_u = st.text_input("Choisir un pseudo", key="signup_user")
                new_p = st.text_input("Choisir un mot de passe", type="password", key="signup_pw")
                if st.button("Forger mon destin"):
                    gerer_inscription(new_u, new_p)

# ------------------------------------------------------------------------------------
#   4. NAVIGATION ET LOGIQUE GLOBALE
# ------------------------------------------------------------------------------------

login_screen = st.Page(login_page, title="Connexion", icon="🔒")
page_1 = st.Page("accueil.py", title="Accueil", icon="🏠")
page_2 = st.Page("arbre.py", title="Arbre des Compétences", icon="🌳")
page_3 = st.Page("bureaux.py", title="Bureaux de Domaine", icon="📂")
page_4 = st.Page("journal.py", title="Journal de Quêtes", icon="🗒️")
page_5 = st.Page("oracle.py", title="Antre de l'Oracle", icon="🔮")
page_6 = st.Page("clan.py", title="Clan", icon="🏛️")
page_7 = st.Page("base_domaines.py", title="Base de Domaine", icon="🗃️")
page_8 = st.Page("settings.py", title="Paramètres", icon="⚙️")
page_9 = st.Page("actu.py", title="Actualité", icon="📰")

st.set_page_config(layout="wide")

if not st.session_state.logged_in:
    pg = st.navigation([login_screen])
else:
    # ON NE CALCULE LE NIVEAU QUE SI ON EST CONNECTÉ (Bye bye data_None.csv !)
    if "atrophie_calculee" not in st.session_state:
        # On lance le calcul de perte d'XP une seule fois par session
        perte_detectee = appliquer_atrophie(st.session_state.username)
        if perte_detectee:
            st.toast("⚠️ Tes compétences s'atrophient par manque de pratique...", icon="📉")
        st.session_state.atrophie_calculee = True
    lvl_global = get_global_level(st.session_state.username)
    
    pg = st.navigation([page_1, page_2, page_3, page_4, page_5, page_6, page_7, page_8, page_9])

    if "admin" not in st.session_state:
        st.session_state.admin = False

    if "clan" not in st.session_state:
        st.session_state.clan = None
        joueur_in_clan(st.session_state.username)
    
    if "clan_role" not in st.session_state:
        st.session_state.clan_role = None
        role_in_clan(st.session_state.username,st.session_state.clan)

    with st.sidebar:
        st.sidebar.metric("🌟 Niveau Global", f"LVL {lvl_global}")
        st.sidebar.progress(lvl_global / 100)

pg.run()