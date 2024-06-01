import json
import time
import requests
import pyttsx3
import pyaudio
import vosk
import random
import os
from PIL import Image

#api 4 варианта имеет какие то проблемы, по этому выполнил задание 3 варианта
class Speech:
    def __init__(self):
        self.speaker = 0
        self.tts = pyttsx3.init()

    def set_voice(self, speaker):
        self.voices = self.tts.getProperty('voices')
        id = self.voices[speaker].id if speaker < len(self.voices) else self.voices[0].id
        return id

    def text2voice(self, speaker=0, text='Готов'):
        self.tts.setProperty('voice', self.set_voice(speaker))
        self.tts.say(text)
        self.tts.runAndWait()

class Recognize:
    def __init__(self):
        model = vosk.Model('vosk-model-small-ru-0.4')
        self.record = vosk.KaldiRecognizer(model, 16000)
        self.stream()

    def stream(self):
        pa = pyaudio.PyAudio()
        self.stream = pa.open(format=pyaudio.paInt16,
                              channels=1,
                              rate=16000,
                              input=True,
                              frames_per_buffer=8000)

    def listen(self):
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.record.AcceptWaveform(data) and len(data) > 0:
                answer = json.loads(self.record.Result())
                if answer['text']:
                    yield answer['text']

def fetch_character_data():
    url = "https://rickandmortyapi.com/api/character/108"
    response = requests.get(url)
    return response.json()

def fetch_random_character_data():
    url = "https://rickandmortyapi.com/api/character/"
    response = requests.get(url)
    characters = response.json()['results']
    return random.choice(characters)

def handle_command(command, data):
    if command == 'случайный':
        random_character = fetch_random_character_data()
        return f"Случайный персонаж: {random_character['name']}"
    elif command == 'сохранить':
        img_url = data['image']
        img_data = requests.get(img_url).content
        with open('character_image.png', 'wb') as handler:
            handler.write(img_data)
        return "Картинка сохранена как character_image.png"
    elif command == 'эпизод':
        first_episode = data['episode'][0]
        episode_data = requests.get(first_episode).json()
        return f"Первое появление в эпизоде: {episode_data['name']}"
    elif command == 'показать':
        img_url = data['image']
        img_data = requests.get(img_url).content
        with open('character_image.png', 'wb') as handler:
            handler.write(img_data)
        img = Image.open('character_image.png')
        img.show()
        return "Картинка отображена"
    elif command == 'разрешение':
        img_url = data['image']
        img_data = requests.get(img_url).content
        with open('character_image.png', 'wb') as handler:
            handler.write(img_data)
        img = Image.open('character_image.png')
        return f"Разрешение картинки: {img.size}"
    else:
        return "Команда не распознана."

def speak(text):
    speech = Speech()
    speech.text2voice(speaker=1, text=text)

rec = Recognize()
text_gen = rec.listen()
data = fetch_character_data()

rec.stream.stop_stream()
speak('Starting')
time.sleep(0.5)
rec.stream.start_stream()

for text in text_gen:
    if text == 'закрыть':
        speak('Бывай, бро)')
        break
    else:
        response = handle_command(text, data)
        print(text)
        speak(response)
