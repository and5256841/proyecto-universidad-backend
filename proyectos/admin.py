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

class ProyectoAdmin(admin.ModelAdmin):
    search_fields = ['titulo', 'consecutivo']
    list_display = ('consecutivo', 'titulo', 'epidemiologo', 'fecha_inicio', 'activo')
    list_filter = ('activo', 'grupos_investigacion', 'foco_estrategico')
    filter_horizontal = (
        'grupos_investigacion', 
        'programas_postgrado', 
        'programas_pregrado',
        'asesores', 
        'jurados'
    )

admin.site.register(Proyecto, ProyectoAdmin)
admin.site.register(GrupoInvestigacion)
admin.site.register(FocoEstrategico)
admin.site.register(ProgramaAcademico)
admin.site.register(Investigador)
admin.site.register(Producto)
admin.site.register(Avance)