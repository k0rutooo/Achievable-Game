import streamlit as st
import pandas as pd
from utils.data import charger_donnees_user
from utils.progression import (
    calculer_fraicheur,
    get_global_level,
    obtenir_date_fraicheur_reelle,
)

st.set_page_config(layout="wide",page_title="L'antre de l'Oracle")

user = st.session_state.username
df_user = charger_donnees_user(user)
lvl_global = get_global_level(user)

# ------------------------------------------------------------------------------------
#   STYLE CSS
# ------------------------------------------------------------------------------------

st.markdown("""
    <style>
    .oracle-card {
        background: rgba(15, 174, 185, 0.05);
        border-left: 5px solid #0faeb9;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .vision-title {
        color: #0faeb9;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------------
#   ENTÊTE ÉPIQUE
# ------------------------------------------------------------------------------------

st.title("🔮 L'Antre de l'Oracle")
st.caption("Le temps s'arrête ici. Écoute les murmures de ta propre progression.")

col_stats, col_oubli = st.columns([0.4, 0.6], gap="large")

with col_stats:
    st.markdown("<p class='vision-title'>✨ Miroir du Destin</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        # --- 1. FILTRAGE INTELLIGENT ---
        # On exclut le META et le GLO technique
        df_game = df_user[(df_user['Parent'] != 'META') & (df_user['ID'] != 'GLO')].copy()
        
        # On identifie les "Feuilles" (domaines qui ne sont les parents de personne)
        # C'est là que l'XP est réellement injectée (ex: Boxe, Foot)
        ids_qui_sont_parents = df_game['Parent'].unique()
        df_feuilles = df_game[~df_game['ID'].isin(ids_qui_sont_parents)]

        # --- 2. FORCES ET FAIBLESSES (Basées sur les feuilles) ---
        if not df_feuilles.empty:
            domaine_faible = df_feuilles.loc[df_feuilles['XP'].idxmin()]['Label']
            domaine_fort = df_feuilles.loc[df_feuilles['XP'].idxmax()]['Label']
            
            st.write(f"🛡️ **Ta plus grande force :** {domaine_fort}")
            st.write(f"⚠️ **Ton point de vulnérabilité :** {domaine_faible}")
        else:
            st.write("🌌 Ton destin est encore une page blanche.")

with col_oubli:
    st.markdown("<p class='vision-title'>🌀 Murmures de l'Oubli</p>", unsafe_allow_html=True)

    with st.container(border=True):
        # --- 3. MURMURES DE L'OUBLI (Basés sur les parents pour la clarté) ---
        alertes = 0

        df_racines = df_game[(df_game['Parent'] == 'GLO') | (df_game['Parent'].isna()) | (df_game['Parent'] == '')]

        for _, row in df_racines.iterrows():
            date_reelle = obtenir_date_fraicheur_reelle(df_user, row['ID'])
            f = calculer_fraicheur(date_reelle)
            
            if f < 50:
                st.caption(f"{row['Label']} s'efface... ({f}%)")
                st.progress(f / 100)
                alertes += 1

        # --- 4. BILAN GLOBAL (HORS DE LA BOUCLE !) ---
        if alertes == 0:
            st.write("✅ Tes connaissances sont vives et alertes.")
            
            # Conseil passif basé sur l'Aura
            if lvl_global < 20:
                st.info("L'Oracle voit que ton Aura globale est encore fragile. Diversifie tes quêtes.")
            else:
                st.success("Ton aura grandit. La maîtrise est à portée de main.")

st.divider()
st.caption("Rappelle-toi Aventurier : l'Oracle guide, mais c'est ton bras qui forge.")