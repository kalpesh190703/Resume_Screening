import streamlit as st
import pandas as pd

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
        st.success("Screening completed successfully!")

        # ----------------------------
        # Dummy Results (from backend)
        # ----------------------------
        results = [
            {
                "Candidate": "Parth Pandit",
                "Score": 82,
                "Email Status": "Qualified",
                "Missing Skills": []
            },
            {
                "Candidate": "Rohan Kumar",
                "Score": 58,
                "Email Status": "Email Sent",
                "Missing Skills": ["SQL", "NLP"]
            }
        ]
    #implement after the pipline app.py completed
    #    results = run_pipeline(
    #        job_description_file,
    #        uploaded_resumes,
    #        threshold
    #    )
        df = pd.DataFrame(results)
        df["Rank"] = df["Score"].rank(ascending=False).astype(int)

        # ----------------------------
        # Ranking Dashboard
        # ----------------------------
        st.subheader("📊 Candidate Ranking Dashboard")
        st.dataframe(
            df[["Rank", "Candidate", "Score", "Email Status"]]
            .sort_values("Rank")
        )

        # ----------------------------
        # Detailed Feedback
        # ----------------------------
        st.subheader("🛠 Resume Feedback")

        for row in results:
            with st.expander(f"{row['Candidate']} – Score: {row['Score']}"):
                if row["Score"] < threshold:
                    st.write("❌ **Below Threshold**")
                    st.write("**Missing Skills:**", ", ".join(row["Missing Skills"]))
                    st.write("**Suggestions:**")
                    st.write("- Add relevant projects")
                    st.write("- Include measurable achievements")
                else:
                    st.write("✅ **Qualified – No improvements needed**")