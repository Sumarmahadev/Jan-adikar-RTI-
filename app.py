from flask import Flask, request, jsonify, send_from_directory
import os, json, uuid
from datetime import datetime, UTC
from pathlib import Path
from dotenv import load_dotenv

# here we  load all api keys .env
load_dotenv()

# Local imports
from runtime.database import init_db, get_db_conn
from agents.agent_a import download_and_convert, process_audio_file
from agents.agent_c import agent_c_validate
from agents.agent_b import agent_b_draft
from tools.pio_finder import find_pio
from tools.pdf_generator import generate_pdf
from twilio.rest import Client as TwilioClient

BASE = Path.cwd()
WORKDIR = BASE / 'runtime'
WORKDIR.mkdir(exist_ok=True)


init_db()

app = Flask(__name__)

# Twilio helper
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM')
PUBLIC_BASE_URL = os.getenv('PUBLIC_BASE_URL')


def send_whatsapp_media(to_number, session_id, body_text):
    if not all([TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, PUBLIC_BASE_URL]):
        raise RuntimeError('Twilio credentials and PUBLIC_BASE_URL must be set in .env')
    client = TwilioClient(TWILIO_SID, TWILIO_AUTH_TOKEN)
    media_url = f"{PUBLIC_BASE_URL}/download/{session_id}/rti.pdf"
    msg = client.messages.create(body=body_text, from_=TWILIO_WHATSAPP_FROM, to=to_number, media_url=[media_url])
    return msg.sid


@app.route('/download/<session_id>/rti.pdf', methods=['GET'])
def download_pdf(session_id):
    filename = f"RTI_{session_id}.pdf"
    path = WORKDIR / filename
    if not path.exists():
        return ("Not found", 404)
    return send_from_directory(str(WORKDIR), filename, as_attachment=True)


@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Entry point for Twilio WhatsApp webhook."""
    # Use timezone-aware datetime.now(UTC) to fix deprecation warning
    current_time = datetime.now(UTC).isoformat()
    conn = None # Initialize conn outside try block

    try:
        from_number = request.form.get('From')
        media_url = request.form.get('MediaUrl0')
        body = request.form.get('Body')
        session_id = str(uuid.uuid4())
        
        
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute('INSERT INTO sessions (session_id, phone, state, data, created_at, updated_at) VALUES (?,?,?,?,?,?)',
                    (session_id, from_number, 'started', json.dumps({}), current_time, current_time))
        conn.commit()

        # Agent A: Interview
        if media_url:
            mp3_path = download_and_convert(media_url, (os.getenv('TWILIO_SID'), os.getenv('TWILIO_AUTH_TOKEN')), session_id)
            a_out = process_audio_file(mp3_path, session_id)
        else:
            a_out = {
                'session_id': session_id, 'user_contact': from_number, 'language': 'en', 'raw_transcript': body, 
                'english_transcript': body, 'user_name': None, 'city': None, 'issue_summary': body, 
                'timestamps': {'created_at': current_time}
            }

        current_time = datetime.now(UTC).isoformat()
        cur.execute('UPDATE sessions SET data = ?, state = ?, updated_at = ? WHERE session_id = ?',
                    (json.dumps(a_out), 'interviewed', current_time, session_id))
        conn.commit()
        print(f"[{current_time}] SESSION {session_id} - State: 'interviewed'. Starting Agent C.")

        c_out = agent_c_validate(a_out)
        
        if c_out.get('exempt'):
            current_time = datetime.now(UTC).isoformat()
            cur.execute('UPDATE sessions SET data = ?, state = ?, updated_at = ? WHERE session_id = ?',
                        (json.dumps({**a_out, **c_out}), 'exempt', current_time, session_id))
            conn.commit(); conn.close()
            try:
                send_whatsapp_media(from_number, session_id, f"Your request appears exempt: {c_out.get('exempt_reason')}. Please see advice.")
            except Exception as e:
                print(f"Twilio SEND ERROR (Exempt): {e}")
            return jsonify({'status': 'exempt', 'reason': c_out.get('exempt_reason')})

        # --- CHECK FOR FOLLOW-UP ---
        if c_out.get('followups'):
            current_time = datetime.now(UTC).isoformat()
            cur.execute('UPDATE sessions SET data = ?, state = ?, updated_at = ? WHERE session_id = ?',
                        (json.dumps({**a_out, **c_out}), 'waiting_followup', current_time, session_id))
            conn.commit(); conn.close()
            try:
                client = TwilioClient(TWILIO_SID, TWILIO_AUTH_TOKEN)
                client.messages.create(body=c_out['followups'][0]['text'], from_=TWILIO_WHATSAPP_FROM, to=from_number)
            except Exception as e:
                print(f"Twilio SEND ERROR (Followup): {e}")
            return jsonify({'status': 'need_followup', 'followup': c_out['followups'][0]})

       
        # 1. Agent B (draft)

        b_out = agent_b_draft(c_out)
        print(f"[{datetime.now(UTC).isoformat()}] SESSION {session_id} - Agent B successful. Starting PIO Lookup.")


        # 2.  here PIO lookup
        try:
            pio = find_pio(b_out.get('department_likely'), b_out.get('city'))
        except Exception as e:
           
            print(f"[{datetime.now(UTC).isoformat()}] CRASH POINT: PIO LOOKUP FAILED. Error: {e}")
            raise RuntimeError(f"PIO Lookup failed: {e}") 

        print(f"[{datetime.now(UTC).isoformat()}] SESSION {session_id} - PIO Lookup successful. Starting PDF Generation.")

        # 3 here we geanrate pdf
        try:
            pdf_meta = generate_pdf({**b_out, 'pio_address': pio['pio_address'], 'session_id': session_id})
        except Exception as e:
            print(f"[{datetime.now(UTC).isoformat()}] CRASH POINT: PDF GENERATION FAILED. Error: {e}")
            raise RuntimeError(f"PDF Generation failed: {e}") 
        
        # Persist final (State: 'completed')
        current_time = datetime.now(UTC).isoformat()
        cur.execute('UPDATE sessions SET data = ?, state = ?, updated_at = ? WHERE session_id = ?',
                    (json.dumps({**a_out, **c_out, **b_out, **pio, **pdf_meta}), 'completed', current_time, session_id))
        conn.commit(); conn.close()
        print(f"[{current_time}] SESSION {session_id} - State: 'completed'. Attempting final Twilio send.")

        # 4. Final Twilio send
        try:
            send_whatsapp_media(from_number, session_id, 'Here is your RTI application. Verify address before submitting.')
        except Exception as e:
            print(f"[{datetime.now(UTC).isoformat()}] CRITICAL Twilio MEDIA SEND ERROR (POST-COMPLETE): {e}")

        return jsonify({'status': 'success', 'session_id': session_id, 'pdf': pdf_meta['pdf_file_path']})

    except Exception as e:
        if conn: conn.close()
        print(f"[{datetime.now(UTC).isoformat()}] FATAL UNHANDLED ERROR for session {session_id}: {e}")
        return jsonify({'status': 'error', 'error': str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)