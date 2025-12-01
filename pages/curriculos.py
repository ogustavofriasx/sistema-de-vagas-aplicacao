import streamlit as st
from google import genai
from google.genai import types
from pymongo import MongoClient
from database import get_collection_curriculos
from utils.auth import require_role

#configuração da pagina
st.set_page_config(
    page_title="Currículos",
    page_icon="🪪",
    layout="wide"
)


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
    db = client["sistema_de_vagas"]  # seu banco
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

#função pra busca do fts
def buscar_curriculos_fts(termo_busca):
    """
    busca do fts nos curriculos
    """

    collection = get_collection_curriculos()

    if not termo_busca or termo_busca.strip() == "":
        return []
    
    try:
        #busca usando o indice de texto
        resultados = collection.find(
            {"$text": {"$search": termo_busca}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})])

        return list(resultados)
    except Exception as e:
        st.error(f"Erro na busca: {str(e)}")
        st.info("Certifique-se de que o índice de texto foi criado na coleção 'currículos'")
        return []

collection = get_collection_curriculos()

curriulos = collection.find()



curriculos_list = list(curriulos)


tab_lista, tab_ia, tab_fts = st.tabs(["Listagem de Curriculos", "Consulta IA", "Buscar FTS"])


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
        st.markdown("""
        **Como usar:**
        - Digite palavras-chave relacionadas a skills, formação, experiência ou empresas
        - Você pode usar múltiplos termos separados por espaço
        - Exemplo: "python javascript" ou "engenheiro senior"
        """)

        with st.form("fts"):
            termo_busca = st.text_input(
                "Digite os termos de busca:",
                placeholder="Ex: python, react, engenheiro, etc."
            )

            #opções de filtro adicional
            col1, col2 = st.columns(2)
            with col1:
                filtrar_cidade = st.text_input("Filtrar por cidade:")#testando, achoq vou tirar dps
            with col2:
                filtrar_estado = st.text_input("Filtrar por estado")#msm coisa da cidade

            buscar = st.form_submit_button("Buscar", type="primary")

        if buscar:
            if termo_busca.strip() == "":
                st.warning("por favor, digite um termo de busca")
            else:
                with st.spinner("Buscando currículos..."):
                    resultados = buscar_curriculos_fts(termo_busca)

                    #aplicar filtros adicionais se fornecidos
                    if filtrar_cidade:
                        resultados = [r for r in resultados if filtrar_cidade.lower() in r.get('cidade', '').lower()]
                    if filtrar_estado:
                        resultados = [r for r in resultados if filtrar_estado.lower() in r.get('estado', '').lower()]

                    if len(resultados) == 0:
                        st.info(f"Nenhum curriculo encontrado para '{termo_busca}'")
                        st.markdown("**Dicas**")
                        st.markdown("- Tente termos mais genéricos")
                        st.markdown("- Verifique a ortografia")
                        st.markdown("- Use sinônimos ou termos relacionados")
                    else:
                        st.success(f"Encontrados {len(resultados)} currículo(s)")

                        for curriculo in resultados:
                            #mostrar score de relevância se disponível
                            score = curriculo.get('score', 0)
                                
                            with st.expander(f"{curriculo['nome']} - Relevância: {score:.2f}"):
                                col_a, col_b = st.columns(2)
                                    
                                with col_a:
                                    st.write(f"**Email:** {curriculo['email']}")
                                    st.write(f"**Telefone:** {curriculo['telefone']}")
                                    st.write(f"**Localização:** {curriculo.get('cidade', 'N/A')}, {curriculo.get('estado', 'N/A')}")
                                    st.write(f"**Idiomas:** {', '.join(curriculo['idiomas'])}")
                                    
                                with col_b:
                                    st.write(f"**Skills:** {', '.join(curriculo['skills'])}")
                                    st.write(f"**Empresas Anteriores:** {', '.join(curriculo['empresas_previas'])}")
                                    
                                st.write(f"**Formação:** {curriculo['formacao']}")
                                st.write(f"**Experiência:** {curriculo['experiencia']}")
                                
                            st.markdown("---")

        #dica sobre o índice
        with st.expander("ℹInformações sobre a busca"):
            st.markdown("""
            **Como funciona o Full-Text Search:**
                
            O FTS busca nos seguintes campos:
            - Nome do candidato
            - Formação acadêmica
            - Experiência profissional
            - Skills
            - Empresas anteriores
                
            **Índice necessário:**
            Se você ainda não criou o índice, execute no MongoDB:
            ```javascript
            db.curriculos.createIndex({
            "nome": "text",
            "formacao": "text",
            "experiencia": "text",
            "skills": "text",
            "empresas_previas": "text"
            })
            ```
            """)
        #st.write("### Consulta Full-Text Search (FTS)")
        #enviar = st.form_submit_button("Buscar")
            
    else:
        #st.info("Faça login como administrador ou empregador para usar a busca.")
        if st.button("Fazer login", key = "bt3", type="primary"):
            st.switch_page("app.py")



#botao para voltar para o menu
if st.button("Voltar ao Menu Principal", type="secondary"):
    st.switch_page("app.py")
