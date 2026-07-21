# 🤖 AI Resume Screening Agent — HireSense AI

An AI-assisted Resume Screening and Ranking System that automatically screens, scores, and ranks multiple resumes against a Job Description using Natural Language Processing (NLP), skill matching, weighted scoring, and Large Language Model (LLM) reasoning.

Built for the **Rooman Technologies – Junior AI Research Associate AI Agent Challenge**.

---

## 🚀 Project Overview

Recruiters often receive hundreds of resumes for a single job opening. Manually reviewing every resume is slow, repetitive, and inconsistent.

This project automates the initial screening process by:

- **Parsing resumes** (PDF, DOCX, TXT)
- **Parsing job descriptions**
- **Extracting technical skills**
- **Computing semantic similarity using TF-IDF**
- **Matching candidate skills against job requirements**
- **Calculating weighted ATS scores**
- **Generating AI-powered recruiter summaries**
- **Ranking all candidates automatically**
- **Exporting professional reports**

The objective is not to replace recruiters, but to help them shortlist candidates faster and more consistently.

---

## ✨ Features

### Resume Processing
- ✅ PDF Resume Parsing
- ✅ DOCX Resume Parsing
- ✅ TXT Resume Parsing
- ✅ Automatic Text Cleaning

### Job Description Processing
- ✅ Job Description Parsing
- ✅ Dynamic Skill Extraction
- ✅ Education Detection
- ✅ Keyword Matching

### ATS Scoring Engine
- ✅ TF-IDF Semantic Similarity
- ✅ Dynamic Skill Matching
- ✅ Education Score Alignment
- ✅ Weighted Final ATS Score
- ✅ Candidate Leaderboard Ranking

### AI Features
- ✅ AI-generated Candidate Summary
- ✅ Strengths Identification
- ✅ Weakness Detection
- ✅ Hiring Recommendation
*(Powered by Groq Llama 3.3 70B)*

### Reports
- ✅ CSV Export (`output/ranked.csv`)
- ✅ JSON Export (`output/ranked.json`)
- ✅ PDF Summary Export (`output/ranked_summary.pdf`)
- ✅ Interactive HTML Report (`output/report.html`)

### Engineering Features
- ✅ Modular Project Structure
- ✅ Automated Logging
- ✅ Dynamic Skills Database
- ✅ Automated Unit Tests
- ✅ Localhost Web Dashboard Server (`server.py`)
- ✅ Git Version Control

---

## 🏗 System Architecture

```
                     Job Description
                            │
                            ▼
                   Job Description Parser
                            │
                            ▼
                  Dynamic Skill Extraction
                            │
                            ▼
                     Resume Parser
                            │
                            ▼
                  Text Normalization
                            │
                            ▼
               TF-IDF Similarity Engine
                            │
                            ▼
                  Skill Matching Engine
                            │
                            ▼
                Weighted ATS Score Engine
                            │
                            ▼
              AI Candidate Evaluation
                            │
                            ▼
               Ranked Candidate Reports
```

---

## 📂 Project Structure

```
HireSense_AI/
│
├── app.py                  # Main screening engine & CLI launcher
├── server.py               # Localhost web server (http://localhost:5000)
├── config.py               # Environment configuration loader
├── requirements.txt        # Core dependencies
├── README.md               # Documentation
├── .gitignore
├── pytest.ini
│
├── job_description/
│   └── jd.txt              # Target job description input
│
├── resumes/
│   ├── *.pdf
│   ├── *.docx
│   └── *.txt               # Candidate resumes folder
│
├── output/
│   ├── ranked.csv          # Candidate dataset CSV export
│   ├── ranked.json         # Candidate evaluation JSON export
│   ├── ranked_summary.pdf  # Candidate ranking PDF summary
│   └── report.html         # Interactive recruiter HTML dashboard
│
├── sample_data/
│   └── skills.txt          # Technical skill database taxonomy
│
├── templates/
│   └── report_template.html# Dashboard HTML template
│
├── assets/
│   ├── style.css           # Dashboard stylesheet
│   └── *.png               # Screenshot assets
│
├── tests/
│   ├── test_jd_parser.py
│   ├── test_resume_parser.py
│   ├── test_scorer.py
│   └── test_skills_loader.py
│
└── utils/
    ├── __init__.py
    ├── exporter.py         # CSV, JSON, PDF, HTML exporters
    ├── jd_parser.py        # Job description parser
    ├── llm.py              # Groq AI evaluator & fallback
    ├── logger.py           # Logging module
    ├── pdf_parser.py       # Multi-format PDF/DOCX/TXT text extractor
    ├── resume_parser.py    # Resume parser
    ├── scorer.py           # ATS weighted scoring engine
    ├── skills_loader.py    # Skill database cache manager
    └── text_cleaner.py     # RegEx text normalizer
```

---

## 🛠 Tech Stack

