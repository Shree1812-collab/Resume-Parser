import streamlit as st
import pdfplumber
import docx
import re
import spacy

# ---------------- CACHE NLP MODEL ----------------
@st.cache_resource
def load_nlp():
    return spacy.load("en_core_web_sm")

nlp = load_nlp()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Resume Parser & Job Matcher",
    page_icon="📄",
    layout="centered"
)

# ---------------- STYLES ----------------
st.markdown("""
<style>
.card {
    padding:20px;
    border-radius:10px;
    background:#f9f9f9;
    box-shadow:2px 2px 10px #ddd;
    margin-bottom:20px;
}
</style>
""", unsafe_allow_html=True)

st.title("📄 AI Resume Parser & Job Matcher")

# ---------------- JOB ROLE → SKILLS MAP ----------------
job_skill_map = {
    "python developer": [
        "python", "django", "flask", "sql"
    ],
    "data analyst": [
        "python", "sql", "data science", "machine learning"
    ],
    "mern stack developer": [
        "mongodb", "express", "react", "node",
        "javascript", "html", "css"
    ],
    "machine learning engineer": [
        "python", "machine learning", "data science"
    ],
    "cloud engineer": [
        "aws", "cloud", "linux", "docker", "devops"
    ]
}

# ---------------- FUNCTIONS ----------------
def extract_text(file):
    if file.name.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join(p.text for p in doc.paragraphs)

def extract_details(text):
    email = re.findall(r"\S+@\S+", text)
    phone = re.findall(r"\+?\d[\d -]{8,12}\d", text)

    skills_db = [
        "python","java","c","c++","javascript","html","css","sql",
        "machine learning","data science","django","flask",
        "react","node","mongodb","aws","cloud","git","excel"
    ]

    # normalize + remove duplicates
    skills = list(set(s for s in skills_db if s in text.lower()))
    skills.sort()  # alphabetically sort skills

    name = "Not Found"
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break

    return name, email, phone, skills

def skill_match_percentage(resume_skills, required_skills):
    if not required_skills:
        return 0.0
    matched = set(resume_skills).intersection(set(required_skills))
    return (len(matched) / len(required_skills)) * 100

# ---------------- UI INPUTS ----------------
resume_file = st.file_uploader(
    "Upload Resume (PDF or DOCX)",
    type=["pdf", "docx"]
)

job_title = st.selectbox(
    "Select Job Role",
    list(job_skill_map.keys())
)

# ---------------- MAIN LOGIC ----------------
if resume_file:
    resume_text = extract_text(resume_file)
    name, email, phone, skills = extract_details(resume_text)

    required_skills = job_skill_map[job_title]
    score = skill_match_percentage(skills, required_skills)

    matched = set(skills).intersection(set(required_skills))
    missing = set(required_skills) - set(skills)

    # -------- Candidate Details --------
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("👤 Candidate Details")
    st.write("**Name:**", name)
    st.write("**Email:**", email[0] if email else "Not Found")
    st.write("**Phone:**", phone[0] if phone else "Not Found")
    st.write("**Skills:**", ", ".join(skills) if skills else "Not Found")
    st.markdown("</div>", unsafe_allow_html=True)

    # -------- Similarity Result --------
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader(f"📊 Similarity with {job_title.title()}")
    st.progress(int(score))
    st.markdown(f"### 🔥 Similarity Score: **{score:.2f}%**")

    # -------- COLOR INDICATOR --------
    if score >= 70:
        st.success("Excellent Match")
    elif score >= 50:
        st.warning("Good Match")
    else:
        st.error("Low Match")

    st.write("✅ **Matched Skills:**", ", ".join(matched) if matched else "None")
    st.write("❌ **Missing Skills:**", ", ".join(missing) if missing else "None")
    st.markdown("</div>", unsafe_allow_html=True)

    # -------- JOB SUGGESTIONS --------
    if score < 50:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("💡 Suggested Job Roles (Better Fit)")

        suggestions_found = False
        for role, role_skills in job_skill_map.items():
            if role != job_title:
                s = skill_match_percentage(skills, role_skills)
                if s >= 40:
                    st.write(f"✔ **{role.title()}** — {s:.2f}% match")
                    suggestions_found = True

        if not suggestions_found:
            st.info("No strong alternative roles found. Consider improving skills.")

        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("⬆ Upload resume to continue")
