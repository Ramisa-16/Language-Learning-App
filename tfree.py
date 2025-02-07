import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

openai.api_key = ""  # Replace with your actual OpenAI API key

app = FastAPI()
data = []
languages = {
    'en': 'English',
    'es': 'Spanish',
    'zh': 'Chinese (Mandarin)',
    'fr': 'French',
    'ar': 'Arabic',
    'sy': 'Egyptian Arabic'
}

class TextRequest(BaseModel):
    text: str
    language: str 

def respond_to_text(text: str, language: str) -> str:
    """Uses OpenAI to respond to text-based conversation."""
    try:
        user_language = languages.get(language, language)
        messages = [
            {"role": "system", "content": f"""You are an assistant that speaks and responds in the language of the user ({languages.get(language, language)}).
            """},
            {"role": "user", "content": f"Here is the text:\n\n{text}"}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4",  
            messages=messages,
            max_tokens=2000,  
            temperature=0.7 
        )
        response_text = response['choices'][0]['message']['content'].strip()

        return response_text

    except openai.error.OpenAIError as e:
        raise HTTPException(status_code=500, detail=str(e))



