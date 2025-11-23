import os, json
from pathlib import Path
from datetime import datetime
import google.generativeai as genai


WORKDIR = Path.cwd() / 'runtime'
SYSTEM_PROMPT_PATH = WORKDIR / 'agentB_system.txt'

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Define the expected JSON schema for Agent B's output
DRAFTING_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "rti_letter_english": {
            "type": "STRING",
            "description": "The complete drafted RTI application letter, ready for formatting into a PDF."
        },
        "department_likely": {
            "type": "STRING",
            "description": "The specific Government department (e.g., Public Works Dept) the application should be addressed to."
        },
        "city": {
            "type": "STRING",
            "description": "The specific city or municipality related to the issue, used for PIO lookup."
        },
        "jurisdiction_type": {
            "type": "STRING",
            "description": "Central or State government jurisdiction."
        }
    },
    "required": ["rti_letter_english", "department_likely", "city", "jurisdiction_type"]
}


def agent_b_draft(validated_json):
    if not SYSTEM_PROMPT_PATH.exists():
        raise RuntimeError('agentB_system.txt missing in runtime/')
    system_text = SYSTEM_PROMPT_PATH.read_text()
    
    prompt = f"Using the validated JSON below, draft a legally-sound RTI application and fill the required fields in the Drafting Schema.\n{json.dumps(validated_json)}"
    
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
    
   
    config_dict = {
        "response_mime_type": "application/json",
        "response_schema": DRAFTING_SCHEMA
    }
    
   
    response = model.generate_content(
        [system_text, prompt],
        generation_config=config_dict
    )
    
   
    try:
        parsed = json.loads(response.text)
    except Exception as e:
        
        raise RuntimeError(f'Agent B: failed to parse API JSON response: {e}\nRaw:\n{response.text}')

    parsed.setdefault('audit', {})
    parsed['audit']['agentB'] = {'model': 'gemini-2.5-flash-preview-09-2025'} 
    parsed.setdefault('drafted_at', datetime.utcnow().isoformat())
    return parsed