# Discord Ping v2

Monitors a Discord channel for webhook alerts containing a **"Queue Detected"** embed and instantly opens the embedded `pokemoncenter.com` link in your default browser.

## How it works

- Logs into Discord using your personal user token
- Watches a single configured channel
- When a message arrives with an embed whose title contains `"queue"` and whose URL points to `pokemoncenter.com`, it opens the link immediately

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`

## Setup

### 1. Clone & install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure your `.env`

Copy the example and fill in your credentials:

**Getting the Channel ID:**

1. In Discord, go to **Settings → Advanced** and enable **Developer Mode**
2. Right-click the target channel → **Copy Channel ID**

### 3. Run

```bash
python3 ping.py
```

## Disclaimer

Self-botting (automating a personal Discord account) violates Discord's Terms of Service. Use at your own risk — a secondary account is recommended.

## Future Roadmap

- Add more sites
- Sync with user roles
