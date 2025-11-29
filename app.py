# app.py

import streamlit as st
import os
import shutil # New import to handle directory cleanup
from rag_backend import build_vector_db, load_vector_db, get_qa_chain

# --- CONFIGURATION ---
# Assumes CHROMA_PATH is read from .env in rag_backend.py, 
# but we need it here for cleanup/checking.
# For simplicity, we hardcode the known path used in rag_backend.py:
CHROMA_PATH = "db/hr_policy_embeddings" 
UPLOAD_DIR = "uploads"
DEFAULT_POLICY_PATH = "sample_policies/combined_hr_policy.pdf"


st.set_page_config(page_title="HR Assistant Agent", layout="wide")

st.title("🧑‍💼 HR Assistant Agent (Policy & Action)")
st.write("Ask questions about HR policies, leave rules, or request actions like checking PTO balance.")

# --- SIDEBAR: Knowledge Base Management ---
st.sidebar.header("📄 Knowledge Base Manager")

# Option to use the default policy file
use_default = st.sidebar.checkbox("Use default HR policy (combined_hr_policy.pdf)", value=True)

# Option to upload new policies
uploaded_files = st.sidebar.file_uploader(
    "Upload additional HR policy PDFs", 
    type=["pdf"], 
    accept_multiple_files=True
)

if st.sidebar.button("Build / Rebuild Vector DB"):
    pdf_list = []

    # 1. Cleanup old uploads and DB
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # 2. Collect file paths
    if use_default:
        if os.path.exists(DEFAULT_POLICY_PATH):
            pdf_list.append(DEFAULT_POLICY_PATH)
        else:
            st.warning(f"Default policy not found at: {DEFAULT_POLICY_PATH}")
            
    if uploaded_files:
        for file in uploaded_files:
            # Save uploaded files to the uploads directory
            path = os.path.join(UPLOAD_DIR, file.name)
            with open(path, "wb") as f:
                f.write(file.getbuffer())
            pdf_list.append(path)

    # 3. Build DB
    if pdf_list:
        with st.spinner("Indexing documents and building vector store..."):
            try:
                # build_vector_db now accepts a list of PDF paths
                vectordb = build_vector_db(pdf_list) 
                st.session_state['vectordb_ready'] = True
                st.success(f"Indexing complete! {len(pdf_list)} documents indexed.")
            except Exception as e:
                 st.error(f"Error during indexing. Check OPENAI_API_KEY and document format: {e}")
    else:
        st.error("No PDFs selected to index! Check the default checkbox or upload a file.")

# --- Initialize QA Chain ---
qa = None
vectordb_ready = st.session_state.get('vectordb_ready', False)

if os.path.exists(CHROMA_PATH) or vectordb_ready:
    try:
        # Load existing DB
        vectordb = load_vector_db()
        # Get the Tool-Enabled Agent Executor
        qa = get_qa_chain(vectordb)
        st.sidebar.success("✅ Agent and Knowledge Base Loaded.")
    except Exception as e:
        st.error(f"Error loading Agent/DB: {e}. Please rebuild the Vector DB.")
else:
    st.warning("Please build the Vector DB first from the sidebar.")


# ---- MAIN QUERY SECTION ----
st.subheader("❓ Ask a Question")
# Hardcoded Employee ID for the tool use demonstrations (in a real app, this is secured via user session)
st.info(f"Using Mock Employee ID: E1001 for personalized queries (defined in hris_tools.py).")

query = st.text_input("Example questions: 'How many vacation days do I have left?' or 'What is the WFH policy?'")

if st.button("Get Answer"):
    if not qa:
        st.error("The Agent is not configured. Please build the documents first.")
    elif query.strip() == "":
        st.error("Please enter a question.")
    else:
        with st.spinner("Agent is searching and deciding whether to use RAG or HRIS Tools..."):
            try:
                # The 'qa' variable now points to the execute_agent_query wrapper function
                result = qa(query) 
                
                st.markdown("### ✅ Agent Answer")
                # The agent's final answer is in the 'result' key
                st.write(result["result"]) 

                st.markdown("---")
                st.markdown("### ℹ️ Note on Sources")
                st.info("Since the Agent can use multiple tools (RAG, HRIS APIs), the source tracking is handled by the Agent's reasoning, not the simple source document list of the previous chain type. Check your terminal output for the Agent's 'verbose' reasoning log.")
                
            except Exception as e:
                st.error(f"An error occurred during query execution: {e}")


# --- End of app.py ---