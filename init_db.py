"""
Inicializador de base de datos
Crea todas las tablas e inserta datos iniciales
"""
import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "negocio.db"

def crear_tablas():
    """Crea las tablas de la base de datos"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT DEFAULT 'cliente',
            telefono TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabla de servicios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            duracion INTEGER NOT NULL,
            activo INTEGER DEFAULT 1
        )
    ''')

    # Tabla de turnos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS turnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            servicio_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            estado TEXT DEFAULT 'pendiente',
            notas TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (servicio_id) REFERENCES servicios(id)
        )
    ''')
    
    # Índices para mejor rendimiento
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_turnos_fecha ON turnos(fecha)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_turnos_estado ON turnos(estado)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_turnos_usuario ON turnos(usuario_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_servicios_activo ON servicios(activo)')

    # Tabla de configuración
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracion (
            clave TEXT PRIMARY KEY,
            valor TEXT
        )
    ''')

    # Tabla de testimonios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS testimonios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            texto TEXT NOT NULL,
            calificacion INTEGER DEFAULT 5,
            activo INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabla de reseñas (nueva)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reseñas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            texto TEXT NOT NULL,
            calificacion INTEGER NOT NULL CHECK(calificacion >= 1 AND calificacion <= 5),
            respuesta TEXT,
            aprobado INTEGER DEFAULT 0,
            activo INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')

    # Tabla de FAQs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pregunta TEXT NOT NULL,
            respuesta TEXT NOT NULL,
            orden INTEGER DEFAULT 0,
            activo INTEGER DEFAULT 1
        )
    ''')

    conn.commit()
    conn.close()
    print("[OK] Tablas creadas correctamente")

def insertar_datos_iniciales():
    """Inserta datos iniciales de ejemplo"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Verificar si ya hay datos
    cursor.execute("SELECT COUNT(*) FROM configuracion")
    if cursor.fetchone()[0] > 0:
        conn.close()
        print("[OK] Datos iniciales ya existen")
        return

    # Insertar configuración por defecto
    config_default = [
        ('nombre_negocio', 'Mi Negocio'),
        ('descripcion', 'Tu negocio local de confianza'),
        ('telefono', '+54 11 1234-5678'),
        ('email', 'contacto@minegocio.com'),
        ('direccion', 'Av. Principal 123'),
        ('horario_atencion', 'Lunes a Viernes: 9:00 - 18:00'),
        ('whatsapp', '+5491112345678'),
        ('facebook', 'https://facebook.com/minegocio'),
        ('instagram', 'https://instagram.com/minegocio'),
        ('color_primario', '#2563eb'),
        ('color_secundario', '#1e40af'),
        ('color_acento', '#f59e0b'),
        ('color_fondo', '#ffffff'),
        ('color_texto', '#1f2937'),
        ('logo_url', '/static/img/logo.png'),
        ('metatitle', 'Mi Negocio - Servicios Profesionales'),
        ('metadescription', 'Los mejores servicios para ti'),
    ]

    cursor.executemany("INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)", config_default)

    # Insertar usuario administrador por defecto
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    cursor.execute('''
        INSERT INTO usuarios (nombre, email, password_hash, rol, telefono)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Administrador', 'admin@minegocio.com', admin_password, 'admin', '+54 11 1234-5678'))

    # Insertar servicios de ejemplo
    servicios = [
        ('Consulta General', 'Atención médica general para toda la familia', 5000, 30),
        ('Limpieza Dental', 'Limpieza profesional de dientes', 8000, 45),
        ('Corte de Pelo', 'Corte y peinado profesional', 2500, 30),
        ('Manicura', 'Manicura completa con esmaltado', 3000, 45),
        ('Masaje Relajante', 'Masaje corporal completo', 6000, 60),
    ]

    cursor.executemany('''
        INSERT INTO servicios (nombre, descripcion, precio, duracion)
        VALUES (?, ?, ?, ?)
    ''', servicios)

    # Insertar testimonios de ejemplo
    testimonios = [
        ('María González', 'Excelente atención, muy profesionales', 5),
        ('Juan Pérez', 'Muy satisfecho con el servicio', 5),
        ('Ana López', 'Recomiendo este negocio a todos', 5),
    ]

    cursor.executemany('''
        INSERT INTO testimonios (nombre, texto, calificacion)
        VALUES (?, ?, ?)
    ''', testimonios)

    # Insertar FAQs iniciales
    faqs = [
        ('¿Cómo puedo reservar un turno?', 'Puedes reservar un turno online creando una cuenta o iniciando sesión. Selecciona el servicio, fecha y horario que más te convenga.', 1),
        ('¿Cuál es la política de cancelación?', 'Puedes cancelar tu turno hasta 24 horas antes sin costo adicional. Cancelaciones con menos tiempo pueden tener cargo.', 2),
        ('¿Qué métodos de pago aceptan?', 'Aceptamos efectivo, tarjetas de crédito/débito, Mercado Pago y transferencias bancarias.', 3),
        ('¿Tienen garantía?', 'Sí, todos nuestros servicios tienen garantía de satisfacción. Si no quedás conforme, te devolvemos el dinero.', 4),
    ]
    cursor.executemany('''
        INSERT INTO faqs (pregunta, respuesta, orden)
        VALUES (?, ?, ?)
    ''', faqs)

    conn.commit()
    conn.close()
print("[OK] Datos iniciales insertados correctamente")
print("  Usuario admin: admin@minegocio.com / admin123")

def main():
    """Función principal"""
    print("Inicializando base de datos...")
    crear_tablas()
    insertar_datos_iniciales()
print("\n[OK] Base de datos lista!")
print(f"  Archivo: {DB_NAME}")

if __name__ == '__main__':
    main()
