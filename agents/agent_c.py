import os, json
from pathlib import Path
from datetime import datetime, UTC
import google.generativeai as genai

WORKDIR = Path.cwd() / 'runtime'
SYSTEM_PROMPT_PATH = WORKDIR / 'agentC_system.txt'

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# here expected JSON schema for Agent C's output
VALIDATOR_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "exempt": {"type": "BOOLEAN", "description": "True if request is exempt under RTI Section 8."},
        "exempt_reason": {"type": "STRING", "nullable": True, "description": "Reason for exemption, if applicable."},
        "followups": {
            "type": "ARRAY",
            "description": "List of missing details needed to proceed.",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "id": {"type": "STRING"},
                    "text": {"type": "STRING"}
                }
            }
        },
        "cleaned_issue_summary": {"type": "STRING", "description": "A single clear English sentence summarizing the issue."}
    },
    "required": ["exempt", "followups", "cleaned_issue_summary"]
}


def agent_c_validate(interviewer_json):
    if not SYSTEM_PROMPT_PATH.exists():

        raise RuntimeError('agentC_system.txt missing in runtime/')
    system_text = SYSTEM_PROMPT_PATH.read_text()
    
    
    prompt = f"Given the interviewer JSON below, return only a compact JSON object matching the validator schema.\n{json.dumps(interviewer_json)}"
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
    
    response = model.generate_content(
        [system_text, prompt],
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": VALIDATOR_SCHEMA
        }
    )
    
    # The response.text is now comes  to be JSON or the API call fails
    try:
        
        parsed = json.loads(response.text)
    except Exception as e:
        raise RuntimeError(f'Agent C: failed to parse API JSON response: {e}\nRaw:\n{response.text}')

    parsed.setdefault('audit', {})
    parsed['audit']['agentC'] = {'model': 'gemini-2.5-flash-preview-09-2025'}
    parsed.setdefault('validated_at', datetime.now(UTC).isoformat())
    return parsed