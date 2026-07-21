import streamlit as st
import pandas as pd
from config import DATA_DOMAINE_DIR, DATA_ASSET_DIR
from utils.data import charger_donnees_user,sauvegarder_donnees_user
from utils.domains import ajouter_famille_domaine, supprimer_domaine, trier_domaines_utilisateur, trier_domaines

# ------------------------------------------------------------------------------------
#   1. VARIABLES UTILES
# ------------------------------------------------------------------------------------

username = st.session_state.username
df_user = charger_donnees_user(username)
liste_domaines_user = df_user['ID'].to_list()

if "suppression" not in st.session_state:
    st.session_state.suppression = ""

chemin = DATA_DOMAINE_DIR
chemin_domaine_csv = chemin / "domaine.csv"

chemin_asset = DATA_ASSET_DIR

# ------------------------------------------------------------------------------------
#   2. MANIPULATION DATAFRAME
# ------------------------------------------------------------------------------------

df_domaines = pd.read_csv(chemin_domaine_csv)
df_domaines_split = df_domaines.copy()
df_domaines_split['Parent'] = df_domaines_split['Parent'].str.split(';')

df_domaines_split = df_domaines_split.explode('Parent')

df_affichage = df_domaines_split[(df_domaines_split["ID"] != "GLO") & (df_domaines_split["ID"].isin(df_domaines_split["Parent"]))]
df_affichage = df_affichage.drop_duplicates(subset=['ID'], keep='first')

# ------------------------------------------------------------------------------------
#   3. PAGE
# ------------------------------------------------------------------------------------

st.markdown("""
<style>
.big-body-font {
    font-size:16px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.medium-body-font {
    font-size:16px !important;
}
</style>
""", unsafe_allow_html=True)

@st.dialog("Informations sur le fonctionnement des domaines", width="medium")
def information_sup():
    st.space("small")
    with st.container(border=True):
        st.markdown("""<p class='medium-body-font'>Quand vous ajoutez un  
                domaine, ces parents et composants sont automatiquement 
                ajoutés avec lui-même.</p>""", unsafe_allow_html=True)
        st.space("xxsmall")
        st.image(chemin_asset / "ajout_recursif_hres_02.png", width="stretch")
        st.space("xxsmall")
        st.markdown("""<p class='medium-body-font'>Inversement, quand vous supprimez un domaine, 
                si certain de ces parents ou enfants ne sont plus reliés
                à un domaine actif alors ils seront supprimés.</p>""", unsafe_allow_html=True)


st.title("Base de Domaines")
st.space("small")
st.markdown("""<p class='big-body-font'>ici vous trouverez les différents domaines existants, 
            avec leur sous domaines respectifs (et desfois partagés), 
            que vous pourrez ajouter à votre compte</p>""", unsafe_allow_html=True)
st.space("small")

if st.button("Information supplémentaire"):
    information_sup()

st.divider()

#-----------------------
#   Couleur badge

hub = "orange"
domaine = "yellow"
#-----------------------

@st.dialog("À savoir avant de supprimer un domaine", width="medium")
def pop_up_avant_suppression():
    st.write("Attention, si vous supprimer un domaine, et que ces enfants " \
    "se retrouvent sans parents ils seront automatiquement supprimés, " \
    "vous donc perderez toutes les informations qui lui sont liées (l'XP)")
    st.image(chemin_asset / "popup_suppression_domaine_hres_01.png", width="stretch")
    st.write("D'ailleurs, les parents du domaines que vous êtes en train de supprimer seront aussi supprimés si vous n'avez plus aucun de leurs enfants")
    c1,c2 = st.columns(2)
    with st.container(horizontal=True):

        if st.button("Revenir en arrière"):
            st.session_state.suppression = False
            st.rerun()

        st.space("stretch")

        if st.button("Continuer"):
            st.session_state.suppression = True
            edited_df = supprimer_domaine(l['ID'], username)
            sauvegarder_donnees_user(username,edited_df)
            trier_domaines_utilisateur(username)
            st.session_state.domaine_actif = None
            st.rerun()

colonne_ajouter,colonne_intervalle,colonne_supprimer = st.columns([0.5, 0.1 ,0.5])
with colonne_ajouter:
    st.header("Domaines disponibles")
    st.divider()
    for _, l in df_domaines[df_domaines["Type"] != "Composant"].iterrows():
        if l["ID"] != "GLO" and l["ID"] not in df_user["ID"].values:

            if ";" in l["Parent"]:
                l["Parent"] = l["Parent"].split(';')
            else:
                l["Parent"] = l["Parent"].split()

            if l["Parent"] in liste_domaines_user or df_user["ID"].isin(l["Parent"]).any():
                with st.container(border=True):
                    c1,c2,c3 = st.columns([0.5,0.4,0.4])
                    with c1:
                        if l["Type"] == "Hub":
                            st.badge(l["Label"], color=hub)
                        elif l["Type"] == "Domaine":
                            st.badge(l["Label"], color=domaine)
                    with c2:
                        if l["ID"] == "GLO":
                            pass
                        elif l["Parent"] == "GLO":
                            st.write("Parent: Global")

                        elif l["Parent"]:

                            if type(l["Parent"]) == list:
                                st.write("Parent:")
                                for parent in l["Parent"]:
                                    st.write(f"{df_domaines[df_domaines["ID"] == parent]["Label"].item()}")
                            else:
                                st.write("Parent:", df_domaines[df_domaines["ID"] == l["Parent"]]["Label"].item())
                    with c3:
                        if l["Label"] in df_user["Label"].values:
                            st.badge("✅ déjà posséder", color="green")
                        
                        else:
                            if st.button("Ajouter", key=f"btn_{l['ID']}"):
                                edited_df = pd.concat([df_user,ajouter_famille_domaine(l["ID"], df_user)], ignore_index=True)
                                sauvegarder_donnees_user(username,edited_df)
                                trier_domaines_utilisateur(username)
                                st.rerun()


with colonne_supprimer:
    st.header("Vos domaines")
    st.divider()
    for _, l in df_user[df_user["Type"] != "Composant"].iterrows():
        if (l['ID'] in liste_domaines_user) and (l["ID"] != "GLO"):
            with st.container(border=True):
                c1,c2,c3 = st.columns([0.7,0.4,0.4])
                with c1:
                    if l["Type"] == "Hub":
                        st.badge(l["Label"], color=hub)
                    elif l["Type"] == "Domaine":
                        st.badge(l["Label"], color=domaine)
                with c2:
                    if l["ID"] == "GLO":
                        pass
                    elif l["Parent"] == "GLO":
                        st.write("Parent: Global")
                    elif l["Parent"]:
                        if ";" in l["Parent"]:
                            l["Parent"] = l["Parent"].split(';')
                            st.write("Parent:")
                            for parent in l["Parent"]:
                                st.write(f"{df_affichage[df_affichage["ID"] == parent]["Label"].item()}")
                        else:
                            st.write("Parent:", df_affichage[df_affichage["ID"] == l["Parent"]]["Label"].item())
                with c3:
                    if l["ID"] in df_user["ID"].values:
                        if st.button("Supprimer", key=f"btn{l['ID']}c2"):
                            pop_up_avant_suppression()

st.divider()