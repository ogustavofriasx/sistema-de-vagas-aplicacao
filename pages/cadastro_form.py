import streamlit as st
from database import get_database, get_collection_users
from utils.auth import require_role

#configuração da pagina
st.set_page_config(
    page_title="Cadastro de Usuários",
    page_icon="💻",
    layout="wide"
)


db = get_database()
collection = get_collection_users()

if require_role(["administrador"]):
    with st.form("cadastro_form"):

        st.title("Cadastro de Usuários")

        nome = st.text_input("Nome: ")
        email = st.text_input("Email: ")
        senha = st.text_input("Senha: ", type="password")
        tipo = st.selectbox("Tipo de Usuário:", ["administrador", "empregador", "candidato"])
        submit = st.form_submit_button("Cadastrar Usuário")
        
        if submit:
            collection.insert_one({
                "nome": nome,
                "email": email,
                "senha": senha,
                "tipo": tipo
            })
            st.success(f"Usuário '{nome}' cadastrado com sucesso!")    



#botao para voltar para o menu
if st.button("Voltar ao Menu Principal", type="secondary"):
    st.switch_page("app.py")