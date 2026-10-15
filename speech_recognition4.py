
import speech_recognition as sr
import pyttsx3
import ollama
import webbrowser
import re
import subprocess
import keyboard
import threading

recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Pause variable
is_paused = False

def toggle_pause():
    global is_paused
    is_paused = not is_paused
    if is_paused:
        print("\npress p for resume")
    else:
        print("\nzaqu is resumd")

# P key se pause/resume
keyboard.add_hotkey('p', toggle_pause)


def speak(text):
    print("Zaqu:", text)
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()


WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "whatsapp": "https://web.whatsapp.com",
    "gmail": "https://mail.google.com",
    "chatgpt": "https://chatgpt.com",
}


def handle_website_command(text):
    command = text.lower().strip()
    open_words = [
        "open", "launch", "start", "khol",
        "kholo", "kholna", "khol do"
    ]
    if not any(word in command.split() for word in open_words):
        return False
    for name, url in WEBSITES.items():
        if name in command:
            speak(f"Opening {name}")
            webbrowser.open(url)
            return True
    return False


APPS = {
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "calc": ["calc.exe"],
    "paint": ["mspaint.exe"],
    "whatsapp": ["whatsapp.exe"]
}

OFFICE_APPS = {
    "excel": ["excel", "EXCEL.EXE"],
    "word": ["winword", "WINWORD.EXE"],
    "powerpoint": ["powerpnt", "POWERPNT.EXE"],
    "outlook": ["outlook", "OUTLOOK.EXE"],
}


def handle_app_command(text):
    command = text.lower().strip()
    open_words = [
        "open", "launch", "start", "khol",
        "kholo", "kholna", "khol do"
    ]
    if not any(word in command.split() for word in open_words):
        return False
    command = command.replace("microsoft", " ")
    command = command.replace("ms ", " ")
    command = re.sub(r"\b(the|please|app|application)\b", " ", command)
    command = " ".join(command.split())

    for name, executable in APPS.items():
        if re.search(r"\b" + re.escape(name) + r"\b", command):
            try:
                subprocess.Popen(executable)
                speak(f"Opening {name}")
            except Exception as e:
                print("App error:", e)
                speak(f"Could not open {name}")
            return True

    for name, executables in OFFICE_APPS.items():
        if re.search(r"\b" + re.escape(name) + r"\b", command):
            launched = False
            for executable in executables:
                try:
                    subprocess.Popen(
                        ["cmd", "/c", "start", "", executable],
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    speak(f"Opening Microsoft {name}")
                    launched = True
                    break
                except Exception:
                    continue
            if not launched:
                speak(f"Could not launch {name}. Check Microsoft Office.")
            return True
    return False


def detect_language(text):
    hindi_words = {
        "kya", "hai", "mera", "tera", "aap", "main",
        "hoon", "kaise", "namaste", "nahi", "haan",
        "theek", "bolo", "batao", "accha", "bahut",
        "kaisa", "kyun", "kab", "kholo", "khol"
    }
    words = set(re.findall(r"\b\w+\b", text.lower()))
    if words.intersection(hindi_words):
        return "hindi"
    return "english"


def ask_ai(question, language="english"):
    print("Zaqu thinking...")
    if language == "hindi":
        system_prompt = """
You are Zaqu, a helpful assistant.
Reply in Hinglish using English alphabets only.
Keep your answer short, around 1-2 lines.
"""
    else:
        system_prompt = """
You are Zaqu, a helpful assistant.
Reply in English only.
Keep your answer short, around 1-2 lines.
"""
    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    )
    return response["message"]["content"]


def listner():
    # Pause check karo
    while is_paused:
        pass

    print("Listening...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(
            source, timeout=7, phrase_time_limit=6
        )

    # Audio record hone ke baad PHIR check karo
    if is_paused:
        print("Paused")
        return "", "english"  # Khali return karo!

    try:
        try:
            text = recognizer.recognize_google(
                audio, language="en-IN"
            )
            language = detect_language(text)
        except sr.UnknownValueError:
            text = recognizer.recognize_google(
                audio, language="hi-IN"
            )
            language = "hindi"

        print(f"You said ({language}):", text)
        return text.lower().strip(), language

    except sr.UnknownValueError:
        speak("Sorry, couldn't understand, speak again")
        return "", "english"

    except sr.RequestError as e:
        print("Speech recognition error:", e)
        speak("Some technical issue")
        return "", "english"

def respond(text, language="english"):
    text = text.lower().strip()

    if text in ["stop", "band karo", "exit", "quit"]:
        speak("Goodbye, see you again!")
        return "bye"

    if handle_website_command(text):
        return None

    if handle_app_command(text):
        return None

    commands = {
        "hello": "Hello! How are you?",
        "namaste": "Namaste! Aap kaise hain?",
        "what is your name": "My name is Zaqu!",
        "tera naam kya hai": "Mera naam Zaqu hai!",
        "how are you": "I am doing great! How about you?",
        "kaise ho": "Main bilkul theek hoon! Aap batao?",
    }

    if text in commands:
        speak(commands[text])
        return None

    try:
        ai_reply = ask_ai(text, language)
        speak(ai_reply)
    except Exception as e:
        print("AI error:", e)
        speak("Sorry, couldn't respond now")

    return None


# Main Loop
while True:
    print("\n===== ZAQU AI =====")
    print("1. Voice Chat 🎤")
    print("2. Type Chat ⌨️")
    print("3. Close ❌")
    print("💡 press 'P' pause/resume1" \
    "")

    choice = input("Choose (1/2/3): ").strip()

    if choice == "1":
        print("\n press p for pause")
        while True:
            try:
                if is_paused:
                    continue

                text, language = listner()

                if not text:
                    continue

                result = respond(text, language)

                if result == "bye":
                    break

            except sr.WaitTimeoutError:
                print("Timeout! Speak again.")

            except Exception as e:
                print("Voice error:", e)

    elif choice == "2":
        print("\nZaqu:type anything, press stop for close")

        while True:
            text = input("\nAap: ").strip().lower()

            if not text:
                continue

            language = detect_language(text)
            print("Language detected:", language)

            result = respond(text, language)

            if result == "bye":
                break

    elif choice == "3":
        speak("Goodbye! See you again!")
        break

    else:
        print("1, 2 ya 3 choose karo!")