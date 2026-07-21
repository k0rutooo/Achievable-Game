import pandas as pd

from utils.data import charger_donnees_user, sauvegarder_donnees_user


def obtenir_difficulte_jeu(username):
    df = charger_donnees_user(username)
    ligne = df[df["ID"] == "SETTING_DIFF"]
    if not ligne.empty:
        return ligne.iloc[0]["Label"]
    return "Normal"


def sauvegarder_difficulte_jeu(username, nouvelle_diff):
    df = charger_donnees_user(username)

    if "SETTING_DIFF" in df["ID"].values:
        df.loc[df["ID"] == "SETTING_DIFF", "Label"] = nouvelle_diff
    else:
        nouvelle_ligne = pd.DataFrame(
            [{"ID": "SETTING_DIFF", "Label": nouvelle_diff, "Parent": "META", "XP": 0}]
        )
        df = pd.concat([df, nouvelle_ligne], ignore_index=True)

    sauvegarder_donnees_user(username, df)
