import streamlit as st

def validar(nome, senha):
    if nome == "" or senha == "":
        st.error("Por favor, preencha todos os campos.")
        return False
    return True

st.title("Login")

# Se o usuário já estiver logado, mostra as opções
if st.session_state.get("logado"):
    st.success("Login bem-sucedido!")

    if st.button("Ver Vagas", type="primary"):
        st.switch_page("pages/vagas.py")
    if st.button("Cadastrar Vaga", type="primary"):
        st.switch_page("pages/cadastro_vaga.py")
    if st.button("Ver Currículos", type="primary"):
        st.switch_page("pages/curriculos.py")
    if st.button("Cadastrar Currículo", type="primary"):
        st.switch_page("pages/cadastro_curriculo.py")

    if st.button("Sair", type="secondary"):
        st.session_state["logado"] = False
        st.rerun()

else:
        
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        nome = st.text_input("Nome: ")
        senha = st.text_input("Senha: ", type="password")
        submit = st.form_submit_button("Entrar")

        if submit:
            if validar(nome, senha):
                st.session_state["logado"] = True
                st.success("Login bem-sucedido!")
                st.rerun()
            else:
                st.warning("Tentativa de login falhou.")

if st.button("Cadastrar", type="secondary"):
    st.switch_page("pages/cadastro_form.py")
