import streamlit as st
from database import get_collection_vagas


st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
[data-testid="collapsedControl"] {display: none;}
</style>
""", unsafe_allow_html=True)

collection = get_collection_vagas()

vagas = collection.find()

st.title("Vagas Disponíveis")

vagas_list = list(vagas)

if len(vagas_list) == 0:
    st.info("Nenhuma vaga cadastrada no momento.")
else:
    for vaga in vagas_list:
        st.subheader(f"{vaga['titulo']} - {vaga['empresa']}")
        st.write(f"**Descrição:** {vaga['descricao']}")
        st.write(f"**Localização:** {vaga['cidade']}, {vaga['estado']}")
        if 'tipo_contratacao' in vaga:
            st.write(f"**Tipo:** {vaga['tipo_contratacao']}")
        else:
            st.write("**Tipo:** Não informado")
        st.write(f"**Salário:** R$ {vaga['salario']}")
        st.write(f"**Skills Requeridas:** {', '.join(vaga['skills'])}")
        st.markdown("---")  


#botao para voltar para o menu
if st.button("Voltar ao Menu Principal", type="secondary"):
    st.switch_page("app.py")