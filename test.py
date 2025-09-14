import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests, json



load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API'))


model = genai.GenerativeModel("gemini-2.5-flash")


response = model.generate_content("Write a short poem about AI and the future")

print(response.text)
import requests
import json

API_KEY = os.getenv('GEMINI_API')   
MODEL = "gemini-2.5-flash"       

# Gemini API endpoint
url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

# Headers (telling Gemini we are sending JSON data)
headers = {
    "Content-Type": "application/json"
}

# The prompt we send to Gemini
data = {
    "contents": [
        {
            "parts": [
                {"text": "Explain AI in very simple words like I am 10 years old."}
            ]
        }
    ]
}

# Send the POST request
response = requests.post(url, headers=headers, data=json.dumps(data))

# Check response
if response.status_code == 200:
    result = response.json()
    # print("Gemini says:", result["candidates"][0]["content"]["parts"][0]["text"])
    print(result[""])

else:
    print("Error:", response.status_code, response.text)
