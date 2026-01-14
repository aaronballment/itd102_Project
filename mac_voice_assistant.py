import speech_recognition as sr
import subprocess
import os
import google.generativeai as genai

# --- CONFIGURATION ---
# PASTE YOUR API KEY DIRECTLY BELOW:
API_KEY = "ENTER API KEY HERE"

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
4. You are having a conversation. Ask follow-up questions to help the user get ready for their date. Every now and again, ask if the user is ready to go. 

If the user suggests they are done, then give them a short and encouraging goodbye message before they go on their date.

"""
def initialize_chat_session(system_instruction):
    """
    Initializes a Gemini chat session with history.
    """
    if not API_KEY:
        print("I need an API key to think effectively.")
        return None
    
    try:
        # UPDATED MODEL TO 2.5-flash as requested
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_instruction)
        chat = model.start_chat(history=[])
        return chat
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

def speak_text(text):
    """
    Uses 'say' to speak text on macOS.
    """
    print(f"Speaking: {text}")
    try:
        subprocess.call(['say', text])
    except Exception as e:
        print(f"Error speaking text: {e}")

def listen_and_recognize(recognizer, source):
    """
    Listens to microphone input and converts to text.
    Returns the text or None if failed.
    """
    print("Listening now... (Speak!)")
    try:
        # Fail-safe: Stop listening after 60 seconds automatically
        audio_data = recognizer.listen(source, timeout=60, phrase_time_limit=10)
        
        print("Processing with Google Speech Recognition...")
        text = recognizer.recognize_google(audio_data)
        print(f"User said: {text}")
        return text
        
    except sr.WaitTimeoutError:
        print("Error: You didn't speak in time.")
        return None
    except sr.UnknownValueError:
        print("Error: Could not understand audio.")
        speak_text("I heard sound, but no words.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("\n--- Running in macOS Mode (Gemini Enhanced) ---")

    # 1. Setup Recognizer
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = False
    
    # 1000 is a good starting point for a built-in Mac mic
    recognizer.energy_threshold = 500 
    recognizer.pause_threshold = 2.0
    
    # 2. Greeting (Moved after questions)
    # speak_text("Hey handsome, how can I help?")
    
    try:
        # 3. Start Listening
        with sr.Microphone() as source:
            
            print(f"DEBUG: Threshold set to: {recognizer.energy_threshold}")
            
            # --- New Questions ---
            speak_text("What is your name?")
            user_name = listen_and_recognize(recognizer, source)

            speak_text("What are you looking for in a date?")
            date_preference = listen_and_recognize(recognizer, source)
            
            speak_text("What is your date's name?")
            date_name = listen_and_recognize(recognizer, source)
            
            # --- Main Interaction ---
            # --- Main Interaction ---
            display_name = user_name if user_name else "friend"
            
            # Update System Instruction with Context
            context_instruction = SYSTEM_INSTRUCTION + f"\nUser Name: {user_name}\nDate Preference: {date_preference}\nDate Name: {date_name}"
            
            chat_session = initialize_chat_session(context_instruction)
            
            speak_text(f"Hey {display_name}, how can I help?")

            # Loop for conversation
            while True:
                # Listening for the actual help request
                user_input = listen_and_recognize(recognizer, source)
                
                if not user_input:
                    continue # Try listening again if nothing was caught or error
                
                # Check for exit phrases
                if user_input.lower() in ["exit", "quit", "goodbye", "bye", "stop"]:
                    speak_text("Good luck on your date! Catch you later.")
                    break
                
                print("Thinking (querying Gemini)...")
                try:
                    if chat_session:
                        response = chat_session.send_message(user_input)
                        response_text = response.text
                    else:
                        response_text = "I'm not connected to my brain."
                except Exception as e:
                     print(f"Gemini Error: {e}")
                     response_text = "I'm having a bit of trouble thinking right now."
                
                #print(f"Gemini says: {response_text}")
                speak_text(response_text)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
