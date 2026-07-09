<h1 align="center">
  <br>
  🎯 HireSense AI
  <br>
</h1>

<h4 align="center">AI-Powered Resume Screening & Candidate Ranking System</h4>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#installation">Installation</a> •
  <a href="#api-documentation">API</a> •
  <a href="#scoring-formula">Scoring</a>
</p>

---

## ✨ Key Features

- **Smart Resume Parsing**: Parse PDF, DOCX, and TXT resumes
- **Structured Extraction**: Extract skills, experience, education, projects, and certifications using AI
- **Semantic Matching**: Use cosine similarity with Sentence Transformers and FAISS
- **ATS Scoring**: Calculate weighted ATS scores based on job requirements
- **Candidate Ranking**: Rank candidates by combined similarity and ATS scores
- **Interview Questions**: Generate tailored interview questions with difficulty levels
- **Skill Gap Analysis**: Identify missing skills in candidates
- **Professional Dashboard**: Modern, responsive recruiter UI
- **Export Options**: Download rankings as CSV or JSON

---

## 🏗️ Architecture

### High-Level Architecture Diagram
```
┌─────────────────┐
│  Streamlit UI   │
│  (Frontend)     │
└────────┬────────┘
         │
         ▼
┌───────────────────────────────┐
│     FastAPI Backend           │
│  ┌───────────────────────┐    │
│  │  HireSense Orchestration│ │
│  └───────────┬───────────┘    │
└──────────────┼────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌──────────────┐  ┌──────────────────┐
│   Services   │  │  LangChain + AI │
├──────────────┤  ├──────────────────┤
│- Parser      │  │- Groq LLM        │
│- Extraction  │  │- Prompt Templates│
│- Embedding   │  └──────────────────┘
│- ATS Scoring │
│- Ranking     │
└──────────────┘
      │
      ▼
┌──────────────┐
│  FAISS Index │
│ (Vector DB)  │
└──────────────┘
```

### Folder Structure
```
HireSense_AI/
├── ai/                                  # AI Components
│   ├── chains/
│   │   ├── extraction_chains.py        # LangChain extraction chains
│   │   └── __init__.py
│   ├── prompts/
│   │   ├── extraction_prompts.py       # Prompt templates
│   │   └── __init__.py
│   └── __init__.py
│
├── backend/                              # FastAPI Backend
│   ├── api/
│   │   └── v1/
│   │       ├── ats.py                   # ATS scoring endpoints
│   │       ├── embeddings.py            # Embedding & vector endpoints
│   │       ├── hiresense.py             # Unified endpoints
│   │       ├── interview_questions.py   # Interview question generator
│   │       ├── job.py                   # Job description endpoints
│   │       ├── ranking.py               # Candidate ranking endpoints
│   │       ├── resume.py                # Resume endpoints
│   │       ├── similarity.py            # Similarity endpoints
│   │       └── __init__.py
│   ├── core/
│   │   ├── config.py                    # Configuration
│   │   ├── logging.py                   # Logging setup
│   │   └── __init__.py
│   ├── models/
│   │   ├── schemas.py                   # Pydantic schemas
│   │   └── __init__.py
│   ├── services/
│   │   ├── ats_scoring.py               # ATS scoring service
│   │   ├── candidate_ranking.py         # Ranking service
│   │   ├── embedding_service.py         # Embedding service
│   │   ├── extraction_service.py        # Structured extraction service
│   │   ├── hiresense_orchestration.py   # Orchestration service
│   │   ├── interview_question_generator.py # Interview Q service
│   │   ├── resume_parser.py             # Resume parser service
│   │   ├── similarity_engine.py         # Similarity engine
│   │   ├── vector_store.py              # FAISS vector store
│   │   └── __init__.py
│   ├── utils/
│   │   ├── embedding_utils.py           # Embedding utilities
│   │   ├── parser.py                    # Parser utilities
│   │   ├── similarity_utils.py          # Similarity utilities
│   │   └── __init__.py
│   ├── main.py                          # FastAPI entry point
│   └── __init__.py
│
├── frontend/                             # Streamlit Frontend
│   ├── components/
│   ├── utils/
│   ├── app.py                           # Main app
│   └── __init__.py
│
├── data/                                 # Data storage
│   ├── faiss_index/
│   ├── job_descriptions/
│   ├── resumes/
│   └── temp/
│
├── .env.example                          # Environment variables template
├── .gitignore
├── requirements.txt                      # Dependencies
└── README.md                             # This file
```

---

## ⚙️ Installation

### Requirements
- Python 3.10 or higher
- pip
- A Groq API key (free tier available)

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd HireSense_AI
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/MacOS:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Add your Groq API key to `.env`
   ```bash
   cp .env.example .env
   # Edit .env and set your GROQ_API_KEY
   ```

