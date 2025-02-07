from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
import tnew
import audion  
import tfree
import vfree
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
from datetime import datetime, timedelta
from fastapi import HTTPException
from contextlib import asynccontextmanager
DetectorFactory.seed = 0 

languages = {
    'en': 'en-US',
    'es': 'es-ES',
    'zh': 'zh-CN',
    'fr': 'fr-FR',
    'ar': 'ar-SA'
}

translator = Translator()
from fastapi import Form
app = FastAPI()
openai.api_key = "sk-svcacct-KBnnF-0KRobG1j17ah1p-jQ81c9HUGpdHZAsCawOMJSvaxoG2ozHgroUFedjkpT3BlbkFJrywiP4MDf-sqI9diCPyu0rT2M6rC1Ofeko-lK2u0qDDdR9Qgr4NGuCEBBczlUA"
class TextRequest(BaseModel):
    text: str
    language: str 
    user_id: str 
    plan: str
    level : str

from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()

from datetime import datetime, timedelta

def delete_expired_conversations():
    current_time = datetime.now()
    tnew.data = [message for message in tnew.data if current_time - datetime.strptime(message['create_date'], '%Y-%m-%d') < timedelta(hours=24)]
    audion.data = [message for message in audion.data if current_time - datetime.strptime(message['create_date'], '%Y-%m-%d') < timedelta(hours=24)]
    vfree.data = [message for message in vfree.data if current_time - datetime.strptime(message['create_date'], '%Y-%m-%d') < timedelta(hours=24)]
    tfree.data = [message for message in tfree.data if current_time - datetime.strptime(message['create_date'], '%Y-%m-%d') < timedelta(hours=24)]
    
    print("Expired conversations deleted!")

delete_expired_conversations()
scheduler.add_job(delete_expired_conversations, 'interval', hours=24)



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Custom lifespan manager to start and stop the scheduler."""
    print("Scheduler started!")
    scheduler.start()
    yield
    print("Scheduler stopped!")
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)



@app.post("/correct_grammar/")
async def correct_text(request: TextRequest):
    """API endpoint to correct grammar and highlight differences."""
    print("Received text:", request.text)
    if request.plan =="Free":
        await chat(request.text, request.user_id, request.language)
    else:
        print( request.language)
    
        
        corrected_text = tnew.correct_grammar(request.text, request.language, request.level)
        print("Corrected text:", corrected_text)
        message_id = len(tnew.data) + 1  
        today_date = datetime.now().strftime('%Y-%m-%d')
        create_date = today_date
        
        if "grammatically incorrect" in corrected_text:
            highlighted_text = tnew.mark_differences(request.text, corrected_text)
            
            tnew.data.append({
            "id": message_id,
            "text": highlighted_text['original_text'],  
            "sender": "user",
            "user_id": request.user_id,
            "create_date": create_date
        })
            tnew.data.append({
                "id": message_id + 1,  
                "text": highlighted_text['corrected_text'],
                "sender": "bot",
                "user_id": request.user_id,
                "create_date": create_date
            })
        
            
            filtered_data = [message for message in tnew.data if message['user_id'] == request.user_id]
            
            print(filtered_data)
            

            return filtered_data
        else:
            tnew.data.append({
            "id": message_id ,
            "text": f'<span style="color: #8E44AD;">{request.text}</span>',  
            "sender": "user",
            "user_id": request.user_id,
            "create_date": create_date
        })        
            tnew.data.append({
                "id": message_id + 1,  
                "text": f'<span style="color: #4B98E5;">{corrected_text}</span>',
                "sender": "bot",
                "user_id": request.user_id,
                "create_date": create_date
            })
            

            filtered_data = [message for message in tnew.data if message['user_id'] == request.user_id]
            print(filtered_data)
            

            return filtered_data


@app.post("/process_audio/")  
async def audio(file: UploadFile = File(...), language: str = Form(...), user_id: str =Form(...), plan: str = Form(...)):
    """Process audio and return the chatbot's response as audio."""
    if plan =="Free":
        return await free_audio(file, language, user_id)
    else:
        print(language)
        text = await audion.process_audio(file, language)
        corrected_text = audion.correct_grammar(text, language)
        print(corrected_text)
        message_id = len(audion.data) + 1 
        today_date = datetime.now().strftime('%Y-%m-%d')
        create_date = today_date

        if "grammatically incorrect" in corrected_text:
            highlighted_text = audion.mark_differences(text, corrected_text)
            audion.data.append({
                "id": message_id ,
                "text": highlighted_text['original_text'],  
                "sender": "user",
                "user_id": user_id,
                "create_date": create_date
            })
            audion.data.append({
                "id": message_id + 1,  
                "text": highlighted_text['corrected_text'],
                "sender": "bot",
                "user_id": user_id,
                "create_date": create_date
            })
           
        
            

            return {"transcription":corrected_text}
           
        else:
            audion.data.append({
                "id": message_id ,
                "text": f'<span style="color: #8E44AD;">{text}</span>',  
                "sender": "user",
                "user_id": user_id,
                "create_date": create_date
            })        
            audion.data.append({
                "id": message_id + 1,  
                "text": f'<span style="color: #4B98E5;">{corrected_text}</span>',
                "sender": "bot",
                "user_id": user_id,
                "create_date": create_date
            })
             

        return {"transcription":corrected_text}
    
        

