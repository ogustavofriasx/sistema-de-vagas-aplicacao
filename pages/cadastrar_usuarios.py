import streamlit as st
from database import get_database, get_collection_users
from utils.auth import require_role

#configuração da pagina
st.set_page_config(
    page_title="Cadastro de Usuários",
    page_icon="💻",
    layout="wide"
)


st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}   /* esconde a lista automática */
[data-testid="stSidebar"] section:nth-child(1) {padding-top: 0;}
</style>
""", unsafe_allow_html=True)


with st.sidebar:

    st.title("Sistema de Vagas")
    
    nome = st.session_state.get("nome", "")
    tipo = st.session_state.get("tipo", "")

    st.write(f"👤 {nome} ({tipo})")

    st.divider()

    if tipo == "administrador":
        if st.button("Home", type="primary", use_container_width=True):
            st.switch_page("app.py")

        if st.button("Cadastrar Currículo",type="primary", use_container_width=True):
            st.switch_page("pages/cadastrar_curriculo.py")

        if st.button("Cadastrar Usuário", type="primary", use_container_width=True):
            st.switch_page("pages/cadastrar_usuarios.py")
        
        if st.button("Cadastrar Vaga", type="primary", use_container_width=True):
            st.switch_page("pages/cadastrar_vagas.py")
        
        if st.button("Currículos", type="primary", use_container_width=True):
            st.switch_page("pages/curriculos.py")
        
        if st.button("Mapa de vagas", type="primary", use_container_width=True):
            st.switch_page("pages/distribuicao_geografica.py")
        
        if st.button("Matching", type="primary", use_container_width=True):
            st.switch_page("pages/matching.py")

        if st.button("Vagas", type="primary", use_container_width=True):
            st.switch_page("pages/vagas.py")

    elif tipo == "empregador":
        if st.button("Home", type="primary", use_container_width=True):
            st.switch_page("app.py")

        if st.button("Cadastrar Vaga", type="primary", use_container_width=True):
            st.switch_page("pages/cadastrar_vagas.py")

        if st.button("Currículos", type="primary", use_container_width=True):
            st.switch_page("pages/curriculos.py")

        if st.button("Matching", type="primary", use_container_width=True):
            st.switch_page("pages/matching.py")

        if st.button("Vagas", type="primary", use_container_width=True):
            st.switch_page("pages/vagas.py")

    elif tipo == "candidato":
        if st.button("Home", type="primary", use_container_width=True):
            st.switch_page("app.py")

        if st.button("Cadastrar Currículo", type="primary", use_container_width=True):
            st.switch_page("pages/cadastrar_curriculo.py")

        if st.button("Mapa de vagas",type="primary", use_container_width=True):
            st.switch_page("pages/distribuicao_geografica.py")

        if st.button("Vagas", type="primary", use_container_width=True):
            st.switch_page("pages/vagas.py")



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