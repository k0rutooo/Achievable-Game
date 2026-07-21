import os
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
    filename = get_user_data_path(username)
    _ensure_parent_dir(filename)

    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        try:
            df = pd.read_csv(filename)
            if "Derniere_Activite" not in df.columns:
                df["Derniere_Activite"] = date.today().strftime("%Y-%m-%d")
                df.to_csv(filename, index=False)
            return df
        except Exception:
            pass

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
    df.to_csv(filename, index=False)
    return df


def sauvegarder_donnees_user(username, edited_df):
    filename = get_user_data_path(username)
    _ensure_parent_dir(filename)
    edited_df.to_csv(filename, index=False)


def charger_quetes_user(username):
    filename = get_quest_data_path(username)
    _ensure_parent_dir(filename)

    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        df = pd.read_csv(filename)
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        for col in QUEST_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df

    df = pd.DataFrame(columns=QUEST_COLUMNS)
    df.to_csv(filename, index=False)
    return df


def sauvegarder_quetes_user(username, df_q):
    filename = get_quest_data_path(username)
    _ensure_parent_dir(filename)
    df_q.to_csv(filename, index=False)
