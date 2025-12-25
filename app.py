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
            # Chinese voices - using actual TTSMaker IDs
            {'id': 1504, 'name': '潇潇-热门推荐通用女声 - Female'},
            {'id': 349, 'name': '阿佐-标准女声 - Female'},
            {'id': 350, 'name': '云希-标准女声 - Female'},
            {'id': 351, 'name': '云夏-标准女声 - Female'},
            {'id': 352, 'name': '云健-新闻男声 - Male'},
            {'id': 353, 'name': '云杰-新闻男声 - Male'},
            {'id': 354, 'name': '云飞-新闻男声 - Male'},
            {'id': 355, 'name': '云博-新闻男声 - Male'},
            {'id': 356, 'name': '云瑞-新闻男声 - Male'},
            {'id': 357, 'name': '云朵-儿童女声 - Female'},
            {'id': 358, 'name': '云亮-儿童男声 - Male'},
            {'id': 359, 'name': '云阳-专业男声 - Male'},
            {'id': 360, 'name': '云云-儿童女声 - Female'},
            {'id': 361, 'name': '云峰-新闻男声 - Male'},
            {'id': 362, 'name': '云伟-新闻男声 - Male'},
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

    def tts_maker(self, text, voice_id=1504, speed=1.0, pitch=1.0, volume=1.0):
        """Convert text to speech using the real TTSMaker API"""
        try:
            import requests
            import os
            from datetime import datetime
            
            # Create output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)
            
            # TTSMaker API endpoint
            url = 'https://ttsmaker.cn/api/tts'
            
            # Prepare the request data
            data = {
                'text': text,
                'voice_id': voice_id,  # Use the actual voice ID from TTSMaker
                'speed': speed,
                'volume': volume,
                'pitch': pitch,
                'audio_format': 'mp3',
                'audio_speed': speed,
                'audio_volume': volume,
                'audio_norm': '0',
                'text_paragraph_pause_time': '0',
                'background_music_volume': '0',
                'background_music_speed': '1',
                'speech_rate': speed,
                'pitch_rate': pitch,
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://ttsmaker.cn/',
                'Origin': 'https://ttsmaker.cn',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }
            
            # Make the API request
            response = requests.post(url, data=data, headers=headers)
            
            if response.status_code == 200:
                # Generate a unique filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'ttsmaker_{timestamp}.mp3'
                filepath = os.path.join(self.output_dir, filename)
                
                # Save the audio response
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                # Verify the file was created
                if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                    return {
                        'success': True, 
                        'filename': filename, 
                        'service': f'TTSMaker (ID: {voice_id})'
                    }
                else:
                    return {'success': False, 'error': 'Failed to save audio file'}
            else:
                return {'success': False, 'error': f'API request failed with status {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': f'Error with TTSMaker API: {str(e)}'}

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

    def ai_speaker(self, text, voice_id='zh-CN-XiaoxiaoNeural', speed='medium', pitch='medium', volume='medium'):
        """Convert text to speech using AI Speaker service with edge-tts"""
        try:
            import edge_tts
            import asyncio
            import os
            from datetime import datetime
            
            # Convert string parameters to appropriate values for edge_tts
            # Map string values to numeric values for edge-tts
            speed_map = {
                'x-slow': '-50%', 'slow': '-25%', 'medium': '0%', 'fast': '25%', 'x-fast': '50%',
                # Also handle numeric values that might be passed as strings
                '0.5': '-50%', '0.75': '-25%', '1.0': '0%', '1.25': '25%', '1.5': '50%', '2.0': '100%'
            }
            pitch_map = {
                'x-low': '-50%', 'low': '-25%', 'medium': '0%', 'high': '25%', 'x-high': '50%',
                # Also handle numeric values that might be passed as strings
                '0.5': '-50%', '0.75': '-25%', '1.0': '0%', '1.25': '25%', '1.5': '50%', '2.0': '100%'
            }
            volume_map = {
                'silent': '0%', 'x-soft': '25%', 'soft': '50%', 'medium': '75%', 'loud': '90%', 'x-loud': '100%',
                # Also handle numeric values that might be passed as strings
                '0.5': '50%', '0.75': '75%', '1.0': '100%', '1.25': '125%', '1.5': '150%', '2.0': '200%'
            }
            
            # Get the mapped values or default to medium if not found
            mapped_speed = speed_map.get(str(speed), '0%')
            mapped_pitch = pitch_map.get(str(pitch), '0%')
            mapped_volume = volume_map.get(str(volume), '100%')
            
            # Create output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Generate a unique filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'ai_speaker_{timestamp}.mp3'
            filepath = os.path.join(self.output_dir, filename)
            
            async def generate_speech():
                # Create SSML (Speech Synthesis Markup Language) to include voice parameters
                ssml_text = f"""<speak>
                    <voice name="{voice_id}">
                        <prosody rate="{mapped_speed}" pitch="{mapped_pitch}" volume="{mapped_volume}">
                            {text}
                        </prosody>
                    </voice>
                </speak>"""
                
                communicate = edge_tts.Communicate(
                    text=ssml_text,
                    voice=voice_id
                )
                await communicate.save(filepath)
            
            # Run the async function
            asyncio.run(generate_speech())
            
            # Verify the file was created
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                return {
                    'success': True, 
                    'filename': filename, 
                    'service': f'AI Speaker ({voice_id})'
                }
            else:
                return {'success': False, 'error': 'Failed to generate audio file'}
                
        except Exception as e:
            return {'success': False, 'error': f'Error with AI Speaker: {str(e)}'}

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
            # Use ai_speaker method for AI Speaker service
            result = tts_converter.ai_speaker(text, voice_id, speed, pitch, volume)
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
