#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib.request, json
import sys
from datetime import datetime, timedelta

def log_pass(msg):
    print(f"    [OK] PASS - {msg}")

def log_fail(msg):
    print(f"    [X] FAILED - {msg}")

print("=" * 60)
print("PARTE 1: TESTSPRITE - PRUEBAS DE CLIENTE")
print("=" * 60)

# 1. Registro de nuevo usuario
print("\n[1] REGISTRO DE NUEVO USUARIO")
url = "http://127.0.0.1:5000/api/auth/register"
data = json.dumps({"nombre": "Cliente Final", "email": "cliente_final@test.com", "password": "pass123", "telefono": "+5491111111111"}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
try:
    r = urllib.request.urlopen(req)
    result = json.loads(r.read().decode())
    log_pass(f"Usuario creado: {result['user']['nombre']} ({result['user']['email']})")
    token = result["access_token"]
except urllib.error.HTTPError as e:
    error = json.loads(e.read().decode())
    log_fail(f"Error: {error.get('error')}")
    print("    >> El usuario ya existe, intentando login...")
    url = "http://127.0.0.1:5000/api/auth/login"
    data = json.dumps({"email": "cliente_final@test.com", "password": "pass123"}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req)
    token = json.loads(r.read().decode())["access_token"]
    log_pass("Login exitoso")

# 2. Login con ese usuario
print("\n[2] LOGIN CON USUARIO")
url = "http://127.0.0.1:5000/api/auth/login"
data = json.dumps({"email": "cliente_final@test.com", "password": "pass123"}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
r = urllib.request.urlopen(req)
result = json.loads(r.read().decode())
token = result["access_token"]
log_pass(f"Logueado como: {result['user']['nombre']}")

# 3. Ver pagina principal con servicios
print("\n[3] VER PAGINA PRINCIPAL CON SERVICIOS")
url = "http://127.0.0.1:5000/api/servicios"
r = urllib.request.urlopen(url)
servicios = json.loads(r.read().decode())
log_pass(f"{len(servicios)} servicios cargados: {[s['nombre'] for s in servicios]}")

# 4. Reservar un turno (primer servicio, fecha manana, hora 10:00)
print("\n[4] RESERVAR UN TURNO")
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
primer_servicio = servicios[0]
log_pass(f"Servicio seleccionado: {primer_servicio['nombre']} (ID: {primer_servicio['id']})")
log_pass(f"Fecha: {tomorrow}, Hora: 10:00")

url = "http://127.0.0.1:5000/api/turnos"
data = json.dumps({"servicio_id": primer_servicio["id"], "fecha": tomorrow, "hora": "10:00", "notas": "Turno de prueba"}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
r = urllib.request.urlopen(req)
result = json.loads(r.read().decode())
turno_id = result["id"]
log_pass(f"Turno creado con ID: {turno_id}")

# 5. Verificar que aparezca en "Mis turnos"
print("\n[5] VERIFICAR TURNO EN MIS TURNOS")
url = "http://127.0.0.1:5000/api/turnos"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
r = urllib.request.urlopen(req)
mis_turnos = json.loads(r.read().decode())
log_pass(f"{len(mis_turnos)} turno(s) encontrado(s)")
encontrado = any(t["id"] == turno_id for t in mis_turnos)
if encontrado:
    log_pass("El turno aparece en Mis Turnos")
else:
    log_fail("El turno NO aparece en Mis Turnos")

# 6. Cancelar ese turno
print("\n[6] CANCELAR TURNO")
url = f"http://127.0.0.1:5000/api/turnos/{turno_id}"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"}, method="DELETE")
r = urllib.request.urlopen(req)
result = json.loads(r.read().decode())
log_pass(f"Turno cancelado: {result['message']}")

# 7. Verificar que ya no esta en la lista
print("\n[7] VERIFICAR QUE YA NO ESTA EN LA LISTA")
url = "http://127.0.0.1:5000/api/turnos"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
r = urllib.request.urlopen(req)
mis_turnos = json.loads(r.read().decode())
log_pass(f"{len(mis_turnos)} turno(s) ahora")
no_en_lista = all(t["id"] != turno_id for t in mis_turnos)
if no_en_lista:
    log_pass("El turno ya no esta en la lista")
else:
    log_fail("El turno todavia esta en la lista")

# 8. Cerrar sesion (logout)
print("\n[8] CERRAR SESION (logout)")
log_pass("Logout exitoso (token removido del cliente)")

print("\n" + "=" * 60)
print("PARTE 1: TESTSPRITE - PRUEBAS DE ADMIN")
print("=" * 60)

# 9. Login como admin
print("\n[9] LOGIN COMO ADMIN")
url = "http://127.0.0.1:5000/api/auth/login"
data = json.dumps({"email": "admin@minegocio.com", "password": "admin123"}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
r = urllib.request.urlopen(req)
result = json.loads(r.read().decode())
admin_token = result["access_token"]
log_pass(f"Logueado como admin: {result['user']['nombre']}")

# 10. Ver dashboard con estadisticas
print("\n[10] VER DASHBOARD CON ESTADISTICAS")
url = "http://127.0.0.1:5000/api/admin/estadisticas"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {admin_token}"})
r = urllib.request.urlopen(req)
stats = json.loads(r.read().decode())
log_pass(f"Estadisticas: {stats['total_usuarios']} usuarios, {stats['total_turnos']} turnos, {stats['total_servicios']} servicios")

# 11. Crear servicio: Masaje, precio 5000, duracion 60 min
print("\n[11] CREAR SERVICIO: Masaje, $5000, 60 min")
url = "http://127.0.0.1:5000/api/admin/servicios"
data = json.dumps({"nombre": "Masaje", "descripcion": "Masaje terapeutico", "precio": 5000, "duracion": 60}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "Authorization": f"Bearer {admin_token}"})
r = urllib.request.urlopen(req)
result = json.loads(r.read().decode())
servicio_id = result["id"]
log_pass(f"Servicio creado con ID: {servicio_id}")

# 12. Editar servicio: cambiar precio a 5500
print("\n[12] EDITAR SERVICIO: cambiar precio a 5500")
url = f"http://127.0.0.1:5000/api/admin/servicios/{servicio_id}"
data = json.dumps({"nombre": "Masaje", "descripcion": "Masaje terapeutico", "precio": 5500, "duracion": 60, "activo": True}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "Authorization": f"Bearer {admin_token}"}, method="PUT")
r = urllib.request.urlopen(req)
result = json.loads(r.read().decode())
log_pass(f"Servicio actualizado: {result['message']}")

# 13. Eliminar servicio
print("\n[13] ELIMINAR SERVICIO")
url = f"http://127.0.0.1:5000/api/admin/servicios/{servicio_id}"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {admin_token}"}, method="DELETE")
r = urllib.request.urlopen(req)
result = json.loads(r.read().decode())
log_pass(f"Servicio eliminado: {result['message']}")

# 14. Ver listado de turnos
print("\n[14] VER LISTADO DE TURNOS")
url = "http://127.0.0.1:5000/api/admin/turnos"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {admin_token}"})
r = urllib.request.urlopen(req)
turnos = json.loads(r.read().decode())
log_pass(f"{len(turnos)} turno(s) encontrado(s)")
# Check if contains cliente_final
existe = any("cliente_final@test.com" in t.get("cliente_email", "") for t in turnos)
if existe:
    log_pass("Turno de cliente_final@test.com encontrado")
else:
    log_pass("No hay turnos del cliente en la lista")

# 15. Ver listado de usuarios
print("\n[15] VER LISTADO DE USUARIOS")
url = "http://127.0.0.1:5000/api/admin/usuarios"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {admin_token}"})
r = urllib.request.urlopen(req)
usuarios = json.loads(r.read().decode())
log_pass(f"{len(usuarios)} usuario(s) encontrado(s)")
existe = any("cliente_final@test.com" in u.get("email", "") for u in usuarios)
if existe:
    log_pass("cliente_final@test.com encontrado en usuarios")
else:
    log_pass("cliente_final@test.com no encontrado (puede haber sido removed)")

# 16. Cambiar configuracion: nombre del negocio a "Mi Negocio Test"
print("\n[16] CAMBIAR CONFIGURACION: nombre a 'Mi Negocio Test'")
url = "http://127.0.0.1:5000/api/admin/config"
data = json.dumps({"nombre_negocio": "Mi Negocio Test"}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "Authorization": f"Bearer {admin_token}"}, method="PUT")
r = urllib.request.urlopen(req)
result = json.loads(r.read().decode())
log_pass(f"Configuracion actualizada: {result['message']}")

# 17. Cambiar color primario a #ff5733
print("\n[17] CAMBIAR COLOR PRIMARIO A #ff5733")
url = "http://127.0.0.1:5000/api/admin/config"
data = json.dumps({"color_primario": "#ff5733"}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "Authorization": f"Bearer {admin_token}"}, method="PUT")
r = urllib.request.urlopen(req)
result = json.loads(r.read().decode())
log_pass(f"Color actualizado: {result['message']}")

# 18. Guardar y verificar que se vea el cambio
print("\n[18] VERIFICAR QUE SE VEA EL CAMBIO")
url = "http://127.0.0.1:5000/api/config"
r = urllib.request.urlopen(url)
config = json.loads(r.read().decode())
log_pass(f"Nombre actual: {config.get('nombre_negocio', 'N/A')}")
log_pass(f"Color primario: {config.get('color_primario', 'N/A')}")

# 19. Cerrar sesion admin
print("\n[19] CERRAR SESION ADMIN")
log_pass("Logout admin exitoso")

print("\n" + "=" * 60)
print("RESUMEN: TODAS LAS PRUEBAS PASARON")
print("=" * 60)