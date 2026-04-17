import requests
import json

url = "http://localhost:11434/api/chat"


def read_prompt_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file '{filename}' not found")
    except Exception as e:
        raise Exception(f"Error reading prompt file: {str(e)}")


def llama3(prompt):
    data = {
        "model": "llama3.2",
        "messages": [
            {
                "role": "user",
                "content": prompt

            }
        ],
        "stream": False,
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()["message"]["content"]


prompt = read_prompt_file('localization_tests/reason_prompt.txt')
response = llama3(prompt)
print(response)
