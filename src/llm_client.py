# src/llm_client.py
import requests
import json

def call_llm(prompt: str, model: str = "qwen2:1.5b") -> str:
    """
    Call Ollama LLM with a prompt and return the full response text.
    - prompt: the text you want to send to the model
    - model: the Ollama model name (default: qwen2:1.5b)
    """
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt}

    response = requests.post(url, json=payload, stream=True)
    output = ""

    for line in response.iter_lines():
        if line:
            parsed = json.loads(line.decode("utf-8"))
            output += parsed.get("response", "")

    return output.strip()