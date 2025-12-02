# Sistema de Vagas — Aplicação Web Completa

Desenvolvido por: Arnaldo Godoy, Gustavo Gomes e Gustavo Frias

Aplicação desenvolvida para o projeto final da disciplina de **Laboratório de Banco de Dados**, integrando conceitos de bancos relacionais, NoSQL (MongoDB), autenticação, visualização de dados e RAG (Retrieval-Augmented Generation).

O sistema fornece uma experiência completa para **Empregadores**, **Candidatos** e **Administradores**, permitindo publicação de vagas, gestão de currículos, consulta inteligente e interação em linguagem natural.

---

**Link da aplicação:** https://sistema-de-vagas-aplicacao-labbd-2025.streamlit.app

---

O grupo desenvolveu a aplicação a partir da base fornecida durante as aulas da disciplina Laboratório de Banco de Dados (Unesp - 2025). O sistema foi implementado em Python, utilizando a biblioteca Streamlit para construção da interface Web e organização dos fluxos de interação com o usuário.

Para a camada de persistência, utilizou-se o MongoDB, no qual foram estruturadas coleções específicas para Usuários, Currículos e Vagas, permitindo um gerenciamento eficiente e flexível dos dados. Parte das funcionalidades do sistema faz uso de recursos avançados, como Full-Text Search (FTS), integração com Tableau, visualização da distribuição geográfica das vagas, além de um mecanismo de autenticação baseado em níveis hierárquicos (Administrador, Empregador e Candidato).

O banco de dados foi inicializado a partir dos arquivos previamente populados e disponibilizados pelo docente responsável pela disciplina, garantindo consistência para testes e validação das funcionalidades implementadas.

---

## Estrutura de Dados no MongoDB

A aplicação utiliza o MongoDB como banco de dados principal, organizado em três coleções: **Usuários**, **Currículos** e **Vagas**. Utilizamos do Atlas, versão em nuvem do MongoDB, para trabalharmos entre nós e podermos subir para a nuvem uma aplicação funcional.

Exemplos da estrutura das Collections:

**Collection Usuários**

```json
{
  "nome": "Sr. Adm",
  "email": "adm@sdv.com",
  "senha": "adminstrador123",
  "tipo": "administrador"
}
````
**Collection Currículos**

```json
{
  "id": 1,
  "nome": "Henrique Ferreira Santos",
  "email": "henrique.ferreira.santos@exemplo.com",
  "telefone": "+55 11 91896-2569",
  "formacao": "Bacharelado em Sistemas de Informação",
  "experiencia": "5 anos como analista de dados",
  "skills": [
    "React", "PostgreSQL", "MongoDB",
    "Azure", "Python", "Java"
  ],
  "idiomas": ["Inglês"],
  "certificacoes": [
    "Certified Kubernetes Administrator",
    "Microsoft Certified: Azure Fundamentals"
  ],
  "resumo": "Profissional com 5 anos como analista de dados, aplicando tecnologias …",
  "empresas_previas": ["IBM Brasil"],
  "ids_contatos": [33, 13, 53, 70, 96, 92, 27, 2, 54, 29, 32]
}
````
**Collection Vagas**

```json
{
  "id": 1,
  "titulo": "Desenvolvedor Frontend",
  "descricao": "Conduzir projetos de ciência de dados, desde a coleta e limpeza até a …",
  "cidade": "Rio Claro",
  "estado": "SP",
  "tipo_contratacao": "CLT",
  "salario": 9020,
  "empresa": "Whirpool",
  "skills": ["AWS", "Python", "Scrum"]
}
````
Para cada collections, existe a funcionalidade de fazer o cadastro de dados dependendo do nível de usuário.


Fique a vontade para explorar nossa aplicação de Sistema de Vagas!
