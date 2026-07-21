# 🤖 HireSense AI — ATS Resume Screening & Candidate Ranking Engine

[![Python 3.11](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Groq Llama-3.3](https://img.shields.io/badge/AI-Groq_Llama_3.3_70B-f97316?style=for-the-badge&logo=openai&logoColor=white)](https://groq.com)
[![Scikit-Learn](https://img.shields.io/badge/NLP-TF--IDF_Scikit--Learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)](https://scikit-learn.org)
[![Localhost Server](https://img.shields.io/badge/Web_Server-http%3A%2F%2Flocalhost%3A5000-success?style=for-the-badge&logo=googlechrome&logoColor=white)](http://localhost:5000)

An intelligent **AI-Powered Resume Screening & Candidate Ranking Engine** that parses candidate resumes (PDF, DOCX, TXT), matches extracted technical skills and education qualifications against job description requirements, calculates weighted ATS scores using TF-IDF vectorization, generates AI recruiter insights, and serves interactive dashboards locally.

Built for the **Rooman Technologies — Junior AI Research Associate AI Agent Challenge**.

---

## 🚀 Step-by-Step Guide: How to Run the Project

### Step 1: Open Terminal in Project Directory
Navigate to the project root directory in your PowerShell or Command Prompt:
```bash
cd d:\HireSense_AI
```

### Step 2: Create & Activate Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows (PowerShell / CMD):
.venv\Scripts\activate

# Activate on Linux / macOS:
source .venv/bin/activate
```

### Step 3: Install Required Dependencies
Install all core application dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

### Step 4: Configure Environment Variables (`.env`)
Open the [.env](file:///d:/HireSense_AI/.env) file located in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```
> 💡 **Note**: If `GROQ_API_KEY` is not provided, HireSense AI automatically utilizes a built-in structured evaluation engine fallback so the project runs seamlessly without an API key.

---

### Step 5: Run Candidate Resume Screening
To execute the ATS scoring engine, rank all resumes in `resumes/` against `job_description/jd.txt`, and automatically open the report in your web browser:

```bash
python app.py
```

#### What happens when you run `python app.py`:
1. Parses the target Job Description (`job_description/jd.txt`).
2. Reads and extracts text from all candidate resumes in `resumes/` (`PDF`, `DOCX`, `TXT`).
3. Cleans and normalizes text using regular expressions.
4. Computes dynamic skill match ratios, TF-IDF cosine similarity, and education alignment.
5. Calculates weighted final ATS scores.
6. Generates AI recruiter summaries (Strengths, Weaknesses, Recommendations).
7. Renders an interactive leaderboard in your terminal.
8. Exports reports to `output/ranked.csv`, `output/ranked.json`, and `output/report.html`.
9. **Automatically launches `output/report.html` in Google Chrome / default browser**.

---

### Step 6: Host & View on Localhost (`http://localhost:5000`)
To host the interactive Candidate Screening Dashboard on a local web server:

```bash
python server.py
```

#### Features of `server.py`:
- Hosts the web dashboard live at: **`http://localhost:5000`**
- Automatically opens **`http://localhost:5000`** in your browser.
- **Dynamic Port Selection**: If port 5000 is occupied, it automatically tries 5001, 5002, 5003, etc., preventing socket address conflicts (`WinError 10048`).

---

### Step 7: Run Automated Unit Tests
To verify all scoring, parsing, and loading modules:
```bash
python -m unittest discover -s tests
```

---

## 🏗 System Architecture

```
                    Job Description File (jd.txt)
                                  │
                                  ▼
                   ┌──────────────────────────────┐
                   │   Job Description Parser     │
                   └──────────────┬───────────────┘
                                  │
                       Extracted Skills & Degree
                                  │
                                  ▼
┌──────────────────┐    ┌──────────────────────────┐
│  Candidate Files ├───►│   Multi-Format Parser    │
│ (PDF, DOCX, TXT) │    │(PyMuPDF / docx / cleaner)│
└──────────────────┘    └─────────┬────────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────────┐
                   │    ATS Scoring Engine        │
                   │  • 50% Skill Match           │
                   │  • 40% TF-IDF Similarity     │
                   │  • 10% Education Match       │
                   └──────────────┬───────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────────┐
                   │   AI Recruiter Evaluation    │
                   │  (Groq LLM / Robust Fallback)│
                   └──────────────┬───────────────┘
                                  │
                                  ▼
      ┌───────────────────────────┼───────────────────────────┐
      ▼                           ▼                           ▼
┌───────────┐               ┌───────────┐               ┌──────────────────────────┐
│  ranked.csv               │ranked.json│               │report.html (Localhost)   │
└───────────┘               └───────────┘               └──────────────────────────┘
```

---

## 📊 ATS Scoring Methodology

The candidate **Final ATS Score** is calculated deterministically:

$$\text{Final Score} = (\text{Skill Match Score} \times 0.50) + (\text{TF-IDF Similarity} \times 0.40) + (\text{Education Match} \times 0.10)$$

| Component | Weight | Calculation |
| :--- | :---: | :--- |
| **Skill Match** | **50%** | $\frac{\text{Matched Required Skills}}{\text{Total JD Required Skills}} \times 100$ |
| **TF-IDF Similarity** | **40%** | Cosine similarity between TF-IDF term-frequency vectors |
| **Education Match** | **10%** | $100\%$ if candidate holds required degree level, else $0\%$ |

### Recommendation Badges

- **🟢 Highly Recommended**: Final Score $\ge 85\%$
- **🔵 Recommended**: Final Score $\ge 70\%$
- **🟡 Consider**: Final Score $\ge 50\%$
- **🔴 Not Recommended**: Final Score $< 50\%$

---

## 📂 Project Structure

```
HireSense_AI/
│
├── app.py                  # Main CLI application & report generator
├── server.py               # Localhost web server script (http://localhost:5000)
├── config.py               # Environment & API configuration loader
├── requirements.txt        # Python dependencies
├── .env                    # Groq API key configuration
├── README.md               # Detailed project documentation
│
├── job_description/
│   └── jd.txt              # Target job description text
│
├── resumes/
│   └── *.pdf, *.docx, *.txt# Candidate resumes directory
│
├── sample_data/
│   └── skills.txt          # Technical skills taxonomy database
│
├── templates/
│   └── report_template.html# Dashboard HTML layout template
│
├── assets/
│   └── style.css           # Modern CSS dashboard stylesheet
│
├── utils/
│   ├── jd_parser.py        # Job description extraction & skill matching
│   ├── resume_parser.py    # Resume text structuring
│   ├── pdf_parser.py       # PDF, DOCX, and TXT parser
│   ├── text_cleaner.py     # Text cleaning & regex normalizer
│   ├── skills_loader.py    # Skill database cache manager
│   ├── scorer.py           # Weighted ATS scoring engine
│   ├── llm.py              # Groq AI summary generator with fallback
│   ├── exporter.py         # CSV, JSON, and HTML report generator
│   └── logger.py           # System logging module
│
├── tests/
│   ├── test_jd_parser.py   # Unit tests for JD parser
│   ├── test_resume_parser.py # Unit tests for resume parser
│   ├── test_scorer.py      # Unit tests for scoring engine
│   └── test_skills_loader.py # Unit tests for skills loader
│
└── output/
    ├── ranked.csv          # Exported candidate CSV dataset
    ├── ranked.json         # Exported candidate JSON payload
    └── report.html         # Generated web dashboard report
```

---

## 🏆 Challenge Metadata

- **Track**: Junior AI Research Associate AI Agent Challenge
- **Organization**: Rooman Technologies
- **System**: HireSense AI Engine
- **License**: MIT