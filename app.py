import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from utils.llm import generate_candidate_summary
from utils.jd_parser import parse_job_description
from utils.resume_parser import parse_resume
from utils.pdf_parser import extract_text
from utils.text_cleaner import clean_text
from utils.scorer import score_resume
from utils.exporter import (
    export_to_csv,
    export_to_json,
    export_to_html,
    export_to_pdf,
)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import print as rprint
    console = Console(force_terminal=True, legacy_windows=False)
    HAS_RICH = True
except Exception:
    console = None
    HAS_RICH = False

JD_PATH = "job_description/jd.txt"
RESUME_FOLDER = "resumes"



def print_banner():
    if HAS_RICH:
        console = Console()
        console.print(
            Panel.fit(
                "[bold cyan]🤖 HireSense AI — ATS Resume Screening & Candidate Ranking Engine[/bold cyan]\n"
                "[dim]Built for Rooman Technologies — Junior AI Research Associate AI Agent Challenge[/dim]",
                border_style="cyan",
            )
        )
    else:
        print("=" * 70)
        print("🤖 HireSense AI — ATS Resume Screening & Candidate Ranking Engine")
        print("Rooman Technologies — AI Agent Challenge")
        print("=" * 70)


def format_status(status: str) -> str:
    if not HAS_RICH:
        return status
    if status == "Highly Recommended":
        return "[bold green]🟢 Highly Recommended[/bold green]"
    elif status == "Recommended":
        return "[bold cyan]🔵 Recommended[/bold cyan]"
    elif status == "Consider":
        return "[bold yellow]🟡 Consider[/bold yellow]"
    else:
        return "[bold red]🔴 Not Recommended[/bold red]"


