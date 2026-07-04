import datetime

from freezegun import freeze_time

from vagas.models import Vaga
from vagas.serializers import VagaSerializer


def _dados_vaga(**overrides):
    dados = dict(
        titulo='Dev Backend',
        descricao='Descricao da vaga',
        empresa='ACME',
        tipo_contrato='CLT',
        modalidade='Remoto',
        data_inicio='2026-01-01T00:00:00Z',
        data_fim='2026-01-31T00:00:00Z',
    )
    dados.update(overrides)
    return dados


def test_data_fim_antes_de_data_inicio_e_invalido():
    dados = _dados_vaga(data_inicio='2026-02-01T00:00:00Z', data_fim='2026-01-01T00:00:00Z')

    serializer = VagaSerializer(data=dados)

    assert not serializer.is_valid()
    assert 'data_fim' in serializer.errors


def test_data_fim_igual_a_data_inicio_e_valido():
    dados = _dados_vaga(data_inicio='2026-01-01T00:00:00Z', data_fim='2026-01-01T00:00:00Z')

    serializer = VagaSerializer(data=dados)

    assert serializer.is_valid(), serializer.errors


def test_data_fim_e_obrigatoria():
    dados = _dados_vaga()
    del dados['data_fim']

    serializer = VagaSerializer(data=dados)

    assert not serializer.is_valid()
    assert 'data_fim' in serializer.errors


def test_datas_com_timezone_sao_convertidas_para_utc_naive():
    dados = _dados_vaga(
        data_inicio='2026-01-01T10:00:00-03:00',
        data_fim='2026-01-31T10:00:00-03:00',
    )

    serializer = VagaSerializer(data=dados)

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data['data_inicio'].tzinfo is None
    assert serializer.validated_data['data_inicio'] == datetime.datetime(2026, 1, 1, 13, 0, 0)


def test_empregador_id_e_somente_leitura():
    dados = _dados_vaga(empregador_id=999)

    serializer = VagaSerializer(data=dados)

    assert serializer.is_valid(), serializer.errors
    assert 'empregador_id' not in serializer.validated_data


def test_status_aberta_quando_data_fim_no_futuro():
    with freeze_time('2026-01-15'):
        vaga = Vaga(
            titulo='Dev', descricao='desc', empresa='ACME', empregador_id=1,
            data_inicio=datetime.datetime(2026, 1, 1),
            data_fim=datetime.datetime(2026, 1, 31),
        ).save()

        assert VagaSerializer(vaga).data['status'] == 'Aberta'


def test_status_expirada_quando_data_fim_no_passado():
    with freeze_time('2026-02-15'):
        vaga = Vaga(
            titulo='Dev', descricao='desc', empresa='ACME', empregador_id=1,
            data_inicio=datetime.datetime(2026, 1, 1),
            data_fim=datetime.datetime(2026, 1, 31),
        ).save()

        assert VagaSerializer(vaga).data['status'] == 'Expirada'
