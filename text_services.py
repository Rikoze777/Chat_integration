import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


torch.cuda.empty_cache()

model_name = "Qwen/Qwen2.5-Coder-0.5B-Instruct"
device = "cuda" if torch.cuda.is_available() else "cpu"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    device_map="auto"
).to(device)

tokenizer = AutoTokenizer.from_pretrained(model_name)
file_path = 'test.txt'

with open(file_path, 'r', encoding='utf-8') as file:
    file_content = file.read()


MAX_TOKENS = 512
OVERLAP_TOKENS = 40


def generate_with_context(text, overlap_tokens=OVERLAP_TOKENS):
    responses = []
    text_segments = split_text_into_segments(text, MAX_TOKENS - overlap_tokens)

    for i, segment in enumerate(text_segments):
        prompt = f"Continue with the context: \n{segment}"
        
        model_inputs = tokenizer(prompt, return_tensors="pt", truncation=True).to(device)
        with torch.no_grad():
            generated_ids = model.generate(
                **model_inputs,
                max_new_tokens=1024
            )
        response = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        responses.append(response)
        
        if i < len(text_segments) - 1:
            next_segment = tokenizer.decode(generated_ids[0][-overlap_tokens:], skip_special_tokens=True)
            text_segments[i + 1] = next_segment + text_segments[i + 1]
    
    return " ".join(responses)


def split_text_into_segments(text, max_length):
    words = text.split()
    segments = []
    current_segment = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1  # Учёт пробела
        if current_length + word_length > max_length:
            segments.append(" ".join(current_segment))
            current_segment = []
            current_length = 0
        current_segment.append(word)
        current_length += word_length

    if current_segment:
        segments.append(" ".join(current_segment))
    
    return segments


print(generate_with_context(file_content))