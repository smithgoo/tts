import os
import requests
from bs4 import BeautifulSoup
import time

class LuyinzhushouTester:
    def __init__(self):
        self.output_dir = 'test_output/luyinzhushou'
        os.makedirs(self.output_dir, exist_ok=True)
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_url = 'https://www.luyinzhushou.com/voice/convert'
        
    def get_token(self):
        """Get the CSRF token from the main page"""
        try:
            main_page = self.session.get('https://www.luyinzhushou.com/text2voice/', 
                                      headers=self.headers, 
                                      timeout=10)
            soup = BeautifulSoup(main_page.text, 'html.parser')
            token_input = soup.find('input', {'name': '_token'})
            return token_input['value'] if token_input and token_input.get('value') else ''
        except Exception as e:
            print(f"Error getting token: {e}")
            return ''
    
    def test_chinese_tts(self, text, voice_id='zh-CN-YunxiNeural'):
        """Test Chinese TTS with the given text and voice"""
        try:
            # Get CSRF token
            token = self.get_token()
            if not token:
                return False, "Failed to get CSRF token"
            
            # Prepare the request data
            data = {
                '_token': token,
                'text': text,
                'voice': voice_id,
                'style': 'general',
                'rate': '0%',
                'pitch': '0%',
                'format': 'mp3',
            }
            
            # Send the request
            response = self.session.post(self.base_url, 
                                      data=data, 
                                      headers=self.headers,
                                      timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    audio_url = result.get('url')
                    if audio_url:
                        # Download the audio file
                        audio_response = self.session.get(audio_url, 
                                                       headers=self.headers,
                                                       timeout=30)
                        if audio_response.status_code == 200:
                            # Save the audio file
                            filename = f"luyinzhushou_{int(time.time())}.mp3"
                            filepath = os.path.join(self.output_dir, filename)
                            with open(filepath, 'wb') as f:
                                f.write(audio_response.content)
                            return True, f"Success! Audio saved to: {filepath}"
                        else:
                            return False, f"Failed to download audio: {audio_response.status_code}"
                return False, f"API error: {result.get('message', 'Unknown error')}"
            return False, f"HTTP error: {response.status_code}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"

def main():
    tester = LuyinzhushouTester()
    
    # Test with different Chinese texts
    test_texts = [
        "你好，这是一个测试。",
        "欢迎使用录音助手语音合成。",
        "今天天气真好！"
    ]
    
    for text in test_texts:
        print(f"\nTesting text: {text}")
        success, message = tester.test_chinese_tts(text)
        print(f"Result: {'✅' if success else '❌'} {message}")
        time.sleep(1)  # Add delay between requests

if __name__ == "__main__":
    main()
