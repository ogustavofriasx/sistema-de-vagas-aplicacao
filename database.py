from pymongo import MongoClient, ReturnDocument
import streamlit as st

@st.cache_resource
def get_database():
    uri = st.secrets["mongodb"]["uri"]
    client = MongoClient(uri)
    db = st.secrets["mongodb"]["database"]
    return client[db]

def get_collection_vagas():
    db = get_database()
    collection_name = st.secrets["mongodb"]["collection_vagas"]
    return db[collection_name]

def get_collection_curriculos():
    db = get_database()
    collection_name = st.secrets["mongodb"]["collection_curriculos"]
    return db[collection_name]

def get_collection_users():
    db = get_database()
    collection_name = st.secrets["mongodb"]["collection_users"]
    return db[collection_name]

def get_next_sequence(name, collection):
    db = get_database()
    counter = db["counters"]

    # tenta achar o contador existente
    result = counter.find_one({"_id": name})

    if result is None:
        # contador ainda não existe → pegar o maior id atual na collection
        ultimo = collection.find_one(sort=[("id", -1)])
        ultimo_id = ultimo["id"] if ultimo and "id" in ultimo else 0

        # cria o contador começando do último id
        result = counter.find_one_and_update(
            {"_id": name},
            {"$set": {"seq": ultimo_id}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

    # incrementa e retorna o novo valor
    result = counter.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        return_document=ReturnDocument.AFTER
    )

    return result["seq"]
