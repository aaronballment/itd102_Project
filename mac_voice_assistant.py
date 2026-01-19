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
# --- SYSTEM PROMPT ---
def load_system_instruction(file_path="system_prompt.txt"):
    try:
        with open(file_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Using default prompt.")
        return "You are a helpful assistant."

SYSTEM_INSTRUCTION = load_system_instruction()
def initialize_chat_session(system_instruction):
    """
    Initializes a Gemini chat session with history.
    """
    if not API_KEY:
        print("I need an API key to think effectively.")
        return None
    
    try:
        # UPDATED MODEL TO 2.5-flash as requested
        model = genai.GenerativeModel('gemini-2.5-flash-lite', system_instruction=system_instruction)
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
        speak_text("Sorry, I didn't verify that.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_valid_input(recognizer, source, prompt_text):
    """
    Speaks the prompt and loops until a valid input is received.
    """
    speak_text(prompt_text)
    
    while True:
        user_input = listen_and_recognize(recognizer, source)
        if user_input:
            return user_input
        
        speak_text(prompt_text)

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
            user_name = get_valid_input(recognizer, source, "What is your name?")

            date_preference = get_valid_input(recognizer, source, "What are you looking for in a date?")
            
            date_name = get_valid_input(recognizer, source, "What is your date's name?")
            
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
                normalized_input = user_input.lower().replace(",", "").replace(".", "").replace("!", "")
                if normalized_input == "goodbye":
                    try:
                        if chat_session:
                            final_input = f"{context_instruction}\n\nThe user is leaving now. Give them one last energetic, confidence-boosting hype-up message before their date. Keep it short (max 2 sentences)."
                            final_response = chat_session.send_message(final_input)
                            speak_text(final_response.text)
                        else:
                            speak_text("You're a legend! Go get 'em!")
                    except Exception as e:
                        print(f"Error generating goodbye: {e}")
                        speak_text("Good luck! You're going to be great.")
                    break
                
                print("Thinking (querying Gemini)...")
                try:
                    if chat_session:
                        # Stream the response
                        response_stream = chat_session.send_message(user_input, stream=True)
                        
                        buffer = ""
                        for chunk in response_stream:
                            text_chunk = chunk.text
                            buffer += text_chunk
                            
                            # Check for sentence endings to speak incrementally
                            if any(punct in buffer for punct in [".", "!", "?", ":", "\n"]):
                                import re
                                parts = re.split(r'([.!?:\n]+)', buffer)
                                
                                for i in range(0, len(parts) - 1, 2):
                                    sentence = parts[i] + parts[i+1]
                                    clean_sentence = sentence.strip()
                                    if clean_sentence:
                                        print(f"Gemini Streaming: {clean_sentence}")
                                        speak_text(clean_sentence)
                                
                                buffer = parts[-1]
                        
                        if buffer.strip():
                            print(f"Gemini Streaming (Final): {buffer.strip()}")
                            speak_text(buffer.strip())
                            
                    else:
                        speak_text("I'm not connected to my brain.")
                except Exception as e:
                     print(f"Gemini Error: {e}")
                     speak_text("I'm having a bit of trouble thinking right now.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
