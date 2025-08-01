import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from proyectos.models import (
    Proyecto, GrupoInvestigacion, FocoEstrategico, 
    ProgramaAcademico, Investigador
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Importar proyectos desde archivo CSV'

    def handle(self, *args, **options):
        csv_file_path = 'proyectos_datos.csv'
        
        if not os.path.exists(csv_file_path):
            self.stdout.write(
                self.style.ERROR(f'Archivo {csv_file_path} no encontrado')
            )
            return

        proyectos_creados = 0
        proyectos_actualizados = 0
        errores = 0

        self.stdout.write('Iniciando importación de proyectos...')

        # Probar diferentes codificaciones
        encodings = ['utf-8-sig', 'latin-1', 'cp1252', 'utf-8']
        file_data = None
        encoding_used = None
        
        for encoding in encodings:
            try:
                with open(csv_file_path, 'r', encoding=encoding) as file:
                    reader = csv.DictReader(file, delimiter=';')  # Separador punto y coma
                    # Probar leer todas las filas
                    file_data = list(reader)
                    encoding_used = encoding
                    self.stdout.write(f'Archivo abierto correctamente con codificación: {encoding}')
                    break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if file_data is None:
            self.stdout.write(
                self.style.ERROR('No se pudo abrir el archivo con ninguna codificación conocida')
            )
            return

        total_rows = len(file_data)
        self.stdout.write(f'Se encontraron {total_rows} filas para procesar')

        for row_num, row in enumerate(file_data, start=2):
            try:
                # Función para obtener valor de columna con nombre flexible
                def get_column_value(row_data, *possible_names):
                    for name in possible_names:
                        # Buscar nombre exacto
                        if name in row_data:
                            return row_data[name]
                        # Buscar nombre con variaciones de espacios/saltos de línea
                        for key in row_data.keys():
                            clean_key = key.strip().replace('\n', ' ').replace('  ', ' ')
                            if clean_key == name.strip():
                                return row_data[key]
                    return ''

                # Limpiar datos usando la función flexible
                titulo = get_column_value(row, 'Título').strip()
                if not titulo:
                    self.stdout.write(f'Fila {row_num}: Título vacío, saltando...')
                    continue

                # Crear o obtener objetos relacionados
                grupo1_nombre = get_column_value(row, 'Grupo de Investigación N° 1').strip()
                grupo2_nombre = get_column_value(row, 'Grupo de Investigación N° 2').strip()
                
                grupos = []
                if grupo1_nombre and grupo1_nombre.lower() != 'no aplica':
                    grupo1, _ = GrupoInvestigacion.objects.get_or_create(
                        nombre=grupo1_nombre
                    )
                    grupos.append(grupo1)
                
                if grupo2_nombre and grupo2_nombre.lower() != 'no aplica':
                    grupo2, _ = GrupoInvestigacion.objects.get_or_create(
                        nombre=grupo2_nombre
                    )
                    grupos.append(grupo2)

                # Foco estratégico
                foco_nombre = get_column_value(row, 'Foco Estratégico').strip()
                foco_estrategico = None
                if foco_nombre:
                    foco_estrategico, _ = FocoEstrategico.objects.get_or_create(
                        nombre=foco_nombre
                    )

                # Programas académicos
                programa_postgrado_nombre = get_column_value(row, 'Programa Postgrado Unisanitas').strip()
                programa_pregrado_nombre = get_column_value(row, 'Programa Pregrado Unisanitas').strip()
                
                programas_postgrado = []
                programas_pregrado = []
                
                if programa_postgrado_nombre and programa_postgrado_nombre.upper() != 'NO APLICA':
                    prog_post, _ = ProgramaAcademico.objects.get_or_create(
                        nombre=programa_postgrado_nombre
                    )
                    programas_postgrado.append(prog_post)
                
                if programa_pregrado_nombre and programa_pregrado_nombre.upper() != 'NO APLICA':
                    prog_pre, _ = ProgramaAcademico.objects.get_or_create(
                        nombre=programa_pregrado_nombre
                    )
                    programas_pregrado.append(prog_pre)

                # Epidemiólogo (usuario)
                epidemiologo_nombre = get_column_value(row, 'Epidemiólogo').strip()
                epidemiologo = None
                if epidemiologo_nombre:
                    # Buscar usuario existente o crearlo
                    username = epidemiologo_nombre.lower().replace(' ', '_').replace('.', '_')
                    epidemiologo, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'first_name': epidemiologo_nombre.split()[0] if epidemiologo_nombre.split() else '',
                            'last_name': ' '.join(epidemiologo_nombre.split()[1:]) if len(epidemiologo_nombre.split()) > 1 else '',
                            'email': get_column_value(row, 'Email').strip() or f"{username}@funisanitas.edu.co"
                        }
                    )

                # Convertir valores booleanos
                def str_to_bool(val):
                    if not val or val.strip().lower() in ['', 'no', 'false', '0']:
                        return False
                    return val.strip().lower() in ['sí', 'si', 'yes', 'true', '1']

                # Convertir fechas formato "ene-21" o "MM/AA"
                def parse_date(date_str):
                    if not date_str or date_str.strip() == '':
                        return None
                    try:
                        date_clean = date_str.strip()
                        
                        # Formato "ene-21"
                        if '-' in date_clean:
                            month_str, year_str = date_clean.split('-')
                            months = {
                                'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
                                'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12
                            }
                            month = months.get(month_str.lower(), 1)
                            year = int(f"20{year_str}")
                            return datetime(year, month, 1).date()
                        
                        # Formato "MM/AA"
                        elif '/' in date_clean:
                            month, year = date_clean.split('/')
                            return datetime(int(f"20{year}"), int(month), 1).date()
                            
                    except Exception as e:
                        return None
                    return None

                # Convertir porcentajes
                def parse_percentage(val):
                    if not val or val.strip() == '':
                        return 0
                    try:
                        # Eliminar % si existe y convertir
                        clean_val = val.strip().replace('%', '')
                        return int(float(clean_val))
                    except:
                        return 0

                # Crear o actualizar proyecto
                consecutivo_str = get_column_value(row, 'N° Consecutivo').strip()
                consecutivo = int(consecutivo_str) if consecutivo_str.isdigit() else None

                # Obtener duración del proyecto
                duracion_str = get_column_value(row, 'Duración del Proyecto (meses)', 'Duración del Proyecto\n(meses)').strip()
                duracion_meses = int(duracion_str) if duracion_str.isdigit() else None

                proyecto_data = {
                    'titulo': titulo,
                    'pais': get_column_value(row, 'Pais').strip() or 'Colombia',
                    'es_proyecto_estrategico': str_to_bool(get_column_value(row, 'Proyecto Estratégico')),
                    'otra_afiliacion': get_column_value(row, 'Si no hay afiliación a Grupo, Área o servicio al que pertenece').strip() or None,
                    'foco_estrategico': foco_estrategico,
                    'epidemiologo': epidemiologo,
                    'investigador_principal': get_column_value(row, 'Investigador principal').strip() or None,
                    'participacion_otra_entidad': str_to_bool(get_column_value(row, 'Participación de alguna otra Entidad')),
                    'presentado_a_convocatoria': str_to_bool(get_column_value(row, 'Presentado a Convocatoria')),
                    'financiado_por_convocatoria': str_to_bool(get_column_value(row, 'Proyecto Financiado por Convocatoria')),
                    'duracion_meses': duracion_meses,
                    'fecha_inicio': parse_date(get_column_value(row, 'MM/AA Inicio')),
                    'fecha_fin': parse_date(get_column_value(row, 'MM/AA Fin', 'MM/AA \nFin')),
                    'activo': str_to_bool(get_column_value(row, '¿Activo?')),
                    'progreso_construccion': parse_percentage(get_column_value(row, 'En Construcción')),
                    'progreso_recoleccion': parse_percentage(get_column_value(row, 'Recolección de Datos', 'Recolección de Datos ')),
                    'progreso_analisis': parse_percentage(get_column_value(row, 'Analisis de Datos', 'Analisis de Datos ')),
                    'progreso_documento_final': parse_percentage(get_column_value(row, 'Documento Final', 'Documento Final ')),
                    'progreso_sometimiento': parse_percentage(get_column_value(row, 'Sometimiento')),
                    'progreso_publicacion': parse_percentage(get_column_value(row, 'Publicación', 'Publicación ')),
                    'aprobacion_cei': str_to_bool(get_column_value(row, 'Aprobación CEI UNISANITAS')),
                    'consecutivo_ceifus': get_column_value(row, 'Consecutivo CEIFUS').strip() or None,
                    'fecha_ceifus': parse_date(get_column_value(row, 'Fecha CEIFUS')),
                }

                # Buscar proyecto existente por consecutivo
                proyecto = None
                if consecutivo:
                    try:
                        proyecto = Proyecto.objects.get(consecutivo=consecutivo)
                        # Actualizar proyecto existente
                        for field, value in proyecto_data.items():
                            setattr(proyecto, field, value)
                        proyecto.save()
                        proyectos_actualizados += 1
                    except Proyecto.DoesNotExist:
                        # Crear nuevo proyecto
                        proyecto_data['consecutivo'] = consecutivo
                        proyecto = Proyecto.objects.create(**proyecto_data)
                        proyectos_creados += 1
                else:
                    # Sin consecutivo, crear nuevo
                    proyecto = Proyecto.objects.create(**proyecto_data)
                    proyectos_creados += 1

                # Asignar relaciones ManyToMany
                if grupos:
                    proyecto.grupos_investigacion.set(grupos)
                if programas_postgrado:
                    proyecto.programas_postgrado.set(programas_postgrado)
                if programas_pregrado:
                    proyecto.programas_pregrado.set(programas_pregrado)

                if (row_num - 1) % 50 == 0:
                    self.stdout.write(f'Procesadas {row_num - 1} filas...')

            except Exception as e:
                errores += 1
                self.stdout.write(
                    self.style.ERROR(f'Error en fila {row_num}: {str(e)}')
                )
                continue

        self.stdout.write(
            self.style.SUCCESS(
                f'\n¡Importación completada!\n'
                f'Proyectos creados: {proyectos_creados}\n'
                f'Proyectos actualizados: {proyectos_actualizados}\n'
                f'Errores: {errores}\n'
                f'Total procesado: {proyectos_creados + proyectos_actualizados}'
            )
        )