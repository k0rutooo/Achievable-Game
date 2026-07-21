import pandas as pd
import streamlit as st
from datetime import date
from config import DATA_DOMAINE_DIR
from utils.data import charger_donnees_user, sauvegarder_donnees_user

# ------------------------------------------------------------------------------------
#   DEBUG
# ------------------------------------------------------------------------------------

debug = False

# ------------------------------------------------------------------------------------
#   CHEMINS
# ------------------------------------------------------------------------------------

path_dossier_domaines = DATA_DOMAINE_DIR
path_fichier_domaines = path_dossier_domaines / "domaine.csv"

# ------------------------------------------------------------------------------------
#   Load (temporaire, il faudra tout refaire à ce niveau là)
# ------------------------------------------------------------------------------------

username = st.session_state.username

df_domaines = pd.read_csv(path_fichier_domaines)

df_domaines_parents_split = df_domaines.copy()
df_domaines_parents_split["Parent"] = df_domaines_parents_split["Parent"].str.split(';')

df_domaines_explode = df_domaines.copy()
df_domaines_explode["Parent"] = df_domaines_explode["Parent"].fillna("").astype(str).str.split(';')
df_domaines_explode = df_domaines_explode.explode("Parent")
df_domaines_explode["Parent"] = df_domaines_explode["Parent"].str.strip()
df_domaines_explode["ID"] = df_domaines_explode["ID"].astype(str).str.strip()

# ------------------------------------------------------------------------------------
#   FONCTIONS
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------
# Explication
def est_domaine_principal(df, node_id):
    if df.loc[df["ID"] == node_id, "Type"].item() == "Domaine":
        return True
    else:
        return False

# ------------------------------------------------------------------------------------
# Explication
# Retourne un dataframe avec le domaine qu'on cherche à ajouter, si ce domaine à des parents, ou des composants,
# qui ne sont pas encore dans le csv de l'utilisateur alors on les rajoute en ré-appelant la fonction (récursion)
# et ils sont concat au df du domaine du premier appel de la fonction
# les donnees utilisateur sont dans les paramètres de la fonction (mais il faudra peut être les actualisés dans la fonction plus tard)

def ajouter_famille_domaine(id_domaine, df_user, est_racine=True, visites=None):

    id_domaine = str(id_domaine).strip()

    if visites is None:
        visites = set()
    
    if id_domaine in visites:
        return pd.DataFrame()
    
    visites.add(id_domaine)

    ligne_domaine = df_domaines.loc[df_domaines["ID"] == id_domaine]
    if ligne_domaine.empty:
        return pd.DataFrame()

    liste_df_parents = []
    liste_df_composants = []
    
    nouveau_domaine = {
        "ID": id_domaine,
        "Parent": ligne_domaine["Parent"].item(),
        "Label": ligne_domaine["Label"].item(),
        "XP": 0,
        "Derniere_Activite": date.today().strftime("%Y-%m-%d"),
        "Type": ligne_domaine["Type"].item()
    }
    df_nouveau_domaine = pd.DataFrame([nouveau_domaine])

    if est_racine:
        valeur_parent = ligne_domaine["Parent"].item()
        if pd.notna(valeur_parent) and valeur_parent.strip() != "":
            liste_parents = valeur_parent.split(";")
            for parent in liste_parents:
                if (parent not in df_user["ID"].values) and (parent not in visites):
                    df_parent = ajouter_famille_domaine(parent, df_user, est_racine=True,visites=visites)
                    if not df_parent.empty:
                        liste_df_parents.append(df_parent)

            if liste_df_parents:
                df_parents = pd.concat(liste_df_parents, ignore_index=True).fillna("")
                df_nouveau_domaine = pd.concat([df_nouveau_domaine, df_parents], ignore_index=True)

    type_actuel = ligne_domaine["Type"].item()
    if type_actuel == "Domaine":
        liste_composants = df_domaines_explode.loc[
            (df_domaines_explode["Parent"] == id_domaine) & 
            (df_domaines_explode["Type"] == "Composant"), 
            "ID"
        ].tolist()
    
        if liste_composants:
            for composant in liste_composants:
                if (composant not in df_user["ID"].values) and (composant not in visites):
                    df_composant = ajouter_famille_domaine(composant, df_user, est_racine=False,visites=visites)
                    if not df_composant.empty:
                        liste_df_composants.append(df_composant)

            if liste_df_composants:
                df_composants = pd.concat(liste_df_composants, ignore_index=True).fillna("")
                df_nouveau_domaine = pd.concat([df_nouveau_domaine, df_composants], ignore_index=True)

    if debug:
        print(f"Appel de la fonction pour l'ID : {id_domaine}")
        print("\nDEBUG\n",df_nouveau_domaine,"\n", df_user)

    return df_nouveau_domaine

# ------------------------------------------------------------------------------------
# Explication
# Trie les domaines de l'utilisateur par Hub, Domaine et Composant
def trier_domaines_utilisateur(username):
    df_a_trier = charger_donnees_user(username)
    ordre = ["Hub","Domaine","Composant"]
    df_a_trier["Type"] = pd.Categorical(df_a_trier["Type"], categories=ordre, ordered=True)
    df_a_trier = df_a_trier.sort_values(by="Type")
    sauvegarder_donnees_user(username,df_a_trier)

# ------------------------------------------------------------------------------------
# Explication
# Trie le fichier des domaines par Hub, Domaine et Composant
def trier_domaines(df_a_trier):
    with open(path_fichier_domaines, "w") as f:
        ordre = ["Hub","Domaine","Composant"]
        df_a_trier["Type"] = pd.Categorical(df_a_trier["Type"], categories=ordre, ordered=True)
        df_a_trier = df_a_trier.sort_values(by="Type")
        df_a_trier.to_csv(path_fichier_domaines, index=False)


