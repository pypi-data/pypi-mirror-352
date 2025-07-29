from rich.style import Style

class Colors:
    # ANSI Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # ANSI Styles
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
    # Rich Styles
    INFO = Style(color="bright_blue")
    SUCCESS = Style(color="bright_green")
    WARNING = Style(color="bright_yellow")
    ERROR = Style(color="bright_red")
    CRITICAL = Style(color="red", bold=True)
    
    PORT_OPEN = Style(color="green")
    PORT_CLOSED = Style(color="red")
    VULNERABLE = Style(color="bright_red", bold=True)
    SAFE = Style(color="bright_green")
    
    URL = Style(color="bright_cyan", underline=True)
    IP_ADDRESS = Style(color="yellow")
    PORT = Style(color="bright_yellow")
    
    SECTION_HEADER = Style(color="bright_white", bold=True, underline=True)
    
    VERBOSE = Style(color="grey50", dim=True)
    VERBOSE_HIGHLIGHT = Style(color="white")
    
    # New validation styles
    VALID = Style(color="bright_green", bold=True)
    INVALID = Style(color="bright_red", bold=True)
    CHECKING = Style(color="bright_yellow")
    
    @classmethod
    def render(cls, text: str) -> str:
        """Render text with color and reset at the end"""
        return f"{text}{cls.RESET}"

class Messages:
    # Rich-style messages
    SCAN_STARTED = Style(color="bright_blue", bold=True).render("[*] Scan started")
    SCAN_COMPLETED = Style(color="bright_green", bold=True).render("[+] Scan completed")
    SITE_UP = Style(color="bright_green", bold=True).render("[+] Website is accessible")
    SITE_DOWN = Style(color="bright_red", bold=True).render("[×] Website is unreachable")
    
    # ANSI-style message types
    INFO = Colors.BLUE
    SUCCESS = Colors.GREEN
    WARNING = Colors.YELLOW
    ERROR = Colors.RED
    CRITICAL = Colors.RED + Colors.BOLD