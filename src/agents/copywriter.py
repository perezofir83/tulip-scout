"""Copywriter agent - generates personalized emails using pain-point matching."""
import uuid
from typing import Dict, Optional
from datetime import datetime

from src.agents.base import BaseAgent
from src.database.models import Email, EmailStatus, PainPoint, TulipAsset
from src.database.database import get_db
from src.services import gemini_service, gmail_service
from src.utils.logger import logger


class CopywriterAgent(BaseAgent):
    """
    Copywriter agent that generates personalized emails using pain-point matching.
    
    Workflow:
    1. Analyze lead's website/LinkedIn for pain points
    2. Map pain point to Tulip's matching asset
    3. Generate solution-oriented email
    4. Create Gmail draft
    """
    
    def __init__(self):
        """Initialize Copywriter agent."""
        super().__init__(name="Copywriter")
    
    async def execute(
        self,
        lead_id: str,
        company_name: str,
        decision_maker_name: str,
        decision_maker_title: str,
        website_content: str,
        linkedin_posts: Optional[str] = None,
        inferred_emails: Optional[list] = None,
    ) -> str:
        """
        Generate personalized email for a lead.
        
        Args:
            lead_id: Lead database ID
            company_name: Company name
            decision_maker_name: Decision maker's name
            decision_maker_title: Decision maker's title
            website_content: Scraped website content
            linkedin_posts: Optional LinkedIn posts/updates
            inferred_emails: List of possible email addresses
            
        Returns:
            Email ID
        """
        logger.info(
            "copywriter_starting",
            lead_id=lead_id,
            company=company_name,
        )
        
        try:
            # Step 1: Analyze pain points
            logger.info("copywriter_analyzing_pain_points", lead_id=lead_id)
            analysis = await gemini_service.analyze_pain_points(
                company_name=company_name,
                website_content=website_content,
                linkedin_posts=linkedin_posts,
            )
            
            pain_point = analysis["pain_point"]
            evidence = analysis["evidence"]
            
            await self.log_activity(
                lead_id=lead_id,
                action="analyzed_pain_point",
                details={
                    "pain_point": pain_point,
                    "evidence": evidence,
                },
            )
            
            # Step 2: Generate email
            logger.info("copywriter_generating_email", lead_id=lead_id, pain_point=pain_point)
            email_data = await gemini_service.generate_email(
                company_name=company_name,
                decision_maker_name=decision_maker_name,
                decision_maker_title=decision_maker_title,
                pain_point=pain_point,
                evidence=evidence,
            )
            
            subject = email_data["subject"]
            body = email_data["body"]
            tulip_asset = email_data["tulip_asset_used"]
            
            # Step 3: Create Gmail draft
            to_email = inferred_emails[0] if inferred_emails else f"info@{company_name.lower().replace(' ', '')}.com"
            
            logger.info("copywriter_creating_draft", lead_id=lead_id)
            gmail_draft_id = await gmail_service.create_draft(
                to_email=to_email,
                subject=subject,
                body=body,
            )
            
            # Step 4: Save email to database
            email_id = str(uuid.uuid4())
            
            with get_db() as db:
                email = Email(
                    id=email_id,
                    lead_id=lead_id,
                    subject=subject,
                    body=body,
                    detected_pain_point=PainPoint(pain_point),
                    tulip_asset_used=TulipAsset(tulip_asset),
                    gmail_draft_id=gmail_draft_id,
                    status=EmailStatus.DRAFT,
                    created_at=datetime.utcnow(),
                )
                db.add(email)
                db.commit()
            
            await self.log_activity(
                lead_id=lead_id,
                action="drafted_email",
                details={
                    "email_id": email_id,
                    "subject": subject,
                    "pain_point": pain_point,
                    "tulip_asset": tulip_asset,
                    "gmail_draft_id": gmail_draft_id,
                },
            )
            
            logger.info(
                "copywriter_complete",
                lead_id=lead_id,
                email_id=email_id,
                pain_point=pain_point,
                asset=tulip_asset,
            )
            
            return email_id
            
        except Exception as e:
            logger.error(
                "copywriter_failed",
                lead_id=lead_id,
                error=str(e),
            )
            await self.log_activity(
                lead_id=lead_id,
                action="draft_failed",
                details={"error": str(e)},
            )
            raise


# Global agent instance
copywriter_agent = CopywriterAgent()
