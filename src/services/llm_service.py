"""Gemini LLM service for lead scoring and email generation."""
import google.generativeai as genai
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.utils.logger import logger


class GeminiService:
    """Service for interacting with Google Gemini API."""
    
    def __init__(self):
        """Initialize Gemini service."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        logger.info("gemini_service_initialized", model="gemini-2.5-flash")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """
        Generate text using Gemini.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        try:
            logger.info(
                "gemini_request",
                prompt_length=len(prompt),
                temperature=temperature,
            )
            
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
            )
            
            result = response.text
            
            logger.info(
                "gemini_response",
                response_length=len(result),
            )
            
            return result
            
        except Exception as e:
            logger.error("gemini_error", error=str(e))
            raise
    
    async def score_lead(
        self,
        company_name: str,
        website_content: str,
        metadata: Dict[str, Any],
    ) -> float:
        """
        Score a lead's fit with Tulip Winery (0-10).
        
        Args:
            company_name: Company name
            website_content: Scraped website text
            metadata: Additional context
            
        Returns:
            Fit score (0-10)
        """
        prompt = f"""You are an expert B2B lead qualifier for Tulip Winery, a premium Israeli winery.

Tulip Winery's profile:
- Premium kosher wines from Galilee region
- Social mission: "Village of Hope" empowers at-risk youth
- AgTech innovation in winemaking
- Award-winning quality and unique terroir

Company to evaluate: {company_name}

Website content:
{website_content[:2000]}  # Limit to first 2000 chars

Additional context:
{metadata}

Task: Score this company's fit as a potential wine importer/distributor for Tulip Winery.

Consider:
1. Do they import premium wines? (New World, Mediterranean, or similar)
2. Do they value social impact/ESG initiatives?
3. Do they work with kosher wines or specialty markets?
4. Company size and market reach
5. Geographic location alignment with target regions

Respond with ONLY a number from 0-10 where:
- 0-3: Poor fit
- 4-6: Moderate fit
- 7-8: Good fit
- 9-10: Excellent fit

Score:"""
        
        try:
            response = await self.generate_text(prompt, temperature=0.3, max_tokens=10)
            score_str = response.strip()
            
            # Extract number from response
            score = float(''.join(c for c in score_str if c.isdigit() or c == '.'))
            score = max(0.0, min(10.0, score))  # Clamp to 0-10
            
            logger.info(
                "lead_scored",
                company=company_name,
                score=score,
            )
            
            return score
            
        except Exception as e:
            logger.error("lead_scoring_failed", company=company_name, error=str(e))
            return 5.0  # Default to middle score on error
    
    async def analyze_pain_points(
        self,
        company_name: str,
        website_content: str,
        linkedin_posts: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Analyze company's pain points and challenges.
        
        Args:
            company_name: Company name
            website_content: Scraped website text
            linkedin_posts: Recent LinkedIn posts/updates
            
        Returns:
            Dict with 'pain_point' (ESG/Innovation/Quality/Unknown) and 'evidence'
        """
        prompt = f"""Analyze this wine importer/distributor to identify their primary business challenge or focus area.

Company: {company_name}

Website content:
{website_content[:2000]}

LinkedIn activity:
{linkedin_posts[:500] if linkedin_posts else "N/A"}

Identify which category best describes their current focus:

1. **ESG** - Seeking sustainable, socially responsible, or ethical brands
   Evidence: Terms like "sustainable", "social impact", "ESG", "community", "ethical"

2. **Innovation** - Looking for cutting-edge, tech-forward, or unique products
   Evidence: Terms like "innovation", "technology", "precision", "AgTech", "new methods"

3. **Quality** - Focused on premium, award-winning, terroir-driven wines
   Evidence: Terms like "premium", "award-winning", "terroir", "quality", "excellence"

4. **Unknown** - Insufficient information to determine focus

Respond in this exact format:
CATEGORY: [ESG|Innovation|Quality|Unknown]
EVIDENCE: [1-2 sentence explanation with specific quotes if available]

Response:"""
        
        try:
            response = await self.generate_text(prompt, temperature=0.4, max_tokens=200)
            
            # Parse response
            lines = response.strip().split('\n')
            category = "Unknown"
            evidence = ""
            
            for line in lines:
                if line.startswith("CATEGORY:"):
                    category = line.split(":", 1)[1].strip()
                elif line.startswith("EVIDENCE:"):
                    evidence = line.split(":", 1)[1].strip()
            
            logger.info(
                "pain_point_analyzed",
                company=company_name,
                category=category,
            )
            
            return {
                "pain_point": category,
                "evidence": evidence,
            }
            
        except Exception as e:
            logger.error("pain_point_analysis_failed", company=company_name, error=str(e))
            return {"pain_point": "Unknown", "evidence": "Analysis failed"}
    
    async def generate_email(
        self,
        company_name: str,
        decision_maker_name: str,
        decision_maker_title: str,
        pain_point: str,
        evidence: str,
    ) -> Dict[str, str]:
        """
        Generate personalized email based on pain-point matching.
        
        Args:
            company_name: Company name
            decision_maker_name: Contact person
            decision_maker_title: Their title
            pain_point: Detected pain point category
            evidence: Supporting evidence
            
        Returns:
            Dict with 'subject', 'body', and 'tulip_asset_used'
        """
        # Map pain point to Tulip asset
        asset_mapping = {
            "ESG": {
                "asset": "Village_of_Hope",
                "pitch": "Tulip Winery's 'Village of Hope' social mission—empowering at-risk youth through winemaking—creates a compelling story that resonates with conscious consumers.",
            },
            "Innovation": {
                "asset": "AgTech",
                "pitch": "Tulip Winery's precision AgTech approach to winemaking combines traditional terroir with cutting-edge technology, delivering innovation your clients will appreciate.",
            },
            "Quality": {
                "asset": "Accolades",
                "pitch": "Tulip Winery's award-winning kosher wines from the Galilee region offer the premium quality and unique terroir story that premium importers seek.",
            },
            "Unknown": {
                "asset": "Village_of_Hope",
                "pitch": "Tulip Winery combines premium quality with a powerful social mission, offering both exceptional wines and a story that connects with consumers.",
            },
        }
        
        
        asset_info = asset_mapping.get(pain_point, asset_mapping["Unknown"])
        
        prompt = f"""You are writing a cold outreach email from Tulip Winery to a potential wine importer.

**Sender:** Tulip Winery (premium kosher winery from Israel)
**Recipient:** {decision_maker_name}, {decision_maker_title} at {company_name}

**Your Research:**
- {company_name} appears focused on: {pain_point}
- Evidence: {evidence}

**Your Pitch:**
{asset_info['pitch']}

**Instructions:**
Write a professional B2B email following these rules:
1. Start with a warm, personalized greeting
2. Open with a specific observation about their company based on the evidence
3. Smoothly transition to how Tulip Winery's offering addresses their {pain_point} focus
4. Keep the total email between 150-200 words
5. End with a friendly, low-pressure call-to-action (suggest a brief call next week)
6. Use a professional but warm, founder-to-buyer tone
7. DO NOT use generic phrases like "I came across your company online"

**Format your response EXACTLY like this:**
Subject: [Write an engaging subject line here]

[Write the complete email body here]

Now write the email:"""
        
        
        try:
            response = await self.generate_text(prompt, temperature=0.8, max_tokens=1000)
            
            # Parse response - expect format "Subject: ...\n\n[body]"
            subject = ""
            body = ""
            
            # Split by "Subject:" to get subject line and rest
            if "Subject:" in response:
                parts = response.split("Subject:", 1)
                after_subject = parts[1].strip()
                
                # Split on first double newline or single newline
                if "\n\n" in after_subject:
                    lines = after_subject.split("\n\n", 1)
                    subject = lines[0].strip()
                    body = lines[1].strip() if len(lines) > 1 else ""
                elif "\n" in after_subject:
                    lines = after_subject.split("\n", 1)
                    subject = lines[0].strip()
                    body = lines[1].strip() if len(lines) > 1 else ""
                else:
                    subject = after_subject.strip()
            else:
                # Fallback: use first line as subject, rest as body
                lines = response.strip().split('\n', 1)
                subject = lines[0].strip()
                body = lines[1].strip() if len(lines) > 1 else ""
            
            # Ensure we have content
            if not subject:
                subject = f"Tulip Winery x {company_name}: Premium Israeli Wines"
            if not body:
                body = response.strip()  # Use entire response as body
            
            logger.info(
                "email_generated",
                company=company_name,
                pain_point=pain_point,
                asset=asset_info['asset'],
                subject_length=len(subject),
                body_length=len(body),
            )
            
            return {
                "subject": subject,
                "body": body,
                "tulip_asset_used": asset_info['asset'],
            }
            
        except Exception as e:
            logger.error("email_generation_failed", company=company_name, error=str(e))
            raise


# Global service instance
gemini_service = GeminiService()
