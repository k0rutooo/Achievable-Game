import streamlit as st
from datetime import date
import pandas as pd
import time
import gspread
from google.oauth2.service_account import Credentials
import datetime
from utils.progression import get_global_level
from config import DATA_CLAN_DIR

# ------------------------------------------------------------------------------------
#   CHAT CLAN INIT
# ------------------------------------------------------------------------------------

def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

gc = init_connection()
spreadsheet = gc.open("achievable-game-clan-chat")

# ------------------------------------------------------------------------------------
#   CHEMINS
# ------------------------------------------------------------------------------------

path_dossier_clans = DATA_CLAN_DIR

# ------------------------------------------------------------------------------------
#   FONCTIONS
# ------------------------------------------------------------------------------------

def liste_clans():
    noms_clans = [n.name for n in path_dossier_clans.iterdir() if n.is_file()]
    return noms_clans

def creer_clan(nom, user):

    chemin_fichier = path_dossier_clans / f"{nom}.csv"

    if chemin_fichier.exists():
        return st.error("Erreur, un clan existe déjà avec le même nom")
    else:
        niveau = get_global_level(user)

        data = {
        "nom": [nom, ""],
        "date_creation": [date.today().strftime('%Y-%m-%d'), date.today().strftime('%Y-%m-%d')],
        "membre": ["", user],
        "mode": ["ouvert",""],
        "niveau": [1, niveau],
        "xp": [0, ""],
        "role": ["", "chef"]
        }

        df_clan = pd.DataFrame(data)
        df_clan.to_csv(chemin_fichier,index=False, encoding="utf8")
        creer_chat(nom)
        envoyer_message(nom,user,f"{user} vient de créer {nom}, je vous souhaite une excellente aventure!")
        return st.success("Clan créé avec succès")
    

def rejoindre_clan(clan,user):
    niveau = get_global_level(user)
    if st.session_state.get('clan') is None:
        chemin_fichier = path_dossier_clans / f"{clan}.csv"
        nouvelle_ligne = {
            "nom":"",
            "date_rejoint": date.today().strftime("%Y-%m-%d"),
            "mode":"",
            "membre":user,
            "niveau":niveau,
            "xp": "",
            "role":"membre"
        }
        df_clan = pd.read_csv(chemin_fichier)
        df_clan.loc[len(df_clan)] = nouvelle_ligne
        df_clan.to_csv(chemin_fichier, index=False)
        st.success("bienvenue dans le clan!")
        st.session_state.onglet_clan = "Mon Clan"
        envoyer_message(clan,user,f"{user} vient de rejoindre {clan}")
        st.rerun()
    else:
        st.error("joueur déjà dans un clan")

def quitter_clan(clan,user):
    chemin_fichier = path_dossier_clans / f"{clan}.csv"
    if chemin_fichier.exists():
        df = pd.read_csv(chemin_fichier)
        df = df[df['membre'] != user]
        df.to_csv(chemin_fichier, index=False)
        envoyer_message(clan,user,f"{user} vient de quitter {clan}")

        st.session_state.clan = None
        st.session_state.clan_role = None
        st.rerun()

def joueur_in_clan(user):

    for f in path_dossier_clans.glob("*.csv"):
        df = pd.read_csv(f)
        if "membre" in df.columns and (df["membre"] == user).any():
            st.session_state.clan = f.stem
            return df
        
    st.session_state.clan = None
    st.session_state.clan_role = None
    return None
        
def chercher_clan(entrée):
    noms_clans = liste_clans()
    recherche_liste = []

    df_clans = pd.DataFrame(noms_clans)
    try:
        df_clans["recherche"] = df_clans[df_clans.apply(lambda row: row.astype(str).str.contains(entrée, case=False, na=False).any(), axis=1)].head(5)
        recherche_liste = df_clans["recherche"].dropna().tolist()

        liste_dataframes = [pd.read_csv(path_dossier_clans / str(f)) for f in recherche_liste]
        try:
            df_complet = pd.concat([df.iloc[0:1] for df in liste_dataframes], ignore_index=True)
            return df_complet
        except ValueError:
            pass
    except ValueError:
        pass

def classer_clans():
    for f in path_dossier_clans.glob("*.csv"):
        df_classement = pd.read_csv(f)
        taille = df_classement["membre"].sizes
        return taille
    
