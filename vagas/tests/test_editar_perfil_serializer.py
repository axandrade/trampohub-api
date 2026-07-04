import pytest

from vagas.serializers import EditarPerfilSerializer
from .factories import criar_empregador, criar_candidato


@pytest.mark.django_db
def test_username_de_outro_usuario_e_invalido():
    criar_empregador(username='outro')
    user = criar_empregador(username='eu')

    serializer = EditarPerfilSerializer(data={'username': 'outro'}, context={'user': user})

    assert not serializer.is_valid()
    assert 'username' in serializer.errors


@pytest.mark.django_db
def test_manter_o_proprio_username_e_valido():
    user = criar_empregador(username='eu')

    serializer = EditarPerfilSerializer(data={'username': 'eu'}, context={'user': user})

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_candidato_nao_pode_remover_o_email():
    user = criar_candidato(username='joao')

    serializer = EditarPerfilSerializer(data={'email': ''}, context={'user': user})

    assert not serializer.is_valid()
    assert 'email' in serializer.errors


@pytest.mark.django_db
def test_empregador_pode_deixar_email_em_branco():
    user = criar_empregador(username='chefe')

    serializer = EditarPerfilSerializer(data={'email': ''}, context={'user': user})

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_trocar_senha_sem_informar_senha_atual_e_invalido():
    user = criar_empregador(username='chefe', password='antiga123')

    serializer = EditarPerfilSerializer(data={'nova_senha': 'nova12345'}, context={'user': user})

    assert not serializer.is_valid()
    assert 'senha_atual' in serializer.errors


@pytest.mark.django_db
def test_trocar_senha_com_senha_atual_incorreta_e_invalido():
    user = criar_empregador(username='chefe', password='antiga123')

    serializer = EditarPerfilSerializer(
        data={'nova_senha': 'nova12345', 'senha_atual': 'errada'},
        context={'user': user},
    )

    assert not serializer.is_valid()
    assert 'senha_atual' in serializer.errors


@pytest.mark.django_db
def test_trocar_senha_com_senha_atual_correta():
    user = criar_empregador(username='chefe', password='antiga123')

    serializer = EditarPerfilSerializer(
        data={'nova_senha': 'nova12345', 'senha_atual': 'antiga123'},
        context={'user': user},
    )

    assert serializer.is_valid(), serializer.errors
    serializer.save()

    user.refresh_from_db()
    assert user.check_password('nova12345')
