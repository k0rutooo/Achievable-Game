import math
from datetime import date, datetime

import pandas as pd
import streamlit as st

from utils.data import charger_donnees_user, sauvegarder_donnees_user


def get_level(xp):
    if xp <= 0:
        return 0
    lvl = math.floor(math.sqrt(xp / 10))
    return min(100, lvl)


def get_xp_for_level(level):
    return 10 * (level ** 2)


def calculer_xp_noeud(df, node_id):
    if node_id is None or node_id == "" or df.empty:
        return 0

    mask_soi = df["ID"] == node_id
    xp_propre = 0
    if mask_soi.any():
        xp_propre = pd.to_numeric(df.loc[mask_soi, "XP"].iloc[0], errors="coerce") or 0

    enfants = df[df["Parent"] == node_id]
    xp_enfants = 0
    for _, row_enfant in enfants.iterrows():
        xp_enfants += calculer_xp_noeud(df, row_enfant["ID"])

    return xp_propre + xp_enfants


def obtenir_stats_completes(df, node_id):
    xp_actuelle = calculer_xp_noeud(df, node_id)
    lvl = get_level(xp_actuelle)

    if lvl >= 100:
        return {"lvl": 100, "xp": xp_actuelle, "next_xp": 0, "pct": 100}

    xp_palier_actuel = get_xp_for_level(lvl)
    xp_palier_suivant = get_xp_for_level(lvl + 1)
    progression_dans_lvl = xp_actuelle - xp_palier_actuel
    distance_entre_paliers = xp_palier_suivant - xp_palier_actuel
    pct = (progression_dans_lvl / distance_entre_paliers) * 100

    return {
        "lvl": lvl,
        "xp": xp_actuelle,
        "next_xp": xp_palier_suivant,
        "pct": round(pct, 1),
    }


def get_global_level(username):
    df = charger_donnees_user(username)
    if df.empty:
        return 0

    df_game = df[df["Parent"] != "META"].copy()
    if df_game.empty:
        return 0

    df_game["XP"] = pd.to_numeric(df_game["XP"], errors="coerce").fillna(0)
    liste_parents = df_game["Parent"].unique()
    df_feuilles = df_game[~df_game["ID"].isin(liste_parents)]
    somme_des_niveaux = df_feuilles["XP"].apply(get_level).sum()
    niveau_global = somme_des_niveaux / 5
    return max(1, min(100, math.floor(niveau_global)))


def obtenir_titre_rang(niveau):
    if niveau < 10:
        return "Vagabond"
    if niveau < 20:
        return "Apprenti Aventurier"
    if niveau < 30:
        return "Médaillé d'or"
    if niveau < 40:
        return "Explorateur Pro"
    if niveau < 50:
        return "Tailleur de Saphir"
    if niveau < 60:
        return "Aventurier Confirmé"
    if niveau < 70:
        return "Visionnaire"
    if niveau < 80:
        return "Presque Maître"
    if niveau < 90:
        return "Chercheur de Diamant"
    if niveau < 100:
        return "Demi-Dieu"
    return "Légende Vivante"


def calculer_fraicheur(date_str):
    if not date_str or pd.isna(date_str) or date_str == "":
        return 100

    try:
        derniere = datetime.strptime(str(date_str), "%Y-%m-%d").date()
        jours_ecoules = (date.today() - derniere).days
        if jours_ecoules <= 7:
            return 100
        fraicheur = max(0, 100 - ((jours_ecoules - 7) * 4.34))
        return round(fraicheur)
    except Exception as exc:
        st.error(f"Erreur Date : {exc} sur la valeur '{date_str}'")
        return 100


def obtenir_date_fraicheur_reelle(df_user, domaine_id):
    selection = df_user[df_user["ID"] == domaine_id]
    if selection.empty:
        return ""

    date_max = pd.to_datetime(selection.iloc[0].get("Derniere_Activite", ""), errors="coerce")

    def trouver_tous_descendants(parent_id):
        enfants = df_user[df_user["Parent"] == parent_id]["ID"].tolist()
        descendants = list(enfants)
        for enfant_id in enfants:
            descendants.extend(trouver_tous_descendants(enfant_id))
        return descendants

    tous_ids = trouver_tous_descendants(domaine_id)
    if tous_ids:
        df_descendants = df_user[df_user["ID"].isin(tous_ids)]
        dates_desc = pd.to_datetime(df_descendants["Derniere_Activite"], errors="coerce").dropna()
        if not dates_desc.empty:
            date_max_desc = dates_desc.max()
            if pd.isna(date_max) or date_max_desc > date_max:
                date_max = date_max_desc

    return date_max.strftime("%Y-%m-%d") if pd.notna(date_max) else ""


def appliquer_atrophie(username):
    df = charger_donnees_user(username)
    seuil_grace = 14
    taux_perte = 0.001
    modifie = False

    mask_jeu = (df["Parent"] != "META") & (df["ID"] != "GLO")
    for idx, row in df[mask_jeu].iterrows():
        valeur_date = row["Derniere_Activite"]
        if pd.isna(valeur_date) or valeur_date == "":
            continue

        try:
            derniere = datetime.strptime(str(valeur_date), "%Y-%m-%d").date()
        except ValueError:
            derniere = datetime.strptime(str(valeur_date), "%y-%m-%d").date()
            df.at[idx, "Derniere_Activite"] = derniere.strftime("%Y-%m-%d")
            modifie = True

        jours_inactifs = (date.today() - derniere).days
        if jours_inactifs > seuil_grace:
            jours_a_punir = jours_inactifs - seuil_grace
            xp_actuelle = row["XP"]
            perte = xp_actuelle * (taux_perte * jours_a_punir)

            if perte > 0:
                df.at[idx, "XP"] = max(0, xp_actuelle - perte)
                modifie = True

    if modifie:
        sauvegarder_donnees_user(username, df)
        return True
    return False
