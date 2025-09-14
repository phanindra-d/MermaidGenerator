import requests, re, os
from dotenv import load_dotenv
import logging
from datetime import datetime


load_dotenv()

api_key = os.getenv('GEMINI_API')

logging.basicConfig(
    filename="diagram_requests.log",  
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_diagram_action(user_prompt: str, existing_code: str | None, action: str):
    log_message = (
        f"USER_PROMPT: {user_prompt} | "
        f"EXISTING_CODE: {existing_code if existing_code else 'None'} | "
        f"ACTION: {action}"
    )
    logging.info(log_message)


def decide(description:str, existing_code:str):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents":[
                {
                    "role": "user",
                    "parts":[{
                        "text":f""" 
                                Decide if the user wants to:
                                1. MODIFY the existing diagram.
                                2. Start a NEW diagram.
                                Existing Diagram:{existing_code}
                                User Request:{description}
                                Answer only with one word: MODIFY or NEW  """
                    }]
                }
            ]
        }
        response = requests.post(url, headers={"content-type":"application/json"}, json=payload)
        if response.status_code == 200:
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return text.upper()
        else:
            return "NEW"
    except Exception as e:
        return e    



def generate_mermaid(description: str, action: str, diagram_type: str = "flowchart TD", existing_code: str | None = None):

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        if action == "MODIFY" and existing_code:
            prompt = f"""
                    Modify the existing {diagram_type} Mermaid diagram based on user request.
                        Existing Diagram:{existing_code}
                        User Request:{description}
                        Return ONLY raw Mermaid code (no markdown, no explanation).
                            """
        else:  
            prompt = f"""TASK: Generate Mermaid diagram
                    DIAGRAM TYPE: {diagram_type}
                    DESCRIPTION: {description}
                    REQUIREMENTS:
                        - Clean, readable syntax
                        - No markdown code blocks
                        - Raw Mermaid code only
                    Generate the Mermaid code:"""

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ]
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(url, headers=headers, json=payload)  

        if response.status_code == 200:
            data = response.json()
            raw_text = ''.join([part.get('text', '') for part in data['candidates'][0]['content']['parts']])
            log_diagram_action(
                user_prompt=description,
                existing_code=existing_code,
                action=action
                )
            cleaned_code = re.sub(r"^```[a-zA-Z]*\s*", "", raw_text, flags=re.MULTILINE)
            cleaned_code = re.sub(r"```$", "", cleaned_code, flags=re.MULTILINE).strip()
            return cleaned_code
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return e




