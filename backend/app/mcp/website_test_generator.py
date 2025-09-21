import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup, Tag
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class WebsiteAnalysis:
    url: str
    title: str
    forms: List[Dict[str, Any]]
    links: List[Dict[str, str]]
    buttons: List[str]
    inputs: List[Dict[str, str]]
    navigation: List[str]
    features: List[str]
    page_type: str

class WebsiteTestCaseGenerator:
    """MCP Server for generating test cases from website URLs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })
    
    def _get_website_content(self, url: str, retry_attempt: int = 0) -> str:
        """Get website content with retry logic"""
        try:
            # Increase timeout on retry
            timeout = 15 if retry_attempt == 0 else 30
            
            logger.info(f"Attempting to access {url} (attempt {retry_attempt + 1}/2)")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.content.decode('utf-8')
        except requests.exceptions.RequestException as e:
            if retry_attempt == 0:
                logger.warning(f"First attempt to access {url} failed. Retrying with increased timeout...")
                return self._get_website_content(url, retry_attempt=1)
            else:
                raise e
    
    async def analyze_website(self, url: str) -> WebsiteAnalysis:
        """Analyze website structure and identify testable elements"""
        try:
            # Validate URL format
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL format: {url}. URL must start with http:// or https://")
            
            # Get website content with retry logic
            content = self._get_website_content(url)
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract basic info
            title = soup.find('title')
            title_text = title.text.strip() if title else "Unknown Page"
            
            # Find forms and their inputs
            forms = []
            for form in soup.find_all('form'):
                # Ensure we're working with a Tag object that has the get method
                if isinstance(form, Tag):
                    form_data = {
                        'action': form.get('action', ''),
                        'method': str(form.get('method', 'get') or 'get').lower(),
                        'inputs': []
                    }
                    
                    for inp in form.find_all(['input', 'select', 'textarea']):
                        if isinstance(inp, Tag):
                            input_data = {
                                'type': inp.get('type', 'text'),
                                'name': inp.get('name', ''),
                                'placeholder': inp.get('placeholder', ''),
                                'required': inp.has_attr('required')
                            }
                            form_data['inputs'].append(input_data)
                    
                    forms.append(form_data)
            
            # Find navigation elements
            nav_elements = []
            for nav in soup.find_all(['nav', 'ul', 'ol']):
                if isinstance(nav, Tag):
                    for link in nav.find_all('a'):
                        if isinstance(link, Tag):
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            if text and href:
                                nav_elements.append(text)
            
            # Find buttons
            buttons = []
            for button in soup.find_all(['button', 'input']):
                if isinstance(button, Tag):
                    if button.name == 'input' and button.get('type') not in ['button', 'submit']:
                        continue
                    text = button.get_text(strip=True) or button.get('value', '')
                    if text:
                        buttons.append(text)
            
            # Find all links
            links = []
            for link in soup.find_all('a', href=True):
                if isinstance(link, Tag):
                    links.append({
                        'text': link.get_text(strip=True),
                        'href': link.get('href', '')
                    })
            
            # Find input fields
            inputs = []
            for inp in soup.find_all('input'):
                if isinstance(inp, Tag):
                    inputs.append({
                        'type': inp.get('type', 'text'),
                        'name': inp.get('name', ''),
                        'placeholder': inp.get('placeholder', ''),
                        'id': inp.get('id', '')
                    })
            
            # Determine page type and features
            page_type = self._determine_page_type(soup, url, title_text)
            features = self._identify_features(soup, forms, buttons, links)
            
            return WebsiteAnalysis(
                url=url,
                title=title_text,
                forms=forms,
                links=links[:20],  # Limit links
                buttons=buttons[:10],  # Limit buttons
                inputs=inputs[:15],  # Limit inputs
                navigation=nav_elements[:10],
                features=features,
                page_type=page_type
            )
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error accessing website {url}: {str(e)}"
            logger.error(error_msg)
            if 'ConnectionError' in str(e.__class__.__name__):
                error_msg = f"Could not connect to {url}. Please check the URL and try again."
            elif 'Timeout' in str(e.__class__.__name__):
                error_msg = f"Connection to {url} timed out. The website might be slow or unavailable."
            elif 'TooManyRedirects' in str(e.__class__.__name__):
                error_msg = f"Too many redirects while trying to access {url}."
            elif hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 403:
                    error_msg = f"Access to {url} was forbidden (403). The website may block automated access."
                elif e.response.status_code == 404:
                    error_msg = f"The page at {url} was not found (404)."
                else:
                    error_msg = f"HTTP error {e.response.status_code} while accessing {url}."
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error analyzing website {url}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _determine_page_type(self, soup: BeautifulSoup, url: str, title: str) -> str:
        """Determine the type of webpage"""
        url_lower = url.lower()
        title_lower = title.lower()
        text_content = soup.get_text().lower()
        
        # Check for specific page types
        if any(keyword in url_lower or keyword in title_lower for keyword in ['login', 'signin', 'auth']):
            return 'login'
        elif any(keyword in url_lower or keyword in title_lower for keyword in ['register', 'signup', 'join']):
            return 'registration'
        elif any(keyword in url_lower or keyword in title_lower for keyword in ['shop', 'store', 'product', 'cart']):
            return 'ecommerce'
        elif any(keyword in text_content for keyword in ['dashboard', 'admin', 'profile']):
            return 'dashboard'
        elif soup.find_all('form'):
            return 'form'
        else:
            return 'general'
    
    def _identify_features(self, soup: BeautifulSoup, forms: List, buttons: List, links: List) -> List[str]:
        """Identify testable features on the page"""
        features = []
        text_content = soup.get_text().lower()
        
        # Authentication features
        if any('password' in str(form).lower() for form in forms):
            features.append('user_authentication')
        
        # Shopping features
        if any(keyword in text_content for keyword in ['cart', 'add to cart', 'buy', 'purchase']):
            features.append('shopping_cart')
        
        # Search functionality
        if any('search' in str(form).lower() for form in forms):
            features.append('search')
        
        # Navigation
        if len(links) > 5:
            features.append('navigation')
        
        # Form submission
        if forms:
            features.append('form_submission')
        
        return features
    
    async def generate_test_cases_from_url(self, url: str, project_id: str, test_count: int = 5) -> List[Dict[str, Any]]:
        """Generate test cases based on website analysis"""
        try:
            analysis = await self.analyze_website(url)
            
            # Generate test cases based on analysis
            test_cases = []
            
            # Login test cases
            if analysis.page_type == 'login' or 'user_authentication' in analysis.features:
                test_cases.extend(self._generate_login_tests(analysis))
            
            # E-commerce test cases
            if analysis.page_type == 'ecommerce' or 'shopping_cart' in analysis.features:
                test_cases.extend(self._generate_ecommerce_tests(analysis))
            
            # Form validation tests
            if analysis.forms:
                test_cases.extend(self._generate_form_tests(analysis))
            
            # Navigation tests
            if 'navigation' in analysis.features:
                test_cases.extend(self._generate_navigation_tests(analysis))
            
            # Generate specialized test cases for different test types
            test_cases.extend(self._generate_api_tests(analysis))
            test_cases.extend(self._generate_visual_tests(analysis))
            test_cases.extend(self._generate_security_tests(analysis))
            test_cases.extend(self._generate_performance_tests(analysis))
            
            # General functionality tests
            test_cases.extend(self._generate_general_tests(analysis))
            
            # Limit to requested count
            return test_cases[:test_count]
        except ValueError as e:
            # Propagate more specific error messages from analyze_website
            logger.error(f"Error generating test cases from URL: {str(e)}")
            raise
        except Exception as e:
            error_msg = f"Unexpected error generating test cases from URL {url}: {str(e)}"
            logger.error(error_msg)
            # Add stack trace for better debugging
            import traceback
            logger.error(traceback.format_exc())
            raise ValueError(error_msg)
    
    def _generate_login_tests(self, analysis: WebsiteAnalysis) -> List[Dict[str, Any]]:
        """Generate login-specific test cases"""
        return [
            {
                "title": "User Login with Valid Credentials",
                "description": f"Verify successful login functionality on {analysis.title}",
                "test_type": "functional",
                "priority": "high",
                "steps": [
                    {"step_number": 1, "description": "Navigate to login page", "expected_result": "Login form is displayed"},
                    {"step_number": 2, "description": "Enter valid email/username", "expected_result": "Email field accepts input"},
                    {"step_number": 3, "description": "Enter valid password", "expected_result": "Password field accepts input"},
                    {"step_number": 4, "description": "Click login button", "expected_result": "User is authenticated and redirected"}
                ],
                "expected_result": "User successfully logs in and is redirected to dashboard/home page",
                "tags": ["authentication", "login", "smoke", "critical"],
                "preconditions": "Valid user account exists",
                "test_data": {"email": "test@example.com", "password": "validPassword123"}
            },
            {
                "title": "Login with Invalid Credentials",
                "description": "Verify error handling for invalid login attempts",
                "test_type": "functional", 
                "priority": "medium",
                "steps": [
                    {"step_number": 1, "description": "Navigate to login page", "expected_result": "Login form is displayed"},
                    {"step_number": 2, "description": "Enter invalid email", "expected_result": "Email field accepts input"},
                    {"step_number": 3, "description": "Enter invalid password", "expected_result": "Password field accepts input"},
                    {"step_number": 4, "description": "Click login button", "expected_result": "Error message is displayed"}
                ],
                "expected_result": "Appropriate error message is shown for invalid credentials",
                "tags": ["authentication", "negative", "security"],
                "test_data": {"email": "invalid@test.com", "password": "wrongPassword"}
            }
        ]
    
    def _generate_ecommerce_tests(self, analysis: WebsiteAnalysis) -> List[Dict[str, Any]]:
        """Generate e-commerce specific test cases"""
        return [
            {
                "title": "Shopping Cart Add/Remove Items",
                "description": f"Test adding and removing items from shopping cart on {analysis.title}",
                "test_type": "functional",
                "priority": "high", 
                "steps": [
                    {"step_number": 1, "description": "Browse product catalog", "expected_result": "Products are displayed correctly"},
                    {"step_number": 2, "description": "Select a product", "expected_result": "Product details page loads"},
                    {"step_number": 3, "description": "Click 'Add to Cart' button", "expected_result": "Item is added to cart"},
                    {"step_number": 4, "description": "Navigate to shopping cart", "expected_result": "Cart shows added item"},
                    {"step_number": 5, "description": "Remove item from cart", "expected_result": "Item is removed successfully"}
                ],
                "expected_result": "Items can be successfully added to and removed from shopping cart",
                "tags": ["ecommerce", "cart", "regression", "core-functionality"],
                "test_data": {"product_id": "sample_product_123"}
            }
        ]
        
    def _generate_form_tests(self, analysis: WebsiteAnalysis) -> List[Dict[str, Any]]:
        """Generate form validation test cases"""
        return [
            {
                "title": "Form Validation and Submission",
                "description": f"Test form validation rules on {analysis.title}",
                "test_type": "functional",
                "priority": "medium",
                "steps": [
                    {"step_number": 1, "description": "Navigate to form page", "expected_result": "Form is displayed with all fields"},
                    {"step_number": 2, "description": "Leave required fields empty", "expected_result": "Form shows validation errors"},
                    {"step_number": 3, "description": "Fill all required fields", "expected_result": "Validation errors clear"},
                    {"step_number": 4, "description": "Submit form", "expected_result": "Form submits successfully"}
                ],
                "expected_result": "Form validates input correctly and submits when valid",
                "tags": ["form", "validation", "input"]
            }
        ]
    
    def _generate_navigation_tests(self, analysis: WebsiteAnalysis) -> List[Dict[str, Any]]:
        """Generate navigation test cases"""
        return [
            {
                "title": "Website Navigation Flow",
                "description": f"Test navigation between pages on {analysis.title}",
                "test_type": "functional",
                "priority": "medium",
                "steps": [
                    {"step_number": 1, "description": "Navigate to homepage", "expected_result": "Homepage loads correctly"},
                    {"step_number": 2, "description": "Click navigation menu items", "expected_result": "Each page loads without errors"},
                    {"step_number": 3, "description": "Use browser back button", "expected_result": "Previous page loads correctly"},
                    {"step_number": 4, "description": "Test breadcrumb navigation", "expected_result": "Breadcrumbs work correctly"}
                ],
                "expected_result": "All navigation elements work correctly and pages load properly",
                "tags": ["navigation", "ui", "usability"]
            }
        ]

    def _generate_api_tests(self, analysis: WebsiteAnalysis) -> List[Dict[str, Any]]:
        """Generate API test cases"""
        return [
            {
                "title": "API Endpoint Validation",
                "description": f"Validate API endpoints for {analysis.title}",
                "test_type": "api",
                "priority": "high",
                "steps": [
                    {"step_number": 1, "description": "Identify API endpoints from website", "expected_result": "All API endpoints are mapped"},
                    {"step_number": 2, "description": "Test API response codes", "expected_result": "All endpoints return appropriate HTTP status codes"},
                    {"step_number": 3, "description": "Validate API response structure", "expected_result": "Responses match expected schema"},
                    {"step_number": 4, "description": "Test API error handling", "expected_result": "Proper error responses for invalid requests"}
                ],
                "expected_result": "All API endpoints function correctly with proper responses",
                "tags": ["api", "integration", "backend"]
            },
            {
                "title": "API Performance and Rate Limiting",
                "description": f"Test API performance and rate limiting for {analysis.title}",
                "test_type": "api",
                "priority": "medium",
                "steps": [
                    {"step_number": 1, "description": "Measure API response times", "expected_result": "Response times are within acceptable limits"},
                    {"step_number": 2, "description": "Test concurrent API requests", "expected_result": "System handles concurrent requests properly"},
                    {"step_number": 3, "description": "Test API rate limiting", "expected_result": "Rate limiting is enforced appropriately"},
                    {"step_number": 4, "description": "Validate API throughput", "expected_result": "System maintains performance under load"}
                ],
                "expected_result": "API performs well under various load conditions",
                "tags": ["api", "performance", "load-testing"]
            }
        ]

    def _generate_visual_tests(self, analysis: WebsiteAnalysis) -> List[Dict[str, Any]]:
        """Generate visual test cases"""
        return [
            {
                "title": "Cross-Browser Visual Consistency",
                "description": f"Verify visual consistency across browsers for {analysis.title}",
                "test_type": "visual",
                "priority": "high",
                "steps": [
                    {"step_number": 1, "description": "Load website in Chrome", "expected_result": "Page renders correctly"},
                    {"step_number": 2, "description": "Load website in Firefox", "expected_result": "Page renders correctly"},
                    {"step_number": 3, "description": "Load website in Safari", "expected_result": "Page renders correctly"},
                    {"step_number": 4, "description": "Compare visual appearance", "expected_result": "Consistent appearance across browsers"}
                ],
                "expected_result": "Website appears consistent across different browsers",
                "tags": ["visual", "cross-browser", "ui"]
            },
            {
                "title": "Responsive Design Validation",
                "description": f"Test responsive design for {analysis.title}",
                "test_type": "visual",
                "priority": "high",
                "steps": [
                    {"step_number": 1, "description": "Test website on mobile viewport", "expected_result": "Layout adapts appropriately"},
                    {"step_number": 2, "description": "Test website on tablet viewport", "expected_result": "Layout adapts appropriately"},
                    {"step_number": 3, "description": "Test website on desktop viewport", "expected_result": "Layout adapts appropriately"},
                    {"step_number": 4, "description": "Verify element visibility and positioning", "expected_result": "All elements are properly positioned"}
                ],
                "expected_result": "Website layout adapts correctly to different screen sizes",
                "tags": ["visual", "responsive", "mobile"]
            }
        ]

    def _generate_security_tests(self, analysis: WebsiteAnalysis) -> List[Dict[str, Any]]:
        """Generate security test cases"""
        return [
            {
                "title": "Input Validation and Sanitization",
                "description": f"Test input validation and sanitization for {analysis.title}",
                "test_type": "security",
                "priority": "high",
                "steps": [
                    {"step_number": 1, "description": "Test form inputs with special characters", "expected_result": "Special characters are properly sanitized"},
                    {"step_number": 2, "description": "Test SQL injection payloads", "expected_result": "SQL injection attempts are blocked"},
                    {"step_number": 3, "description": "Test XSS payloads", "expected_result": "XSS attempts are blocked"},
                    {"step_number": 4, "description": "Test command injection payloads", "expected_result": "Command injection attempts are blocked"}
                ],
                "expected_result": "All malicious input is properly sanitized and blocked",
                "tags": ["security", "input-validation", "xss", "sql-injection"]
            },
            {
                "title": "Authentication Security",
                "description": f"Test authentication security for {analysis.title}",
                "test_type": "security",
                "priority": "high",
                "steps": [
                    {"step_number": 1, "description": "Test brute force protection", "expected_result": "Account lockout after failed attempts"},
                    {"step_number": 2, "description": "Test password strength requirements", "expected_result": "Weak passwords are rejected"},
                    {"step_number": 3, "description": "Test session management", "expected_result": "Sessions expire properly"},
                    {"step_number": 4, "description": "Test secure cookie flags", "expected_result": "Cookies have proper security flags"}
                ],
                "expected_result": "Authentication system is secure against common attacks",
                "tags": ["security", "authentication", "session-management"]
            }
        ]

    def _generate_performance_tests(self, analysis: WebsiteAnalysis) -> List[Dict[str, Any]]:
        """Generate performance test cases"""
        return [
            {
                "title": "Page Load Performance",
                "description": f"Test page load performance for {analysis.title}",
                "test_type": "performance",
                "priority": "high",
                "steps": [
                    {"step_number": 1, "description": "Measure first contentful paint (FCP)", "expected_result": "FCP is within acceptable limits"},
                    {"step_number": 2, "description": "Measure largest contentful paint (LCP)", "expected_result": "LCP is within acceptable limits"},
                    {"step_number": 3, "description": "Measure cumulative layout shift (CLS)", "expected_result": "CLS is minimal"},
                    {"step_number": 4, "description": "Measure time to interactive (TTI)", "expected_result": "TTI is within acceptable limits"}
                ],
                "expected_result": "Website meets Core Web Vitals performance metrics",
                "tags": ["performance", "core-web-vitals", "loading"]
            },
            {
                "title": "Resource Loading Optimization",
                "description": f"Test resource loading optimization for {analysis.title}",
                "test_type": "performance",
                "priority": "medium",
                "steps": [
                    {"step_number": 1, "description": "Analyze JavaScript bundle size", "expected_result": "Bundle size is optimized"},
                    {"step_number": 2, "description": "Check image optimization", "expected_result": "Images are properly compressed"},
                    {"step_number": 3, "description": "Verify caching headers", "expected_result": "Appropriate caching headers are set"},
                    {"step_number": 4, "description": "Test lazy loading implementation", "expected_result": "Non-critical resources are lazy loaded"}
                ],
                "expected_result": "Website resources are optimized for fast loading",
                "tags": ["performance", "optimization", "resources"]
            }
        ]

    def _generate_general_tests(self, analysis: WebsiteAnalysis) -> List[Dict[str, Any]]:
        """Generate general functionality test cases"""
        return [
            {
                "title": "Page Load and Responsiveness",
                "description": f"Verify page loading and basic functionality on {analysis.title}",
                "test_type": "functional",
                "priority": "medium",
                "steps": [
                    {"step_number": 1, "description": "Navigate to website", "expected_result": "Page loads within acceptable time"},
                    {"step_number": 2, "description": "Verify page elements load", "expected_result": "All images, text, and UI elements display"},
                    {"step_number": 3, "description": "Test responsive design", "expected_result": "Page adapts to different screen sizes"},
                    {"step_number": 4, "description": "Check for broken links", "expected_result": "All links are functional"}
                ],
                "expected_result": "Website loads properly and is responsive across devices", 
                "tags": ["performance", "responsive", "basic-functionality"]
            }
        ]

# Global instance
website_test_generator = WebsiteTestCaseGenerator()