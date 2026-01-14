import speech_recognition as sr
import subprocess
import os
import google.generativeai as genai

# --- CONFIGURATION ---
# PASTE YOUR API KEY DIRECTLY BELOW:
API_KEY = "AIzaSyA0IzwJJvEBzzOL40WebQPcDEsm98cx1qk"

if API_KEY == " ":
    # Fallback to env variable if user hasn't pasted key yet
    API_KEY = os.environ.get("GOOGLE_API_KEY")

if not API_KEY:
    print("WARNING: GOOGLE_API_KEY not found in code or environment.")

if API_KEY:
    genai.configure(api_key=API_KEY)

# --- SYSTEM PROMPT ---
SYSTEM_INSTRUCTION = """
You are "The Wingman," the ultimate smooth operator accompanying your best friend on a first date. 

You are effortlessly charming, highly romantic, and very cheeky. You don't just give advice; you give confidence with a wink. Your goal is to make your friend feel like a Casanova.

Constraints:
1. STRICT LENGTH LIMIT: Maximum 3 sentences.
2. Tone: Playful, flirty, and bold.
3. Always prioritize romance and smooth moves.
"""
def get_gemini_response(prompt):
    """
    Sends text to Gemini Flash model and returns the response text.
    """
    if not API_KEY:
        return "I need an API key to think effectively."
    
    try:
        # UPDATED MODEL TO 2.5-flash as requested
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_INSTRUCTION)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "I'm having trouble connecting to my brain right now."

def speak_text(text):
    """
    Uses 'say' to speak text on macOS.
    """
    print(f"Speaking: {text}")
    try:
        subprocess.call(['say', text])
    except Exception as e:
        print(f"Error speaking text: {e}")

def main():
    print("\n--- Running in macOS Mode (Gemini Enhanced) ---")

    # 1. Setup Recognizer
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = False
    
    # 1000 is a good starting point for a built-in Mac mic
    recognizer.energy_threshold = 1000 
    recognizer.pause_threshold = 2.0
    
    # 2. Greeting
    speak_text("Hey handsome, how can I help?")
    
    try:
        # 3. Start Listening
        with sr.Microphone() as source:
            
            print(f"DEBUG: Threshold set to: {recognizer.energy_threshold}")
            print("Listening now... (Speak!)")
            
            # Fail-safe: Stop listening after 60 seconds automatically
            audio_data = recognizer.listen(source, timeout=60, phrase_time_limit=10)
            
            print("Processing with Google Speech Recognition...")
            user_input = recognizer.recognize_google(audio_data)
            
            print(f"User said: {user_input}")
            
            print("Thinking (querying Gemini)...")
            response_text = get_gemini_response(user_input)
            
            #print(f"Gemini says: {response_text}")
            speak_text(response_text)

    except sr.WaitTimeoutError:
        print("Error: You didn't speak in time.")
    except sr.UnknownValueError:
        print("Error: Could not understand audio.")
        speak_text("I heard sound, but no words.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()