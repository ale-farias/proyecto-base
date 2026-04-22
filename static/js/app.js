/**
 * APP.JS - Sistema de Gestión para Negocios Locales
 * Lógica del frontend senza frameworks
 */

// ==================== CONFIGURACIÓN ====================
const API_URL = '/api';
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'usuario_actual';
const THEME_KEY = 'theme_preference';

// ==================== TEMA OSCURO ====================
function initTheme() {
    const savedTheme = localStorage.getItem(THEME_KEY);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (prefersDark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
    return theme;
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem(THEME_KEY, next);
    renderThemeButton();
    return next;
}

function getTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light';
}

function renderThemeButton() {
    const theme = getTheme();
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        themeBtn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
        themeBtn.setAttribute('title', theme === 'dark' ? 'Modo claro' : 'Modo oscuro');
    }
}

// Inicializar tema al cargar
document.addEventListener('DOMContentLoaded', initTheme);

// ==================== UTILIDADES ====================

function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

function removeToken() {
    localStorage.removeItem(TOKEN_KEY);
}

function getUsuario() {
    const user = localStorage.getItem(USER_KEY);
    return user ? JSON.parse(user) : null;
}

function setUsuario(usuario) {
    localStorage.setItem(USER_KEY, JSON.stringify(usuario));
}

function removeUsuario() {
    localStorage.removeItem(USER_KEY);
}

function isLoggedIn() {
    return !!getToken();
}

function isAdmin() {
    const user = getUsuario();
    return user && user.rol === 'admin';
}

async function apiRequest(endpoint, options = {}) {
    const token = getToken();

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || 'Error en la solicitud');
    }

    return data;
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alerta alerta-${type}`;
    alertDiv.textContent = message;

    const container = document.querySelector('.contenedor');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        setTimeout(() => alertDiv.remove(), 5000);
    }
}

function formatFecha(fecha) {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-AR', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatPrecio(precio) {
    return new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'ARS'
    }).format(precio);
}

// ==================== AUTH ====================

async function login(email, password) {
    const data = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
    });

    setToken(data.access_token);
    setUsuario(data.user);
    return data.user;
}

async function register(nombre, email, password, telefono) {
    const data = await apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ nombre, email, password, telefono })
    });

    setToken(data.access_token);
    setUsuario(data.user);
    return data.user;
}

function logout() {
    removeToken();
    removeUsuario();
    window.location.href = '/static/index.html';
}

async function checkAuth() {
    if (!isLoggedIn()) return false;

    try {
        const user = await apiRequest('/auth/me');
        setUsuario(user);
        return true;
    } catch (e) {
        removeToken();
        removeUsuario();
        return false;
    }
}

// ==================== CONFIGURACIÓN ====================

async function loadConfig() {
    try {
        const config = await apiRequest('/config');
        applyConfig(config);
        return config;
    } catch (e) {
        console.error('Error cargando configuración:', e);
        return {};
    }
}

function applyConfig(config) {
    const root = document.documentElement;

    if (config.color_primario) {
        root.style.setProperty('--color-primario', config.color_primario);
    }
    if (config.color_secundario) {
        root.style.setProperty('--color-secundario', config.color_secundario);
    }
    if (config.color_acento) {
        root.style.setProperty('--color-acento', config.color_acento);
    }
    if (config.color_fondo) {
        root.style.setProperty('--color-fondo', config.color_fondo);
    }
    if (config.color_texto) {
        root.style.setProperty('--color-texto', config.color_texto);
    }

    // Actualizar elementos del DOM
    const titulo = document.getElementById('nombre-negocio');
    if (titulo && config.nombre_negocio) {
        titulo.textContent = config.nombre_negocio;
    }

    const desc = document.getElementById('descripcion-negocio');
    if (desc && config.descripcion) {
        desc.textContent = config.descripcion;
    }

    document.title = config.metatitle || config.nombre_negocio || 'Mi Negocio';
}

// ==================== SERVICIOS ====================

async function loadServicios() {
    return await apiRequest('/servicios');
}

async function loadAllServicios() {
    return await apiRequest('/admin/servicios');
}

async function createServicio(servicio) {
    return await apiRequest('/admin/servicios', {
        method: 'POST',
        body: JSON.stringify(servicio)
    });
}

async function updateServicio(id, servicio) {
    return await apiRequest(`/admin/servicios/${id}`, {
        method: 'PUT',
        body: JSON.stringify(servicio)
    });
}

async function deleteServicio(id) {
    return await apiRequest(`/admin/servicios/${id}`, {
        method: 'DELETE'
    });
}

// ==================== TURNOS ====================

async function loadMisTurnos() {
    return await apiRequest('/turnos');
}

async function loadHorariosDisponibles(fecha, servicioId) {
    return await apiRequest(`/turnos/disponibles?fecha=${fecha}&servicio_id=${servicioId}`);
}

async function crearTurno(servicioId, fecha, hora, notas) {
    return await apiRequest('/turnos', {
        method: 'POST',
        body: JSON.stringify({
            servicio_id: servicioId,
            fecha,
            hora,
            notas
        })
    });
}

async function cancelarTurno(id) {
    return await apiRequest(`/turnos/${id}`, {
        method: 'DELETE'
    });
}

// ==================== ADMIN - TURNOS ====================

async function loadAllTurnos(estado = null) {
    const query = estado ? `?estado=${estado}` : '';
    return await apiRequest(`/admin/turnos${query}`);
}

async function cambiarEstadoTurno(id, estado) {
    return await apiRequest(`/admin/turnos/${id}/estado`, {
        method: 'PUT',
        body: JSON.stringify({ estado })
    });
}

// ==================== ADMIN - USUARIOS ====================

async function loadAllUsuarios() {
    return await apiRequest('/admin/usuarios');
}

async function updateUsuario(id, data) {
    return await apiRequest(`/admin/usuarios/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

