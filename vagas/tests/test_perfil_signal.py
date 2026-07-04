import pytest

from .factories import criar_empregador, criar_candidato


@pytest.mark.django_db
def test_perfil_empregador_adiciona_usuario_ao_grupo_empregador():
    user = criar_empregador(username='chefe')

    assert user.groups.filter(name='Empregador').exists()
    assert not user.groups.filter(name='Candidato').exists()


@pytest.mark.django_db
def test_perfil_candidato_adiciona_usuario_ao_grupo_candidato():
    user = criar_candidato(username='joao')

    assert user.groups.filter(name='Candidato').exists()
    assert not user.groups.filter(name='Empregador').exists()


@pytest.mark.django_db
def test_trocar_tipo_do_perfil_move_usuario_de_grupo():
    user = criar_candidato(username='joao')
    perfil = user.perfil

    perfil.tipo = 'empregador'
    perfil.save()

    user.refresh_from_db()
    assert user.groups.filter(name='Empregador').exists()
    assert not user.groups.filter(name='Candidato').exists()
