import pytest
from freezegun import freeze_time
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .factories import criar_empregador


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_login_retorna_token_valido(api_client):
    criar_empregador(username='chefe', password='senha123')

    resp = api_client.post('/api/token/', {'username': 'chefe', 'password': 'senha123'}, format='json')

    assert resp.status_code == 200
    assert 'token' in resp.data
    assert Token.objects.count() == 1


@pytest.mark.django_db
def test_login_invalida_token_anterior_e_emite_um_novo(api_client):
    user = criar_empregador(username='chefe', password='senha123')
    token_antigo = Token.objects.create(user=user)

    resp = api_client.post('/api/token/', {'username': 'chefe', 'password': 'senha123'}, format='json')

    assert resp.status_code == 200
    assert resp.data['token'] != token_antigo.key
    assert Token.objects.count() == 1
    assert not Token.objects.filter(key=token_antigo.key).exists()


@pytest.mark.django_db
def test_token_recem_criado_autentica(api_client):
    user = criar_empregador(username='chefe')
    token = Token.objects.create(user=user)

    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    resp = api_client.get('/api/perfil/me/')

    assert resp.status_code == 200


@pytest.mark.django_db
def test_token_com_14_minutos_ainda_e_valido(api_client):
    with freeze_time('2026-01-01 10:00:00'):
        user = criar_empregador(username='chefe')
        token = Token.objects.create(user=user)

    with freeze_time('2026-01-01 10:14:00'):
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        resp = api_client.get('/api/perfil/me/')

    assert resp.status_code == 200


@pytest.mark.django_db
def test_token_expirado_apos_15_minutos_e_rejeitado_e_removido(api_client):
    with freeze_time('2026-01-01 10:00:00'):
        user = criar_empregador(username='chefe')
        token = Token.objects.create(user=user)

    with freeze_time('2026-01-01 10:16:00'):
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        resp = api_client.get('/api/perfil/me/')

    assert resp.status_code == 401
    assert not Token.objects.filter(key=token.key).exists()


@pytest.mark.django_db
def test_fluxo_completo_login_usar_expirar_e_logar_de_novo(api_client):
    criar_empregador(username='chefe', password='senha123')

    with freeze_time('2026-01-01 10:00:00'):
        resp_login = api_client.post('/api/token/', {'username': 'chefe', 'password': 'senha123'}, format='json')
        token = resp_login.data['token']

    with freeze_time('2026-01-01 10:16:00'):
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        resp = api_client.get('/api/perfil/me/')
        assert resp.status_code == 401

        novo_client = APIClient()
        resp_login2 = novo_client.post('/api/token/', {'username': 'chefe', 'password': 'senha123'}, format='json')
        assert resp_login2.status_code == 200
        novo_token = resp_login2.data['token']
        assert novo_token != token

        novo_client.credentials(HTTP_AUTHORIZATION=f'Token {novo_token}')
        resp2 = novo_client.get('/api/perfil/me/')
        assert resp2.status_code == 200
