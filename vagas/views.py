from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import Vaga, Candidatura
from .serializers import VagaSerializer, CandidaturaSerializer
from .permissions import IsEmpregador, IsCandidato


class VagaViewSet(viewsets.ModelViewSet):
    queryset = Vaga.objects.all()
    serializer_class = VagaSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsEmpregador()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(empregador_id=self.request.user.id)


class CandidaturaViewSet(viewsets.ModelViewSet):
    queryset = Candidatura.objects.all()
    serializer_class = CandidaturaSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsCandidato()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        vaga = serializer.validated_data.get('vaga')
        candidato_id = self.request.user.id

        ja_existe = Candidatura.objects(vaga=vaga, candidato_id=candidato_id).first()
        if ja_existe:
            raise ValidationError('Você já se candidatou a essa vaga.')

        serializer.save(candidato_id=candidato_id)