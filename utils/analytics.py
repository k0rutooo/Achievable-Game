import pandas as pd

from utils.data import charger_donnees_user, charger_quetes_user


def preparer_donnees_graphique(username, periode="Semaine"):
    df_q = charger_quetes_user(username)
    df_terminees = df_q[df_q["Statut"] == "Terminée"].copy()

    if df_terminees.empty:
        return pd.DataFrame(columns=["Date", "XP"])

    df_terminees["XP_Recompense"] = pd.to_numeric(
        df_terminees["XP_Recompense"], errors="coerce"
    ).fillna(0)
    df_terminees["Date_Completion"] = df_terminees["Date_Completion"].fillna(
        df_terminees["Date_Creation"]
    )
    df_terminees.loc[df_terminees["Date_Completion"] == "", "Date_Completion"] = df_terminees[
        "Date_Creation"
    ]
    df_terminees["Date_Completion"] = pd.to_datetime(
        df_terminees["Date_Completion"], dayfirst=True, errors="coerce"
    )
    df_terminees = df_terminees.dropna(subset=["Date_Completion"])

    aujourdhui = pd.Timestamp.now().normalize()
    jours_delta = 6 if periode == "Semaine" else 29 if periode == "Mois" else 364
    date_debut = aujourdhui - pd.Timedelta(days=jours_delta)
    idx = pd.date_range(date_debut, aujourdhui)

    stats_xp = df_terminees.groupby("Date_Completion")["XP_Recompense"].sum()
    stats_xp = stats_xp.reindex(idx, fill_value=0).reset_index()
    stats_xp.columns = ["Date", "XP"]
    return stats_xp


def preparer_donnees_echarts_bureau(username, domaine_id, periode="Semaine"):
    df_user = charger_donnees_user(username)
    df_q = charger_quetes_user(username)

    df_user["Parent"] = df_user["Parent"].str.split(';')
    df_user = df_user[df_user["ID"] != "GLO"]

    sous_domaines = df_user[df_user["Parent"].apply(lambda x: domaine_id in x)]
    ids_interet = sous_domaines["ID"].tolist() + [domaine_id]
    print(sous_domaines,ids_interet)
    df_t = df_q[
        (df_q["Statut"] == "Terminée") & (df_q["ID_Competence"].isin(ids_interet))
    ].copy()

    if df_t.empty:
        return [], [], []

    df_t["XP_Recompense"] = pd.to_numeric(df_t["XP_Recompense"], errors="coerce").fillna(0)
    df_t["Date_Completion"] = pd.to_datetime(
        df_t["Date_Completion"], dayfirst=True, errors="coerce"
    )
    df_t = df_t.dropna(subset=["Date_Completion"])

    jours = 7 if periode == "Semaine" else 30
    dates_axe = [
        (pd.Timestamp.now().normalize() - pd.Timedelta(days=i)).strftime("%d/%m")
        for i in range(jours)
    ][::-1]

    series_data = []
    for _, enfant in sous_domaines.iterrows():
        valeurs = []
        for d_str in dates_axe:
            mask = (
                (df_t["Date_Completion"].dt.strftime("%d/%m") == d_str)
                & (df_t["ID_Competence"] == enfant["ID"])
            )
            valeurs.append(int(df_t[mask]["XP_Recompense"].sum()))

        if sum(valeurs) > 0:
            series_data.append(
                {"name": enfant["Label"], "type": "line", "smooth": True, "data": valeurs}
            )

    return dates_axe, series_data, [s["name"] for s in series_data]
