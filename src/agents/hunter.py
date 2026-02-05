"""Hunter agent - scrapes LinkedIn and web for lead generation."""
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from src.agents.base import BaseAgent
from src.database.models import Lead, LeadStatus
from src.database.database import get_db
from src.services import playwright_scraper, gemini_service
from src.utils import validate_linkedin_url, extract_domain_from_url, infer_email_pattern
from src.utils.logger import logger


class HunterAgent(BaseAgent):
    """
    Hunter agent that finds and qualifies leads through web scraping.
    
    Workflow:
    1. Search LinkedIn for target companies/people
    2. Scrape LinkedIn profiles
    3. Scrape company websites
    4. Score leads with AI
    5. Create lead records in database
    """
    
    def __init__(self):
        """Initialize Hunter agent."""
        super().__init__(name="Hunter")
    
    async def execute(
        self,
        campaign_id: str,
        search_query: str,
        max_leads: int = 10,
        region: str = "Eastern_Europe",
    ) -> list[str]:
        """
        Hunt for leads based on search criteria.
        
        Args:
            campaign_id: Campaign ID to associate leads with
            search_query: LinkedIn search query (e.g., "wine importer Poland")
            max_leads: Maximum number of leads to generate
            region: Target region for rate limiting
            
        Returns:
            List of created lead IDs
        """
        logger.info(
            "hunter_starting",
            campaign_id=campaign_id,
            query=search_query,
            max_leads=max_leads,
        )
        
        created_leads = []
        
        try:
            # Start browser
            await playwright_scraper.start()
            
            # Step 1: Search LinkedIn
            logger.info("hunter_searching_linkedin", query=search_query)
            profile_urls = await playwright_scraper.linkedin_search(
                search_query=search_query,
                max_results=max_leads,
                region=region,
            )
            
            if not profile_urls:
                logger.warning("hunter_no_results", query=search_query)
                return created_leads
            
            # Step 2: Process each profile
            for profile_url in profile_urls:
                try:
                    lead_id = await self._process_profile(
                        campaign_id=campaign_id,
                        profile_url=profile_url,
                        region=region,
                    )
                    
                    if lead_id:
                        created_leads.append(lead_id)
                    
                except Exception as e:
                    logger.error(
                        "hunter_profile_failed",
                        profile_url=profile_url,
                        error=str(e),
                    )
                    continue
            
            logger.info(
                "hunter_complete",
                campaign_id=campaign_id,
                leads_created=len(created_leads),
            )
            
            return created_leads
            
        except Exception as e:
            logger.error(
                "hunter_failed",
                campaign_id=campaign_id,
                error=str(e),
            )
            raise
        
        finally:
            # Stop browser
            await playwright_scraper.stop()
    
    async def _process_profile(
        self,
        campaign_id: str,
        profile_url: str,
        region: str,
    ) -> Optional[str]:
        """
        Process a single LinkedIn profile and create lead.
        
        Args:
            campaign_id: Campaign ID
            profile_url: LinkedIn profile URL
            region: Target region
            
        Returns:
            Lead ID if created, None otherwise
        """
        logger.info("hunter_processing_profile", url=profile_url)
        
        # Scrape LinkedIn profile
        profile_data = await playwright_scraper.scrape_linkedin_profile(
            profile_url=profile_url,
            region=region,
        )
        
        # Extract company info
        company_name = profile_data.get('company', 'Unknown Company')
        decision_maker_name = profile_data.get('name', '')
        decision_maker_title = profile_data.get('title', '')
        location = profile_data.get('location', '')
        
        if not company_name or company_name == 'Unknown Company':
            logger.warning("hunter_no_company", profile_url=profile_url)
            return None
        
        # Try to find company website
        # In real implementation, you'd search for company LinkedIn page
        # For now, we'll infer from company name
        company_domain = f"{company_name.lower().replace(' ', '')}.com"
        website_url = f"https://{company_domain}"
        
        # Scrape company website
        website_content = await playwright_scraper.scrape_company_website(website_url)
        
        # Infer emails
        domain = extract_domain_from_url(website_url)
        inferred_emails = infer_email_pattern(domain, decision_maker_name) if domain else []
        
        # Score lead with AI
        logger.info("hunter_scoring_lead", company=company_name)
        fit_score = await gemini_service.score_lead(
            company_name=company_name,
            website_content=website_content,
            metadata={
                "location": location,
                "decision_maker": f"{decision_maker_name} ({decision_maker_title})",
                "linkedin_profile": profile_url,
            },
        )
        
        # Create lead in database
        lead_id = str(uuid.uuid4())
        
        with get_db() as db:
            lead = Lead(
                id=lead_id,
                campaign_id=campaign_id,
                company_name=company_name,
                website=website_url,
                location=location,
                employee_count=None,  # Would extract from LinkedIn company page
                decision_maker_name=decision_maker_name,
                decision_maker_title=decision_maker_title,
                decision_maker_linkedin=profile_url,
                office_phone=None,
                inferred_emails=inferred_emails,
                fit_score=fit_score,
                status=LeadStatus.PENDING,
                extra_data={
                    "website_content": website_content[:2000],  # Store sample
                    "linkedin_posts": '\n'.join(profile_data.get('recent_posts', [])[:3]),
                    "about": profile_data.get('about', ''),
                },
                created_at=datetime.utcnow(),
            )
            db.add(lead)
            db.commit()
        
        # Log activity
        await self.log_activity(
            lead_id=lead_id,
            action="scraped_and_scored",
            details={
                "profile_url": profile_url,
                "company": company_name,
                "fit_score": fit_score,
                "inferred_emails_count": len(inferred_emails),
            },
        )
        
        logger.info(
            "hunter_lead_created",
            lead_id=lead_id,
            company=company_name,
            fit_score=fit_score,
        )
        
        return lead_id


# Global agent instance
hunter_agent = HunterAgent()
