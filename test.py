from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyDr9ZR3S79jy6RdrH3UfCEk4cPfVG32orM")
chat = client.chats.create(model="gemini-2.0-flash", config=types.GenerateContentConfig(max_output_tokens=500, temperature=2.0, system_instruction="You are a cat. Your name is Neko."))

response = chat.send_message_stream("I have 2 dogs in my house.")
for chunk in response:
    print(chunk.text, end="")

response = chat.send_message_stream("How many paws are in my house?")
for chunk in response:
    print(chunk.text, end="")



#AIzaSyDr9ZR3S79jy6RdrH3UfCEk4cPfVG32orM