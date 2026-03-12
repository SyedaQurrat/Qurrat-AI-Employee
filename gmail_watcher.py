#!/usr/bin/env python3
"""
📧 Qurrat-AI Gmail Watcher
Monitors Gmail for unread important emails and creates task files in Needs_Action/
"""

import os
import re
import time
import base64
from datetime import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()

BASE_DIR = Path(__file__).parent
NEEDS_ACTION_DIR = BASE_DIR / "Needs_Action"
TOKEN_FILE = BASE_DIR / "token.json"
CREDENTIALS_FILE = BASE_DIR / "credentials.json"

# Gmail API scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Watch interval in seconds
CHECK_INTERVAL = 120  # 2 minutes

# Priority keywords for email classification
PRIORITY_KEYWORDS = {
    "high": ["urgent", "asap", "priority", "important", "action required", "deadline"],
    "medium": ["review", "approval", "meeting", "schedule", "reminder"],
    "low": ["newsletter", "update", "notification", "info"]
}


def sanitize_filename(text):
    """Remove invalid characters from filename."""
    text = text.replace("/", "-").replace("\\", "-")
    text = re.sub(r"[^\w\s\-_\.]", "", text)
    return text[:50]  # Limit length


def get_priority(subject, snippet):
    """Determine email priority based on keywords."""
    text = f"{subject} {snippet}".lower()
    
    for priority, keywords in PRIORITY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return priority
    
    return "normal"


def decode_email_part(part):
    """Decode email part data."""
    if "data" in part:
        data = part["data"]
        decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        return decoded
    return ""


def extract_email_info(message):
    """Extract relevant information from Gmail message."""
    headers = message["payload"]["headers"]
    
    info = {
        "sender": "",
        "subject": "",
        "date": "",
        "snippet": message.get("snippet", ""),
    }
    
    for header in headers:
        name = header["name"].lower()
        value = header["value"]
        
        if name == "from":
            # Extract email address from "Name <email@example.com>" format
            match = re.search(r"<([^>]+)>", value)
            info["sender"] = match.group(1) if match else value.split("<")[0].strip()
        elif name == "subject":
            info["subject"] = value
        elif name == "date":
            info["date"] = value
    
    # Try to get full body if available
    body = ""
    if "parts" in message["payload"]:
        for part in message["payload"]["parts"]:
            if part["mimeType"] == "text/plain":
                body = decode_email_part(part)
                break
    
    if not body and "body" in message["payload"]:
        body = decode_email_part(message["payload"]["body"])
    
    info["body"] = body[:500] if body else info["snippet"]  # Limit body preview
    info["priority"] = get_priority(info["subject"], info["snippet"])
    
    return info


def create_task_file(email_info):
    """Create a markdown task file for the email."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sender_clean = sanitize_filename(email_info["sender"].split("@")[0])
    
    filename = f"EMAIL_{sender_clean}_{timestamp}.md"
    filepath = NEEDS_ACTION_DIR / filename
    
    # Priority emoji mapping
    priority_emoji = {
        "high": "🔴 HIGH",
        "medium": "🟡 MEDIUM",
        "low": "🟢 LOW",
        "normal": "⚪ NORMAL"
    }
    
    content = f"""---
type: email_task
priority: {email_info["priority"].upper()}
sender: {email_info["sender"]}
date: {email_info["date"]}
created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
status: pending
---

# 📧 Email Task: {email_info["subject"]}

## 📋 Details

| Field | Value |
| :--- | :--- |
| **Sender** | {email_info["sender"]} |
| **Date** | {email_info["date"]} |
| **Priority** | {priority_emoji.get(email_info["priority"], email_info["priority"].upper())} |
| **Status** | 📥 Needs Action |

## 📝 Message Preview

{email_info["body"] if email_info["body"] else email_info["snippet"]}

---

## ✅ Action Items

- [ ] Review email content
- [ ] Determine required action
- [ ] Respond or delegate
- [ ] Move to appropriate folder

