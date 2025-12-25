#!/usr/bin/env python3
"""
Script to extract the actual voice data from TTSMaker website
"""
import requests
import re
import json
from urllib.parse import unquote

def extract_voice_data():
    """Extract actual voice data from TTSMaker website"""
    print("Extracting actual voice data from TTSMaker...")
    
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
        page_content = response.text
        
        # Find the support_language_data JavaScript variable
        # This looks for var support_language_data = { ... };
        pattern = r'var support_language_data\s*=\s*({.*?});'
        match = re.search(pattern, page_content, re.DOTALL)
        
        if match:
            data_str = match.group(1)
            print("Found voice data in page source")
            
            # Convert JavaScript object notation to valid JSON
            # Replace single quotes with double quotes, but be careful not to replace quotes inside strings
            json_str = convert_js_to_json(data_str)
            
            try:
                voice_data = json.loads(json_str)
                
                # Extract Chinese voices specifically
                if 'zh-cn' in voice_data:
                    chinese_voices = voice_data['zh-cn']
                    print(f"Found {len(chinese_voices)} Chinese voices:")
                    
                    formatted_voices = []
                    for voice in chinese_voices:
                        voice_id = voice.get('id', '')
                        name = voice.get('name', '')
                        gender = voice.get('gender', '')
                        
                        gender_str = 'Female' if gender == 2 else 'Male' if gender == 1 else 'Other'
                        print(f"  ID: {voice_id}, Name: {name}, Gender: {gender_str}")
                        
                        formatted_voices.append({
                            'id': voice_id,
                            'name': f"{name} - {gender_str}"
                        })
                    
                    return formatted_voices
                else:
                    print("No Chinese voices found in the data")
                    return []
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print("Trying alternative extraction method...")
                return extract_voices_alternative(data_str)
        else:
            print("Could not find support_language_data in page")
            return []
            
    except Exception as e:
        print(f"Error extracting voice data: {e}")
        return []

def convert_js_to_json(js_str):
    """Convert JavaScript object notation to valid JSON"""
    # This is a simplified conversion - in practice, a more robust solution would be needed
    # For now, we'll use a different approach
    
    # Find the zh-cn section specifically
    zh_cn_pattern = r"'zh-cn':\s*(\[.*?\])(?=\s*,\s*['\"]|$)"
    zh_cn_match = re.search(zh_cn_pattern, js_str, re.DOTALL)
    
    if zh_cn_match:
        # Extract just the Chinese voices array
        voices_str = zh_cn_match.group(1)
        
        # Replace single quotes with double quotes, but be careful about quotes inside strings
        # This is a simplified approach - for a robust solution we'd need a proper JS parser
        result = voices_str
        
        # Replace property names with double quotes
        result = re.sub(r"'(\w+)':", r'"\1":', result)
        
        # Replace standalone single quotes with double quotes (this is imperfect)
        # For now, let's return the original string to avoid breaking it
        return result
    
    return js_str

def extract_voices_alternative(data_str):
    """Alternative method to extract voices using regex"""
    print("Using alternative extraction method...")
    
    # Look for the zh-cn array specifically
    zh_cn_pattern = r"'zh-cn':\s*\[(.*?)\](?=\s*,\s*['\"]|\s*\})"
    zh_cn_match = re.search(zh_cn_pattern, data_str, re.DOTALL)
    
    if zh_cn_match:
        voices_content = zh_cn_match.group(1)
        
        # Extract individual voice objects
        # Each voice object looks like: {'id': number, 'name': 'string', 'gender': number, ...}
        voice_pattern = r"\{\s*'id'\s*:\s*(\d+)[^}]*?'name'\s*:\s*'([^']*)'[^}]*?'gender'\s*:\s*(\d+)"
        voice_matches = re.findall(voice_pattern, voices_content)
        
        print(f"Found {len(voice_matches)} Chinese voices using alternative method:")
        formatted_voices = []
        
        for voice_id, name, gender in voice_matches:
            gender_str = 'Female' if gender == '2' else 'Male' if gender == '1' else 'Other'
            print(f"  ID: {voice_id}, Name: {name}, Gender: {gender_str}")
            
            formatted_voices.append({
                'id': int(voice_id),
                'name': f"{name} - {gender_str}"
            })
        
        return formatted_voices
    
    return []

def main():
    voices = extract_voice_data()
    
    if voices:
        print(f"\nFound {len(voices)} voices total")
        
        # Print in format that can be used in app.py
        print("\nFormat for app.py TTS_SERVICES:")
        print("            # Chinese voices")
        for i, voice in enumerate(voices[:10]):  # Show first 10
            print(f"            {{'id': {voice['id']}, 'name': '{voice['name']}'}},")
        
        if len(voices) > 10:
            print(f"            # ... and {len(voices) - 10} more voices")
    else:
        print("No voices found")

if __name__ == "__main__":
    main()