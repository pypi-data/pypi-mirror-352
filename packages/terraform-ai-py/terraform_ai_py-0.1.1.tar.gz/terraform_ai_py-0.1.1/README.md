# Assistente IA do Terraform com Python

![banner](img/banner.png)

```bash

terraform-ai/
├── main.py
├── ai.py           # Módulo que conversa com OpenAI ou Ollama
├── cli.py          # Entrada de terminal
├── prompts.py      # Prompts base para reutilizar
├── templates/      # (Opcional) templates .tf
└── generated/      # Arquivos gerados

```

Eai galera, por questão de estudos e quem sabe virar algo que seja usado pela comunidade, estou desenvolvendo um assistente de IA para Terraform usando python chamado **terraform-ai-py**. Muito semelhante ao [kubectl-ai](https://github.com/sozercan/kubectl-ai).

É uma ferramenta de linha de comando que usa modelos de linguagem (LLMs) para gerar código Terraform com base em solicitações em linguagem natural. Seu principal objetivo é acelerar a criação de infraestrutura como código de forma inteligente e automatizada.

Atualmente, o projeto utiliza nativamente o Ollama, permitindo o uso de modelos LLMs locais, como LLaMA 3, Mistral, entre outros, sem depender da nuvem ou de APIs pagas.

Essa abordagem oferece:

✅ Privacidade dos dados

✅ Baixo custo (sem taxas de uso de API)

✅ Execução local e offline


## Fluxo geral

```bash
[main.py] → [cli.py] → [ai.py + prompts.py] → [templates/] → [generated/main.tf]
```

### Requisitos

- Ollama com modelos LLM configurado
- python >=3

#### dependências pip

```bash
openai>=0.28.1      # cliente OpenAI (compatível com ChatCompletion)
requests>=2.31.0    # usado para conversar com o Ollama local
python-dotenv>=1.0  # opcional: carregar variáveis do .env

python3 -m venv .venv 
source .venv/bin/activate   

pip install --upgrade pip
pip install -r requirements.txt

```

## Ideias futuras (em construção)

Em breve, o projeto incluirá suporte à API da OpenAI (GPT-4, GPT-3.5), permitindo aos usuários escolher entre:

Modelos locais via Ollama

Modelos na nuvem via OpenAI

Essa flexibilidade permitirá escolher o melhor equilíbrio entre velocidade, precisão e custo, de acordo com o seu ambiente.

Se quiser contribuir simbora.