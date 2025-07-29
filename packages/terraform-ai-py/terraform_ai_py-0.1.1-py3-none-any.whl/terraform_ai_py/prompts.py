def base_prompt(user_input: str) -> str:
    return f"""
Você é um assistente especialista em Terraform. Gere o código Terraform necessário para a seguinte solicitação:

{user_input}

Responda apenas com o código, sem explicações.
"""
