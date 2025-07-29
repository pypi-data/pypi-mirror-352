"""
Setup configuration for Promptplex
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
requirements_path = this_directory / "requirements.txt"
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split('\n')

setup(
    name="promptplex",
    version="0.1.0",
    author="Ejiga Peter Ojonugwa Oluwafemi",
    author_email="ejigsonpeter@gmail.com",
    description="A Python library for mastering AI prompts with versioning, templating, and testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ejigsonpeter/promptplex",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.991",
        ],
        "test": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "promptplex=promptplex.cli:main",
        ],
    },
    keywords="ai, prompts, templates, llm, prompt-engineering, artificial-intelligence",
    project_urls={
        "Bug Reports": "https://github.com/ejigsonpeter/promptplex/issues",
        "Source": "https://github.com/ejigsonpeter/promptplex",
        "Documentation": "https://github.com/ejigsonpeter/promptplex#readme",
    },
)