def afficher_membre(clan):
    chemin_fichier = path_dossier_clans / f"{clan}.csv"
    with open(chemin_fichier, mode="r") as f:
        df = pd.read_csv(f)
        df_membre = df.dropna(subset=["membre", "niveau", "role"])
        return df_membre

def role_in_clan(clan,user):
    if clan is not None and clan != "":
        chemin_fichier = path_dossier_clans / f'{clan}.csv'
        if chemin_fichier.exists():
            df_clan = pd.read_csv(chemin_fichier)
            mask =  df_clan["membre"] == user
            if mask.any():
                role = df_clan.loc[mask, 'role'].values[0]
                st.session_state.clan_role = role
                return
    
    st.session_state.role_clan = None

def supprimer_clan(clan):
    chemin_fichier = path_dossier_clans / f"{clan}.csv"
    if chemin_fichier.exists():
        chemin_fichier.unlink()
        supprimer_chat(clan)
        st.success("clan correctement supprimé")
        time.sleep(1)
        return
    else:
        st.error("le fichier n'existe pas")

def clan_option(clan,mode):
    chemin_fichier = path_dossier_clans / f"{clan}.csv"
    if chemin_fichier.exists():
        df_clan = pd.read_csv(chemin_fichier)
        df_clan.loc[df_clan["nom"] == clan, "mode"] = mode
        df_clan.to_csv(chemin_fichier, index=False)

def charger_donnees_clan(clan):
    chemin_fichier = path_dossier_clans / f"{clan}.csv"
    df_clan = pd.read_csv(chemin_fichier)
    df_clan_option = df_clan.loc[df_clan["nom"] == clan]
    return df_clan_option

def membre_par_clan(clan):
    chemin_fichier = path_dossier_clans / f"{clan}.csv"
    df = pd.read_csv(chemin_fichier)
    df = df.dropna(subset=['membre'])
    return len(df)


def actualiser_niveau_membre(username,clan):
    chemin_fichier = path_dossier_clans / f"{clan}.csv"
    if chemin_fichier.exists():
        df_clan = pd.read_csv(chemin_fichier)
        df_clan.loc[df_clan["membre"] == username, "niveau"] = get_global_level(username)
        df_clan.to_csv(chemin_fichier, index=False)


# ------------------------------------------------------------------------------------
#   CHAT DE CLAN
# ------------------------------------------------------------------------------------

MAX_MESSAGES = 60
MAX_AGE_MINUTES = 120

def creer_chat(nom_chat):
    try:
        spreadsheet.worksheet(nom_chat)
    except gspread.exceptions.WorksheetNotFound:
        nouveau_chat = spreadsheet.add_worksheet(title=nom_chat, rows="100", cols="3")
        nouveau_chat.append_row(["Timestamp", "User", "Message"])

def supprimer_chat(nom_chat):
    try:
        onglet_chat = spreadsheet.worksheet(nom_chat)
        spreadsheet.del_worksheet(onglet_chat)
    except gspread.exceptions.WorksheetNotFound:
        pass

def nettoyer_onglet_sheet(nom_chat):
    worksheet = spreadsheet.worksheet(nom_chat)
    all_records = worksheet.get_all_records() # <--- 1 requête

    if not all_records:
        return []
    
    maintenant = datetime.datetime.now()
    ligne_valide = []
    modifie = False

    if len(all_records) > MAX_MESSAGES:
        all_records = all_records[-MAX_MESSAGES:]
        modifie = True

    for record in all_records:
        try:
            msg_temps = datetime.datetime.strptime(record["Timestamp"], "%Y-%m-%d %H:%M:%S")
            age_en_minutes = (maintenant - msg_temps).total_seconds() / 60

            if age_en_minutes <= MAX_AGE_MINUTES:
                ligne_valide.append([record["Timestamp"], record["User"], record["Message"]])
            else:
                modifie = True
        except ValueError:
            modifie = True
    
    if modifie:
        worksheet.clear()

        payload = [["Timestamp", "User", "Message"]] + ligne_valide

        worksheet.update(range_name="A1", values=payload)

    return ligne_valide

def envoyer_message(nom_chat,username, texte_message):
    onglet = spreadsheet.worksheet(nom_chat)
    timestamp_maintenant = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nouvelle_ligne = [timestamp_maintenant, username, texte_message]

    onglet.append_row(nouvelle_ligne)

# ------------------------------------------------------------------------------------
#   NIVEAU CLAN
# ------------------------------------------------------------------------------------