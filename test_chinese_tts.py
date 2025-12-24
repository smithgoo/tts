import asyncio
import edge_tts
import os

async def test_chinese_tts():
    # Create output directory if it doesn't exist
    os.makedirs('test_output', exist_ok=True)
    
    # Test with different Chinese texts
    test_texts = [
        "你好，这是一个测试。",
        "欢迎使用中文语音合成。",
        "今天天气真好！"
    ]
    
    # Test with different voices
    voices = [
        'zh-CN-YunxiNeural',  # 男声
        'zh-CN-XiaoxiaoNeural',  # 女声
    ]
    
    for i, text in enumerate(test_texts):
        for voice in voices:
            try:
                # Create output filename
                output_file = os.path.join('test_output', f'test_{i}_{voice}.mp3')
                
                # Generate speech with minimal parameters
                communicate = edge_tts.Communicate(
                    text=text,
                    voice=voice
                )
                
                print(f"Generating speech for: '{text}' with voice: {voice}")
                await communicate.save(output_file)
                print(f"Success! Output saved to: {output_file}")
                
            except Exception as e:
                print(f"Error with voice {voice}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_chinese_tts())
