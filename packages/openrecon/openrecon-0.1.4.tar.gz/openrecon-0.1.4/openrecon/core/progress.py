from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel

class ProgressTracker:
    def __init__(self, console=None):
        self.console = console or Console()
        
    def create_progress_bar(self):
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        )
        
    def track_progress(self, items, operation_name, callback):
        results = []
        
        with self.create_progress_bar() as progress:
            task = progress.add_task(f"[cyan]{operation_name}[/cyan]", total=len(items))
            
            for item in items:
                result = callback(item)
                results.append(result)
                progress.update(task, advance=1)
                
        return results
        
    def display_status(self, message, style="info"):
        styles = {
            "info": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "critical": "red bold"
        }
        
        color = styles.get(style, "white")
        self.console.print(f"[{color}][+] {message}[/{color}]")
        
    def display_header(self, text):
        self.console.print(Panel(f"[bold blue]{text}[/bold blue]", expand=False))
        
    def display_summary(self, title, items):
        if not items:
            self.console.print(f"[yellow]No {title} found[/yellow]")
            return
            
        self.console.print(f"[bold blue]{title} Summary:[/bold blue]")
        for i, item in enumerate(items, 1):
            self.console.print(f"  {i}. {item}")
            
    def create_task(self, progress_bar, description, total):
        return progress_bar.add_task(f"[cyan]{description}[/cyan]", total=total)