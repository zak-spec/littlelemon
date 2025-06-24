#!/usr/bin/env python3
"""
Test script para verificar la migración a ViewSets en Little Lemon API
Este script prueba todos los endpoints principales de la nueva API basada en ViewSets.
"""

import requests
import json
import time
from datetime import datetime

# Configuración base
BASE_URL = "http://localhost:8000/api"
USERNAME = "testuser_viewsets"
EMAIL = "testviewsets@example.com"
PASSWORD = "testpassword123!"

# Headers para las peticiones
headers = {
    'Content-Type': 'application/json',
}

class LittleLemonAPITester:
    def __init__(self):
        self.token = None
        self.headers = headers.copy()
        self.test_results = []
        
    def log_test(self, test_name, success, message="", response_data=None):
        """Log de resultados de test"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = f"[{timestamp}] {status} - {test_name}"
        if message:
            result += f": {message}"
        
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': timestamp,
            'response_data': response_data
        })
        
    def make_request(self, method, endpoint, data=None, expected_status=None):
        """Hacer petición HTTP con manejo de errores"""
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=10)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, timeout=10)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data, timeout=10)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers, timeout=10)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
                
            if expected_status and response.status_code != expected_status:
                return None, f"Status code esperado {expected_status}, recibido {response.status_code}"
                
            return response, None
            
        except requests.exceptions.ConnectionError:
            return None, "Error de conexión - ¿Está el servidor ejecutándose en localhost:8000?"
        except requests.exceptions.Timeout:
            return None, "Timeout en la petición"
        except Exception as e:
            return None, f"Error inesperado: {str(e)}"
    
    def test_server_status(self):
        """Test 1: Verificar que el servidor está ejecutándose"""
        print("\n" + "="*50)
        print("INICIANDO TESTS DE MIGRACIÓN A VIEWSETS")
        print("="*50)
        
        response, error = self.make_request('GET', '/')
        if error:
            self.log_test("Server Status", False, error)
            return False
        
        self.log_test("Server Status", True, f"Servidor responde con status {response.status_code}")
        return True
    
    def test_user_registration(self):
        """Test 2: Registro de usuario"""
        user_data = {
            'username': USERNAME,
            'email': EMAIL,
            'password': PASSWORD
        }
        
        response, error = self.make_request('POST', '/register/', user_data)
        if error:
            self.log_test("User Registration", False, error)
            return False
            
        if response.status_code in [201, 400]:  # 400 si ya existe
            self.log_test("User Registration", True, f"Status: {response.status_code}")
            return True
        else:
            self.log_test("User Registration", False, f"Status inesperado: {response.status_code}")
            return False
    
    def test_authentication(self):
        """Test 3: Autenticación"""
        auth_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        response, error = self.make_request('POST', '/token-auth/', auth_data)
        if error:
            self.log_test("Authentication", False, error)
            return False
            
        if response.status_code == 200:
            try:
                data = response.json()
                self.token = data.get('token')
                if self.token:
                    self.headers['Authorization'] = f'Token {self.token}'
                    self.log_test("Authentication", True, "Token obtenido correctamente")
                    return True
                else:
                    self.log_test("Authentication", False, "No se encontró token en la respuesta")
                    return False
            except json.JSONDecodeError:
                self.log_test("Authentication", False, "Respuesta no es JSON válido")
                return False
        else:
            self.log_test("Authentication", False, f"Status: {response.status_code}")
            return False
    
    def test_categories_viewset(self):
        """Test 4: Categories ViewSet"""
        print("\n--- Testing Categories ViewSet ---")
        
        # Test GET categories
        response, error = self.make_request('GET', '/categories/')
        if error:
            self.log_test("Categories List", False, error)
        else:
            self.log_test("Categories List", response.status_code == 200, 
                         f"Status: {response.status_code}")
        
        # Test POST category (requiere permisos)
        category_data = {'title': 'Test Category ViewSet'}
        response, error = self.make_request('POST', '/categories/', category_data)
        if error:
            self.log_test("Categories Create", False, error)
        else:
            success = response.status_code in [201, 403]  # 403 si no tiene permisos
            self.log_test("Categories Create", success, 
                         f"Status: {response.status_code} (403 esperado sin permisos manager)")
    
    def test_menu_items_viewset(self):
        """Test 5: Menu Items ViewSet"""
        print("\n--- Testing Menu Items ViewSet ---")
        
        # Test GET menu items
        response, error = self.make_request('GET', '/menu-items/')
        if error:
            self.log_test("Menu Items List", False, error)
        else:
            self.log_test("Menu Items List", response.status_code == 200, 
                         f"Status: {response.status_code}")
        
        # Test filtros
        response, error = self.make_request('GET', '/menu-items/?page=1&page_size=5')
        if error:
            self.log_test("Menu Items Pagination", False, error)
        else:
            self.log_test("Menu Items Pagination", response.status_code == 200,
                         f"Status: {response.status_code}")
    
    def test_cart_viewset(self):
        """Test 6: Cart ViewSet"""
        print("\n--- Testing Cart ViewSet ---")
        
        # Test GET cart
        response, error = self.make_request('GET', '/cart/')
        if error:
            self.log_test("Cart View", False, error)
        else:
            self.log_test("Cart View", response.status_code == 200,
                         f"Status: {response.status_code}")
        
        # Test clear cart action
        response, error = self.make_request('DELETE', '/cart/clear/')
        if error:
            self.log_test("Cart Clear", False, error)
        else:
            self.log_test("Cart Clear", response.status_code == 200,
                         f"Status: {response.status_code}")
    
    def test_orders_viewset(self):
        """Test 7: Orders ViewSet"""
        print("\n--- Testing Orders ViewSet ---")
        
        # Test GET orders
        response, error = self.make_request('GET', '/orders/')
        if error:
            self.log_test("Orders List", False, error)
        else:
            self.log_test("Orders List", response.status_code == 200,
                         f"Status: {response.status_code}")
    
    def test_users_viewset(self):
        """Test 8: Users ViewSet"""
        print("\n--- Testing Users ViewSet ---")
        
        # Test GET current user info
        response, error = self.make_request('GET', '/users/me/')
        if error:
            self.log_test("Users Me", False, error)
        else:
            self.log_test("Users Me", response.status_code == 200,
                         f"Status: {response.status_code}")
    
    def test_utility_viewset(self):
        """Test 9: Utility ViewSet"""
        print("\n--- Testing Utility ViewSet ---")
        
        # Test throttle check authenticated
        response, error = self.make_request('GET', '/utils/throttle_check_auth/')
        if error:
            self.log_test("Utils Throttle Auth", False, error)
        else:
            self.log_test("Utils Throttle Auth", response.status_code == 200,
                         f"Status: {response.status_code}")
        
        # Test secret endpoint
        response, error = self.make_request('GET', '/utils/secret/')
        if error:
            self.log_test("Utils Secret", False, error)
        else:
            self.log_test("Utils Secret", response.status_code == 200,
                         f"Status: {response.status_code}")
    
    def test_permissions_and_filtering(self):
        """Test 10: Verificar permisos y filtros"""
        print("\n--- Testing Permissions & Filtering ---")
        
        # Test filtros en menu items
        test_filters = [
            '/menu-items/?search=test',
            '/menu-items/?ordering=title',
            '/menu-items/?page_size=3',
        ]
        
        for filter_url in test_filters:
            response, error = self.make_request('GET', filter_url)
            if error:
                self.log_test(f"Filter {filter_url}", False, error)
            else:
                self.log_test(f"Filter {filter_url}", response.status_code == 200,
                             f"Status: {response.status_code}")
    
    def run_all_tests(self):
        """Ejecutar todos los tests"""
        print("Little Lemon API - Test de Migración a ViewSets")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Tests secuenciales
        tests = [
            self.test_server_status,
            self.test_user_registration,
            self.test_authentication,
            self.test_categories_viewset,
            self.test_menu_items_viewset,
            self.test_cart_viewset,
            self.test_orders_viewset,
            self.test_users_viewset,
            self.test_utility_viewset,
            self.test_permissions_and_filtering,
        ]
        
        for test_func in tests:
            try:
                test_func()
                time.sleep(0.5)  # Pequeña pausa entre tests
            except Exception as e:
                self.log_test(test_func.__name__, False, f"Error inesperado: {str(e)}")
        
        self.print_summary()
    
    def print_summary(self):
        """Imprimir resumen de tests"""
        print("\n" + "="*50)
        print("RESUMEN DE TESTS")
        print("="*50)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Tests ejecutados: {total}")
        print(f"Tests exitosos: {passed}")
        print(f"Tests fallidos: {total - passed}")
        print(f"Tasa de éxito: {(passed/total*100):.1f}%")
        
        if total - passed > 0:
            print("\nTests fallidos:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "="*50)
        if passed == total:
            print("🎉 ¡TODOS LOS TESTS PASARON! La migración a ViewSets fue exitosa.")
        elif passed > total * 0.8:
            print("⚠️  La mayoría de tests pasaron. Revisar tests fallidos.")
        else:
            print("❌ Muchos tests fallaron. Revisar configuración y código.")
        print("="*50)

if __name__ == "__main__":
    print("🚀 Iniciando tests de migración a ViewSets...")
    print("📋 Asegúrate de que el servidor Django esté ejecutándose en localhost:8000")
    print("⏱️  Los tests comenzarán en 3 segundos...")
    
    time.sleep(3)
    
    tester = LittleLemonAPITester()
    tester.run_all_tests()
