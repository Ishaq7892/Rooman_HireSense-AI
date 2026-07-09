import streamlit as st
import requests
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"

# Page config
st.set_page_config(
    page_title="HireSense AI - Recruiter Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    /* Main styles */
    .main {
        background-color: #f8fafc;
    }
    
    /* Header */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
    }
    
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
    }
    
    /* Cards */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #667eea;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    .stat-label {
        color: #64748b;
        font-size: 0.95rem;
        margin-top: 0.25rem;
    }
    
    /* Progress bars */
    .progress-bar {
        height: 8px;
        background: #e2e8f0;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    /* Candidate card */
    .candidate-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
    }
    
    .candidate-card:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        border-color: #667eea;
    }
    
    /* Skill tags */
    .skill-tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .skill-tag.present {
        background-color: #dcfce7;
        color: #166534;
    }
    
    .skill-tag.missing {
        background-color: #fee2e2;
        color: #991b1b;
    }
    
    /* Sidebar */
    .sidebar-nav {
        padding: 1rem 0;
    }
    
    .nav-item {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.25rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .nav-item:hover {
        background-color: #f1f5f9;
    }
    
    .nav-item.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Buttons */
    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        border: 1px solid #e2e8f0;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-color: transparent;
    }
    
    /* File upload area */
    .upload-container {
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background-color: white;
        transition: all 0.2s ease;
    }
    
    .upload-container:hover {
        border-color: #667eea;
        background-color: #f0f4ff;
    }
    
    /* Interview question card */
    .question-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'jd_id' not in st.session_state:
    st.session_state.jd_id = None
if 'resume_ids' not in st.session_state:  # Store actual resume IDs instead of numbers
    st.session_state.resume_ids = []
if 'ranking' not in st.session_state:
    st.session_state.ranking = None
if 'selected_candidate' not in st.session_state:
    st.session_state.selected_candidate = None
if 'page' not in st.session_state:
    st.session_state.page = "dashboard"
if 'resumes_processed' not in st.session_state:
    st.session_state.resumes_processed = False
if 'last_processed_count' not in st.session_state:
    st.session_state.last_processed_count = 0


