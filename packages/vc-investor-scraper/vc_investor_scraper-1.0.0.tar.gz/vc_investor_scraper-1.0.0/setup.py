from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="vc-investor-scraper",
    version="1.0.0",
    author="Anton Pavlenko",
    author_email="apavlenko@hmcorp.fund",
    description="A powerful Python tool to scrape VC investor data from VCSheet.com with Odoo CRM integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/antonpavlenko/vc-investor-scraper",
    project_urls={
        "Bug Reports": "https://github.com/antonpavlenko/vc-investor-scraper/issues",
        "Source": "https://github.com/antonpavlenko/vc-investor-scraper",
        "Documentation": "https://github.com/antonpavlenko/vc-investor-scraper#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="vc venture capital investors scraper odoo crm vcsheet fintech startup",
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "vc-investor-scraper=vcsheet_scraper.scraper:main",
            "vcsheet-scraper=vcsheet_scraper.scraper:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
