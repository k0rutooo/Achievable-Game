import streamlit as st
from datetime import date
import pandas as pd
import time
import io
import gspread
from google.oauth2.service_account import Credentials
import datetime
from connexion import supabase
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
bucket_name = "clan_data"

# ------------------------------------------------------------------------------------
#   FONCTIONS
# ------------------------------------------------------------------------------------

def lire_csv_cloud(nom_fichier):
    octets = supabase.storage.from_(bucket_name).download(nom_fichier)
    return pd.read_csv(io.BytesIO(octets))

def enregistrer_csv_cloud(df,nom_fichier):
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode('utf-8')
    
    supabase.storage.from_(bucket_name).upload(
        path=nom_fichier,
        file=csv_bytes,
        file_options={"content-type": "text/csv", "x-upsert": "true"}
    )

def liste_clans():
    bucket_name = "clan_data"
    
    # 1. Récupérer la liste brute des dictionnaires depuis Supabase
    fichiers_bruts = supabase.storage.from_(bucket_name).list()
    
    # 2. Extraire uniquement le nom (clé 'name') si c'est un fichier CSV
    # et retirer le '.csv' pour obtenir le nom propre du clan
    noms_propres = [
        f['name'].replace('.csv', '') 
        for f in fichiers_bruts 
        if f['name'].endswith('.csv')
    ]

    return noms_propres # Renvoie maintenant : ['clan_alpha', 'clan_beta']

def creer_clan(nom, user):

    nom_fichier = f"{nom}.csv"

    try:
        # 1. Tenter de télécharger le fichier depuis Supabase
        reponse_octets = supabase.storage.from_(bucket_name).download(nom_fichier)
        return st.error("Erreur, un clan existe déjà avec le même nom")

    #si on n'arrive pas à installer le fichier du clan, alors il n'existe pas et on le créé
    except Exception:
        pass

    
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
    csv_buffer = io.StringIO()
    df_clan.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode('utf-8')
    
    supabase.storage.from_(bucket_name).upload(
        path=nom_fichier,
        file=csv_bytes,
        file_options={"content-type": "text/csv", "x-upsert": "true"}
    )
    creer_chat(nom)
    envoyer_message(nom,user,f"{user} vient de créer {nom}, je vous souhaite une excellente aventure!")
    return st.success("Clan créé avec succès")


def rejoindre_clan(clan,user):
    niveau = get_global_level(user)
    if st.session_state.get('clan') is None:

        nom_fichier = f"{clan}.csv"
        nouvelle_ligne = {
            "nom":"",
            "date_rejoint": date.today().strftime("%Y-%m-%d"),
            "mode":"",
            "membre":user,
            "niveau":niveau,
            "xp": "",
            "role":"membre"
        }
        reponse_octets = supabase.storage.from_(bucket_name).download(nom_fichier)
                
            # Équivalent de os.path.getsize(filename) > 0
        if reponse_octets and len(reponse_octets) > 0:
            df_clan = pd.read_csv(io.BytesIO(reponse_octets))
            df_clan.loc[len(df_clan)] = nouvelle_ligne
            csv_buffer = io.StringIO()
            df_clan.to_csv(csv_buffer, index=False)
            csv_bytes = csv_buffer.getvalue().encode('utf-8')
                
            supabase.storage.from_(bucket_name).upload(
                path=nom_fichier,
                file=csv_bytes,
                file_options={"content-type": "text/csv", "x-upsert": "true"}
            )
            st.success("bienvenue dans le clan!")
            st.session_state.onglet_clan = "Mon Clan"
            envoyer_message(clan,user,f"{user} vient de rejoindre {clan}")
            st.rerun()
    else:
        st.error("joueur déjà dans un clan")

def quitter_clan(clan,user):
    nom_fichier = f"{clan}.csv"
    if nom_fichier.exists():
        df = pd.read_csv(nom_fichier)
        df = df[df['membre'] != user]
        df.to_csv(nom_fichier, index=False)
        envoyer_message(clan,user,f"{user} vient de quitter {clan}")

        st.session_state.clan = None
        st.session_state.clan_role = None
        st.rerun()