@app.get("/get_messages_text/")
async def get_messages(user_id: str):
    """
    Get the conversation history filtered by user_id (messages from the specified user).
    """
    filtered_data = [message for message in tnew.data if message['user_id'] == user_id]
    return filtered_data






@app.get("/get_messages_audio/")  
async def get_messages(user_id: str):
    """
    Get the conversation history filtered by user_id (messages from the specified user).
    """
    filtered_data = [message for message in audion.data if message['user_id'] == user_id]

    return filtered_data

@app.post("/translate/")
async def translate_messages(lang: str = Form(...), user_id:str = Form(...)):
    """
    Translate all stored messages in the conversation data.
    """
    try:
        if not audion.data:
            raise HTTPException(status_code=400, detail="No messages to translate.")
        translated_data = audion.translate_text_in_html_dynamic(audion.data, lang)

        filtered_data = [message for message in translated_data if message['user_id'] == user_id]
    
        return filtered_data

    except Exception as e:
        return {"error": str(e)}



async def chat(text, user_id, language):
    """API endpoint for handling text-based conversation."""
    print("Received chat text:", text)
    
    response_text = tfree.respond_to_text(text,language)
    print("AI Response:", response_text)
    
    message_id = len(tfree.data) + 1  
    create_date = datetime.now().strftime('%Y-%m-%d')
    tfree.data.append({
        "id": message_id,
        "text": f'<span style="color: #8E44AD;">{text}</span>',
        "sender": "user",
        "user_id" : user_id,
        "create_date": create_date
    })
    
    tfree.data.append({
        "id": message_id + 1, 
        "text": f'<span style="color: #4B98E5;">{response_text}</span>',
        "sender": "bot",
        "user_id" : user_id,
         "create_date": create_date
    })
 

    return {"message": "Message sent successfully!"}

    



@app.get("/get_messages_free/")
async def get_messages(user_id: str):
    """
    Get the conversation history filtered by user_id and today's date.
    Limit the response to 25 messages.
    """
    today_date = datetime.now().strftime('%Y-%m-%d') 
    filtered_data = [message for message in tfree.data if message['user_id'] == user_id and message['create_date'] == today_date]

    if len(filtered_data) > 25:
        raise HTTPException(status_code=400, detail="Your response limit of 25 messages for today has been reached.")
    return filtered_data


async def free_audio(file, language, user_id):
    """Process audio and return the chatbot's response as audio."""
    try:
        text = await vfree.process_audio_free(file)
        print("text", text)
        
        today_date = datetime.now().strftime('%Y-%m-%d')  
        filtered_data = [
            message for message in vfree.data 
            if message['user_id'] == user_id and message['create_date'] == today_date
        ]

        if len(filtered_data) >= 25:
            raise HTTPException(status_code=400, detail="Your response limit of 25 messages for today has been reached.")

        message_id = len(vfree.data) + 1
        create_date = today_date

        messages = [
            {"role": "system", "content": f"You are an assistant that speaks and responds in the language of the user ({vfree.languages.get(language, language)})."},
            {"role": "user", "content": text}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=2000,
            temperature=0.7
        )

        chatbot_response = response['choices'][0]['message']['content'].strip()
        print("chatbot_response", chatbot_response)
        vfree.data.append({
            "id": message_id,
            "text": f'<span style="color: #8E44AD;">{text}</span>',  
            "sender": "user",
            "user_id": user_id,
            "create_date": create_date
        })
        vfree.data.append({
            "id": message_id + 1,
            "text": f'<span style="color: #4B98E5;">{chatbot_response}</span>', 
            "sender": "bot",
            "user_id": user_id,
            "create_date": create_date
        })

        print("transcription", chatbot_response)
        return {"transcription": chatbot_response}

    except Exception as e:
        return {"error": str(e)}

@app.get("/get_messages_afree/")
async def get_messages_audio(user_id: str):
    """
    Get the conversation history filtered by user_id and today's date.
    Limit the response to 25 messages.
    """
    today_date = datetime.now().strftime('%Y-%m-%d')  
    filtered_data = [message for message in vfree.data if message['user_id'] == user_id and message['create_date'] == today_date]

    if len(filtered_data) > 25:
        raise HTTPException(status_code=400, detail="Your response limit of 25 messages for today has been reached.")
    return filtered_data
