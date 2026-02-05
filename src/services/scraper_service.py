"""Web scraper service using Playwright with stealth mode."""
import asyncio
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from src.utils.logger import logger
from src.utils.rate_limiter import linkedin_rate_limiter


class PlaywrightScraper:
    """
    Playwright-based web scraper with stealth mode for anti-detection.
    Optimized for LinkedIn Premium (40 profiles/day, 10/hour).
    """
    
    def __init__(self):
        """Initialize scraper."""
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
    
    async def start(self) -> None:
        """Start browser with stealth configuration."""
        if self.browser:
            return  # Already started
        
        self.playwright = await async_playwright().start()
        
        # Launch Chromium with stealth settings
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Set to True for production
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
            ],
        )
        
        # Create context with stealth settings
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
        )
        
        # Additional stealth: Remove webdriver flags
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            window.chrome = {
                runtime: {}
            };
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        logger.info("playwright_started", headless=False)
    
    async def stop(self) -> None:
        """Stop browser and cleanup."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        logger.info("playwright_stopped")
    
    async def create_page(self) -> Page:
        """Create a new page in the browser context."""
        if not self.context:
            await self.start()
        
        page = await self.context.new_page()
        return page
    
    async def scrape_linkedin_profile(
        self,
        profile_url: str,
        region: str = "Eastern_Europe",
    ) -> Dict[str, Any]:
        """
        Scrape a LinkedIn profile.
        
        Args:
            profile_url: LinkedIn profile URL
            region: Region for rate limiting
            
        Returns:
            Extracted profile data
        """
        # Apply rate limiting
        await linkedin_rate_limiter.acquire(region=region)
        
        page = await self.create_page()
        
        try:
            logger.info("scraping_linkedin_profile", url=profile_url)
            
            # Navigate to profile
            await page.goto(profile_url, wait_until='networkidle', timeout=30000)
            
            # Wait for DOM and additional JS rendering
            await page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(1)
            
            # Wait for profile content to load with increased timeout
            await page.wait_for_selector('.pv-top-card', timeout=15000)
            
            # Extract data
            data = await page.evaluate("""
                () => {
                    const getTextContent = (selector) => {
                        const el = document.querySelector(selector);
                        return el ? el.textContent.trim() : '';
                    };
                    
                    return {
                        name: getTextContent('.pv-top-card--list li:first-child'),
                        title: getTextContent('.text-body-medium.break-words'),
                        company: getTextContent('.pv-text-details__right-panel .hoverable-link-text'),
                        location: getTextContent('.pv-top-card--list.pv-top-card--list-bullet li:first-child'),
                        about: getTextContent('.pv-about__summary-text'),
                    };
                }
            """)
            
            # Extract additional posts/activity if available
            posts = []
            try:
                await page.wait_for_selector('.feed-shared-update-v2', timeout=5000)
                posts_data = await page.evaluate("""
                    () => {
                        const postElements = document.querySelectorAll('.feed-shared-update-v2');
                        return Array.from(postElements).slice(0, 5).map(post => {
                            return post.textContent.trim();
                        });
                    }
                """)
                posts = posts_data
            except:
                logger.info("no_posts_found", url=profile_url)
            
            data['recent_posts'] = posts
            
            logger.info(
                "linkedin_profile_scraped",
                url=profile_url,
                name=data.get('name'),
            )
            
            return data
            
        except Exception as e:
            logger.error("linkedin_scrape_failed", url=profile_url, error=str(e))
            raise
        
        finally:
            await page.close()
    
    async def scrape_company_website(
        self,
        url: str,
    ) -> str:
        """
        Scrape company website content.
        
        Args:
            url: Company website URL
            
        Returns:
            Extracted text content
        """
        page = await self.create_page()
        
        try:
            logger.info("scraping_website", url=url)
            
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Extract main text content
            content = await page.evaluate("""
                () => {
                    // Remove scripts, styles, hidden elements
                    const elementsToRemove = document.querySelectorAll('script, style, [hidden]');
                    elementsToRemove.forEach(el => el.remove());
                    
                    // Get body text
                    return document.body.innerText;
                }
            """)
            
            # Clean and truncate
            content = ' '.join(content.split())  # Normalize whitespace
            content = content[:5000]  # Limit to first 5000 chars
            
            logger.info(
                "website_scraped",
                url=url,
                content_length=len(content),
            )
            
            return content
            
        except Exception as e:
            logger.error("website_scrape_failed", url=url, error=str(e))
            return ""
        
        finally:
            await page.close()
    
    async def linkedin_search(
        self,
        search_query: str,
        max_results: int = 10,
        region: str = "Eastern_Europe",
    ) -> List[str]:
        """
        Search LinkedIn for companies/profiles with robust selector fallbacks.
        
        Args:
            search_query: Search query (e.g., "wine importer Poland")
            max_results: Maximum number of results to return
            region: Region for rate limiting
            
        Returns:
            List of profile/company URLs
        """
        # Apply rate limiting for search
        await linkedin_rate_limiter.acquire(region=region)
        
        page = await self.create_page()
        
        try:
            logger.info("linkedin_search", query=search_query, max_results=max_results)
            
            # Navigate to LinkedIn search
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query.replace(' ', '%20')}"
            await page.goto(search_url, wait_until='networkidle', timeout=30000)
            
            # Wait for DOM to be fully loaded
            await page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(2)  # Additional buffer for JS rendering
            
            # Try multiple selectors with fallback strategy
            selectors_to_try = [
                '.reusable-search__result-container',  # Original selector
                '[data-view-name="search-entity-result"]',  # Data attribute
                '.entity-result',  # Simplified class
                'li.reusable-search__result-container',  # With tag
                'ul.reusable-search__entity-result-list li',  # Parent-child
                'main[role="main"] ul li',  # Semantic fallback
            ]
            
            results_selector = None
            for selector in selectors_to_try:
                try:
                    await page.wait_for_selector(selector, timeout=5000, state='visible')
                    results_selector = selector
                    logger.info("linkedin_selector_found", selector=selector)
                    break
                except:
                    logger.debug("linkedin_selector_failed", selector=selector)
                    continue
            
            if not results_selector:
                # Last resort: use Playwright Locator API
                logger.info("trying_locator_api")
                try:
                    results_locator = page.locator('main').locator('ul').first
                    await results_locator.wait_for(state='visible', timeout=10000)
                    results_selector = 'main ul li'  # Fallback to generic
                except:
                    raise Exception("No search results container found with any selector")
            
            # Extract profile URLs with retry logic
            urls = await page.evaluate(f"""
                (maxResults) => {{
                    // Try multiple selectors to find results
                    let results = document.querySelectorAll('.reusable-search__result-container');
                    if (results.length === 0) {{
                        results = document.querySelectorAll('[data-view-name="search-entity-result"]');
                    }}
                    if (results.length === 0) {{
                        results = document.querySelectorAll('.entity-result');
                    }}
                    if (results.length === 0) {{
                        results = document.querySelectorAll('main ul li');
                    }}
                    
                    const urls = [];
                    
                    for (let i = 0; i < Math.min(results.length, maxResults); i++) {{
                        // Try multiple link selectors
                        let link = results[i].querySelector('a.app-aware-link');
                        if (!link) link = results[i].querySelector('a[href*="/in/"]');
                        if (!link) link = results[i].querySelector('a');
                        
                        if (link && link.href && link.href.includes('/in/')) {{
                            urls.push(link.href.split('?')[0]);
                        }}
                    }}
                    
                    return urls;
                }}
            """, max_results)
            
            logger.info(
                "linkedin_search_complete",
                query=search_query,
                results_found=len(urls),
                selector_used=results_selector,
            )
            
            return urls
            
        except Exception as e:
            logger.error("linkedin_search_failed", query=search_query, error=str(e))
            return []
        
        finally:
            await page.close()


# Global scraper instance
playwright_scraper = PlaywrightScraper()
