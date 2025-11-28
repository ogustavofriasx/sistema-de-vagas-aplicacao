import streamlit as st

def require_role(roles):
    if not st.session_state.get("logado"):
        st.error("Você precisa fazer login para acessar esta página.")
        st.switch_page("app.py")

    tipo = st.session_state.get("tipo")

    if tipo not in roles:
        st.error("Acesso negado. Seu tipo de usuário não é bem-vindo aqui.")
        st.stop()