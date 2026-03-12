import ollama
from src.utils.json_utils import load_json
config_json = load_json("config/config_files.json")["app.py"]

def run_llm(query, system_prompt):

    response = ollama.chat(
        model=config_json["OLLAMA_MODEL"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )

    return response["message"]["content"]