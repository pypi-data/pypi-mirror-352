import requests
from bs4 import BeautifulSoup
import csv
import logging
import time
import random
import argparse
import sys
import urllib.parse
import xmlrpc.client
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class OdooAPI:
    """Odoo API client for uploading investor data directly to Odoo CRM"""

    def __init__(self, url: str, db: str, username: str, password: str):
        """
        Initialize Odoo API connection

        Args:
            url: Odoo server URL (e.g., 'https://your-odoo.com' or 'http://localhost:8069')
            db: Database name
            username: Odoo username
            password: Odoo password or API key
        """
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.uid = None

        # Initialize XML-RPC clients
        self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

        logger.info(f"Initializing Odoo API connection to {self.url}")

    def authenticate(self) -> bool:
        """
        Authenticate with Odoo server

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            if self.uid:
                logger.info(f"Successfully authenticated with Odoo as user ID: {self.uid}")
                return True
            else:
                logger.error("Authentication failed - invalid credentials")
                return False
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def test_connection(self) -> bool:
        """
        Test the connection to Odoo

        Returns:
            True if connection successful, False otherwise
        """
        try:
            version = self.common.version()
            logger.info(f"Connected to Odoo version: {version}")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def create_leads(self, investors: List[Dict], model: str = 'crm.lead',
                    default_stage: str = None, default_team: str = None,
                    default_user: str = None) -> List[int]:
        """
        Create CRM leads from investor data

        Args:
            investors: List of investor dictionaries
            model: Odoo model to create records in ('crm.lead' or 'res.partner')
            default_stage: Default pipeline stage for leads
            default_team: Default sales team
            default_user: Default user to assign leads to

        Returns:
            List of created record IDs
        """
        if not self.uid:
            raise Exception("Not authenticated. Call authenticate() first.")

        created_ids = []

        # Get stage and team IDs if specified
        stage_id = self._get_stage_id(default_stage) if default_stage else None
        team_id = self._get_team_id(default_team) if default_team else None
        user_id = self._get_user_id(default_user) if default_user else None

        logger.info(f"Creating {len(investors)} records in Odoo model: {model}")

        for i, investor in enumerate(investors, 1):
            try:
                # Prepare lead data based on model type
                if model == 'crm.lead':
                    lead_data = self._prepare_lead_data(investor, stage_id, team_id, user_id)
                elif model == 'res.partner':
                    lead_data = self._prepare_partner_data(investor)
                else:
                    raise ValueError(f"Unsupported model: {model}")

                # Create the record
                record_id = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    model, 'create', [lead_data]
                )

                created_ids.append(record_id)
                logger.debug(f"Created {model} record {record_id} for {investor.get('name')}")

                # Progress logging
                if i % 10 == 0:
                    logger.info(f"Created {i}/{len(investors)} records...")

            except Exception as e:
                logger.error(f"Failed to create record for {investor.get('name', 'Unknown')}: {e}")
                continue

        logger.info(f"Successfully created {len(created_ids)} out of {len(investors)} records")
        return created_ids

    def _prepare_lead_data(self, investor: Dict, stage_id: int = None,
                          team_id: int = None, user_id: int = None) -> Dict:
        """Prepare lead data for crm.lead model"""
        # Create comprehensive description
        description_parts = []

        if investor.get('company'):
            description_parts.append(f"Company: {investor.get('company')}")

        if investor.get('focus'):
            description_parts.append(f"Focus Areas: {investor.get('focus')}")

        if investor.get('stage'):
            description_parts.append(f"Investment Stages: {investor.get('stage')}")

        if investor.get('description'):
            description_parts.append(f"Bio: {investor.get('description')}")

        # Add social media links
        social_links = []
        if investor.get('linkedin'):
            social_links.append(f"LinkedIn: {investor.get('linkedin')}")
        if investor.get('twitter'):
            social_links.append(f"Twitter: {investor.get('twitter')}")
        if investor.get('crunchbase'):
            social_links.append(f"Crunchbase: {investor.get('crunchbase')}")
        if investor.get('youtube'):
            social_links.append(f"YouTube: {investor.get('youtube')}")

        if social_links:
            description_parts.append("Social Media & Links:")
            description_parts.extend(social_links)

        description_parts.append("Source: VCSheet.com")
        description = "\n".join(description_parts)

        lead_data = {
            'name': investor.get('name', 'Unknown'),
            'contact_name': investor.get('name', ''),
            'partner_name': investor.get('company', ''),
            'email_from': investor.get('email', ''),
            'website': investor.get('website', ''),
            'function': 'Investor',
            'description': description,
        }

        # Add source_id only if we can get/create it
        source_id = self._get_or_create_source('VCSheet.com')
        if source_id:
            lead_data['source_id'] = source_id

        # Add optional fields if provided (and not None)
        if stage_id:
            lead_data['stage_id'] = stage_id
        if team_id:
            lead_data['team_id'] = team_id
        if user_id:
            lead_data['user_id'] = user_id

        return lead_data

    def _prepare_partner_data(self, investor: Dict) -> Dict:
        """Prepare partner data for res.partner model"""
        # Create comprehensive comment
        comment_parts = []

        if investor.get('focus'):
            comment_parts.append(f"Focus Areas: {investor.get('focus')}")

        if investor.get('stage'):
            comment_parts.append(f"Investment Stages: {investor.get('stage')}")

        if investor.get('description'):
            comment_parts.append(f"Bio: {investor.get('description')}")

        # Add social media links
        social_links = []
        if investor.get('linkedin'):
            social_links.append(f"LinkedIn: {investor.get('linkedin')}")
        if investor.get('twitter'):
            social_links.append(f"Twitter: {investor.get('twitter')}")
        if investor.get('crunchbase'):
            social_links.append(f"Crunchbase: {investor.get('crunchbase')}")
        if investor.get('youtube'):
            social_links.append(f"YouTube: {investor.get('youtube')}")

        if social_links:
            comment_parts.append("Social Media & Links:")
            comment_parts.extend(social_links)

        comment_parts.append("Source: VCSheet.com")
        comment = "\n".join(comment_parts)

        partner_data = {
            'name': investor.get('name', 'Unknown'),
            'parent_name': investor.get('company', ''),
            'email': investor.get('email', ''),
            'website': investor.get('website', ''),
            'function': 'Investor',
            'comment': comment,
            'is_company': False,
            'supplier_rank': 0,
            'customer_rank': 1,  # Mark as customer for CRM purposes
            'category_id': [(4, self._get_or_create_category('Investor'))],
        }

        return partner_data

    def _get_stage_id(self, stage_name: str) -> int:
        """Get stage ID by name"""
        if not stage_name:
            return None
        try:
            stage_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'crm.stage', 'search', [['name', '=', stage_name]]
            )
            return stage_ids[0] if stage_ids else None
        except Exception as e:
            logger.warning(f"Could not find stage '{stage_name}': {e}")
            return None

    def _get_team_id(self, team_name: str) -> int:
        """Get team ID by name"""
        if not team_name:
            return None
        try:
            # Get all teams and search manually to avoid domain issues
            all_teams = self.models.execute_kw(
                self.db, self.uid, self.password,
                'crm.team', 'search_read', [[]], {'fields': ['id', 'name']}
            )

            # Look for exact match first
            for team in all_teams:
                if team['name'] == team_name:
                    logger.info(f"Found team by exact match: '{team['name']}'")
                    return team['id']

            # Look for partial match (case-insensitive)
            for team in all_teams:
                if team_name.lower() in team['name'].lower():
                    logger.info(f"Found team by partial match: '{team['name']}' for search '{team_name}'")
                    return team['id']

            logger.warning(f"Team '{team_name}' not found. Available teams: {[t['name'] for t in all_teams]}")
            return None
        except Exception as e:
            logger.warning(f"Could not find team '{team_name}': {e}")
            return None

    def _get_user_id(self, username: str) -> int:
        """Get user ID by name or login"""
        if not username:
            return None
        try:
            # Get all users and search manually to avoid domain issues
            all_users = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.users', 'search_read', [[]], {'fields': ['id', 'name', 'login']}
            )

            # Look for exact match first
            for user in all_users:
                if user['name'] == username or user['login'] == username:
                    logger.info(f"Found user by exact match: '{user['name']}'")
                    return user['id']

            # Look for partial match (case-insensitive)
            for user in all_users:
                if (username.lower() in user['name'].lower() or
                    username.lower() in user['login'].lower()):
                    logger.info(f"Found user by partial match: '{user['name']}' for search '{username}'")
                    return user['id']

            logger.warning(f"User '{username}' not found. Available users: {[(u['name'], u['login']) for u in all_users[:5]]}")
            return None
        except Exception as e:
            logger.warning(f"Could not find user '{username}': {e}")
            return None

    def _get_or_create_source(self, source_name: str) -> int:
        """Get or create UTM source"""
        if not source_name:
            return None
        try:
            # Get all sources and search manually to avoid domain issues
            all_sources = self.models.execute_kw(
                self.db, self.uid, self.password,
                'utm.source', 'search_read', [[]], {'fields': ['id', 'name']}
            )

            # Look for exact match
            for source in all_sources:
                if source['name'] == source_name:
                    return source['id']

            # Create new source if not found
            try:
                source_id = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'utm.source', 'create', [{'name': source_name}]
                )
                logger.info(f"Created new UTM source: {source_name}")
                return source_id
            except Exception as create_error:
                logger.warning(f"Could not create UTM source '{source_name}': {create_error}")
                return None
        except Exception as e:
            logger.warning(f"Could not get/create source '{source_name}': {e}")
            return None

    def _get_or_create_category(self, category_name: str) -> int:
        """Get or create partner category"""
        try:
            category_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner.category', 'search', [['name', '=', category_name]]
            )

            if category_ids:
                return category_ids[0]
            else:
                # Create new category
                category_id = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'res.partner.category', 'create', [{'name': category_name}]
                )
                logger.info(f"Created new partner category: {category_name}")
                return category_id
        except Exception as e:
            logger.warning(f"Could not get/create category '{category_name}': {e}")
            return None


class VCSheetScraper:
    """Scraper for extracting investor data from vcsheet.com"""
    
    BASE_URL = "https://www.vcsheet.com/investors"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.vcsheet.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def get_investors(self, keywords: Optional[List[str]] = None) -> List[Dict]:
        """
        Scrape investors from vcsheet.com with optional keyword filtering

        Args:
            keywords: List of keywords to filter investors

        Returns:
            List of investor dictionaries with relevant data
        """
        all_investors = []
        page = 1

        while True:
            url = self.BASE_URL
            params = {}

            # Note: Website search doesn't work via URL parameters (client-side JS only)
            # So we scrape all investors and filter locally

            if page > 1:
                params['bd69063d_page'] = str(page)

            if params:
                url = f"{url}?" + "&".join([f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in params.items()])

            logger.info(f"Fetching investors from {url}")
            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Check if there's a next page first (before filtering)
            next_link = soup.select_one('a[href*="bd69063d_page"]:contains("Next")')
            has_next_page = bool(next_link)

            # Apply keyword filtering locally since website search doesn't work via URL
            page_investors = self._parse_investors(soup, keywords)

            # Always extend the list, even if empty (some pages might have no matches)
            all_investors.extend(page_investors)

            if page_investors:
                logger.info(f"Found {len(page_investors)} investors on page {page}")
            else:
                logger.debug(f"No matching investors found on page {page}")

            # Stop only when there are no more pages, not when no matches on current page
            if not has_next_page:
                logger.debug("No next page found - reached end of investor list")
                break

            page += 1
            # Add delay between pages
            time.sleep(random.uniform(1.0, 2.0))

        return all_investors
    
    def _parse_investors(self, soup: BeautifulSoup, keywords: Optional[List[str]] = None) -> List[Dict]:
        """Extract investor data from the parsed HTML

        Args:
            soup: Parsed HTML soup
            keywords: Optional list of keywords to filter investors

        Returns:
            List of investor dictionaries
        """
        investors = []

        # Look for h3 elements that contain investor names - this is the main structure
        investor_headings = soup.select('h3')

        for heading in investor_headings:
            try:
                # Skip if this doesn't look like an investor name
                heading_text = heading.get_text(strip=True)
                if not heading_text or len(heading_text.split()) < 2:
                    continue

                # Find the parent container that holds all investor info
                # Look for the section that contains this heading
                investor_container = heading.find_parent()
                while investor_container and investor_container.name != 'body':
                    # Look for a container that has multiple elements (name, company, description, etc.)
                    if len(investor_container.find_all(['p', 'strong', 'a'])) >= 3:
                        break
                    investor_container = investor_container.find_parent()

                if not investor_container:
                    continue

                # Extract investor details
                name = heading_text

                # Extract company/fund - look for text after @ symbol in the next element after h3
                company = ""
                next_elem = heading.find_next_sibling()
                if next_elem:
                    next_text = next_elem.get_text(strip=True)
                    if '@' in next_text:
                        # Extract company name after @
                        parts = next_text.split('@')
                        if len(parts) > 1:
                            company_part = parts[1].strip()
                            # Clean up the company name
                            company = company_part.split('\n')[0].split('Angel')[0].strip()

                # If no company found, look for strong elements in the container
                if not company:
                    strong_elems = investor_container.find_all('strong')
                    for elem in strong_elems:
                        text = elem.get_text(strip=True)
                        if text and text != name and len(text) > 2 and '@' not in text:
                            company = text
                            break

                # Extract description - look for the description field first, then fallback to paragraphs
                description = ""

                # First try to find the description field by attribute
                desc_elem = investor_container.find(attrs={'fs-cmsfilter-field': 'Description'})
                if desc_elem:
                    description = desc_elem.get_text(strip=True)

                # If no description found, look for longer text blocks in paragraphs
                if not description:
                    paragraphs = investor_container.find_all('p')
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if len(text) > 50 and not any(skip in text.lower() for skip in ['website', 'dms open', 'view profile', 'linkedin', 'twitter']):
                            description = text
                            break

                # Extract contact information and social media accounts
                email = ""
                linkedin = ""
                twitter = ""
                website = ""
                crunchbase = ""
                youtube = ""
                personal_website = ""

                links = investor_container.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '').strip()
                    if not href:
                        continue

                    if href.startswith('mailto:'):
                        # Extract email and clean it
                        email_part = href.replace('mailto:', '').split('?')[0]
                        if '@' in email_part and not email:  # Take the first valid email
                            email = email_part
                    elif 'linkedin.com' in href:
                        linkedin = href
                    elif 'twitter.com' in href or 'x.com' in href:
                        twitter = href
                    elif 'crunchbase.com' in href:
                        crunchbase = href
                    elif 'youtube.com' in href or 'youtu.be' in href:
                        youtube = href
                    elif href.startswith('http') and not any(social in href for social in ['linkedin', 'twitter', 'crunchbase', 'youtube', 'vcsheet.com']):
                        # This could be a personal website or company website
                        if not personal_website:
                            personal_website = href

                # Use personal_website as the main website if available
                website = personal_website

                # Extract investment focus and stages
                focus_areas = []
                stages = []

                # Look for common investment terms in the container text
                container_text = investor_container.get_text()
                text_lower = container_text.lower()

                # Investment stages
                stage_indicators = ['pre-seed', 'seed', 'series a', 'series b', 'series c', 'growth', 'late stage']
                for stage in stage_indicators:
                    if stage in text_lower:
                        stages.append(stage.title())

                # Focus areas
                focus_indicators = ['fintech', 'ai', 'ml', 'saas', 'b2b', 'b2c', 'healthcare', 'biotech', 'crypto', 'blockchain', 'enterprise', 'consumer', 'mobile', 'e-commerce', 'marketplace']
                for focus in focus_indicators:
                    if focus in text_lower:
                        focus_areas.append(focus.upper() if focus in ['ai', 'ml', 'b2b', 'b2c'] else focus.title())

                # Apply keyword filtering if specified
                if keywords:
                    search_text = f"{name} {company} {description} {' '.join(focus_areas)} {' '.join(stages)}".lower()
                    if not any(keyword.lower() in search_text for keyword in keywords):
                        continue

                investor = {
                    "name": name,
                    "company": company,
                    "website": website,
                    "description": description,
                    "focus": ", ".join(focus_areas),
                    "location": "",  # Would need more specific parsing
                    "stage": ", ".join(stages),
                    "email": email,
                    "linkedin": linkedin,
                    "twitter": twitter,
                    "crunchbase": crunchbase,
                    "youtube": youtube,
                    "check_size": ""  # Would need more specific parsing
                }

                investors.append(investor)
                logger.debug(f"Parsed investor: {name} @ {company}")

                # Add a small delay to avoid overloading the server
                time.sleep(random.uniform(0.1, 0.3))

            except Exception as e:
                logger.error(f"Error parsing investor container: {e}")
                continue

        return investors

    def _is_investor_container(self, element) -> bool:
        """Check if an element is likely to be an investor container"""
        if not element:
            return False

        # Look for elements that contain typical investor information
        text = element.get_text().lower()
        has_contact = any(contact in text for contact in ['mailto:', 'linkedin', 'twitter'])
        has_role = any(role in text for role in ['partner', 'founder', 'investor', 'managing', 'general'])
        has_reasonable_length = len(text) > 100  # Should have substantial content

        return has_contact and has_role and has_reasonable_length

    def save_to_csv(self, investors: List[Dict], filename: str) -> None:
        """
        Save investor data to a CSV file

        Args:
            investors: List of investor dictionaries
            filename: Output CSV filename
        """
        if not investors:
            logger.warning("No investors to save")
            return

        fieldnames = [
            "name", "company", "website", "description", "focus", "location",
            "stage", "email", "linkedin", "twitter", "crunchbase", "youtube", "check_size"
        ]

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(investors)

            logger.info(f"Successfully saved {len(investors)} investors to {filename}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            raise

    def save_to_odoo_csv(self, investors: List[Dict], filename: str) -> None:
        """
        Save investors data to Odoo CRM leads compatible CSV file using investor_contacts.csv structure.

        Args:
            investors: List of investor dictionaries
            filename: Output CSV filename for Odoo import
        """
        if not investors:
            logger.warning("No investors to save")
            return

        try:
            # Use the same structure as investor_contacts.csv
            fieldnames = [
                "External ID",
                "Name",
                "Company Name",
                "Contact Name",
                "Email",
                "Job Position",
                "Phone",
                "Mobile",
                "Street",
                "Street2",
                "City",
                "State",
                "Zip",
                "Country",
                "Website",
                "Notes"
            ]

            odoo_investors = []
            for i, investor in enumerate(investors, 1):
                # Create comprehensive notes with all information
                notes_parts = []

                # Add company and basic info
                if investor.get('company'):
                    notes_parts.append(f"Company: {investor.get('company')}")

                # Add focus areas
                if investor.get('focus'):
                    notes_parts.append(f"Focus Areas: {investor.get('focus')}")

                # Add investment stages
                if investor.get('stage'):
                    notes_parts.append(f"Investment Stages: {investor.get('stage')}")

                # Add description if available
                if investor.get('description'):
                    notes_parts.append(f"Bio: {investor.get('description')}")

                # Add check size if available
                if investor.get('check_size'):
                    notes_parts.append(f"Check Size: {investor.get('check_size')}")

                # Add social media and contact links
                social_links = []
                if investor.get('linkedin'):
                    social_links.append(f"LinkedIn: {investor.get('linkedin')}")
                if investor.get('twitter'):
                    social_links.append(f"Twitter: {investor.get('twitter')}")
                if investor.get('crunchbase'):
                    social_links.append(f"Crunchbase: {investor.get('crunchbase')}")
                if investor.get('youtube'):
                    social_links.append(f"YouTube: {investor.get('youtube')}")

                if social_links:
                    notes_parts.append("Social Media & Links:")
                    notes_parts.extend(social_links)

                # Add source information
                notes_parts.append("Source: VCSheet.com")

                # Join all notes with semicolons and line breaks for readability
                notes = "; ".join(notes_parts)

                # Map our data to the investor_contacts.csv structure
                odoo_lead = {
                    "External ID": str(i),
                    "Name": investor.get('name', ''),
                    "Company Name": investor.get('company', ''),
                    "Contact Name": investor.get('name', ''),
                    "Email": investor.get('email', ''),
                    "Job Position": "Investor",
                    "Phone": "",  # Not available in our data
                    "Mobile": "",  # Not available in our data
                    "Street": "",  # Not available in our data
                    "Street2": "",  # Not available in our data
                    "City": "",  # Could be extracted from location if available
                    "State": "",  # Not available in our data
                    "Zip": "",  # Not available in our data
                    "Country": "",  # Not available in our data
                    "Website": investor.get('website', ''),
                    "Notes": notes
                }
                odoo_investors.append(odoo_lead)

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(odoo_investors)

            logger.info(f"Successfully saved {len(odoo_investors)} Odoo-compatible leads to {filename}")
        except Exception as e:
            logger.error(f"Error saving to Odoo CSV: {e}")
            raise


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration"""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Scrape investor data from vcsheet.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Save to CSV
  python scraper.py -o investors.csv
  python scraper.py -k "fintech" "AI" -o fintech_investors.csv
  python scraper.py -k "seed" -o seed_investors.csv --log-level DEBUG

  # Save Odoo-compatible CSV
  python scraper.py -k "fintech" -o odoo_leads.csv --odoo

  # Upload directly to Odoo via API
  python scraper.py -k "marketing" --odoo-upload --odoo-url "http://localhost:8069" --odoo-db "mydb" --odoo-user "admin" --odoo-password "admin"

  # Upload to Odoo with specific settings
  python scraper.py -k "fintech" --odoo-upload --odoo-url "https://mycompany.odoo.com" --odoo-db "production" --odoo-user "api_user" --odoo-password "api_key" --odoo-stage "New" --odoo-team "Sales Team"
        """
    )

    parser.add_argument(
        "-k", "--keywords",
        nargs="*",
        help="Keywords to filter investors (e.g., 'fintech', 'AI', 'seed')"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output CSV filename (optional when using --odoo-upload)"
    )

    parser.add_argument(
        "--odoo",
        action="store_true",
        help="Generate Odoo CRM leads compatible CSV format"
    )

    # Odoo API integration arguments
    parser.add_argument(
        "--odoo-upload",
        action="store_true",
        help="Upload data directly to Odoo via API (requires --odoo-url, --odoo-db, --odoo-user, --odoo-password)"
    )

    parser.add_argument(
        "--odoo-url",
        help="Odoo server URL (e.g., 'https://your-odoo.com' or 'http://localhost:8069')"
    )

    parser.add_argument(
        "--odoo-db",
        help="Odoo database name"
    )

    parser.add_argument(
        "--odoo-user",
        help="Odoo username"
    )

    parser.add_argument(
        "--odoo-password",
        help="Odoo password or API key"
    )

    parser.add_argument(
        "--odoo-model",
        choices=["crm.lead", "res.partner"],
        default="crm.lead",
        help="Odoo model to create records in (default: crm.lead)"
    )

    parser.add_argument(
        "--odoo-stage",
        help="Default pipeline stage for leads (e.g., 'New', 'Qualified')"
    )

    parser.add_argument(
        "--odoo-team",
        help="Default sales team to assign leads to"
    )

    parser.add_argument(
        "--odoo-user-assign",
        help="Default user to assign leads to"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )

    return parser.parse_args()


def main() -> None:
    """Main function to run the scraper from command line"""
    try:
        args = parse_arguments()
        setup_logging(args.log_level)

        # Validate arguments
        if not args.odoo_upload and not args.output:
            logger.error("Output filename (-o) is required when not using --odoo-upload")
            sys.exit(1)

        logger.info("Starting VC Sheet scraper...")

        # Create scraper instance
        scraper = VCSheetScraper()

        # Scrape investors
        if args.keywords:
            logger.info(f"Searching for investors with keywords: {', '.join(args.keywords)}")
            investors = scraper.get_investors(keywords=args.keywords)
        else:
            logger.info("Scraping all investors...")
            investors = scraper.get_investors()

        if not investors:
            logger.warning("No investors found")
            return

        logger.info(f"Found {len(investors)} investors")

        # Handle output options
        if args.odoo_upload:
            # Validate required Odoo parameters
            if not all([args.odoo_url, args.odoo_db, args.odoo_user, args.odoo_password]):
                logger.error("Odoo upload requires --odoo-url, --odoo-db, --odoo-user, and --odoo-password")
                sys.exit(1)

            # Upload to Odoo via API
            logger.info("Uploading data directly to Odoo via API...")
            odoo_api = OdooAPI(args.odoo_url, args.odoo_db, args.odoo_user, args.odoo_password)

            # Test connection and authenticate
            if not odoo_api.test_connection():
                logger.error("Failed to connect to Odoo server")
                sys.exit(1)

            if not odoo_api.authenticate():
                logger.error("Failed to authenticate with Odoo")
                sys.exit(1)

            # Upload investors
            created_ids = odoo_api.create_leads(
                investors,
                model=args.odoo_model,
                default_stage=args.odoo_stage,
                default_team=args.odoo_team,
                default_user=args.odoo_user_assign
            )

            logger.info(f"Successfully uploaded {len(created_ids)} investors to Odoo!")

            # Also save CSV if output file specified
            if args.output:
                if args.odoo:
                    logger.info("Also saving Odoo-compatible CSV...")
                    scraper.save_to_odoo_csv(investors, args.output)
                else:
                    logger.info("Also saving regular CSV...")
                    scraper.save_to_csv(investors, args.output)

        elif args.odoo:
            logger.info("Saving in Odoo CRM leads compatible format...")
            scraper.save_to_odoo_csv(investors, args.output)
        else:
            scraper.save_to_csv(investors, args.output)

        logger.info("Scraping completed successfully!")

    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()