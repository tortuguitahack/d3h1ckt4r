import requests
import sys
import json
from datetime import datetime

class TambarExpressAPITester:
    def __init__(self, base_url="https://liquor-system.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_product_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    return success, response_data
                except:
                    print(f"   Response: {response.text[:200]}...")
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API", "GET", "", 200)

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        success, response = self.run_test("Dashboard Stats", "GET", "dashboard/stats", 200)
        if success:
            required_fields = ['total_products', 'low_stock_alerts', 'total_orders', 'pending_orders', 
                             'today_sales', 'monthly_sales', 'total_customers', 'whatsapp_messages']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing field in dashboard stats: {field}")
                    return False
            print("✅ All required dashboard fields present")
        return success

    def test_get_products(self):
        """Test getting products list"""
        success, response = self.run_test("Get Products", "GET", "products", 200)
        if success and isinstance(response, list):
            print(f"✅ Found {len(response)} products")
            if len(response) > 0:
                product = response[0]
                required_fields = ['id', 'name', 'cost_price', 'sale_price', 'stock', 'category']
                for field in required_fields:
                    if field not in product:
                        print(f"❌ Missing field in product: {field}")
                        return False
                print("✅ Product structure is correct")
        return success

    def test_create_product(self):
        """Test creating a new product"""
        test_product = {
            "name": "Test Cerveza Pilsener",
            "description": "Cerveza de prueba para testing",
            "cost_price": 8.0,
            "sale_price": 12.0,
            "stock": 50,
            "min_stock": 10,
            "supplier": "Proveedor Test",
            "category": "cervezas"
        }
        
        success, response = self.run_test("Create Product", "POST", "products", 200, data=test_product)
        if success and 'id' in response:
            self.created_product_id = response['id']
            print(f"✅ Product created with ID: {self.created_product_id}")
            
            # Verify margin calculation
            expected_margin = ((12.0 - 8.0) / 8.0) * 100  # 50%
            if abs(response.get('margin', 0) - expected_margin) < 0.1:
                print("✅ Margin calculation is correct")
            else:
                print(f"❌ Margin calculation incorrect. Expected: {expected_margin}, Got: {response.get('margin')}")
        return success

    def test_low_stock_products(self):
        """Test getting low stock products"""
        return self.run_test("Low Stock Products", "GET", "products/low-stock", 200)

    def test_get_customers(self):
        """Test getting customers list"""
        return self.run_test("Get Customers", "GET", "customers", 200)

    def test_create_customer(self):
        """Test creating a new customer"""
        test_customer = {
            "name": "Cliente Test",
            "phone": "59170000001",
            "email": "test@example.com",
            "address": "La Paz, Bolivia"
        }
        
        return self.run_test("Create Customer", "POST", "customers", 200, data=test_customer)

    def test_get_orders(self):
        """Test getting orders list"""
        return self.run_test("Get Orders", "GET", "orders", 200)

    def test_whatsapp_messages(self):
        """Test getting WhatsApp messages"""
        return self.run_test("WhatsApp Messages", "GET", "whatsapp/messages", 200)

    def test_whatsapp_process_menu(self):
        """Test WhatsApp menu command processing"""
        return self.run_test(
            "WhatsApp Process Menu", 
            "POST", 
            "whatsapp/process", 
            200,
            params={"phone": "59170000000", "message": "/menu"}
        )

    def test_whatsapp_process_stock(self):
        """Test WhatsApp stock command processing"""
        return self.run_test(
            "WhatsApp Process Stock", 
            "POST", 
            "whatsapp/process", 
            200,
            params={"phone": "59170000000", "message": "/stock Cerveza"}
        )

    def test_whatsapp_process_report(self):
        """Test WhatsApp report command processing"""
        return self.run_test(
            "WhatsApp Process Report", 
            "POST", 
            "whatsapp/process", 
            200,
            params={"phone": "59170000000", "message": "/reporte ventas"}
        )

    def test_social_media_posts(self):
        """Test getting social media posts"""
        return self.run_test("Social Media Posts", "GET", "social-media/posts", 200)

    def test_create_facebook_ad(self):
        """Test creating Facebook ad"""
        return self.run_test(
            "Create Facebook Ad", 
            "POST", 
            "social-media/create-ad", 
            200,
            params={"platform": "facebook"}
        )

    def test_create_instagram_ad(self):
        """Test creating Instagram ad"""
        return self.run_test(
            "Create Instagram Ad", 
            "POST", 
            "social-media/create-ad", 
            200,
            params={"platform": "instagram"}
        )

    def test_create_product_specific_ad(self):
        """Test creating product-specific ad"""
        if self.created_product_id:
            return self.run_test(
                "Create Product Ad", 
                "POST", 
                "social-media/create-ad", 
                200,
                params={"platform": "tiktok", "product_id": self.created_product_id}
            )
        else:
            print("⚠️  Skipping product-specific ad test - no product ID available")
            return True

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Tambar Express API Tests")
        print("=" * 50)

        # Basic API tests
        self.test_root_endpoint()
        
        # Dashboard tests
        self.test_dashboard_stats()
        
        # Product management tests
        self.test_get_products()
        self.test_create_product()
        self.test_low_stock_products()
        
        # Customer management tests
        self.test_get_customers()
        self.test_create_customer()
        
        # Order management tests
        self.test_get_orders()
        
        # WhatsApp Business tests
        self.test_whatsapp_messages()
        self.test_whatsapp_process_menu()
        self.test_whatsapp_process_stock()
        self.test_whatsapp_process_report()
        
        # Social Media Marketing tests
        self.test_social_media_posts()
        self.test_create_facebook_ad()
        self.test_create_instagram_ad()
        self.test_create_product_specific_ad()

        # Print final results
        print("\n" + "=" * 50)
        print(f"📊 FINAL RESULTS")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
            return 0
        else:
            print("❌ SOME TESTS FAILED")
            return 1

def main():
    tester = TambarExpressAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())