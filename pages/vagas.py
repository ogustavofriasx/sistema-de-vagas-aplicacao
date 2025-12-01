import streamlit as st
from database import get_collection_vagas
from google import genai
from google.genai import types
from pymongo import MongoClient
from database import get_collection_curriculos
from utils.auth import require_role

#configuração da pagina
st.set_page_config(
    page_title="Vagas",
    page_icon="🔍",
    layout="wide"
)

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


def buscar_vagas_fts(termo_busca):
    """
    busca fts nas vagas
    """
    collection = get_collection_vagas()
    
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
        st.info("Certifique-se de que o índice de texto foi criado na coleção 'vagas'")
        return []

collection = get_collection_vagas()

vagas = collection.find()

st.title("Vagas")

vagas_list = list(vagas)

tab_lista, tab_ia, tab_mapa, tab_fts = st.tabs(["Listagem de Vagas", "Consulta IA", "Distribuição Geográfica", "Buscar"])


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

with tab_fts:
    st.subheader("Busca Full-Text Search de Vagas")
    
    st.markdown("""
    **Como usar:**
    - Digite palavras-chave relacionadas a cargo, empresa, skills ou descrição
    - Você pode usar múltiplos termos separados por espaço
    - Exemplo: "desenvolvedor python" ou "analista dados"
    """)
    
    with st.form("fts_vagas"):
        termo_busca = st.text_input(
            "Digite os termos de busca:",
            placeholder="Ex: desenvolvedor, python, remoto, etc."
        )
        
        #filtros adicionais, talvez não precisa
        col1, col2, col3 = st.columns(3)
        with col1:
            filtrar_cidade = st.text_input("Filtrar por cidade (opcional):")
        with col2:
            filtrar_tipo = st.selectbox(
                "Tipo de contratação:",
                ["Todos", "CLT", "PJ", "Estágio", "Freelancer"]
            )
        with col3:
            salario_min = st.number_input(
                "Salário mínimo (R$):",
                min_value=0,
                value=0,
                step=500
            )
        
        buscar = st.form_submit_button("Buscar", type="primary")
    
    if buscar:
        if termo_busca.strip() == "":
            st.warning("Por favor, digite um termo de busca.")
        else:
            with st.spinner("Buscando vagas..."):
                resultados = buscar_vagas_fts(termo_busca)
                
                # Aplicar filtros adicionais
                if filtrar_cidade:
                    resultados = [r for r in resultados if filtrar_cidade.lower() in r.get('cidade', '').lower()]
                if filtrar_tipo != "Todos":
                    resultados = [r for r in resultados if r.get('tipo_contratacao') == filtrar_tipo]
                if salario_min > 0:
                    resultados = [r for r in resultados if r.get('salario', 0) >= salario_min]
                
                if len(resultados) == 0:
                    st.info(f"Nenhuma vaga encontrada para '{termo_busca}'")
                    st.markdown("**Dicas:**")
                    st.markdown("- Tente termos mais genéricos")
                    st.markdown("- Verifique a ortografia")
                    st.markdown("- Use sinônimos ou termos relacionados")
                else:
                    st.success(f"Encontradas {len(resultados)} vaga(s)")
                    
                    for vaga in resultados:
                        score = vaga.get('score', 0)
                        
                        with st.expander(f"{vaga['titulo']} - {vaga['empresa']} (Relevância: {score:.2f})"):
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                st.write(f"**Localização:** {vaga['cidade']}, {vaga['estado']}")
                                st.write(f"**Tipo:** {vaga.get('tipo_contratacao', 'Não informado')}")
                                st.write(f"**Salário:** R$ {vaga['salario']:,.2f}".replace(',', '.'))
                            
                            with col_b:
                                st.write(f"**Skills:** {', '.join(vaga['skills'])}")
                            
                            st.write(f"**Descrição:** {vaga['descricao']}")
                        
                        st.markdown("---")
    
    #informações sobre a busca
    with st.expander("ℹ Informações sobre a busca"):
        st.markdown("""
        **Como funciona o Full-Text Search:**
        
        O FTS busca nos seguintes campos:
        - Título da vaga
        - Descrição
        - Nome da empresa
        - Skills requeridas
        
        **Índice necessário:**
        Se você ainda não criou o índice, execute no MongoDB:
        ```javascript
        db.vagas.createIndex({
          "titulo": "text",
          "descricao": "text",
          "empresa": "text",
          "skills": "text"
        })
        ```
        """)
        
with tab_mapa:
    st.subheader("Distribuição Geográfica das Vagas")
    if st.button("Ver Mapa de Distribuição Geográfica"):
        st.switch_page("pages/distribuicao_geografica.py")

#botao para voltar para o menu
if st.button("Voltar ao Menu Principal", type="secondary"):
    st.switch_page("app.py")