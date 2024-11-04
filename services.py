import json
import faiss
import requests
from sentence_transformers import SentenceTransformer
from environs import Env
from openai import OpenAI


env = Env()
env.read_env()
model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')
OPENAI_API_KEY = env.str("OPENAI_API_KEY")
OPENROUTER_API_KEY = env.str("OPENROUTER_API_KEY")
GROK_API_KEY = env.str("GROK_API_KEY")


def load_and_index_api_data():
    with open("api_data.txt", "r", encoding="utf-8") as file:
        data = file.read().split("\n\n")

    embeddings = model.encode(data)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return data, index


def get_relevant_segment(query: str, api_data_segments, api_index, top_k=1) -> str:
    query_embedding = model.encode([query])
    _, indices = api_index.search(query_embedding, top_k)
    relevant_segments = [api_data_segments[idx] for idx in indices[0]]
    return "\n\n".join(relevant_segments)


async def get_llm_response(prompt: str, model: str, instructions: str, api_data: str, provider: str) -> str:
    full_prompt = f"{instructions}\n\n{api_data}\n\n{prompt}"

    if provider == "openai":
        client = OpenAI(
            api_key=OPENAI_API_KEY,
        )
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content

    elif provider == "openrouter":
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
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"Ошибка OpenRouter: {response.status_code} - {response.text}")

    elif provider == "grok":
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

    else:
        raise ValueError("Неверный провайдер модели")
