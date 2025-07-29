from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class ScanConfig:
    target_url: str
    custom_payload: Optional[str] = None
    payload_file: Optional[str] = None
    cookies: Dict[str, str] = None
    headers: Dict[str, str] = None
    threads: int = 5
    timeout: int = 10
    depth: int = 1
    verbose: bool = False
    user_agent: str = "OpenRecon/1.0"
    crawl: bool = False
    fuzz_params: bool = False
    delay: float = 0
    methods: List[str] = None
    exclude: List[str] = None
    auth: Optional[Tuple[str, str]] = None

    def __post_init__(self):
        if self.methods is None:
            self.methods = ['GET', 'POST']
        if self.cookies is None:
            self.cookies = {}
        if self.headers is None:
            self.headers = {}

@dataclass
class Vulnerability:
    url: str
    method: str
    param_name: Optional[str]
    payload: str
    response: str
    confirmed: bool