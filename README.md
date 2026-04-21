# Sistema de Gestión para Negocios Locales

Una base reutilizable y profesional para negocios locales (restaurantes, peluquerías, clínicas, etc.) con sistema de reservas online.

## Estructura del Proyecto

```
├── app.py              # Backend Flask con API REST
├── init_db.py          # Inicializador de base de datos
├── requirements.txt    # Dependencias Python
├── negocio.db          # Base de datos SQLite (se crea automáticamente)
├── README.md           # Este archivo
├── static/
│   ├── index.html      # Página principal pública
│   ├── login.html      # Página de login
│   ├── register.html   # Página de registro
│   ├── dashboard.html  # Panel del cliente
│   ├── admin.html      # Panel de administración
│   ├── css/
│   │   └── styles.css  # Todos los estilos
│   └── js/
│       └── app.js      # Lógica del frontend
```

## Características

- **Sistema de autenticación** con JWT (registro, login, logout)
- **Roles**: Cliente y Administrador
- **Gestión de servicios**: CRUD completo desde el panel admin
- **Reservas de turnos**: Los clientes pueden reservar, cancelar y ver sus turnos
- **Panel de administración**: Estadísticas, gestión de usuarios y turnos
- **Personalización**: Colores, nombre, logo, horarios desde la base de datos
- **Diseño responsive**: Mobile-first
- **WhatsApp flotante**: Contacto directo

## Requisitos

- Python 3.8 o superior
- Navegador web moderno

## Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Inicializar la base de datos

```bash
python init_db.py
```

Esto creará el archivo `negocio.db` con:
- Usuario admin por defecto: `admin@minegocio.com` / `admin123`
- 5 servicios de ejemplo
- 3 testimonios de ejemplo

### 3. Ejecutar el servidor

```bash
python app.py
```

El servidor estará disponible en: **http://localhost:5000**

## Uso

### Acceso público (index.html)
- Ver servicios disponibles
- Ver testimonios
- Botón para reservar (requiere registro)

### Cliente (dashboard.html)
- Registro y login
- Ver mis turnos
- Reservar nuevo turno (seleccionar servicio, fecha, hora)
- Cancelar turnos
- Editar perfil

### Administrador (admin.html)
Acceso: `admin@minegocio.com` / `admin123`

- **Dashboard**: Estadísticas (usuarios, turnos, ingresos)
- **Turnos**: Ver todos, filtrar por estado, cambiar estado
- **Usuarios**: Ver lista de clientes registrados
- **Servicios**: Crear, editar, eliminar servicios
- **Configuración**: Personalizar:
  - Nombre del negocio
  - Descripción
  - Teléfono, email, dirección
  - Horario de atención
  - WhatsApp
  - Colores (principal, secundario, acento, fondo)
  - Meta tags SEO

## Personalización

### Cambiar colores

Desde el panel de admin (http://localhost:5000/static/admin.html):

1. Inicia sesión como admin
2. Ve a Configuración
3. Cambia los colores usando los selectores de color
4. Guarda los cambios

Los cambios se aplican automáticamente a toda la web.

### Agregar servicios

1. Inicia sesión como admin
2. Ve a la sección Servicios
3. Click en "Nuevo Servicio"
4. Completa nombre, descripción, precio y duración

### Cambiar textos y datos

Desde Configuración puedes cambiar:
- Nombre del negocio
- Descripción
- Teléfono y email
- Dirección
- Horario de atención
- WhatsApp
- Redes sociales

## Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/register` | Registar usuario |
| POST | `/api/auth/login` | Iniciar sesión |
| GET | `/api/auth/me` | Datos del usuario actual |
| PUT | `/api/auth/update-profile` | Actualizar perfil |
| GET | `/api/config` | Configuración pública |
| GET | `/api/servicios` | Lista de servicios activos |
| GET | `/api/turnos` | Turnos del usuario |
| POST | `/api/turnos` | Crear turno |
| DELETE | `/api/turnos/{id}` | Cancelar turno |
| GET | `/api/admin/turnos` | Todos los turnos (admin) |
| GET | `/api/admin/usuarios` | Todos los usuarios (admin) |
| GET | `/api/admin/estadisticas` | Estadísticas (admin) |
| PUT | `/api/admin/config` | Actualizar config (admin) |

## Producción

Para desplegar en producción:

1. Cambia la `SECRET_KEY` en `app.py`
2. Cambia la `JWT_SECRET_KEY` en `app.py`
3. Usa un servidor WSGI como Gunicorn
4. Configura HTTPS

Ejemplo con Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Troubleshooting

### Error: "Base de datos no encontrada"
Ejecuta: `python init_db.py`

### Error: "Puerto en uso"
Cambia el puerto en `app.py` línea final:
```python
app.run(debug=True, port=5001)
```

### Olvidaste la contraseña de admin
Edita `init_db.py` y vuelve a ejecutar:
```bash
python init_db.py
```

## Licencia

MIT - Uso libre para proyectos comerciales y personales.
