import streamlit as st
from database import get_collection_vagas, get_next_sequence
from utils.auth import require_role

#configuração da pagina
st.set_page_config(
    page_title="Cadastro de Vagas",
    page_icon="📢",
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


collection = get_collection_vagas()

if require_role(["administrador", "empregador"]):
    # id int, titulo, descricao, cidade, estado, tipo, salario int, empresa, skills array, embedding array (se for no mongo)
    with st.form("cadastrar_vaga"):
        st.title("Cadastro de Vaga")

        titulo = st.text_input("Título da Vaga: ")
        descricao = st.text_area("Descrição da Vaga: ")
        cidade = st.text_input("Cidade: ")
        estado = st.text_input("Estado: ")
        tipo = st.selectbox("Tipo de Vaga:", ["CLT", "PJ", "Estágio", "Freelancer"])
        salario = st.number_input("Salário (R$): ", min_value=0, step=1000)
        empresa = st.text_input("Empresa: ")
        skills = st.text_input("Skills Requeridas (separadas por vírgula): ")

        submit = st.form_submit_button("Cadastrar Vaga")

        if submit:
            # Insert do banco
            collection.insert_one({
                "id": get_next_sequence("id", collection),
                "titulo": titulo,
                "descricao": descricao,
                "cidade": cidade,
                "estado": estado,
                "tipo_contratacao": tipo,
                "salario": salario,
                "empresa": empresa,
                "skills": [skill.strip() for skill in skills.split(",")],
            })

            st.success(f"Vaga '{titulo}' cadastrada com sucesso!")

#botao para voltar para o menu
if st.button("Voltar ao Menu Principal", type="secondary"):
    st.switch_page("app.py")