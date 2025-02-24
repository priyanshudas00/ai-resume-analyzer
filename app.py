import streamlit as st
import time
import os
import google.generativeai as genai
from PyPDF2 import PdfReader
import docx
import re

# --- Set Streamlit Page Config ---
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

# Load API Key
genai.configure(api_key="AIzaSyCYDO3mCrFX0I0wFmqjSFpYLaDtzqsrbxI") 

# --- Helper Functions ---
def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    reader = PdfReader(pdf_file)
    text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    return text.strip() if text else ""

def extract_text_from_docx(docx_file):
    """Extract text from a DOCX file."""
    doc = docx.Document(docx_file)
    text = "\n".join(para.text for para in doc.paragraphs)
    return text.strip()

import time

def analyze_resume(resume_text, job_role):
    """AI-powered Resume Analysis with Time Tracking."""
    prompt = f"""
    You are an AI Resume Expert. Analyze the following resume for the job role: {job_role}.
    
    Provide:
    - **Scores (Out of 10) for:**
      - Resume Structure & Clarity
      - Relevant Skills & Experience
      - Grammar & Readability
      - ATS Optimization
    
    - **Strengths & Weaknesses**
    - **Actionable Improvements**
    
    Resume:
    {resume_text}
    """
    try:
        start_time = time.time()  # Start timer
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        ai_time_taken = time.time() - start_time  # Calculate AI response time
        
        if response:
            feedback = response.text
        else:
            feedback = "Error: No response from AI."

        # Estimate manual review time (Assumption: ~10 minutes)
        manual_time = 600  # 600 seconds (10 min)
        reduction_percent = ((manual_time - ai_time_taken) / manual_time) * 100

        # Append time comparison to feedback
        feedback += f"\n\n⏳ AI Processing Time: {ai_time_taken:.2f} sec"
        feedback += f"\n⚡ Estimated Time Reduction: {reduction_percent:.1f}% (vs manual review)"
        
        return feedback
    except Exception as e:
        return f"Error: {e}"


def chatbot_response(user_query, resume_feedback):
    """AI Chatbot for resume discussion."""
    prompt = f"""
    You are a resume expert assistant. Based on the following resume feedback, answer user questions conversationally.
    Resume Feedback:
    {resume_feedback}
    User Query:
    {user_query}
    """
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text if response else "I couldn't process that. Try rephrasing!"
    except Exception as e:
        return f"Error: {e}"

# --- Custom CSS Styling ---
st.markdown("""
    <style>
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            background: linear-gradient(to right, #007bff, #00c6ff);
            color: white;
            font-weight: bold;
        }
        .stTextInput>div>div>input {
            border-radius: 10px;
            border: 2px solid #007bff;
        }
        .stFileUploader>div {
            border: 2px dashed #007bff;
            border-radius: 10px;
            padding: 10px;
        }
        .header {
            text-align: center;
            color: #007bff;
            font-size: 2.5em;
            margin-bottom: 20px;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            font-size: 0.9em;
            color: #555;
        }
    </style>
""", unsafe_allow_html=True)

# --- Streamlit UI ---
st.markdown("<h1 class='header'>📄 AI-Powered Resume Analyzer</h1>", unsafe_allow_html=True)
st.write("Upload your resume and get AI-powered feedback instantly! 🎯")

col1, col2 = st.columns([3, 2])

with col1:
    uploaded_file = st.file_uploader("📂 Upload your resume (PDF/DOCX):", type=["pdf", "docx"])
    resume_text = ""
    if uploaded_file:
        if uploaded_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.name.endswith(".docx"):
            resume_text = extract_text_from_docx(uploaded_file)
    else:
        resume_text = st.text_area("📜 Or paste your resume here:", height=250)

with col2:
    job_role = st.text_input("🎯 Enter Job Role:")
    if st.button("Analyze Resume", use_container_width=True):
        if resume_text.strip() and job_role.strip():
            with st.spinner("🔍 Analyzing resume... Please wait."):
                feedback = analyze_resume(resume_text, job_role)
                st.session_state["resume_feedback"] = feedback
                st.success("✅ Analysis Complete!")
                st.subheader("📊 Resume Feedback")
                st.write(feedback)
        else:
            st.warning("⚠️ Please upload a resume and enter a job role.")

# --- Chatbot Section ---
st.markdown("---")
st.subheader("💬 Chat with AI about your Resume")
user_query = st.text_input("Ask something about your resume feedback:")
if user_query and "resume_feedback" in st.session_state:
    response = chatbot_response(user_query, st.session_state["resume_feedback"])
    st.write("🤖 AI: ", response)

st.markdown("---")
st.markdown("<div class='footer'>Made with ❤️ using Google Gemini & Streamlit</div>", unsafe_allow_html=True)

