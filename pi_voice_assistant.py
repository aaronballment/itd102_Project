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
        model = genai.GenerativeModel('gemini-2.5-flash-lite', system_instruction=SYSTEM_INSTRUCTION)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "I'm having trouble connecting to my brain right now."

def find_usb_mic_index():
    """
    Scans for a USB microphone on the Raspberry Pi.
    Returns the index if found, otherwise None.
    """
    print("\n--- Available Audio Devices ---")
    devices = sr.Microphone.list_microphone_names()
    
    strong_match = None
    weak_match = None
    
    for index, name in enumerate(devices):
        print(f"Index {index}: {name}")
        name_lower = name.lower()
        
        # 1. IMMEDIATE RETURN: Known USB Descriptors
        if "usb" in name_lower or "c-media" in name_lower or "uac" in name_lower or "webcam" in name_lower:
            print(f"\n✅ Auto-selected Strong Match: '{name}' at index {index}")
            return index
            
        # 2. WEAK MATCH: Anything that is NOT the built-in Pi audio (which are usually outputs)
        if "bcm2835" not in name_lower and "hdmi" not in name_lower and "vc4" not in name_lower:
            if weak_match is None:
                weak_match = index

    if weak_match is not None:
        print(f"\n⚠️ No 'USB' named device found, but '{devices[weak_match]}' looks promising.")
        print(f"Auto-selected Best Guess: Index {weak_match}")
        return weak_match

    print("\n❌ No USB Mic found. Falling back to system default.")
    return None

def speak_text(text):
    """
    Uses 'espeak-ng' to speak text on Raspberry Pi.
    """
    print(f"Speaking: {text}")
    try:
        # Using -ven+m3 for a male voice, -s130 for speed.
        subprocess.call(['espeak-ng', '-ven+m3', '-s130', text])
    except FileNotFoundError:
        print("Error: 'espeak-ng' not found. Please install it using: sudo apt install espeak-ng")
    except Exception as e:
        print(f"Error speaking text: {e}")

def main():
    print("\n--- Running in Raspberry Pi Mode (The Wingman) ---")

    # 1. Setup Recognizer
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = False
    
    # High threshold for noisy environments/USB mics on Pi
    recognizer.energy_threshold = 4000 
    recognizer.pause_threshold = 2.0
    
    # 2. Get Mic
    mic_index = find_usb_mic_index()
    
    # 3. Greeting
    speak_text("Hey handsome, how can I help?")
    
    try:
        # 4. Start Listening
        with sr.Microphone(device_index=mic_index) as source:
            
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
