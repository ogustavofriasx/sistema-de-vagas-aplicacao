import streamlit as st
from database import get_collection_curriculos

st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
[data-testid="collapsedControl"] {display: none;}
</style>
""", unsafe_allow_html=True)

collection = get_collection_curriculos()

curriulos = collection.find()

st.title("Currículos Cadastrados")

curriculos_list = list(curriulos)

if len(curriculos_list) == 0:
    st.info("Nenhum currículo cadastrado no momento.")
else:
    for curriculo in curriculos_list:
        st.subheader(f"{curriculo['nome']}")
        st.write(f"**Email:** {curriculo['email']}")
        st.write(f"**Idiomas:** {', '.join(curriculo['idiomas'])}")
        st.write(f"**Telefone:** {curriculo['telefone']}")
        st.write(f"**Formação Acadêmica:** {curriculo['formacao']}")
        st.write(f"**Experiência Profissional:** {curriculo['experiencia']}")
        st.write(f"**Empresas Anteriores:** {', '.join(curriculo['empresas_previas'])}")
        st.write(f"**Skills:** {', '.join(curriculo['skills'])}")
        st.markdown("---")


#botao para voltar para o menu
if st.button("Voltar ao Menu Principal", type="secondary"):
    st.switch_page("app.py")