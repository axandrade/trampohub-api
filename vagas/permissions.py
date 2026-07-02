from rest_framework.permissions import BasePermission


class IsEmpregador(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Empregador').exists()


class IsCandidato(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Candidato').exists()