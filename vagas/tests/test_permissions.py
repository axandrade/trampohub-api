from types import SimpleNamespace

import pytest

from django.contrib.auth.models import AnonymousUser

from vagas.permissions import IsEmpregador, IsCandidato
from .factories import criar_empregador, criar_candidato


@pytest.mark.django_db
def test_is_empregador_permite_empregador():
    user = criar_empregador(username='chefe')
    request = SimpleNamespace(user=user)

    assert IsEmpregador().has_permission(request, None) is True


@pytest.mark.django_db
def test_is_empregador_bloqueia_candidato():
    user = criar_candidato(username='joao')
    request = SimpleNamespace(user=user)

    assert IsEmpregador().has_permission(request, None) is False


def test_is_empregador_bloqueia_anonimo():
    request = SimpleNamespace(user=AnonymousUser())

    assert IsEmpregador().has_permission(request, None) is False


@pytest.mark.django_db
def test_is_candidato_permite_candidato():
    user = criar_candidato(username='joao')
    request = SimpleNamespace(user=user)

    assert IsCandidato().has_permission(request, None) is True


@pytest.mark.django_db
def test_is_candidato_bloqueia_empregador():
    user = criar_empregador(username='chefe')
    request = SimpleNamespace(user=user)

    assert IsCandidato().has_permission(request, None) is False


def test_is_candidato_bloqueia_anonimo():
    request = SimpleNamespace(user=AnonymousUser())

    assert IsCandidato().has_permission(request, None) is False
