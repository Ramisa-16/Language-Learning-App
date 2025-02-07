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

def convert_to_wav(input_file, output_file):
    """Converts an audio file to WAV format."""
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format="wav")


async def process_audio_free(file):
    """Processes audio: detects language, transcribes, and returns text and language code."""
    recognizer = sr.Recognizer()
    temp_input = f"temp_{file.filename}"
    temp_output = "processed_audio.wav"

    try:
        with open(temp_input, "wb") as f:
            f.write(file.file.read())
        convert_to_wav(temp_input, temp_output)

        with sr.AudioFile(temp_output) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)  

        return text  

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}", "en-US"
    finally:
        if os.path.exists(temp_input):
            os.remove(temp_input)
        if os.path.exists(temp_output):
            os.remove(temp_output)








