import warnings
from urllib3.exceptions import NotOpenSSLWarning

# Suppress the NotOpenSSLWarning
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import time
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'static/audio'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Available TTS services with their settings
TTS_SERVICES = {
    'ttsmaker': {
        'name': 'TTSMaker',
        'voices': [
            # Female voices
            {'id': 0, 'name': '女声1 - 标准女声'},
            {'id': 1, 'name': '女声2 - 温柔女声'},
            {'id': 2, 'name': '女声3 - 甜美女生'},
            {'id': 3, 'name': '女声4 - 知性女声'},
            # Male voices
            {'id': 4, 'name': '男声1 - 标准男声'},
            {'id': 5, 'name': '男声2 - 浑厚男声'},
            {'id': 6, 'name': '男声3 - 阳光男声'},
            {'id': 7, 'name': '男声4 - 磁性男声'},
            # Child voices
            {'id': 8, 'name': '童声1 - 小男孩'},
            {'id': 9, 'name': '童声2 - 小女孩'},
            # Special voices
            {'id': 10, 'name': '方言 - 四川话'},
            {'id': 11, 'name': '方言 - 广东话'},
            {'id': 12, 'name': '方言 - 台湾腔'},
            {'id': 13, 'name': '英文 - 美式女声'},
            {'id': 14, 'name': '英文 - 英式男声'},
        ],
        'speeds': [0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
        'pitches': [0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
        'volumes': [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
    },
    'ai_speaker': {
        'name': 'AI Speaker',
        'voices': [
            # Chinese voices
            {'id': 'zh-CN-XiaoxiaoNeural', 'name': '晓晓 - 标准女声'},
            {'id': 'zh-CN-YunxiNeural', 'name': '云溪 - 标准男声'},
            {'id': 'zh-CN-YunjianNeural', 'name': '云健 - 新闻男声'},
            {'id': 'zh-CN-XiaoyiNeural', 'name': '小艺 - 温柔女声'},
            {'id': 'zh-CN-YunyangNeural', 'name': '云扬 - 专业男声'},
            # English voices
            {'id': 'en-US-JennyNeural', 'name': 'Jenny - 美式女声'},
            {'id': 'en-US-GuyNeural', 'name': 'Guy - 美式男声'},
            {'id': 'en-GB-SoniaNeural', 'name': 'Sonia - 英式女声'},
            {'id': 'en-GB-RyanNeural', 'name': 'Ryan - 英式男声'},
            # Japanese voices
            {'id': 'ja-JP-NanamiNeural', 'name': '七海 - 日语女声'},
            {'id': 'ja-JP-KeitaNeural', 'name': '圭太 - 日语男声'},
            # Korean voices
            {'id': 'ko-KR-SunHiNeural', 'name': '선희 - 韩语女声'},
            {'id': 'ko-KR-InJoonNeural', 'name': '인준 - 韩语男声'},
        ],
        'speeds': ['x-slow', 'slow', 'medium', 'fast', 'x-fast'],
        'pitches': ['x-low', 'low', 'medium', 'high', 'x-high'],
        'volumes': ['silent', 'x-soft', 'soft', 'medium', 'loud', 'x-loud']
    }
}

class TTSConverter:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def tts_maker(self, text, voice_id=0, speed=1.0, pitch=1.0, volume=1.0):
        """Convert text to speech using edge-tts library"""
        try:
            import edge_tts
            import asyncio
            import os
            from datetime import datetime
            
            # Create output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Available Chinese voices in edge-tts
            chinese_voices = [
                'zh-CN-YunxiNeural',    # 男声
                'zh-CN-XiaoxiaoNeural', # 女声
                'zh-CN-YunjianNeural',  # 男声（带效果）
                'zh-CN-XiaoyiNeural',   # 女声（带效果）
                'zh-TW-HsiaoChenNeural', # 台湾女声
                'zh-HK-HiuGaaiNeural'   # 香港女声
            ]
            
            # Select voice based on voice_id
            voice = chinese_voices[voice_id % len(chinese_voices)]
            
            # Generate a unique filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'tts_output_{timestamp}.mp3'
            filepath = os.path.join(self.output_dir, filename)
            
            async def generate_speech():
                communicate = edge_tts.Communicate(
                    text=text,
                    voice=voice
                )
                await communicate.save(filepath)
            
            # Run the async function
            asyncio.run(generate_speech())
            
            # Verify the file was created
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                return {
                    'success': True, 
                    'filename': filename, 
                    'service': f'Edge TTS ({voice})'
                }
            else:
                return {'success': False, 'error': 'Failed to generate audio file'}
                
        except Exception as e:
            return {'success': False, 'error': f'Error with Edge TTS: {str(e)}'}

    def luyinzhushou(self, text, voice_id=0, speed=1.0, pitch=1.0, volume=1.0):
        """Convert text to speech using edge-tts as fallback for luyinzhushou"""
        try:
            # Use edge-tts as a fallback
            # Map voice_id to a different range if needed
            # voice_id 0 -> 0, 1 -> 1, etc.
            return self.tts_maker(text, voice_id=voice_id % 6, speed=speed, pitch=pitch, volume=volume)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error with TTS service: {str(e)}'
            }

    def google_tts(self, text, voice_id='zh-CN-Wavenet-A', speed=1.0, pitch=1.0, volume=1.0):
        """Convert text to speech using edge-tts as fallback for Google TTS"""
        try:
            # Use edge-tts as a fallback
            return self.tts_maker(text, voice_id=0, speed=speed, pitch=pitch, volume=volume)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error with TTS service: {str(e)}'
            }

# Initialize TTS converter
tts_converter = TTSConverter(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html', services=TTS_SERVICES)

@app.route('/api/convert', methods=['POST'])
def convert_text():
    data = request.get_json()
    text = data.get('text', '').strip()
    service = data.get('service', 'ttsmaker')
    
    if not text:
        return jsonify({'success': False, 'error': '请输入要转换的文本'}), 400
    
    try:
        if service == 'ttsmaker':
            voice_id = int(data.get('voice_id', 0))
            speed = float(data.get('speed', 1.0))
            pitch = float(data.get('pitch', 1.0))
            volume = float(data.get('volume', 1.0))
            result = tts_converter.tts_maker(text, voice_id, speed, pitch, volume)
        elif service == 'ai_speaker':
            voice_id = data.get('voice_id', 'zh-CN-XiaoxiaoNeural')
            speed = data.get('speed', 'medium')
            pitch = data.get('pitch', 'medium')
            volume = data.get('volume', 'medium')
            # Use tts_maker as a fallback for now
            result = tts_converter.tts_maker(text, 0, 1.0, 1.0, 1.0)
        else:
            return jsonify({'success': False, 'error': '不支持的TTS服务'}), 400
            
        if result['success'] and 'filename' in result:
            result['download_url'] = f'/download/{result["filename"]}'
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'转换失败: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Changed to 5001 to avoid port conflict
