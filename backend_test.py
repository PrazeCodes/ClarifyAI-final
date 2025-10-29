import requests
import sys
import json
import io
from datetime import datetime
from pathlib import Path

class ClarifyAITester:
    def __init__(self, base_url="https://smart-clarify.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.token and 'Authorization' not in test_headers:
            test_headers['Authorization'] = f'Bearer {self.token}'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                if files:
                    # Remove Content-Type for multipart/form-data
                    if 'Content-Type' in test_headers:
                        del test_headers['Content-Type']
                    response = requests.post(url, data=data, files=files, headers=test_headers, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=test_headers, timeout=30)

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            
            if success:
                try:
                    response_data = response.json()
                    self.log_test(name, True, f"Status: {response.status_code}")
                    return True, response_data
                except:
                    self.log_test(name, True, f"Status: {response.status_code} (No JSON response)")
                    return True, {}
            else:
                try:
                    error_data = response.json()
                    self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}. Error: {error_data}")
                except:
                    self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}. Response: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            self.log_test(name, False, "Request timeout (30s)")
            return False, {}
        except Exception as e:
            self.log_test(name, False, f"Request error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_user_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_user_data = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "TestPass123!"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=test_user_data
        )
        
        if success and 'token' in response and 'user' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   Registered user: {response['user']['username']}")
            return True
        return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        # First register a user
        timestamp = datetime.now().strftime('%H%M%S')
        register_data = {
            "username": f"logintest_{timestamp}",
            "email": f"logintest_{timestamp}@example.com",
            "password": "LoginTest123!"
        }
        
        # Register user
        reg_success, reg_response = self.run_test(
            "User Registration for Login Test",
            "POST",
            "auth/register",
            200,
            data=register_data
        )
        
        if not reg_success:
            return False
        
        # Now test login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'token' in response and 'user' in response:
            print(f"   Logged in user: {response['user']['username']}")
            return True
        return False

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        invalid_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        success, response = self.run_test(
            "Invalid Login",
            "POST",
            "auth/login",
            401,
            data=invalid_data
        )
        return success

    def test_ask_ai_without_auth(self):
        """Test Ask AI endpoint without authentication"""
        # Temporarily remove token
        temp_token = self.token
        self.token = None
        
        success, response = self.run_test(
            "Ask AI Without Auth",
            "POST",
            "ask-ai",
            401,
            data={"question": "What is AI?"}
        )
        
        # Restore token
        self.token = temp_token
        return success

    def test_ask_ai_with_auth(self):
        """Test Ask AI endpoint with authentication"""
        if not self.token:
            print("❌ No authentication token available for Ask AI test")
            return False
        
        success, response = self.run_test(
            "Ask AI With Auth",
            "POST",
            "ask-ai",
            200,
            data={"question": "What is artificial intelligence?"}
        )
        
        if success and 'answer' in response:
            print(f"   AI Answer received (length: {len(response['answer'])} chars)")
            return True
        return False

    def test_chat_pdf_without_file(self):
        """Test Chat PDF endpoint without file"""
        if not self.token:
            print("❌ No authentication token available for Chat PDF test")
            return False
        
        success, response = self.run_test(
            "Chat PDF Without File",
            "POST",
            "chat-pdf",
            422,  # Unprocessable Entity for missing file
            data={"question": "What is this document about?"}
        )
        return success

    def test_chat_pdf_with_file(self):
        """Test Chat PDF endpoint with a sample PDF"""
        if not self.token:
            print("❌ No authentication token available for Chat PDF test")
            return False
        
        # Create a simple PDF content for testing
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000206 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n299\n%%EOF"
        
        files = {
            'pdf_file': ('test.pdf', io.BytesIO(pdf_content), 'application/pdf')
        }
        
        data = {
            'question': 'What does this document say?'
        }
        
        success, response = self.run_test(
            "Chat PDF With File",
            "POST",
            "chat-pdf",
            200,
            data=data,
            files=files
        )
        
        if success and 'answer' in response:
            print(f"   PDF Chat Answer received (length: {len(response['answer'])} chars)")
            return True
        return False

    def test_duplicate_registration(self):
        """Test duplicate user registration"""
        # Use the same email as the first registration
        if not hasattr(self, 'first_user_email'):
            # Create a user first
            timestamp = datetime.now().strftime('%H%M%S')
            self.first_user_email = f"duplicate_test_{timestamp}@example.com"
            
            first_user = {
                "username": f"firstuser_{timestamp}",
                "email": self.first_user_email,
                "password": "FirstUser123!"
            }
            
            success, response = self.run_test(
                "First User Registration",
                "POST",
                "auth/register",
                200,
                data=first_user
            )
            
            if not success:
                return False
        
        # Now try to register with same email
        duplicate_user = {
            "username": "duplicateuser",
            "email": self.first_user_email,
            "password": "DuplicateUser123!"
        }
        
        success, response = self.run_test(
            "Duplicate Email Registration",
            "POST",
            "auth/register",
            400,
            data=duplicate_user
        )
        return success

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting ClarifyAI Backend API Tests")
        print("=" * 50)
        
        # Basic API tests
        self.test_root_endpoint()
        
        # Authentication tests
        self.test_user_registration()
        self.test_user_login()
        self.test_invalid_login()
        self.test_duplicate_registration()
        
        # Protected endpoint tests
        self.test_ask_ai_without_auth()
        self.test_ask_ai_with_auth()
        
        # PDF processing tests
        self.test_chat_pdf_without_file()
        self.test_chat_pdf_with_file()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("❌ Some tests failed!")
            return 1

def main():
    tester = ClarifyAITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())