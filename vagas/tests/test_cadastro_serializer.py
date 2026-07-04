import pytest

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from vagas.serializers import CadastroSerializer

GIF_1X1 = (
    b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,'
    b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
)


def _foto():
    return SimpleUploadedFile('foto.gif', GIF_1X1, content_type='image/gif')


@pytest.mark.django_db
def test_username_duplicado_e_invalido():
    User.objects.create_user(username='joao', password='123456')

    serializer = CadastroSerializer(data={'username': 'joao', 'password': '123456', 'tipo': 'empregador'})

    assert not serializer.is_valid()
    assert 'username' in serializer.errors


@pytest.mark.django_db
def test_candidato_sem_foto_e_invalido():
    serializer = CadastroSerializer(data={
        'username': 'maria', 'password': '123456', 'tipo': 'candidato', 'email': 'maria@example.com',
    })

    assert not serializer.is_valid()
    assert 'foto' in serializer.errors


@pytest.mark.django_db
def test_candidato_sem_email_e_invalido():
    serializer = CadastroSerializer(data={
        'username': 'maria', 'password': '123456', 'tipo': 'candidato', 'foto': _foto(),
    })

    assert not serializer.is_valid()
    assert 'email' in serializer.errors


@pytest.mark.django_db
def test_candidato_com_foto_e_email_e_valido():
    serializer = CadastroSerializer(data={
        'username': 'maria', 'password': '123456', 'tipo': 'candidato',
        'foto': _foto(), 'email': 'maria@example.com',
    })

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_empregador_nao_precisa_de_foto_nem_email():
    serializer = CadastroSerializer(data={
        'username': 'chefe', 'password': '123456', 'tipo': 'empregador', 'nome_empresa': 'ACME',
    })

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_create_empregador_entra_no_grupo_empregador():
    serializer = CadastroSerializer(data={
        'username': 'chefe', 'password': '123456', 'tipo': 'empregador', 'nome_empresa': 'ACME',
    })
    assert serializer.is_valid(), serializer.errors

    user = serializer.save()

    assert user.perfil.tipo == 'empregador'
    assert user.groups.filter(name='Empregador').exists()
    assert user.check_password('123456')


@pytest.mark.django_db
def test_create_candidato_entra_no_grupo_candidato():
    serializer = CadastroSerializer(data={
        'username': 'joao', 'password': '123456', 'tipo': 'candidato',
        'foto': _foto(), 'email': 'joao@example.com',
    })
    assert serializer.is_valid(), serializer.errors

    user = serializer.save()

    assert user.perfil.tipo == 'candidato'
    assert user.groups.filter(name='Candidato').exists()
