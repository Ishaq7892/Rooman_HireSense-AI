import re
from typing import List, Set
from backend.core.logging import logger
from backend.models.schemas import (
    StructuredResume, 
    StructuredJobDescription, 
    ATSScoreBreakdown, 
    ATSResult
)
from ai.chains import extraction_chains


class ATSScoringService:
    """
    Service for calculating ATS scores and providing analysis.
    """

    def __init__(self):
        self.extraction_chains = extraction_chains
        logger.info("ATSScoringService initialized")

    def _normalize_skill(self, skill: str) -> str:
        """Normalize skill for comparison (lowercase, remove punctuation, normalize spacing, etc.)"""
        # Remove punctuation, replace hyphens/underscores with spaces, lowercase, strip, normalize whitespace
        normalized = re.sub(r'[^\w\s]', '', skill.strip().lower())
        normalized = re.sub(r'[\s_-]+', ' ', normalized)
        return normalized.strip()

    def _extract_additional_skills(self, structured_resume) -> Set[str]:
        """Extract additional skills from experience, projects, education, etc."""
        additional_skills = set()
        # Extract from experience descriptions
        for exp in structured_resume.experience:
            if exp.description:
                # Extract words from description
                words = re.findall(r'\b[a-zA-Z0-9+#]{3,}\b', exp.description.lower())
                additional_skills.update(words)
        # Extract from project descriptions and technologies
        for proj in structured_resume.projects:
            if proj.technologies:
                for tech in proj.technologies:
                    additional_skills.add(self._normalize_skill(tech))
            if proj.description:
                words = re.findall(r'\b[a-zA-Z0-9+#]{3,}\b', proj.description.lower())
                additional_skills.update(words)
        # Extract from certifications
        for cert in structured_resume.certifications:
            if cert.name:
                words = re.findall(r'\b[a-zA-Z0-9+#]{3,}\b', cert.name.lower())
                additional_skills.update(words)
        return additional_skills

    def _skill_matches(self, jd_skill_norm: str, resume_skill_set: Set[str]) -> bool:
        """Check if a JD skill matches any resume skill (exact or substring match)."""
        if jd_skill_norm in resume_skill_set:
            return True
        for res_skill in resume_skill_set:
            if jd_skill_norm in res_skill or res_skill in jd_skill_norm:
                return True
        return False

    def _calculate_skill_match_score(
        self,
        resume_structured,
        jd_required_skills: List[str],
        jd_preferred_skills: List[str],
        jd_technologies: List[str]
    ) -> float:
        """
        Calculate skill match score (0-100).
        """
        resume_skill_set: Set[str] = set()
        # Add skills from structured skills list
        for skill in resume_structured.skills:
            normalized = self._normalize_skill(skill)
            if normalized:
                resume_skill_set.add(normalized)
        # Add additional skills extracted from experience/projects/certifications
        additional_skills = self._extract_additional_skills(resume_structured)
        resume_skill_set.update(additional_skills)
        
        logger.info(f"Normalized resume skill set (including extracted): {resume_skill_set}")

        all_jd_skills = list(set(jd_required_skills + jd_preferred_skills + jd_technologies))
        
        if not all_jd_skills:
            logger.info("No JD skills found, returning 100")
            return 100.0

        matched_required = 0
        matched_preferred = 0
        matched_tech = 0
        
        total_required = len(jd_required_skills) if jd_required_skills else 1
        total_preferred = len(jd_preferred_skills) if jd_preferred_skills else 1
        total_tech = len(jd_technologies) if jd_technologies else 1
        
        logger.info(f"Total required: {total_required}, total preferred: {total_preferred}, total tech: {total_tech}")
        
        for skill in jd_required_skills:
            normalized = self._normalize_skill(skill)
            logger.info(f"Checking required skill: {skill} (normalized: {normalized})")
            if normalized and self._skill_matches(normalized, resume_skill_set):
                matched_required += 1
                logger.info(f"  MATCHED!")
        
        for skill in jd_preferred_skills:
            normalized = self._normalize_skill(skill)
            logger.info(f"Checking preferred skill: {skill} (normalized: {normalized})")
            if normalized and self._skill_matches(normalized, resume_skill_set):
                matched_preferred += 1
                logger.info(f"  MATCHED!")
        
        for tech in jd_technologies:
            normalized = self._normalize_skill(tech)
            logger.info(f"Checking tech skill: {tech} (normalized: {normalized})")
            if normalized and self._skill_matches(normalized, resume_skill_set):
                matched_tech += 1
                logger.info(f"  MATCHED!")
        
        logger.info(f"Matched required: {matched_required}, preferred: {matched_preferred}, tech: {matched_tech}")
        
        required_score = (matched_required / total_required) * 60  # 60% weight for required skills
        preferred_score = (matched_preferred / total_preferred) * 25  # 25% weight for preferred skills
        tech_score = (matched_tech / total_tech) * 15  # 15% weight for technologies
        
        total_score = required_score + preferred_score + tech_score
        logger.info(f"Skill match score breakdown: req={required_score}, pref={preferred_score}, tech={tech_score}, total={total_score}")
        return min(100.0, max(0.0, total_score))

    def _calculate_experience_score(
        self, 
        resume_experience: List, 
        jd_experience_required: str
    ) -> float:
        """
        Calculate experience score (0-100) with more variation based on number of roles and relevance.
        """
        num_experiences = len(resume_experience)
        base_score = min(100.0, 50.0 + (num_experiences * 10))  # 50 base, +10 per experience, max 100
        
        if not jd_experience_required:
            return min(100.0, base_score)
        
        # Try to extract years from JD requirement using simple regex
        jd_years_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)', jd_experience_required.lower())
        jd_required_years = int(jd_years_match.group(1)) if jd_years_match else 0
        
        total_experience_years = 0
        for exp in resume_experience:
            # Try to estimate years of experience (simplified)
            if exp.start_date and exp.end_date:
                # Very rough estimate: assume each job is at least 1 year
                total_experience_years += 1
            elif exp.start_date and not exp.end_date:
                # Current job: add 1 year
                total_experience_years += 1
        
        # If we couldn't parse, assume some experience
        if total_experience_years == 0 and len(resume_experience) > 0:
            total_experience_years = len(resume_experience)
        
        if jd_required_years == 0:
            return min(100.0, base_score)
        
        # Calculate score
        if total_experience_years >= jd_required_years:
            return min(100.0, base_score + 30)
        else:
            return min(100.0, (total_experience_years / jd_required_years) * 70 + base_score * 0.3)

    def _calculate_education_score(
        self, 
        resume_education: List, 
        jd_education_required: str
    ) -> float:
        """
        Calculate education score (0-100) with more variation based on number of degrees.
        """
        num_degrees = len(resume_education)
        base_score = 30.0 + (num_degrees * 20)  # 30 base, +20 per degree
        
        if not jd_education_required or not resume_education:
            return min(100.0, base_score)
        
        # Simple keyword-based scoring for education match
        jd_education_lower = jd_education_required.lower()
        
        education_keywords = {
            'bachelor': ['bachelor', 'bsc', 'ba', 'bs'],
            'master': ['master', 'msc', 'ma', 'ms'],
            'phd': ['phd', 'doctorate', 'ph.d'],
            'associate': ['associate', 'diploma']
        }
        
        bonus_score = 0
        # Check if any resume degree matches JD keywords
        for edu in resume_education:
            degree_lower = edu.degree.lower()
            for level, keywords in education_keywords.items():
                if any(kw in degree_lower for kw in keywords) and any(kw in jd_education_lower for kw in keywords):
                    bonus_score += 40
                    break
            # Check if school name is mentioned in JD (rare but possible)
            if edu.school.lower() in jd_education_lower:
                bonus_score += 20
                break
        
        return min(100.0, max(0.0, base_score + bonus_score))

    def _calculate_project_match_score(
        self, 
        resume_projects: List, 
        jd_required_skills: List[str], 
        jd_technologies: List[str]
    ) -> float:
        """
        Calculate project match score (0-100) with more variation.
        """
        num_projects = len(resume_projects)
        base_score = num_projects * 15  # 15 points per project base score
        
        if not resume_projects:
            return 0.0
        
        jd_keywords = [self._normalize_skill(s) for s in jd_required_skills + jd_technologies]
        
        total_matches = 0
        total_checked = 0
        
        for project in resume_projects:
            tech_list = project.technologies or []
            desc = project.description or ""
            
            project_text = " ".join(tech_list) + " " + desc
            project_text = self._normalize_skill(project_text)
            
            for kw in jd_keywords:
                if kw in project_text:
                    total_matches += 1
                total_checked += 1
        
        match_score = 0
        if total_checked > 0:
            match_score = (total_matches / total_checked) * 85
        
        return min(100.0, base_score + match_score)

    def _calculate_certification_score(
        self, 
        resume_certifications: List, 
        jd_required_skills: List[str], 
        jd_technologies: List[str]
    ) -> float:
        """
        Calculate certification score (0-100) with more variation.
        """
        num_certs = len(resume_certifications)
        base_score = num_certs * 20  # 20 points per certification base
        
        if not resume_certifications:
            return 0.0
        
        jd_keywords = [self._normalize_skill(s) for s in jd_required_skills + jd_technologies]
        
        total_matches = 0
        total_checked = 0
        
        for cert in resume_certifications:
            cert_text = self._normalize_skill(cert.name + " " + cert.issuer)
            
            for kw in jd_keywords:
                if kw in cert_text:
                    total_matches += 1
                total_checked += 1
        
        match_score = 0
        if total_checked > 0:
            match_score = (total_matches / total_checked) * 80
        
        return min(100.0, base_score + match_score)

    def calculate_ats_score(
        self,
        resume_structured: StructuredResume,
        jd_structured: StructuredJobDescription
    ) -> ATSResult:
        """
        Calculate full ATS score and analysis.

        Args:
            resume_structured: Structured resume data
            jd_structured: Structured job description data

        Returns:
            ATSResult with total score, breakdown, reasoning, strengths, weaknesses, missing skills
        """
        try:
            logger.info(f"Starting ATS score calculation for candidate: {resume_structured.name}")
            logger.info(f"Resume skills: {resume_structured.skills}")
            logger.info(f"JD required skills: {jd_structured.required_skills}")
            logger.info(f"JD preferred skills: {jd_structured.preferred_skills}")
            logger.info(f"JD tech: {jd_structured.technologies}")
            
            # Calculate individual scores
            skill_match_score = self._calculate_skill_match_score(
                resume_structured=resume_structured,
                jd_required_skills=jd_structured.required_skills,
                jd_preferred_skills=jd_structured.preferred_skills,
                jd_technologies=jd_structured.technologies
            )
            
            experience_score = self._calculate_experience_score(
                resume_experience=resume_structured.experience,
                jd_experience_required=jd_structured.experience_required
            )
            
            education_score = self._calculate_education_score(
                resume_education=resume_structured.education,
                jd_education_required=jd_structured.education_required
            )
            
            project_match_score = self._calculate_project_match_score(
                resume_projects=resume_structured.projects,
                jd_required_skills=jd_structured.required_skills,
                jd_technologies=jd_structured.technologies
            )
            
            certification_score = self._calculate_certification_score(
                resume_certifications=resume_structured.certifications,
                jd_required_skills=jd_structured.required_skills,
                jd_technologies=jd_structured.technologies
            )
            
            # Calculate total score with weights
            total_score = (
                (skill_match_score * 0.40) +
                (experience_score * 0.25) +
                (education_score * 0.15) +
                (project_match_score * 0.10) +
                (certification_score * 0.10)
            )
            
            # Create score breakdown
            score_breakdown = ATSScoreBreakdown(
                skill_match_score=round(skill_match_score, 2),
                experience_score=round(experience_score, 2),
                education_score=round(education_score, 2),
                project_match_score=round(project_match_score, 2),
                certification_score=round(certification_score, 2)
            )
            
            # Manual missing skills calculation
            missing_skills = []
            resume_skill_set_normalized = set(
                self._normalize_skill(skill) for skill in resume_structured.skills
            )
            # Add additional skills to check
            resume_skill_set_normalized.update(self._extract_additional_skills(resume_structured))
            
            for skill in jd_structured.required_skills:
                normalized_jd_skill = self._normalize_skill(skill)
                if not self._skill_matches(normalized_jd_skill, resume_skill_set_normalized):
                    missing_skills.append(skill)
            
            logger.info(f"Manual missing skills: {missing_skills}")
            
            # Generate reasoning, strengths, weaknesses using LLM
            reasoning_data = self.extraction_chains.generate_ats_reasoning(
                resume_data=resume_structured.dict(),
                jd_data=jd_structured.dict(),
                score_breakdown=score_breakdown.dict()
            )
            
            # Create ATS result
            ats_result = ATSResult(
                total_score=round(total_score, 2),
                score_breakdown=score_breakdown,
                reasoning=reasoning_data.get('reasoning', 'Score calculated successfully.'),
                strengths=reasoning_data.get('strengths', []),
                weaknesses=reasoning_data.get('weaknesses', []),
                missing_skills=missing_skills
            )
            
            logger.info(f"ATS score calculated: {total_score:.2f}")
            return ats_result
            
        except Exception as e:
            logger.error(f"Error calculating ATS score: {str(e)}", exc_info=True)
            raise Exception(f"Failed to calculate ATS score: {str(e)}")


# Singleton instance
ats_scoring_service = ATSScoringService()
