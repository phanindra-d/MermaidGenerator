from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus
from prompt import generate_mermaid, decide, correct_mermaid_code
from pydantic import BaseModel
import logging
from validate_mermaid import validate_mermaid_code


load_dotenv()

api_key = os.getenv('OPEN_ROUTER_API')



class MermaidRequest(BaseModel):
    description: str
    diagram_type: str = "flowchart TD"
    existing_code: str | None = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

def diagram_type_in_code(diagram_type, existing_code):
    # Check if the first line of the code matches the diagram type
    if not existing_code:
        return False
    first_line = existing_code.splitlines()[0].strip()
    return diagram_type in first_line

@app.post("/generate-mermaid")
async def create_mermaid(request: MermaidRequest):
    try:
        logging.info(f"New Request → description='{request.description}', diagram_type='{request.diagram_type}'")

        # If diagram type changed, thenn NEW
        if not request.existing_code or not diagram_type_in_code(request.diagram_type, request.existing_code):
            action = "NEW"
        else:
            action = decide(request.description, request.existing_code)

        max_attempts = 4
        result = None
        error_msg = ""
        for attempt in range(max_attempts):
            result = generate_mermaid(
                request.description,
                action=action,
                diagram_type=request.diagram_type,
                existing_code=request.existing_code
            )
            is_valid, error_msg = validate_mermaid_code(result)
            if is_valid:
                logging.info(f"Action={action}, Generated code length={len(result)}")
                return {
                    "mermaid_code": result,
                    "action": action,
                    "diagram_type": request.diagram_type
                }
            else:
                logging.error(f"Mermaid validation failed: {error_msg}")
                result = correct_mermaid_code(error_msg, result, request.diagram_type)
        raise HTTPException(status_code=400, detail=f"Mermaid code invalid after {max_attempts} attempts: {error_msg}")
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))