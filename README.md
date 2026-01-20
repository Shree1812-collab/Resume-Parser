# AI Resume Parser & Job Matcher

A Streamlit-based AI application that parses resumes (PDF/DOCX), extracts key candidate details, 
matches skills with predefined job roles, calculates ATS-style similarity scores, 
and suggests better-fit roles when similarity is low.

## Features
- Resume parsing (PDF & DOCX)
- Skill extraction
- Job-role based similarity matching
- Matched & missing skills display
- Intelligent job role suggestions
- Clean and interactive UI using Streamlit

## Tech Stack
- Python
- Streamlit
- spaCy
- PDFPlumber
- python-docx

## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py