| Category | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **AI** | Groq Llama 3.3 70B |
| **NLP** | TF-IDF Vectorization |
| **ML / Math** | Scikit-Learn |
| **PDF Generation** | ReportLab |
| **PDF Parsing** | PyMuPDF (`fitz`) |
| **DOCX Parsing** | `python-docx` |
| **Data Handling** | Pandas |
| **CLI Styling** | Rich |
| **Testing** | Unittest / Pytest |

---

## ⚙ Installation

### 1. Clone the repository
```bash
git clone https://github.com/Ishaq7892/Rooman_HireSense-AI.git
cd HireSense_AI
```

### 2. Create virtual environment
```bash
python -m venv .venv
```

### 3. Activate virtual environment
- **Windows (PowerShell / CMD)**:
  ```bash
  .venv\Scripts\activate
  ```
- **Linux / macOS**:
  ```bash
  source .venv/bin/activate
  ```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🔑 Configuration

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

> 💡 *Note: If `GROQ_API_KEY` is omitted, the engine automatically uses a built-in structured evaluation engine fallback so all evaluations execute seamlessly.*

---

## ▶ Running

### Step 1: Run Candidate Screening
```bash
python app.py
```
The application will:
1. Parse the Job Description (`job_description/jd.txt`)
2. Parse every resume in `resumes/`
3. Clean and normalize text
4. Extract required skills
5. Compute TF-IDF similarity
6. Match candidate skills
7. Calculate weighted ATS scores
8. Generate AI explanations & recommendations
9. Rank all candidates automatically
10. Export reports to `output/` and open `output/report.html` in your default browser

### Step 2: Host Localhost Web Server
```bash
python server.py
```
Hosts the interactive dashboard live at **`http://localhost:5000`**.

---

## 🧪 Running Tests

Run unit tests using unittest or pytest:

```bash
python -m unittest discover -s tests
```
or
```bash
pytest
```

---

## 📊 Scoring Methodology

The ATS score combines three weighted components:

| Component | Weight | Description |
| :--- | :---: | :--- |
| **Skill Match** | **50%** | Ratio of matched candidate skills against required JD skills |
| **TF-IDF Similarity** | **40%** | Cosine similarity between resume text and job description term vectors |
| **Education Match** | **10%** | Degree qualification match score |

The weighted score determines the final candidate ranking and recommendation status:
- 🟢 **Highly Recommended**: Score $\ge 85\%$
- 🔵 **Recommended**: Score $\ge 70\%$
- 🟡 **Consider**: Score $\ge 50\%$
- 🔴 **Not Recommended**: Score $< 50\%$

---

## 📤 Output

The application generates:

```
output/
│
├── ranked.csv
├── ranked.json
├── ranked_summary.pdf
└── report.html
```

The terminal displays:
- Candidate Rank
- Final ATS Score
- TF-IDF Match % | Skill Match % | Education Match %
- Matched Skills
- Missing Skills
- AI Evaluation (Strengths, Weaknesses, Recommendation)

---

## 🧠 AI Integration

This project integrates the Groq API using the **Llama 3.3 70B** model.

The LLM is not responsible for raw score calculation, ensuring that ATS scoring remains deterministic while using AI for explainability.

It provides human-readable explanations including:
- Candidate strengths
- Candidate weaknesses
- Hiring recommendation

---

## 📈 Future Improvements

- [ ] Interactive Recruiter Dashboard UI
- [ ] Resume Upload Web Drag & Drop
- [ ] Sentence Transformer Embeddings
- [ ] Semantic Skill Matching
- [ ] Experience Timeline Analysis
- [ ] Recruiter Feedback Loop
- [ ] GitHub Actions CI/CD Pipeline
- [ ] Docker Support

---

## 📸 Screenshots

### HTML Report
![HTML Report](assets/html_report.png)

### Candidate Ranking
![Candidate Ranking](assets/rankings.png)

### Project Folder
![Project Folder](assets/project_structure.png)

### GitHub Repository
![GitHub Repository](assets/GitHub-Account.png)

### Terminal Output
![Terminal Output 1](assets/terminal_output1.png)
![Terminal Output 2](assets/terminal_output2.png)

### Unit Tests
![Unit Tests](assets/Test.png)

---

## ⚠️ Known Limitations

- Uses TF-IDF for term-frequency matching alongside technical skill extraction.
- Skill matching relies on taxonomy term extraction.
- Job descriptions are parsed using rule-based extraction.

---

## 👨‍💻 Author

**Ishaq Gaima**  
*HireSense AI — AI Resume Screening Agent*  
Built for the **Rooman Technologies – Junior AI Research Associate AI Agent Challenge**.

---

## ⭐ Acknowledgements

This project was developed to demonstrate practical skills in:
- Artificial Intelligence & LLM Integration
- Natural Language Processing (NLP)
- Python Software Engineering
- Resume Screening Automation & ATS Engines
- Prompt Engineering & Fallback Systems
- Software Testing & Modular Architecture
