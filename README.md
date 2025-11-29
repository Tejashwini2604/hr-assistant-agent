HR Assistant Agent (RAG-based AI Chatbot)

An AI-powered HR Assistant Agent that answers policy, leave, payroll, and benefits-related questions using Retrieval-Augmented Generation (RAG).
This system loads HR policy documents, creates embeddings, stores them in a vector database, and generates accurate, document-grounded answers using an LLM.

Built for internship/project evaluation — simple, clear, and production-ready.

📚 Features
✅ 1. HR Query Answering

Answers employee questions about:

Leave policies
Payroll rules
Attendance guidelines
Benefits & allowances
HR procedures

Responses are factual and based on your uploaded PDF policies.

✅ 2. RAG Pipeline

PDF ingestion → Text splitting
Embedding generation using OpenAI
Vector DB storage using ChromaDB
Retrieval + LLM generation using LangChain

✅ 3. Streamlit UI

Simple chat interface
Upload PDFs and rebuild the vector database
Ask real-time HR queries

✅ 4. Configurable

Add your own policy PDFs
Supports multiple files
Local vector DB persistence

🏗️ Tech Stack
Component	Technology
Backend	Python, LangChain
Vector DB	ChromaDB
Embeddings	OpenAI Embeddings
UI	Streamlit
Document Loader	PyPDFLoader
Framework	RAG pipeline
📁 Project Structure
hr-assistant-agent/
│
├── app.py                  # Streamlit UI
├── rag_backend.py          # RAG pipeline backend
├── hris_tools.py           # Utility helpers
├── sample_policies/        # Example HR PDFs
├── requirements.txt        # Dependencies
├── .env                    # API keys
└── README.md               # Project documentation

⚙️ Installation & Setup
1. Clone Repository
git clone https://github.com/Tejashwini2604/hr-assistant-agent.git
cd hr-assistant-agent

2. Create Virtual Environment
python -m venv venv
source venv/Scripts/activate  # Windows

3. Install Dependencies
pip install -r requirements.txt

4. Add API Key
Create a .env file:
OPENAI_API_KEY=your_api_key_here

▶️ Run the Application
streamlit run app.py

App will start at:
http://127.0.0.1:8501

🧠 How It Works (Short Explanation)

Load PDFs → PyPDFLoader extracts text

Split Text → Large documents become manageable chunks

Generate Embeddings → OpenAI converts text → vector format

Store in Vector DB → Chroma stores embeddings

User asks a query

Retriever fetches relevant chunks

LLM generates a final answer grounded in policy text
