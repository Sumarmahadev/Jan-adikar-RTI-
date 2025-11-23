# 🤖 Jan Adhikar RTI-AI — India’s Multilingual Voice-to-PDF RTI Generator

This project helps people in India file RTI (Right to Information) applications easily using WhatsApp.
Many people speak local languages like Hindi, Marathi, Tamil, Telugu, etc., but the RTI office only accepts English letters.
Also, writing a proper RTI letter is very confusing for normal people.

So, I built a WhatsApp-based AI system that can:
- Take voice notes or text messages from users  
- Understand the voice, even if it's in any Indian language  
- Extract the important details  
- Check if anything is missing  
- Create a proper RTI application PDF in English  
- Send it back to the user on WhatsApp  

This whole system works using multiple AI agents, each doing their own job step-by-step.

---

## ✨ Project Highlights

- **Multi-Agent Workflow:** A three-agent system (Agent A → Agent C → Agent B) ensures highly reliable data extraction, validation, and document generation.  
- **Long-Running Sessions:** Manages session state via a database, allowing users to pause, receive follow-up questions, and resume later.  
- **Multi-Lingual Input:** Processes voice messages in various local languages and translates them for structured data extraction.  
- **Structured Data Pipeline (JSON):** The system relies on clean JSON outputs between agents.  

---

## 🚀 Architecture and Data Flow

- **User Input:** User sends a voice note or message on WhatsApp.  
- **Webhook Trigger:** Twilio sends a webhook via Ngrok to the server.  
- **Audio Pipeline:** Converts `.ogg` to `.mp3` using FFMPEG/Pydub.  
- **Agent A:** Extracts structured JSON from the message/audio.  
- **Agent C:** Validates missing data and asks follow-up questions.  
- **Agent B:** Generates the English RTI letter.  
- **PDF Generator:** Creates a professional PDF.  
- **Delivery:** PDF is uploaded and returned to the user.  

---

# Project Description (<15)

I built the RTI-BOT project with one simple goal: helping normal people file RTI applications easily through WhatsApp. Many citizens do not know how to draft a formal RTI letter, especially in proper English. Some can only explain their issues in their own mother tongue like Hindi, Marathi, Tamil, Kannada, or Telugu. Because of this, a lot of genuine concerns never get filed. I wanted to solve this gap with the help of AI and automation.

In my system, the entire workflow starts when a user sends a message or audio on WhatsApp. They can speak normally in their language, explain their issue, and share the details they know. Twilio receives this WhatsApp message and forwards it to my backend server. Since I am running the backend locally during development, I use ngrok to create a public tunnel so Twilio can communicate with my local Flask server.

Once the server receives the message, the first AI Agent processes the text or transcribes the audio and extracts important details like the user's address, department they want information from, and the exact issue they want to raise. This agent also handles multilingual input — it understands regional languages but converts everything into clean English for the RTI letter.

The second agent works like a smart validator. It checks whether the user’s problem is suitable for an RTI or whether more information is needed. If something is missing, the agent waits for the user’s next reply and continues the workflow without breaking the conversation. Then the system automatically searches for the correct Public Information Officer (PIO) address using online data via SerpAPI. Another tool checks similar RTI cases to make the response more accurate.

After collecting all details, the letter-generation agent creates a legally formatted RTI letter in English, because government offices accept RTI applications only in English format. Finally, a PDF is generated using fpdf2 and sent back to the user through WhatsApp.

This project shows how AI, automation, and simple communication tools like WhatsApp can make government processes easy and accessible for everyone.

---

# Problem, Solution & AI Workflow Images

### 1. **Problem**
Citizen stuck with the "Homework Trap" and "Local Language Wall". Rejected applications everywhere.

### 2. **Solution**
"The RTI Warrior" — AI assistant on WhatsApp that clears the path.

### 3. **AI Agent Work**
User says: “Fix my street light!” → System turns it into a perfect RTI letter.

### 4. **Final PDF**
Citizen receives acknowledgment and can file the RTI formally.

---

# 📁 Repository Structure

```
Jan-adikr/
│── app.py
│── agents/
│   ├── agent_a.py
│   ├── agent_b.py
│   └── agent_c.py
│── tools/
│   ├── pio_finder.py
│   ├── pdf_generator.py
│── runtime/
│   ├── agentA_system.txt
│   ├── agentB_system.txt
│   ├── agentC_system.txt
│   ├── pdf/
│   └── db.sqlite3
│── requirements.txt
│── README.md
```

---

# 🧰 Tech Stack

| Purpose          | Technology                          |
| ---------------- | ----------------------------------- |
| AI Agents        | Google Gemini 2.0 Flash & 2.5 Flash |
| Messaging        | Twilio WhatsApp API                 |
| Tunneling        | Ngrok                               |
| Server           | Python (Flask/FastAPI)              |
| Audio Conversion | FFMPEG + Pydub                      |
| File Handling    | Python utils                        |
| PDF Generation   | Python (FPDF2)                      |
| State Management | SQLite                              |
| JSON Workflow    | Agent A → C → B                     |

---

# 🛠️ Setup & Installation

### Clone repo
```
git clone https://github.com/Sumarmahadev/Jan-adikar-RTI-.git
cd jan-adikar
```

### Create environment
```
python -m venv venv
source venv/bin/activate
```

### Install dependencies
```
pip install -r requirements.txt
```

### Add environment variables in `.env`
```
GEMINI_API_KEY=
SERPAPI_KEY=
TWILIO_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=
PUBLIC_BASE_URL=
FLASK_ENV=development
```

### Run server
```
python server.py
```

### Start ngrok
```
ngrok http 5000
```

---

# 📝 Capstone Submission Notes

This project demonstrates expertise in:
- Advanced LLM Orchestration  
- Multi-agent pipelines (A → C → B)  
- WhatsApp automation via Twilio  
- Audio processing with FFMPEG  
- Structured JSON workflows  
- PDF generation pipeline  
- Real-world citizen assistance via AI  

---

