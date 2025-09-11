#!/usr/bin/env python3
"""
Playwright System Navigation Test
Tests the system compatibility and navigation without making changes
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from playwright.async_api import async_playwright, Page, Browser

class SystemNavigationTest:
    def __init__(self):
        self.base_url = "http://localhost:5173"  # Frontend dev server
        self.api_url = "http://localhost:8000"  # Backend API
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "navigation_tests": [],
            "compatibility_checks": [],
            "errors": []
        }
        
    async def check_frontend_availability(self, page: Page) -> bool:
        """Check if frontend is accessible"""
        try:
            response = await page.goto(self.base_url, wait_until="networkidle", timeout=10000)
            if response and response.status == 200:
                print("[OK] Frontend is accessible")
                return True
            else:
                print(f"[ERROR] Frontend returned status: {response.status if response else 'No response'}")
                return False
        except Exception as e:
            print(f"[ERROR] Frontend not accessible: {str(e)}")
            self.test_results["errors"].append({
                "test": "frontend_availability",
                "error": str(e)
            })
            return False
            
    async def check_api_availability(self, page: Page) -> bool:
        """Check if API is accessible"""
        try:
            response = await page.request.get(f"{self.api_url}/docs")
            if response.status == 200:
                print("[OK] API docs are accessible")
                return True
            else:
                print(f"[ERROR] API returned status: {response.status}")
                return False
        except Exception as e:
            print(f"[ERROR] API not accessible: {str(e)}")
            self.test_results["errors"].append({
                "test": "api_availability",
                "error": str(e)
            })
            return False
            
    async def test_login_page(self, page: Page) -> Dict[str, Any]:
        """Test login page elements"""
        result = {
            "test": "login_page",
            "passed": False,
            "elements_found": {},
            "issues": []
        }
        
        try:
            # Navigate to login
            await page.goto(f"{self.base_url}/login", wait_until="networkidle", timeout=10000)
            
            # Check for CPF input
            cpf_input = await page.query_selector('input[name="cpf"], input[id="cpf"], input[placeholder*="CPF"]')
            result["elements_found"]["cpf_input"] = cpf_input is not None
            
            # Check for password input
            password_input = await page.query_selector('input[type="password"], input[name="senha"], input[name="password"]')
            result["elements_found"]["password_input"] = password_input is not None
            
            # Check for submit button
            submit_button = await page.query_selector('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")')
            result["elements_found"]["submit_button"] = submit_button is not None
            
            # Check if all elements are present
            result["passed"] = all(result["elements_found"].values())
            
            if not result["passed"]:
                missing = [k for k, v in result["elements_found"].items() if not v]
                result["issues"].append(f"Missing elements: {', '.join(missing)}")
                
            print(f"[TEST] Login page: {'PASSED' if result['passed'] else 'FAILED'}")
            
        except Exception as e:
            result["issues"].append(str(e))
            print(f"[ERROR] Login page test failed: {str(e)}")
            
        return result
        
    async def test_navigation_routes(self, page: Page) -> List[Dict[str, Any]]:
        """Test main navigation routes"""
        routes = [
            "/",
            "/login",
            "/dashboard",
            "/eventos",
            "/usuarios",
            "/produtos",
            "/pdv",
            "/checkin",
            "/financeiro",
            "/ranking"
        ]
        
        results = []
        
        for route in routes:
            result = {
                "route": route,
                "accessible": False,
                "status_code": None,
                "has_content": False
            }
            
            try:
                response = await page.goto(f"{self.base_url}{route}", wait_until="domcontentloaded", timeout=5000)
                
                if response:
                    result["status_code"] = response.status
                    result["accessible"] = response.status < 400
                    
                    # Check if page has content
                    content = await page.content()
                    result["has_content"] = len(content) > 500
                    
                print(f"[ROUTE] {route}: {result['status_code']} - {'OK' if result['accessible'] else 'FAIL'}")
                
            except Exception as e:
                result["error"] = str(e)
                print(f"[ERROR] Route {route}: {str(e)}")
                
            results.append(result)
            
        return results
        
    async def check_responsive_design(self, page: Page) -> Dict[str, Any]:
        """Check responsive design compatibility"""
        viewports = [
            {"name": "mobile", "width": 375, "height": 667},
            {"name": "tablet", "width": 768, "height": 1024},
            {"name": "desktop", "width": 1920, "height": 1080}
        ]
        
        results = {}
        
        for viewport in viewports:
            await page.set_viewport_size(width=viewport["width"], height=viewport["height"])
            await page.goto(self.base_url, wait_until="networkidle", timeout=10000)
            
            # Check if content is visible
            body = await page.query_selector("body")
            is_visible = await body.is_visible() if body else False
            
            results[viewport["name"]] = {
                "width": viewport["width"],
                "height": viewport["height"],
                "content_visible": is_visible
            }
            
            print(f"[RESPONSIVE] {viewport['name']}: {'OK' if is_visible else 'FAIL'}")
            
        return results
        
    async def check_browser_compatibility(self) -> List[Dict[str, Any]]:
        """Test with different browser engines"""
        browsers = ["chromium", "firefox", "webkit"]
        results = []
        
        async with async_playwright() as p:
            for browser_name in browsers:
                result = {
                    "browser": browser_name,
                    "compatible": False,
                    "issues": []
                }
                
                try:
                    # Launch browser
                    if browser_name == "chromium":
                        browser = await p.chromium.launch(headless=True)
                    elif browser_name == "firefox":
                        browser = await p.firefox.launch(headless=True)
                    else:  # webkit
                        browser = await p.webkit.launch(headless=True)
                        
                    page = await browser.new_page()
                    
                    # Try to load the page
                    response = await page.goto(self.base_url, wait_until="networkidle", timeout=10000)
                    
                    if response and response.status == 200:
                        result["compatible"] = True
                        
                    await browser.close()
                    
                    print(f"[BROWSER] {browser_name}: {'OK' if result['compatible'] else 'FAIL'}")
                    
                except Exception as e:
                    result["issues"].append(str(e))
                    print(f"[ERROR] Browser {browser_name}: {str(e)}")
                    
                results.append(result)
                
        return results
        
    async def run_all_tests(self):
        """Run all navigation and compatibility tests"""
        print("\n" + "="*60)
        print(" PLAYWRIGHT SYSTEM NAVIGATION TEST")
        print("="*60)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # 1. Check frontend availability
            print("\n[1/6] Checking frontend availability...")
            frontend_ok = await self.check_frontend_availability(page)
            self.test_results["compatibility_checks"].append({
                "test": "frontend_availability",
                "passed": frontend_ok
            })
            
            if not frontend_ok:
                print("[WARNING] Frontend not available, skipping navigation tests")
            else:
                # 2. Test login page
                print("\n[2/6] Testing login page...")
                login_result = await self.test_login_page(page)
                self.test_results["navigation_tests"].append(login_result)
                
                # 3. Test navigation routes
                print("\n[3/6] Testing navigation routes...")
                routes_results = await self.test_navigation_routes(page)
                self.test_results["navigation_tests"].extend(routes_results)
                
                # 4. Check responsive design
                print("\n[4/6] Checking responsive design...")
                responsive_results = await self.check_responsive_design(page)
                self.test_results["compatibility_checks"].append({
                    "test": "responsive_design",
                    "results": responsive_results
                })
            
            # 5. Check API availability
            print("\n[5/6] Checking API availability...")
            api_ok = await self.check_api_availability(page)
            self.test_results["compatibility_checks"].append({
                "test": "api_availability",
                "passed": api_ok
            })
            
            await browser.close()
            
        # 6. Check browser compatibility
        print("\n[6/6] Checking browser compatibility...")
        browser_results = await self.check_browser_compatibility()
        self.test_results["compatibility_checks"].append({
            "test": "browser_compatibility",
            "results": browser_results
        })
        
        # Save results
        self.save_results()
        self.print_summary()
        
    def save_results(self):
        """Save test results to JSON file"""
        results_file = Path("playwright_test_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n[OK] Results saved to: {results_file}")
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print(" TEST SUMMARY")
        print("="*60)
        
        # Count passed/failed
        nav_passed = sum(1 for t in self.test_results["navigation_tests"] 
                        if t.get("passed") or t.get("accessible"))
        nav_total = len(self.test_results["navigation_tests"])
        
        compat_passed = sum(1 for t in self.test_results["compatibility_checks"] 
                          if t.get("passed"))
        compat_total = len(self.test_results["compatibility_checks"])
        
        print(f"\nNavigation Tests: {nav_passed}/{nav_total} passed")
        print(f"Compatibility Tests: {compat_passed}/{compat_total} passed")
        print(f"Total Errors: {len(self.test_results['errors'])}")
        
        if self.test_results["errors"]:
            print("\n[ERRORS]:")
            for error in self.test_results["errors"]:
                print(f"  - {error['test']}: {error['error']}")
                
        print("\n" + "="*60)
        
async def main():
    """Main function"""
    tester = SystemNavigationTest()
    await tester.run_all_tests()
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")