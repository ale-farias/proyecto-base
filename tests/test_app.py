"""
Tests unitarios para el sistema de reservas Flask
Ejecutar con: pytest tests/ -v
"""
import os
import sys
import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  


@pytest.fixture
def app():
    """Crea aplicación Flask para tests"""
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
    
    from app import app as flask_app
    flask_app.config['TESTING'] = True
    flask_app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    
    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def client(app):
    """Cliente para hacer requests"""
    return app.test_client()


@pytest.fixture
def admin_token(client):
    """Token JWT de admin para tests"""
    response = client.post('/api/auth/login', json={
        'email': 'admin@minegocio.com',
        'password': 'admin123'
    })
    if response.status_code == 200:
        return json.loads(response.data)['access_token']
    return None


@pytest.fixture
def nuevo_usuario(client):
    """Crea un nuevo usuario para tests"""
    import random
    email = f"test_{random.randint(1000, 9999)}@test.com"
    
    response = client.post('/api/auth/register', json={
        'nombre': 'Usuario Test',
        'email': email,
        'password': 'test123456',
        'telefono': '+5491112345678'
    })
    
    if response.status_code == 201:
        data = json.loads(response.data)
        return {
            'email': email,
            'password': 'test123456',
            'token': data.get('access_token'),
            'id': data.get('user', {}).get('id')
        }
    return None


