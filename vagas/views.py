from rest_framework import status
from rest_framework_mongoengine import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from .models import Vaga, Candidatura
from .serializers import VagaSerializer, CandidaturaSerializer, CadastroSerializer, PerfilSerializer, EditarPerfilSerializer
from .permissions import IsEmpregador, IsCandidato


class CadastroView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CadastroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Usuário criado com sucesso.'},
            status=status.HTTP_201_CREATED
        )


class PerfilMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = PerfilSerializer(request.user.perfil)
        return Response(serializer.data)

    def patch(self, request):
        serializer = EditarPerfilSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        perfil = serializer.save()
        return Response(PerfilSerializer(perfil).data)


class VagaViewSet(viewsets.ModelViewSet):
    queryset = Vaga.objects.all()
    serializer_class = VagaSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsEmpregador()]
        return [AllowAny()]

    def get_queryset(self):
        queryset = Vaga.objects.all()
        user = self.request.user

        if user.is_authenticated and user.groups.filter(name='Empregador').exists():
            queryset = queryset.filter(empregador_id=user.id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(empregador_id=self.request.user.id)


class CandidaturaViewSet(viewsets.ModelViewSet):
    queryset = Candidatura.objects.all()
    serializer_class = CandidaturaSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsCandidato()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Candidatura.objects.all()
        user = self.request.user

        if user.groups.filter(name='Candidato').exists():
            queryset = queryset.filter(candidato_id=user.id)
        elif user.groups.filter(name='Empregador').exists():
            vagas = Vaga.objects.filter(empregador_id=user.id)
            queryset = queryset.filter(vaga__in=vagas)

        return queryset

    def perform_create(self, serializer):
        vaga = serializer.validated_data.get('vaga')
        candidato_id = self.request.user.id

        ja_existe = Candidatura.objects(vaga=vaga, candidato_id=candidato_id).first()
        if ja_existe:
            raise ValidationError('Você já se candidatou a essa vaga.')

        serializer.save(candidato_id=candidato_id)