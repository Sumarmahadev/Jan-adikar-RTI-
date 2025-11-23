🤖 Jan Adhikar RTI-AI — India’s Multilingual Voice-to-PDF RTI Generator
This project helps people in India file RTI (Right to Information) applications easily using WhatsApp.
Many people speak local languages like Hindi, Marathi, Tamil, Telugu, etc., but the RTI office only accepts English letters.
Also, writing a proper RTI letter is very confusing for normal people.So, 
I built a WhatsApp-based AI system that can:
Take voice notes or text messages from users
nderstand the voice, even if it’s in any Indian language
Extract the important details
Check if anything is missing
And finally, create a proper RTI application PDF in English
Then send it back to the user on WhatsApp
This whole system works using multiple AI agents, each doing their own job step-by-step.
✨ Project Highlights
Multi-Agent Workflow: A three-agent system (Agent A -> Agent C -> Agent B) ensures highly reliable data extraction, validation, and document generation.
Long-Running Sessions: Manages session state via a database, allowing users to pause, receive follow-up questions from Agent C, and resume later.
Multi-Lingual Input: Processes voice messages in various local languages, transcribing and translating them for structured data extraction.
Structured Data Pipeline (JSON): The entire system relies on clean JSON outputs between agents for predictability and robustness.
🚀 Architecture and Data Flow
The system runs entirely within a Python backend, serving as a webhook receiver for Twilio.
User Input: A user sends a voice note to the Twilio WhatsApp number.
Webhook Trigger: Twilio sends a webhook (including MediaUrl) via Ngrok to the server.py endpoint.
Audio Pipeline (utils.py): Downloads the audio (.ogg), converts it to a standard format (.mp3) using FFMPEG/Pydub, and stores it temporarily.
Agent A (JSON Extractor): Uses Gemini 2.0 Flash to consume the audio file and strictly output a JSON object containing user_name, city, issue_summary, and language.
Agent C (Session Manager/Validator): Takes the JSON, checks for missing mandatory fields (like city or name). If data is incomplete, it initiates a follow-up conversation loop with the user via WhatsApp to gather missing data. If valid, it proceeds.
Agent B (Legal Draftsman): Uses Gemini 2.5 Flash and its system prompt to generate the formal RTI application letter text based on the validated JSON.
PDF Generation: The server uses the generated text to create a professionally formatted PDF.
User Delivery: The server uploads the PDF to a public asset host (e.g., using the Ngrok asset URL trick for local testing) and sends the PDF link back to the user via Twilio.


1:Project Description(<15)
I built the RTI-BOT project with one simple goal: helping normal people file RTI applications easily through WhatsApp. Many citizens do not know how to draft a formal RTI letter, especially in proper English. Some can only explain their issues in their own mother tongue like Hindi, Marathi, Tamil, Kannada, or Telugu. Because of this, a lot of genuine concerns never get filed. I wanted to solve this gap with the help of AI and automation.
In my system, the entire workflow starts when a user sends a message or audio on WhatsApp. They can speak normally in their language, explain their issue, and share the details they know. Twilio receives this WhatsApp message and forwards it to my backend server. Since I am running the backend locally during development, I use ngrok to create a public tunnel so Twilio can communicate with my local Flask server.
Once the server receives the message, the first AI Agent processes the text or transcribes the audio and extracts important details like the user’s address, department they want information from, and the exact issue they want to raise. This agent also handles multilingual input — it understands regional languages but converts everything into clean English for the RTI letter.The second agent works like a smart validator. It checks whether the user’s problem is suitable for an RTI or whether more information is needed. If something is missing, the agent waits for the user’s next reply and continues the workflow without breaking the conversation.Then the system automatically searches for the correct Public Information Officer (PIO) address using online data via SerpAPI. Another tool checks similar RTI cases to make the response more accurate. After collecting all details, the letter-generation agent creates a legally formatted RTI letter in English, because government offices accept RTI applications only in English format.
Finally, a PDF is generated using fpdf2 and sent back to the user through WhatsApp. The user receives a ready-to-print, professional RTI application directly on their phone, just by chatting in their own language.

This project shows how AI, automation, and simple communication tools like WhatsApp can make government processes easy and accessible for everyone.



1:problem :
This image depicts the initial struggle of a citizen facing the "Homework Trap" and the "Local Language Wall." The character is overwhelmed by a pile of rejected applications and a language barrier, with no clear path forward.




2:soluton:This image introduces "The RTI Warrior" as the solution. The same citizen is now empowered, using the ai agnet  on their whatsapp . The app has simplified the process, and a clear path has opened up through the obstacles, leading to the correct government department.



3:ai agent work here:
This image visualizes the core function of the app. A simple, natural-language request ("Fix my street light!") on the phone is instantly transformed into a perfectly formatted, formal letter that is correctly addressed to the relevant government office.


4)Final pdf:
The final image shows the positive outcome. The citizen's problem (the broken street light) has been fixed, and they are receiving an official government document acknowledging their request.after that bu using the pdf they can compailne the report 


6)Project Description(<15)





















📁 Repository Structure
Jan-adikr/
│── app.py                     # Flask server + routing
│── agents/
│   ├── agent_a.py
│   ├── agent_b.py
│   └── agent_c.py
│── tools/
│   ├── pio_finder.py
│   ├── pdf_generator.py
│  
│── runtime/
│   ├── agentA_system.txt
│   ├── agentB_system.txt
│   ├── agentC_system.txt
│   ├── pdf/
│   └── db.sqlite3
│── requirements.txt
│── README.md
__________________________________________________________________

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
| JSON Workflow    | Between Agent A → C → B             |


🛠️ Setup and Installation
Prerequisites
Python 3.12 or higher.
FFMPEG: Must be installed on your system and accessible via the command line for audio conversion.
Twilio Account: A registered WhatsApp sandbox or number.
Ngrok: A free account to expose your local environment.
Gemini API Key: Set as an environment variable (GEMINI_API_KEY).
Installation Steps
Clone the repository:
git clone https://github.com/Sumarmahadev/Jan-adikar-RTI-.git
cd jan-adikar


Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows, use: .\venv\Scripts\activate


Install dependencies:
pip install -r requirements.txt


Configure Environment Variables:
Create a .env file in the root directory:
GEMINI_API_KEY=
SERPAPI_KEY=
TWILIO_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=
PUBLIC_BASE_URL=
FLASK_ENV=development

Start Ngrok and the Server:
In terminal 1, start the backend (e.g., if using Flask):
python server.py


In terminal 2, start ngrok, pointing it to your server's port (e.g., 5000):
ngrok http 5000


Copy the secure Ngrok HTTPS URL and configure it as the Messaging Webhook URL in your Twilio console.
📝 Capstone Submission Notes
This project demonstrates expertise in:
Advanced LLM Orchestration: Utilizing distinct LLMs (Gemini 2.0 Flash for multimodal/structured output, Gemini 2.5 Flash for complex text generation) within a multi-step pipeline.
System Integration: Seamlessly connecting a messaging platform (WhatsApp/Twilio), external tools (FFMPEG), and the AI backend.
Robustness: Enforcing a JSON-based data contract between sequential agents to ensure stability and reliable data transfer.
