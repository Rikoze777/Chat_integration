import requests
from environs import Env
from openai import OpenAI


env = Env()
env.read_env()
OPENAI_API_KEY = env.str("OPENAI_API_KEY")
OPENROUTER_API_KEY = env.str("OPENROUTER_API_KEY")
GROK_API_KEY = env.str("GROK_API_KEY")


async def openai_response(prompt, model):
    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt}]
    )
    return response.choices[0].message.content


async def openrouter_response(prompt, model):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
    data={
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "top_p": 1,
        "temperature": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "repetition_penalty": 1,
        "top_k": 0,
        
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        if "error" in response_data:
                    error_message = response_data["error"].get("message")
                    raise Exception(f"OpenRouter Error: {error_message}")
        return response_data['choices'][0]['message']['content']
    else:
        raise Exception(f"Ошибка OpenRouter: {response.status_code} - {response.text}")


async def get_grok_response(prompt, model):
    headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
    data = {"messages": [
        {
        "role": "system",
        "content": "Ты программист, который пишет API"
        },
        {
        "role": "user",
        "content": prompt
        }
        ],
        "model": model,
        "stream": False,
        "temperature": 0
    }
    response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise Exception(f"Ошибка OpenRouter: {response.status_code} - {response.text}")


async def get_llm_response(prompt: str, model: str, provider: str) -> str:

    if provider == "openai":
        response = await openai_response(prompt, model)

    elif provider == "openrouter":
        response = await openrouter_response(prompt, model)

    elif provider == "grok":
        response = await get_grok_response(prompt, model)

    else:
        raise ValueError("Неверный провайдер модели")
