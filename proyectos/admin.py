from django.contrib import admin
from .models import (
    Proyecto, 
    GrupoInvestigacion, 
    FocoEstrategico, 
    ProgramaAcademico, 
    Investigador, 
    Producto, 
    Avance
)

# Configuración simple para evitar errores
admin.site.register(Proyecto)
admin.site.register(GrupoInvestigacion)
admin.site.register(FocoEstrategico)
admin.site.register(ProgramaAcademico)
admin.site.register(Investigador)
admin.site.register(Producto)
admin.site.register(Avance)