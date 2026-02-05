"""
Hunter Agent v2.0 - Google OSINT Search Strategy

RETIRED: LinkedIn web scraping (TOS violation, unreliable)
NEW: Advanced Google search with OSINT protocols

This agent uses sophisticated Google search operators to find high-quality leads
in countries with full diplomatic trade relations with Israel.
"""

import asyncio
from typing import List, Dict, Any
from src.database.models import Lead, LeadStatus, PainPoint
from src.database.database import get_db
from src.services.llm_service import gemini_service
from src.utils.logger import logger
from src.utils.rate_limiter import linkedin_rate_limiter  # Reuse for Google API
import uuid


# OSINT Search Protocols
OSINT_PROTOCOLS = {
    "portfolio_match": {
        "name": "Portfolio Match (Hidden Web)",
        "query_template": 'filetype:pdf "wine portfolio" ("Israel" OR "Kosher") site:.{country_code}',
        "description": "Finds importers with PDF catalogs showing Israeli/Kosher wine expertise"
    },
    "direct_executive": {
        "name": "Direct Executive (Decision Maker)",
        "query_template": 'site:linkedin.com/in/ ("Wine Importer" OR "Distributor" OR "CEO") ("{country_name}") -intitle:jobs',
        "description": "Finds wine industry executives in target country"
    },
    "official_entity": {
        "name": "Official Entity (Vivino Related)",
        "query_template": 'related:vivino.com "wine importer" "{country_name}"',
        "description": "Finds major wine distributors recognized by Vivino"
    },
    "competitor_piggyback": {
        "name": "Competitor Piggyback",
        "query_template": '"imported by" ("Yarden" OR "Golan Heights" OR "Recanati" OR "Teperberg") site:.{country_code}',
        "description": "Finds existing Israeli wine importers"
    }
}

# Countries with full Israel trade relations
APPROVED_COUNTRIES = {
    "Poland": {"code": "pl", "name": "Poland"},
    "Romania": {"code": "ro", "name": "Romania"},
    "Czech Republic": {"code": "cz", "name": "Czech Republic"},
    "Japan": {"code": "jp", "name": "Japan"},
    "South Korea": {"code": "kr", "name": "South Korea"},
}


class HunterAgentV2:
    """
    Hunter Agent v2.0 - Google OSINT Search Implementation
    
    Uses advanced Google search operators instead of LinkedIn scraping.
    Completely legal, compliant, and more effective.
    """
    
    def __init__(self, search_function):
        """
        Initialize Hunter v2.0
        
        Args:
            search_function: Function to perform web searches (e.g., search_web tool)
        """
        self.search = search_function
        self.gemini = gemini_service
        logger.info("hunter_v2_initialized", version="2.0", method="google_osint")
    
    async def execute_protocol(
        self,
        protocol_name: str,
        country: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        """
        Execute a single OSINT protocol for a country.
        
        Args:
            protocol_name: Name of protocol from OSINT_PROTOCOLS
            country: Country info dict with 'code' and 'name'
            
        Returns:
            List of search results
        """
        protocol = OSINT_PROTOCOLS[protocol_name]
        
        # Build query from template
        query = protocol["query_template"].format(
            country_code=country.get("code", ""),
            country_name=country.get("name", "")
        )
        
        logger.info(
            "osint_search_starting",
            protocol=protocol_name,
            country=country["name"],
            query=query
        )
        
        try:
            # Execute search using the search_web tool
            result = await self.search(query)
            
            logger.info(
                "osint_search_complete",
                protocol=protocol_name,
                country=country["name"],
                results_found=len(result) if isinstance(result, list) else 1
            )
            
            return {
                "protocol": protocol_name,
                "country": country["name"],
                "query": query,
                "raw_result": result
            }
            
        except Exception as e:
            logger.error(
                "osint_search_failed",
                protocol=protocol_name,
                country=country["name"],
                error=str(e)
            )
            return {
                "protocol": protocol_name,
                "country": country["name"],
                "query": query,
                "error": str(e)
            }
    
    async def search_all_countries(self) -> List[Dict[str, Any]]:
        """
        Execute all OSINT protocols across all approved countries.
        
        Returns:
            List of all search results
        """
        all_results = []
        
        for country_name, country_info in APPROVED_COUNTRIES.items():
            logger.info("country_search_starting", country=country_name)
            
            for protocol_name in OSINT_PROTOCOLS.keys():
                result = await self.execute_protocol(protocol_name, country_info)
                all_results.append(result)
                
                # Rate limiting - be respectful to Google
                await asyncio.sleep(2)  # 2 second delay between searches
            
            logger.info("country_search_complete", country=country_name)
        
        return all_results
    
    async def parse_results_to_leads(
        self,
        search_results: List[Dict[str, Any]],
        campaign_id: str
    ) -> List[str]:
        """
        Parse raw search results into Lead records using Gemini AI.
        
        Args:
            search_results: Raw search results from OSINT protocols
            campaign_id: Campaign ID to associate leads with
            
        Returns:
            List of created lead IDs
        """
        leads_created = []
        
        with get_db() as db:
            for result in search_results:
                if "error" in result:
                    continue
                
                # Use Gemini to extract structured data from search result
                try:
                    prompt = f"""Extract lead information from this search result.

Protocol: {result['protocol']}
Country: {result['country']}
Search Result: {result['raw_result']}

Extract:
1. Company name
2. Website URL (must exist)
3. Decision maker name and title (if available)
4. Relevance score/reason (why this is a good lead)

Return as JSON with keys: company_name, website, decision_maker_name, decision_maker_title, relevance_score
If you can't extract clean data, return {{"skip": true}}
"""
                    
                    extracted = await self.gemini.generate_text(prompt, temperature=0.3)
                    
                    # TODO: Parse JSON and create Lead record
                    # This is a placeholder - needs proper JSON parsing
                    
                    logger.info("lead_extracted", result=extracted[:100])
                    
                except Exception as e:
                    logger.error("lead_extraction_failed", error=str(e))
                    continue
        
        return leads_created


# Global instance (replaces old hunter_agent)
hunter_agent_v2 = None  # Will be initialized with search function
