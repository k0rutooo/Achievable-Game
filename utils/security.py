import streamlit as st


def securite_page():
    if "username" not in st.session_state or not st.session_state.logged_in:
        st.error("Accès refusé. Veuillez vous connecter.")
        st.stop()
