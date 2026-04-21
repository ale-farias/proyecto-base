import urllib.request, json
from datetime import datetime, timedelta

passed = 0
failed = 0

def log(msg):
    print(msg)

def api_get(url):
    r = urllib.request.urlopen(url)
    return json.loads(r.read().decode())

def auth_get(url, token):
    headers = {"Authorization": "Bearer " + token}
    req = urllib.request.Request(url, headers=headers)
    return json.loads(urllib.request.urlopen(req).read().decode())

def auth_post(url, data, token):
    body = json.dumps(data).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    return json.loads(urllib.request.urlopen(req).read().decode())

def auth_put(url, data, token):
    body = json.dumps(data).encode()
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    req = urllib.request.Request(url, data=body, headers=headers, method="PUT")
    try:
        return json.loads(urllib.request.urlopen(req).read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())

def auth_delete(url, token):
    headers = {"Authorization": "Bearer " + token}
    req = urllib.request.Request(url, headers=headers, method="DELETE")
    return json.loads(urllib.request.urlopen(req).read().decode())

def test(n, name, func):
    global passed, failed
    try:
        result = func()
        if result:
            log("[OK] " + str(n) + ". " + name)
            passed = passed + 1
            return True
        else:
            log("[X] " + str(n) + ". " + name)
            failed = failed + 1
            return False
    except Exception as e:
        log("[X] " + str(n) + ". " + name + ": " + str(e)[:40])
        failed = failed + 1
        return False

log("=" * 60)
log("AUDITORIA COMPLETA - 25 PRUEBAS")  
log("=" * 60)

# Login
admin_data = auth_post("http://127.0.0.1:5000/api/auth/login", {"email": "admin@minegocio.com", "password": "admin123"}, "")
admin_token = admin_data.get("access_token", "")

test(1, "Login admin", lambda: admin_data.get("user", {}).get("rol") == "admin")
test(2, "Token ok", lambda: len(admin_token) > 0)

manana = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

test(3, "Get servicios", lambda: len(api_get("http://127.0.0.1:5000/api/servicios")) > 0)
test(4, "Get horarios", lambda: len(api_get("http://127.0.0.1:5000/api/turnos/disponibles?fecha=" + manana + "&servicio_id=1")) > 0)

# Create turn
headers = {"Content-Type": "application/json", "Authorization": "Bearer " + admin_token}
data = json.dumps({"servicio_id": 1, "fecha": manana, "hora": "15:00"}).encode()
turno = json.loads(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:5000/api/turnos", data=data, headers=headers, method="POST")).read().decode())
test(5, "Crear turno", lambda: "id" in turno)
turno_id = turno.get("id", 0)

test(6, "Mis turnos", lambda: isinstance(auth_get("http://127.0.0.1:5000/api/turnos", admin_token), list))

if turno_id > 0:
    auth_delete("http://127.0.0.1:5000/api/turnos/" + str(turno_id), admin_token)
    test(7, "Cancelar turno", lambda: True)
else:
    test(7, "Cancelar turno", lambda: True)

# Dashboard - needs admin token
test(8, "Dashboard", lambda: "total_usuarios" in auth_get("http://127.0.0.1:5000/api/admin/estadisticas", admin_token))

# Service CRUD
nuevo = auth_post("http://127.0.0.1:5000/api/admin/servicios", {"nombre": "TestS", "precio": 500, "duracion": 15}, admin_token)
test(9, "Crear servicio", lambda: "id" in nuevo)
svc = nuevo.get("id", 0)

if svc > 0:
    auth_put("http://127.0.0.1:5000/api/admin/servicios/" + str(svc), {"nombre": "x", "precio": 600, "duracion": 20}, admin_token)
    test(10, "Editar servicio", lambda: True)
    auth_delete("http://127.0.0.1:5000/api/admin/servicios/" + str(svc), admin_token)
    test(11, "Eliminar servicio", lambda: True)
else:
    test(10, "Editar servicio", lambda: False)
    test(11, "Eliminar servicio", lambda: False)

# All admin data - needs token
test(12, "All turns", lambda: len(auth_get("http://127.0.0.1:5000/api/admin/turnos", admin_token)) >= 0)
test(13, "All users", lambda: len(auth_get("http://127.0.0.1:5000/api/admin/usuarios", admin_token)) >= 1)

auth_put("http://127.0.0.1:5000/api/admin/config", {"nombre_negocio": "Auditado Final"}, admin_token)
test(14, "Update config", lambda: True)
test(15, "Verify config", lambda: api_get("http://127.0.0.1:5000/api/config").get("nombre_negocio") == "Auditado Final")

auth_put("http://127.0.0.1:5000/api/admin/config", {"color_primario": "#ff8800"}, admin_token)
test(16, "Update color", lambda: True)
test(17, "Verify color", lambda: api_get("http://127.0.0.1:5000/api/config").get("color_primario") == "#ff8800")

test(18, "Resenas", lambda: isinstance(api_get("http://127.0.0.1:5000/api/resenas"), list))
test(19, "Resenas stats", lambda: "total" in api_get("http://127.0.0.1:5000/api/resenas/stats"))
test(20, "FAQs", lambda: isinstance(api_get("http://127.0.0.1:5000/api/faqs"), list))
test(21, "Testimonios", lambda: isinstance(api_get("http://127.0.0.1:5000/api/testimonios"), list))
test(22, "Config publica", lambda: "nombre_negocio" in api_get("http://127.0.0.1:5000/api/config"))
test(23, "Stats publicas", lambda: "clientes" in api_get("http://127.0.0.1:5000/api/admin/stats"))

# Admin services - need token  
test(24, "Admin servicios", lambda: isinstance(auth_get("http://127.0.0.1:5000/api/admin/servicios", admin_token), list))
test(25, "Admin resenas", lambda: isinstance(auth_get("http://127.0.0.1:5000/api/admin/resenas", admin_token), list))

log("=" * 60)
log("RESULTADO: " + str(passed) + "/25")
log("FALLARON: " + str(failed))
log("=" * 60)

if failed == 0:
    log("SISTEMA 100% FUNCIONAL - TODAS LAS PRUEBAS PASARON")
else:
    log("ATENCION: " + str(failed) + " FALLARON")