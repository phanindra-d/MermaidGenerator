def correct_mermaid_code(error_msg: str, invalid_code: str, diagram_type: str = "flowchart TD"):
    """
    Sends Mermaid syntax error and invalid code to LLM, asks for corrected valid raw Mermaid code.
    """
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        prompt = f"""
        You are a Mermaid diagram expert.

        The following Mermaid code failed to validate with this error:
        {error_msg}

        Diagram type: {diagram_type}

        Invalid Mermaid code:
        {invalid_code}

        Please analyze the error and return only valid raw Mermaid code for the same diagram type. Do not include any explanation or markdown formatting.
        """
        payload = {
            "model": "google/gemini-2.5-flash",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            raw_text = data["choices"][0]["message"]["content"]
            # Remove markdown fences if present
            cleaned_code = re.sub(r"```[a-zA-Z]*", "", raw_text)
            cleaned_code = re.sub(r"```", "", cleaned_code).strip()
            cleaned_code = re.sub(r"^Here.*?:", "", cleaned_code).strip()
            return cleaned_code
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return str(e)
import requests, re, os
from dotenv import load_dotenv
import logging
from datetime import datetime


load_dotenv()

api_key = os.getenv('OPEN_ROUTER_API')

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


def decide(description: str, existing_code: str):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        payload = {
            # "model": "meta-llama/llama-3.3-70b-instruct",
             "model": "google/gemini-2.5-flash",     
            "messages": [
                {
                    "role": "user",
                    "content": f"""
                        Decide if the user wants to:
                        1. MODIFY the existing diagram.
                        2. Start a NEW diagram.
                        Existing Diagram: {existing_code}
                        User Request: {description}
                        Answer only with one word: MODIFY or NEW
                    """
                }
            ],
             "max_tokens": 5
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            text = data["choices"][0]["message"]["content"].strip()
            return text.upper()
        else:
            return "NEW"
    except Exception as e:
        return str(e)
   

def generate_mermaid(description: str, action: str, diagram_type: str = "flowchart TD", existing_code: str | None = None):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"

        if action == "MODIFY" and existing_code:
            prompt = f"""
                You are a Mermaid diagram editor.

                Existing {diagram_type} diagram:
                {existing_code}

                User wants this modification:
                {description}

                Rules:
                - Keep the existing code intact.
                - Only add/remove/update nodes and edges as required.
                - Do NOT regenerate the whole diagram if unnecessary.
                - Output ONLY valid raw Mermaid code (no markdown, no explanation).
            """
        else:
            prompt = f"""
            Generate a new {diagram_type} Mermaid diagram for:
            {description}

            Rules:
            - Output ONLY valid raw Mermaid code (no markdown, no explanation).
            """

        # Add strict rules and example for erDiagram type
        if diagram_type == "erDiagram":
            prompt += """
            - For erDiagram, follow Mermaid's official ER diagram syntax exactly.
            - Each entity must have attributes inside curly braces.
            - Relationships must be defined outside the entity blocks, after all entities.
            - Do not include any code or text outside valid Mermaid ER syntax.
            - Example:
            erDiagram
                USER {
                VARCHAR id PK
                VARCHAR email
                }
                ACCOUNT {
                UUID id PK
                UUID user_id FK
                }
                OAUTHPROVIDER {
                STRING name PK
                }
                SIGNUPREQUEST {
                UUID id PK
                }
                USER ||--o{ ACCOUNT : has
                ACCOUNT ||--|{ OAUTHPROVIDER : associated_with
                SIGNUPREQUEST ||--o{ USER : initiates_for
                SIGNUPREQUEST ||--o{ OAUTHPROVIDER : uses
                """
        payload = {
            "model": "google/gemini-2.5-flash", 
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            raw_text = data["choices"][0]["message"]["content"]
            if isinstance(raw_text, list):  # handle list content
                raw_text = "".join([t.get("text", "") for t in raw_text])

            log_diagram_action(
                user_prompt=description,
                existing_code=existing_code,
                action=action
            )

            # Remove markdown fences if present
            cleaned_code = re.sub(r"```[a-zA-Z]*", "", raw_text)
            cleaned_code = re.sub(r"```", "", cleaned_code).strip()
            cleaned_code = re.sub(r"^Here.*?:", "", cleaned_code).strip()

            return cleaned_code
        else:
            return f"Error {response.status_code}: {response.text}"

    except Exception as e:
        return str(e) 

