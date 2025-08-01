from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg, Q
from proyectos.models import Proyecto, GrupoInvestigacion, FocoEstrategico
from django.contrib.auth import get_user_model
import json
from datetime import datetime

User = get_user_model()

@staff_member_required
def dashboard_view(request):
    # Estadísticas generales
    total_proyectos = Proyecto.objects.count()
    proyectos_activos = Proyecto.objects.filter(activo=True).count()
    proyectos_inactivos = total_proyectos - proyectos_activos
    
    # Progreso promedio
    avg_construccion = Proyecto.objects.aggregate(avg=Avg('progreso_construccion'))['avg'] or 0
    avg_recoleccion = Proyecto.objects.aggregate(avg=Avg('progreso_recoleccion'))['avg'] or 0
    avg_analisis = Proyecto.objects.aggregate(avg=Avg('progreso_analisis'))['avg'] or 0
    avg_documento = Proyecto.objects.aggregate(avg=Avg('progreso_documento_final'))['avg'] or 0
    avg_publicacion = Proyecto.objects.aggregate(avg=Avg('progreso_publicacion'))['avg'] or 0
    
    # Proyectos por grupo de investigación (Top 10)
    grupos_stats = Proyecto.objects.values('grupos_investigacion__nombre')\
        .annotate(count=Count('id'))\
        .filter(grupos_investigacion__nombre__isnull=False)\
        .order_by('-count')[:10]
    
    # Proyectos por foco estratégico
    focos_stats = Proyecto.objects.values('foco_estrategico__nombre')\
        .annotate(count=Count('id'))\
        .filter(foco_estrategico__nombre__isnull=False)\
        .order_by('-count')
    
    # Proyectos por año de inicio
    proyectos_por_ano = {}
    for proyecto in Proyecto.objects.filter(fecha_inicio__isnull=False):
        ano = proyecto.fecha_inicio.year
        proyectos_por_ano[ano] = proyectos_por_ano.get(ano, 0) + 1
    
    # Proyectos por estado de progreso (categorizados)
    proyectos_iniciando = Proyecto.objects.filter(
        progreso_construccion__lte=25
    ).count()
    
    proyectos_desarrollo = Proyecto.objects.filter(
        progreso_construccion__gt=25,
        progreso_analisis__lte=50
    ).count()
    
    proyectos_finalizando = Proyecto.objects.filter(
        progreso_analisis__gt=50,
        progreso_publicacion__lt=100
    ).count()
    
    proyectos_completados = Proyecto.objects.filter(
        progreso_publicacion=100
    ).count()
    
    # Proyectos estratégicos vs normales
    proyectos_estrategicos = Proyecto.objects.filter(es_proyecto_estrategico=True).count()
    proyectos_normales = total_proyectos - proyectos_estrategicos
    
    # Preparar datos para gráficos (JSON)
    grupos_nombres = [item['grupos_investigacion__nombre'] for item in grupos_stats if item['grupos_investigacion__nombre']]
    grupos_cantidades = [item['count'] for item in grupos_stats if item['grupos_investigacion__nombre']]
    
    focos_nombres = [item['foco_estrategico__nombre'] for item in focos_stats if item['foco_estrategico__nombre']]
    focos_cantidades = [item['count'] for item in focos_stats if item['foco_estrategico__nombre']]
    
    anos_ordenados = sorted(proyectos_por_ano.keys()) if proyectos_por_ano else []
    cantidades_por_ano = [proyectos_por_ano[ano] for ano in anos_ordenados]
    
    context = {
        # Estadísticas generales
        'total_proyectos': total_proyectos,
        'proyectos_activos': proyectos_activos,
        'proyectos_inactivos': proyectos_inactivos,
        'proyectos_estrategicos': proyectos_estrategicos,
        'proyectos_normales': proyectos_normales,
        
        # Promedios de progreso
        'avg_construccion': round(avg_construccion, 1),
        'avg_recoleccion': round(avg_recoleccion, 1),
        'avg_analisis': round(avg_analisis, 1),
        'avg_documento': round(avg_documento, 1),
        'avg_publicacion': round(avg_publicacion, 1),
        
        # Estados de proyectos
        'proyectos_iniciando': proyectos_iniciando,
        'proyectos_desarrollo': proyectos_desarrollo,
        'proyectos_finalizando': proyectos_finalizando,
        'proyectos_completados': proyectos_completados,
        
        # Datos para gráficos (JSON)
        'grupos_nombres_json': json.dumps(grupos_nombres),
        'grupos_cantidades_json': json.dumps(grupos_cantidades),
        'focos_nombres_json': json.dumps(focos_nombres),
        'focos_cantidades_json': json.dumps(focos_cantidades),
        'anos_json': json.dumps(anos_ordenados),
        'cantidades_por_ano_json': json.dumps(cantidades_por_ano),
        
        # Listas para mostrar en tablas
        'grupos_stats': grupos_stats,
        'focos_stats': focos_stats,
    }
    
    return render(request, 'admin/dashboard.html', context)