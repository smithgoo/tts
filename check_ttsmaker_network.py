#!/usr/bin/env python3
"""
Script to check how TTSMaker works by examining the page source and finding the real API endpoints
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import urllib.parse

def get_page_and_extract_api_info():
    """Get the TTSMaker page and extract API-related information"""
    print("Getting TTSMaker page and extracting API information...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://ttsmaker.cn/',
    }
    
    try:
        response = requests.get('https://ttsmaker.cn/', headers=headers)
        print(f"Page loaded successfully, status: {response.status_code}")
        
        # Look for JavaScript files
        js_pattern = r'<script[^>]*src=[\'"]([^\'"]*\.js)[\'"][^>]*>'
        js_files = re.findall(js_pattern, response.text, re.IGNORECASE)
        
        print(f"\nFound {len(js_files)} JavaScript files:")
        for js_file in js_files[:10]:  # Show first 10
            print(f"  - {js_file}")
        
        # Look for potential API endpoints in the HTML
        # Common patterns for API endpoints
        api_patterns = [
            r'["\'](/api/[^"\']+)["\']',
            r'["\'](/tts[^"\']*)["\']',
            r'["\'](https?://[^"\']*/api/[^"\']+)["\']',
            r'["\'](https?://[^"\']*/tts[^"\']+)["\']',
        ]
        
        print("\nLooking for API endpoints in HTML source...")
        found_endpoints = set()
        for pattern in api_patterns:
            matches = re.findall(pattern, response.text)
            for match in matches:
                if 'tts' in match.lower() or 'api' in match.lower():
                    found_endpoints.add(match)
        
        if found_endpoints:
            print("Found potential API endpoints in HTML:")
            for endpoint in sorted(found_endpoints):
                print(f"  - {endpoint}")
        else:
            print("No obvious API endpoints found in HTML")
        
        # Look for JavaScript files that might contain API calls
        for js_file in js_files[:5]:  # Check first 5 JS files
            if js_file.startswith('/'):
                js_url = f"https://ttsmaker.cn{js_file}"
            elif js_file.startswith('http'):
                js_url = js_file
            else:
                js_url = f"https://ttsmaker.cn/{js_file}"
            
            print(f"\nChecking JS file: {js_url}")
            try:
                js_response = requests.get(js_url, headers=headers)
                if js_response.status_code == 200:
                    # Look for API calls in JS
                    js_content = js_response.text
                    js_endpoints = set()
                    for pattern in api_patterns:
                        matches = re.findall(pattern, js_content)
                        for match in matches:
                            if 'tts' in match.lower() or 'api' in match.lower():
                                js_endpoints.add(match)
                    
                    if js_endpoints:
                        print("  Found API endpoints in JS:")
                        for endpoint in sorted(js_endpoints):
                            print(f"    - {endpoint}")
                    
                    # Look for fetch or XMLHttpRequest calls
                    fetch_calls = re.findall(r'fetch\s*\(\s*[\'"]([^\'"]+)[\'"]', js_content)
                    xhr_calls = re.findall(r'open\s*\(\s*[\'"][^\'"]*[\'"]\s*,\s*[\'"]([^\'"]+)[\'"]', js_content)
                    
                    all_calls = fetch_calls + xhr_calls
                    api_calls = [call for call in all_calls if 'api' in call.lower() or 'tts' in call.lower()]
                    
                    if api_calls:
                        print("  Found API calls in JS:")
                        for call in api_calls:
                            print(f"    - {call}")
                            
            except Exception as e:
                print(f"  Error checking JS file: {e}")
        
        return response.text
        
    except Exception as e:
        print(f"Error getting page: {e}")
        return None

def test_new_api_approach():
    """Test a new approach to understand the current API"""
    print("\nTesting new approach to find working API...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://ttsmaker.cn/',
        'Origin': 'https://ttsmaker.cn',
    }
    
    # Try to get the page and see if there are any tokens or session IDs needed
    try:
        session = requests.Session()
        main_page = session.get('https://ttsmaker.cn/', headers=headers)
        
        # Extract potential tokens or form data from the page
        soup = BeautifulSoup(main_page.text, 'html.parser')
        
        # Look for any hidden inputs that might be tokens
        hidden_inputs = soup.find_all('input', {'type': 'hidden'})
        print(f"\nFound {len(hidden_inputs)} hidden inputs:")
        for inp in hidden_inputs:
            name = inp.get('name')
            value = inp.get('value')
            if name and value:
                print(f"  {name}: {value[:50]}{'...' if len(value) > 50 else ''}")
        
        # Look for any script tags that might contain configuration
        scripts = soup.find_all('script')
        config_data = []
        for script in scripts:
            if script.string:
                # Look for JavaScript objects that might contain API config
                config_matches = re.findall(r'var\s+(\w+)\s*=\s*({.*?});', script.string, re.DOTALL)
                for var_name, config_str in config_matches:
                    print(f"\nFound JavaScript config variable: {var_name}")
                    # Try to parse as JSON
                    try:
                        # Clean up the JSON string
                        cleaned = config_str.strip()
                        if cleaned.startswith('{') and cleaned.endswith('}'):
                            # This is a simplified approach - real parsing would be more complex
                            print(f"  Config: {cleaned[:200]}...")
                    except:
                        print(f"  Could not parse as JSON: {cleaned[:100]}...")
        
        return session
        
    except Exception as e:
        print(f"Error in new approach: {e}")
        return None

def main():
    print("Comprehensive TTSMaker API Investigation")
    print("="*50)
    
    # Extract API info from the page
    page_content = get_page_and_extract_api_info()
    
    # Try new approach
    session = test_new_api_approach()
    
    print("\nInvestigation complete!")
    print("\nBased on the investigation, it appears that TTSMaker has changed their API")
    print("and the old endpoints are no longer working (returning 404 errors).")
    print("The service may now require authentication, session tokens, or use a different")
    print("approach than the one we were using previously.")

if __name__ == "__main__":
    main()