import io
import os
import openai
import tempfile
import speech_recognition as sr
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from gtts import gTTS
from langdetect import detect, DetectorFactory, LangDetectException
from pydub import AudioSegment
import difflib
import re
from googletrans import Translator 
from deep_translator import GoogleTranslator 
DetectorFactory.seed = 0  

app = FastAPI()

openai.api_key = "sk-svcacct-KBnnF-0KRobG1j17ah1p-jQ81c9HUGpdHZAsCawOMJSvaxoG2ozHgroUFedjkpT3BlbkFJrywiP4MDf-sqI9diCPyu0rT2M6rC1Ofeko-lK2u0qDDdR9Qgr4NGuCEBBczlUA"  # Replace with actual OpenAI API key

languages = {
    'en': 'en-US',
    'es': 'es-ES',
    'zh': 'zh-CN',
    'fr': 'fr-FR',
    'ar': 'ar-SA'
}

data = [] 

translator = Translator()  
 

def translate_text_in_html_dynamic(auidio, language: str):
    for item in auidio:
        print("language : ", language) 
        original_text = item["text"]
    
        translator = GoogleTranslator(source='auto', target=language)
        
        matches = re.findall(r'>([^<>]+)<', original_text)  
        translated_text = original_text
        
        print(f"Original Text: {original_text}") 

        for inner_text in matches:
            if inner_text.strip():  
                try:
                    translated_inner_text = translator.translate(inner_text.strip())
                    translated_inner_text = translated_inner_text if translated_inner_text else inner_text 
                    print(f"Original: {inner_text} -> Translated: {translated_inner_text}")  
                except Exception as e:
                    translated_inner_text = inner_text
                    print(f"Translation error: {e}")
                translated_text = translated_text.replace(inner_text, translated_inner_text, 1)
        item["text"] = translated_text

    return auidio


def split_words(text: str):
    return re.findall(r'\b\w+\b|[^\w\s]', text, re.UNICODE)

def clean_text(text: str):
    """Ensure that the input is a string before applying regex."""
    if not isinstance(text, str):
        return ""
    return re.sub(r'[\+\^]', '', text)  

def mark_differences(original: str, corrected: str) -> dict:
    """Highlights the differences between original and corrected text."""
    original = clean_text(original)
    corrected = clean_text(corrected)
    print(corrected)
    original_words = split_words(original)
    corrected_words = split_words(corrected)

    original_highlighted, corrected_highlighted = [], []
    diff = difflib.ndiff(original_words, corrected_words)

    for word in diff:
        if word.startswith("- "): 
            original_highlighted.append(f'<span style="color: red;">{clean_text(word[2:])}</span>')
        elif word.startswith("+ "): 
            corrected_highlighted.append(f'<span style="color: green;">{clean_text(word[2:])}</span>')
        else:  
            word_cleaned = {clean_text(word[2:])}
            original_highlighted.append(f'<span style="color: #8E44AD;">{word_cleaned}</span>') 
            corrected_highlighted.append(f'<span style="color: #4B98E5;">{word_cleaned}</span>')  

    return {
        "original_text": " ".join(original_highlighted),
        "corrected_text": " ".join(corrected_highlighted)
    }

def correct_grammar(text: str, language: str) -> str:
   

        if text.lower() in ["hi", "hello"]:
            return "Hello, How can I assist you?"
        print(text,language)  
        messages = [
            {"role": "system", "content": f"""
            You are an assistant that speaks and responds in the language of the user ({languages.get(language, language)}). 
            If the sentence contains grammatical errors, correct them while preserving the original meaning. 
            If the sentence is grammatically correct, provide a response based on the context:
               - If it's a question (like "What is the capital of France?"), answer it.
               - If it's a statement (like "I like pizza"), respond accordingly.
            
            For both cases:
            - If the sentence is grammatically incorrect, say "Your sentence is grammatically incorrect. The correct sentence is: <corrected sentence>."
            - If the sentence is grammatically correct, provide a response based on the context.
            - Be concise and direct in your response.
            """},
            {"role": "user", "content": f"Here is the text:\n\n{text}"}
        
        ]
        print(languages.get(language, language))
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=2000, 
            temperature=0.7  
        )

        print(response)

        corrected_text = response['choices'][0]['message']['content'].strip()
        print(f"OpenAI response: {corrected_text}")
        if "grammatically incorrect" in corrected_text:
            corrected_sentence = corrected_text.replace("Your sentence is grammatically incorrect.", "").strip()
            return f"Your sentence is grammatically incorrect: {corrected_sentence}"
        elif corrected_text:
            return corrected_text