async function loadEstadisticas() {
    return await apiRequest('/admin/estadisticas');
}

// ==================== ADMIN - CONFIG ====================

async function updateConfig(config) {
    return await apiRequest('/admin/config', {
        method: 'PUT',
        body: JSON.stringify(config)
    });
}

// ==================== TESTIMONIOS ====================

async function loadTestimonios() {
    return await apiRequest('/testimonios');
}

// ==================== RESEÑAS ====================

async function loadResenas() {
    return await apiRequest('/resenas');
}

async function loadResenasStats() {
    return await apiRequest('/resenas/stats');
}

async function createResena(texto, calificacion) {
    return await apiRequest('/resenas', {
        method: 'POST',
        body: JSON.stringify({ texto, calificacion })
    });
}

async function loadAllResenas() {
    return await apiRequest('/admin/resenas');
}

async function updateResena(id, data) {
    return await apiRequest(`/admin/resenas/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

async function deleteResena(id) {
    return await apiRequest(`/admin/resenas/${id}`, {
        method: 'DELETE'
    });
}

// ==================== FAQs ====================

async function loadFaqs() {
    return await apiRequest('/faqs');
}

async function loadAllFaqs() {
    return await apiRequest('/admin/faqs');
}

async function createFaq(pregunta, respuesta) {
    return await apiRequest('/admin/faqs', {
        method: 'POST',
        body: JSON.stringify({ pregunta, respuesta })
    });
}

async function updateFaq(id, data) {
    return await apiRequest(`/admin/faqs/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

async function deleteFaq(id) {
    return await apiRequest(`/admin/faqs/${id}`, {
        method: 'DELETE'
    });
}

// ==================== ESTADÍSTICAS ====================

async function loadPublicStats() {
    return await apiRequest('/admin/stats');
}

// ==================== UI DINÁMICA ====================

function updateNav() {
    const navUser = document.getElementById('nav-user');
    if (!navUser) return;

    if (isLoggedIn()) {
        const user = getUsuario();
        navUser.innerHTML = `
            <span>Hola, ${user.nombre}</span>
            ${user.rol === 'admin'
                ? '<a href="/static/admin.html" class="btn btn-chico btn-secundario">Admin</a>'
                : '<a href="/static/dashboard.html" class="btn btn-chico btn-secundario">Mi Panel</a>'
            }
            <button onclick="logout()" class="btn btn-chico btn-peligro">Salir</button>
        `;
    } else {
        navUser.innerHTML = `
            <a href="/static/login.html" class="btn btn-chico btn-secundario">Iniciar Sesión</a>
            <a href="/static/register.html" class="btn btn-chico btn-primario">Registrarse</a>
        `;
    }
}

function updateAdminNav() {
    const path = window.location.pathname;
    const links = document.querySelectorAll('.sidebar-link');

    links.forEach(link => {
        const href = link.getAttribute('href');
        if (path.includes(href)) {
            link.classList.add('activo');
        }
    });
}

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', async () => {
    // Cargar configuración global
    await loadConfig();

    // Actualizar navegación
    updateNav();

    // Menu toggle para móvil
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('.nav');

    if (menuToggle && nav) {
        menuToggle.addEventListener('click', () => {
            nav.classList.toggle('active');
        });
    }
});

// ==================== EXPORTAR ====================
window.App = {
    initTheme,
    getTheme,
    toggleTheme,
    renderThemeButton,
    getToken,
    setToken,
    removeToken,
    getUsuario,
    setUsuario,
    removeUsuario,
    isLoggedIn,
    isAdmin,
    apiRequest,
    showAlert,
    formatFecha,
    formatPrecio,
    login,
    register,
    logout,
    checkAuth,
    loadConfig,
    applyConfig,
    loadServicios,
    loadAllServicios,
    createServicio,
    updateServicio,
    deleteServicio,
    loadMisTurnos,
    loadHorariosDisponibles,
    crearTurno,
    cancelarTurno,
    loadAllTurnos,
    cambiarEstadoTurno,
    loadAllUsuarios,
    updateUsuario,
    loadEstadisticas,
    updateConfig,
    loadTestimonios,
    updateNav,
    updateAdminNav,
    loadResenas,
    loadResenasStats,
    createResena,
    loadAllResenas,
    updateResena,
    deleteResena,
    loadAllFaqs,
    createFaq,
    updateFaq,
    deleteFaq
};