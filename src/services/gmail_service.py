"""Gmail service for creating drafts."""
import pickle
import base64
import os
from email.mime.text import MIMEText
from typing import Optional
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

from src.config import settings
from src.utils.logger import logger


class GmailService:
    """Service for Gmail API integration."""
    
    def __init__(self):
        """Initialize Gmail service."""
        self.service = None
        self._load_credentials()
    
    def _load_credentials(self):
        """Load Gmail OAuth credentials."""
        token_path = settings.gmail_token_path
        
        if not os.path.exists(token_path):
            logger.error("gmail_token_not_found", path=token_path)
            raise FileNotFoundError(
                f"Gmail token not found at {token_path}. "
                f"Run 'python scripts/oauth_setup.py' first."
            )
        
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        
        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("gmail_service_initialized")
    
    async def create_draft(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
    ) -> str:
        """
        Create a draft email in Gmail.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body
            from_email: Sender email (defaults to authenticated user)
            
        Returns:
            Gmail draft ID
        """
        try:
            # Create message
            message = MIMEText(body)
            message['to'] = to_email
            message['subject'] = subject
            if from_email:
                message['from'] = from_email
            
            # Encode message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Create draft
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw}}
            ).execute()
            
            draft_id = draft['id']
            
            logger.info(
                "gmail_draft_created",
                draft_id=draft_id,
                to=to_email,
                subject=subject,
            )
            
            return draft_id
            
        except Exception as e:
            logger.error("gmail_draft_failed", to=to_email, error=str(e))
            raise
    
    async def send_draft(self, draft_id: str) -> str:
        """
        Send a draft email.
        
        Args:
            draft_id: Gmail draft ID
            
        Returns:
            Sent message ID
        """
        try:
            sent = self.service.users().drafts().send(
                userId='me',
                body={'id': draft_id}
            ).execute()
            
            message_id = sent['id']
            
            logger.info(
                "gmail_draft_sent",
                draft_id=draft_id,
                message_id=message_id,
            )
            
            return message_id
            
        except Exception as e:
            logger.error("gmail_send_failed", draft_id=draft_id, error=str(e))
            raise
    
    async def get_draft_link(self, draft_id: str) -> str:
        """Get Gmail web link for a draft."""
        return f"https://mail.google.com/mail/u/0/#drafts?compose={draft_id}"


# Global service instance
gmail_service = GmailService()
