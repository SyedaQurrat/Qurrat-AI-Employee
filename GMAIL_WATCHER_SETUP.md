# 📧 Gmail Watcher Setup Guide

## Prerequisites

You need Google OAuth2 credentials to use the Gmail Watcher.

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Gmail API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it

## Step 2: Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select **Desktop app** as the application type
4. Download the JSON file
5. Save it as `credentials.json` in the `AI_Employee_Vault` directory

## Step 3: Configure .env File

Create or update your `.env` file:

```bash
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 5: Run the Gmail Watcher

```bash
python3 gmail_watcher.py
```

### First Run:
- A browser window will open asking you to authenticate with Google
- Sign in with your Gmail account
- Grant permissions to access your emails
- The token will be saved to `token.json` for future use

## Step 6: (Optional) Run as Background Service

### Using systemd (Linux):

Create `/etc/systemd/system/gmail-watcher.service`:

```ini
[Unit]
Description=Qurrat-AI Gmail Watcher
After=network.target

[Service]
Type=simple
User=syeda
WorkingDirectory=/home/syeda/AI_Employee_Vault
ExecStart=/home/syeda/AI_Employee_Vault/venv/bin/python3 /home/syeda/AI_Employee_Vault/gmail_watcher.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then enable and start:

```bash
sudo systemctl enable gmail-watcher
sudo systemctl start gmail-watcher
sudo systemctl status gmail-watcher
```

## Features

- ✅ Checks Gmail every 2 minutes
- ✅ Creates `.md` files in `Needs_Action/` folder
- ✅ Priority detection (HIGH, MEDIUM, LOW, NORMAL)
- ✅ Extracts sender, subject, date, and preview
- ✅ OAuth2 secure authentication
- ✅ Token auto-refresh

## File Naming Convention

```
EMAIL_[sender]_[timestamp].md
```

Example: `EMAIL_john_doe_20260311_145030.md`

## Troubleshooting

### "credentials.json not found"
- Make sure you downloaded and saved the OAuth2 credentials file

### "Token expired"
- Delete `token.json` and re-run the script to re-authenticate

### "Gmail API error"
- Check that Gmail API is enabled in Google Cloud Console
- Verify your OAuth2 credentials have the correct scopes
