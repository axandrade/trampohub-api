from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework_mongoengine.fields import ReferenceField
from .models import Vaga, Candidatura


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