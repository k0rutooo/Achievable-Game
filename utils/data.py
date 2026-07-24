import os
import io
from connexion import supabase
from datetime import date

import pandas as pd


USER_DATA_DIR = "data/user_data"
QUEST_DATA_DIR = "data/quest_data"
USER_COLUMNS = ["ID", "Parent", "Label", "XP", "Derniere_Activite"]
QUEST_COLUMNS = [
    "ID_Quete",
    "ID_Competence",
    "Titre",
    "XP_Recompense",
    "Statut",
    "Type",
    "Date_Creation",
    "Date_Completion",
]


def _ensure_parent_dir(filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)


def get_user_data_path(username):
    return f"{USER_DATA_DIR}/data_{username}.csv"


def get_quest_data_path(username):
    return f"{QUEST_DATA_DIR}/quests_{username}.csv"


def charger_donnees_user(username):
    nom_fichier = f"user_domaines/{username}.csv"
    bucket_name = "user_data"  # Le nom du bucket créé sur Supabase

    try:
        # 1. Tenter de télécharger le fichier depuis Supabase
        reponse_octets = supabase.storage.from_(bucket_name).download(nom_fichier)
        
        # Équivalent de os.path.getsize(filename) > 0
        if reponse_octets and len(reponse_octets) > 0:
            df = pd.read_csv(io.BytesIO(reponse_octets))
            
            # Vérification et mise à jour de la colonne manquante
            if "Derniere_Activite" not in df.columns:
                df["Derniere_Activite"] = date.today().strftime("%Y-%m-%d")
                # Sauvegarde immédiate de la correction sur Supabase
                sauvegarder_donnees_user(nom_fichier, df)
            return df
            
    except Exception:
        # Si le fichier n'existe pas ou qu'une erreur survient, on passe à la création du profil par défaut
        pass

    # 2. Création du DataFrame par défaut (si le fichier n'existait pas sur Supabase)
    df = pd.DataFrame(columns=USER_COLUMNS)
    nouvelle_ligne = pd.DataFrame(
        [
            {
                "ID": "GLO",
                "Label": "Global",
                "Parent": "",
                "XP": 0,
                "Derniere_Activite": date.today().strftime("%Y-%m-%d"),
                "Type": "Hub"
            }
        ]
    )
    df = pd.concat([df, nouvelle_ligne], ignore_index=True)

    # Envoi du nouveau profil utilisateur sur Supabase
    sauvegarder_donnees_user(username, df)
    return df


def sauvegarder_donnees_user(username, edited_df):
    """Remplace l'ancienne sauvegarde locale par un envoi sur Supabase"""
    # 1. On définit le nom du fichier cible sur le Cloud
    nom_fichier = f"user_domaines/{username}.csv"
    bucket_name = "user_data"
    
    # 2. On transforme le DataFrame modifié en octets (en mémoire)
    csv_buffer = io.StringIO()
    edited_df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode('utf-8')
    
    # 3. On pousse le fichier sur Supabase (l'option x-upsert écrase l'ancienne version)
    supabase.storage.from_(bucket_name).upload(
        path=nom_fichier,
        file=csv_bytes,
        file_options={"content-type": "text/csv", "x-upsert": "true"}
    )


def charger_quetes_user(username):
    nom_fichier = f"quests_{username}.csv"
    bucket_name = "user_quest"

    try:
        reponse_octets = supabase.storage.from_(bucket_name).download(nom_fichier)
        if reponse_octets and len(reponse_octets) > 0:
            df = pd.read_csv(io.BytesIO(reponse_octets), dtype={"Date_Creation": str, "Date_Completion": str})
            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
            for col in QUEST_COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            return df

    except Exception:
        df = pd.DataFrame(columns=QUEST_COLUMNS)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode('utf-8')
        
        supabase.storage.from_(bucket_name).upload(
            path=nom_fichier,
            file=csv_bytes,
            file_options={"content-type": "text/csv", "x-upsert": "true"}
        )
        return df


def sauvegarder_quetes_user(username, df_q):
    nom_fichier = f"quests_{username}.csv"
    bucket_name = "user_quest"

    csv_buffer = io.StringIO()
    df_q.to_csv(csv_buffer, index=False)
    print(df_q)
    csv_bytes = csv_buffer.getvalue().encode('utf-8')
    
    supabase.storage.from_(bucket_name).upload(
        path=nom_fichier,
        file=csv_bytes,
        file_options={"content-type": "text/csv", "x-upsert": "true"}
    )