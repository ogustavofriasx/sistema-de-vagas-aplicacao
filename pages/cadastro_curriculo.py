import streamlit as st
from database import get_collection_curriculos, get_next_sequence

st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
[data-testid="collapsedControl"] {display: none;}
</style>
""", unsafe_allow_html=True)

collection = get_collection_curriculos()

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