import streamlit as st
from google import genai
from google.genai import types
from pymongo import MongoClient
from database import get_collection_curriculos
from utils.auth import require_role


st.title("Currículos Cadastrados")



client_gemini = genai.Client(api_key=st.secrets["gemini"]["api_key"])
client_atlas = MongoClient(st.secrets["mongodb"]["uri"])
db = client_atlas[st.secrets["mongodb"]["database"]]


# Função que gera embeddings com Gemini
def gerarEmbeddingsPerguntas(txt_query):
    response = client_gemini.models.embed_content(
        model="gemini-embedding-001",
        contents=txt_query,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=512
        )
    )
    return response.embeddings[0].values


# Função que consulta o MongoDB Atlas usando vector search
def getDocsMongodbAtlas(query_embedding):
    client = MongoClient(st.secrets["mongodb"]["uri"])
    db = client["atv6"]  # seu banco
    collection = db["curriculos"]

    docs = list(collection.find({}))
    return docs


# Gera resposta via geração do Gemini
def gerarPrompt(docs, query):

    contexto = "\n\n".join([str(doc) for doc in docs])

    prompt = f"""
    Você é um assistente prestativo de MongoDB. Use SOMENTE o contexto fornecido.
    Se a resposta não estiver no contexto, diga que não sabe.

    CONTEXTO DOS CURRÍCULOS:
    {contexto}

    Pergunta do usuário:
    {query}

    Se não encontrar a informação no contexto acima, responda:
    "Nenhum candidato no banco possui essa informação".
    Não invente dados.
    """

    resposta = client_gemini.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    return resposta.text



collection = get_collection_curriculos()

curriulos = collection.find()



curriculos_list = list(curriulos)


tab_lista, tab_ia, tab_fts = st.tabs(["Listagem de Curriculos", "Consulta IA", "Consulta FTS"])


with tab_lista:
    st.title("Curriculos cadastrados no sistema")
    if require_role(["administrador", "empregador"]):
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
    else:
        if st.button("Fazer login", key = "bt2",type="primary"):
            st.switch_page("app.py")


with tab_ia:
    st.subheader("Pergunte algo sobre os curriculos")

    if require_role(["administrador", "empregador"]):
        with st.form("ia"):
            query = st.text_input("Digite sua pergunta:")
            enviar = st.form_submit_button("Enviar")

            if enviar and query.strip() != "":
                with st.status("Processando consulta..."):
                    st.write("Gerando embedding...")
                    emb = gerarEmbeddingsPerguntas(query)

                    st.write("Consultando MongoDB...")
                    docs = getDocsMongodbAtlas(emb)

                    st.write("Gerando resposta com Gemini...")
                    resposta = gerarPrompt(docs, query)

                st.success("Resposta gerada!")
                st.markdown(f"### Resposta:\n{resposta}")
    else:
        if st.button("Fazer login", key = "bt1", type="primary"):
            st.switch_page("app.py")


with tab_fts:
    st.subheader("Busca FTS nos currículos")
    if require_role(["administrador", "empregador"]):
        with st.form("fts"):
            st.write("### Consulta Full-Text Search (FTS)")
            enviar = st.form_submit_button("Buscar")
    else:
        if st.button("Fazer login", key = "bt3", type="primary"):
            st.switch_page("app.py")



#botao para voltar para o menu
if st.button("Voltar ao Menu Principal", type="secondary"):
    st.switch_page("app.py")