from pathlib import Path
from rich.console import Console
from rich.table import Table
from datetime import datetime
import json

console = Console()

class Reporter:
    def __init__(self):
        self.reports_dir = self.get_reports_dir()

    def get_reports_dir(self):
        """Get the path to the reports directory in user's Documents folder"""
        docs_dir = Path.home() / "Documents"
        reports_dir = docs_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        return reports_dir

    def display_scan_summary(self, scan_type: str, target: str, vulnerabilities: list):
        """Display a summary of the scan results"""
        console.print(f"\n[bold green]═══ {scan_type} Scan Summary for {target} ═══[/bold green]")
        
        if not vulnerabilities:
            console.print("[yellow]No vulnerabilities were found.[/yellow]")
            return

        table = Table(title=f"{scan_type} Vulnerabilities")
        table.add_column("URL/Location", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Details", style="white")

        for vuln in vulnerabilities:
            url = vuln.get('url', target)
            vuln_type = vuln.get('type', 'Unknown')
            details = vuln.get('details', 'No additional details')
            
            table.add_row(url, vuln_type, str(details))

        console.print(table)
        console.print(f"\n[bold green]Total vulnerabilities found: {len(vulnerabilities)}[/bold green]")

    def display_vulnerabilities(self, vulnerabilities: list):
        """Display detailed information about each vulnerability"""
        if not vulnerabilities:
            return

        for i, vuln in enumerate(vulnerabilities, 1):
            console.print(f"\n[bold red]Vulnerability #{i}[/bold red]")
            for key, value in vuln.items():
                if key != 'raw_data':  # Skip raw data to keep output clean
                    console.print(f"[yellow]{key}[/yellow]: {value}")

    def save_results(self, target: str, scan_type: str, vulnerabilities: list, formats=None):
        """Save scan results to file(s)"""
        if not formats:
            formats = ['json']

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{scan_type}_{Path(target).name}_{timestamp}"

        for fmt in formats:
            if fmt.lower() == 'json':
                output_file = self.reports_dir / f"{base_filename}.json"
                with open(output_file, 'w') as f:
                    json.dump({
                        'target': target,
                        'scan_type': scan_type,
                        'timestamp': timestamp,
                        'vulnerabilities': vulnerabilities
                    }, f, indent=4)
                console.print(f"[green]Results saved to: {output_file}[/green]")