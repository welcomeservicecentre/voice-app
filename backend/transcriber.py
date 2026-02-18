"""
Speech-to-Text using OpenAI Whisper
"""

import whisper
import os

class Transcriber:
    def __init__(self, model_size="base"):
        print(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        print("Whisper model loaded")
    
    async def transcribe(self, audio_path):
        """Transcribe audio file to text"""
        try:
            result = self.model.transcribe(audio_path)
            text = result["text"].strip()
            print(f"Transcribed: {text}")
            return text
        except Exception as e:
            print(f"Transcription error: {e}")
            return None
