# Discord Server Drop - Ping

Monitors a Discord channel for webhook alerts containing keywords like: **"Queue Detected"** embed and instantly opens the embedded `pokemoncenter.com` link in your default browser. (Safe to use!)

## How it works

- Logs into Discord using your personal user token
- Watches configured channels
- When a message arrives with chosen key words, it opens the link immediately

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
python3 pokeping.py
```

- pokeping.py - pokemoncenter + other stores
- ping.py - specifically pokemoncenter (only looks for the word "queue" to prevent multiple browser spam when products are announced)
- walmart.py - specifically for stores (walmart, ebgames, costco anything)

## Future Roadmap

- Add more sites
- Sync with user roles
- Better search
