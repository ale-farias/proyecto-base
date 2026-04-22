"""
Backend Flask - Sistema de Gestión de Turnos para Negocios Locales
Proporciona API RESTful para el sistema de reservas
"""
import os
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, get_jwt
)

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or secrets.token_hex(32)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

jwt = JWTManager(app)
CORS(app, supports_credentials=True)

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=["200 per day", "50 per hour"]
)

DB_NAME = "negocio.db"

# ============ FUNCIONES AUXILIARES ============

def get_db_connection():
    """Obtiene conexión a la base de datos"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def dict_from_row(row):
    """Convierte fila SQLite a diccionario"""
    return dict(row) if row else None

def query_to_list(query, params=()):
    """Ejecuta query y retorna lista de diccionarios"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict_from_row(row) for row in rows]

def query_one(query, params=()):
    """Ejecuta query y retorna un resultado"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    row = cursor.fetchone()
    conn.close()
    return dict_from_row(row)

def execute_query(query, params=()):
    """Ejecuta query de modificación"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def get_config():
    """Obtiene toda la configuración como diccionario"""
    rows = query_to_list("SELECT clave, valor FROM configuracion")
    return {row['clave']: row['valor'] for row in rows}

# ============ RUTAS DE AUTENTICACIÓN ============

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """Registrar nuevo usuario"""
    data = request.get_json()

    nombre = data.get('nombre', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    telefono = data.get('telefono', '').strip()

    if not nombre or not email or not password:
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    if len(password) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400

    # Verificar si el email ya existe
    existing = query_one("SELECT id FROM usuarios WHERE email = ?", (email,))
    if existing:
        return jsonify({'error': 'El email ya está registrado'}), 400

    # Hash de contraseña
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Insertar usuario
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO usuarios (nombre, email, password_hash, telefono, rol)
        VALUES (?, ?, ?, ?, 'cliente')
    ''', (nombre, email, password_hash, telefono))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Crear token JWT
    access_token = create_access_token(identity=str(user_id))

    return jsonify({
        'message': 'Usuario registrado correctamente',
        'access_token': access_token,
        'user': {'id': user_id, 'nombre': nombre, 'email': email, 'rol': 'cliente'}
    }), 201

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Iniciar sesión"""
    data = request.get_json()

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email y contraseña son obligatorios'}), 400

    # Buscar usuario
    user = query_one("SELECT * FROM usuarios WHERE email = ?", (email,))
    if not user:
        return jsonify({'error': 'Email o contraseña incorrectos'}), 401

    # Verificar contraseña
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user['password_hash'] != password_hash:
        return jsonify({'error': 'Email o contraseña incorrectos'}), 401

    # Crear token JWT
    access_token = create_access_token(identity=str(user['id']))

    return jsonify({
        'message': 'Login exitoso',
        'access_token': access_token,
        'user': {
            'id': user['id'],
            'nombre': user['nombre'],
            'email': user['email'],
            'rol': user['rol'],
            'telefono': user['telefono']
        }
    })

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Obtener usuario actual"""
    user_id = get_jwt_identity()
    user = query_one("SELECT id, nombre, email, rol, telefono, fecha_registro FROM usuarios WHERE id = ?", (user_id,))
    return jsonify(user)

@app.route('/api/auth/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Actualizar perfil del usuario"""
    user_id = get_jwt_identity()
    data = request.get_json()

    nombre = data.get('nombre', '').strip()
    telefono = data.get('telefono', '').strip()

    if not nombre:
        return jsonify({'error': 'El nombre es obligatorio'}), 400

    execute_query(
        "UPDATE usuarios SET nombre = ?, telefono = ? WHERE id = ?",
        (nombre, telefono, user_id)
    )

    return jsonify({'message': 'Perfil actualizado correctamente'})

# ============ RUTAS DE CONFIGURACIÓN ============

@app.route('/api/config', methods=['GET'])
def get_config_api():
    """Obtener configuración pública del negocio"""
    config = get_config()
    return jsonify(config)

@app.route('/api/admin/config', methods=['PUT'])
@jwt_required()
def update_config():
    """Actualizar configuración (solo admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Solo el administrador puede modificar la configuración'}), 403

    data = request.get_json()

    for clave, valor in data.items():
        execute_query(
            "INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)",
            (clave, str(valor))
        )

    return jsonify({'message': 'Configuración actualizada correctamente'})

# ============ RUTAS DE SERVICIOS ============

@app.route('/api/servicios', methods=['GET'])
def get_servicios():
    """Obtener lista de servicios activos"""
    servicios = query_to_list("SELECT * FROM servicios WHERE activo = 1 ORDER BY nombre")
    return jsonify(servicios)

@app.route('/api/admin/servicios', methods=['GET'])
@jwt_required()
def get_all_servicios():
    """Obtener todos los servicios (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    servicios = query_to_list("SELECT * FROM servicios ORDER BY nombre")
    return jsonify(servicios)

@app.route('/api/admin/servicios', methods=['POST'])
@jwt_required()
def create_servicio():
    """Crear nuevo servicio (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    data = request.get_json()

    nombre = data.get('nombre', '').strip()
    descripcion = data.get('descripcion', '').strip()
    precio = float(data.get('precio', 0))
    duracion = int(data.get('duracion', 30))

    if not nombre or precio <= 0:
        return jsonify({'error': 'Nombre y precio son obligatorios'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO servicios (nombre, descripcion, precio, duracion)
        VALUES (?, ?, ?, ?)
    ''', (nombre, descripcion, precio, duracion))
    servicio_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'message': 'Servicio creado correctamente', 'id': servicio_id}), 201

