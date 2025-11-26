"""
Web Scraper Module
Handles scraping of JavaScript-rendered quiz pages using Playwright
"""
import logging
import re
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)

class QuizScraper:
    """Scrapes quiz content from JavaScript-rendered pages"""
    
    def __init__(self):
        self.browser = None
        self.context = None
    
    async def fetch_quiz_content(self, url: str) -> Dict[str, Any]:
        """
        Fetch and parse quiz content from URL
        
        Args:
            url: Quiz page URL
            
        Returns:
            Dictionary containing:
                - question: The quiz question text
                - submit_url: URL to submit answers
                - download_links: Any file download links
        """
        try:
            logger.info(f"Fetching quiz from: {url}")
            
            async with async_playwright() as p:
                # Launch browser in headless mode
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                # Navigate to quiz page
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for content to render
                await page.wait_for_timeout(2000)
                
                # Get page content
                content = await page.content()
                
                # Extract text content
                body_text = await page.evaluate('() => document.body.innerText')
                
                # Extract any base64 decoded content
                decoded_content = await self._extract_base64_content(page)
                if decoded_content:
                    body_text = decoded_content
                
                # Extract submit URL
                submit_url = await self._extract_submit_url(content, body_text)
                
                # Extract download links
                download_links = await self._extract_download_links(page)
                
                await browser.close()
                
                result = {
                    "question": body_text.strip(),
                    "submit_url": submit_url,
                    "download_links": download_links,
                    "html": content
                }
                
                logger.info(f"Successfully extracted quiz content ({len(body_text)} chars)")
                return result
                
        except PlaywrightTimeout:
            logger.error(f"Timeout fetching quiz from {url}")
            return {"question": "", "submit_url": "", "download_links": []}
        except Exception as e:
            logger.error(f"Error fetching quiz content: {e}", exc_info=True)
            return {"question": "", "submit_url": "", "download_links": []}
    
    async def _extract_base64_content(self, page) -> Optional[str]:
        """
        Extract content decoded from base64 (atob) in JavaScript
        
        Args:
            page: Playwright page object
            
        Returns:
            Decoded content or None
        """
        try:
            # Try to find result div or similar containers
            result_divs = await page.query_selector_all('#result, .result, [id*="result"]')
            
            for div in result_divs:
                content = await div.inner_text()
                if content.strip():
                    logger.info("Found decoded content in result container")
                    return content
            
            # If no result div, check if page has executed atob
            decoded = await page.evaluate('''
                () => {
                    const elements = document.querySelectorAll('*');
                    for (let elem of elements) {
                        const text = elem.innerText;
                        if (text && text.length > 50 && !elem.querySelector('*')) {
                            return text;
                        }
                    }
                    return null;
                }
            ''')
            
            if decoded:
                logger.info("Found decoded content via JavaScript evaluation")
                return decoded
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting base64 content: {e}")
            return None
    
    async def _extract_submit_url(self, html: str, text: str) -> str:
        """
        Extract submission URL from page content
        
        Args:
            html: Raw HTML content
            text: Rendered text content
            
        Returns:
            Submit URL or empty string
        """
        try:
            # Common patterns for submit URLs
            patterns = [
                r'(?:Post|Submit|Send).*?(?:to|at)[:\s]+(https?://[^\s<>"]+/submit[^\s<>"]*)',
                r'(?:POST|post)[^\n]*?(https?://[^\s<>"]+/submit[^\s<>"]*)',
                r'"submit"[:\s]+"(https?://[^\s<>"]+)"',
                r'submit.*?url["\']?\s*:\s*["\']([^"\']+)["\']',
                r'https?://[^\s<>"]+/submit[^\s<>"]*'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    url = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    logger.info(f"Found submit URL: {url}")
                    return url
            
            # Try HTML as well
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    url = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    logger.info(f"Found submit URL in HTML: {url}")
                    return url
            
            logger.warning("No submit URL found")
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting submit URL: {e}")
            return ""
    
    async def _extract_download_links(self, page) -> list:
        """
        Extract download links from page
        
        Args:
            page: Playwright page object
            
        Returns:
            List of download URLs
        """
        try:
            links = await page.query_selector_all('a[href*=".pdf"], a[href*=".csv"], a[href*=".xlsx"], a[href*="download"]')
            
            download_urls = []
            for link in links:
                href = await link.get_attribute('href')
                if href:
                    # Convert relative URLs to absolute
                    if href.startswith('http'):
                        download_urls.append(href)
                    else:
                        base_url = page.url
                        if href.startswith('/'):
                            download_urls.append(f"{base_url.rstrip('/')}{href}")
                        else:
                            download_urls.append(f"{base_url.rstrip('/')}/{href}")
            
            if download_urls:
                logger.info(f"Found {len(download_urls)} download links")
            
            return download_urls
            
        except Exception as e:
            logger.error(f"Error extracting download links: {e}")
            return []

# Synchronous wrapper for use in sync contexts
def fetch_quiz_sync(url: str) -> Dict[str, Any]:
    """Synchronous wrapper for fetch_quiz_content"""
    import asyncio
    scraper = QuizScraper()
    return asyncio.run(scraper.fetch_quiz_content(url))