def text_to_speech(text: str, lang: str) -> io.BytesIO:
    """Converts text to speech using gTTS."""
    tts = gTTS(text, lang=lang.split('-')[0])  
    audio_file = io.BytesIO()
    tts.save(audio_file)
    audio_file.seek(0)
    return audio_file

def convert_to_wav(input_file, output_file):
    """Converts an audio file to WAV format."""
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format="wav")

async def process_audio(file: UploadFile, language: str):
    """Processes audio: detects language, transcribes, and returns text."""
    recognizer = sr.Recognizer()
    temp_input = f"temp_{file.filename}"
    temp_output = "processed_audio.wav"

    try:
        with open(temp_input, "wb") as f:
            f.write(file.file.read())

        convert_to_wav(temp_input, temp_output)

        with sr.AudioFile(temp_output) as source:
            audio_data = recognizer.record(source)
            
            text = recognizer.recognize_google(audio_data, language=language)  

        return text  

    except Exception as e:
        return f"An error occurred during transcription: {str(e)}"
    
    finally:
        if os.path.exists(temp_input):
            os.remove(temp_input)
        if os.path.exists(temp_output):
            os.remove(temp_output)

@app.post("/process_audio/")  
async def audio(file: UploadFile = File(...), language: str = Form(...)):
    """Process audio and return the chatbot's response as audio."""
    try:
        print(language)
        text = await process_audio(file, language)
        corrected_text = correct_grammar(text, language)
        message_id = len(data) + 1 
        if "grammatically incorrect" in corrected_text:
            highlighted_text = mark_differences(text, corrected_text)
            data.append({
                "id": message_id ,
                "text": highlighted_text['original_text'],  
                "sender": "user"
            })
            data.append({
                "id": message_id + 1,  
                "text": highlighted_text['corrected_text'],
                "sender": "bot"
            })
        else:
            data.append({
                "id": message_id ,
                "text": f'<span style="color: #8E44AD;">{text}</span>',  
                "sender": "user"
            })        
            data.append({
                "id": message_id + 1,  
                "text": f'<span style="color: #4B98E5;">{corrected_text}</span>',
                "sender": "bot"
            })
            
        return {"transcription": corrected_text}

    except Exception as e:
        return {"error": str(e)}




@app.get("/get_messages_a/")  
async def get_messages():
    
    return data

from fastapi import Form

@app.post("/translate/")
async def translate_messages(lang: str = Form(...)):
    """Translate all stored messages in the conversation data."""
    try:
        if not data:
            raise HTTPException(status_code=400, detail="No messages to translate.")
        
        print("Hello bd" ,lang)
        translated_data = translate_text_in_html_dynamic(data, language=lang)

        print("Habibi : " ,translated_data)

        return translated_data  
    
    except Exception as e:
        return {"error": str(e)}

@app.post("/translate/")
async def translate_messages(lang: str = Form(...)):
    """Translate all stored messages in the conversation data."""
    try:
        if not data:
            raise HTTPException(status_code=400, detail="No messages to translate.")
        
        print("Received language code: ", lang)
        print(len(lang))
        translated_data = translate_text_in_html_dynamic(data, lang)

        print("Translated data: ", translated_data)

        return translated_data 
    
    except Exception as e:
        return {"error": str(e)}