@app.route('/api/admin/servicios/<int:servicio_id>', methods=['PUT'])
@jwt_required()
def update_servicio(servicio_id):
    """Actualizar servicio (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    data = request.get_json()

    nombre = data.get('nombre', '').strip()
    descripcion = data.get('descripcion', '').strip()
    precio = float(data.get('precio', 0))
    duracion = int(data.get('duracion', 30))
    activo = 1 if data.get('activo', True) else 0

    execute_query('''
        UPDATE servicios SET nombre = ?, descripcion = ?, precio = ?, duracion = ?, activo = ?
        WHERE id = ?
    ''', (nombre, descripcion, precio, duracion, activo, servicio_id))

    return jsonify({'message': 'Servicio actualizado correctamente'})

@app.route('/api/admin/servicios/<int:servicio_id>', methods=['DELETE'])
@jwt_required()
def delete_servicio(servicio_id):
    """Eliminar servicio (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    execute_query("DELETE FROM servicios WHERE id = ?", (servicio_id,))
    return jsonify({'message': 'Servicio eliminado correctamente'})

# ============ RUTAS DE TURNOS ============

@app.route('/api/turnos/disponibles', methods=['GET'])
def get_horarios_disponibles():
    """Obtener horarios disponibles para una fecha"""
    fecha = request.args.get('fecha')
    servicio_id = request.args.get('servicio_id')

    if not fecha or not servicio_id:
        return jsonify({'error': 'Fecha y servicio son obligatorios'}), 400

    # Obtener duración del servicio
    servicio = query_one("SELECT duracion FROM servicios WHERE id = ?", (servicio_id,))
    if not servicio:
        return jsonify({'error': 'Servicio no encontrado'}), 404

    duracion = servicio['duracion']

    # Obtener configuración de horario
    config = get_config()
    hora_inicio = 9  # 9:00 por defecto
    hora_fin = 18    # 18:00 por defecto

    # Generar horarios disponibles
    horarios = []
    hora_actual = hora_inicio

    while hora_actual < hora_fin:
        hora_str = f"{hora_actual:02d}:00"

        # Verificar si hay turno reservado
        turno = query_one(
            "SELECT id FROM turnos WHERE fecha = ? AND hora = ? AND estado != 'cancelado'",
            (fecha, hora_str)
        )

        if not turno:
            horarios.append(hora_str)

        hora_actual += 1

    return jsonify(horarios)

@app.route('/api/turnos', methods=['GET'])
@jwt_required()
def get_mis_turnos():
    """Obtener turnos del usuario actual"""
    user_id = get_jwt_identity()
    turnos = query_to_list('''
        SELECT t.*, s.nombre as servicio_nombre, s.precio, s.duracion
        FROM turnos t
        JOIN servicios s ON t.servicio_id = s.id
        WHERE t.usuario_id = ?
        ORDER BY t.fecha DESC, t.hora DESC
    ''', (user_id,))
    return jsonify(turnos)

@app.route('/api/turnos', methods=['POST'])
@jwt_required()
def crear_turno():
    """Crear nuevo turno"""
    user_id = get_jwt_identity()
    data = request.get_json()

    servicio_id = data.get('servicio_id')
    fecha = data.get('fecha')
    hora = data.get('hora')
    notas = data.get('notas', '')

    if not servicio_id or not fecha or not hora:
        return jsonify({'error': 'Servicio, fecha y hora son obligatorios'}), 400

    # Verificar que el servicio existe
    servicio = query_one("SELECT id FROM servicios WHERE id = ? AND activo = 1", (servicio_id,))
    if not servicio:
        return jsonify({'error': 'Servicio no disponible'}), 400

    # Verificar que el horario está disponible
    existente = query_one(
        "SELECT id FROM turnos WHERE fecha = ? AND hora = ? AND estado != 'cancelado'",
        (fecha, hora)
    )
    if existente:
        return jsonify({'error': 'El horario ya no está disponible'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO turnos (usuario_id, servicio_id, fecha, hora, notas, estado)
        VALUES (?, ?, ?, ?, ?, 'pendiente')
    ''', (user_id, servicio_id, fecha, hora, notas))
    turno_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'message': 'Turno reservado correctamente', 'id': turno_id}), 201

@app.route('/api/turnos/<int:turno_id>', methods=['DELETE'])
@jwt_required()
def cancelar_turno(turno_id):
    """Cancelar turno"""
    user_id = get_jwt_identity()

    # Verificar que el turno pertenece al usuario
    turno = query_one("SELECT * FROM turnos WHERE id = ?", (turno_id,))
    if not turno:
        return jsonify({'error': 'Turno no encontrado'}), 404

    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    # Solo el owner o admin puede cancelar
    if str(turno['usuario_id']) != str(user_id) and user['rol'] != 'admin':
        return jsonify({'error': 'No tienes permiso para cancelar este turno'}), 403

    execute_query(
        "UPDATE turnos SET estado = 'cancelado' WHERE id = ?",
        (turno_id,)
    )

    return jsonify({'message': 'Turno cancelado correctamente'})

# ============ RUTAS DE ADMINISTRACIÓN ============

@app.route('/api/admin/turnos', methods=['GET'])
@jwt_required()
def get_all_turnos():
    """Obtener todos los turnos (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    estado = request.args.get('estado')

    query = '''
        SELECT t.*, s.nombre as servicio_nombre, s.precio, s.duracion,
               u.nombre as cliente_nombre, u.email as cliente_email, u.telefono as cliente_telefono
        FROM turnos t
        JOIN servicios s ON t.servicio_id = s.id
        JOIN usuarios u ON t.usuario_id = u.id
    '''

    params = []
    if estado:
        query += " WHERE t.estado = ?"
        params.append(estado)
    query += " ORDER BY t.fecha DESC, t.hora DESC"

    turnos = query_to_list(query, tuple(params))
    return jsonify(turnos)

@app.route('/api/admin/turnos/<int:turno_id>/estado', methods=['PUT'])
@jwt_required()
def cambiar_estado_turno(turno_id):
    """Cambiar estado del turno (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    data = request.get_json()
    nuevo_estado = data.get('estado')

    if nuevo_estado not in ['pendiente', 'confirmado', 'completado', 'cancelado']:
        return jsonify({'error': 'Estado inválido'}), 400

    execute_query(
        "UPDATE turnos SET estado = ? WHERE id = ?",
        (nuevo_estado, turno_id)
    )

    return jsonify({'message': 'Estado actualizado correctamente'})

@app.route('/api/admin/usuarios', methods=['GET'])
@jwt_required()
def get_all_usuarios():
    """Obtener todos los usuarios (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    usuarios = query_to_list('''
        SELECT id, nombre, email, rol, telefono, fecha_registro,
               (SELECT COUNT(*) FROM turnos WHERE usuario_id = usuarios.id) as total_turnos
        FROM usuarios
        ORDER BY fecha_registro DESC
    ''')
    return jsonify(usuarios)

@app.route('/api/admin/usuarios/<int:usuario_id>', methods=['PUT'])
@jwt_required()
def update_usuario(usuario_id):
    """Actualizar usuario (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    data = request.get_json()

    nombre = data.get('nombre', '').strip()
    rol = data.get('rol', 'cliente')
    telefono = data.get('telefono', '').strip()

    execute_query(
        "UPDATE usuarios SET nombre = ?, rol = ?, telefono = ? WHERE id = ?",
        (nombre, rol, telefono, usuario_id)
    )

    return jsonify({'message': 'Usuario actualizado correctamente'})

@app.route('/api/admin/estadisticas', methods=['GET'])
@jwt_required()
def get_estadisticas():
    """Obtener estadísticas del negocio (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    # Total usuarios
    total_usuarios = query_one("SELECT COUNT(*) as total FROM usuarios WHERE rol = 'cliente'")
    total_usuarios = total_usuarios['total'] if total_usuarios else 0

    # Usuarios nuevos este mes
    usuarios_mes = query_one('''
        SELECT COUNT(*) as total FROM usuarios
        WHERE rol = 'cliente' AND fecha_registro >= date('now', '-30 days')
    ''')
    usuarios_mes = usuarios_mes['total'] if usuarios_mes else 0

    # Total turnos
    total_turnos = query_one("SELECT COUNT(*) as total FROM turnos")
    total_turnos = total_turnos['total'] if total_turnos else 0

    # Turnos de hoy
    turnos_hoy = query_one("SELECT COUNT(*) as total FROM turnos WHERE fecha = date('now') AND estado != 'cancelado'")
    turnos_hoy = turnos_hoy['total'] if turnos_hoy else 0

    # Turnos de esta semana
    turnos_semana = query_one("SELECT COUNT(*) as total FROM turnos WHERE fecha >= date('now', '-7 days') AND estado != 'cancelado'")
    turnos_semana = turnos_semana['total'] if turnos_semana else 0

    # Turnos pendientes
    turnos_pendientes = query_one("SELECT COUNT(*) as total FROM turnos WHERE estado = 'pendiente'")
    turnos_pendientes = turnos_pendientes['total'] if turnos_pendientes else 0

    # Total servicios
    total_servicios = query_one("SELECT COUNT(*) as total FROM servicios WHERE activo = 1")
    total_servicios = total_servicios['total'] if total_servicios else 0

    # Turnos por día (últimos 7 días)
    turnos_por_dia = query_to_list('''
        SELECT fecha, COUNT(*) as total
        FROM turnos
        WHERE fecha >= date('now', '-7 days') AND estado != 'cancelado'
        GROUP BY fecha
        ORDER BY fecha
    ''')

    # Ingresos估算 (turnos completados)
    ingresos = query_one('''
        SELECT SUM(s.precio) as total
        FROM turnos t
        JOIN servicios s ON t.servicio_id = s.id
        WHERE t.estado = 'completado'
    ''')
    ingresos = ingresos['total'] if ingresos and ingresos['total'] else 0

    # Últimos 5 turnos
    ultimos_turnos = query_to_list('''
        SELECT t.*, s.nombre as servicio_nombre, u.nombre as cliente_nombre
        FROM turnos t
        JOIN servicios s ON t.servicio_id = s.id
        JOIN usuarios u ON t.usuario_id = u.id
        ORDER BY t.fecha DESC, t.hora DESC
        LIMIT 5
    ''')

    # Turnos del mes actual
    turnos_mes = query_one("SELECT COUNT(*) as total FROM turnos WHERE fecha >= date('now', '-30 days') AND estado != 'cancelado'")
    turnos_mes = turnos_mes['total'] if turnos_mes else 0

    # Servicios más reservados
    servicios_top = query_to_list('''
        SELECT s.id, s.nombre, COUNT(t.id) as total_reservas
        FROM servicios s
        LEFT JOIN turnos t ON s.id = t.servicio_id AND t.estado != 'cancelado'
        GROUP BY s.id
        ORDER BY total_reservas DESC
        LIMIT 5
    ''')

    return jsonify({
        'total_usuarios': total_usuarios,
        'usuarios_mes': usuarios_mes,
        'total_turnos': total_turnos,
        'turnos_hoy': turnos_hoy,
        'turnos_semana': turnos_semana,
        'turnos_mes': turnos_mes,
        'total_servicios': total_servicios,
        'turnos_pendientes': turnos_pendientes,
        'turnos_por_dia': turnos_por_dia,
        'ingresos': ingresos,
        'ultimos_turnos': ultimos_turnos,
        'servicios_top': servicios_top
    })

# ============ RUTAS DE TESTIMONIOS ============

@app.route('/api/testimonios', methods=['GET'])
def get_testimonios():
    """Obtener testimonios activos"""
    testimonios = query_to_list("SELECT * FROM testimonios WHERE activo = 1 ORDER BY fecha_creacion DESC")
    return jsonify(testimonios)

@app.route('/api/admin/testimonios', methods=['POST'])
@jwt_required()
def create_testimonio():
    """Crear testimonio (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    data = request.get_json()

    nombre = data.get('nombre', '').strip()
    texto = data.get('texto', '').strip()
    calificacion = int(data.get('calificacion', 5))

    if not nombre or not texto:
        return jsonify({'error': 'Nombre y texto son obligatorios'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO testimonios (nombre, texto, calificacion)
        VALUES (?, ?, ?)
    ''', (nombre, texto, calificacion))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Testimonio creado correctamente'}), 201

# ============ RUTAS DE RESEÑAS ============

@app.route('/api/resenas', methods=['GET'])
def get_resenas():
    """Obtener reseñas aprobadas para mostrar"""
    reseñas = query_to_list("""
        SELECT r.*, u.nombre as usuario_nombre
        FROM reseñas r
        JOIN usuarios u ON r.usuario_id = u.id
        WHERE r.aprobado = 1 AND r.activo = 1
        ORDER BY r.fecha_creacion DESC
        LIMIT 5
    """)
    return jsonify(reseñas)

@app.route('/api/resenas', methods=['POST'])
@jwt_required()
def create_resena():
    """Crear nueva reseña (cliente logueado)"""
    user_id = get_jwt_identity()
    data = request.get_json()

    texto = data.get('texto', '').strip()
    calificacion = int(data.get('calificacion', 5))

    if not texto:
        return jsonify({'error': 'El texto de la reseña es obligatorio'}), 400

    if calificacion < 1 or calificacion > 5:
        return jsonify({'error': 'La calificación debe ser entre 1 y 5'}), 400

    # Verificar que no haya deja2do reseña recientemente
    reciente = query_one("""
        SELECT id FROM reseñas
        WHERE usuario_id = ? AND fecha_creacion >= datetime('now', '-7 days')
    """, (user_id,))

    if reciente:
        return jsonify({'error': 'Ya dejaste una reseña recientemente. Gracias!'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reseñas (usuario_id, texto, calificacion)
        VALUES (?, ?, ?)
    ''', (user_id, texto, calificacion))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Reseña enviada. Gracias por tu opinión!'}), 201

@app.route('/api/admin/resenas', methods=['GET'])
@jwt_required()
def get_all_resenas():
    """Obtener todas las reseñas (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    reseñas = query_to_list("""
        SELECT r.*, u.nombre as usuario_nombre, u.email as usuario_email
        FROM reseñas r
        JOIN usuarios u ON r.usuario_id = u.id
        ORDER BY r.fecha_creacion DESC
    """)
    return jsonify(reseñas)

@app.route('/api/admin/resenas/<int:resena_id>', methods=['PUT'])
@jwt_required()
def update_resena(resena_id):
    """Aprobar/responder reseña (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    data = request.get_json()
    aprobado = 1 if data.get('aprobado') else 0
    respuesta = data.get('respuesta', '').strip()

    execute_query(
        "UPDATE reseñas SET aprobado = ?, respuesta = ? WHERE id = ?",
        (aprobado, respuesta, resena_id)
    )

    return jsonify({'message': 'Reseña actualizada'})

@app.route('/api/admin/resenas/<int:resena_id>', methods=['DELETE'])
@jwt_required()
def delete_resena(resena_id):
    """Eliminar reseña (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    execute_query("UPDATE reseñas SET activo = 0 WHERE id = ?", (resena_id,))
    return jsonify({'message': 'Reseña eliminada'})

@app.route('/api/resenas/stats', methods=['GET'])
def get_resenas_stats():
    """Obtener estadísticas de reseñas"""
    stats = query_one("""
        SELECT 
            COUNT(*) as total,
            ROUND(AVG(calificacion), 1) as promedio
        FROM reseñas
        WHERE aprobado = 1 AND activo = 1
    """)
    return jsonify(stats)

# ============ RUTAS DE FAQs ============

@app.route('/api/faqs', methods=['GET'])
def get_faqs():
    """Obtener FAQs activas"""
    faqs = query_to_list("SELECT * FROM faqs WHERE activo = 1 ORDER BY orden")
    return jsonify(faqs)

@app.route('/api/admin/faqs', methods=['GET'])
@jwt_required()
def get_all_faqs():
    """Obtener todas las FAQs (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    faqs = query_to_list("SELECT * FROM faqs ORDER BY orden")
    return jsonify(faqs)

@app.route('/api/admin/faqs', methods=['POST'])
@jwt_required()
def create_faq():
    """Crear FAQ (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    data = request.get_json()
    pregunta = data.get('pregunta', '').strip()
    respuesta = data.get('respuesta', '').strip()

    if not pregunta or not respuesta:
        return jsonify({'error': 'Pregunta y respuesta son obligatorias'}), 400

    max_orden = query_one("SELECT MAX(orden) as max FROM faqs")
    orden = (max_orden['max'] or 0) + 1

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO faqs (pregunta, respuesta, orden)
        VALUES (?, ?, ?)
    ''', (pregunta, respuesta, orden))
    conn.commit()
    conn.close()

    return jsonify({'message': 'FAQ creada correctamente'}), 201

@app.route('/api/admin/faqs/<int:faq_id>', methods=['PUT'])
@jwt_required()
def update_faq(faq_id):
    """Actualizar FAQ (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    data = request.get_json()
    pregunta = data.get('pregunta', '').strip()
    respuesta = data.get('respuesta', '').strip()
    orden = data.get('orden', 0)

    execute_query(
        "UPDATE faqs SET pregunta = ?, respuesta = ?, orden = ? WHERE id = ?",
        (pregunta, respuesta, orden, faq_id)
    )

    return jsonify({'message': 'FAQ actualizada'})

@app.route('/api/admin/faqs/<int:faq_id>', methods=['DELETE'])
@jwt_required()
def delete_faq(faq_id):
    """Eliminar FAQ (admin)"""
    user_id = get_jwt_identity()
    user = query_one("SELECT rol FROM usuarios WHERE id = ?", (user_id,))

    if user['rol'] != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403

    execute_query("UPDATE faqs SET activo = 0 WHERE id = ?", (faq_id,))
    return jsonify({'message': 'FAQ eliminada'})

# ============ ESTADÍSTICAS ADICIONALES ============

@app.route('/api/admin/stats', methods=['GET'])
def get_public_stats():
    """Obtener estadísticas públicas"""
    clientes = query_one("SELECT COUNT(*) as total FROM usuarios WHERE rol = 'cliente'")
    return jsonify({'clientes': clientes['total'] if clientes else 0})

# ============ RUTA PRINCIPAL ============

@app.route('/')
def index():
    """Página principal"""
    return '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cargando...</title>
    </head>
    <body>
        <p>Cargando aplicación...</p>
        <script>
            window.location.href = '/static/index.html';
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    import os
    
    # Verificar que existe la base de datos
    if not os.path.exists(DB_NAME):
        print("[WARN] Base de datos no encontrada. Ejecuta: python init_db.py")
        print("     Luego reinicia el servidor.")
    
    # Obtener el puerto de Render (o usar 5000 localmente)
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 50)
    print("[OK] Servidor iniciado")
    print(f"     Puerto: {port}")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=port)