# YouTube Channel Analyzer 📈

A comprehensive suite of tools to analyze YouTube channel strategies, growth metrics, and content performance using the official YouTube Data API v3. 

This repository contains three tools: an interactive HTML dashboard designed for non-technical users, a Streamlit web app, and a simple Python script.

## Features

- **Video vs. Shorts Classification**: Automatically categorizes videos based on length (≤ 3 minutes = Shorts).
- **Engagement Rate Analysis**: Calculates the engagement rate `(Likes + Comments) / Views` to identify high-potential content formats.
- **Posting Strategy Visualization**: Charts revealing the channel's daily upload frequency for both Shorts and standard Videos.
- **Social Media Detection**: Scans the channel's "About" description to automatically find links/mentions of Instagram, TikTok, Facebook, Threads, and X (Twitter).
- **Video Details**: Shows each video's category, captions (CC), tags, description, and upload time (to the minute).
- **CSV Export**: One-click download of all fetched video data (views, likes, comments, duration, engagement rate) for further spreadsheet analysis.

## Included Tools

### 1. HTML Dashboard (`index.html`) 🌟 **Recommended**
The most feature-rich version. It is a single HTML file that runs entirely in your web browser. No Python installations required!
- **Online**: Open the repository's GitHub Pages site (served from `index.html`).
- **Locally**: Double-click `index.html` to open it in Chrome/Safari/Edge.
- **How to use**: Paste your API key, type a channel handle (e.g., `@gaoweirenzhi`), choose a timeframe (last 7, 30, or 90 days, or the latest 500 videos), and click **Run Integration**.

### 2. Streamlit Web App (`app.py`)
A Python-based interactive dashboard built with Streamlit.
- **Requirements**: Python 3.x, `streamlit`, `pandas`, `requests`
- **How to use**: 
  ```bash
  pip install streamlit pandas requests
  streamlit run app.py
  ```

### 3. Basic Python Script (`youtube_channel_analyzer.py`)
A pure backend script that fetches the channel data and outputs it directly to a CSV file.
- **Requirements**: Python 3.x, `requests`
- **How to use**:
  ```bash
  export YOUTUBE_API_KEY="YOUR_API_KEY_HERE"
  python youtube_channel_analyzer.py @gaoweirenzhi
  ```

## Getting a YouTube API Key
To use any of these tools, you need a free YouTube Data API v3 key:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Search for "YouTube Data API v3" and enable it.
4. Go to "Credentials", click "Create Credentials", and select "API key".

**Protect your key**: The HTML dashboard uses your key directly in the browser. In the Google Cloud Console, restrict the key to the YouTube Data API v3, and limit it to your own website (HTTP referrer) if you use GitHub Pages.

## Limitations
Due to the official YouTube Data API v3 restrictions:
- We cannot fetch historical growth series (e.g., subscriber count per day from exactly a year ago).
- Community Posts data is not accessible.
- Share counts are not publicly available via this API.

## License
MIT License