---

## 🔧 Environment Variables

Create a `.env` file in the root directory with these variables:

```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Optional: Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

## 🚀 Usage

### 1. Start the Backend Server
```bash
python -m backend.main
```
The FastAPI backend will start at: http://localhost:8000

API Documentation (Swagger UI): http://localhost:8000/docs

### 2. Start the Frontend Dashboard
In a new terminal:
```bash
streamlit run frontend/app.py
```
The Streamlit dashboard will open at: http://localhost:8501

---

## 📋 API Documentation

### Main Endpoints (`/api/v1/hiresense`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload-jd` | Upload and parse a job description |
| `POST` | `/upload-resume` | Upload and parse a single resume |
| `POST` | `/upload-resumes` | Upload and parse multiple resumes |
| `POST` | `/rank/{jd_id}` | Rank candidates for a job description |
| `GET` | `/summary/{jd_id}` | Get job description summary |
| `GET` | `/candidate/{resume_id}` | Get candidate details |
| `POST` | `/download-csv/{jd_id}` | Download rankings as CSV |
| `POST` | `/download-json/{jd_id}` | Download rankings as JSON |

### Individual Endpoints
| Group | Endpoint | Description |
|-------|----------|-------------|
| Resumes | `/api/v1/resume/*` | Resume upload/parsing/extraction |
| Job Descriptions | `/api/v1/job/*` | JD upload/parsing/extraction |
| Embeddings | `/api/v1/embeddings/*` | Embedding generation and storage |
| Similarity | `/api/v1/similarity/*` | Cosine similarity calculations |
| ATS Scoring | `/api/v1/ats/*` | ATS score calculation |
| Ranking | `/api/v1/ranking/*` | Candidate ranking |
| Interview Questions | `/api/v1/interview-questions/*` | Question generation |

Full API docs available at http://localhost:8000/docs when the backend is running.

---

## 📊 Scoring Formula

### Overall ATS Score
The total ATS score is calculated using the weighted average of these components:

| Component | Weight | Description |
|-----------|--------|-------------|
| Skill Match | 40% | Match against required and preferred skills |
| Experience | 25% | Relevant work experience |
| Education | 15% | Education background match |
| Project Match | 10% | Relevant projects |
| Certifications | 10% | Relevant certifications |

```
Total ATS Score =
    (Skill_Match * 0.40) +
    (Experience * 0.25) +
    (Education * 0.15) +
    (Project_Match * 0.10) +
    (Certifications * 0.10)
```

### Combined Ranking Score
The final combined score (used for ranking) is a weighted average of:
- ATS Score (default weight: 0.6)
- Semantic Similarity Score (default weight: 0.4)

Weights are configurable in the ranking endpoint!

```
Combined_Score =
    (ATS_Score * ats_weight) +
    (Similarity_Score * similarity_weight)
```

---

## 📈 Screenshots

### Dashboard
![Dashboard](https://coresg-normal.trae.ai/api/ide/v1/text_to_image?prompt=professional%20recruiter%20dashboard%20with%20stat%20cards%20and%20gradient%20design&image_size=square)

### Candidate Ranking
![Candidate Ranking](https://coresg-normal.trae.ai/api/ide/v1/text_to_image?prompt=candidate%20ranking%20page%20with%20scores%20and%20top%20candidate%20highlighted&image_size=square)

### Candidate Details
![Candidate Details](https://coresg-normal.trae.ai/api/ide/v1/text_to_image?prompt=candidate%20profile%20page%20with%20interview%20questions&image_size=square)

---

## 🚀 Future Improvements

- [ ] Persistent database (PostgreSQL/MongoDB) instead of in-memory
- [ ] User authentication & multi-user support
- [ ] Cloud deployment (AWS/GCP/Azure)
- [ ] Batch processing for large number of resumes
- [ ] Customizable scoring weights via UI
- [ ] Email notifications
- [ ] Integration with ATS platforms (Greenhouse, Lever, etc.)
- [ ] Interview scheduling integration
- [ ] Historical hiring data analytics
- [ ] Custom prompt templates
- [ ] Multi-language support

---

## 📜 License

This project is open source and available for educational and personal use.

---

## 🤝 Contributing

Feel free to fork this repository and make improvements! Pull requests are welcome.

---

## 🙏 Acknowledgments

- **Groq**: For providing the LLM API
- **Sentence Transformers**: For embeddings
- **FAISS**: For vector storage
- **LangChain**: For AI orchestration
- **Streamlit**: For the dashboard framework
- **FastAPI**: For the backend framework

---

<p align="center">
  Made with ❤️ for Junior AI Research Associate Challenge
</p>
