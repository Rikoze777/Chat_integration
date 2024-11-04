import faiss
import openai


def load_and_index_api_data(model):
    with open("api_data.txt", "r", encoding="utf-8") as file:
        data = file.read().split("\n\n")

    embeddings = model.encode(data)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return data, index, embeddings


def get_relevant_segment(query, model, api_index, api_data_segments, top_k=1) -> str:
    query_embedding = model.encode([query])
    _, indices = api_index.search(query_embedding, top_k)
    relevant_segments = [api_data_segments[idx] for idx in indices[0]]
    return "\n\n".join(relevant_segments)


async def get_llm_response(prompt, model, instructions, api_index, api_data_segments) -> str:
    relevant_api_data = get_relevant_segment(prompt, model, api_index, api_data_segments)

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": instructions},
                  {"role": "user", "content": f"{relevant_api_data}\n\n{prompt}"}]
    )
    return response.choices[0].message["content"].strip()
