import streamlit as st
from database import get_collection_vagas
from google import genai
from google.genai import types
from pymongo import MongoClient
from database import get_collection_curriculos
from utils.auth import require_role



client_gemini = genai.Client(api_key=st.secrets["gemini"]["api_key"])
client_atlas = MongoClient(st.secrets["mongodb"]["uri"])
db = client_atlas[st.secrets["mongodb"]["database"]]


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

def getDocsMongodbAtlas(query_embedding):
    client = MongoClient(st.secrets["mongodb"]["uri"])
    db = client["atv6"]  # seu banco
    collection = db["vagas"]

    docs = list(collection.find({}))
    return docs


def gerarPrompt(docs, query):

    contexto = "\n\n".join([str(doc) for doc in docs])

    prompt = f"""
    Você é um assistente prestativo de MongoDB. Use SOMENTE o contexto fornecido.
    Se a resposta não estiver no contexto, diga que não sabe.

    CONTEXTO DAS VAGAS:
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



collection = get_collection_vagas()

vagas = collection.find()

st.title("Vagas")

vagas_list = list(vagas)

tab_lista, tab_ia = st.tabs(["Listagem de Vagas", "Consulta IA"])


with tab_lista:
    st.title("Vagas cadastradas no sistema")

    collection = get_collection_vagas()
    vagas = list(collection.find())

    if len(vagas) == 0:
        st.info("Nenhuma vaga cadastrada no momento.")
    else:
        for vaga in vagas:
            st.subheader(f"{vaga['titulo']} — {vaga['empresa']}")
            st.write(f"**Descrição:** {vaga['descricao']}")
            st.write(f"**Localização:** {vaga['cidade']}, {vaga['estado']}")

            st.write(f"**Tipo:** {vaga.get('tipo_contratacao', 'Não informado')}")
            st.write(f"**Salário:** R$ {vaga['salario']}")
            st.write(f"**Skills Requeridas:** {', '.join(vaga['skills'])}")

            st.markdown("---")

with tab_ia:
    st.subheader("Pergunte algo sobre os curriculos")
    if require_role(["administrador", "candidato", "empregador"]):
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
        if st.button("Fazer login", key = "bt1",type="primary"):
            st.switch_page("app.py")
        

