import streamlit as st
from database import get_database

st.set_page_config(
    page_title="Sistema de Vagas",
    layout="wide"
)

#esconde menuzin lateral
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
    st.session_state["nome"] = user.get("nome", "usuário")
    return True

st.markdown("""
<style>
button[kind="secondary"] {
    background-color: #4169E1 !important;
    padding: 30px 10px !important;
    border-radius: 14px !important;
    font-size: 40px !important;
    font-weight: 600 !important;
    color: #FAFAFA !important;
    text-align: center !important;
    transition: 0.20s ease-in-out !important;
    height: 130px !important;
}

button[kind="secondary"]:hover {
    transform: scale(1.05) !important;
    border-color: #4A60E8 !important;
    box-shadow: 0px 4px 18px rgba(0,0,0,0.10) !important;
}
</style>
""", unsafe_allow_html=True)

def card_button(label, page):
    if st.button(label, use_container_width=True):
        st.switch_page(page)

if st.session_state.get("logado"):
    st.title("Menu Principal")

    nome = st.session_state.get("nome")
    tipo = st.session_state.get("tipo")

    st.success(f"Bem-vindo, {nome}! ({tipo})")

    if tipo == "administrador":
        col1, col2, col3 = st.columns(3)
        with col1:
            card_button("Ver Vagas", "pages/vagas.py")
        with col2:
            card_button("Cadastrar Vaga", "pages/cadastrar_vagas.py")
        with col3:
            card_button("Ver Currículos", "pages/curriculos.py")

        col4, col5, col6 = st.columns(3)
        with col4:
            card_button("Cadastrar Currículo", "pages/cadastrar_curriculo.py")
        with col5:
            card_button("Cadastrar Usuários", "pages/cadastrar_usuarios.py")
        with col6:
            card_button("Matching", "pages/matching.py")

    if tipo == "empregador":
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            card_button("Ver Vagas", "pages/vagas.py")
        with col2:
            card_button("Cadastrar Vaga", "pages/cadastrar_vagas.py")
        with col3:
            card_button("Ver Currículos", "pages/curriculos.py")
        with col4:
            card_button("Matching", "pages/matching.py")

    if tipo == "candidato":
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            card_button("Ver Vagas", "pages/vagas.py")
        with col2:
            card_button("Cadastrar Currículo", "pages/cadastrar_curriculo.py")
        with col3:
            card_button("Matching", "pages/matching.py")
        with col4:
            card_button("Distribuição de Vagas", "pages/distribuicao_geografica.py")


    st.markdown("""
        <style>
        button[kind="primary"] {
            background-color: #FF4B4B !important;    
            color: white !important;                      
            border: 1px solid #CC0000 !important;    
            border-radius: 8px !important;                
            padding: 10px 20px !important;                
            font-weight: 600 !important;                 
            font-size: 18px !important;              
            transition: all 0.2s ease-in-out !important;  
        }

        button[kind="primary"]:hover {
            background-color: #D93838 !important; 
            border-color: #A40000 !important;       
            transform: scale(1.03);                 
            box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        }
        </style>
        """, unsafe_allow_html=True)
    
    if st.button("Sair", type="primary"):
        st.session_state["logado"] = False
        st.rerun()

else:
    st.title("Login")
    with st.form("login_form"):
        email = st.text_input("Email:")
        senha = st.text_input("Senha:", type="password")

        submit = st.form_submit_button("Entrar")
        lista = st.form_submit_button("Vagas disponíveis")

        if submit:
            if validar(email, senha):
                st.session_state["logado"] = True
                st.success("Login bem-sucedido!")
                st.rerun()
            else:
                st.warning("Tentativa de login falhou.")

        if lista:
            st.switch_page("pages/vagas.py")
