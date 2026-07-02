from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework_mongoengine.fields import ReferenceField
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Vaga, Candidatura, Perfil


class VagaSerializer(DocumentSerializer):
    class Meta:
        model = Vaga
        fields = '__all__'
        read_only_fields = ['empregador_id']


class CandidaturaSerializer(DocumentSerializer):
    vaga = ReferenceField(queryset=Vaga.objects.all())

    class Meta:
        model = Candidatura
        fields = '__all__'
        read_only_fields = ['candidato_id']


class CadastroSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    tipo = serializers.ChoiceField(choices=['empregador', 'candidato'])
    nome_empresa = serializers.CharField(required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Esse nome de usuário já existe.')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        Perfil.objects.create(
            user=user,
            tipo=validated_data['tipo'],
            nome_empresa=validated_data.get('nome_empresa', '')
        )
        return user