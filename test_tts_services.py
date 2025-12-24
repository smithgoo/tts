import os
import sys
import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import TTSConverter

# Configuration
OUTPUT_DIR = 'test_output'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def test_tts_maker():
    """Test TTSMaker service"""
    print("\n=== Testing TTSMaker (ttsmaker.cn) ===")
    
    # Initialize converter
    converter = TTSConverter(OUTPUT_DIR)
    
    # Test voice fetching (TTSMaker doesn't seem to have a public API for this, so we'll test with known voices)
    test_voices = [0, 1, 2]  # Common voice IDs
    print(f"Testing with voices: {test_voices}")
    
    # Test text
    test_text = "这是一个测试文本，用于验证TTS服务是否正常工作。"
    
    # Test each voice
    for voice_id in test_voices:
        print(f"\nTesting voice ID: {voice_id}")
        
        # Test with default parameters
        print("Testing with default parameters...")
        result = converter.tts_maker(
            text=test_text,
            voice_id=voice_id,
            speed=1.0,
            pitch=1.0,
            volume=1.0
        )
        
        if result['success']:
            print(f"✅ Success! Audio saved as: {result['filename']}")
            print(f"   Service: {result['service']}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        # Add a small delay between requests
        time.sleep(2)

def test_luyinzhushou():
    """Test LuYinZhuShou service"""
    print("\n=== Testing LuYinZhuShou (luyinzhushou.com) ===")
    
    # Initialize converter
    converter = TTSConverter(OUTPUT_DIR)
    
    # Known voices for this service
    test_voices = [
        'zh-CN-YunxiNeural',
        'zh-CN-YunyangNeural',
        'zh-CN-XiaoxiaoNeural'
    ]
    
    print(f"Testing with voices: {test_voices}")
    
    # Test text
    test_text = "这是一个测试文本，用于验证TTS服务是否正常工作。"
    
    # Test each voice
    for voice_id in test_voices:
        print(f"\nTesting voice: {voice_id}")
        
        # Test with default parameters
        print("Testing with default parameters...")
        result = converter.luyinzhushou(
            text=test_text,
            voice_id=voice_id,
            speed='0%',
            pitch='0%'
        )
        
        if result['success']:
            print(f"✅ Success! Audio saved as: {result['filename']}")
            print(f"   Service: {result['service']}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        # Add a small delay between requests
        time.sleep(2)

def test_ai_speaker():
    """Test AI-Speaker.net service"""
    print("\n=== Testing AI-Speaker (ai-speaker.net) ===")
    print("⚠️ Note: AI-Speaker.net requires a different implementation.")
    print("This test is a placeholder and needs to be implemented based on the service's API.")
    
    # Implementation for AI-Speaker.net would go here
    # This is a placeholder as the service might require a different approach
    
    print("❌ AI-Speaker.net test not implemented yet")

def main():
    print("Starting TTS Service Tests...")
    print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}")
    
    # Test TTSMaker
    test_tts_maker()
    
    # Test LuYinZhuShou
    test_luyinzhushou()
    
    # Test AI-Speaker (placeholder)
    test_ai_speaker()
    
    print("\n=== Test Complete ===")
    print(f"Check the '{OUTPUT_DIR}' directory for generated audio files.")

if __name__ == "__main__":
    main()