def joueur_in_clan(user):

    try:
        # 1. Lister tous les fichiers présents dans le bucket Supabase
        # (Équivalent cloud de path.glob("*.csv"))
        fichiers = supabase.storage.from_(bucket_name).list()
        
        # 2. Boucler sur la liste des fichiers trouvés
        for f in fichiers:
            nom_fichier = f['name']
            
            # On s'assure qu'on ne traite que les fichiers CSV
            if nom_fichier.endswith('.csv'):
                # 3. Télécharger le fichier en octets
                reponse_octets = supabase.storage.from_(bucket_name).download(nom_fichier)
                df = pd.read_csv(io.BytesIO(reponse_octets))
                
                # 4. Votre logique métier d'origine reste inchangée
                if "membre" in df.columns and (df["membre"] == user).any():
                    # f.stem en local correspond au nom du fichier sans le ".csv"
                    nom_sans_extension = nom_fichier.replace('.csv', '')
                    st.session_state.clan = nom_sans_extension
                    return df
                    
    except Exception as e:
        st.session_state.clan = None
        st.session_state.clan_role = None
        st.error(f"Erreur lors de la recherche du clan : {e}")
        
    return None  # Retourne None si l'utilisateur n'est trouvé dans aucun clan


def chercher_clan(entrée):
    # 1. On récupère la liste des noms de clans depuis Supabase (ex: ['clan_alpha', 'clan_beta'])
    noms_clans = liste_clans()
    
    # 2. Filtrer les noms de clans qui contiennent le mot-clé 'entrée' (Insensible à la casse)
    # On limite à 5 résultats maximum comme votre .head(5) d'origine
    clans_trouves = [clan for clan in noms_clans if entrée.lower() in clan.lower()][:5]

    # Si aucun clan ne correspond, on s'arrête ici proprement
    if not clans_trouves:
        return pd.DataFrame()

    # 3. On recrée les vrais noms de fichiers requis par Supabase (.csv)
    recherche_liste = [f"{clan}.csv" for clan in clans_trouves]

    try:
        # 4. Téléchargement des 5 fichiers en mémoire
        liste_dataframes = [lire_csv_cloud(f) for f in recherche_liste]
        
        # 5. Concaténation de la première ligne de chaque DataFrame
        df_complet = pd.concat([df.iloc[0:1] for df in liste_dataframes], ignore_index=True)
        return df_complet
        
    except Exception as e:
        st.error(f"Erreur lors de la lecture des fichiers de clans : {e}")
        return pd.DataFrame()

    
def afficher_membre(clan):
    nom_fichier = f"{clan}.csv"
    reponse_octets = supabase.storage.from_(bucket_name).download(nom_fichier)

    if reponse_octets and len(reponse_octets) > 0:
        df_membre = pd.read_csv(io.BytesIO(reponse_octets))
        df_membre = df_membre.dropna(subset=["membre", "niveau", "role"])
        return df_membre

def role_in_clan(clan,user):
    if clan is not None and clan != "":
        nom_fichier = f'{clan}.csv'
        try:
            df_clan = lire_csv_cloud(nom_fichier)
            mask =  df_clan["membre"] == user
            if mask.any():
                role = df_clan.loc[mask, 'role'].values[0]
                st.session_state.clan_role = role
                return
        except:
            pass
    
    st.session_state.role_clan = None

def supprimer_clan(clan):
    nom_fichier = f"{clan}.csv"
    try:
        response = (
            supabase.storage
            .from_(bucket_name)
            .remove([nom_fichier])
        )
        supprimer_chat(clan)
        st.session_state.clan = None
        st.session_state.role_clan = None
        st.success("clan correctement supprimé")
        time.sleep(1)
        return
    except:
        st.error("le fichier n'existe pas")

def clan_option(clan,mode):
    nom_fichier = f"{clan}.csv"
    try:
        df_clan = lire_csv_cloud(nom_fichier)
        df_clan.loc[df_clan["nom"] == clan, "mode"] = mode
        enregistrer_csv_cloud(df_clan, nom_fichier)
    except Exception:
        st.error("Une erreur est survenue, veuillez réessayer plus tard")

def charger_donnees_clan(clan):
    nom_fichier = f"{clan}.csv"
    df_clan = lire_csv_cloud(nom_fichier)
    df_clan_option = df_clan.loc[df_clan["nom"] == clan]
    return df_clan_option

def membre_par_clan(clan):
    nom_fichier = f"{clan}.csv"
    df = lire_csv_cloud(nom_fichier)
    df = df.dropna(subset=['membre'])
    return len(df)


def actualiser_niveau_membre(username,clan):
    nom_fichier = f"{clan}.csv"
    try:
        df_clan = lire_csv_cloud(nom_fichier)
        df_clan.loc[df_clan["membre"] == username, "niveau"] = get_global_level(username)
        enregistrer_csv_cloud(df_clan, nom_fichier)
    except Exception:
        pass


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