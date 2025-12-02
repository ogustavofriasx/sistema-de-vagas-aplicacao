import streamlit as st
from database import get_collection_vagas, get_collection_curriculos
from utils.auth import require_role
import pandas as pd
from collections import Counter

# Configuração da página
st.set_page_config(
    page_title="Matching Automático com FTS",
    page_icon="🤝",
    layout="wide"
)

st.title("🔍 Matching Automático (com FTS Score)")


st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}   /* esconde a lista automática */
[data-testid="stSidebar"] section:nth-child(1) {padding-top: 0;}
</style>
""", unsafe_allow_html=True)


with st.sidebar:

    st.title("Sistema de Vagas")
    
    nome = st.session_state.get("nome", "")
    tipo = st.session_state.get("tipo", "")

    st.write(f"👤 {nome} ({tipo})")

    st.divider()

    if tipo == "administrador":
        if st.button("Home", type="primary", use_container_width=True):
            st.switch_page("app.py")

        if st.button("Cadastrar Currículo",type="primary", use_container_width=True):
            st.switch_page("pages/cadastrar_curriculo.py")

        if st.button("Cadastrar Usuário", type="primary", use_container_width=True):
            st.switch_page("pages/cadastrar_usuarios.py")
        
        if st.button("Cadastrar Vaga", type="primary", use_container_width=True):
            st.switch_page("pages/cadastrar_vagas.py")
        
        if st.button("Currículos", type="primary", use_container_width=True):
            st.switch_page("pages/curriculos.py")
        
        if st.button("Mapa de vagas", type="primary", use_container_width=True):
            st.switch_page("pages/distribuicao_geografica.py")
        
        if st.button("Matching", type="primary", use_container_width=True):
            st.switch_page("pages/matching.py")

        if st.button("Vagas", type="primary", use_container_width=True):
            st.switch_page("pages/vagas.py")

    elif tipo == "empregador":
        if st.button("Home", type="primary", use_container_width=True):
            st.switch_page("app.py")

        if st.button("Cadastrar Vaga", type="primary", use_container_width=True):
            st.switch_page("pages/cadastrar_vagas.py")

        if st.button("Currículos", type="primary", use_container_width=True):
            st.switch_page("pages/curriculos.py")

        if st.button("Matching", type="primary", use_container_width=True):
            st.switch_page("pages/matching.py")

        if st.button("Vagas", type="primary", use_container_width=True):
            st.switch_page("pages/vagas.py")

    elif tipo == "candidato":
        if st.button("Home", type="primary", use_container_width=True):
            st.switch_page("app.py")

        if st.button("Cadastrar Currículo", type="primary", use_container_width=True):
            st.switch_page("pages/cadastrar_curriculo.py")

        if st.button("Mapa de vagas",type="primary", use_container_width=True):
            st.switch_page("pages/distribuicao_geografica.py")

        if st.button("Vagas", type="primary", use_container_width=True):
            st.switch_page("pages/vagas.py")


def buscar_candidatos_por_skills_fts(skills_vaga, limite=10):
    """
    Busca candidatos usando FTS baseado nas skills da vaga
    Retorna candidatos com score de relevância do FTS
    """
    collection = get_collection_curriculos()
    
    if not skills_vaga:
        return []
    
    #cria query fts com as skills da vaga
    #usar operador OR para buscar qualquer uma das skills
    query_fts = " ".join(skills_vaga)
    
    try:
        #busca fts na coleção de currículos
        resultados = collection.find(
            {"$text": {"$search": query_fts}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limite * 2)  #busca mais para filtrar depois
        
        candidatos_com_score = []
        for doc in resultados:
            # Calcular match detalhado das skills
            skills_candidato = doc.get('skills', [])
            skills_encontradas = []
            skills_faltando = []
            
            # Converter para lowercase para comparação
            skills_vaga_lower = [s.lower() for s in skills_vaga]
            skills_candidato_lower = [s.lower() for s in skills_candidato]
            
            # Verificar quais skills da vaga estão no candidato
            for skill_vaga in skills_vaga_lower:
                encontrou = False
                for skill_cand in skills_candidato_lower:
                    if skill_vaga in skill_cand or skill_cand in skill_vaga:
                        skills_encontradas.append(skill_vaga)
                        encontrou = True
                        break
                if not encontrou:
                    skills_faltando.append(skill_vaga)
            
            #score fts (normalizar para 0-100)
            score_fts = doc.get('score', 0)
            score_fts_normalizado = min(score_fts * 10, 100)  # Ajuste de escala
            
            #score de match de skills (0-100)
            if skills_vaga_lower:
                score_skills = (len(skills_encontradas) / len(skills_vaga_lower)) * 100
            else:
                score_skills = 0
            
            # Score total (combina FTS e match de skills)
            # Peso: 70% FTS score + 30% skills match
            score_total = (score_fts_normalizado * 0.7) + (score_skills * 0.3)
            
            candidatos_com_score.append({
                "curriculo_id": doc["_id"],
                "nome": doc["nome"],
                "email": doc["email"],
                "telefone": doc["telefone"],
                "skills_candidato": skills_candidato,
                "experiencia": doc["experiencia"],
                "formacao": doc["formacao"],
                "idiomas": doc["idiomas"],
                "empresas_previas": doc["empresas_previas"],
                "score_fts_bruto": round(score_fts, 4),
                "score_fts_normalizado": round(score_fts_normalizado, 1),
                "score_skills": round(score_skills, 1),
                "score_total": round(score_total, 1),
                "skills_encontradas": skills_encontradas,
                "skills_faltando": skills_faltando,
                "match_percentual": f"{len(skills_encontradas)}/{len(skills_vaga)}",
                "cidade": doc.get('cidade', 'N/A'),
                "estado": doc.get('estado', 'N/A')
            })
        
        # Ordenar por score total (maior primeiro)
        candidatos_com_score.sort(key=lambda x: x["score_total"], reverse=True)
        return candidatos_com_score[:limite]
        
    except Exception as e:
        st.error(f"Erro na busca FTS: {str(e)}")
        st.info("Certifique-se de que o índice de texto foi criado na coleção 'curriculos'")
        return []

def buscar_vagas_fts_com_skills(skills_vaga):
    """
    Busca vagas similares usando FTS (para comparação)
    """
    collection = get_collection_vagas()
    
    if not skills_vaga:
        return []
    
    query_fts = " ".join(skills_vaga)
    
    try:
        resultados = collection.find(
            {"$text": {"$search": query_fts}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(5)
        
        return list(resultados)
    except:
        return []

def calcular_score_final(candidato, vaga):
    """
    Calcula score final combinando FTS e outros fatores
    """
    # Base: score fts normalizado (ja calculado na busca)
    score_base = candidato["score_fts_normalizado"]
    
    # Bonus por experiência mencionada (talvez tirar)
    bonus_experiencia = 0
    experiencia_lower = candidato["experiencia"].lower()
    for skill in vaga['skills']:
        if skill.lower() in experiencia_lower:
            bonus_experiencia += 2  # 2% por skill mencionada
    
    # Bonus por formação relevante
    bonus_formacao = 0
    formacao_lower = candidato["formacao"].lower()
    palavras_chave_formacao = ['engenharia', 'ciência', 'tecnologia', 'sistemas', 
                              'informática', 'computação', 'desenvolvimento', 'programação']
    for palavra in palavras_chave_formacao:
        if palavra in formacao_lower:
            bonus_formacao += 3
    
    # Bonus por localização (se vaga tem localização, talvez tirar)
    bonus_localizacao = 0
    if 'cidade' in vaga and 'estado' in vaga:
        if candidato.get('cidade') == vaga['cidade']:
            bonus_localizacao += 5
        elif candidato.get('estado') == vaga['estado']:
            bonus_localizacao += 3
    
    # Score final
    score_final = min(
        score_base + bonus_experiencia + bonus_formacao + bonus_localizacao,
        100
    )
    
    return {
        "score_final": round(score_final, 1),
        "bonus_experiencia": bonus_experiencia,
        "bonus_formacao": bonus_formacao,
        "bonus_localizacao": bonus_localizacao
    }

def main():
    #verificar permissão
    if not require_role(["administrador", "empregador"]):
        if st.button("Fazer login", type="primary"):
            st.switch_page("app.py")
        return
    
    # Obter lista de vagas
    vagas_collection = get_collection_vagas()
    vagas = list(vagas_collection.find())
    
    if not vagas:
        st.warning("Nenhuma vaga cadastrada no sistema.")
        if st.button("Cadastrar Nova Vaga", type="primary"):
            st.switch_page("pages/cadastrar_vaga.py")
        return
    
    # Layout principal
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Selecionar Vaga")
        
        # Criar lista de opções para o selectbox
        opcoes_vagas = [f"{v['titulo']} - {v['empresa']}" for v in vagas]
        vaga_selecionada_str = st.selectbox(
            "Escolha uma vaga:",
            opcoes_vagas,
            help="Selecione a vaga para encontrar candidatos compatíveis"
        )
        
        # Encontrar vaga selecionada
        vaga_selecionada = None
        if vaga_selecionada_str:
            for v in vagas:
                if f"{v['titulo']} - {v['empresa']}" == vaga_selecionada_str:
                    vaga_selecionada = v
                    break
        
        if vaga_selecionada:
            # Mostrar skills da vaga
            st.info(f"**Skills da vaga:** {', '.join(vaga_selecionada['skills'])}")
            
            # Configurações da busca
            st.subheader("Configurações da Busca")
            
            limite_resultados = st.slider(
                "Número de candidatos:",
                min_value=5,
                max_value=20,
                value=10
            )
            
            peso_fts = st.slider(
                "Peso do FTS vs Skills:",
                min_value=0,
                max_value=100,
                value=70,
                help="Quanto maior, mais importância para o score do FTS"
            )
            
            # Botão para executar matching
            if st.button("Buscar Candidatos com FTS", type="primary", use_container_width=True):
                st.session_state['executar_matching'] = True
                st.session_state['vaga_selecionada'] = vaga_selecionada
                st.session_state['limite'] = limite_resultados
                st.session_state['peso_fts'] = peso_fts
            
            # Botão para limpar
            if st.button("Limpar Resultados", use_container_width=True):
                for key in ['executar_matching', 'resultados_matching', 'vaga_selecionada']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        # Informações sobre o algoritmo FTS
        with st.expander("Como funciona o FTS?"):
            st.markdown("""
            **Full-Text Search (FTS) no MongoDB:**
            
            1. **Índice de Texto:**
               - Busca em múltiplos campos simultaneamente
               - Campos indexados: skills, experiência, formação, empresas
            
            2. **Score de Relevância:**
               - Calculado pelo MongoDB Atlas
               - Baseado em TF-IDF (frequência do termo)
               - Termos mais raros = maior score
            
            3. **Nossa Fórmula:**
               - **Score FTS (70%):** Relevância textual do MongoDB
               - **Match Skills (30%):** Porcentagem de skills encontradas
               - **Bônus:** Experiência, formação, localização
            
            **Índice necessário:**
            ```javascript
            db.curriculos.createIndex({
              "skills": "text",
              "experiencia": "text",
              "formacao": "text",
              "empresas_previas": "text",
              "nome": "text"
            })
            ```
            """)
    
    with col2:
        st.subheader("Resultados do Matching com FTS")
        
        # Executar matching se solicitado
        if 'executar_matching' in st.session_state and st.session_state['executar_matching']:
            vaga = st.session_state['vaga_selecionada']
            
            with st.spinner(f"Buscando candidatos para '{vaga['titulo']}'..."):
                # Buscar candidatos usando FTS com as skills da vaga
                resultados = buscar_candidatos_por_skills_fts(
                    vaga['skills'],
                    st.session_state['limite']
                )
                
                # Aplicar pesos personalizados
                peso_fts = st.session_state['peso_fts'] / 100
                peso_skills = 1 - peso_fts
                
                for candidato in resultados:
                    # Recalcular score com pesos personalizados
                    candidato['score_total'] = round(
                        (candidato['score_fts_normalizado'] * peso_fts) + 
                        (candidato['score_skills'] * peso_skills), 
                        1
                    )
                
                # Ordenar novamente com novo score
                resultados.sort(key=lambda x: x["score_total"], reverse=True)
                
                st.session_state['resultados_matching'] = resultados
                st.session_state['executar_matching'] = False
        
        # Mostrar resultados se existirem
        if 'resultados_matching' in st.session_state and 'vaga_selecionada' in st.session_state:
            resultados = st.session_state['resultados_matching']
            vaga = st.session_state['vaga_selecionada']
            
            # Mostrar informações da vaga
            with st.container(border=True):
                col_vaga1, col_vaga2 = st.columns([2, 1])
                with col_vaga1:
                    st.markdown(f"### 🎯 Vaga: **{vaga['titulo']}**")
                    st.write(f"**Empresa:** {vaga['empresa']} | **Local:** {vaga['cidade']}, {vaga['estado']}")
                    st.write(f"**Skills:** {', '.join(vaga['skills'])}")
                with col_vaga2:
                    st.write(f"**Salário:** R$ {vaga['salario']}")
                    st.write(f"**Tipo:** {vaga.get('tipo_contratacao', 'Não especificado')}")    
                
            # Mostrar cada candidato
            st.subheader("Candidatos por Relevância FTS")
                
            for idx, candidato in enumerate(resultados, 1):
                    
                    with st.container(border=True):
                        # Cabeçalho com scores
                        col_head1, col_head2, col_head3 = st.columns([3, 1, 1])
                        with col_head1:
                            st.markdown(f"### {idx}º - {candidato['nome']}")
                        with col_head2:
                            st.metric("Score Total", f"{candidato['score_total']}%")
                        with col_head3:
                            st.metric("FTS", f"{candidato['score_fts_normalizado']}%")
                        
                        # Detalhes do candidato
                        col_det1, col_det2 = st.columns(2)
                        with col_det1:
                            st.write(f"**Email:** {candidato['email']}")
                            st.write(f"**Telefone:** {candidato['telefone']}")
                            st.write(f"**Local:** {candidato.get('cidade', 'N/A')}, {candidato.get('estado', 'N/A')}")
                            
                        with col_det2:
                            st.write(f"**Idiomas:** {', '.join(candidato['idiomas'])}")
                            st.write(f"**Formação:** {candidato['formacao'][:80]}..." if len(candidato['formacao']) > 80 else f"**🎓 Formação:** {candidato['formacao']}")
                        
                        # Skills match
                        col_skill1, col_skill2 = st.columns(2)
                        with col_skill1:
                            if candidato['skills_encontradas']:
                                st.success(f"**Skills match:** {candidato['match_percentual']}")
                                st.write(f"Encontradas: {', '.join(candidato['skills_encontradas'])}")
                            else:
                                st.warning("Nenhuma skill encontrada")
                        
                        with col_skill2:
                            if candidato['skills_faltando']:
                                st.error(f"**Skills faltando:** {len(candidato['skills_faltando'])}")
                                with st.expander("Ver skills faltando"):
                                    st.write(", ".join(candidato['skills_faltando']))
                        
                        # Skills do candidato
                        st.write(f"**Skills do candidato:** {', '.join(candidato['skills_candidato'])}")
                        
                        # Score breakdown
                        with st.expander("Detalhes do Score"):
                            col_score1, col_score2 = st.columns(2)
                            with col_score1:
                                st.write(f"**Score FTS bruto:** {candidato['score_fts_bruto']}")
                                st.write(f"**Score FTS normalizado:** {candidato['score_fts_normalizado']}%")
                                st.write(f"**Score Skills:** {candidato['score_skills']}%")
                            with col_score2:
                                st.write(f"**Match de skills:** {candidato['match_percentual']}")
                                st.write(f"**Peso FTS/Skills:** {st.session_state.get('peso_fts', 70)}/30")
                        
                        #biotão de ação
                        if st.button(f"Contatar", key=f"contatar_{candidato['curriculo_id']}"):
                            st.info(f"**Email:** {candidato['email']}  \n**Telefone:** {candidato['telefone']}")
                        
                        st.markdown("---")
                
                
            # Vagas similares (usando mesmo FTS)
            st.subheader("Vagas Similares")
            vagas_similares = buscar_vagas_fts_com_skills(vaga['skills'])
            if vagas_similares:
                for vaga_sim in vagas_similares[:3]:
                    if vaga_sim['_id'] != vaga['_id']:
                        with st.container(border=True):
                            st.write(f"**{vaga_sim['titulo']}** - {vaga_sim['empresa']}")
                            st.write(f"Score FTS: {vaga_sim.get('score', 0):.2f}")
                            st.write(f"Skills: {', '.join(vaga_sim['skills'][:3])}...")
            else:
                st.warning("Nenhum candidato encontrado com FTS para esta vaga.")
                st.markdown("""
                **Sugestões:**
                1. Verifique se o índice FTS foi criado na coleção `curriculos`
                2. Tente buscar por termos mais gerais
                3. Verifique se há currículos cadastrados
                """)
                
                if st.button("Criar Índice FTS"):
                    st.code("""
                    // Execute no MongoDB Atlas
                    db.curriculos.createIndex({
                      "skills": "text",
                      "experiencia": "text",
                      "formacao": "text",
                      "empresas_previas": "text",
                      "nome": "text"
                    })
                    """)
        
        else:
            # Estado inicial
            st.info("Selecione uma vaga e clique em 'Buscar Candidatos com FTS'")
            
            with st.expander("Comece Aqui"):
                st.markdown("""
                **Fluxo do Sistema:**
                
                1. **Selecione uma vaga** → Sistema extrai automaticamente as skills
                2. **Clique em Buscar** → Usa FTS para encontrar candidatos relevantes
                3. **Analise resultados** → Ordenados por score de relevância FTS
                4. **Exporte ou contate** → Ações rápidas disponíveis
                
                **Vantagens do FTS:**
                - Busca em múltiplos campos simultaneamente
                - Score de relevância calculado pelo MongoDB
                - Considera frequência e importância dos termos
                - Mais preciso que busca exata
                """)
    
    # Botão para voltar
    st.markdown("---")
    if st.button("Voltar ao Menu Principal", type="secondary"):
        st.switch_page("app.py")

if __name__ == "__main__":
    main()