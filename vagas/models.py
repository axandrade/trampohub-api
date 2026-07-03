from mongoengine import Document, StringField, DecimalField, DateTimeField, ReferenceField, IntField
import datetime

from django.contrib.auth.models import User, Group
from django.db import models as django_models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Vaga(Document):
    titulo = StringField(required=True, max_length=200)
    descricao = StringField(required=True)
    empresa = StringField(required=True)
    localizacao = StringField()
    salario = DecimalField()
    tipo_contrato = StringField(choices=['CLT', 'PJ', 'Freelance', 'Estágio'])
    modalidade = StringField(choices=['Presencial', 'Remoto', 'Híbrido'])
    empregador_id = IntField(required=True)  # vai referenciar o User do Django (SQLite)
    data_inicio = DateTimeField()  # a partir de quando a vaga aceita candidaturas
    data_fim = DateTimeField()  # a partir dessa data a vaga fica expirada
    criado_em = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'vagas'
    }


class Candidatura(Document):
    vaga = ReferenceField(Vaga, required=True)
    candidato_id = IntField(required=True)  # referencia o User do Django (SQLite)
    status = StringField(
        choices=['Pendente', 'Em analise', 'Aprovado', 'Rejeitado'],
        default='Pendente'
    )
    mensagem = StringField()  # carta de apresentação / mensagem opcional do candidato
    data_candidatura = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'candidaturas'
    }


class Perfil(django_models.Model):
    user = django_models.OneToOneField(User, on_delete=django_models.CASCADE)
    tipo = django_models.CharField(
        max_length=20,
        choices=[('empregador', 'Empregador'), ('candidato', 'Candidato')]
    )
    nome_empresa = django_models.CharField(max_length=200, blank=True, null=True)  # só pra empregador
    foto = django_models.ImageField(upload_to='perfis/', blank=True, null=True)  # obrigatória pra candidato

    def __str__(self):
        return f"{self.user.username} ({self.tipo})"


@receiver(post_save, sender=Perfil)
def sincronizar_grupo(sender, instance, created, **kwargs):
    """
    Sempre que um Perfil é salvo, garante que o User
    esteja no Group correto (Empregador ou Candidato).
    """
    nome_grupo = 'Empregador' if instance.tipo == 'empregador' else 'Candidato'
    grupo, _ = Group.objects.get_or_create(name=nome_grupo)
    instance.user.groups.clear()
    instance.user.groups.add(grupo)
