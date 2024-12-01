import requests
from environs import Env
from openai import OpenAI


env = Env()
env.read_env()
OPENAI_API_KEY = env.str("OPENAI_API_KEY")
OPENROUTER_API_KEY = env.str("OPENROUTER_API_KEY")
GROK_API_KEY = env.str("GROK_API_KEY")
OPENAI_MODEL = env.str("GPT_MODEL", "gpt-3.5-turbo")
OPENROUTER_MODEL = env.str("OPENROUTER_MODEL", "liquid/lfm-40b:free")
GROK_MODEL = env.str("GROK_MODEL", "grok-beta")


async def openai_response(prompt, query, model):
    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )
    if prompt != '':
        response = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": query
            }]
        )
    else:
         response = client.chat.completions.create(
            model=model,
            messages=[
            {
                "role": "user",
                "content": query
            }]
        )
    return response.choices[0].message.content


async def openrouter_response(prompt, query, model):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
    if prompt != '':
        data={
            "model": model,
            "messages": [{
                "role": "user",
                "content": query
            },
            {
                "role": "system",
                "content": prompt
            },
            ],
            "top_p": 1,
            "temperature": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "repetition_penalty": 1,
            "top_k": 0,
            
        }
    else:
         data={
            "model": model,
            "messages": [{
                "role": "user",
                "content": query
            },
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


async def get_grok_response(prompt, query, model):
    headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
    if prompt != '':
        data = {"messages": [
            {
            "role": "system",
            "content": prompt
            },
            {
            "role": "user",
            "content": query
            }
            ],
            "model": model,
            "stream": False,
            "temperature": 0
        }
    else:
        data = {"messages": [
            {
            "role": "user",
            "content": query
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


async def get_llm_response(query: str, prompt: str, provider: str) -> str:

    if provider == "openai":
        openai_model = OPENAI_MODEL
        response = await openai_response(prompt, query, openai_model)
        return response

    elif provider == "openrouter":
        openrouter_model = OPENROUTER_MODEL
        response = await openrouter_response(prompt, query, openrouter_model)
        return response

    elif provider == "grok":
        grok_model = GROK_MODEL
        response = await get_grok_response(prompt, query, grok_model)
        return response

    else:
        raise ValueError("Неверный провайдер модели")
