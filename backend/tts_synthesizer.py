"""
Text-to-Speech using OpenAI TTS
"""

import os
import base64
import openai

class TTSSynthesizer:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI(api_key=self.api_key)
        self.voice = "alloy"
    
    async def synthesize(self, text):
        """Convert text to speech and return base64 audio"""
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.voice,
                input=text
            )
            
            # Get audio content
            audio_data = response.content
            
            # Convert to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            print(f"TTS generated: {len(text)} chars")
            return audio_base64
            
        except Exception as e:
            print(f"TTS error: {e}")
            return None
