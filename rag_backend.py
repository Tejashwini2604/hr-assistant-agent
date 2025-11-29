# rag_backend.py

import os
import shutil 
from dotenv import load_dotenv

# --- CORE LANGCHAIN IMPORTS (Modularized and Corrected) ---
# Text Splitter
from langchain_text_splitters import RecursiveCharacterTextSplitter 
# Loaders/Utilities
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
# OpenAI Components
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# --- AGENT AND CORE RUNNABLES IMPORTS ---
# AgentExecutor, Tool, and Prompts are consistently under langchain_core
from langchain_core.agents import AgentExecutor 
from langchain_core.tools import Tool 
from langchain_core.prompts import ChatPromptTemplate
# Other core runnables
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# The Agent creation function is one of the few that often remains in the top-level
# If the clean install works, this line should resolve the import error
from langchain.agents import create_openai_tools_agent 

# --- HRIS TOOLS IMPORT ---
# IMPORTANT: Ensure your hris_tools.py file has these functions defined!
from hris_tools import check_pto_balance, submit_leave_request 

# --- 1. Configuration ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_PATH = os.getenv("CHROMA_PATH", "db/hr_policy_embeddings")
LLM_MODEL = "gpt-4-turbo-2024-04-09" # Recommended model for tool use

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please check your .env file.")

# --- 2. Core Vector DB Functions ---

def build_vector_db(pdf_paths: list):
    """Loads PDFs, chunks the text, creates embeddings, and saves them to ChromaDB."""
    print("--- 📄 Starting PDF Loading and Chunking ---")
    documents = []
    
    for path in pdf_paths:
        try:
            if os.path.exists(path):
                loader = PyPDFLoader(path)
                documents.extend(loader.load())
                print(f"Loaded pages from {path}")
            else:
                print(f"Skipping file: {path} not found.")
        except Exception as e:
            print(f"Error loading PDF from {path}: {e}")

    if not documents:
        print("No documents loaded successfully.")
        return None
        
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Total documents split into {len(chunks)} chunks.")
    
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    
    os.makedirs(CHROMA_PATH, exist_ok=True)
    
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH 
    )
    
    db.persist()
    print(f"--- ✅ Vector Store successfully saved to {CHROMA_PATH} ---")
    return db


def load_vector_db():
    """Loads the existing ChromaDB vector store."""
    if not os.path.exists(CHROMA_PATH) or not os.listdir(CHROMA_PATH):
        raise FileNotFoundError(f"Vector DB not found at {CHROMA_PATH}.") 
        
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    
    db = Chroma(
        persist_directory=CHROMA_PATH, 
        embedding_function=embeddings
    )
    
    print("--- 💾 Vector Store loaded successfully ---")
    return db

# --- 3. Agent Executor Function (get_qa_chain) ---

def get_qa_chain(vectordb: Chroma):
    """Creates and returns a LangChain Agent Executor (Tool-Enabled Agent)."""
    llm = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY, 
        model_name=LLM_MODEL, 
        temperature=0
    )
    
    # 3.1 Define the RAG Retriever as a Tool
    retriever_tool = Tool(
        name="Policy_Document_Retriever",
        func=vectordb.as_retriever(search_kwargs={"k": 3}).invoke,
        description="Tool for searching and retrieving information from the official HR Policy Documents. USE THIS ONLY FOR GENERAL POLICY QUESTIONS (e.g., 'What is the WFH policy?').",
    )
    
    # 3.2 Define the HRIS Tools and combine with the RAG Tool
    hris_tools = [check_pto_balance, submit_leave_request]
    tools = hris_tools + [retriever_tool]

    # 3.3 Define the System Prompt
    system_message = (
        "You are the **HR Assistant Agent**. Your role is to provide quick, accurate, and confidential "
        "support to employees. Your primary goal is to determine the user's intent: \n\n"
        "1. **Personalized Action (Tools):** If the user asks for their specific PTO, leave submission, or other personal data, **ALWAYS** use the appropriate HRIS tool (e.g., `check_pto_balance`). The default Employee ID for mock data is 'E1001'.\n"
        "2. **General Policy (RAG):** If the user asks for general company rules, **ALWAYS** use the `Policy_Document_Retriever` tool.\n"
        "Answer concisely and clearly. **Do not** generate output until the necessary tool steps are complete."
    )
    
    # 3.4 Create the Prompt Template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("placeholder", "{agent_scratchpad}"), 
            ("human", "{query}")
        ]
    )
    
    # 3.5 Create the Agent and Agent Executor
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    qa_agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_errors=True,
        max_iterations=15
    )
    
    print("--- 🔗 Agent Executor (Tool-Enabled QA Chain) ready ---")
    
    # 3.6 Return the executable function
    def execute_agent_query(query: str):
        return {
            "result": qa_agent_executor.invoke({"query": query})['output'],
            "source_documents": [] 
        }

    return execute_agent_query

# --- 4. Example/Test Execution (Optional) ---
if __name__ == "__main__":
    print("--- Running Test Execution ---")
    try:
        db = load_vector_db()
        qa_agent = get_qa_chain(db)
        
        test_query = "What is the policy for working from home?"
        print(f"\nQUERY: {test_query}")
        
        result = qa_agent(test_query)
        
        print("\n--- FINAL ANSWER ---")
        print(result["result"])
                
    except FileNotFoundError as e:
        print(f"\n{e}")
        print("Run the build_vector_db function (via Streamlit sidebar) to create the database first.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")