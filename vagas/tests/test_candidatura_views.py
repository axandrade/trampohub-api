import datetime

import pytest
from freezegun import freeze_time
from rest_framework.test import APIClient

from vagas.models import Vaga, Candidatura
from .factories import criar_empregador, criar_candidato


@pytest.fixture
def api_client():
    return APIClient()


def _criar_vaga(empregador_id, data_fim):
    return Vaga(
        titulo='Dev', descricao='d', empresa='ACME', empregador_id=empregador_id,
        data_inicio=datetime.datetime(2026, 1, 1), data_fim=data_fim,
    ).save()


@pytest.mark.django_db
def test_candidato_pode_se_candidatar_a_vaga_aberta(api_client):
    empregador = criar_empregador(username='chefe')
    candidato = criar_candidato(username='joao')
    vaga = _criar_vaga(empregador.id, datetime.datetime(2026, 12, 31))

    api_client.force_authenticate(user=candidato)
    resp = api_client.post('/api/candidaturas/', {'vaga': str(vaga.id)}, format='json')

    assert resp.status_code == 201
    assert Candidatura.objects.count() == 1
    assert Candidatura.objects.first().candidato_id == candidato.id


@pytest.mark.django_db
def test_empregador_nao_pode_se_candidatar(api_client):
    empregador = criar_empregador(username='chefe')
    outro_empregador = criar_empregador(username='chefe2')
    vaga = _criar_vaga(outro_empregador.id, datetime.datetime(2026, 12, 31))

    api_client.force_authenticate(user=empregador)
    resp = api_client.post('/api/candidaturas/', {'vaga': str(vaga.id)}, format='json')

    assert resp.status_code == 403
    assert Candidatura.objects.count() == 0


@pytest.mark.django_db
def test_nao_pode_se_candidatar_a_vaga_expirada(api_client):
    empregador = criar_empregador(username='chefe')
    candidato = criar_candidato(username='joao')
    vaga = _criar_vaga(empregador.id, datetime.datetime(2026, 1, 31))

    with freeze_time('2026-02-15'):
        api_client.force_authenticate(user=candidato)
        resp = api_client.post('/api/candidaturas/', {'vaga': str(vaga.id)}, format='json')

    assert resp.status_code == 400
    assert Candidatura.objects.count() == 0


@pytest.mark.django_db
def test_nao_pode_se_candidatar_duas_vezes_na_mesma_vaga(api_client):
    empregador = criar_empregador(username='chefe')
    candidato = criar_candidato(username='joao')
    vaga = _criar_vaga(empregador.id, datetime.datetime(2026, 12, 31))

    api_client.force_authenticate(user=candidato)
    resp1 = api_client.post('/api/candidaturas/', {'vaga': str(vaga.id)}, format='json')
    resp2 = api_client.post('/api/candidaturas/', {'vaga': str(vaga.id)}, format='json')

    assert resp1.status_code == 201
    assert resp2.status_code == 400
    assert Candidatura.objects.count() == 1


@pytest.mark.django_db
def test_candidato_ve_apenas_suas_proprias_candidaturas(api_client):
    empregador = criar_empregador(username='chefe')
    candidato1 = criar_candidato(username='joao')
    candidato2 = criar_candidato(username='maria')
    vaga = _criar_vaga(empregador.id, datetime.datetime(2026, 12, 31))
    Candidatura(vaga=vaga, candidato_id=candidato1.id).save()
    Candidatura(vaga=vaga, candidato_id=candidato2.id).save()

    api_client.force_authenticate(user=candidato1)
    resp = api_client.get('/api/candidaturas/')

    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert resp.data[0]['candidato_id'] == candidato1.id


@pytest.mark.django_db
def test_empregador_ve_candidaturas_apenas_das_proprias_vagas(api_client):
    emp1 = criar_empregador(username='emp1')
    emp2 = criar_empregador(username='emp2')
    candidato = criar_candidato(username='joao')
    vaga_emp1 = _criar_vaga(emp1.id, datetime.datetime(2026, 12, 31))
    vaga_emp2 = _criar_vaga(emp2.id, datetime.datetime(2026, 12, 31))
    Candidatura(vaga=vaga_emp1, candidato_id=candidato.id).save()
    Candidatura(vaga=vaga_emp2, candidato_id=candidato.id).save()

    api_client.force_authenticate(user=emp1)
    resp = api_client.get('/api/candidaturas/')

    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert resp.data[0]['vaga'] == str(vaga_emp1.id)