def make_api_request(method, endpoint, files=None, json=None, params=None):
    """Helper function to make API requests"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, params=params)
            else:
                response = requests.post(url, json=json, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None


# Sidebar navigation
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       font-size: 1.75rem;">
                🎯 HireSense AI
            </h2>
            <p style="color: #64748b;">Recruiter Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
    
    # Navigation items
    nav_items = [
        ("dashboard", "📊 Dashboard"),
        ("upload_jd", "📝 Upload JD"),
        ("upload_resume", "📄 Upload Resumes"),
        ("ranking", "🏆 Candidate Ranking"),
        ("candidate", "👤 Candidate Details"),
        ("skill_gap", "🔍 Skill Gap"),
        ("summary", "📈 Recruiter Summary"),
        ("downloads", "💾 Downloads")
    ]
    
    for page_id, page_label in nav_items:
        if st.button(page_label, key=f"nav_{page_id}", use_container_width=True):
            st.session_state.page = page_id
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.jd_id:
        st.divider()
        st.info(f"Active Job ID: {st.session_state.jd_id}")


# Main content
page = st.session_state.page

# --- DASHBOARD PAGE ---
if page == "dashboard":
    st.markdown("""
        <div class="header-container">
            <div class="header-title">Welcome back, Recruiter!</div>
            <div class="header-subtitle">Manage your hiring process and find the perfect candidates</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    stats = [
        {
            "value": len(st.session_state.candidates) if st.session_state.jd_id else 0,
            "label": "Total Candidates",
            "icon": "👥"
        },
        {
            "value": "1" if st.session_state.jd_id else "0",
            "label": "Active Job Posts",
            "icon": "💼"
        },
        {
            "value": "7" if st.session_state.ranking else "0",
            "label": "Avg ATS Score",
            "icon": "📊"
        },
        {
            "value": "3" if st.session_state.ranking and len(st.session_state.ranking['ranked_candidates']) > 2 else "0",
            "label": "Top Picks",
            "icon": "⭐"
        }
    ]
    
    for idx, stat in enumerate(stats):
        with [col1, col2, col3, col4][idx]:
            st.markdown(f"""
                <div class="stat-card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{stat['icon']}</div>
                    <div class="stat-value">{stat['value']}</div>
                    <div class="stat-label">{stat['label']}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Upload Job Description", use_container_width=True):
            st.session_state.page = "upload_jd"
            st.rerun()
    with col2:
        if st.button("📄 Upload Resumes", use_container_width=True, disabled=not st.session_state.jd_id):
            st.session_state.page = "upload_resume"
            st.rerun()
    with col3:
        if st.button("🏆 View Rankings", use_container_width=True, disabled=not st.session_state.jd_id):
            st.session_state.page = "ranking"
            st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Recent activity
    st.subheader("📋 Quick Guide")
    st.info("""
        1. **Upload Job Description**: Start by uploading your job description
        2. **Upload Resumes**: Add resumes you want to evaluate
        3. **View Rankings**: See how candidates match against the job
        4. **Download Results**: Export your rankings as CSV or JSON
    """)

# --- UPLOAD JD PAGE ---
elif page == "upload_jd":
    st.markdown("""
        <div class="header-container">
            <div class="header-title">Upload Job Description</div>
            <div class="header-subtitle">Upload your job description to start matching candidates</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📝 Upload Job Description")
    
    uploaded_file = st.file_uploader(
        "Upload your job description (PDF, DOCX, TXT)",
        type=['pdf', 'docx', 'txt'],
        key="jd_uploader"
    )
    
    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")
        
        if st.button("Process Job Description", type="primary"):
            with st.spinner("Processing..."):
                try:
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    result = make_api_request("POST", "/hiresense/upload-jd", files=files)
                    if result:
                        st.session_state.jd_id = result['jd_id']
                        st.success(f"Job Description processed! ID: {result['jd_id']}")
                        st.balloons()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# --- UPLOAD RESUMES PAGE ---
elif page == "upload_resume":
    st.markdown("""
        <div class="header-container">
            <div class="header-title">Upload Resumes</div>
            <div class="header-subtitle">Upload candidate resumes to evaluate</div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.jd_id:
        st.warning("Please upload a job description first!")
        if st.button("Upload Job Description"):
            st.session_state.page = "upload_jd"
            st.rerun()
    else:
        uploaded_files = st.file_uploader(
            "Upload candidate resumes (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            key="resume_uploader"
        )

        if uploaded_files:
            st.success(f"{len(uploaded_files)} file(s) uploaded!")

            if st.button("Process Resumes", type="primary"):
                with st.spinner("Processing..."):
                    success_count = 0
                    for uploaded_file in uploaded_files:
                        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        result = make_api_request(
                            "POST",
                            "/hiresense/upload-resume",
                            files=files,
                            params={"jd_id": st.session_state.jd_id}
                        )
                        if result:
                            success_count +=1
                            st.session_state.resume_ids.append(result['resume_id'])  # Store actual resume ID

                    st.session_state.resumes_processed = True
                    st.session_state.last_processed_count = success_count
                    st.rerun()

            if st.session_state.resumes_processed:
                st.success(f"Successfully processed {st.session_state.last_processed_count} resume(s)!")
                if st.button("View Rankings", type="primary"):
                    st.session_state.page = "ranking"
                    st.session_state.resumes_processed = False
                    st.rerun()

    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# --- RANKING PAGE ---
elif page == "ranking":
    st.markdown("""
        <div class="header-container">
            <div class="header-title">Candidate Ranking</div>
            <div class="header-subtitle">See how candidates match against your job requirements</div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.jd_id:
        st.warning("Please upload a job description first!")
        if st.button("Upload Job Description"):
            st.session_state.page = "upload_jd"
            st.rerun()
    else:
        if st.button("Generate Rankings", type="primary"):
            with st.spinner("Generating rankings..."):
                ranking = make_api_request(
                    "POST",
                    f"/hiresense/rank/{st.session_state.jd_id}"
                )
                if ranking:
                    st.session_state.ranking = ranking
                    st.success("Rankings generated!")

        if st.session_state.ranking:
            ranking = st.session_state.ranking
            # Top candidate
            if ranking['top_candidate']:
                top_candidate = ranking['top_candidate']
                st.markdown(f"""
                    <div class="candidate-card" style="border-color: #fbbf24; border-width: 3px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <div style="display: flex; align-items: center; gap: 1rem;">
                                <div style="font-size: 3rem;">🏆</div>
                                <div>
                                    <h3 style="margin: 0;">#1 - {top_candidate['candidate_name'] or 'Candidate'}</h3>
                                    <p style="margin: 0; color: #64748b;">Top Candidate</p>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 2rem; font-weight: 700; color: #16a34a;">
                                    {top_candidate['combined_score']:.1f}/100
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

            st.subheader("All Candidates")

            for idx, candidate in enumerate(ranking['ranked_candidates']):
                rank = candidate['rank']
                score = candidate['combined_score']
                score_color = "#16a34a" if score >= 70 else "#f59e0b" if score >=50 else "#dc2626"

                col1, col2 = st.columns([3,1])
                with col1:
                    st.markdown(f"""
                        <div class="candidate-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <h4 style="margin:0; display: flex; align-items: center; gap: 0.5rem;">
                                        #{rank} - {candidate['candidate_name'] or 'Candidate'}
                                    </h4>
                                    <p style="color: #64748b; margin: 0.25rem 0;">
                                        ATS: {candidate['ats_score']:.1f} | Similarity: {candidate['similarity_score']:.1f}
                                    </p>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 1.5rem; font-weight: 700; color: {score_color};">
                                        {score:.1f}
                                    </div>
                                    <div class="progress-bar" style="margin-top: 0.5rem; width: 120px;">
                                        <div class="progress-fill" style="width: {score}%; background-color: {score_color};"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    if st.button(f"View Details - {candidate['candidate_name'] or 'Candidate'}", key=f"view_{candidate['document_id']}"):
                        st.session_state.selected_candidate = candidate
                        st.session_state.page = "candidate"
                        st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# --- CANDIDATE DETAILS PAGE ---
elif page == "candidate":
    st.markdown("""
        <div class="header-container">
            <div class="header-title">Candidate Details</div>
            <div class="header-subtitle">Review candidate profile and interview questions</div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.selected_candidate:
        st.warning("Please select a candidate from the ranking page!")
        if st.button("View Rankings"):
            st.session_state.page = "ranking"
            st.rerun()
    else:
        candidate_ranked = st.session_state.selected_candidate
        # Call backend API to get full candidate details
        candidate_details = make_api_request(
            "GET",
            f"/hiresense/candidate/{candidate_ranked['document_id']}",
            params={"jd_id": st.session_state.jd_id}
        )
        
        if candidate_details:
            st.markdown(f"""
                <div class="candidate-card">
                    <h2 style="margin:0;">👤 {candidate_details.get('name', 'Candidate')}</h2>
                    <p style="margin:0.25rem 0 1rem; color:#64748b;">Document ID: {candidate_ranked['document_id']}</p>
                    <div style="display:flex; gap:2rem; margin-bottom:1.5rem;">
                        <div>
                            <p style="font-weight:600; margin:0;">ATS Score</p>
                            <p style="font-size:1.5rem; margin:0;">{candidate_ranked['ats_score']:.1f}</p>
                        </div>
                        <div>
                            <p style="font-weight:600; margin:0;">Similarity</p>
                            <p style="font-size:1.5rem; margin:0;">{candidate_ranked['similarity_score']:.1f}</p>
                        </div>
                        <div>
                            <p style="font-weight:600; margin:0;">Combined</p>
                            <p style="font-size:1.5rem; margin:0;">{candidate_ranked['combined_score']:.1f}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Candidate info columns
            col1, col2 = st.columns([1,1])
            
            with col1:
                st.markdown("#### 📧 Contact")
                st.markdown(f"**Email:** {candidate_details.get('email', 'N/A')}")
                st.markdown(f"**Phone:** {candidate_details.get('phone', 'N/A')}")
                
                st.markdown("#### 🔧 Skills")
                if candidate_details.get('skills'):
                    for skill in candidate_details['skills']:
                        st.markdown(f'<span class="skill-tag present" style="margin-right:0.5rem; margin-bottom:0.5rem; display:inline-block;">{skill}</span>', unsafe_allow_html=True)
                else:
                    st.info("No skills listed")
            
            with col2:
                st.markdown("#### 💪 Strengths")
                if candidate_ranked.get('strengths'):
                    for strength in candidate_ranked['strengths']:
                        st.markdown(f"- {strength}")
                else:
                    st.info("No strengths listed")

                st.markdown("#### ⚠️ Areas for Improvement")
                if candidate_ranked.get('weaknesses'):
                    for weakness in candidate_ranked['weaknesses']:
                        st.markdown(f"- {weakness}")
                else:
                    st.info("No weaknesses listed")

            st.markdown("<br>", unsafe_allow_html=True)
            
            # Experience, Education, Projects
            tab1, tab2, tab3 = st.tabs(["Experience", "Education", "Projects"])
            
            with tab1:
                if candidate_details.get('experience'):
                    for exp in candidate_details['experience']:
                        st.markdown(f"**{exp.get('job_title', 'N/A')}** at {exp.get('company', 'N/A')}")
                        if exp.get('location'):
                            st.markdown(f"📍 {exp.get('location')}")
                        if exp.get('description'):
                            st.markdown(f"- {exp.get('description')}")
                        st.divider()
                else:
                    st.info("No experience listed")
            
            with tab2:
                if candidate_details.get('education'):
                    for edu in candidate_details['education']:
                        st.markdown(f"**{edu.get('degree', 'N/A')}** at {edu.get('school', 'N/A')}")
                        if edu.get('description'):
                            st.markdown(f"- {edu.get('description')}")
                        st.divider()
                else:
                    st.info("No education listed")
            
            with tab3:
                if candidate_details.get('projects'):
                    for proj in candidate_details['projects']:
                        st.markdown(f"**{proj.get('title', 'N/A')}**")
                        if proj.get('description'):
                            st.markdown(f"- {proj.get('description')}")
                        if proj.get('technologies'):
                            st.markdown(f"🔧 Tech: {', '.join(proj.get('technologies', []))}")
                        st.divider()
                else:
                    st.info("No projects listed")
            
            st.markdown("<br>", unsafe_allow_html=True)

            # Missing skills
            st.markdown("#### 🔍 Missing Skills")
            if candidate_ranked.get('missing_skills'):
                for skill in candidate_ranked['missing_skills']:
                    st.markdown(f'<span class="skill-tag missing">{skill}</span>', unsafe_allow_html=True)
            else:
                st.success("Candidate has all required skills!")

            st.markdown("<br>", unsafe_allow_html=True)

            # Interview questions
            st.markdown("#### 📝 Interview Questions")
            if candidate_details.get('interview_questions'):
                questions = candidate_details['interview_questions']['questions']
                for q in questions:
                    with st.expander(f"{q['difficulty']} - {q['category']}"):
                        st.markdown(q['question'])
                        if q.get('context'):
                            st.markdown(f"*Context: {q['context']}*")
            else:
                st.info("No interview questions generated")

    if st.button("← Back to Rankings"):
        st.session_state.page = "ranking"
        st.rerun()

# --- SKILL GAP PAGE ---
elif page == "skill_gap":
    st.markdown("""
        <div class="header-container">
            <div class="header-title">Skill Gap Analysis</div>
            <div class="header-subtitle">Identify missing skills across all candidates</div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.jd_id or not st.session_state.ranking:
        st.warning("Please upload JD and generate rankings first!")
        if st.button("Upload JD"):
            st.session_state.page = "upload_jd"
            st.rerun()
        if st.button("Generate Rankings"):
            st.session_state.page = "ranking"
            st.rerun()
    else:
        # Get JD summary for required skills
        jd_summary = make_api_request("GET", f"/hiresense/summary/{st.session_state.jd_id}")
        if jd_summary:
            required_skills = jd_summary.get('required_skills', [])
            
            if required_skills:
                st.markdown("### Required Skills for the Job")
                for skill in required_skills:
                    st.markdown(f'<span class="skill-tag present" style="margin-right:0.5rem; margin-bottom:0.5rem; display:inline-block;">{skill}</span>', unsafe_allow_html=True)
                
                st.markdown("### Skill Gap Across Candidates")
                
                # Aggregate missing skills
                missing_skills_count = {}
                for candidate in st.session_state.ranking['ranked_candidates']:
                    for skill in candidate.get('missing_skills', []):
                        if skill not in missing_skills_count:
                            missing_skills_count[skill] = 0
                        missing_skills_count[skill] += 1
                
                if missing_skills_count:
                    # Sort by count (descending)
                    sorted_missing = sorted(missing_skills_count.items(), key=lambda x: x[1], reverse=True)
                    
                    st.markdown("#### Missing Skills and How Many Candidates Lack Them")
                    for skill, count in sorted_missing:
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.markdown(f"**{skill}**")
                        with col2:
                            percentage = (count / len(st.session_state.ranking['ranked_candidates'])) * 100
                            st.progress(percentage / 100, text=f"{count}/{len(st.session_state.ranking['ranked_candidates'])} candidates missing ({percentage:.1f}%)")
                else:
                    st.success("All candidates have all required skills!")
            else:
                st.info("No required skills found in the job description")

    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# --- SUMMARY PAGE ---
elif page == "summary":
    st.markdown("""
        <div class="header-container">
            <div class="header-title">Recruiter Summary</div>
            <div class="header-subtitle">Comprehensive overview of your hiring process and candidate matching</div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.jd_id:
        st.warning("Please upload a job description first to view the recruiter summary!")
        if st.button("Upload Job Description", type="primary"):
            st.session_state.page = "upload_jd"
            st.rerun()
    else:
        # Fetch Job Description Summary
        with st.spinner("Loading summary..."):
            summary_data = make_api_request("GET", f"/hiresense/summary/{st.session_state.jd_id}")
        
        if summary_data:
            st.markdown(f"""
                <div style="background-color: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 2rem; border-left: 5px solid #764ba2;">
                    <span style="background-color: #e0e7ff; color: #4338ca; padding: 0.35rem 0.75rem; border-radius: 9999px; font-size: 0.85rem; font-weight: 600;">Job Post Summary</span>
                    <h2 style="margin: 0.75rem 0 0.25rem 0; color: #1e293b;">{summary_data.get('job_title', 'N/A')}</h2>
                    <p style="margin: 0; color: #64748b; font-size: 1.1rem; font-weight: 500;">
                        🏢 {summary_data.get('company', 'N/A')} &nbsp;|&nbsp; 📍 {summary_data.get('location', 'N/A')}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Columns for Details and Metrics
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📋 Role Requirements")
                
                st.markdown("**Required Skills:**")
                required_skills = summary_data.get('required_skills', [])
                if required_skills:
                    skills_html = "".join([f'<span class="skill-tag present" style="margin-right: 0.5rem; margin-bottom: 0.5rem; display: inline-block;">{skill}</span>' for skill in required_skills])
                    st.markdown(f'<div style="margin-bottom: 1.5rem;">{skills_html}</div>', unsafe_allow_html=True)
                else:
                    st.info("No required skills specified in the Job Description.")

                st.markdown("**Technologies & Tools:**")
                technologies = summary_data.get('technologies', [])
                if technologies:
                    tech_html = "".join([f'<span class="skill-tag" style="background-color: #f1f5f9; color: #475569; margin-right: 0.5rem; margin-bottom: 0.5rem; display: inline-block;">{tech}</span>' for tech in technologies])
                    st.markdown(f'<div style="margin-bottom: 1.5rem;">{tech_html}</div>', unsafe_allow_html=True)
                else:
                    st.info("No specific technologies listed in the Job Description.")
            
            with col2:
                st.subheader("📊 Candidate Analytics")
                
                # Render Metrics Cards
                total_cand = summary_data.get('total_candidates', 0)
                st.metric("Total Resumes Uploaded", total_cand)
                
                if st.session_state.ranking:
                    top_cand = st.session_state.ranking.get('top_candidate')
                    if top_cand:
                        st.metric("Top Matching Candidate", top_cand.get('candidate_name', 'N/A'))
                        st.metric("Highest Match Score", f"{top_cand.get('combined_score', 0.0):.1f}%")
                else:
                    st.info("💡 Rankings have not been generated yet. Go to the Candidate Ranking page to score your candidates.")
            
            st.divider()
            
            # Candidates Match Overview Table
            if st.session_state.ranking:
                st.subheader("🏆 Candidate Rankings Table")
                
                ranked_list = st.session_state.ranking.get('ranked_candidates', [])
                if ranked_list:
                    # Build pandas dataframe for clean rendering
                    table_data = []
                    for cand in ranked_list:
                        table_data.append({
                            "Rank": f"#{cand['rank']}",
                            "Candidate Name": cand['candidate_name'] or 'Candidate',
                            "ATS Score": f"{cand['ats_score']:.1f}",
                            "Similarity Score": f"{cand['similarity_score']:.1f}",
                            "Combined Score": f"{cand['combined_score']:.1f}%"
                        })
                    
                    df = pd.DataFrame(table_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No candidates ranked yet.")
            else:
                if total_cand > 0:
                    st.warning("You have uploaded candidates but haven't generated rankings yet!")
                    if st.button("Generate Rankings Now", type="primary"):
                        st.session_state.page = "ranking"
                        st.rerun()
                else:
                    st.warning("No candidates uploaded yet for this role.")
                    if st.button("Upload Candidate Resumes", type="primary"):
                        st.session_state.page = "upload_resume"
                        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# --- DOWNLOADS PAGE ---
elif page == "downloads":
    st.markdown("""
        <div class="header-container">
            <div class="header-title">Downloads</div>
            <div class="header-subtitle">Export your candidate rankings</div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.jd_id or not st.session_state.ranking:
        st.warning("Please generate rankings first!")
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Download CSV 📊", type="primary", use_container_width=True):
                st.info("CSV download would be available here via API")
        with col2:
            if st.button("Download JSON 📋", type="primary", use_container_width=True):
                st.info("JSON download would be available here via API")

    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

else:
    st.session_state.page = "dashboard"
    st.rerun()
