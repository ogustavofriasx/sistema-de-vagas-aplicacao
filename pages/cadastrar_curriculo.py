import streamlit as st
from database import get_collection_curriculos, get_next_sequence
from utils.auth import require_role


#configuração da pagina
st.set_page_config(
    page_title="Cadastro de Currículos",
    page_icon="📝",
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


collection = get_collection_curriculos()
if require_role(["administrador", "candidato"]):
    # id int, nome, email, idiomas, telefone, cidade, formacao, estado, experiencia, empresas previas array, 
    # skills array, embedding array (se for no mongo)
    # id_contatos array
    with st.form("cadastra_curriculo"):
        st.title("Cadastro de Currículo")

        nome = st.text_input("Nome Completo: ")
        email = st.text_input("Email: ")
        idiomas = st.text_input("Idiomas (separados por vírgula): ")
        telefone = st.text_input("Telefone: ")
        cidade = st.text_input("Cidade: ")
        estado = st.text_input("Estado: ")
        formacao = st.text_area("Formação Acadêmica: ")
        experiencia = st.text_area("Experiência Profissional: ")
        empresas_previas = st.text_input("Empresas Anteriores (separadas por vírgula): ")
        skills = st.text_input("Skills (separadas por vírgula): ")

        submit = st.form_submit_button("Cadastrar Currículo")

        if submit:
            collection.insert_one({
                "id": get_next_sequence("id", collection),
                "nome": nome,
                "email": email,
                "idiomas": [idioma.strip() for idioma in idiomas.split(",")],
                "telefone": telefone,
                "cidade": cidade,
                "estado": estado,
                "formacao": formacao,
                "experiencia": experiencia,
                "empresas_previas": [empresa.strip() for empresa in empresas_previas.split(",")],
                "skills": [skill.strip() for skill in skills.split(",")],
            })
            st.success(f"Currículo de '{nome}' cadastrado com sucesso!")


#botao para voltar para o menu
if st.button("Voltar ao Menu Principal", type="secondary"):
    st.switch_page("app.py")