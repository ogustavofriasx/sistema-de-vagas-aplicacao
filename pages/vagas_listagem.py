import streamlit as st
from database import get_collection_vagas

st.title("Vagas Disponíveis")

# Obtém a coleção de vagas
collection = get_collection_vagas()

# Busca todas as vagas
vagas = list(collection.find())

st.write("Faça o login para mais recursos:")
submit_login = st.button("Logar")

if submit_login:
            st.switch_page("app.py")

st.write("### Lista de Vagas Cadastradas:")

if len(vagas) == 0:
    st.info("Nenhuma vaga cadastrada no momento.")
else:
    for vaga in vagas:
        st.subheader(f"{vaga['titulo']} — {vaga['empresa']}")
        st.write(f"**Descrição:** {vaga['descricao']}")
        st.write(f"**Localização:** {vaga['cidade']}, {vaga['estado']}")
        st.write(f"**Tipo de Contratação:** {vaga.get('tipo_contratacao', 'Não informado')}")
        st.write(f"**Salário:** R$ {vaga['salario']}")
        st.write(f"**Skills Requeridas:** {', '.join(vaga['skills'])}")

        st.markdown("---")
