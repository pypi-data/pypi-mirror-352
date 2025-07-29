# VC Investor Scraper

[![PyPI version](https://badge.fury.io/py/vc-investor-scraper.svg)](https://badge.fury.io/py/vc-investor-scraper)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Python tool to scrape investor data from [VCSheet.com](https://vcsheet.com) and export to CSV format or upload directly to Odoo CRM via API.

Perfect for **startups**, **investment firms**, and **business development teams** looking to build comprehensive investor databases.

## 🚀 Features

- 🔍 **Smart Keyword Filtering**: Search for investors by keywords (e.g., "fintech", "AI", "marketing")
- 📊 **Complete Data Extraction**: Extracts names, companies, emails, social media links, investment focus, and stages
- 📁 **Multiple Export Options**:
  - Standard CSV format
  - Odoo CRM-compatible CSV format
  - Direct Odoo API upload
- 🎯 **Odoo Integration**: Upload leads directly to your Odoo CRM with team and user assignments
- 🔄 **Full Pagination**: Scrapes all pages (35+ pages, 1000+ investors)
- 🛡️ **Robust Error Handling**: Handles network issues, parsing errors, and API failures gracefully
- ⚡ **Rate Limiting**: Built-in delays to respect website resources
- 🌐 **Cross-Platform**: Works on Windows, macOS, and Linux

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install vc-investor-scraper
```

### From Source
```bash
git clone https://github.com/antonpavlenko/vc-investor-scraper.git
cd vc-investor-scraper
pip install -e .
```

### Requirements
- Python 3.7+
- Internet connection
- Optional: Odoo instance for CRM integration

## ⚡ Quick Start

### Command Line Interface
After installation, you can use the tool directly from the command line:

```bash
# Export all investors to CSV
vc-investor-scraper -o all_investors.csv

# Export investors with specific keywords
vc-investor-scraper -k "fintech" "AI" -o fintech_ai_investors.csv

# Export in Odoo-compatible format
vc-investor-scraper -k "marketing" -o marketing_investors.csv --odoo
```

### Python API
```python
from vcsheet_scraper import VCSheetScraper

# Create scraper instance
scraper = VCSheetScraper()

# Get all investors
investors = scraper.get_investors()

# Get investors with keywords
ai_investors = scraper.get_investors(keywords=["AI", "machine learning"])

# Save to CSV
scraper.save_to_csv(investors, "investors.csv")
```

### Direct Odoo Upload
```bash
# Upload to Odoo CRM
vc-investor-scraper -k "AI research" --odoo-upload \
  --odoo-url "https://your-odoo.com" \
  --odoo-db "your_database" \
  --odoo-user "your_username" \
  --odoo-password "your_password" \
  --odoo-team "Your Sales Team" \
  --odoo-user-assign "Your Name"
```

## 📋 Usage Examples

### 1. Marketing Investors
```bash
vc-investor-scraper -k "marketing" -o marketing_investors.csv --odoo
```

### 2. AI & Machine Learning Investors
```bash
vc-investor-scraper -k "AI" "machine learning" -o ai_ml_investors.csv
```

### 3. Early Stage Investors
```bash
vc-investor-scraper -k "seed" "pre-seed" -o early_stage_investors.csv
```

### 4. Fintech Investors with Geographic Focus
```bash
vc-investor-scraper -k "fintech" "payments" "blockchain" -o fintech_investors.csv
```

### 5. Upload to Odoo with Team Assignment
```bash
vc-investor-scraper -k "fintech" --odoo-upload \
  --odoo-url "https://your-company.odoo.com" \
  --odoo-db "production" \
  --odoo-user "admin" \
  --odoo-password "your_api_key" \
  --odoo-model "crm.lead" \
  --odoo-stage "New" \
  --odoo-team "Investment Team" \
  --odoo-user-assign "john.doe@company.com"
```

### 6. Python Script Integration
```python
from vcsheet_scraper import VCSheetScraper, OdooAPI

# Initialize scraper
scraper = VCSheetScraper()

# Get fintech investors
fintech_investors = scraper.get_investors(keywords=["fintech", "payments"])

# Upload to Odoo
odoo = OdooAPI("https://your-odoo.com", "db", "user", "password")
odoo.authenticate()
lead_ids = odoo.create_leads(fintech_investors, default_team="Sales Team")

print(f"Created {len(lead_ids)} leads in Odoo")
```

## Command Line Options

### Basic Options
- `-k, --keywords`: Keywords to filter investors (e.g., 'fintech', 'AI', 'seed')
- `-o, --output`: Output CSV filename (optional when using --odoo-upload)
- `--odoo`: Generate Odoo CRM leads compatible CSV format
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR)

### Odoo API Options
- `--odoo-upload`: Upload data directly to Odoo via API
- `--odoo-url`: Odoo server URL (e.g., 'https://your-odoo.com')
- `--odoo-db`: Odoo database name
- `--odoo-user`: Odoo username
- `--odoo-password`: Odoo password or API key
- `--odoo-model`: Odoo model ('crm.lead' or 'res.partner', default: crm.lead)
- `--odoo-stage`: Default pipeline stage for leads
- `--odoo-team`: Default sales team to assign leads to
- `--odoo-user-assign`: Default user to assign leads to

## Output Formats

### Standard CSV Format
```csv
name,company,website,description,focus,location,stage,email,linkedin,twitter,crunchbase,youtube,check_size
John Doe,Acme Ventures,https://acme.vc,Bio and description,AI,San Francisco,Seed,john@acme.vc,linkedin.com/in/johndoe,twitter.com/johndoe,crunchbase.com/person/john-doe,,
```

### Odoo-Compatible CSV Format
```csv
External ID,Name,Company Name,Contact Name,Email,Job Position,Phone,Mobile,Street,Street2,City,State,Zip,Country,Website,Notes
1,John Doe,Acme Ventures,John Doe,john@acme.vc,Investor,,,,,,,,,https://acme.vc,"Company: Acme Ventures; Focus Areas: AI; Bio: ...; LinkedIn: ...; Source: VCSheet.com"
```

## Odoo Integration

### Setting Up Odoo API Access

1. **Get API Key** (recommended):
   - Log into Odoo → Settings → Users & Companies → Users
   - Click your user → Preferences tab → API Keys section
   - Create new API key

2. **Or use regular password** (less secure)

### Odoo Configuration Requirements

- **CRM module** must be installed
- **User permissions**: Create/write access to CRM leads
- **Sales teams**: Must exist if using --odoo-team
- **Users**: Must exist if using --odoo-user-assign

### What Gets Created in Odoo

**For CRM Leads (crm.lead)**:
- Lead name: Investor's name (without "Investor:" prefix)
- Contact name, company, email, website
- Comprehensive description with bio, focus areas, investment stages
- All social media links in description
- UTM source tracking ("VCSheet.com")
- Optional stage, team, and user assignment

## 📊 Data Extracted

For each investor, the scraper extracts:

- **Basic Info**: Name, company/fund, email, website
- **Professional**: Investment focus areas, stages, bio/description
- **Social Media**: LinkedIn, Twitter, Crunchbase, YouTube profiles
- **Metadata**: Source tracking, external IDs

### Sample Data Output
```csv
name,company,website,description,focus,stage,email,linkedin,twitter
John Doe,Acme Ventures,https://acme.vc,"Partner at Acme Ventures focusing on early-stage startups","AI, SaaS","Seed, Series A",john@acme.vc,linkedin.com/in/johndoe,twitter.com/johndoe
```

## 🎯 Use Cases

- **Startup Fundraising**: Build targeted investor lists for your industry
- **Business Development**: Identify potential partners and advisors
- **Market Research**: Analyze investment trends and focus areas
- **CRM Integration**: Automatically populate your sales pipeline
- **Lead Generation**: Create comprehensive prospect databases

## Error Handling

The scraper includes robust error handling for:
- Network connectivity issues
- Website structure changes
- Odoo API authentication failures
- Invalid search parameters
- Rate limiting and timeouts

## Rate Limiting

- Built-in delays between page requests (1-2 seconds)
- Respectful scraping practices
- Configurable timeouts and retries

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** if applicable
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Submit a pull request**

### Development Setup
```bash
git clone https://github.com/antonpavlenko/vc-investor-scraper.git
cd vc-investor-scraper
pip install -e ".[dev]"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and business purposes. Please respect VCSheet.com's terms of service and use responsibly. The authors are not responsible for any misuse of this tool.

## 🆘 Support

- **Documentation**: [GitHub README](https://github.com/antonpavlenko/vc-investor-scraper#readme)
- **Issues**: [GitHub Issues](https://github.com/antonpavlenko/vc-investor-scraper/issues)
- **PyPI**: [Package Page](https://pypi.org/project/vc-investor-scraper/)

## 🏆 Acknowledgments

- Built for the startup and investment community
- Inspired by the need for better investor discovery tools
- Thanks to VCSheet.com for providing comprehensive investor data

---

**Made with ❤️ for the startup ecosystem**

*Star ⭐ this repo if you find it useful!*
