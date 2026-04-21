import sqlite3
conn = sqlite3.connect('negocio.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM reseñas WHERE aprobado=1')
if c.fetchone()[0] == 0:
    c.execute('INSERT INTO reseñas (usuario_id, texto, calificacion, aprobado, activo) VALUES (1, "Excelente atención, muy profesionales", 5, 1, 1)')
    c.execute('INSERT INTO reseñas (usuario_id, texto, calificacion, aprobado, activo) VALUES (1, "Muy satisfecho con el servicio", 5, 1, 1)')
    c.execute('INSERT INTO reseñas (usuario_id, texto, calificacion, aprobado, activo) VALUES (1, "Recomiendo este negocio a todos", 5, 1, 1)')
    conn.commit()
    print('Reseñas insertadas')
else:
    print('Ya existen reseñas')
conn.close()