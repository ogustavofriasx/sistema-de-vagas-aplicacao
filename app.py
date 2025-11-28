import streamlit as st
from database import get_database

db = get_database()

def validar(email, senha):
    if email == "" or senha == "":
        st.error("Por favor, preencha todos os campos.")
        return False
    
    users = db["users"]

    user = users.find_one({"email": email, "senha": senha})

    if not user:
        st.error("Email ou senha incorretos.")
        return False
    
    st.session_state["tipo"] = user.get("tipo", "candidato")

    return True

st.title("Login")

# Se o usuário já estiver logado, mostra as opções
if st.session_state.get("logado"):

    tipo = st.session_state.get("tipo")


    st.success("Login bem-sucedido, você está logado como {}!".format(tipo))

    if tipo == "administrador":
        if st.button("Ver Vagas", type="primary"):
            st.switch_page("pages/vagas.py")
        if st.button("Cadastrar Vaga", type="primary"):
            st.switch_page("pages/cadastro_vaga.py")
        if st.button("Ver Currículos", type="primary"):
            st.switch_page("pages/curriculos.py")
        if st.button("Cadastrar Currículo", type="primary"):
            st.switch_page("pages/cadastro_curriculo.py")
        if st.button("Cadastrar Usuários", type="primary"):
            st.switch_page("pages/cadastro_form.py")

        if st.button("Sair", type="secondary"):
            st.session_state["logado"] = False
            st.rerun()
    
    if tipo == "empregador":
        if st.button("Ver Vagas", type="primary"):
            st.switch_page("pages/vagas.py")
        if st.button("Cadastrar Vaga", type="primary"):
            st.switch_page("pages/cadastro_vaga.py")
        if st.button("Sair", type="secondary"):
            st.session_state["logado"] = False
            st.rerun()
    
    if tipo == "candidato":
        if st.button("Ver Vagas", type="primary"):
            st.switch_page("pages/vagas.py")
        if st.button("Cadastrar Currículo", type="primary"):
            st.switch_page("pages/cadastro_curriculo.py")

else:
        
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("Email: ")
        senha = st.text_input("Senha: ", type="password")
        submit = st.form_submit_button("Entrar")

        submit_list = st.form_submit_button("Vagas disponíveis")

        if submit:
            if validar(email, senha):
                st.session_state["logado"] = True
                st.success("Login bem-sucedido!")
                st.rerun()
            else:
                st.warning("Tentativa de login falhou.")
        
        if submit_list:
            st.switch_page("pages/vagas_listagem.py")

