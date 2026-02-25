import streamlit as st
import pandas as pd
import os
import importlib.util
import sys

# Dynamically import app.py from parent directory
APP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app.py'))
spec = importlib.util.spec_from_file_location("app", APP_PATH)
app_module = importlib.util.module_from_spec(spec)
sys.modules["app"] = app_module
spec.loader.exec_module(app_module)
main = app_module.main

DATA_INPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "input")

# ----------------------------
# Page Configuration
# ----------------------------
st.set_page_config(
    page_title="AI Resume Screening System",
    layout="wide"
)

# ----------------------------
# Header
# ----------------------------
st.title("📄 AI Resume Screening & Ranking System")
st.caption("Automated resume evaluation using NLP & AI")

# ----------------------------
# Sidebar – Inputs
# ----------------------------
st.sidebar.header("Screening Controls")

# 🔹 Job Description as SINGLE File Upload
job_description_file = st.sidebar.file_uploader(
    "Upload Job Description (PDF / TXT)",
    type=["pdf", "txt"],
    accept_multiple_files=False
)

threshold = st.sidebar.slider(
    "Minimum Qualification Score",
    min_value=0,
    max_value=100,
    value=65
)

uploaded_resumes = st.sidebar.file_uploader(
    "Upload Resumes (PDF / TXT)",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

run_button = st.sidebar.button("🚀 Run Resume Screening")

# ----------------------------
# Main Area – Output
# ----------------------------
if run_button:
    if not job_description_file or not uploaded_resumes:
        st.warning("Please upload a job description and at least one resume.")
    else:
        # Clean input folder before saving new uploads
        for f in os.listdir(DATA_INPUT_DIR):
            try:
                os.remove(os.path.join(DATA_INPUT_DIR, f))
            except Exception:
                pass
        # Save JD
        jd_ext = os.path.splitext(job_description_file.name)[1]
        jd_save_path = os.path.join(DATA_INPUT_DIR, f"jd{jd_ext}")
        with open(jd_save_path, "wb") as f:
            f.write(job_description_file.read())
        # Save resumes
        resume_paths = []
        resumes_to_save = uploaded_resumes
        if not isinstance(resumes_to_save, list):
            resumes_to_save = [resumes_to_save]
        for resume_file in resumes_to_save:
            resume_ext = os.path.splitext(resume_file.name)[1]
            resume_save_path = os.path.join(DATA_INPUT_DIR, resume_file.name)
            with open(resume_save_path, "wb") as f:
                f.write(resume_file.read())
            resume_paths.append(resume_save_path)
        st.info("Files uploaded. Running screening pipeline...")
        # Clean output folder before processing
        for f in os.listdir(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "output")):
            try:
                os.remove(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "output", f))
            except Exception:
                pass
        # Run the main pipeline with threshold
        results = main(threshold)
        if not results:
            st.error("No results returned. Check logs for errors.")
        else:
            df = pd.DataFrame(results)
            df["Rank"] = df["score"].rank(ascending=False).astype(int)
            df["Result"] = df["score"].apply(lambda x: "Pass" if x >= threshold else "Fail")
            st.subheader("📊 Candidate Ranking Dashboard")
            st.dataframe(
                df[["Rank", "filename", "score", "email_status", "Result"]].sort_values("Rank")
            )
            st.subheader("🔍 Candidate Detailed Stats & Recommendations")
            for idx, row in df.iterrows():
                with st.expander(f"{row['filename']} – Score: {row['score']} ({row['Result']})"):
                    st.markdown(f"**Email:** {row['email']}")
                    st.markdown(f"**Strengths:** {', '.join(row['recommendations'].get('strengths', []))}")
                    st.markdown(f"**Missing Skills:** {', '.join(row['recommendations'].get('missing_skills', []))}")
                    st.markdown(f"**Missing Tools:** {', '.join(row['recommendations'].get('missing_tools', []))}")
                    st.markdown(f"**Missing Keywords:** {', '.join(row['recommendations'].get('missing_keywords', []))}")
                    st.markdown(f"**Experience Gap:** {row['recommendations'].get('experience_gap', '')}")
                    st.markdown(f"**Overall Assessment:** {row['recommendations'].get('overall_assessment', '')}")
                    st.markdown("**Recommendations:**")
                    for rec in row['recommendations'].get('recommendations', []):
                        st.write(f"- {rec}")