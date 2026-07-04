import pytest
from mongoengine.connection import get_db

# A conexao com o mongomock e feita em trampohub_api/settings.py quando
# rodando sob pytest, antes de qualquer model/serializer ser importado.
# Aqui so limpamos as colecoes entre um teste e outro.


@pytest.fixture(autouse=True)
def mongo_test_db():
    yield
    db = get_db('default')
    for nome_colecao in db.list_collection_names():
        db.drop_collection(nome_colecao)
