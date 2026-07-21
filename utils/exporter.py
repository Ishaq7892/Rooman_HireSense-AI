"""
exporter.py

Exports ranked resume results to:
1. CSV
2. JSON
3. Professional HTML Report
"""

import json
from datetime import datetime

import pandas as pd

from utils.logger import logger


def export_to_csv(results: list, output_path: str):
    """
    Export ranked results to CSV.
    """

    try:
        df = pd.DataFrame(results)
        df.to_csv(output_path, index=False)

        logger.info(f"CSV exported to {output_path}")

    except Exception as e:
        logger.error(f"CSV export failed: {e}")


def export_to_json(results: list, output_path: str):
    """
    Export ranked results to JSON.
    """

    try:
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(results, file, indent=4)

        logger.info(f"JSON exported to {output_path}")

    except Exception as e:
        logger.error(f"JSON export failed: {e}")


def export_to_pdf(results: list, output_path: str):
    """
    Generate clean Candidate Ranking PDF summary document.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#1e1b4b'),
            spaceAfter=4
        )

        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#475569'),
            spaceAfter=12
        )

        cell_style = ParagraphStyle(
            'CellText',
            parent=styles['Normal'],
            fontSize=9,
            leading=11,
            textColor=colors.HexColor('#0f172a')
        )

        cell_header_style = ParagraphStyle(
            'CellHeader',
            parent=styles['Normal'],
            fontSize=9,
            leading=11,
            fontName='Helvetica-Bold',
            textColor=colors.white
        )

        elements = []

        elements.append(Paragraph("🤖 HireSense AI — Candidate Ranking Summary", title_style))
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | Total Candidates Evaluated: {len(results)}", subtitle_style))
        elements.append(Spacer(1, 8))

        table_data = [
            [
                Paragraph("Rank", cell_header_style),
                Paragraph("Candidate Resume File", cell_header_style),
                Paragraph("Status", cell_header_style),
                Paragraph("ATS Score", cell_header_style),
                Paragraph("Matched Skills", cell_header_style),
            ]
        ]

        for candidate in results:
            rank_str = f"#{candidate.get('rank', '-')}"
            filename = candidate.get('resume_file', 'Unknown')
            status = candidate.get('status', '-')
            score = f"{candidate.get('final_score', 0)}%"

            matched_list = candidate.get('matched_skills', [])
            matched_str = ", ".join(matched_list) if matched_list else "None"
            matched_text = f"({candidate.get('matched_skill_count', 0)}/{candidate.get('required_skill_count', 0)}) {matched_str}"

            status_color = "#059669" if "Highly" in status or status == "Recommended" else ("#d97706" if status == "Consider" else "#e11d48")

            table_data.append([
                Paragraph(f"<b>{rank_str}</b>", cell_style),
                Paragraph(filename, cell_style),
                Paragraph(f"<font color='{status_color}'><b>{status}</b></font>", cell_style),
                Paragraph(f"<b>{score}</b>", cell_style),
                Paragraph(matched_text, cell_style),
            ])

        table = Table(table_data, colWidths=[40, 130, 110, 65, 195])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ]))

        elements.append(table)
        doc.build(elements)
        logger.info(f"PDF summary exported to {output_path}")

    except Exception as e:
        logger.error(f"PDF export failed: {e}")


def export_to_html(results: list, output_path: str):
    """
    Generate modern recruiter dashboard HTML report.
    """

    try:
        total = len(results)
        highly_recommended = sum(1 for r in results if r["status"] == "Highly Recommended")
        recommended = sum(1 for r in results if r["status"] == "Recommended")
        consider = sum(1 for r in results if r["status"] == "Consider")
        rejected = sum(1 for r in results if r["status"] == "Not Recommended")

        average = round(
            sum(r["final_score"] for r in results) / total,
            2
        ) if total > 0 else 0.0

        highest = max(r["final_score"] for r in results) if total > 0 else 0.0

        with open(
            "templates/report_template.html",
            "r",
            encoding="utf-8"
        ) as file:
            html = file.read()

        summary_html = f"""
        <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-info">
                <h3>{total}</h3>
                <p>Total Candidates</p>
            </div>
        </div>

        <div class="stat-card stat-success">
            <div class="stat-icon">⭐</div>
            <div class="stat-info">
                <h3>{highly_recommended + recommended}</h3>
                <p>Recommended</p>
            </div>
        </div>

        <div class="stat-card stat-warning">
            <div class="stat-icon">⚡</div>
            <div class="stat-info">
                <h3>{consider}</h3>
                <p>Under Consideration</p>
            </div>
        </div>

        <div class="stat-card stat-danger">
            <div class="stat-icon">✖</div>
            <div class="stat-info">
                <h3>{rejected}</h3>
                <p>Not Recommended</p>
            </div>
        </div>

        <div class="stat-card stat-primary">
            <div class="stat-icon">🎯</div>
            <div class="stat-info">
                <h3>{average}%</h3>
                <p>Average Score</p>
            </div>
        </div>
        """

        candidate_html = ""

        for candidate in results:
            status = candidate["status"]
            if status == "Highly Recommended":
                badge_class = "badge-highly"
                badge_text = "🟢 Highly Recommended"
            elif status == "Recommended":
                badge_class = "badge-good"
                badge_text = "🔵 Recommended"
            elif status == "Consider":
                badge_class = "badge-medium"
                badge_text = "🟡 Consider"
            else:
                badge_class = "badge-bad"
                badge_text = "🔴 Not Recommended"

            # Format matched & missing skill tags
            matched_tags = "".join(
                f'<span class="skill-tag skill-matched">✓ {skill}</span>'
                for skill in candidate["matched_skills"]
            ) if candidate["matched_skills"] else '<span class="no-skills">None</span>'

            missing_tags = "".join(
                f'<span class="skill-tag skill-missing">✖ {skill}</span>'
                for skill in candidate["missing_skills"]
            ) if candidate["missing_skills"] else '<span class="no-skills">None</span>'

            # Clean AI summary into formatted lines
            ai_summary_text = candidate["ai_summary"]
            ai_summary_html = f'<div class="ai-summary-content">{ai_summary_text.replace(chr(10), "<br>")}</div>'

            candidate_html += f"""
            <div class="candidate-card" id="candidate-rank-{candidate['rank']}">
                <div class="candidate-header">
                    <div class="candidate-title-grp">
                        <span class="rank-badge">#{candidate['rank']}</span>
                        <h2>{candidate['resume_file']}</h2>
                    </div>
                    <span class="status-badge {badge_class}">{badge_text}</span>
                </div>

                <div class="score-grid">
                    <div class="score-box final-score-box">
                        <span class="score-label">Final ATS Score</span>
                        <span class="score-val">{candidate['final_score']}%</span>
                        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {min(candidate['final_score'], 100)}%;"></div></div>
                    </div>

                    <div class="score-box">
                        <span class="score-label">TF-IDF Match (40%)</span>
                        <span class="score-val">{candidate['tfidf_score']}%</span>
                        <div class="progress-bar-bg"><div class="progress-bar-fill tfidf-fill" style="width: {min(candidate['tfidf_score'], 100)}%;"></div></div>
                    </div>

                    <div class="score-box">
                        <span class="score-label">Skill Match (50%)</span>
                        <span class="score-val">{candidate['skill_score']}%</span>
                        <div class="progress-bar-bg"><div class="progress-bar-fill skill-fill" style="width: {min(candidate['skill_score'], 100)}%;"></div></div>
                    </div>

                    <div class="score-box">
                        <span class="score-label">Education Match (10%)</span>
                        <span class="score-val">{candidate['education_score']}%</span>
                        <div class="progress-bar-bg"><div class="progress-bar-fill edu-fill" style="width: {min(candidate['education_score'], 100)}%;"></div></div>
                    </div>
                </div>

                <div class="skills-section">
                    <div class="skills-grp">
                        <h4>Matched Core Competencies ({candidate['matched_skill_count']}/{candidate['required_skill_count']})</h4>
                        <div class="tags-container">{matched_tags}</div>
                    </div>

                    <div class="skills-grp">
                        <h4>Missing Core Competencies</h4>
                        <div class="tags-container">{missing_tags}</div>
                    </div>
                </div>

                <div class="ai-eval-box">
                    <h4>🤖 Recruiter AI Intelligence Summary</h4>
                    {ai_summary_html}
                </div>
            </div>
            """

        html = html.replace(
            "{{GENERATED_DATE}}",
            datetime.now().strftime("%B %d, %Y at %I:%M %p")
        )

        html = html.replace(
            "{{SUMMARY}}",
            summary_html
        )

        html = html.replace(
            "{{CANDIDATES}}",
            candidate_html
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(html)

        logger.info(f"HTML report exported to {output_path}")

    except Exception as e:
        logger.error(f"HTML export failed: {e}")