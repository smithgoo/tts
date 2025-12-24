import os
import time
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup

class TTSConverter:
    def __init__(self, output_dir='tts_output'):
        """Initialize the TTS converter with output directory"""
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def tts_maker_cn(self, text, voice_type=0):
        """Convert text to speech using ttsmaker.cn"""
        try:
            url = 'https://ttsmaker.cn/api/tts'
            data = {
                'text': text,
                'voice_id': voice_type,  # 0-7 for different voices
                'speed': 1.0,
                'volume': 1.0,
                'pitch': 1.0,
                'audio_format': 'mp3',
                'audio_speed': 1.0,
                'audio_volume': 0,
                'audio_norm': '0',
                'text_paragraph_pause_time': 0,
                'background_music_volume': 0,
                'background_music_speed': 1.0,
                'background_music_volume': 0,
                'speech_rate': 1.0,
                'pitch_rate': 1.0,
                'speech_volume': 1.0,
            }
            
            response = requests.post(url, data=data, headers=self.headers)
            if response.status_code == 200:
                timestamp = int(time.time())
                filename = os.path.join(self.output_dir, f'ttsmaker_{timestamp}.mp3')
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return f"Success! Audio saved as {filename}"
            return f"Error from ttsmaker.cn: {response.status_code}"
        except Exception as e:
            return f"Error with ttsmaker.cn: {str(e)}"

    def luyinzhushou(self, text):
        """Convert text to speech using luyinzhushou.com"""
        try:
            # First, get the token from the main page
            session = requests.Session()
            main_page = session.get('https://www.luyinzhushou.com/text2voice/', headers=self.headers)
            soup = BeautifulSoup(main_page.text, 'html.parser')
            token = soup.find('input', {'name': '_token'})['value']
            
            # Then make the TTS request
            url = 'https://www.luyinzhushou.com/voice/convert'
            data = {
                '_token': token,
                'text': text,
                'voice': 'zh-CN-YunxiNeural',
                'style': 'general',
                'rate': '0%',
                'pitch': '0%',
                'format': 'mp3',
            }
            
            response = session.post(url, data=data, headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    audio_url = result.get('url')
                    if audio_url:
                        audio_response = session.get(audio_url, headers=self.headers)
                        timestamp = int(time.time())
                        filename = os.path.join(self.output_dir, f'luyinzhushou_{timestamp}.mp3')
                        with open(filename, 'wb') as f:
                            f.write(audio_response.content)
                        return f"Success! Audio saved as {filename}"
            return f"Error from luyinzhushou.com: {response.status_code}"
        except Exception as e:
            return f"Error with luyinzhushou.com: {str(e)}"

    def ai_speaker_net(self, text):
        """Convert text to speech using ai-speaker.net"""
        try:
            # This is a simplified version and might need adjustments based on the actual website's API
            url = 'https://ai-speaker.net/api/tts'
            data = {
                'text': text,
                'language': 'zh-CN',
                'speed': 1.0,
                'pitch': 1.0,
                'volume': 1.0,
            }
            
            response = requests.post(url, json=data, headers=self.headers)
            if response.status_code == 200:
                timestamp = int(time.time())
                filename = os.path.join(self.output_dir, f'ai_speaker_{timestamp}.mp3')
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return f"Success! Audio saved as {filename}"
            return f"Error from ai-speaker.net: {response.status_code}"
        except Exception as e:
            return f"Error with ai-speaker.net: {str(e)}"

def main():
    print("中文TTS转换器 - 支持多种免费TTS服务\n" + "="*50)
    
    # Get user input
    text = input("请输入要转换为语音的中文文本: ")
    if not text.strip():
        print("错误: 输入不能为空")
        return
    
    # Initialize TTS converter
    tts = TTSConverter()
    
    print("\n正在转换，请稍候...\n")
    
    # Try each TTS service
    print("1. 使用 ttsmaker.cn 转换中...")
    result1 = tts.tts_maker_cn(text)
    print(f"   {result1}")
    
    print("\n2. 使用 luyinzhushou.com 转换中...")
    result2 = tts.luyinzhushou(text)
    print(f"   {result2}")
    
    print("\n3. 使用 ai-speaker.net 转换中...")
    result3 = tts.ai_speaker_net(text)
    print(f"   {result3}")
    
    print("\n转换完成！请查看输出文件夹中的MP3文件。")

if __name__ == "__main__":
    main()
