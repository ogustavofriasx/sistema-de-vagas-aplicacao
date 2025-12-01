import streamlit as st
from database import get_database

#configuração da pagina
st.set_page_config(
    page_title="Sistema de Vagas",
    layout="wide"
)

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

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



# Se o usuário já estiver logado, mostra as opções
if st.session_state.get("logado"):
    st.title("Menu Principal")

    tipo = st.session_state.get("tipo")


    st.success("Você está logado como {}!".format(tipo))

    if tipo == "administrador":
        if st.button("Ver Vagas"):
            st.switch_page("pages/vagas.py")
        if st.button("Cadastrar Vaga"):
            st.switch_page("pages/cadastro_vaga.py")
        if st.button("Ver Currículos"):
            st.switch_page("pages/curriculos.py")
        if st.button("Cadastrar Currículo"):
            st.switch_page("pages/cadastro_curriculo.py")
        if st.button("Cadastrar Usuários"):
            st.switch_page("pages/cadastro_form.py")
        if st.button("Matching"):
            st.switch_page("pages/matching.py")

        if st.button("Sair", type="primary"):
            st.session_state["logado"] = False
            st.rerun()
    
    if tipo == "empregador":
        if st.button("Ver Vagas"):
            st.switch_page("pages/vagas.py")
        if st.button("Cadastrar Vaga"):
            st.switch_page("pages/cadastro_vaga.py")
        if st.button("Ver Currículos"):
            st.switch_page("pages/curriculos.py")
        if st.button("Sair", type="primary"):
            st.session_state["logado"] = False
            st.rerun()
    
    if tipo == "candidato":
        if st.button("Ver Vagas"):
            st.switch_page("pages/vagas.py")
        if st.button("Cadastrar Currículo"):
            st.switch_page("pages/cadastro_curriculo.py")
        if st.button("Sair", type="primary"):
            st.session_state["logado"] = False
            st.rerun()

else:
        

    st.title("Login")
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
            st.switch_page("pages/vagas.py")