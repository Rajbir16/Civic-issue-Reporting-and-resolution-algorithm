import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import datetime
from openai import OpenAI

# -----------------------------
# 🔑 SET YOUR OPENAI API KEY
# -----------------------------
client = OpenAI(api_key="YOUR_API_KEY_HERE")

# -----------------------------
# 🔊 Text to Speech Setup
# -----------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# -----------------------------
# 🎤 Voice Input
# -----------------------------
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio)
        print("You:", command)
        return command.lower()
    except:
        speak("Sorry, I didn't catch that.")
        return ""

# -----------------------------
# 🤖 AI Response
# -----------------------------
def ask_ai(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful desktop AI assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# -----------------------------
# 🧠 Main Assistant Logic
# -----------------------------
def run_assistant():
    speak("Hello Himanshu, how can I help you today?")

    while True:
        command = listen()

        if "time" in command:
            time_now = datetime.datetime.now().strftime("%H:%M")
            speak(f"The time is {time_now}")

        elif "open youtube" in command:
            webbrowser.open("https://youtube.com")
            speak("Opening YouTube")

        elif "open google" in command:
            webbrowser.open("https://google.com")
            speak("Opening Google")

        elif "open vs code" in command:
            os.system("code")
            speak("Opening VS Code")

        elif "exit" in command or "stop" in command:
            speak("Goodbye Himanshu!")
            break

        elif command != "":
            ai_response = ask_ai(command)
            speak(ai_response)

# -----------------------------
# 🚀 Start Assistant
# -----------------------------
if __name__== "_main_":
    run_assistant()