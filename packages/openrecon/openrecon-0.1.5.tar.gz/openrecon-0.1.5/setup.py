from setuptools import setup, find_packages
import os

def read_file(filename):
    file_path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def read_requirements():
    requirements = []
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    try:
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    except FileNotFoundError:
        # Fallback
        requirements = [
            "rich>=13.0.0",
            "python-nmap>=0.7.1", 
            "requests>=2.31.0",
            "aiohttp>=3.8.0",
            "beautifulsoup4>=4.12.0",
            "dnspython>=2.3.0",
            "lxml>=4.9.0",
            "urllib3>=2.0.0",
            "validators>=0.20.0",
            "pathlib>=1.0.1",
            "scapy>=2.6.1",
            "httpx>=0.28.1",
            "futures>=3.4.0",
            "argparse>=1.4.0",
            "asyncio>=3.4.3",
            "regex>=2024.11.6"
        ]
    return requirements

setup(
    name="openrecon",
    version="0.1.5",
    author="R0salman",
    author_email="salmanalmtyry522@gmail.com",
    description="A lightweight, modular cybersecurity scanner",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/R0salman/OpenRecon",
    project_urls={
        "Bug Reports": "https://github.com/R0salman/OpenRecon/issues",
        "Source": "https://github.com/R0salman/OpenRecon",
        "Documentation": "https://r0salman.github.io/OpenRecon/",
    },
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "openrecon=openrecon.cli:cli_entrypoint",
        ],
    },
    keywords=[
        "security", 
        "vulnerability scanner", 
        "xss", 
        "sql injection",
        "cms detection", 
        "web security",
        "penetration testing",
        "reconnaissance",
        "subdomain enumeration",
        "port scanning"
    ],
    include_package_data=True,
    zip_safe=False,
    platforms=['any'],
)