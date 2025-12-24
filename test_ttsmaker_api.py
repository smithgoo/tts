#!/usr/bin/env python3
"""
Test script to analyze and test the TTSMaker API
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import urllib.parse
from datetime import datetime

def analyze_ttsmaker_page():
    """Analyze the TTSMaker page to understand its structure and API endpoints"""
    print("Analyzing TTSMaker page structure...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get('https://ttsmaker.cn/', headers=headers)
        print(f"Status Code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for JavaScript files that might contain API calls
        scripts = soup.find_all('script', src=True)
        print("\nFound JavaScript files:")
        for script in scripts:
            if 'tts' in script['src'] or 'main' in script['src'] or 'app' in script['src']:
                print(f"  - {script['src']}")
        
        # Look for any script tags with inline JavaScript
        inline_scripts = soup.find_all('script', src=False)
        for script in inline_scripts:
            if script.string and ('api' in script.string.lower() or 'tts' in script.string.lower()):
                print(f"Found potential API references in inline script")
        
        # Look for form actions or data attributes that might indicate API endpoints
        forms = soup.find_all('form')
        for form in forms:
            if form.get('action'):
                print(f"Form action: {form['action']}")
        
        # Look for data attributes that might indicate API endpoints
        elements_with_data = soup.find_all(attrs={"data-action": True})
        for elem in elements_with_data:
            print(f"Data action: {elem['data-action']}")
            
        return response.text
        
    except Exception as e:
        print(f"Error analyzing page: {e}")
        return None

def test_api_endpoints():
    """Test various API endpoints that might be used by TTSMaker"""
    print("\nTesting potential API endpoints...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://ttsmaker.cn/',
    }
    
    # Common endpoints that TTS services might use
    endpoints = [
        'https://ttsmaker.cn/api/tts',
        'https://ttsmaker.cn/tts',
        'https://ttsmaker.cn/create-tts',
        'https://api.ttsmaker.cn/v1/create-tts-task',
        'https://ttsmaker.cn/api/create',
        'https://ttsmaker.cn/api/v1/tts',
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\nTesting {endpoint}")
            response = requests.options(endpoint, headers=headers)
            print(f"  OPTIONS Status: {response.status_code}")
            
            if response.status_code in [200, 204, 404, 405]:
                # Try a GET request
                response = requests.get(endpoint, headers=headers)
                print(f"  GET Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  GET Response: {response.text[:200]}...")
                    
        except Exception as e:
            print(f"  Error testing {endpoint}: {e}")

def test_current_implementation():
    """Test the current implementation in the app.py file"""
    print("\nTesting current implementation...")
    
    # Test data similar to what's in the app.py
    test_text = "Hello, this is a test of the TTSMaker service."
    test_voice = 0
    test_speed = 1.0
    test_pitch = 1.0
    test_volume = 1.0
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Origin': 'https://ttsmaker.cn',
        'Referer': 'https://ttsmaker.cn/',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    
    # Try the original endpoint that was causing 404
    url = 'https://ttsmaker.cn/tts'
    data = {
        'text': test_text,
        'voice_id': test_voice,
        'speed': test_speed,
        'pitch': test_pitch,
        'volume': test_volume,
        'audio_format': 'mp3',
        'token': 'ttsmaker',
        'speaker_id': test_voice,
        'text_analysis': 'auto',
        'audio_speed': test_speed,
        'audio_volume': test_volume,
        'audio_norm': '0',
        'text_paragraph_pause_time': '0',
        'background_music_volume': '0',
        'background_music_speed': '1',
        'speech_rate': test_speed,
        'pitch_rate': test_pitch
    }
    
    try:
        print(f"Testing original endpoint: {url}")
        response = requests.post(url, data=data, headers=headers, timeout=30)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        if response.status_code == 200:
            print("Success! Got audio response")
        else:
            print(f"Failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"Error with original endpoint: {e}")
    
    # Try the API endpoint
    api_url = 'https://ttsmaker.cn/api/tts'
    try:
        print(f"\nTesting API endpoint: {api_url}")
        response = requests.post(api_url, data=data, headers=headers, timeout=30)
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            print("Success! Got audio response from API endpoint")
        else:
            print(f"API endpoint failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"Error with API endpoint: {e}")

def find_ajax_calls():
    """Look for potential AJAX calls in the page source"""
    print("\nLooking for AJAX calls in page source...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    try:
        response = requests.get('https://ttsmaker.cn/', headers=headers)
        page_content = response.text
        
        # Look for common AJAX patterns in JavaScript
        import re
        
        # Look for fetch calls
        fetch_calls = re.findall(r'fetch\s*\(\s*[\'"]([^\'"]+)[\'"]', page_content)
        if fetch_calls:
            print("Found fetch calls:")
            for call in fetch_calls:
                if 'api' in call.lower() or 'tts' in call.lower():
                    print(f"  - {call}")
        
        # Look for jQuery AJAX calls
        ajax_calls = re.findall(r'\$\.ajax\s*\(\s*\{[^}]*url\s*:\s*[\'"]([^\'"]+)[\'"]', page_content)
        if ajax_calls:
            print("Found jQuery AJAX calls:")
            for call in ajax_calls:
                if 'api' in call.lower() or 'tts' in call.lower():
                    print(f"  - {call}")
        
        # Look for XMLHttpRequest patterns
        xhr_calls = re.findall(r'open\s*\(\s*[\'"][^\'"]*[\'"]\s*,\s*[\'"]([^\'"]+)[\'"]', page_content)
        if xhr_calls:
            print("Found XHR calls:")
            for call in xhr_calls:
                if 'api' in call.lower() or 'tts' in call.lower():
                    print(f"  - {call}")
                    
    except Exception as e:
        print(f"Error finding AJAX calls: {e}")

def main():
    print("TTSMaker API Analysis and Testing")
    print("="*50)
    
    # Analyze the page structure
    page_content = analyze_ttsmaker_page()
    
    # Look for AJAX calls
    find_ajax_calls()
    
    # Test various endpoints
    test_api_endpoints()
    
    # Test current implementation
    test_current_implementation()
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()