---
*Created by Qurrat-AI Gmail Watcher at {datetime.now().strftime("%H:%M:%S")}*
"""
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filename


def authenticate_gmail():
    """Authenticate with Gmail API using OAuth2."""
    creds = None

    # Load existing token if available
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        print("✅ Token loaded from token.json")

    # Refresh or obtain new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print("❌ Error: credentials.json not found!")
                print("📋 Please download OAuth2 credentials from Google Cloud Console")
                print("   and save as 'credentials.json' in the project directory.")
                return None

            print("🌐 Starting OAuth2 authorization flow...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)

            # Try local server flow first with dynamic port (port=0 finds available port)
            try:
                print("🌐 Attempting local server authentication (auto port)...")
                creds = flow.run_local_server(port=0, prompt='consent')
                print("✅ Authorization successful via local server!")
            except Exception as e:
                # Fallback to noauth_local_webserver for environments where browser redirect fails
                print(f"⚠️  Local server failed: {e}")
                print("🔄 Falling back to --noauth_local_webserver mode...")

                auth_url, _ = flow.authorization_url(prompt='consent')

                print("\n" + "=" * 70)
                print("📋 STEP 1: Copy aur open karein yeh URL apne browser mein:")
                print("=" * 70)
                print(auth_url)
                print("=" * 70)
                print("\n✍️  STEP 2: Google account se login karein aur permissions allow karein")
                print("\n✍️  STEP 3: Authorization code paste karein neeche:")
                print("-" * 70)
                code = input("Authorization code: ").strip()

                if code:
                    flow.fetch_token(code=code)
                    creds = flow.credentials
                    print("✅ Authorization successful!")
                else:
                    print("❌ No code provided. Exiting.")
                    return None

        # Save the credentials for the next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
        print("✅ Token saved to token.json")

    return creds


def check_gmail(service):
    """Check Gmail for unread emails and create task files."""
    try:
        # Fetch unread messages
        results = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["UNREAD"], maxResults=10)
            .execute()
        )
        
        messages = results.get("messages", [])
        
        if not messages:
            print("✅ No unread emails found")
            return 0
        
        print(f"📬 Found {len(messages)} unread email(s)")
        
        processed = 0
        for message in messages:
            try:
                # Get full message details
                msg = (
                    service.users()
                    .messages()
                    .get(userId="me", id=message["id"], format="full")
                    .execute()
                )
                
                email_info = extract_email_info(msg)
                
                # Create task file
                filename = create_task_file(email_info)
                print(f"  ✅ Created: {filename}")
                print(f"     From: {email_info['sender']}")
                print(f"     Subject: {email_info['subject']}")
                print(f"     Priority: {email_info['priority'].upper()}")
                
                processed += 1
                
            except Exception as e:
                print(f"  ⚠️  Error processing message: {e}")
        
        return processed
        
    except HttpError as error:
        print(f"❌ Gmail API error: {error}")
        return 0


def main():
    """Main function to run the Gmail watcher."""
    print("=" * 60)
    print("📧 Qurrat-AI Gmail Watcher")
    print("=" * 60)
    print(f"📂 Monitoring interval: {CHECK_INTERVAL} seconds")
    print(f"📁 Output folder: {NEEDS_ACTION_DIR}")
    print(f"🔑 Token file: {TOKEN_FILE}")
    print("=" * 60)
    
    # Ensure Needs_Action directory exists
    NEEDS_ACTION_DIR.mkdir(parents=True, exist_ok=True)
    
    # Authenticate
    print("\n🔐 Authenticating with Gmail...")
    creds = authenticate_gmail()
    
    if not creds:
        print("\n❌ Authentication failed. Exiting.")
        return
    
    print("✅ Authentication successful!")
    
    # Build Gmail service
    service = build("gmail", "v1", credentials=creds)
    
    print("\n🚀 Starting Gmail monitoring...")
    print("⏸️  Press Ctrl+C to stop\n")
    
    # Main monitoring loop
    check_count = 0
    try:
        while True:
            check_count += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{timestamp}] Check #{check_count}")
            print("-" * 40)
            
            processed = check_gmail(service)
            
            if processed > 0:
                print(f"\n✨ Processed {processed} email(s)")
            
            # Wait for next check
            print(f"\n💤 Sleeping for {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n👋 Stopping Gmail watcher...")
        print("✅ Goodbye!")


if __name__ == "__main__":
    main()
