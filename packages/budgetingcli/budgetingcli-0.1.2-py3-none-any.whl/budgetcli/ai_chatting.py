import ollama
import json
from rich.console import Console
import datetime

console = Console()

today = datetime.datetime.now()
SYSTEM_PROMPT = (
    f"You are a helpful budgeting assistant. Give clear advice based on the user's financial goals and spending patterns. All goals the user has is for a monthly basis not daily so keep that in mind! You are typing in the CLI so there isn't much need to use markdown formatting, format pretty within the CLI as best as you can. Be kind and respectful. user information will be given to you in a nice format that you will leverage throughout all responses to keep being personalized with the user. You are given today's date: {today.strftime('%Y-%m-%d')}. Think hard and be accurate. For stock questions remember to put Not Financial Advice (or say NFA) at the end!!! Avoid hallucinations. \n\n Do not hallucinate!"
)

def generate_advice(user_json, user_input):
    context = f"User: {user_json['username']}\nGoals: {json.dumps(user_json.get('goals', {}), indent=2)}\nSpending: {json.dumps(user_json.get('spending', {}), indent=2)}"

    full_prompt = f"/no_think {context}\n\nUser question: {user_input}"

    messages= [
            { "role": "system", "content": SYSTEM_PROMPT },
            { "role": "user", "content": full_prompt }
        ]
    
    for part in ollama.chat('qwen3:8b', messages=messages, stream=True):
        print(part['message']['content'], end='', flush=True)
    
    return