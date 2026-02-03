import streamlit as st
import requests
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Code Documenter",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE INITIALIZATION ---
if "task_id" not in st.session_state:
    st.session_state.task_id = None
if "processed_code" not in st.session_state:
    st.session_state.processed_code = None
if "status" not in st.session_state:
    st.session_state.status = "idle"

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("🔌 Backend Connection")
    # Allow user to change the backend URL if running on a different port/host
    base_url = st.text_input("API URL", value="http://127.0.0.1:8000")
    
    st.header("⚙️ Documentation Style")
    style_option = st.selectbox(
        "Select Style",
        ("Google Style", "NumPy Style", "Sphinx Style"),
        index=0
    )
    
    st.divider()
    st.info("Ensure your FastAPI backend is running before uploading.")

# --- HELPER FUNCTIONS ---
def upload_file(file, style):
    """Sends the file to the backend and returns the task_id."""
    try:
        files = {"file": (file.name, file, "text/x-python")}
        params = {"style": style}
        response = requests.post(f"{base_url}/upload", files=files, params=params)
        
        if response.status_code == 202:
            return response.json().get("task_id")
        else:
            st.error(f"❌ Upload failed: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to Backend. Is it running?")
        return None

def check_status(task_id):
    """Polls the backend to check if processing is done."""
    try:
        response = requests.get(f"{base_url}/status/{task_id}")
        if response.status_code == 200:
            return response.json().get("status")
        return "unknown"
    except:
        return "error"

def get_result(task_id):
    """Fetches the final documented code."""
    try:
        response = requests.get(f"{base_url}/result/{task_id}")
        if response.status_code == 200:
            return response.json().get("code", "")
        else:
            st.error("Failed to fetch result.")
            return None
    except:
        return None

# --- MAIN UI LAYOUT ---
st.title("🤖 Automated Code Commenter")
st.markdown("Upload a raw Python file. The AI will add professional Docstrings and Type Hints in the background.")

col1, col2 = st.columns([1, 1])

# --- COLUMN 1: UPLOAD & ORIGINAL CODE ---
with col1:
    st.subheader("1. Source Code")
    uploaded_file = st.file_uploader("Upload .py file", type=["py"])

    if uploaded_file:
        # Read and decode the uploaded file for preview
        original_code = uploaded_file.getvalue().decode("utf-8")
        st.code(original_code, language="python", line_numbers=True)

        # Action Button
        if st.button("✨ Auto-Document Code", type="primary", disabled=st.session_state.status == "processing"):
            with st.spinner("Initiating background task..."):
                task_id = upload_file(uploaded_file, style_option)
                if task_id:
                    st.session_state.task_id = task_id
                    st.session_state.status = "processing"
                    st.session_state.processed_code = None # Reset previous result
                    st.rerun()

# --- COLUMN 2: PROCESSING & RESULT ---
with col2:
    st.subheader("2. AI Output")

    # STATE: PROCESSING (Polling Loop)
    if st.session_state.status == "processing":
        status_box = st.empty()
        progress_bar = st.progress(0)
        
        # Simple polling mechanism
        for i in range(1, 101):
            status = check_status(st.session_state.task_id)
            
            status_box.info(f"Task ID: {st.session_state.task_id}\n\nStatus: **{status.upper()}**")
            
            if status == "completed":
                st.session_state.status = "completed"
                progress_bar.progress(100)
                # Fetch the result immediately
                st.session_state.processed_code = get_result(st.session_state.task_id)
                st.rerun()
                break
            elif status == "failed":
                st.session_state.status = "failed"
                st.error("Processing failed on the server.")
                break
            
            # Fake progress for UX while waiting
            progress_bar.progress(min(i * 2, 90))
            time.sleep(1) # Poll every 1 second

    # STATE: COMPLETED
    elif st.session_state.status == "completed" and st.session_state.processed_code:
        st.success("✅ Documentation Complete!")
        st.code(st.session_state.processed_code, language="python", line_numbers=True)
        
        # Download Button
        st.download_button(
            label="💾 Download Result",
            data=st.session_state.processed_code,
            file_name=f"documented_{uploaded_file.name}", # type: ignore
            mime="text/x-python"
        )
        
        if st.button("🔄 Start Over"):
            st.session_state.status = "idle"
            st.session_state.task_id = None
            st.session_state.processed_code = None
            st.rerun()
            
    # STATE: IDLE
    else:
        st.info("Waiting for file upload...")