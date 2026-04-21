# PRD - Sistema de Gestión para Negocios Locales

## 1. Descripción del Producto

**Nombre:** Sistema de Gestión de Turnos para Negocios Locales

**Tipo:** Aplicación web full-stack

**Resumen:** Plataforma de reservas online para negocios locales (restaurantes, peluquerías, clínicas, etc.) que permite a los clientes reservar turnos y a los administradores gestionar el negocio.

**Usuarios objetivo:** Dueños de negocios locales que necesitan gestionar reservas y clientes.

---

## 2. Funcionalidad Core

### 2.1 Autenticación
- Registro de usuarios con email, nombre, teléfono y contraseña
- Login con JWT (token expira en 24 horas)
- Logout
- Actualización de perfil
- Roles: `cliente` y `admin`

### 2.2 Reservas de Turnos
- Ver servicios disponibles
- Seleccionar servicio, fecha y hora
- Crear reserva
- Cancelar reserva (propietario o admin)
- Ver mis reservas

### 2.3 Panel de Administración
- Dashboard con estadísticas
- Gestión de usuarios (ver, editar rol)
- Gestión de servicios (CRUD)
- Gestión de turnos (ver todos, cambiar estado)
- Configuración del negocio

### 2.4 Público
- Landing page con servicios y testimonios
- Botón flotante de WhatsApp

---

## 3. Tech Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | HTML, CSS, JavaScript vanilla |
| Backend | Flask (Python) |
| Base de datos | SQLite |
| Auth | JWT (flask-jwt-extended) |
| API | REST |

---

## 4. Estructura de Datos

### Tabla: usuarios
| Campo | Tipo | Descripción |
|------|------|-------------|
| id | INTEGER | PK |
| nombre | TEXT | Requerido |
| email | TEXT | Unique, requerido |
| password_hash | TEXT | SHA256 |
| telefono | TEXT | Opcional |
| rol | TEXT | 'cliente' o 'admin' |
| fecha_registro | DATETIME | Auto |

### Tabla: servicios
| Campo | Tipo | Descripción |
|------|------|-------------|
| id | INTEGER | PK |
| nombre | TEXT | Requerido |
| descripcion | TEXT | |
| precio | REAL | |
| duracion | INTEGER | Minutos |
| activo | INTEGER | 1/0 |

### Tabla: turnos
| Campo | Tipo | Descripción |
|------|------|-------------|
| id | INTEGER | PK |
| usuario_id | INTEGER | FK usuarios |
| servicio_id | INTEGER | FK servicios |
| fecha | TEXT | YYYY-MM-DD |
| hora | TEXT | HH:MM |
| notas | TEXT | |
| estado | TEXT | pendiente/confirmado/completado/cancelado |

### Tabla: configuracion
| Campo | Tipo | Descripción |
|------|------|-------------|
| clave | TEXT | PK |
| valor | TEXT | |

### Tabla: testimonios
| Campo | Tipo | Descripción |
|------|------|-------------|
| id | INTEGER | PK |
| nombre | TEXT | |
| texto | TEXT | |
| calificacion | INTEGER | 1-5 |
| activo | INTEGER | 1/0 |
| fecha_creacion | DATETIME | Auto |

---

## 5. API Endpoints

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | No | Registrar usuario |
| POST | `/api/auth/login` | No | Iniciar sesión |
| GET | `/api/auth/me` | JWT | Datos usuario actual |
| PUT | `/api/auth/update-profile` | JWT | Actualizar perfil |
| GET | `/api/config` | No | Configuración pública |
| PUT | `/api/admin/config` | JWT (admin) | Actualizar config |
| GET | `/api/servicios` | No | Lista servicios activos |
| GET | `/api/admin/servicios` | JWT (admin) | Todos servicios |
| POST | `/api/admin/servicios` | JWT (admin) | Crear servicio |
| PUT | `/api/admin/servicios/<id>` | JWT (admin) | Actualizar servicio |
| DELETE | `/api/admin/servicios/<id>` | JWT (admin) | Eliminar servicio |
| GET | `/api/turnos/disponibles` | No | Horarios disponibles |
| GET | `/api/turnos` | JWT | Mis turnos |
| POST | `/api/turnos` | JWT | Crear turno |
| DELETE | `/api/turnos/<id>` | JWT | Cancelar turno |
| GET | `/api/admin/turnos` | JWT (admin) | Todos turnos |
| PUT | `/api/admin/turnos/<id>/estado` | JWT (admin) | Cambiar estado |
| GET | `/api/admin/usuarios` | JWT (admin) | Todos usuarios |
| PUT | `/api/admin/usuarios/<id>` | JWT (admin) | Actualizar usuario |
| GET | `/api/admin/estadisticas` | JWT (admin) | Estadísticas |
| GET | `/api/testimonios` | No | Testimonios activos |
| POST | `/api/admin/testimonios` | JWT (admin) | Crear testimonio |

---

## 6. Configuraciones Editables

- Nombre del negocio
- Descripción
- Teléfono, email, dirección
- Horario de atención
- WhatsApp
- Colores: principal, secundario, acento, fondo
- Meta tags SEO

---

## 7. Credenciales por Defecto

| Rol | Email | Contraseña |
|-----|-------|-----------|
| Admin | admin@minegocio.com | admin123 |

---

## 8. Características Adicionales

- Diseño responsive (mobile-first)
- Botón flotante de WhatsApp
- Hash de contraseñas con SHA256
- Validaciones en registro (contraseña 6+ caracteres)

---

## 9. Roadmap Potencial

- [ ] Notificaciones por email
- [ ] Recordatorios de turno
- [ ] Calendarización avanzada
- [ ] Múltiples empleados
- [ ] Pago online
- [ ] App móvil
- [ ] Widget para terceros

---

*Documento generado automáticamente*