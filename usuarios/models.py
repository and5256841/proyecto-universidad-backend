from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    ROLES = (
        ('docente', 'Docente Epidemiólogo'),
        ('coord_programa', 'Coordinador de Programa'),
        ('coord_grupo', 'Coordinador de Grupo de Investigación'),
        ('master', 'Master Manager'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='docente')