import streamlit as st
import time
from utils.clan_func import creer_clan, joueur_in_clan, chercher_clan, classer_clans, rejoindre_clan, quitter_clan, afficher_membre, creer_chat,supprimer_chat, nettoyer_onglet_sheet, envoyer_message, role_in_clan, supprimer_clan, clan_option, charger_donnees_clan, membre_par_clan, actualiser_niveau_membre
from utils.security import securite_page
from utils.utils_asset import get_rang_image

# ------------------------------------------------------------------------------------
#   CONFIGURATION
# ------------------------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="Clan")

user = st.session_state.username

if "onglet_clan" not in st.session_state:
    st.session_state.onglet_clan = "Mon Clan"

securite_page()

debug = False

# ------------------------------------------------------------------------------------
#   SYNCHRONISATION
# ------------------------------------------------------------------------------------

joueur_in_clan(user)
role_in_clan(st.session_state.get('clan'), user)


clan_actuel = st.session_state.clan
role_actuel = st.session_state.clan_role

# DÉBUG
if debug:
    st.write(user,clan_actuel,role_actuel)

# ------------------------------------------------------------------------------------
#   FRAGMENT 
# ------------------------------------------------------------------------------------

@st.fragment(run_every=5)
def afficher_chat_actualise():

    if not st.session_state.clan:
        st.info("Rejoins un clan pour acceder au chat")
        return
    
    if st.session_state.onglet_clan != "Mon Clan":
        return
    
    with st.container(border=True, height=400):
        messages_existants = nettoyer_onglet_sheet(st.session_state.clan)

        if not messages_existants:
            st.info("Aucun message ici, soyez le premier à écrire")
        else:
            for msg in messages_existants:
                timestamp = msg[0]
                pseudo = msg[1]
                texte_message = msg[2]

                with st.chat_message(pseudo):
                    st.write(f"**:red[{pseudo} {timestamp}]**")
                    st.write(texte_message)

# ------------------------------------------------------------------------------------
#   NAVIGATION
# ------------------------------------------------------------------------------------

cols_nav = st.columns([1, 1, 1])
if cols_nav[0].button("🔰 Mon Clan", use_container_width=True):
    st.session_state.onglet_clan = "Mon Clan"
    st.rerun()
if cols_nav[1].button("👥 Chercher", use_container_width=True):
    st.session_state.onglet_clan = "Chercher"
    st.rerun()
if cols_nav[2].button("🏆 Classement", use_container_width=True):
    st.session_state.onglet_clan = "Classement"
    st.rerun()

# ------------------------------------------------------------------------------------
#   MON CLAN
# ------------------------------------------------------------------------------------
if st.session_state.onglet_clan == "Mon Clan":

    if st.session_state.clan == None:

        st.title("créer un clan")
        with st.expander("créer un clan", expanded=False):
            with st.form("nouveau clan", clear_on_submit=True):
                nom = st.text_input("nom du clan")
                if st.form_submit_button("créer le clan"):
                    creer_clan(nom, user)
                    time.sleep(2)
                    st.rerun()

    elif st.session_state.clan != None:

        df_membre = afficher_membre(st.session_state.clan)
        actualiser_niveau_membre(user,st.session_state.clan)
        
        st.title(clan_actuel)

        t1, t2, t3, t4 = st.tabs(["Général", "Chat", "Quête de clan","Paramètres"])

        with t1:

            colonne1, colonne2, colonne3 = st.columns([3,2,2])

            with colonne1:

                    with st.container(border=True):
                        c1, c2 = st.columns([0.4,0.4])
                        with c1:
                            st.markdown("**MEMBRE**")
                        with c2:
                            st.markdown("**RÔLE**", text_alignment="center")
            with colonne2:
                with st.container(border=True, width=85):
                    st.markdown("**NIVEAU**")

            for _, l in df_membre.iterrows():
                role = l["role"]

                colonne1, colonne2, colonne3 = st.columns([3,2,2])

                with colonne1:
                    with st.container(border=True):
                        c1,c2 = st.columns([1,1])
                        with c1:
                            st.markdown(f"""#### **{l["membre"]}**""",anchors=False ,text_alignment="left")
                        with c2:
                            st.markdown(f"""#### **{role}**""", anchors=False ,text_alignment="center")

                with colonne2:
                    with st.container(border=True, width="content"):
                        st.image(get_rang_image(l["niveau"]), width=50)

        with t2:

            afficher_chat_actualise()
                    
            if message := st.chat_input("écrire un message..."):
                if message.strip() != "":
                    
                    envoyer_message(st.session_state.clan, user, message)
                    st.rerun()
            
            st.caption("le chat à une limite de messages par minute, par respect pour votre clan veuillez ne pas spammer")

        with t3:
            st.title("coming soon")

        with t4:
            st.subheader("Options du Clan")

            df_clan = charger_donnees_clan(clan_actuel)

            if st.button("quitter clan"):
                quitter_clan(st.session_state.clan, user)
                st.rerun()
            if role_actuel == "chef":
                st.divider()
                st.subheader('Options réservée')

                c1,c2 = st.columns([1,1])

                with c1:
                    mode = st.menu_button("Accès au Clan", options=['ouvert','fermé'])
                    if mode:
                        clan_option(clan_actuel, mode)
                        st.rerun()
                    if st.button("supprimer le clan"):
                        supprimer_clan(clan_actuel)
                        st.rerun()
                
                with c2:
                    st.write(df_clan["mode"].to_string(index=False))

# ------------------------------------------------------------------------------------
#   RECHERCHE
# ------------------------------------------------------------------------------------
if st.session_state.onglet_clan == "Chercher":
        
    recherche = st.text_input("Entrez le nom d'un clan")
    df_recherche = chercher_clan(recherche)

    with st.container(border=True):
        c1, c2, c3, c4, c5 = st.columns([0.4,0.4,0.4, 0.4, 0.4])
        with c1:
            st.markdown("**NOM DU CLAN**")
        with c2:
            st.markdown("**MEMBRES**")
        with c3:
            st.markdown("**NIVEAU**")
        with c4:
            st.markdown("**STATUT**")
        with c5:
            st.markdown("**REJOINDRE**")

    try:
        for _, clan in df_recherche.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([0.4,0.4,0.4, 0.4, 0.4])
                with c1:
                    st.write(clan["nom"])
                with c2:
                    st.markdown(membre_par_clan(clan["nom"]))
                with c3:
                    st.markdown('...')
                with c4:
                    mode = clan["mode"]
                    st.write(mode)
                with c5:
                    if mode == "ouvert":
                        if st.button("rejoindre", key=f"btn_{clan['nom']}"):
                            rejoindre_clan(clan["nom"],user)
    except AttributeError:
        st.write("aucun clan")

# ------------------------------------------------------------------------------------
#   CLASSEMENT
# ------------------------------------------------------------------------------------
if st.session_state.onglet_clan == "Classement":
        st.title("coming soon...")