#!/usr/bin/env python3
"""
Script to scrape the actual voice data from TTSMaker website
"""
import requests
from bs4 import BeautifulSoup
import re
import json
import time

def scrape_ttsmaker_voices():
    """Scrape the actual voices from TTSMaker website"""
    print("Scraping TTSMaker voices...")
    
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
        
        # Parse the page content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for voice-related JavaScript or configuration
        voice_data = []
        
        # Look for script tags that might contain voice data
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for voice-related variables or configurations
                if 'voice' in script.string.lower() or 'speaker' in script.string.lower():
                    # Try to find voice configurations
                    voice_matches = re.findall(r'voices?\s*[:=]\s*(\[.*?\])', script.string, re.DOTALL | re.IGNORECASE)
                    if voice_matches:
                        for match in voice_matches:
                            try:
                                # Try to parse as JSON
                                voice_json = json.loads(match)
                                if isinstance(voice_json, list):
                                    voice_data.extend(voice_json)
                                    print(f"Found {len(voice_json)} voices in script")
                            except:
                                # If JSON parsing fails, try to extract individual voice objects
                                voice_objects = re.findall(r'\{\s*["\']id["\']\s*:\s*["\']?([^"\']*)["\']?\s*,\s*["\']name["\']\s*:\s*["\']([^"\']*)["\']', match)
                                for vid, vname in voice_objects:
                                    voice_data.append({'id': vid, 'name': vname})
        
        # Look for voice selection dropdowns or radio buttons
        voice_selects = soup.find_all('select', {'name': re.compile(r'voice|speaker', re.I)})
        for select in voice_selects:
            options = select.find_all('option')
            for option in options:
                if option.get('value'):
                    voice_name = option.get_text(strip=True)
                    voice_id = option.get('value')
                    if voice_id and voice_name:
                        voice_data.append({'id': voice_id, 'name': voice_name})
        
        # Look for voice buttons or elements with data attributes
        voice_elements = soup.find_all(attrs={"data-voice": True})
        for elem in voice_elements:
            voice_id = elem.get('data-voice')
            voice_name = elem.get_text(strip=True) or elem.get('title') or elem.get('data-name')
            if voice_id:
                voice_data.append({'id': voice_id, 'name': voice_name or f'Voice {voice_id}'})
        
        # Also check for any form elements with voice-related inputs
        voice_inputs = soup.find_all('input', {'name': re.compile(r'voice|speaker', re.I)})
        for input_elem in voice_inputs:
            if input_elem.get('type') == 'radio' or input_elem.get('type') == 'select':
                voice_id = input_elem.get('value')
                # Look for associated label
                label = soup.find('label', {'for': input_elem.get('id')})
                voice_name = label.get_text(strip=True) if label else f'Voice {voice_id}'
                if voice_id:
                    voice_data.append({'id': voice_id, 'name': voice_name})
        
        # Remove duplicates while preserving order
        seen_ids = set()
        unique_voices = []
        for voice in voice_data:
            voice_id = voice.get('id')
            if voice_id not in seen_ids:
                unique_voices.append(voice)
                seen_ids.add(voice_id)
        
        print(f"Found {len(unique_voices)} unique voices:")
        for i, voice in enumerate(unique_voices):
            print(f"  {i+1}. ID: {voice['id']}, Name: {voice['name']}")
        
        return unique_voices
        
    except Exception as e:
        print(f"Error scraping voices: {e}")
        return []

def get_api_voice_data():
    """Try to get voice data by analyzing API calls"""
    print("\nTrying to get voice data from API...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://ttsmaker.cn/',
        'Origin': 'https://ttsmaker.cn',
    }
    
    # Try different potential endpoints for voice data
    potential_endpoints = [
        'https://ttsmaker.cn/api/voices',
        'https://ttsmaker.cn/voices',
        'https://ttsmaker.cn/api/config',
        'https://ttsmaker.cn/config',
        'https://api.ttsmaker.cn/v1/voices',
        'https://api.ttsmaker.cn/voices',
    ]
    
    for endpoint in potential_endpoints:
        try:
            print(f"  Testing: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"    Success! Got voice data: {len(data) if isinstance(data, list) else 'object'}")
                    return data
                except:
                    print(f"    Response is not JSON: {response.text[:200]}...")
        except Exception as e:
            print(f"    Error: {e}")
    
    return None

def main():
    print("TTSMaker Voice Data Scraper")
    print("="*50)
    
    # Try to scrape voices from the page
    scraped_voices = scrape_ttsmaker_voices()
    
    # Try to get voice data from API
    api_voices = get_api_voice_data()
    
    # Combine results
    all_voices = {
        'scraped_from_page': scraped_voices,
        'from_api': api_voices,
        'timestamp': time.time()
    }
    
    # Save to a file
    with open('ttsmaker_voices.json', 'w', encoding='utf-8') as f:
        json.dump(all_voices, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to ttsmaker_voices.json")
    
    # Also print in a format that can be used in app.py
    print("\nFormatted for app.py TTS_SERVICES:")
    print("    'ttsmaker': {")
    print("        'name': 'TTSMaker',")
    print("        'voices': [")
    
    if scraped_voices:
        for voice in scraped_voices:
            print(f"            {{'id': '{voice['id']}', 'name': '{voice['name']}'}},")

    print("        ],")
    print("        'speeds': [0.5, 0.75, 1.0, 1.25, 1.5, 2.0],")
    print("        'pitches': [0.5, 0.75, 1.0, 1.25, 1.5, 2.0],")
    print("        'volumes': [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]")
    print("    },")

if __name__ == "__main__":
    main()