from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus
from prompt import generate_mermaid, decide
from pydantic import BaseModel
import logging


load_dotenv()

api_key = os.getenv('GEMINI_KEY')



class MermaidRequest(BaseModel):
    description: str
    diagram_type: str = "flowchart TD"
    existing_code: str | None = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5501"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.post("/generate-mermaid")
async def create_mermaid(request: MermaidRequest):
    try:
        logging.info(f"New Request → description='{request.description}', diagram_type='{request.diagram_type}'")

        if not request.existing_code:
            action = "NEW"
        else:
            action = decide(request.description, request.existing_code)

        result = generate_mermaid(request.description, action=action, diagram_type=request.diagram_type, existing_code=request.existing_code)

        logging.info(f"Action={action}, Generated code length={len(result)}")

        return {
            "mermaid_code": result,
            "action": action,
            "diagram_type": request.diagram_type
        }
    except Exception as e:
        return {"error":e}