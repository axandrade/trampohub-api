from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from vagas.views import CadastroView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('vagas.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', obtain_auth_token),
    path('api/cadastro/', CadastroView.as_view()),
]