import os
import requests
import time

class AISpeakerTester:
    def __init__(self):
        self.output_dir = 'test_output/ai_speaker'
        os.makedirs(self.output_dir, exist_ok=True)
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://ai-speaker.net/api/tts'
    
    def test_chinese_tts(self, text, voice_id='zh-CN-YunxiNeural'):
        """Test Chinese TTS with the given text and voice"""
        try:
            # Prepare the request data
            data = {
                'text': text,
                'voice': voice_id,
                'speed': 1.0,
                'pitch': 1.0,
                'volume': 1.0,
                'language': 'zh-CN'
            }
            
            # Send the request
            response = self.session.post(self.base_url, 
                                      json=data, 
                                      headers=self.headers,
                                      timeout=30)
            
            if response.status_code == 200:
                # Try to save the response content as audio
                if response.content:
                    filename = f"ai_speaker_{int(time.time())}.mp3"
                    filepath = os.path.join(self.output_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    # Verify the file was created and has content
                    if os.path.getsize(filepath) > 0:
                        return True, f"Success! Audio saved to: {filepath}"
                    else:
                        return False, "Generated audio file is empty"
                return False, "Empty response content"
            else:
                return False, f"HTTP error: {response.status_code} - {response.text}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"

def main():
    tester = AISpeakerTester()
    
    # Test with different Chinese texts
    test_texts = [
        "你好，这是一个AI语音测试。",
        "欢迎使用AI语音合成服务。",
        "祝您今天心情愉快！"
    ]
    
    for text in test_texts:
        print(f"\nTesting text: {text}")
        success, message = tester.test_chinese_tts(text)
        print(f"Result: {'✅' if success else '❌'} {message}")
        time.sleep(1)  # Add delay between requests

if __name__ == "__main__":
    main()
