import streamlit as st

st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
[data-testid="collapsedControl"] {display: none;}
</style>
""", unsafe_allow_html=True)

with st.form("cadastro_form"):
    nome = st.text_input("Nome: ")
    senha = st.text_input("Senha: ", type="password")
    submit = st.form_submit_button("Entrar")
    if submit and nome != "" and senha != "":
        st.success("Cadastro bem-sucedido!")
        st.switch_page("app.py")

    elif submit:
        st.warning("Tentativa de cadastro falhou.")


#botao para voltar para o menu
if st.button("Voltar ao Menu Principal", type="secondary"):
    st.switch_page("app.py")