import ollama
from config.settings import OLLAMA_MODEL

def run_llm(query, system_prompt):

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )

    return response["message"]["content"]