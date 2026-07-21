import streamlit as st
import pandas as pd
from utils.data import charger_donnees_user, charger_quetes_user
from utils.quests import creer_quete, supprimer_quete, valider_quete

df = charger_donnees_user
df_q = charger_quetes_user(st.session_state.username)

# ------------------------------------------------------------------------------------
#   INTERFACE
# ------------------------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="Journal de Quêtes")

tab1, tab2, tab3 = st.tabs(["Quêtes Active","Historique","Création de Quêtes"])

# ------------------------------------------------------------------------------------
#   QUÊTES EN COURS
# ------------------------------------------------------------------------------------

with tab1:
    st.title("🎯 Quêtes en cours")

    df_q = charger_quetes_user(st.session_state.username)

    # On ne montre que les quêtes pas encore terminées
    quetes_actives = df_q[df_q['Statut'] == "En cours"]

    if quetes_actives.empty:
        st.info("Ton carnet de quêtes est vide. Crée-en une pour progresser !")
    else:
        for _, quete in quetes_actives.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([0.8, 0.2])
                with c1:
                    st.write(f"**{quete['Titre']}**")
                    st.caption(f"📍 {quete['ID_Competence']}  |  🏆 {quete['XP_Recompense']} XP")
                with c2:
                    if st.button("✅", key=f"btn_{quete['ID_Quete']}"):
                        valider_quete(st.session_state.username, quete['ID_Quete'])
                        st.rerun()
                    if st.button("🗑️", key=f"del_{quete['ID_Quete']}"):
                        supprimer_quete(st.session_state.username, quete['ID_Quete'])
                        st.rerun()

# ------------------------------------------------------------------------------------
#   HISTORIQUE DE QUÊTES
# ------------------------------------------------------------------------------------

with tab2:
    st.title("🎯 Quêtes Terminées")

    df_h = charger_quetes_user(st.session_state.username)

    # On ne montre que les quêtes terminées, triées par date de complétion
    quetes_terminees = df_h[df_h['Statut'] == "Terminée"]

    if not quetes_terminees.empty:
        quetes_terminees = quetes_terminees.copy()
        quetes_terminees['Date_Completion_Sort'] = pd.to_datetime(
            quetes_terminees['Date_Completion'], dayfirst=True, errors='coerce'
        )
        quetes_terminees = quetes_terminees.sort_values(
            by='Date_Completion_Sort', ascending=False, na_position='last'
        )

    if quetes_terminees.empty:
        st.info("Ton carnet de quêtes est vide. Crée-en une pour progresser !")
    else:
        for _, quete in quetes_terminees.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([0.8, 0.2])
                with c1:
                    st.write(f"**{quete['Titre']}**")
                    st.caption(f"📍 {quete['ID_Competence']}  |  🏆 {quete['XP_Recompense']} XP | {quete['Date_Completion']}")

# ------------------------------------------------------------------------------------
#   CRÉATION DE QUÊTES
# ------------------------------------------------------------------------------------

with tab3:
    st.title("🛡️ Tableau des Quêtes")

# 1. On récupère les compétences disponibles pour le menu déroulant
    df_quete = charger_donnees_user(st.session_state.username)
    df_xp = df_quete[df_quete['Parent'] != 'META'].copy()

    # On filtre : on garde les lignes dont l'ID n'est PAS présent dans la colonne 'Parent'
    # On exclut aussi les lignes où l'ID est vide ou "Global" par sécurité
    mask_feuilles = ~df_xp['ID'].isin(df_xp['Parent'])
    df_feuilles = df_xp[mask_feuilles]

    options_quetes = dict(zip(df_feuilles['Label'], df_feuilles['ID']))

    # 2. Création du formulaire
    with st.expander("➕ Forger une nouvelle quête", expanded=False):
        with st.form("form_nouvelle_quete"):
            titre = st.text_input("Nom de la quête")
            # L'utilisateur choisit le Label, mais on récupérera l'ID
            label_choisi = st.selectbox("Compétence liée", options=options_quetes.keys())
            comp_id = options_quetes[label_choisi] # On récupère l'ID (ex: MUS)
            
            xp_gain = st.number_input("Récompense XP", value=50)
            submit = st.form_submit_button("Forger la quête")
            
            if submit:
                creer_quete(st.session_state.username, comp_id, titre, xp_gain)
                st.rerun()
            else:
                st.error("Donne un nom à ta quête, aventurier !")