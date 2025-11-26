"""
Web scraping utilities for extracting quiz content
"""
import asyncio
import logging
import base64
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class QuizScraper:
    """Handles web scraping with JavaScript rendering support"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
    
    async def __aenter__(self):
        """Context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup browser"""
        await self.close()
    
    async def initialize_browser(self):
        """Initialize headless browser"""
        if self.browser is None:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
            logger.info("Browser initialized")
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            logger.info("Browser closed")
    
    async def fetch_quiz_content(self, url: str, wait_time: int = 3000) -> Dict[str, Any]:
        """
        Fetch quiz content from URL with JavaScript rendering
        
        Args:
            url: The quiz URL
            wait_time: Time to wait for JavaScript execution (ms)
        
        Returns:
            Dictionary with quiz content and metadata
        """
        try:
            await self.initialize_browser()
            
            # Create new page
            page = await self.browser.new_page()
            
            # Navigate to URL
            logger.info(f"Fetching quiz from: {url}")
            await page.goto(url, wait_until="networkidle")
            
            # Wait for dynamic content to load
            await asyncio.sleep(wait_time / 1000)
            
            # Get page content
            html_content = await page.content()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract text content
            text_content = soup.get_text(separator='\n', strip=True)
            
            # Look for base64 encoded content (common pattern in quizzes)
            base64_matches = self._extract_base64_content(html_content)
            
            # Look for submit URL in the content
            submit_url = self._extract_submit_url(html_content, text_content)
            
            # Look for file download links
            download_links = self._extract_download_links(soup, url)
            
            # Get all script tags content
            scripts = [script.string for script in soup.find_all('script') if script.string]
            
            await page.close()
            
            result = {
                'url': url,
                'html': html_content,
                'text': text_content,
                'submit_url': submit_url,
                'download_links': download_links,
                'base64_content': base64_matches,
                'scripts': scripts
            }
            
            logger.info(f"Successfully fetched quiz content from {url}")
            logger.info(f"Found submit URL: {submit_url}")
            logger.info(f"Found {len(download_links)} download links")
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching quiz content: {e}", exc_info=True)
            raise
    
    def _extract_base64_content(self, html: str) -> list:
        """Extract base64 encoded content from HTML"""
        # Look for atob() calls or base64 strings
        base64_pattern = r'atob\(["\']([A-Za-z0-9+/=]+)["\']\)'
        matches = re.findall(base64_pattern, html)
        
        decoded = []
        for match in matches:
            try:
                decoded_content = base64.b64decode(match).decode('utf-8')
                decoded.append({
                    'encoded': match,
                    'decoded': decoded_content
                })
            except Exception as e:
                logger.warning(f"Failed to decode base64: {e}")
        
        return decoded
    
    def _extract_submit_url(self, html: str, text: str) -> Optional[str]:
        """Extract submission URL from content"""
        # Look for URLs in common patterns
        patterns = [
            r'(?:POST|post|submit|POST your answer to)\s+(?:to\s+)?(https?://[^\s<>"]+)',
            r'submit["\s]+(?:to|at|url)?["\s:]+["\']?(https?://[^\s<>"\']+)',
            r'"submit_url"?\s*:\s*"(https?://[^"]+)"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).rstrip('.,;)')
        
        # Fallback: look for any URL that contains "submit"
        submit_urls = re.findall(r'https?://[^\s<>"]+submit[^\s<>"]*', text, re.IGNORECASE)
        if submit_urls:
            return submit_urls[0].rstrip('.,;)')
        
        return None
    
    def _extract_download_links(self, soup: BeautifulSoup, base_url: str) -> list:
        """Extract download links from page"""
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Look for file extensions or download indicators
            if any(ext in href.lower() for ext in ['.pdf', '.csv', '.xlsx', '.json', '.txt', '.zip', 'download']):
                # Handle relative URLs
                if href.startswith('http'):
                    links.append(href)
                elif href.startswith('/'):
                    # Extract domain from base_url
                    domain = re.match(r'(https?://[^/]+)', base_url)
                    if domain:
                        links.append(domain.group(1) + href)
                else:
                    # Relative to current path
                    links.append(base_url.rsplit('/', 1)[0] + '/' + href)
        
        return links


async def fetch_quiz_content_simple(url: str) -> Dict[str, Any]:
    """
    Simple helper function to fetch quiz content
    
    Args:
        url: Quiz URL
    
    Returns:
        Quiz content dictionary
    """
    async with QuizScraper() as scraper:
        return await scraper.fetch_quiz_content(url)


def fetch_quiz_sync(url: str) -> Dict[str, Any]:
    """
    Synchronous wrapper for fetching quiz content
    
    Args:
        url: Quiz URL
    
    Returns:
        Quiz content dictionary
    """
    return asyncio.run(fetch_quiz_content_simple(url))
