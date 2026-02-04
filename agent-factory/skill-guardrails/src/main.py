"""
Skill Guardrails - Main CLI Entry Point

Usage:
    python -m src.main scan --skills-dir ../../skills
    python -m src.main scan --skill ../../skills/python-pro
    python -m src.main report --output reports/security-report.json
"""

import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

from .scanner import SkillScanner
from .models.report import ScanReport

# Load environment variables
load_dotenv()

app = typer.Typer(
    name="skill-guardrails",
    help="🛡️ AI Security Framework for Agent Skills",
    add_completion=False,
)
console = Console()


@app.command("scan")
def scan_skills(
    skills_dir: Optional[Path] = typer.Option(
        None,
        "--skills-dir",
        "-d",
        help="Directory containing skills to scan",
    ),
    skill: Optional[Path] = typer.Option(
        None,
        "--skill",
        "-s",
        help="Single skill directory to scan",
    ),
    level: str = typer.Option(
        "all",
        "--level",
        "-l",
        help="Security level: L1, L2, L3, L4, or all",
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Strict mode: fail on any warnings",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output JSON report to file",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose output",
    ),
):
    """
    Scan agent skills for security vulnerabilities.
    
    Runs multi-level security analysis:
    - L1: Static pattern detection
    - L2: AI-powered semantic analysis (Gemini)
    - L3: Dynamic sandbox execution
    - L4: Trust verification
    """
    # Validate inputs
    if not skills_dir and not skill:
        console.print("[red]Error: Must specify --skills-dir or --skill[/red]")
        raise typer.Exit(1)
    
    # Initialize scanner
    scanner = SkillScanner(verbose=verbose)
    
    # Determine scan targets
    if skill:
        targets = [skill]
    else:
        targets = [
            d for d in skills_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
    
    console.print(f"\n[bold blue]🛡️ Skill Guardrails Security Scan[/bold blue]")
    console.print(f"[dim]Scanning {len(targets)} skill(s) at level: {level.upper()}[/dim]\n")
    
    # Run scan with progress
    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Scanning...", total=len(targets))
        
        for target in targets:
            progress.update(task, description=f"Scanning {target.name}...")
            result = scanner.scan_skill(target, level=level)
            results.append(result)
            progress.advance(task)
    
    # Generate report
    report = ScanReport.from_results(results)
    
    # Display summary
    _display_summary(report)
    
    # Display high-risk skills
    if report.high_risk_skills:
        _display_high_risk(report.high_risk_skills)
    
    # Save report if requested
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report.to_json())
        console.print(f"\n[green]Report saved to: {output}[/green]")
    
    # Exit code
    if strict and report.blocked_count > 0:
        console.print("\n[red]❌ STRICT MODE: Scan failed due to blocked skills[/red]")
        raise typer.Exit(1)
    
    if report.blocked_count > 0:
        raise typer.Exit(1)


@app.command("report")
def generate_report(
    skills_dir: Path = typer.Option(
        ...,
        "--skills-dir",
        "-d",
        help="Directory containing skills",
    ),
    output: Path = typer.Option(
        Path("reports/security-report.json"),
        "--output",
        "-o",
        help="Output file path",
    ),
    format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Output format: json, markdown, html",
    ),
):
    """
    Generate a comprehensive security report for all skills.
    """
    console.print("[bold]Generating security report...[/bold]")
    scanner = SkillScanner()
    report = scanner.full_scan(skills_dir)
    
    output.parent.mkdir(parents=True, exist_ok=True)
    
    if format == "json":
        output.write_text(report.to_json())
    elif format == "markdown":
        output.write_text(report.to_markdown())
    else:
        output.write_text(report.to_json())
    
    console.print(f"[green]✅ Report saved to: {output}[/green]")


@app.command("verify")
def verify_signature(
    skill: Path = typer.Argument(..., help="Skill directory to verify"),
    public_key: Optional[Path] = typer.Option(
        None,
        "--key",
        "-k",
        help="Public key file for verification",
    ),
):
    """
    Verify the cryptographic signature of a skill.
    """
    console.print(f"[bold]Verifying signature for: {skill.name}[/bold]")
    # TODO: Implement signature verification
    console.print("[yellow]⚠️ Signature verification not yet implemented[/yellow]")


def _display_summary(report: ScanReport):
    """Display scan summary table."""
    table = Table(title="Scan Summary", show_header=True, header_style="bold")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="magenta", justify="right")
    table.add_column("Percentage", justify="right")
    
    total = report.total_skills
    table.add_row("📊 Total Scanned", str(total), "100%")
    table.add_row(
        "✅ Passed",
        str(report.passed_count),
        f"{report.passed_count/total*100:.1f}%" if total > 0 else "0%"
    )
    table.add_row(
        "⚠️ Flagged",
        str(report.flagged_count),
        f"{report.flagged_count/total*100:.1f}%" if total > 0 else "0%"
    )
    table.add_row(
        "🚨 Blocked",
        str(report.blocked_count),
        f"{report.blocked_count/total*100:.1f}%" if total > 0 else "0%"
    )
    
    console.print(table)


def _display_high_risk(high_risk_skills: list):
    """Display high-risk skills requiring review."""
    console.print("\n[bold red]🚨 High-Risk Skills Requiring Review:[/bold red]")
    
    table = Table(show_header=True, header_style="bold red")
    table.add_column("#", style="dim", width=4)
    table.add_column("Skill", style="cyan")
    table.add_column("Score", style="magenta", justify="right")
    table.add_column("Top Finding", style="yellow")
    
    for i, skill in enumerate(high_risk_skills[:20], 1):
        badge = "🔴" if skill.risk_score >= 0.8 else "🟠"
        table.add_row(
            str(i),
            f"{badge} {skill.name}",
            f"{skill.risk_score:.2f}",
            skill.top_finding or "N/A"
        )
    
    console.print(table)
    
    if len(high_risk_skills) > 20:
        console.print(f"[dim]...and {len(high_risk_skills) - 20} more[/dim]")


if __name__ == "__main__":
    app()
