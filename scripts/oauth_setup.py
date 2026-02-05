#!/usr/bin/env python3
"""
Gmail OAuth Setup Script
Completes the initial authentication flow and saves refresh token.
"""

import os
import sys
import pickle
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.config import settings

# Gmail API scope for creating drafts
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']


def main():
    """Run OAuth flow and save token."""
    creds = None
    token_path = settings.gmail_token_path
    credentials_path = settings.gmail_credentials_path
    
    # Check if credentials file exists
    if not os.path.exists(credentials_path):
        print(f"❌ Error: {credentials_path} not found!")
        print(f"📋 Please download OAuth credentials from Google Cloud Console")
        print(f"   and save as: {credentials_path}")
        sys.exit(1)
    
    # Check if we already have a token
    if os.path.exists(token_path):
        print(f"✅ Found existing token at {token_path}")
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, run OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🔐 Starting OAuth flow...")
            print("\n📋 Instructions:")
            print("1. A browser window will open")
            print("2. Sign in with your Gmail account")
            print("3. You'll see 'Google hasn't verified this app' - click 'Advanced' → 'Go to TulipScout (unsafe)'")
            print("4. Click 'Allow' to grant permissions")
            print("5. You'll see 'The authentication flow has completed'\n")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=8080)
        
        # Save token for future runs
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        print(f"✅ Token saved to {token_path}")
    
    # Test the credentials
    try:
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        print(f"\n🎉 Success! Authenticated as: {profile['emailAddress']}")
        print(f"📊 Total messages in mailbox: {profile['messagesTotal']}")
    except Exception as e:
        print(f"\n❌ Error testing credentials: {e}")
        return
    
    print("\n✅ OAuth setup complete! You can now create Gmail drafts via the API.")


if __name__ == '__main__':
    main()
