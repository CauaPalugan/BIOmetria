from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cargo = models.CharField(max_length=50, choices=[
        ('estagiario', 'Estagiário'),
        ('analista', 'Analista'),
        ('coordenador', 'Coordenador')
    ])
    dados_biometricos = models.BinaryField(blank=True, null=True)

    def __str__(self):
        return self.usuario.username