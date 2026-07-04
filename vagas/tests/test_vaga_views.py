import datetime

import pytest
from rest_framework.test import APIClient

from vagas.models import Vaga
from .factories import criar_empregador, criar_candidato


@pytest.fixture
def api_client():
    return APIClient()


def _payload_vaga(**overrides):
    dados = dict(
        titulo='Dev Backend',
        descricao='Descricao',
        empresa='ACME',
        tipo_contrato='CLT',
        modalidade='Remoto',
        data_inicio='2026-01-01T00:00:00Z',
        data_fim='2026-12-31T00:00:00Z',
    )
    dados.update(overrides)
    return dados


def _criar_vaga(empregador_id, titulo='Dev Backend'):
    return Vaga(
        titulo=titulo, descricao='d', empresa='ACME', empregador_id=empregador_id,
        data_inicio=datetime.datetime(2026, 1, 1), data_fim=datetime.datetime(2026, 12, 31),
    ).save()


@pytest.mark.django_db
def test_anonimo_pode_listar_vagas(api_client):
    _criar_vaga(empregador_id=1)

    resp = api_client.get('/api/vagas/')

    assert resp.status_code == 200
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_anonimo_nao_pode_criar_vaga(api_client):
    resp = api_client.post('/api/vagas/', _payload_vaga(), format='json')

    assert resp.status_code in (401, 403)
    assert Vaga.objects.count() == 0


@pytest.mark.django_db
def test_candidato_nao_pode_criar_vaga(api_client):
    candidato = criar_candidato(username='joao')
    api_client.force_authenticate(user=candidato)

    resp = api_client.post('/api/vagas/', _payload_vaga(), format='json')

    assert resp.status_code == 403
    assert Vaga.objects.count() == 0


@pytest.mark.django_db
def test_empregador_pode_criar_vaga(api_client):
    empregador = criar_empregador(username='chefe')
    api_client.force_authenticate(user=empregador)

    resp = api_client.post('/api/vagas/', _payload_vaga(), format='json')

    assert resp.status_code == 201
    assert Vaga.objects.count() == 1


@pytest.mark.django_db
def test_empregador_id_e_sempre_do_usuario_autenticado_mesmo_se_forjado(api_client):
    empregador = criar_empregador(username='chefe')
    api_client.force_authenticate(user=empregador)

    resp = api_client.post('/api/vagas/', _payload_vaga(empregador_id=99999), format='json')

    assert resp.status_code == 201
    vaga = Vaga.objects.get(id=resp.data['id'])
    assert vaga.empregador_id == empregador.id


@pytest.mark.django_db
def test_empregador_ve_apenas_suas_proprias_vagas_quando_autenticado(api_client):
    emp1 = criar_empregador(username='emp1')
    emp2 = criar_empregador(username='emp2')
    _criar_vaga(empregador_id=emp1.id, titulo='V1')
    _criar_vaga(empregador_id=emp2.id, titulo='V2')

    api_client.force_authenticate(user=emp1)
    resp = api_client.get('/api/vagas/')

    assert resp.status_code == 200
    assert [v['titulo'] for v in resp.data] == ['V1']


@pytest.mark.django_db
def test_candidato_ve_todas_as_vagas(api_client):
    emp1 = criar_empregador(username='emp1')
    emp2 = criar_empregador(username='emp2')
    _criar_vaga(empregador_id=emp1.id, titulo='V1')
    _criar_vaga(empregador_id=emp2.id, titulo='V2')

    candidato = criar_candidato(username='joao')
    api_client.force_authenticate(user=candidato)
    resp = api_client.get('/api/vagas/')

    assert resp.status_code == 200
    assert len(resp.data) == 2


@pytest.mark.django_db
def test_empregador_nao_pode_editar_vaga_de_outro_empregador(api_client):
    emp1 = criar_empregador(username='emp1')
    emp2 = criar_empregador(username='emp2')
    vaga = _criar_vaga(empregador_id=emp2.id)

    api_client.force_authenticate(user=emp1)
    resp = api_client.patch(f'/api/vagas/{vaga.id}/', {'titulo': 'Hackeado'}, format='json')

    assert resp.status_code == 404
    vaga.reload()
    assert vaga.titulo != 'Hackeado'
