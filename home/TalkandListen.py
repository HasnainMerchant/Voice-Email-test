import pyttsx3
from gtts import gTTS
import speech_recognition as sr
# this speaks the text sent as a parameter
def talk(text):
    engine = pyttsx3.init()  # text to speech initialized.Engine speaks the text out
    engine.say(text)
    engine.runAndWait()

# Speak Function Not Working Properly
def listen():
    print('INSIDE listen FNCTION')
    listener = sr.Recognizer()  # to understand what the user is saying.
    try:
        with sr.Microphone() as source:  # laptop's mic is the source for speech.
            listener.adjust_for_ambient_noise(source, duration=1)
            print('Listening...')
            talk('Now Listening')
            voice = listener.listen(source, phrase_time_limit=None)
            info = listener.recognize_google(voice)  # speech to text function
            print(info, '\n')
            return info
    except Exception as e:
        print(e)
        pass

def save_audio(audio_msg, filename):
    tts = gTTS(text = audio_msg, lang='en', slow=False)
    tts.save(filename)
    return False
