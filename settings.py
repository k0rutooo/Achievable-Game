import streamlit as st
import time
from utils.game_settings import obtenir_difficulte_jeu, sauvegarder_difficulte_jeu

user = st.session_state.username

#ici mettre de quoi importer et exporter les données utilisateurs
#mettre des commentaires partout dans le programme pour qu'il soit facilement compréhensible et modifiable par tout le monde

#--------------------------------------------------------
#   DIALOG
#--------------------------------------------------------

@st.dialog("Passer en mode admin")
def mode_admin(admin):
    st.markdown("""Le mode admin permet d'afficher plus d'informations, 
                pour réparer des bugs ou tester de nouvelles fonctionalitées""")

    if admin == False:
        with st.form("form admin"):
            
            st.write("vous êtes actuellement en mode utilisateur standart")
            password = st.text_input("Veuillez rentrer le mot de passe")

            submitted = st.form_submit_button("Continuer")
            if submitted:
                if  password == st.secrets["admin_mode"]["admin_password"]:
                    st.success("Mot de passe correct")
                    st.session_state.admin = True
                    st.rerun()
                else:
                    st.error("Mot de passe incorrect")
            
    if admin == True:
        st.write("Vous êtes actuellement en mode admin")
        st.write("")
        with st.container(horizontal=True):
            if st.button("retourner en arrière"):
                st.rerun()
            st.space("stretch")
            if st.button("quitter le mode admin"):
                st.session_state.admin = False
                st.rerun()

#--------------------------------------------------------
#   CODE
#--------------------------------------------------------

# --- Dans bureaux.py ou accueil.py (Onglet Gestion/Paramètres) ---
st.title("⚙️ Paramètres du Monde")
st.space("small")

st.divider()

colonne1, colonne2 = st.columns([5,1])

with colonne1:
    if st.button("mode admin"):
        mode_admin(st.session_state.admin)

with colonne2:
    if st.session_state.admin == False:
        st.markdown("Actuellement en mode :blue-background[utilisateur]")
    elif st.session_state.admin == True:
        st.markdown("Actuellement en mode :blue-background[admin]")

if st.button("Déconnexion"):
    st.session_state.logged_in = False
    st.rerun()