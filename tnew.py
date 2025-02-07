import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import difflib
import re
import langid

openai.api_key = ""  

app = FastAPI()

class TextRequest(BaseModel):
    text: str
    language: str 

languages = {
    'en': 'English',
    'es': 'Spanish',
    'zh': 'Chinese (Mandarin)',
    'fr': 'French',
    'ar': 'Arabic',
    'sy': 'Egyptian Arabic'
}

def split_words(text: str):
    return re.findall(r'\b\w+\b|[^\w\s]', text, re.UNICODE)

def clean_text(text: str):
    """Ensure that the input is a string before applying regex."""
    if not isinstance(text, str):
        return ""
    return re.sub(r'[\+\^]', '', text) 

def correct_grammar(text, language, level) -> str:
    """Uses OpenAI to correct grammar and sentence structure or generate context-based responses."""
    try:
        if text.lower() in ["hi", "hello"]:
            return "Hello, How can I assist you?"
        if level == "Beginner":
            prompt = f"""
            You are an assistant that speaks and responds in the language of the user ({languages.get(language, language)}). 
            The user is a beginner. If the sentence contains grammatical errors, correct them in a simple and clear manner, keeping the explanation short.
            If the sentence is grammatically correct, provide a short response or answer based on the context.
            """
        elif level == "Intermediate":
            prompt = f"""
            You are an assistant that speaks and responds in the language of the user ({languages.get(language, language)}). 
            The user is at an intermediate level. If the sentence contains grammatical errors, correct them while maintaining the original meaning and providing a more detailed explanation.
            If the sentence is grammatically correct, provide a more detailed response based on the context.
            """
        elif level == "Advanced":
            prompt = f"""
            You are an assistant that speaks and responds in the language of the user ({languages.get(language, language)}). 
            The user is at an advanced level. Correct any grammatical errors and provide advanced corrections and context-based explanations.
            If the sentence is grammatically correct, provide an in-depth response based on the context.
            """
        else:
            prompt = f"""
            You are an assistant that speaks and responds in the language of the user ({languages.get(language, language)}). 
            If the sentence contains grammatical errors, correct them while preserving the original meaning.
            If the sentence is grammatically correct, provide a response based on the context.
            """
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Here is the text:\n\n{text}"}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4", 
            messages=messages,
            max_tokens=2000, 
            temperature=0.7  
        )

        corrected_text = response['choices'][0]['message']['content'].strip()
        print(f"OpenAI response: {corrected_text}")
        if "grammatically incorrect" in corrected_text:
            corrected_sentence = corrected_text.replace("Your sentence is grammatically incorrect.", "").strip()
            return f"Your sentence is grammatically incorrect: {corrected_sentence}"
        elif corrected_text:
            if "?" in text:
                return f"The answer to your question '{text}' is: {corrected_text}"
            else:
                return corrected_text

    except openai.error.OpenAIError as e:
        raise HTTPException(status_code=500, detail=str(e))

def clean_text_get(text):
    return re.sub(r'[\s\n]+', '', text).strip()  
def clean_data(text_data):
    print(f"Received data type: {type(text_data)}") 
    if not isinstance(text_data, list): 
        raise ValueError("The input must be a list of dictionaries.")
    
    for item in text_data:
        if not isinstance(item, dict): 
            raise ValueError("Each item in the list must be a dictionary.")

        if "text" not in item: 
            raise KeyError("'text' key not found in item.")
        
        original_text = item["text"]
        cleaned_text = re.sub(r'(<span[^>]*>)(.*?)(</span>)', lambda m: f'{m.group(1)}{clean_text_get(m.group(2))}{m.group(3)}', original_text)
        item["text"] = cleaned_text
        print("cleaned_text", cleaned_text)

    return text_data

def mark_differences(original: str, corrected: str) -> dict:
    """Highlights the differences between original and corrected text."""
    original = clean_text(original)
    corrected = clean_text(corrected)

    original_words = split_words(original)
    corrected_words = split_words(corrected)

    original_highlighted, corrected_highlighted = [], []
    diff = difflib.ndiff(original_words, corrected_words)

    for word in diff:
        if word.startswith("- "): 
            original_highlighted.append(f'<span style="color: red;">{word[2:]}</span>')
        elif word.startswith("+ "):  
            corrected_highlighted.append(f'<span style="color: green;">{word[2:]}</span>')
        else: 
            word_cleaned = word[2:]
            original_highlighted.append(f'<span style="color: #8E44AD;">{word_cleaned}</span>')  
            corrected_highlighted.append(f'<span style="color: #4B98E5;">{word_cleaned}</span>')  

    
    original_text= " ".join(original_highlighted)
    corrected_text= " ".join(corrected_highlighted)
    print("original_text",original_text)

    return {
        "original_text": clean_text(original_text),
        "corrected_text": clean_text(corrected_text)
    }

data = []

