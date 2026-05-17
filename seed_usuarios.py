"""
Seeder de usuarios, reseñas y turnos de ejemplo
"""
import sqlite3
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

DB_NAME = "negocio.db"

USUARIOS = [
    ("María González", "maria@gmail.com", "cliente123", "+54 11 5555-0101"),
    ("Juan Pérez", "juan@hotmail.com", "cliente123", "+54 11 5555-0102"),
    ("Ana López", "ana@yahoo.com", "cliente123", "+54 11 5555-0103"),
    ("Carlos Ruiz", "carlos@gmail.com", "cliente123", "+54 11 5555-0104"),
    ("Laura Martínez", "laura@outlook.com", "cliente123", "+54 11 5555-0105"),
    ("Pedro Sánchez", "pedro@gmail.com", "cliente123", "+54 11 5555-0106"),
    ("Sofía Torres", "sofia@hotmail.com", "cliente123", "+54 11 5555-0107"),
    ("Diego Ramírez", "diego@yahoo.com", "cliente123", "+54 11 5555-0108"),
    ("Valentina Castro", "valentina@gmail.com", "cliente123", "+54 11 5555-0109"),
    ("Fernando Díaz", "fernando@outlook.com", "cliente123", "+54 11 5555-0110"),
    ("Camila Vargas", "camila@hotmail.com", "cliente123", "+54 11 5555-0111"),
    ("Andrés Mendoza", "andres@gmail.com", "cliente123", "+54 11 5555-0112"),
    ("Isabella Rojas", "isabella@yahoo.com", "cliente123", "+54 11 5555-0113"),
    ("Santiago Morales", "santiago@outlook.com", "cliente123", "+54 11 5555-0114"),
    ("Gabriela Herrera", "gabriela@gmail.com", "cliente123", "+54 11 5555-0115"),
]

RESENAS = [
    (2, "Excelente atención, muy profesionales. El servicio superó mis expectativas.", 5),
    (3, "Muy buen servicio, volveré pronto. Recomiendo ampliamente.", 5),
    (4, "El mejor lugar para este tipo de servicios. Súper recomendado.", 5),
    (5, "Atención personalizada y resultados increíbles. Muy conforme.", 4),
    (6, "Buen precio y excelente calidad. Me encantó la experiencia.", 5),
    (7, "Llegué sin turno y me atendieron rápido. Muy agradecido.", 4),
    (8, "Profesionales de primer nivel. Instalaciones impecables.", 5),
    (9, "Mejoró mucho mi calidad de vida. Gracias al equipo!", 5),
    (10, "Trato amable y profesional. Sin dudas volveré.", 4),
    (11, "Resultados visibles desde la primera sesión. Recomiendo!", 5),
    (12, "Precios accesibles y atención de calidad. Muy contento.", 4),
    (13, "Excelente experiencia de principio a fin. Sigan así!", 5),
    (14, "Muy puntuales y profesionales. Me encantó el servicio.", 5),
    (15, "Los mejores en lo que hacen. Gracias por todo!", 5),
]

TESTIMONIOS = [
    ("Lucía Fernández", "Calidad y calidez humana excepcional. Siempre salgo feliz de ahí!", 5),
    ("Roberto Giménez", "Llevo años viniendo y nunca me decepciona. Muy recomendado.", 5),
    ("Florencia Acosta", "Precios justos y atención inmejorable. Un antes y después.", 5),
    ("Martín Silva", "Ambiente agradable y profesionales capacitados. 10/10.", 5),
    ("Romina Paz", "Descubrí este lugar por recomendación y no me arrepiento. Excelente!", 5),
]

TEXTOS_RESENA = [
    "Muy buen servicio, lo recomiendo.",
    "Excelente atención al cliente.",
    "Gran profesionalismo y dedicación.",
    "Resultados sorprendentes, volveré pronto.",
    "Atención rápida y eficiente. Muy conforme.",
    "Me encantó el trato, muy amables.",
    "Súper recomendado, calidad garantizada.",
    "Buenos precios y mejor atención.",
]


def seed():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    insertados = 0
    for nombre, email, password, telefono in USUARIOS:
        c.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if c.fetchone():
            continue
        pw_hash = generate_password_hash(password)
        c.execute(
            "INSERT INTO usuarios (nombre, email, password_hash, rol, telefono) VALUES (?, ?, ?, 'cliente', ?)",
            (nombre, email, pw_hash, telefono),
        )
        insertados += 1
    conn.commit()

    c.execute("SELECT id FROM servicios WHERE activo = 1")
    servicios = [r[0] for r in c.fetchall()]
    c.execute("SELECT id FROM usuarios WHERE rol = 'cliente'")
    clientes = [r[0] for r in c.fetchall()]

    if not servicios:
        print("[!] No hay servicios. Ejecutá init_db.py primero.")
        conn.close()
        return

    reseñas_insertadas = 0
    for usuario_id, texto, calif in RESENAS:
        c.execute(
            "SELECT id FROM reseñas WHERE usuario_id = ? AND texto = ?",
            (usuario_id, texto),
        )
        if c.fetchone():
            continue
        dias_atras = random.randint(1, 60)
        fecha = (datetime.now() - timedelta(days=dias_atras)).isoformat()
        c.execute(
            "INSERT INTO reseñas (usuario_id, texto, calificacion, aprobado, activo, fecha_creacion) VALUES (?, ?, ?, 1, 1, ?)",
            (usuario_id, texto, calif, fecha),
        )
        reseñas_insertadas += 1
    conn.commit()

    testimonios_insertados = 0
    for nombre, texto, calif in TESTIMONIOS:
        c.execute(
            "SELECT id FROM testimonios WHERE nombre = ? AND texto = ?",
            (nombre, texto),
        )
        if c.fetchone():
            continue
        c.execute(
            "INSERT INTO testimonios (nombre, texto, calificacion, activo) VALUES (?, ?, ?, 1)",
            (nombre, texto, calif),
        )
        testimonios_insertados += 1
    conn.commit()

    turnos_insertados = 0
    for cliente_id in clientes[:8]:
        for _ in range(random.randint(1, 3)):
            servicio_id = random.choice(servicios)
            dias_atras = random.randint(1, 30)
            fecha = (datetime.now() - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
            hora = f"{random.randint(9, 17):02d}:00"
            estados = ("completado", "completado", "completado", "cancelado", "pendiente")
            estado = random.choice(estados)
            c.execute(
                "SELECT id FROM turnos WHERE usuario_id = ? AND fecha = ? AND hora = ?",
                (cliente_id, fecha, hora),
            )
            if c.fetchone():
                continue
            c.execute(
                "INSERT INTO turnos (usuario_id, servicio_id, fecha, hora, estado) VALUES (?, ?, ?, ?, ?)",
                (cliente_id, servicio_id, fecha, hora, estado),
            )
            turnos_insertados += 1
    conn.commit()

    conn.close()

    print(f"[OK] Usuarios insertados: {insertados}")
    print(f"[OK] Reseñas insertadas: {reseñas_insertadas}")
    print(f"[OK] Testimonios insertados: {testimonios_insertados}")
    print(f"[OK] Turnos insertados: {turnos_insertados}")
    print(f"\n  Total clientes: {len(clientes) + insertados}")
    print(f"  Total reseñas aprobadas: {len(RESENAS)}")
    print(f"  Contraseña para todos: cliente123")


if __name__ == "__main__":
    seed()
