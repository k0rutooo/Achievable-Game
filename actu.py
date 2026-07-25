import streamlit as st

st.title("Actualité de l'app")

st.divider()

#------------------------------------------------------
#V2 Beta

st.title("v2 bêta")
st.caption("20 Juillet 2026")
st.subheader("C'EST EN LIGNEEEEE")
st.markdown(":blue-background[Achievable Game] (anciennement life's a game) est finalement en ligne.")
st.write("""Ce n'est qu'une première version, 
         il y a sûrement quelque bug qui traîne, 
         mais le jeu est finalement en ligne avec déjà quelques fonctionnalités multijoueurs.""")
st.markdown("Tous les changements depuis la dernière fois :")
st.badge("Nouveautés", color='violet')
st.markdown("- Le multijoueurs")
st.markdown("- Les Clans")
st.markdown("- La page d'Actualités (celle-ci)")

st.space("xxsmall")

st.badge("Améliorations", color="green")
st.markdown("- La Base de Domaine (nouveaux système de domaines)")
st.markdown("- Progression retravaillée")
st.markdown("- Typographie et Couleurs plus harmonieuses")

st.space("xxsmall")

st.badge("Changements", color="orange")
st.markdown("- Suppression de l'IA de l'oracle")
st.markdown("- Suppression de l'IA de création de quêtes")
st.markdown('- Suppression de la "Difficultée"')

st.space("xxsmall")

st.subheader("Pourquoi tous ces changements ?")
st.write('''D'abord le :blue-background[multijoueurs]: le manque d'interaction rendait l'application "morte", 
         mis à part la progression personelle il n'y avait pas d'autres motivation à utiliser cet outils 
         plutôt qu'un autre.''')
st.write(''':blue-background[Les Clans] sont donc une solution à ce manque de vie, ils permettent de se créer une petite communauté entre amis, 
         permet d'échanger avec eux grâce au chat de clan, pour progresser en équipe.''')
st.write('''D'autres fonctionnalités arrivent très bientôt pour améliorer les clans, donc restez bien à l'affût!''')

st.space("xxsmall")

st.write(''':blue-background[La Base de Domaines] permet d'ajouter ou supprimer des domaines de votre compte, 
         les domaines commun entre joueurs permetteront d'ajouter énormément de fonctionnalitées multijoueurs, 
         mais nécessitent de les intégrés 1 par 1, cette bêta ne compte qu'une dizaine de domaines, mais des nouveaux sont ajoutés régulièrements.''')

st.space("xxsmall")

st.write('''Et finalement :blue-background[L'Oracle], son IA à été retiré, parce que hors sujet, on utilisait des modèles gratuits, 
         ce n'était donc jamais les même modèles qui répondait aux questions, 
         une amélioration aurait été de garder en mémoire les anciennes interactions mais après refléxion on en est venu à la conclusion 
         que une IA pour l'Oracle n'avait pas de sens, en revanche l'Oracle existe toujours, pour vous dire dans quels domaines 
         vous excellez et quel domaine vous ne pratiquez pas depuis un moment.''')

st.space("xxsmall")

st.write('''Breeeff, comme vous l'aurez compris cette version est encore expérimentale, 
         si vous rencontrez des problèmes, que vous avez des besoin d'aides quelque part 
         ou que vous avez des suggestions à me faire n'hésitez pas à envoyer un message, 
         que ce soit sur :grey-background[Discord], :rainbow-background[Instagram], ou en 
         commentaire :red-background[Youtube] même, 
         je vous laisse les liens des différents réseaux juste en dessous, et je vous remercie énormément de participer 
         au début de ce projet''')
st.space("small")

url_insta = "https://www.instagram.com/achievableengrand/"
url_discord = "https://discord.gg/dv9NpdVufu"
url_youtube = "https://youtube.com/@achievable_fabio?si=CUTAQpBbl5YDr_XR"

st.subheader("Nos Réseaux :")
st.write("[Instagram](%s)"% url_insta)
st.write("[Discord](%s)"% url_discord)
st.write("[Youtube](%s)"% url_youtube)

#------------------------------------------------------

st.divider()

#------------------------------------------------------
#V1

st.title("v1")
st.caption("13 Avril 2026")
st.subheader("Bienvenue dans la V1 du Jeu de la Vie")
st.write("Transformez votre vie en jeu vidéo en créant et progressant dans des domaines, gagnez de l'xp à chaque fois que vous pratiquez, lancez vous des objectifs et des quêtes!")
st.write("Liste des Features :")
st.write("Création et Suppression de domaine")
st.write("Création et Suppression de quêtes")
st.write("Quêtes principales et secondaires")
st.write("Tracking de gains d'xp sur la dernière année")
st.write("")
