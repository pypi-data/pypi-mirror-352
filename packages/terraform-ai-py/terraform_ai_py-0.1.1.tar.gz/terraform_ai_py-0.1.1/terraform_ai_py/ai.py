import os
import requests
import openai

USE_OLLAMA = True  # Mude para False se quiser usar OpenAI

def generate_terraform(prompt: str) -> str:
    base_prompt = f"""
Você é um especialista em Terraform. Gere o código Terraform com base no seguinte pedido do usuário:

{prompt}

Retorne apenas o código entre ```, sem explicações.
"""

    if USE_OLLAMA:
        response = requests.post(
            "http://192.168.1.100:11434/api/generate",
            json={"model": "codellama", "prompt": base_prompt, "stream": False}
        )
        return response.json()["response"]

    else:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": base_prompt}],
            temperature=0.2
        )
        return response.choices[0].message["content"]
1