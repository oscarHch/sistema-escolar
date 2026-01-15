from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import json
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'colegio_secreto_2024'

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
DB_HOST = "localhost"
DB_NAME = "gestion_escolar"
DB_USER = "postgres"
DB_PASS = "28julioOscar"
DB_PORT = "5432"

# --- CONFIGURACIÓN DE ARCHIVOS ---
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# Crear carpeta de uploads si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def obtener_conexion():
    """Función auxiliar para conectarse a PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Error conectando a la BD: {e}")
        return None

def archivo_permitido(filename):
    """Verifica si la extensión del archivo es válida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cargar_noticias():
    try:
        with open('noticias.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            noticias = sorted(data['noticias'], key=lambda x: x['fecha'], reverse=True)
            return noticias
    except FileNotFoundError:
        return []

# --- RUTAS ---
@app.route('/')
@app.route('/inicio')
def inicio():
    noticias = cargar_noticias()[:3]
    return render_template('inicio.html', noticias=noticias)

@app.route('/test_db')
def test_db():
    """Verifica si Flask puede hablar con PostgreSQL"""
    conn = obtener_conexion()
    if conn:
        cur = conn.cursor()
        cur.execute('SELECT version();')
        db_version = cur.fetchone()
        cur.close()
        conn.close()
        return f"<h1>¡Conexión Exitosa!</h1><p>Estás conectado a: {db_version[0]}</p>"
    else:
        return "<h1>Error de Conexión</h1><p>Revisa la terminal de VS Code para ver el error.</p>"

@app.route('/niveles')
def niveles():
    return render_template('niveles.html')

@app.route('/servicios')
def servicios():
    return render_template('servicios.html')

@app.route('/docentes')
def docentes():
    return render_template('docentes.html')

@app.route('/documentos')
def documentos():
    return render_template('documentos.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        conn = None
        try:
            # ===== PASO 1: RECIBIR DATOS DEL FORMULARIO =====
            # Datos del Apoderado
            apoderado_dni = request.form.get('apoderado_dni').strip().upper()
            apoderado_nombres = request.form.get('apoderado_nombres').strip().upper()
            apoderado_apellido_paterno = request.form.get('apoderado_apellido_paterno').strip().upper()
            apoderado_apellido_materno = request.form.get('apoderado_apellido_materno').strip().upper()
            apoderado_telefono = request.form.get('apoderado_telefono').strip()
            apoderado_correo = request.form.get('apoderado_correo').strip().lower()
            apoderado_direccion = request.form.get('apoderado_direccion').strip().upper()
            apoderado_distrito = request.form.get('apoderado_distrito').strip().upper()
            
            # Datos del Alumno
            alumno_dni = request.form.get('alumno_dni').strip().upper()
            alumno_nombres = request.form.get('alumno_nombres').strip().upper()
            alumno_apellido_paterno = request.form.get('alumno_apellido_paterno').strip().upper()
            alumno_apellido_materno = request.form.get('alumno_apellido_materno').strip().upper()
            alumno_fecha_nacimiento = request.form.get('alumno_fecha_nacimiento')
            alumno_sexo = request.form.get('alumno_sexo')
            alumno_direccion = request.form.get('alumno_direccion').strip().upper()
            alumno_distrito = request.form.get('alumno_distrito').strip().upper()
            alumno_parentesco = request.form.get('alumno_parentesco').strip().upper()
            
            # Discapacidad
            tiene_discapacidad = request.form.get('tiene_discapacidad') == 'on'
            detalle_discapacidad = request.form.get('detalle_discapacidad', '').strip().upper() if tiene_discapacidad else None
            
            # Grado
            grado_nombre = request.form.get('grado')
            
            # Validaciones básicas
            if not apoderado_dni or len(apoderado_dni) != 8:
                flash('El DNI del apoderado debe tener 8 dígitos.', 'error')
                return redirect(url_for('registro'))
            
            if not alumno_dni or len(alumno_dni) != 8:
                flash('El DNI del alumno debe tener 8 dígitos.', 'error')
                return redirect(url_for('registro'))
            
            # ===== PASO 2: PROCESAR ARCHIVOS =====
            archivos_subidos = request.files.getlist('documentos')
            rutas_archivos = []
            
            if not archivos_subidos or archivos_subidos[0].filename == '':
                flash('Debes subir al menos un documento.', 'error')
                return redirect(url_for('registro'))
            
            for archivo in archivos_subidos:
                if archivo and archivo_permitido(archivo.filename):
                    # Verificar tamaño
                    archivo.seek(0, os.SEEK_END)
                    file_length = archivo.tell()
                    if file_length > MAX_FILE_SIZE:
                        flash(f'El archivo {archivo.filename} supera los 5MB.', 'error')
                        return redirect(url_for('registro'))
                    archivo.seek(0)
                    
                    # Generar nombre único
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = secure_filename(archivo.filename)
                    nombre_unico = f"{alumno_dni}_{timestamp}_{filename}"
                    
                    # Guardar archivo
                    ruta_completa = os.path.join(app.config['UPLOAD_FOLDER'], nombre_unico)
                    archivo.save(ruta_completa)
                    
                    # Guardar ruta relativa
                    rutas_archivos.append(f"uploads/{nombre_unico}")
                else:
                    flash(f'El archivo {archivo.filename} no es válido. Solo se permiten PDF, JPG, JPEG, PNG.', 'error')
                    return redirect(url_for('registro'))
            
            # Unir rutas con comas
            ruta_documentos_str = ','.join(rutas_archivos)
            
            # ===== PASO 3: TRANSACCIÓN EN BASE DE DATOS =====
            conn = obtener_conexion()
            if not conn:
                flash('Error de conexión con la base de datos.', 'error')
                return redirect(url_for('registro'))
            
            cur = conn.cursor()
            
            # --- 3.1: INSERTAR APODERADO ---
            try:
                cur.execute("""
                    INSERT INTO apoderado (dni, nombres, apellido_paterno, apellido_materno, 
                                          telefono, correo, direccion, distrito)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_apoderado
                """, (apoderado_dni, apoderado_nombres, apoderado_apellido_paterno, 
                      apoderado_apellido_materno, apoderado_telefono, apoderado_correo,
                      apoderado_direccion, apoderado_distrito))
                
                id_apoderado = cur.fetchone()[0]
                print(f"✓ Apoderado insertado con ID: {id_apoderado}")
                
            except psycopg2.IntegrityError:
                # DNI de apoderado ya existe - Buscar su ID
                conn.rollback()
                cur.execute("SELECT id_apoderado FROM apoderado WHERE dni = %s", (apoderado_dni,))
                resultado = cur.fetchone()
                if resultado:
                    id_apoderado = resultado[0]
                    print(f"✓ Apoderado ya existía con ID: {id_apoderado}")
                else:
                    raise Exception("Error al obtener ID del apoderado existente")
            
            # --- 3.2: INSERTAR ALUMNO ---
            try:
                cur.execute("""
                    INSERT INTO alumno (id_apoderado, dni, nombres, apellido_paterno, apellido_materno,
                                       fecha_nacimiento, sexo, direccion, distrito, parentesco,
                                       tiene_discapacidad, detalle_discapacidad)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_alumno
                """, (id_apoderado, alumno_dni, alumno_nombres, alumno_apellido_paterno,
                      alumno_apellido_materno, alumno_fecha_nacimiento, alumno_sexo,
                      alumno_direccion, alumno_distrito, alumno_parentesco,
                      tiene_discapacidad, detalle_discapacidad))
                
                id_alumno = cur.fetchone()[0]
                print(f"✓ Alumno insertado con ID: {id_alumno}")
                
            except psycopg2.IntegrityError as e:
                conn.rollback()
                flash(f'El DNI del alumno {alumno_dni} ya está registrado en el sistema.', 'error')
                return redirect(url_for('registro'))
            
            # --- 3.3: BUSCAR ID DEL GRADO ---
            cur.execute("SELECT id_grado FROM grado WHERE nombre = %s", (grado_nombre,))
            resultado_grado = cur.fetchone()
            
            if not resultado_grado:
                conn.rollback()
                flash(f'Error: El grado "{grado_nombre}" no existe en el sistema.', 'error')
                return redirect(url_for('registro'))
            
            id_grado = resultado_grado[0]
            print(f"✓ Grado encontrado con ID: {id_grado}")
            
            # --- 3.4: INSERTAR PROCESO_MATRICULA ---
            cur.execute("""
                INSERT INTO proceso_matricula (id_alumno, id_grado, anio_escolar, tipo_proceso,
                                               fecha_registro, estado_documentos, estado_matricula,
                                               condicion_final, seccion, ruta_documentos)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s)
                RETURNING id_proceso
            """, (id_alumno, id_grado, 2026, 'SOLICITUD', 'PENDIENTE', 'PENDIENTE',
                  None, None, ruta_documentos_str))
            
            id_proceso = cur.fetchone()[0]
            print(f"✓ Proceso de matrícula creado con ID: {id_proceso}")
            
            # --- COMMIT DE LA TRANSACCIÓN ---
            conn.commit()
            
            # Mensaje de éxito
            nombre_completo_alumno = f"{alumno_nombres} {alumno_apellido_paterno} {alumno_apellido_materno}"
            flash(f'¡Solicitud registrada exitosamente para {nombre_completo_alumno}! Te contactaremos pronto.', 'success')
            
            # Limpiar formulario redirigiendo
            return redirect(url_for('registro'))
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Error en el proceso: {str(e)}")
            flash(f'Error al procesar la solicitud: {str(e)}', 'error')
            return redirect(url_for('registro'))
            
        finally:
            if conn:
                cur.close()
                conn.close()
    
    # GET request - Mostrar formulario
    return render_template('registro.html')

@app.route('/noticias')
def noticias():
    todas_noticias = cargar_noticias()
    return render_template('noticias.html', noticias=todas_noticias)

if __name__ == '__main__':
    app.run(debug=True, port=8000)