def main():
    print_banner()

    jd = parse_job_description(JD_PATH)

    if not jd:
        print("Failed to load Job Description.")
        return

    results = []
    supported_extensions = {".pdf", ".docx", ".txt"}
    resume_dir = Path(RESUME_FOLDER)

    if not resume_dir.exists():
        print(f"Directory {RESUME_FOLDER} not found.")
        return

    for resume in resume_dir.iterdir():
        if resume.suffix.lower() not in supported_extensions:
            continue

        text = extract_text(str(resume))
        if not text:
            continue

        cleaned = clean_text(text)
        resume_data = parse_resume(cleaned)

        result = score_resume(
            jd,
            resume.name,
            resume_data,
        )
        results.append(result)

    if not results:
        print("No valid resumes found.")
        return

    results.sort(key=lambda x: x["final_score"], reverse=True)

    if HAS_RICH and console:
        console.print("\n[bold yellow]⚡ Generating AI Candidate Evaluations...[/bold yellow]\n")
    else:
        print("\nGenerating AI Candidate Evaluations...\n")

    for candidate in results:
        candidate["ai_summary"] = generate_candidate_summary(jd, candidate)

    # Candidate Detail View
    if HAS_RICH and console:
        console.print("\n[bold underline cyan]🏆 Ranked Candidate Leaderboard[/bold underline cyan]\n")

    for index, candidate in enumerate(results, start=1):
        candidate["rank"] = index

        if HAS_RICH and console:
            matched_str = ", ".join(candidate["matched_skills"]) if candidate["matched_skills"] else "None"
            missing_str = ", ".join(candidate["missing_skills"]) if candidate["missing_skills"] else "None"

            content = (
                f"[bold white]File:[/bold white] {candidate['resume_file']}\n"
                f"[bold white]Status:[/bold white] {format_status(candidate['status'])}\n"
                f"[bold white]Final ATS Score:[/bold white] [bold gold1]{candidate['final_score']}%[/bold gold1] "
                f"(TF-IDF: {candidate['tfidf_score']}% | Skill: {candidate['skill_score']}% | Edu: {candidate['education_score']}%)\n\n"
                f"[bold green]✔ Matched Skills ({candidate['matched_skill_count']}/{candidate['required_skill_count']}):[/bold green] {matched_str}\n"
                f"[bold red]✖ Missing Skills:[/bold red] {missing_str}\n\n"
                f"[bold lavender]📋 AI Assessment:[/bold lavender]\n{candidate['ai_summary']}"
            )
            console.print(Panel(content, title=f"[bold cyan]Rank #{index}[/bold cyan]", border_style="blue", expand=False))
        else:
            print("\n" + "=" * 70)
            print(f"Rank #{index}")
            print("=" * 70)
            print(f"Resume File        : {candidate['resume_file']}")
            print(f"Recommendation     : {candidate['status']}")
            print(f"Final Score        : {candidate['final_score']}%")
            print(f"TF-IDF Score       : {candidate['tfidf_score']}%")
            print(f"Skill Match        : {candidate['skill_score']}%")
            print(f"Education Score    : {candidate['education_score']}%")
            print(f"Matched Skills     : {', '.join(candidate['matched_skills']) if candidate['matched_skills'] else 'None'}")
            print(f"Missing Skills     : {', '.join(candidate['missing_skills']) if candidate['missing_skills'] else 'None'}")
            print(f"\nAI Evaluation:\n{candidate['ai_summary']}")
            print("=" * 70)

    # Screening Summary
    total_candidates = len(results)
    highly_recommended = sum(1 for c in results if c["status"] == "Highly Recommended")
    recommended = sum(1 for c in results if c["status"] == "Recommended")
    consider = sum(1 for c in results if c["status"] == "Consider")
    not_recommended = sum(1 for c in results if c["status"] == "Not Recommended")
    average_score = round(sum(c["final_score"] for c in results) / total_candidates, 2)
    highest_score = max(c["final_score"] for c in results)
    lowest_score = min(c["final_score"] for c in results)

    if HAS_RICH and console:
        table = Table(title="📊 Screening Analytics & Summary", border_style="bright_blue", header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold white")

        table.add_row("Total Resumes Evaluated", str(total_candidates))
        table.add_row("🟢 Highly Recommended", str(highly_recommended))
        table.add_row("🔵 Recommended", str(recommended))
        table.add_row("🟡 Consider", str(consider))
        table.add_row("🔴 Not Recommended", str(not_recommended))
        table.add_row("Average Score", f"{average_score}%")
        table.add_row("Highest Score", f"{highest_score}%")
        table.add_row("Lowest Score", f"{lowest_score}%")

        console.print("\n")
        console.print(table)

    else:
        print("\n" + "=" * 70)
        print("SCREENING SUMMARY")
        print("=" * 70)
        print(f"Total Candidates      : {total_candidates}")
        print(f"Highly Recommended    : {highly_recommended}")
        print(f"Recommended           : {recommended}")
        print(f"Consider              : {consider}")
        print(f"Not Recommended       : {not_recommended}")
        print(f"Average Score         : {average_score}%")
        print(f"Highest Score         : {highest_score}%")
        print(f"Lowest Score          : {lowest_score}%")
        print("=" * 70)

    # Export Reports
    report_file = Path("output/report.html").resolve()
    pdf_file = Path("output/ranked_summary.pdf").resolve()
    export_to_csv(results, "output/ranked.csv")
    export_to_json(results, "output/ranked.json")
    export_to_html(results, str(report_file))
    export_to_pdf(results, str(pdf_file))

    # Open HTML Dashboard in Google Chrome / Default Browser automatically
    try:
        import webbrowser
        webbrowser.open(report_file.as_uri())
    except Exception as e:
        pass

    if HAS_RICH:
        rprint("\n[bold green]✅ Generated Reports:[/bold green]")
        rprint("  📄 [dim]output/ranked.csv[/dim]")
        rprint("  📦 [dim]output/ranked.json[/dim]")
        rprint("  📕 [dim]output/ranked_summary.pdf[/dim]")
        rprint(f"  🌐 [bold cyan]{report_file.as_uri()}[/bold cyan]")
        rprint("\n[bold cyan]🚀 Opening Candidate Screening Dashboard in Chrome/Browser...[/bold cyan]\n")
    else:
        print("\nGenerated Files:")
        print("✓ output/ranked.csv")
        print("✓ output/ranked.json")
        print("✓ output/ranked_summary.pdf")
        print(f"✓ {report_file.as_uri()}")
        print("\n" + "=" * 60)
        print("Opening Candidate Screening Dashboard in Browser...")
        print("=" * 60)


if __name__ == "__main__":
    main()