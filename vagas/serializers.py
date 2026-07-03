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


class PerfilSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Perfil
        fields = ['tipo', 'nome_empresa', 'foto', 'username', 'email']


class CadastroSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    tipo = serializers.ChoiceField(choices=['empregador', 'candidato'])
    nome_empresa = serializers.CharField(required=False, allow_blank=True)
    foto = serializers.ImageField(required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Esse nome de usuário já existe.')
        return value

    def validate(self, attrs):
        if attrs.get('tipo') == 'candidato':
            if not attrs.get('foto'):
                raise serializers.ValidationError({'foto': 'A foto é obrigatória para candidatos.'})
            if not attrs.get('email'):
                raise serializers.ValidationError({'email': 'O e-mail é obrigatório para candidatos.'})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        Perfil.objects.create(
            user=user,
            tipo=validated_data['tipo'],
            nome_empresa=validated_data.get('nome_empresa', ''),
            foto=validated_data.get('foto')
        )
        return user


class EditarPerfilSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False, allow_blank=True)
    nome_empresa = serializers.CharField(required=False, allow_blank=True)
    foto = serializers.ImageField(required=False, allow_null=True)
    senha_atual = serializers.CharField(required=False, write_only=True, allow_blank=True)
    nova_senha = serializers.CharField(required=False, write_only=True, min_length=6, allow_blank=True)

    def validate_username(self, value):
        user = self.context['user']
        if User.objects.exclude(id=user.id).filter(username=value).exists():
            raise serializers.ValidationError('Esse nome de usuário já existe.')
        return value

    def validate_email(self, value):
        user = self.context['user']
        if user.perfil.tipo == 'candidato' and not value:
            raise serializers.ValidationError('O e-mail é obrigatório para candidatos.')
        return value

    def validate(self, attrs):
        user = self.context['user']
        if attrs.get('nova_senha'):
            senha_atual = attrs.get('senha_atual')
            if not senha_atual:
                raise serializers.ValidationError({'senha_atual': 'Informe sua senha atual para trocar a senha.'})
            if not user.check_password(senha_atual):
                raise serializers.ValidationError({'senha_atual': 'Senha atual incorreta.'})
        return attrs

    def save(self):
        user = self.context['user']
        perfil = user.perfil
        data = self.validated_data

        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if data.get('nova_senha'):
            user.set_password(data['nova_senha'])
        user.save()

        if 'nome_empresa' in data:
            perfil.nome_empresa = data['nome_empresa']
        if 'foto' in data:
            perfil.foto = data['foto']
        perfil.save()

        return perfil