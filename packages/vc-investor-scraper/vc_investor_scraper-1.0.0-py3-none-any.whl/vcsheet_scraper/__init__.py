"""
VC Investor Scraper Package

A powerful Python tool to scrape VC investor data from VCSheet.com with Odoo CRM integration.

Features:
- Smart keyword filtering for targeted investor searches
- Complete data extraction including social media links
- Multiple export formats (CSV, Odoo-compatible CSV)
- Direct Odoo API integration with team and user assignments
- Full pagination support (1000+ investors)
- Robust error handling and rate limiting
"""

__version__ = "1.0.0"
__author__ = "Anton Pavlenko"
__email__ = "apavlenko@hmcorp.fund"
__description__ = "A powerful Python tool to scrape VC investor data from VCSheet.com with Odoo CRM integration"

from .scraper import VCSheetScraper, OdooAPI

__all__ = ["VCSheetScraper", "OdooAPI"]
