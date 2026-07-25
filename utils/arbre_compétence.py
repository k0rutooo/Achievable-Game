import streamlit as st
import pandas as pd
from streamlit_agraph import Node, Edge
from utils.data import charger_donnees_user


username = st.session_state.username
df_user = charger_donnees_user(username)

PALETTE_COULEURS = {
    0: "#154564", # Racine (Bleu très foncé)
    1: "#21628E", # Niveau 1
    2: "#2B82BC", # Niveau 2
    3: "#4C95C5", # Niveau 3
    4: "#67B6EA",  # Niveau 4+
    5: "#B2E0FF"
}

#-----------------------------------------------
#Pour plus tard
PALETTE_COULEURS_HUBS = {
    0: "#116413", # Racine (Bleu très foncé)
    1: "#12A24C", # Niveau 1
    2: "#12B543", # Niveau 2
    3: "#61D16D", # Niveau 3
    4: "#8FD7A1",  # Niveau 4+
    5: "#DAF5DC"
}

PALETTE_COULEURS_DOMAINES = {
    0: "#1B4F72", # Racine (Bleu très foncé)
    1: "#2874A6", # Niveau 1
    2: "#3498DB", # Niveau 2
    3: "#85C1E9", # Niveau 3
    4: "#AED6F1",  # Niveau 4+
    5: "#DAEAF5"
}

PALETTE_COULEURS_COMPOSANTS = {
    0: "#1B4F72", # Racine (Bleu très foncé)
    1: "#2874A6", # Niveau 1
    2: "#3498DB", # Niveau 2
    3: "#85C1E9", # Niveau 3
    4: "#AED6F1",  # Niveau 4+
    5: "#DAEAF5"
}
#-----------------------------------------------

ids_valide = set(df_user["ID"])


def calculer_profondeur(df_arbre, node_id):
    profondeurs = []
    current_id = node_id
    if node_id == "GLO":
        return 0
    ligne = df_arbre[df_arbre["ID"] == current_id]
    if not ligne.empty and ligne['Parent'].notna().all():
        parents = ligne.iloc[0,1].split(';')
        for p in parents:
            profondeurs.append(calculer_profondeur(df_arbre, p))
    
    if profondeurs == []:
        return 0
    return 1 + max(profondeurs)


def generer_arbre_dynamique(df_arbre):
    nodes = []
    edges = []
    
    # --- NETTOYAGE PRÉVENTIF ---
    # On remplace les NaN par des chaînes vides pour éviter l'erreur JSON
    df_arbre = df_arbre.fillna("")
    tous_les_noeuds = pd.concat([df_arbre['ID'], df_arbre['Parent']]).dropna().unique()

    for _, row in df_arbre.iterrows():

        # 1. Calcul de la profondeur pour ce nœud
        prof = calculer_profondeur(df_arbre, row['ID'])
        
        # 2. Calcul de la taille (décroissante)
        # On part de 40px et on réduit de 20% à chaque niveau
        taille = 40 * (0.85 ** prof)
        
        # 3. Choix de la couleur selon la profondeur
        couleur = PALETTE_COULEURS.get(prof,PALETTE_COULEURS[5])
        #if row["Type"] == "Hub":
            #couleur = PALETTE_COULEURS_HUBS.get(prof, PALETTE_COULEURS_HUBS[5])
        #elif row["Type"] == "Domaine":
            #couleur = PALETTE_COULEURS_DOMAINES.get(prof, PALETTE_COULEURS_DOMAINES[5])
        #elif row["Type"] == "Composant":
            #couleur = PALETTE_COULEURS_COMPOSANTS.get(prof, PALETTE_COULEURS_COMPOSANTS[5])


        # 4. Création du Noeud
        nodes.append(Node(
            id=row['ID'],
            label=f"{row['Label']}", 
            size=taille, 
            color=couleur,
            font={
            "size":10,
            "color": "#ffffff", # Blanc pur
            "face": ""
        }
        ))

        if pd.notna(row['Parent']):
        # Découper la cellule s'il y a plusieurs parents séparés par ";"
            parents = str(row['Parent']).split(';')
            parents_filtrés = [p for p in parents if p in ids_valide]
            print(f"parents: {parents}, ids_valide{ids_valide}, parents_filtrés{parents_filtrés}") #DEBUG
            
            for parent_id in parents_filtrés:
                # Nettoyer les espaces vides potentiels
                parent_id = parent_id.strip()
                if parent_id:
                    edges.append(Edge(source=parent_id, target=row['ID'], color="#D5D8DC", arrows={"to":False,"from":False}, width=0.5))

    return nodes, edges


# ------------------------------------------------------------------------------------
#   IMPORTANT
# ------------------------------------------------------------------------------------
#
#Il faudra, dans le futur trier le dataframe par étage dans l'arbre, le df de tout les domaines et ceux des users
