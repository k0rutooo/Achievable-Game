import datetime

import pandas as pd

from utils.data import (
    charger_donnees_user,
    charger_quetes_user,
    sauvegarder_donnees_user,
    sauvegarder_quetes_user,
)


def ajouter_xp(username, skill_id, montant_xp):
    df_user = charger_donnees_user(username)
    if skill_id in df_user["ID"].values:
        if df_user.loc[df_user["ID"] == skill_id, "Type"].item() == "Composant":
            df_user["XP"] = pd.to_numeric(df_user["XP"], errors="coerce").fillna(0)
            df_user.loc[df_user["ID"] == skill_id, "XP"] += int(montant_xp)
            df_user.loc[df_user["ID"] == skill_id, "Derniere_Activite"] = date.today().strftime("%Y-%m-%d")
            sauvegarder_donnees_user(username, df_user)
            return True
    return False


def creer_quete(username, comp_id, titre, xp, type_quete="Secondaire"):
    df = charger_quetes_user(username)

    if type_quete == "Principale":
        existe = df[
            (df["ID_Competence"] == comp_id)
            & (df["Statut"] == "En cours")
            & (df["Type"] == "Principale")
        ]
        if not existe.empty:
            return False, "Une quête principale est déjà en cours !"

    nouveau_id = f"Q{len(df) + 2}_{datetime.datetime.now().strftime('%f'))}"
    nouvelle_ligne = pd.DataFrame(
        [
            {
                "ID_Quete": nouveau_id,
                "ID_Competence": comp_id,
                "Titre": titre,
                "XP_Recompense": int(xp),
                "Statut": "En cours",
                "Type": type_quete,
                "Date_Creation": date.today().strftime("%d/%m/%Y"),
                "Date_Completion": "",
            }
        ]
    )

    df = pd.concat([df, nouvelle_ligne], ignore_index=True)
    sauvegarder_quetes_user(username, df)
    return True, "La quête a été forgée !"


def valider_quete(username, id_quete):
    df_q = charger_quetes_user(username)
    mask = df_q["ID_Quete"] == id_quete

    if mask.any():
        idx = df_q.index[mask][0]
        df_q.at[idx, "Statut"] = "Terminée"
        df_q.at[idx, "Date_Completion"] = str(f"{date.today().strftime("%d/%m/%Y")}")

        id_comp = df_q.at[idx, "ID_Competence"]
        xp = int(df_q.at[idx, "XP_Recompense"])

        sauvegarder_quetes_user(username, df_q)
        return ajouter_xp(username, id_comp, xp)
    return False


def supprimer_quete(username, quete_id):
    df = charger_quetes_user(username)
    df = df[df["ID_Quete"] != quete_id]
    sauvegarder_quetes_user(username, df)
    return True
