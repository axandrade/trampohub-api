import datetime

import factory

from django.contrib.auth.models import User

from vagas.models import Perfil, Vaga, agora_utc


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f'usuario{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or 'senha123')
        if create:
            self.save()


class PerfilFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Perfil

    user = factory.SubFactory(UserFactory)
    tipo = 'candidato'
    nome_empresa = ''


def criar_empregador(**kwargs):
    senha = kwargs.pop('password', 'senha123')
    nome_empresa = kwargs.pop('nome_empresa', 'ACME Ltda')
    user = UserFactory(password=senha, **kwargs)
    PerfilFactory(user=user, tipo='empregador', nome_empresa=nome_empresa)
    return user


def criar_candidato(**kwargs):
    senha = kwargs.pop('password', 'senha123')
    user = UserFactory(password=senha, **kwargs)
    PerfilFactory(user=user, tipo='candidato')
    return user


def criar_vaga(**kwargs):
    agora = agora_utc()
    defaults = dict(
        titulo='Dev Backend',
        descricao='Descricao da vaga',
        empresa='ACME',
        empregador_id=1,
        tipo_contrato='CLT',
        modalidade='Remoto',
        data_inicio=agora,
        data_fim=agora + datetime.timedelta(days=30),
    )
    defaults.update(kwargs)
    return Vaga(**defaults).save()
