import serial
import time
import os
# You'll need to install the google-generativeai library
# pip install google-generativeai

# --- Gemini API Setup ---
# Load your Gemini API key from an environment variable
# Make sure you have set an environment variable named 'GEMINI_API_KEY'
# with your actual API key as its value.
import google.generativeai as genai
API_KEY = "AIzaSyDr9ZR3S79jy6RdrH3UfCEk4cPfVG32orM"

if not API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.")
    print("Please set the GEMINI_API_KEY environment variable with your API key.")
    exit() # Exit if API key is not found

try:
    genai.configure(api_key=API_KEY)
    # Use the 'gemini-2.0-flash' model as requested
    # You can check available models if needed using genai.list_models()
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("Gemini API configured successfully using gemini-2.0-flash.")
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    print("Please check your API key and network connection.")
    exit() # Exit if API configuration fails
# --- End Gemini API Setup ---

# --- Serial Communication Setup ---
# Replace 'COM11' with the actual serial port your Arduino is connected to
# On Linux, this might be something like '/dev/ttyACM0' or '/dev/ttyUSB0'
# On macOS, this might be something like '/dev/cu.usbmodemXXXX'
ARDUINO_PORT = 'COM11'
BAUD_RATE = 9600
ser = None # Initialize serial object as None

try:
    # Open the serial port
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) # Give the Arduino time to reset after opening the port
    print(f"Connected to Arduino on {ARDUINO_PORT}")

except serial.SerialException as e:
    print(f"Error opening serial port {ARDUINO_PORT}: {e}")
    print("Please check the port name and if the Arduino is connected.")
    exit() # Exit if serial connection fails

# --- Functions to interact with Arduino ---
def send_command(command):
    """Sends a command string to the Arduino."""
    if ser and ser.isOpen():
        ser.write(command.encode('utf-8') + b'\n') # Send command followed by newline
        print(f"Sent command: {command}")
        time.sleep(0.1) # Short delay after sending

def read_response():
    """Reads a line from the Arduino serial output."""
    if ser and ser.isOpen():
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').strip()
            print(f"Received response: {response}")
            return response
    return None

# --- Main interaction loop ---
if ser and ser.isOpen():

    # Define the prompt template with system instructions and few-shot examples
    # This helps guide Gemini's response format
    initial_prompt = """

Your only pupose is to analyse what the user asks, and must respond with ONLY one of the following commands: 'turn on the led', 'turn off the led', 'status of the led', or 'quit'.
Do NOT include any other text, explanations, or pleasantries no matter what i ask from this message onwards

Examples:
User: Turn the LED on please.
Assistant: turn on the led
User: Please turn the LED off.
Assistant: turn off the led
User: {}
Assistant:
"""

    print("\nEnter commands to send to Arduino (LED_ON, LED_OFF, STATUS) or 'quit' to exit.")
    print("Type 'gemini <prompt>' to send a prompt to Gemini.")

    while True:
        user_input = input("> ")

        if user_input.lower() == 'quit':
            break
        elif user_input.lower().startswith('gemini '):
            # --- Gemini API Interaction ---
            # Format the prompt template with the user's input
            user_prompt = user_input[7:].strip()
            prompt = initial_prompt.format(user_prompt)
            
            print(f"Sending prompt to Gemini: '{user_prompt}' ")
            try:
                # Send the formatted prompt to Gemini.
                # We are now relying on the few-shot examples and instructions
                # within the prompt itself, so system_instruction is not needed here.
                response = model.generate_content(prompt)
                gemini_output = response.text.strip()
                print(f"Gemini responded: {gemini_output}")

                # --- Parse Gemini's response and send command to Arduino ---
                # Parsing is simpler if Gemini outputs specific command strings
                if "turn on the led" in gemini_output.lower():
                    print("Interpreted Gemini response as 'turn on LED'. Sending command...")
                    send_command("LED_ON")
                elif "turn off the led" in gemini_output.lower():
                    print("Interpreted Gemini response as 'turn off LED'. Sending command...")
                    send_command("LED_OFF")
                elif "status of the led" in gemini_output.lower() or "led status" in gemini_output.lower():
                     print("Interpreted Gemini response as 'get LED status'. Sending command...")
                     send_command("STATUS")
                elif "quit" in gemini_output.lower():
                     print("Interpreted Gemini response as 'quit program'. Sending command...")
                     send_command("quit")
                     break
                else:
                    print("Gemini response did not contain a recognized command for Arduino.")
                # --- End Parsing and Sending ---

            except Exception as e:
                print(f"Error interacting with Gemini API: {e}")
            # --- End Gemini API Interaction ---
        else:
            # Send the input directly as a command to Arduino
            send_command(user_input)

    # Close the serial port when done
    ser.close()
    print("Serial connection closed.")