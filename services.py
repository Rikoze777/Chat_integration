import faiss
import openai
import requests
from sentence_transformers import SentenceTransformer
from environs import Env


env = Env()
env.read_env()
model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')
OPENAI_API_KEY = env.str("OPENAI_API_KEY")
OPENROUTER_API_KEY = env.str("OPENROUTER_API_KEY")


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
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": full_prompt}]
        )
        return response.choices[0].message["content"].strip()

    elif provider == "openrouter":
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
        data = {
            "model": model,
            "prompt": full_prompt
        }
        response = requests.post("https://api.openrouter.com/v1/completions", headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json().get("choices")[0].get("text").strip()
        else:
            raise Exception(f"Ошибка OpenRouter: {response.status_code} - {response.text}")

    else:
        raise ValueError("Неверный провайдер модели")

