import os, json
from pathlib import Path
from datetime import datetime, UTC
import requests
import google.generativeai as genai

WORKDIR = Path.cwd() / 'runtime'
SYSTEM_PROMPT_PATH = WORKDIR / 'agentA_system.txt'

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))


def download_and_convert(media_url, auth_tuple, session_id):
    """
    Downloads an audio file from Twilio, saves it, and returns the path.
    """
    if not auth_tuple:
        raise RuntimeError('Twilio authentication required for media download.')
        
    response = requests.get(media_url, auth=auth_tuple, stream=True)
    if response.status_code != 200:
        raise RuntimeError(f'Failed to download media: {response.status_code}')

    # Save as .mp3 for simplicity in simulation
    mp3_path = WORKDIR / f'{session_id}.mp3'
    with open(mp3_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    print(f"[{datetime.now(UTC).isoformat()}] Downloaded audio to {mp3_path}")
    return mp3_path


def process_audio_file(mp3_path, session_id):
    """
    Transcribes and extracts structured data from the audio file using a Gemini model.
    """
    if not SYSTEM_PROMPT_PATH.exists():
        raise RuntimeError('agentA_system.txt missing in runtime/')
        
    system_text = SYSTEM_PROMPT_PATH.read_text()
   
    audio_file = genai.upload_file(mp3_path)
    
    prompt = "Transcribe this audio file and use the transcript to extract the required JSON data fields."
    
    # here the expected JSON schema for Agent A's output
    EXTRACTION_SCHEMA = {
        "type": "OBJECT",
        "properties": {
            "user_name": {"type": "STRING", "nullable": True},
            "city": {"type": "STRING", "nullable": True},
            "issue_summary": {"type": "STRING"},
            "language": {"type": "STRING"}
        },
        "required": ["issue_summary", "language"]
    }
    
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
    
    response = model.generate_content(
        [system_text, audio_file, prompt],
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": EXTRACTION_SCHEMA
        }
    )
    genai.delete_file(audio_file)
    Path(mp3_path).unlink()

    try:
        parsed = json.loads(response.text)
    except Exception as e:
        raise RuntimeError(f'Agent A: failed to parse API JSON response: {e}\nRaw:\n{response.text}')
        
    a_out = {
        'session_id': session_id,
        'user_contact': None, 
        'raw_transcript': response.text, # Storing the full model response as 'raw_transcript' for audit/debug
        'english_transcript': parsed.get('issue_summary', ''), 
        'user_name': parsed.get('user_name'),
        'city': parsed.get('city'),
        'issue_summary': parsed.get('issue_summary'),
        'language': parsed.get('language'),
        'timestamps': {'created_at': datetime.now(UTC).isoformat()},
        'audit': {'agentA': {'model': 'gemini-2.5-flash-preview-09-2025'}}
    }
    return a_out