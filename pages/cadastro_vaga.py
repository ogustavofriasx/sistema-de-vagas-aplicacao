import streamlit as st
from database import get_collection_vagas, get_next_sequence
from utils.auth import require_role

#configuração da pagina
st.set_page_config(
    page_title="Cadastro de Vagas",
    page_icon="📢",
    layout="wide"
)


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