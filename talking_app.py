# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 12:03:40 2024

@author: LENOVO T460
"""

import io
import pygame  # type: ignore
from gtts import gTTS  # type: ignore  # Google Text-to-Speech
import google.generativeai as genai  # type: ignore  # Generating the Text from Gemini AI
from deep_translator import GoogleTranslator  # type: ignore
import speech_recognition as sr  # type: ignore  # Listening User Queries
import streamlit as st

# Initialize recognizer
recognizer = sr.Recognizer()  # speech recognizer

# Configure the Google Generative AI with API key

genai.configure(api_key="API_KEY")

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

chat_session = model.start_chat(
    history=[]
)

# Define language options
languages = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese": "zh-CN",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta",
    "Bengali": "bn",
    "Marathi": "mr",
    "Gujarati": "gu"
}

def translate_text(text, dest_language):
    translator = GoogleTranslator(source='auto', target=dest_language)
    return translator.translate(text)

def speak_text(text, language):
    tts = gTTS(text=text, lang=language)
    speech_bytes = io.BytesIO()
    tts.write_to_fp(speech_bytes)
    speech_bytes.seek(0)
    
    pygame.mixer.init()
    pygame.mixer.music.load(speech_bytes, 'mp3')
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        continue

# Streamlit UI
st.title("Talking AI")
st.subheader("Chat in your own language")

image_url = "https://ichef.bbci.co.uk/news/976/cpsprodpb/093B/production/_128936320_gettyimages-1367728606.jpg"
st.image(image_url)


# Language selection dropdown
selected_language = st.selectbox("Choose your preferred language to chat", list(languages.keys()))

# Button to start functionality
if st.button("Start Chat"):
    st.write("Say something:")
    
    # Capture audio from the microphone
    with sr.Microphone() as source:
        st.write("Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, timeout=10)

    # Recognize speech using Google Web Speech API
    try:
        st.write("Recognizing...")
        lang_code = languages[selected_language]
        text = recognizer.recognize_google(audio, language=lang_code)
        st.write("You said in {}: {}".format(selected_language, text))

        instruct = "Give Response according to instruction. Limit to 100 words."
        ques_from_user = instruct + " " + text
        
        response = chat_session.send_message(ques_from_user)
        translated_response = translate_text(response.text, lang_code)
        
        st.write("Translated Response in {}: {}".format(selected_language, translated_response))
        
        speak_text(translated_response, lang_code)  # Speak the translated response
        
    except sr.UnknownValueError:
        st.error("Google Speech Recognition could not understand the audio")
    except sr.RequestError as e:
        st.error("Could not request results from Google Speech Recognition service; {0}".format(e))
    except sr.WaitTimeoutError:
        st.error("Listening timed out while waiting for phrase to start")