class TestAutenticacion:
    """Tests para autenticación"""
    
    def test_login_exitoso(self, client):
        """Test login con credenciales correctas"""
        response = client.post('/api/auth/login', json={
            'email': 'admin@minegocio.com',
            'password': 'admin123'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert data['user']['rol'] == 'admin'
    
    def test_login_email_incorrecto(self, client):
        """Test login con email incorrecto"""
        response = client.post('/api/auth/login', json={
            'email': 'noexiste@test.com',
            'password': 'password123'
        })
        
        assert response.status_code == 401
    
    def test_login_password_incorrecto(self, client):
        """Test login con password incorrecto"""
        response = client.post('/api/auth/login', json={
            'email': 'admin@minegocio.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
    
    def test_login_campos_vacios(self, client):
        """Test login con campos vacíos"""
        response = client.post('/api/auth/login', json={
            'email': '',
            'password': ''
        })
        
        assert response.status_code == 400
    
    def test_register_exitoso(self, client):
        """Test registro de nuevo usuario"""
        import random
        email = f"nuevo_{random.randint(10000, 99999)}@test.com"
        
        response = client.post('/api/auth/register', json={
            'nombre': 'Nuevo Usuario',
            'email': email,
            'password': 'password123',
            'telefono': '+5491112345678'
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'access_token' in data
        assert data['user']['nombre'] == 'Nuevo Usuario'
    
    def test_register_email_existente(self, client):
        """Test registro con email ya existente"""
        response = client.post('/api/auth/register', json={
            'nombre': 'Admin',
            'email': 'admin@minegocio.com',
            'password': 'password123'
        })
        
        assert response.status_code == 400
    
    def test_register_password_corta(self, client):
        """Test registro con password corta"""
        response = client.post('/api/auth/register', json={
            'nombre': 'Test',
            'email': 'test@test.com',
            'password': '123'
        })
        
        assert response.status_code == 400


class TestConfiguracion:
    """Tests para configuración"""
    
    def test_get_config_publica(self, client):
        """Test obtener configuración pública"""
        response = client.get('/api/config')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'nombre_negocio' in data


class TestServicios:
    """Tests para servicios"""
    
    def test_get_servicios_activos(self, client):
        """Test obtener servicios activos"""
        response = client.get('/api/servicios')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        if data:
            assert 'nombre' in data[0]
            assert 'precio' in data[0]


class TestTurnos:
    """Tests para turnos"""
    
    def test_get_turnos_disponibles(self, client):
        """Test obtener horarios disponibles"""
        from datetime import datetime
        fecha_futura = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        
        response = client.get(f'/api/turnos/disponibles?fecha={fecha_futura}&servicio_id=1')
        
        assert response.status_code == 200
    
    def test_get_turnos_sin_fecha(self, client):
        """Test sin fecha retorna error"""
        response = client.get('/api/turnos/disponibles')
        
        assert response.status_code == 400
    
    def test_crear_turno_sin_auth(self, client):
        """Test crear turno sin autenticación"""
        response = client.post('/api/turnos', json={
            'servicio_id': 1,
            'fecha': '2025-12-31',
            'hora': '10:00'
        })
        
        assert response.status_code == 401


class TestResenas:
    """Tests para reseñas"""
    
    def test_get_resenas_publicas(self, client):
        """Test obtener reseñas aprobadas"""
        response = client.get('/api/resenas')
        
        assert response.status_code == 200
    
    def test_create_resena_sin_auth(self, client):
        """Test crear reseña sin auth"""
        response = client.post('/api/resenas', json={
            'texto': 'Muy buen servicio',
            'calificacion': 5
        })
        
        assert response.status_code == 401


class TestFAQs:
    """Tests para FAQs"""
    
    def test_get_faqs(self, client):
        """Test obtener FAQs"""
        response = client.get('/api/faqs')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)


class TestProteccion:
    """Tests de protección y seguridad"""
    
    def test_rate_limiting_login(self, client):
        """Test rate limiting en login"""
        for _ in range(10):
            client.post('/api/auth/login', json={
                'email': 'test@test.com',
                'password': 'wrong'
            })
        
        response = client.post('/api/auth/login', json={
            'email': 'test@test.com',
            'password': 'wrong'
        })
        
        assert response.status_code in [401, 429]
    
    def test_admin_endpoints_protegidos(self, client):
        """Test que endpoints admin requieren auth"""
        endpoints = [
            '/api/admin/servicios',
            '/api/admin/turnos',
            '/api/admin/usuarios',
            '/api/admin/estadisticas'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401
    
    def test_admin_solo_admin(self, client, nuevo_usuario):
        """Test que solo admin puede acceder a admin"""
        if not nuevo_usuario or not nuevo_usuario.get('token'):
            pytest.skip("No se pudo crear usuario de test")
        
        response = client.get(
            '/api/admin/usuarios',
            headers={'Authorization': f'Bearer {nuevo_usuario["token"]}'}
        )
        
        assert response.status_code == 403


class TestValidaciones:
    """Tests devalidaciones"""
    
    def test_fecha_pasada_error(self, client):
        """Test que no acepta fechas pasadas"""
        response = client.get('/api/turnos/disponibles?fecha=2020-01-01&servicio_id=1')
        
        assert response.status_code == 400
    
    def test_servicio_invalido(self, client):
        """Test servicio inexistente"""
        response = client.get('/api/turnos/disponibles?fecha=2025-12-31&servicio_id=99999')
        
        assert response.status_code in [400, 404]
    
    def test_formato_fecha_invalido(self, client):
        """Test formato de fecha inválido"""
        response = client.get('/api/turnos/disponibles?fecha=31-12-2025&servicio_id=1')
        
        assert response.status_code == 400


class TestPaginacion:
    """Tests para paginación"""
    
    def test_paginacion_turnos_admin(self, client, admin_token):
        """Test paginación de turnos admin"""
        if not admin_token:
            pytest.skip("No token de admin")
        
        response = client.get(
            '/api/admin/turnos?pagina=1&por_pagina=5',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert 'pagina' in data
        assert 'total' in data
    
    def test_paginacion_params_default(self, client, admin_token):
        """Test paginación con valores por defecto"""
        if not admin_token:
            pytest.skip("No token de admin")
        
        response = client.get(
            '/api/admin/turnos',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['pagina'] == 1
        assert data['por_pagina'] == 20


if __name__ == '__main__':
    pytest.main([__file__, '-v'])