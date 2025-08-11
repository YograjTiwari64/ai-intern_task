import streamlit as st
from docx import Document
import tempfile
import os

# --- ADGM Checklist Example ---
ADGM_CHECKLIST = {
    "Company Incorporation": [
        "Articles of Association",
        "Memorandum of Association",
        "Board Resolution",
        "Shareholder Resolution",
        "Incorporation Application Form",
        "UBO Declaration Form",
        "Register of Members and Directors",
        "Change of Registered Address Notice"
    ]
    # Add more processes and their required docs as needed
}

def identify_process_and_docs(uploaded_docs):
    # Placeholder: Use LLM/RAG to identify process and doc types
    process = "Company Incorporation"
    doc_types = []
    for doc in uploaded_docs:
        for required in ADGM_CHECKLIST[process]:
            if required.lower().replace(" ", "") in doc.name.lower().replace(" ", ""):
                doc_types.append(required)
    return process, doc_types

def check_missing_docs(process, doc_types):
    required = set(ADGM_CHECKLIST[process])
    uploaded = set(doc_types)
    missing = list(required - uploaded)
    return missing

def analyze_doc(docx_file):
    # Placeholder: Use LLM/RAG to analyze doc and find issues
    # For now, return dummy issue
    return [{
        "document": docx_file.name,
        "section": "Clause 3.1",
        "issue": "Jurisdiction clause does not specify ADGM",
        "severity": "High",
        "suggestion": "Update jurisdiction to ADGM Courts."
    }]

def insert_comments(docx_file, issues):
    doc = Document(docx_file)
    for issue in issues:
        for para in doc.paragraphs:
            if "jurisdiction" in para.text.lower():
                para.text += f" [COMMENT: {issue['suggestion']}]"
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, f"reviewed_{os.path.basename(docx_file.name)}")
    doc.save(output_path)
    return output_path

def process_documents(files):
    process, doc_types = identify_process_and_docs(files)
    missing = check_missing_docs(process, doc_types)
    all_issues = []
    reviewed_files = []
    for f in files:
        issues = analyze_doc(f)
        all_issues.extend(issues)
        reviewed_path = insert_comments(f, issues)
        reviewed_files.append(reviewed_path)
    summary = {
        "process": process,
        "documents_uploaded": len(doc_types),
        "required_documents": len(ADGM_CHECKLIST[process]),
        "missing_document": missing,
        "issues_found": all_issues
    }
    return reviewed_files, summary

# --- Streamlit UI ---
st.title("ADGM Corporate Agent")

uploaded_files = st.file_uploader("Upload .docx files", type=["docx"], accept_multiple_files=True)

if uploaded_files:
    reviewed_files, summary = process_documents(uploaded_files)
    st.subheader("Summary Report")
    st.json(summary)
    st.subheader("Download Reviewed Documents")
    for path in reviewed_files:
        with open(path, "rb") as f:
            st.download_button(
                label=f"Download {os.path.basename(path)}",
                data=f,
                file_name=os.path.basename(path),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
