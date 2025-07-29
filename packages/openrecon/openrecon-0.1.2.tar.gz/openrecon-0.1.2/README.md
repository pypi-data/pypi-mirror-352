<h1>OpenRecon</h1>
<p>
  <em>Extensible CLI Reconnaissance & Vulnerability Assessment Tool</em>
</p>

> **Note:** This tool is currently in active development. While functional, it may contain bugs as we continue to improve it,Your feedback helps make OpenRecon better! Please report any issues.

## Overview

**OpenRecon** is an extensible, CLI-based reconnaissance and vulnerability assessment tool designed for:
- Security researchers
- Bug bounty hunters
- Penetration testers
- IT security students

This project consolidates multiple scanning techniques into a unified interface to efficiently identify vulnerabilities and surface-level threats.

**Project Background**: This is my final college project and also my first large-scale security tool — built from scratch with passion, learning, and extensive trial and error. Feedback and contributions are highly appreciated!

## Key Features

### Reconnaissance
- **Port Scanning**: Comprehensive `nmap` integration for service detection
- **Host Discovery**:
  - ARP-based scanning for local networks
  - ICMP ping sweep for wide-range detection
- **Subdomain Enumeration**: Uses `crt.sh`, DNS resolution with local caching

### Vulnerability Detection
- **XSS Scanner**: Detects reflected, stored, and DOM-based XSS
- **SQL Injection**: Identifies potential SQLi vulnerabilities
- **CSRF Scanner**: Checks for Cross-Site Request Forgery issues
- **GraphQL Scanner**: Finds exposed GraphQL endpoints
- **CMS Detection**: Fingerprints WordPress, Joomla, and other CMS platforms

## Installation

### Option 1: PyPI Installation
```bash
pip install openrecon
```
#### Troubleshooting PATH Issues
If you get a "command not found" error after installation, it may be because the executable isn’t in your system PATH (especially if using Microsoft Store Python or pip install --user). You may see a warning like:
```bash
WARNING: The script openrecon.exe is installed in 'C:\Users\...\Scripts' which is not on PATH.
```

Quick Fix (works immediately):
```bash
python -m openrecon --help
```

**Permanent Fix — Add to PATH:**
- Copy the Scripts directory path shown in the warning message
- Press Win + R, type sysdm.cpl, and press Enter
- Go to the Advanced tab, and click Environment Variables
- Under User variables, select Path and click Edit
- Click New and paste the Scripts directory path
- Click OK on all dialogs and restart your terminal

### Option 2: Manual Installation
**Linux**
```bash
git clone https://github.com/R0salman/OpenRecon
cd openrecon
chmod +x setup.sh
./setup.sh
```
**Windows**
```bash
git clone https://github.com/R0salman/OpenRecon
cd OpenRecon
setup.bat
```

## Basic Usage
```bash
openrecon --help
openrecon scan --target example.com --flags "-T4 -F"
```

#### For full documentation, usage examples, module configurations, and troubleshooting, please visit:

**[OpenRecon Documentation](https://r0salman.github.io/OpenRecon/)**  

## Available Modules

| Module | Description |
|--------|-------------|
| portscan | Nmap-based port scanning and service detection |
| livediscovery | ARP-based active host detection for local networks |
| pingsweep | ICMP ping sweep to identify online hosts |
| subenum | Subdomain enumeration with crt.sh and DNS resolution (caches in ~/.openrecon) |
| xss | Comprehensive XSS vulnerability scanning |
| sql | SQL Injection detection |
| cms | CMS fingerprinting (WordPress, Joomla, etc.) |
| csrf | CSRF vulnerability scanning |
| graphql | GraphQL endpoint detection |

## Requirements
- Python 3.7+
- Nmap (must be in system PATH) - [Download Nmap](https://nmap.org/download.html)
- playwright

## Contributing

We welcome contributions! Here's how to help:

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Disclaimer

**Important**: This tool is intended for:
- Authorized security testing
- Educational purposes
- Research and development

Unauthorized use against systems without explicit permission is illegal and unethical. The developers assume no liability and are not responsible for any misuse or damage caused by this tool.