import streamlit as st
import pandas as pd
from database import get_collection_vagas
from utils.auth import require_role
import requests
from time import sleep


#configuração da pagina
st.set_page_config(
    page_title="Distribuição Geográfica de Vagas",
    page_icon="📍",
    layout="wide"
)


#cache para coordenadas ja buscadas
@st.cache_data
def get_coordenadas(cidade, estado):
    """
    Busca coordenadas da cidade usando a API do Nominatim (OpenStreetMap)
    """
    if not cidade or not estado:
        return None
    
    try:
        #formata a query
        query = f"{cidade}, {estado}, Brasil"
        
        #fazer a requisição para a api do Nominatim, é uma api publica, se acharem q ta demorando mt meio q vai ter q ficar mapeando as cidades manualmente
        #as vezes demora um pouco pra carregar
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': query,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'br'  #limitar ao br
        }
        headers = {
            'User-Agent': 'VagasApp/1.0'  #Nominatim requer User-Agent
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return {
                    'lat': float(data[0]['lat']),
                    'lon': float(data[0]['lon'])
                }
        
        return None
        
    except Exception as e:
        st.warning(f"Erro ao buscar coordenadas de {cidade}: {str(e)}")
        return None

#carregar vagas do banco
@st.cache_data(ttl=300)  #cache por 5 minutos
def load_vagas():
    collection = get_collection_vagas()
    vagas = list(collection.find())
    return vagas

#titulo
st.title("Distribuição Geográfica de Vagas")
st.markdown("---")

#carregar dados
vagas = load_vagas()

if len(vagas) == 0:
    st.warning("Nenhuma vaga cadastrada no sistema.")
    if st.button("Voltar ao Menu Principal", type="secondary"):
        st.switch_page("app.py")
    st.stop()

#processa dados das vagas
dados_processados = []
with st.spinner("Carregando coordenadas das cidades..."):
    for vaga in vagas:
        cidade = vaga.get('cidade', '')
        estado = vaga.get('estado', '')
        coords = get_coordenadas(cidade, estado)
        
        if coords:
            dados_processados.append({
                'titulo': vaga.get('titulo', 'Sem título'),
                'empresa': vaga.get('empresa', 'Não informado'),
                'cidade': cidade,
                'estado': estado,
                'salario': vaga.get('salario', 0),
                'tipo': vaga.get('tipo_contratacao', 'Não informado'),
                'skills': ', '.join(vaga.get('skills', [])),
                'lat': coords['lat'],
                'lon': coords['lon']
            })
        
        #pequeno delay para n sobrecarregar a API
        sleep(0.1)

#criar dataframe
if len(dados_processados) == 0:
    st.error("Nenhuma vaga possui coordenadas válidas. Verifique se as cidades estão cadastradas corretamente.")
    st.info("Dica: Certifique-se de cadastrar o nome completo da cidade e o estado correto nas vagas.")
    if st.button("Voltar ao Menu Principal", type="secondary"):
        st.switch_page("app.py")
    st.stop()

df = pd.DataFrame(dados_processados)

#barra com filtros
st.sidebar.header("Filtros")

#filtro por estado
estados_disponiveis = ['Todos'] + sorted(df['estado'].unique().tolist())
estado_selecionado = st.sidebar.selectbox(
    "Selecione o Estado:",
    estados_disponiveis
)

#filtro por cidade
cidades_disponiveis = ['Todas'] + sorted(df['cidade'].unique().tolist())
cidade_selecionada = st.sidebar.selectbox(
    "Selecione a Cidade:",
    cidades_disponiveis
)

#filtro por tipo de contratação
tipos_disponiveis = ['Todos'] + sorted(df['tipo'].unique().tolist())
tipo_selecionado = st.sidebar.selectbox(
    "Tipo de Contratação:",
    tipos_disponiveis
)

#filtro por salario minimo
min_salario = st.sidebar.slider(
    "Salário mínimo (R$):",
    min_value=0,
    max_value=int(df['salario'].max()) if len(df) > 0 else 10000,
    value=0,
    step=500
)

#aplicar filtros
df_filtrado = df.copy()

if estado_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['estado'] == estado_selecionado]

if cidade_selecionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['cidade'] == cidade_selecionada]

if tipo_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['tipo'] == tipo_selecionado]

df_filtrado = df_filtrado[df_filtrado['salario'] >= min_salario]

#metricas principais (sera que precisa?)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total de Vagas",
        len(df_filtrado)
    )

with col2:
    st.metric(
        "Cidades",
        df_filtrado['cidade'].nunique()
    )

with col3:
    salario_medio = df_filtrado['salario'].mean() if len(df_filtrado) > 0 else 0
    st.metric(
        "Salário Médio",
        f"R$ {salario_medio:,.0f}".replace(',', '.')
    )

with col4:
    st.metric(
        "Estados",
        df_filtrado['estado'].nunique()
    )

st.markdown("---")

#layout com mapa e informaçoes
if len(df_filtrado) > 0:
    col_mapa, col_info = st.columns([2, 1])
    
    with col_mapa:
        st.subheader("Mapa de Distribuição")
        
        #preparar dados para o mapa
        mapa_df = df_filtrado[['lat', 'lon']].copy()
        
        #exibir o mapa
        st.map(
            mapa_df,
            zoom=3,
            width='stretch'
        )
        
        st.info(f"Mostrando {len(df_filtrado)} vagas em {df_filtrado['cidade'].nunique()} cidades")
    
    #tabela detalhada de vagas  (acho q vou tirar)
    st.subheader("Vagas Detalhadas")
    
    for idx, vaga in df_filtrado.iterrows():
        with st.expander(f"🔹 {vaga['titulo']} - {vaga['empresa']}"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.write(f"**Localização:** {vaga['cidade']}, {vaga['estado']}")
                st.write(f"**Salário:** R$ {vaga['salario']:,.0f}".replace(',', '.'))
                st.write(f"**Tipo:** {vaga['tipo']}")
            
            with col_b:
                st.write(f"**Skills:** {vaga['skills']}")
    

else:
    st.warning("Nenhuma vaga encontrada com os filtros selecionados.")
    st.info("Tente ajustar os filtros na barra lateral.")

# rdape
st.markdown("---")
st.caption("Use os filtros na barra lateral para refinar a visualização")

#botão para voltar ao menu
if st.button("Voltar ao Menu Principal", type="secondary"):
    st.switch_page("app.py")