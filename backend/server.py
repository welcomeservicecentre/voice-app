#!/usr/bin/env python3
"""
Voice AI WebSocket Server
"""

import asyncio
import websockets
import json
import os
import base64
import tempfile
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
from transcriber import Transcriber
from kimi_client import KimiClient
from tts_synthesizer import TTSSynthesizer

# Configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 10000))

class VoiceServer:
    def __init__(self):
        self.transcriber = Transcriber()
        self.kimi = KimiClient()
        self.tts = TTSSynthesizer()
        self.clients = set()
    
    async def register(self, websocket):
        self.clients.add(websocket)
        print(f"Client connected. Total: {len(self.clients)}")
    
    async def unregister(self, websocket):
        self.clients.discard(websocket)
        print(f"Client disconnected. Total: {len(self.clients)}")
    
    async def handle_client(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        finally:
            await self.unregister(websocket)
    
    async def process_message(self, websocket, message):
        try:
            data = json.loads(message)
            
            if data.get('type') == 'audio':
                # Process audio
                audio_data = base64.b64decode(data['data'])
                
                # Save to temp file
                with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
                    f.write(audio_data)
                    temp_path = f.name
                
                # Transcribe
                text = await self.transcriber.transcribe(temp_path)
                os.unlink(temp_path)
                
                if text:
                    # Send transcription
                    await websocket.send(json.dumps({
                        'type': 'transcription',
                        'text': text
                    }))
                    
                    # Get AI response
                    response = await self.kimi.get_response(text)
                    
                    # Generate TTS
                    audio_base64 = await self.tts.synthesize(response)
                    
                    # Send response
                    await websocket.send(json.dumps({
                        'type': 'response',
                        'text': response,
                        'audio': audio_base64
                    }))
                    
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))

async def main():
    server = VoiceServer()
    
    print(f"Starting server on {HOST}:{PORT}")
    
    async with websockets.serve(
        server.handle_client,
        HOST,
        PORT,
        ping_interval=20,
        ping_timeout=10
    ):
        print(f"Server running at ws://{HOST}:{PORT}")
        await asyncio.Future()  # Run forever

if __name__ == '__main__':
    asyncio.run(main())
