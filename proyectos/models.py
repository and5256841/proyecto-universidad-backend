# --- CÓDIGO FINAL Y COMPLETO PARA proyectos/models.py ---
# Por favor, reemplaza todo el contenido de tu archivo con este código.

import uuid
from django.db import models
from django.conf import settings

# --- MODELOS DE APOYO (Para los menús desplegables y relaciones) ---

class GrupoInvestigacion(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return self.nombre

class FocoEstrategico(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return self.nombre

class ProgramaAcademico(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return self.nombre

class Investigador(models.Model):
    nombre_completo = models.CharField(max_length=150)
    email = models.EmailField(unique=True, blank=True, null=True)
    rol_externo = models.CharField(max_length=100, help_text="Ej: Asesor Metodológico, Jurado Evaluador")
    def __str__(self):
        return self.nombre_completo

# --- EL MODELO PRINCIPAL: PROYECTO (Ahora sí, la versión correcta) ---

class Proyecto(models.Model):
    consecutivo = models.IntegerField("N° Consecutivo", unique=True, null=True, blank=True)
    titulo = models.CharField("Título", max_length=500)
    pais = models.CharField("País", max_length=100, default='Colombia')
    es_proyecto_estrategico = models.BooleanField("¿Es Proyecto Estratégico?", default=False)
    grupos_investigacion = models.ManyToManyField(GrupoInvestigacion, blank=True)
    otra_afiliacion = models.CharField("Otra afiliación (Área o Servicio)", max_length=200, blank=True, null=True)
    foco_estrategico = models.ForeignKey(FocoEstrategico, on_delete=models.SET_NULL, null=True, blank=True)
    programas_postgrado = models.ManyToManyField(ProgramaAcademico, related_name="proyectos_postgrado", blank=True)
    programas_pregrado = models.ManyToManyField(ProgramaAcademico, related_name="proyectos_pregrado", blank=True)
    epidemiologo = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Epidemiólogo", on_delete=models.SET_NULL, null=True, blank=True, related_name="proyectos_epidemiologo")
    investigador_principal = models.CharField("Investigador Principal", max_length=200, blank=True, null=True)
    participacion_otra_entidad = models.BooleanField("¿Participa otra entidad?", default=False)
    presentado_a_convocatoria = models.BooleanField("¿Presentado a Convocatoria?", default=False)
    financiado_por_convocatoria = models.BooleanField("¿Financiado por Convocatoria?", default=False)
    duracion_meses = models.IntegerField("Duración del Proyecto (meses)", null=True, blank=True)
    fecha_inicio = models.DateField("Fecha de Inicio", null=True, blank=True)
    fecha_fin = models.DateField("Fecha de Fin", null=True, blank=True)
    activo = models.BooleanField("¿Activo?", default=True)
    progreso_construccion = models.IntegerField("Progreso Construcción (%)", default=0)
    progreso_recoleccion = models.IntegerField("Progreso Recolección de Datos (%)", default=0)
    progreso_analisis = models.IntegerField("Progreso Análisis de Datos (%)", default=0)
    progreso_documento_final = models.IntegerField("Progreso Documento Final (%)", default=0)
    progreso_sometimiento = models.IntegerField("Progreso Sometimiento (%)", default=0)
    progreso_publicacion = models.IntegerField("Progreso Publicación (%)", default=0)
    aprobacion_cei = models.BooleanField("Aprobación CEI UNISANITAS", default=False)
    consecutivo_ceifus = models.CharField("Consecutivo CEIFUS", max_length=50, blank=True, null=True)
    fecha_ceifus = models.DateField("Fecha CEIFUS", null=True, blank=True)
    asesores = models.ManyToManyField(Investigador, related_name='proyectos_asesorados', blank=True)
    jurados = models.ManyToManyField(Investigador, related_name='proyectos_evaluados', blank=True)

    def __str__(self):
        return self.titulo

class Producto(models.Model):
    proyecto_padre = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='productos')
    TIPOS_MINCIENCIAS = [('nuevo_conocimiento', 'Generación de Nuevo Conocimiento'), ('desarrollo_innovacion', 'Desarrollo Tecnológico e Innovación'), ('apropiacion_social', 'Apropiación Social del Conocimiento'), ('formacion_rrhh', 'Formación de Recurso Humano')]
    ESTADOS_PRODUCTO = [('desarrollo', 'En Desarrollo'), ('sometido', 'Sometido a Evaluación'), ('publicado', 'Publicado/Finalizado'), ('reconocido', 'Reconocido')]
    titulo_producto = models.CharField(max_length=255)
    tipo_principal = models.CharField(max_length=50, choices=TIPOS_MINCIENCIAS)
    subtipo_especifico = models.CharField(max_length=100, help_text="Ej: Artículo A1, Software, Ponencia, Tesis de Grado")
    estado = models.CharField(max_length=20, choices=ESTADOS_PRODUCTO, default='desarrollo')
    referencia = models.TextField(blank=True, help_text="DOI, ISBN, URL, nombre de la revista, etc.")
    reconocimiento_universidad = models.BooleanField(default=False)
    def __str__(self):
        return self.titulo_producto

class Avance(models.Model):
    TIPOS_AVANCE = [('inicio', 'Inicio Formal del Proyecto'), ('asignacion_asesor', 'Asignación de Asesor'), ('sometimiento_comite', 'Sometimiento a Comité de Ética'), ('aprobacion_comite', 'Aprobación de Comité de Ética'), ('entrega_parcial', 'Entrega Parcial'), ('correcciones', 'Recepción de Correcciones'), ('presentacion_evento', 'Presentación en Evento'), ('sometimiento_publicacion', 'Sometimiento de Artículo/Producto'), ('finalizacion', 'Finalización/Cierre de Proyecto')]
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='avances')
    tipo_avance = models.CharField(max_length=50, choices=TIPOS_AVANCE)
    fecha_avance = models.DateField()
    descripcion = models.TextField(help_text="Detalles del avance, observaciones, etc.")
    autor_del_avance = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, help_text="Usuario que registra el avance.")
    class Meta:
        ordering = ['-fecha_avance']
    def __str__(self):
        return f"Avance en '{self.proyecto.titulo if self.proyecto else 'N/A'}' el {self.fecha_avance.strftime('%Y-%m-%d')}"
    