def collecter_suppressions_v1(id_cible, df, ids_a_supprimer=None):

    df_user_parents_split = df.copy()
    df_user_parents_split["Parent"] = df["Parent"].str.split(';')

    if ids_a_supprimer is None:
        ids_a_supprimer = set()
        
    if id_cible in ids_a_supprimer:
        return ids_a_supprimer
        
    # 1. Ajouter l'élément actuel aux suppressions
    ids_a_supprimer.add(id_cible)
    ligne_actuelle = df[df["ID"] == id_cible]
    if ligne_actuelle.empty:
        return ids_a_supprimer
    
    ids_existants = set(df["ID"].values)
        
    type_actuel = ligne_actuelle["Type"].values[0]

    # 2. Gestion des ENFANTS (Descente si type == Domaine)
    if type_actuel == "Domaine":
        # Trouver les composants qui ont ce domaine comme parent
        enfants = df[df["Parent"].str.contains(id_cible, na=False, regex=False) & (df["Type"] == "Composant")]
        for _, enfant in enfants.iterrows():
            # Vérifier si cet enfant a d'autres parents encore actifs
            parents_enfant = enfant["Parent"].split(";")
            autres_parents_actifs = [p for p in parents_enfant if p != id_cible and p not in ids_a_supprimer and p in ids_existants]
            
            # S'il n'a plus d'autres parents actifs, on le supprime aussi
            if not autres_parents_actifs:
                collecter_suppressions(enfant["ID"], df, ids_a_supprimer)

    # 3. Gestion des PARENTS (Remontée si le parent est un Hub)
    parent_id = ligne_actuelle["Parent"].values[0]
    if pd.notna(parent_id) and parent_id != "" and parent_id != "GLO":
        ligne_parent = df[df["ID"] == parent_id]

        if not ligne_parent.empty and ligne_parent["Type"].values[0] == "Hub":
            # Trouver les autres enfants de ce Hub (qui ne sont pas en cours de suppression)
            autres_enfants = df_user_parents_split[(df_user_parents_split["Parent"] == parent_id) & (~df_user_parents_split["ID"].isin(ids_a_supprimer))]
            # Si le Hub n'a plus aucun autre enfant, on remonte pour le supprimer
            if autres_enfants.empty:
                collecter_suppressions(parent_id, df, ids_a_supprimer)

    return ids_a_supprimer

def collecter_suppressions(id_cible, df, ids_a_supprimer=None):
    if ids_a_supprimer is None:
        ids_a_supprimer = set()
        
    if id_cible in ids_a_supprimer:
        return ids_a_supprimer
        
    # 1. Ajouter l'élément actuel aux suppressions
    ids_a_supprimer.add(id_cible)
    ligne_actuelle = df[df["ID"] == id_cible]
    if ligne_actuelle.empty:
        return ids_a_supprimer
    
    ids_existants = set(df["ID"].values)
    type_actuel = ligne_actuelle["Type"].values[0]

    # 2. Gestion des ENFANTS (Descente si type == Domaine)
    if type_actuel == "Domaine":
        # Trouver les composants qui ont EXACTEMENT id_cible parmi leurs parents splittés
        enfants = df[
            df["Parent"].apply(lambda x: id_cible in str(x).split(';') if pd.notna(x) else False) & 
            (df["Type"] == "Composant")
        ]
        
        for _, enfant in enfants.iterrows():
            parents_enfant = str(enfant["Parent"]).split(";")
            # Filtrer pour voir s'il reste d'autres parents valides en dehors de ceux supprimés
            autres_parents_actifs = [
                p for p in parents_enfant 
                if p != id_cible and p not in ids_a_supprimer and p in ids_existants
            ]
            
            # S'il n'a plus aucun autre parent actif, on le détruit
            if not autres_parents_actifs:
                collecter_suppressions(enfant["ID"], df, ids_a_supprimer)

    # 3. Gestion des PARENTS (Remontée si le parent est un Hub)
    # On split aussi ici car un Domaine (ex: NAT) peut être lié à plusieurs Hubs (ex: MUS;CAR)
    parents_cible = str(ligne_actuelle["Parent"].values[0]).split(";")
    
    for p_id in parents_cible:
        if pd.notna(p_id) and p_id != "" and p_id != "GLO":
            ligne_parent = df[df["ID"] == p_id]

            if not ligne_parent.empty and ligne_parent["Type"].values[0] == "Hub":
                # Trouver les autres enfants (Domaines ou Hubs) qui appartiennent à ce Hub
                autres_enfants = df[
                    df["Parent"].apply(lambda x: p_id in str(x).split(';') if pd.notna(x) else False) & 
                    (~df["ID"].isin(ids_a_supprimer))
                ]
                
                # Si le Hub n'a plus aucun autre enfant actif, on remonte la récursion
                if autres_enfants.empty:
                    collecter_suppressions(p_id, df, ids_a_supprimer)

    return ids_a_supprimer

def supprimer_domaine(id_domaine, username):
    # Charger les données (Simulé ici par votre CSV)
    df_user = charger_donnees_user(username) 
    
    # Étape 1 : Collecter récursivement tous les IDs à supprimer
    ids_to_drop = collecter_suppressions(id_domaine, df_user)
    
    # Étape 2 : Filtrer le DataFrame en une seule fois
    df_final = df_user[~df_user["ID"].isin(ids_to_drop)].copy()
    
    return df_final
