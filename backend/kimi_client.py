"""
Kimi AI Client for responses
"""

import os
import openai

class KimiClient:
    def __init__(self):
        self.api_key = os.getenv('KIMI_API_KEY')
        self.base_url = os.getenv('KIMI_BASE_URL', 'https://api.moonshot.cn/v1')
        self.model = os.getenv('KIMI_MODEL', 'kimi-k2-5')
        
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    async def get_response(self, text):
        """Get AI response from Kimi"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Keep responses concise and natural."},
                    {"role": "user", "content": text}
                ],
                max_tokens=500
            )
            
            reply = response.choices[0].message.content
            print(f"AI response: {reply}")
            return reply
            
        except Exception as e:
            print(f"Kimi error: {e}")
            return "Sorry, I couldn't process that. Please try again."
